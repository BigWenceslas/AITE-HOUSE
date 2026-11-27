# -*- coding: utf-8 -*-
"""Le nombre d'exemplaires des bons de préparation (demande du Messager :
« imprimer 3 fois d'un coup en cuisine » ; 18.0.1.0.13).

Réglage de l'imprimante de préparation (Point de Vente → Configuration →
Imprimantes de préparation) : « Nombre d'exemplaires du bon », 1 d'office,
entre 1 et 5. Sur une caisse au service à table contrôlé, un bon qui porte
de nouveaux plats sort en autant d'exemplaires identiques, numérotés
« Exemplaire 1/3 »… ; un bon fait seulement d'annulations, de notes ou de
la note générale sort en un exemplaire. La règle est appliquée par la caisse
(``static/src/utils/bons.js``).

L'imprimante « Autre » (demande du restaurant de Douala : « chaud, froid,
bar, pizza et autre » ; 18.0.1.0.14) : la case « Prend tout ce qu'aucune
autre imprimante ne prend ». Un plat dont aucune autre imprimante de la
caisse ne prend la famille (ou sans famille) part sur cette imprimante, en
plus des familles qui y sont cochées ; annulations et note générale suivent
le même chemin (``static/src/store/bons_store.js``). Au plus une par caisse.
Le formulaire dit aussi quelles familles de la carte ne sortiraient sur
aucun bon (« familles orphelines », calculées par la caisse :
``pos.config._aite_familles_orphelines``).
"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

EXEMPLAIRES_MIN = 1
EXEMPLAIRES_MAX = 5


class PosPrinter(models.Model):
    _inherit = 'pos.printer'

    aite_exemplaires = fields.Integer(
        "Nombre d'exemplaires du bon", default=1,
        help="Combien de fois chaque nouveau bon sort sur cette imprimante (de 1 à 5).")
    aite_exemplaires_phrase = fields.Char(
        "Ce qui va se passer", compute='_compute_aite_exemplaires_phrase')

    aite_prend_le_reste = fields.Boolean(
        "Prend tout ce qu'aucune autre imprimante ne prend", default=False,
        help="L'imprimante « Autre » : les plats qu'aucune autre imprimante de la caisse ne "
             "prend (famille cochée nulle part, ou plat sans famille) sortent ici.")
    aite_prend_le_reste_phrase = fields.Char(
        "Ce qui va se passer (Autre)", compute='_compute_aite_prend_le_reste_phrase')
    aite_familles_orphelines = fields.Text(
        "Familles qu'aucune imprimante ne prend", compute='_compute_aite_familles_orphelines')

    @api.depends('aite_prend_le_reste')
    def _compute_aite_prend_le_reste_phrase(self):
        for imprimante in self:
            imprimante.aite_prend_le_reste_phrase = self._phrase_prend_le_reste(
                imprimante.aite_prend_le_reste)

    @staticmethod
    def _phrase_prend_le_reste(coche):
        """La phrase « ce qui va se passer » de la case « Autre »."""
        if coche:
            return ("Tout plat qu'aucune autre imprimante de la caisse ne prend (sa famille "
                    "n'est cochée nulle part, ou il n'a pas de famille) sort sur cette "
                    "imprimante, en plus des familles cochées ici : un plat envoyé n'est "
                    "jamais perdu. Ses annulations et la note générale de la table suivent "
                    "le même chemin. Il ne peut y avoir qu'une seule imprimante « Autre » "
                    "par caisse. La case agit sur les caisses au service à table contrôlé "
                    "seulement ; sur une autre caisse, elle n'a pas d'effet.")
        return ("Cette imprimante reçoit seulement les familles cochées ci-dessus, avec "
                "leurs sous-familles (cocher « Bar » envoie aussi les vins, les bières…). "
                "Un plat dont la famille n'est cochée sur aucune imprimante ne sort nulle "
                "part, sauf si la caisse a une imprimante « Autre ».")

    @api.depends('product_categories_ids', 'aite_prend_le_reste')
    def _compute_aite_familles_orphelines(self):
        """Calculé avec les valeurs du formulaire (relecture de 18.0.1.0.14) :
        pendant la saisie, l'imprimante est un enregistrement « nouveau »
        dont l'original donne les caisses ; ses familles et sa case sont
        celles qui sont à l'écran, les autres imprimantes celles en base."""
        Caisse = self.env['pos.config']
        for imprimante in self:
            origine = imprimante._origin.id
            caisses = Caisse.search([('printer_ids', 'in', [origine])]) if origine else Caisse
            textes = []
            for caisse in caisses:
                autres = caisse.printer_ids.filtered(lambda p: p.id != origine)
                texte = caisse._aite_texte_orphelines(autres | imprimante)
                if texte:
                    textes.append((caisse, texte))
            if len(textes) == 1:
                imprimante.aite_familles_orphelines = textes[0][1]
            else:
                imprimante.aite_familles_orphelines = "\n\n".join(
                    "Caisse « %s » : %s" % (caisse.name, texte) for caisse, texte in textes) or False

    @api.constrains('aite_prend_le_reste')
    def _check_aite_une_seule_autre(self):
        caisses = self.env['pos.config'].search([('printer_ids', 'in', self.ids)])
        caisses._aite_verifier_une_seule_autre()

    @api.depends('aite_exemplaires')
    def _compute_aite_exemplaires_phrase(self):
        for imprimante in self:
            imprimante.aite_exemplaires_phrase = self._phrase_exemplaires(
                imprimante.aite_exemplaires)

    @staticmethod
    def _phrase_exemplaires(nombre):
        """La phrase « ce qui va se passer » du réglage."""
        if not nombre or nombre <= 1:
            return ("Chaque nouveau bon envoyé à cette imprimante sort en un seul "
                    "exemplaire.")
        return ("Chaque nouveau bon envoyé à cette imprimante sort en %(n)d exemplaires "
                "identiques, marqués « Exemplaire 1/%(n)d » à « Exemplaire %(n)d/%(n)d ». "
                "Les annulations et les notes seules sortent en un exemplaire." % {'n': nombre})

    @api.constrains('aite_exemplaires')
    def _check_aite_exemplaires(self):
        for imprimante in self:
            if not EXEMPLAIRES_MIN <= imprimante.aite_exemplaires <= EXEMPLAIRES_MAX:
                raise ValidationError(_(
                    "Le nombre d'exemplaires du bon doit être entre 1 et 5 "
                    "(imprimante « %s »).", imprimante.name))

    @api.model
    def _load_pos_data_fields(self, config_id):
        champs = super()._load_pos_data_fields(config_id)
        return champs + ['aite_exemplaires', 'aite_prend_le_reste'] if champs else champs
