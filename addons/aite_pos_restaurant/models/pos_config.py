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


# 18.0.1.0.14 : l'addition et le ticket groupés par famille (demande du
# restaurant de Douala : « au niveau de la facture, grouper les produits par
# famille de produits »). Décoché d'office ; la graine du restaurant et la
# carte Le Messager le cochent.
AIDE_GROUPER_FAMILLES = (
    "Coché : sur l'addition (bouton « Addition », y compris les additions d'une "
    "table divisée) et sur le ticket remis au client (et sa réimpression), les "
    "produits sont rangés sous le nom de leur famille (Petit déjeuner, Plats, "
    "Pizzas & burgers, Afternoon tea, Bar…), dans l'ordre des familles de la "
    "caisse ; chaque famille finit par « Sous-total Plats : 21 000 FCFA ». Les "
    "produits sans famille sont sous « Autres » ; le pourboire et la remise "
    "globale viennent ensuite, sans rubrique. Le total, les taxes, les paiements et la note au client ne "
    "changent pas. Au paiement, le ticket final sort seul si « Impression "
    "automatique du reçu » est coché (avec une imprimante de tickets) ; sinon, "
    "réimprimez-le depuis Commandes. Décoché : le ticket habituel, dans l'ordre "
    "de la saisie. S'applique quand la caisse est rouverte."
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

    aite_grouper_familles = fields.Boolean(
        string="Grouper les produits par famille sur l'addition et le ticket",
        default=False, help=AIDE_GROUPER_FAMILLES)
    # Les familles de la carte qu'aucune imprimante de préparation ne prend
    # (18.0.1.0.14) : affichées dans les réglages et sur chaque imprimante.
    aite_familles_orphelines = fields.Text(
        string="Familles qu'aucune imprimante ne prend",
        compute='_compute_aite_familles_orphelines')

    @api.depends('printer_ids', 'printer_ids.product_categories_ids',
                 'printer_ids.aite_prend_le_reste', 'limit_categories',
                 'iface_available_categ_ids', 'tip_product_id', 'aite_mode_restaurant',
                 'module_pos_restaurant', 'module_pos_hr')
    def _compute_aite_familles_orphelines(self):
        for caisse in self:
            caisse.aite_familles_orphelines = caisse._aite_texte_orphelines(caisse.printer_ids)

    def _aite_texte_orphelines(self, imprimantes):
        """L'avertissement des familles orphelines de la caisse, avec les
        imprimantes ``imprimantes`` (celles de la caisse, ou celles du
        formulaire d'une imprimante en cours de saisie, relecture de
        18.0.1.0.14). L'imprimante « Autre » ne couvre tout qu'au service à
        table contrôlé ; ailleurs la caisse garde le routage d'Odoo et
        l'avertissement le dit. Une caisse aux familles restreintes ne
        signale que ce qu'elle vend."""
        self.ensure_one()
        if not imprimantes:
            return False
        autres = imprimantes.filtered('aite_prend_le_reste')
        actif = self._aite_actif()
        if autres and actif:
            return False
        Famille = self.env['pos.category'].sudo()
        familles = {f.id: (f.display_name, f.parent_id.id, f.sequence) for f in Famille.search([])}
        domaine = [('available_in_pos', '=', True), ('sale_ok', '=', True)]
        restreinte = self.limit_categories and self.iface_available_categ_ids
        vendues = set(self.sudo()._get_available_categories().ids) if restreinte else None
        if restreinte:
            domaine.append(('pos_categ_ids', 'in', list(vendues)))
        produits = self.env['product.template'].sudo().search(domaine)
        hors_cuisine = self.tip_product_id.product_tmpl_id
        if 'discount_product_id' in self._fields:
            hors_cuisine |= self.discount_product_id.product_tmpl_id
        produits -= hors_cuisine
        avec_produits = set(produits.pos_categ_ids.ids)
        if vendues is not None:
            avec_produits &= vendues
        prises = set(imprimantes.product_categories_ids._origin.ids)
        orphelines = self._aite_familles_orphelines(familles, prises, avec_produits)
        sans_famille = produits.filtered(lambda p: not p.pos_categ_ids)
        return self._aite_phrase_orphelines(
            [familles[i][0] for i in orphelines], sans_famille.mapped('name'),
            autres_sans_effet=autres.mapped('name') if autres else None)

    @staticmethod
    def _aite_familles_orphelines(familles, prises, avec_produits):
        """Les familles qu'aucune imprimante ne prend, au plus haut niveau
        possible (« Desserts » plutôt que chacune de ses sous-familles).
        ``familles`` : {id: (nom complet, id du parent ou False, séquence)} ;
        ``prises`` : les familles cochées sur les imprimantes ; une famille
        prise couvre ses sous-familles (règle d'Odoo, parentPosCategIds) ;
        ``avec_produits`` : les familles qui portent directement un produit
        en vente. Une famille sans produit n'est jamais signalée. Rend les
        identifiants, dans l'ordre de la carte."""
        enfants = {}
        for ident, (_nom, parent, _seq) in familles.items():
            enfants.setdefault(parent or False, []).append(ident)

        def couverte(ident):
            vus = set()
            while ident and ident not in vus:
                if ident in prises:
                    return True
                vus.add(ident)
                ident = familles.get(ident, (None, False, 0))[1]
            return False

        def descendants(ident):
            pile, tous = list(enfants.get(ident, [])), []
            while pile:
                courant = pile.pop()
                tous.append(courant)
                pile.extend(enfants.get(courant, []))
            return tous

        def a_des_produits(ident):
            return ident in avec_produits or any(d in avec_produits for d in descendants(ident))

        def entierement_orpheline(ident):
            return not couverte(ident) and not any(d in prises for d in descendants(ident))

        resultat = []
        for ident, (_nom, parent, _seq) in familles.items():
            if couverte(ident) or not a_des_produits(ident):
                continue
            if entierement_orpheline(ident):
                if not (parent and parent in familles and entierement_orpheline(parent)):
                    resultat.append(ident)
            elif ident in avec_produits:
                # En partie prise (une sous-famille est cochée) : ses produits
                # rangés directement à ce niveau ne sortent nulle part.
                resultat.append(ident)

        def chemin(ident):
            cles = []
            while ident and ident in familles:
                cles.insert(0, (familles[ident][2], familles[ident][0]))
                ident = familles[ident][1]
            return cles

        return sorted(resultat, key=chemin)

    @staticmethod
    def _aite_phrase_orphelines(noms, sans_famille, autres_sans_effet=None):
        """L'avertissement des familles orphelines (False s'il n'y en a pas).
        ``autres_sans_effet`` : les imprimantes « Autre » d'une caisse qui
        n'est pas au service à table contrôlé, où la case n'agit pas."""
        if not noms and not sans_famille:
            return False
        morceaux = []
        if noms:
            morceaux.append("Ces familles de la carte ne sont prises par aucune imprimante : "
                            + ", ".join(noms) + ".")
        if sans_famille:
            exemples = ", ".join(sans_famille[:5]) + (", …" if len(sans_famille) > 5 else "")
            morceaux.append("%d produit%s sans famille (%s)." % (
                len(sans_famille), "s" if len(sans_famille) > 1 else "", exemples))
        morceaux.append("Leurs plats ne sortiront sur aucun bon de préparation.")
        if autres_sans_effet:
            morceaux.append(
                "L'imprimante « Autre » (%s) n'agit qu'au service à table contrôlé : sur "
                "cette caisse, elle ne reçoit que les familles cochées sur elle. Cochez ces "
                "familles sur une imprimante." % ", ".join(autres_sans_effet))
        else:
            morceaux.append("Cochez ces familles sur une imprimante, ou cochez « Prend tout "
                            "ce qu'aucune autre imprimante ne prend » sur votre imprimante "
                            "« Autre ».")
        return " ".join(morceaux)

    @api.constrains('printer_ids')
    def _aite_verifier_une_seule_autre(self):
        """Au plus une imprimante « Autre » par caisse : avec deux, on ne
        saurait pas laquelle reçoit les plats restants."""
        for caisse in self:
            autres = caisse.printer_ids.filtered('aite_prend_le_reste')
            if len(autres) > 1:
                raise ValidationError(_(
                    "La caisse « %(caisse)s » ne peut avoir qu'une seule imprimante « Autre » "
                    "(case « Prend tout ce qu'aucune autre imprimante ne prend ») ; elle en a "
                    "%(nombre)d : %(noms)s. Décochez la case sur l'une d'elles, ou retirez-la "
                    "de la caisse.",
                    caisse=caisse.name, nombre=len(autres), noms=", ".join(autres.mapped('name'))))

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
