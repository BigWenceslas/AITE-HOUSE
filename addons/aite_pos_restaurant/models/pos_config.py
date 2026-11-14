# -*- coding: utf-8 -*-
"""La case « Service à table contrôlé » et la caisse posée d'office
(spécification, parties 2.2, 4.3 et 4.4)."""
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from . import regles

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
    'aite_delai_alerte': regles.DELAI_ALERTE,  # Q11 : orange après 60 minutes
    'aite_refus_epuise': True,         # Q12 : un produit suivi épuisé est refusé
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

# Incrément 5 (partie 4.3). La phrase du délai suit le nombre réglé : elle
# est calculée dans les réglages (res.config.settings), à partir de ce modèle.
AIDE_DELAI = (
    "Une table ouverte depuis plus de {delai} passe à l'orange sur le plan, "
    "sans que personne ne touche l'écran : c'est le moment de demander au "
    "client s'il veut l'addition. La durée s'affiche sous le numéro de chaque "
    "table."
)

AIDE_REFUS_EPUISE = (
    "Coché : un produit dont vous suivez le stock (case « Suivre "
    "l'inventaire » de sa fiche, par exemple une bière) ne peut plus être "
    "ajouté à une table quand il n'en reste plus, en comptant ce qui est déjà "
    "parti sur les tables ouvertes ; il redevient vendable moins d'une minute "
    "après l'enregistrement d'une entrée de stock. Les produits sans suivi "
    "(plats, pizzas, café) se vendent toujours. Saisissez le stock de départ "
    "avant le premier service, sinon ces produits seront refusés."
)


