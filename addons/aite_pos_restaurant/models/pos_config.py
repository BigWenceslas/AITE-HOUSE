# -*- coding: utf-8 -*-
"""La case « Service à table contrôlé » et la caisse posée d'office
(spécification, parties 2.2, 4.3 et 4.4)."""
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

AIDE_MODE = (
    "Coché : chaque employé tape son code à 4 chiffres pour ouvrir une table, "
    "encaisser ou annuler ; la caisse applique les quatre niveaux (serveur, "
    "caissière, chef de salle, manager), revient au plan après chaque envoi, "
    "verrouille ce qui est parti en cuisine ou au bar et garde la trace des "
    "saisies et des annulations. Cocher règle aussi, ci-dessous : connexion "
    "par code, contrôle des prix, remises désactivées, partage et impression "
    "de l'addition. Décocher arrête tout cela sur cette caisse. Se change "
    "seulement caisse fermée."
)

# Réglages posés en cochant la case (partie 4.4), à l'écran par l'onchange
# des réglages et directement par _aite_preparer_caisse.
REGLAGES_DU_MODE = {
    'module_pos_hr': True,             # REST-01 : connexion par code
    'restrict_price_control': True,    # REST-04-P1 : prix au seul manager
    'manual_discount': False,          # Q20 : pas de remise par ligne
    'module_pos_discount': False,      # REST-10 critère 7 : pas de remise globale
    'iface_splitbill': True,           # REST-14 : partage de l'addition
    'iface_printbill': True,           # Q58 : addition imprimée avant paiement
    'order_edit_tracking': False,      # T18 : le journal AITE est la trace
    'iface_print_skip_screen': False,  # partie 4.3 : retour au plan après paiement
    'aite_vente_sans_table': False,    # PROF-04-P1 : pas de « + »
}

AIDE_VENTE_SANS_TABLE = (
    "Décoché : chaque vente se fait sur une table ; le bouton « + » "
    "n'apparaît pas. Un numéro de table tapé qui n'est pas sur le plan ouvre "
    "une table à ce nom, avec son nombre de personnes. Coché : le bouton "
    "« + » ouvre une vente au comptoir ou à emporter, sans table ni nombre de "
    "personnes ; elle compte 0 personne et n'entre pas dans le nombre de "
    "tables. Seuls la caissière, le chef de salle et le manager peuvent "
    "l'ouvrir. Se change seulement caisse fermée."
)

NOM_CAISSE = "Restaurant"
NOM_SALLE = "Salle"
NOM_ESPECES = "Espèces"
NOM_MOBILE_MONEY = "Mobile Money"


class PosConfig(models.Model):
    _inherit = 'pos.config'

    aite_mode_restaurant = fields.Boolean(
        string="Service à table contrôlé", default=False, help=AIDE_MODE)
    aite_vente_sans_table = fields.Boolean(
        string="Autoriser la vente sans table", default=False,
        help=AIDE_VENTE_SANS_TABLE)

    def _aite_actif(self):
        """Vrai si la caisse est au service à table contrôlé (même règle que
        ``PosStore.aiteActif`` côté caisse)."""
        self.ensure_one()
        return bool(self.aite_mode_restaurant
                    and self.module_pos_restaurant
                    and self.module_pos_hr)

    @api.constrains('aite_mode_restaurant', 'module_pos_hr', 'module_pos_restaurant')
    def _aite_verifier_mode(self):
        """R31 : sans les codes personnels (ou hors restaurant), la caisse ne
        saurait plus qui fait quoi."""
        for config in self:
            if config.aite_mode_restaurant and not (
                    config.module_pos_hr and config.module_pos_restaurant):
                raise ValidationError(_(
                    "Décochez d'abord « Service à table contrôlé » : sans les "
                    "codes personnels, la caisse ne saurait plus qui fait quoi."))

    def _get_forbidden_change_fields(self):
        # Aucune addition en cours ne change de règle en plein service : les
        # postes gardent les réglages chargés à l'ouverture, le serveur juge
        # sur ceux qui sont enregistrés.
        return super()._get_forbidden_change_fields() + [
            'aite_mode_restaurant', 'aite_vente_sans_table']

    # ------------------------------------------------------------------
    # La caisse « Restaurant » posée d'office (partie 4.4)
    # ------------------------------------------------------------------

    @api.model
    def _aite_preparer_caisse(self, company):
        """Crée la caisse « Restaurant » de ``company`` si la société n'a
        encore aucune caisse au service à table contrôlé. Idempotente ; ne
        modifie jamais une caisse existante (T16).

        Deux modes seulement (Q56) : « Espèces » et « Mobile Money » ; ni
        « Carte » ni « Compte client » (on n'appelle donc pas
        ``_create_journal_and_payment_methods``). La salle créée d'office par
        ``pos_restaurant`` au nom de la société est renommée « Salle ».
        Écriture technique, en ``sudo()``.
        """
        Config = self.sudo().with_company(company)
        if Config.with_context(active_test=False).search_count([
                ('company_id', '=', company.id),
                ('aite_mode_restaurant', '=', True)], limit=1):
            return Config.browse()

        especes = Config._create_cash_payment_method({'name': NOM_ESPECES})
        especes.name = NOM_ESPECES  # Odoo le nomme « Cash » hors français
        mobile_money = Config._aite_mode_mobile_money(company)

        caisse = Config.create({
            'name': NOM_CAISSE,
            'company_id': company.id,
            'payment_method_ids': [(6, 0, (especes | mobile_money).ids)],
            'module_pos_restaurant': True,
            **REGLAGES_DU_MODE,
            'aite_mode_restaurant': True,
        })
        caisse.floor_ids.write({'name': NOM_SALLE})
        _logger.info("Restaurant : caisse « %s » créée pour la société %s.",
                     NOM_CAISSE, company.name)
        return caisse

    @api.model
    def _aite_mode_mobile_money(self, company):
        """Mode « Mobile Money » de la société, sur un journal de banque du
        même nom, créé s'il manque (Odoo crée son compte de trésorerie)."""
        Journal = self.env['account.journal']
        journal = Journal.search([
            ('company_id', '=', company.id),
            ('type', '=', 'bank'),
            ('name', '=', NOM_MOBILE_MONEY),
        ], limit=1)
        if not journal:
            journal = Journal.create({
                'name': NOM_MOBILE_MONEY,
                'type': 'bank',
                'company_id': company.id,
            })
        Methode = self.env['pos.payment.method']
        methode = Methode.search([
            ('company_id', '=', company.id),
            ('journal_id', '=', journal.id),
            ('split_transactions', '=', False),
        ], limit=1)
        if not methode:
            methode = Methode.create({
                'name': NOM_MOBILE_MONEY,
                'journal_id': journal.id,
                'company_id': company.id,
            })
        return methode