def phrase_delai(delai):
    """La phrase « ce qui va se passer » du délai, avec le nombre réglé
    (« plus de 1 minute », « plus de 90 minutes »)."""
    try:
        delai = int(delai or 0)
    except (TypeError, ValueError):
        delai = 0
    minutes = "%d minute" % delai if abs(delai) == 1 else "%d minutes" % delai
    return AIDE_DELAI.format(delai=minutes)


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
    # Incrément 5 : le plan en couleurs (REST-17) et les produits épuisés
    # (REST-19a). Lus par la caisse à son ouverture (pos.config est chargé
    # avec tous ses champs) : un changement s'applique quand la caisse est
    # rouverte (REST-17 critère 4) ; ils ne sont donc pas réservés à la
    # caisse fermée.
    aite_delai_alerte = fields.Integer(
        string="Délai avant l'orange (minutes)", default=regles.DELAI_ALERTE,
        help=phrase_delai(regles.DELAI_ALERTE))
    aite_refus_epuise = fields.Boolean(
        string="Refuser la vente des produits épuisés", default=True,
        help=AIDE_REFUS_EPUISE)

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

    @api.constrains('aite_delai_alerte')
    def _aite_verifier_delai(self):
        for config in self:
            if config.aite_delai_alerte < 1:
                raise ValidationError(_(
                    "Le délai avant l'orange doit être d'au moins 1 minute."))

    def _get_forbidden_change_fields(self):
        # Aucune addition en cours ne change de règle en plein service : les
        # postes gardent les réglages chargés à l'ouverture, le serveur juge
        # sur ceux qui sont enregistrés.
        return super()._get_forbidden_change_fields() + [
            'aite_mode_restaurant', 'aite_vente_sans_table']

    # ------------------------------------------------------------------
    # La caisse « Restaurant » posée d'office (partie 4.4)
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # Le nom de la caisse créée, pour le journal de ses « Espèces » s'il
        # faut en créer un (« Espèces Bar ») : lu par _default_payment_methods,
        # appelé par Odoo pendant la création. Le contexte d'origine est rendu.
        contexte = self.env.context
        if len(vals_list) == 1 and vals_list[0].get('name'):
            self = self.with_context(aite_nom_caisse=vals_list[0]['name'])
        return super().create(vals_list).with_context(contexte)

    def _default_payment_methods(self):
        """Une caisse créée ensuite (un bar, par exemple) reçoit aussi ses
        « Espèces ». Odoo lui propose les modes de la société encore libres ;
        celles de la caisse « Restaurant » ne se partagent pas (un mode
        d'espèces ne sert qu'une caisse) et Odoo n'en crée que si la société
        n'a aucun mode de paiement : la caisse n'avait donc pas d'espèces
        (chasse aux régressions : test d'Odoo ``test_report_listing``). Les
        « Espèces » sont posées comme celles de la caisse « Restaurant » :
        journal d'espèces libre, sinon créé au nom de la caisse (« Espèces
        Bar ») ; écriture technique, en ``sudo()``."""
        methodes = super()._default_payment_methods()
        company = self.env.company
        if methodes.filtered('is_cash_count') or not company.chart_template:
            return methodes
        return methodes | self.sudo()._aite_mode_especes(
            company, self.env.context.get('aite_nom_caisse'))

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

        especes = Config._aite_mode_especes(company)
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
    def _aite_mode_especes(self, company, nom_caisse=False):
        """Mode « Espèces » d'une caisse, sur le journal d'espèces libre de la
        société (type espèces, sans mode de paiement : celui du plan comptable
        sur une base neuve) ; un journal n'est créé, comme le fait Odoo
        (``_create_cash_payment_method``), que s'il n'y en a pas de libre, au
        nom de la caisse quand il est connu (« Espèces Bar » : pas deux
        journaux « Espèces » homonymes). Une seule caisse, un seul journal
        d'espèces (notes de version, §2 : caisse « Restaurant », un seul
        journal « Espèces ») ; Odoo n'accepte qu'un mode d'espèces par
        journal."""
        libre = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', '=', 'cash'),
            ('pos_payment_method_ids', '=', False),
            ('currency_id', 'in', (False, company.currency_id.id)),
        ], limit=1)
        if not libre:
            nom = "%s %s" % (NOM_ESPECES, nom_caisse) if nom_caisse else NOM_ESPECES
            especes = self._create_cash_payment_method({'name': nom})
        else:
            especes = self.env['pos.payment.method'].create({
                'name': 'Cash',
                'journal_id': libre.id,
                'company_id': company.id,
            })
        return self._aite_nommer_especes(especes)

    @api.model
    def _aite_nommer_especes(self, methode):
        """Le nom traduisible d'un mode d'espèces d'Odoo : « Cash » en anglais
        (le nom d'origine), « Espèces » en français (traduction posée quand le
        français est actif). Forcé à « Espèces » dans toutes les langues, le
        mode n'était plus, dans une base en anglais, un « Cash » d'Odoo : resté
        libre après la suppression de sa caisse, il passait avant le « Cash »
        d'une caisse créée ensuite et Odoo le comptait à la fermeture (chasse
        aux régressions : tours d'Odoo ``CashClosingDetails`` et
        ``OrderPaidInCash``)."""
        traductions = {'en_US': 'Cash'}
        if 'fr_FR' in dict(self.env['res.lang'].get_installed()):
            traductions['fr_FR'] = NOM_ESPECES
        methode.update_field_translations('name', traductions)
        return methode

    @api.model
    def _aite_traduire_especes(self):
        """Le français activé après l'installation (base créée en anglais,
        chez un hébergeur) : les modes d'espèces nommés « Cash » sans nom
        français reçoivent « Espèces » (pas d'anglais résiduel sur le bouton
        de paiement). Un nom déjà traduit n'est jamais touché. Appelé au
        chargement des traductions françaises (ir.module.module)."""
        self.env['pos.payment.method'].flush_model(['name', 'is_cash_count'])
        self.env.cr.execute("""
            SELECT id FROM pos_payment_method
             WHERE is_cash_count AND name->>'en_US' = 'Cash' AND NOT name ? 'fr_FR'
        """)
        for methode in self.env['pos.payment.method'].sudo().browse(
                [ligne[0] for ligne in self.env.cr.fetchall()]):
            methode.update_field_translations('name', {'fr_FR': NOM_ESPECES})

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
