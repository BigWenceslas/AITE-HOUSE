# -*- coding: utf-8 -*-
"""Lignes d'addition : ce qui est parti en cuisine ou au bar, tenu par le
serveur seul (spécification, T9, parties 3.1 et 4.2 ; incréments 3 et 4).

``aite_qte_envoyee`` est ce que le serveur sait être parti et pas encore
annulé avec le code d'un responsable ; ``aite_qte_preparation`` est la
dernière quantité de préparation reçue de la caisse pour la ligne : seule sa
hausse (un nouvel envoi) augmente ``aite_qte_envoyee``. Les deux champs ne
sont pas chargés en caisse (la liste des champs de ligne d'Odoo est
explicite) ; ils sont retirés de toute écriture reçue (synchronisation,
écriture directe du compte de la caisse), sauf quand notre propre code
serveur écrit (``contexte_serveur`` : une clé de contexte envoyée par la
caisse n'autorise rien).

Incrément 4 : le compte de la caisse a tous les droits sur les lignes. Hors
de la synchronisation (``contexte_synchro``, posé par ``_process_order``,
qui fait lui-même le bilan des lignes), une baisse de ``qty`` sous ce qui est
parti, ou la suppression d'une ligne envoyée d'une addition en cours, n'est
pas refusée : elle est tracée « Retrait sans code » au journal des
annulations.
"""
from odoo import api, fields, models
from odoo.tools import float_compare

from . import regles
from .pos_session import contexte_serveur, ecrit_par_le_serveur

CHAMPS_LIGNE_SERVEUR = ('aite_qte_envoyee', 'aite_qte_preparation')
PRECISION = 6

# La synchronisation de la caisse (``pos.order._process_order``) écrit et
# supprime des lignes : le bilan qu'elle fait ensuite trace ce qui est retiré.
# Comme pour ``contexte_serveur``, la clé ne vaut que si elle porte ce jeton,
# comparé par identité : une requête ne peut pas l'apporter pour faire passer
# une écriture directe sans trace.
CONTEXTE_SYNCHRO = 'aite_synchronisation'
_JETON_SYNCHRO = object()


def contexte_synchro():
    return {CONTEXTE_SYNCHRO: _JETON_SYNCHRO}


def dans_la_synchro(env):
    return env.context.get(CONTEXTE_SYNCHRO) is _JETON_SYNCHRO


def sans_champs_ligne_serveur(vals):
    return {champ: valeur for champ, valeur in vals.items()
            if champ not in CHAMPS_LIGNE_SERVEUR}


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    aite_qte_envoyee = fields.Float(
        "Quantité envoyée (non annulée)", readonly=True, copy=False,
        digits='Product Unit of Measure',
        help="Ce que le serveur sait être parti en cuisine ou au bar et pas "
             "encore annulé avec le code d'un responsable.")
    aite_qte_preparation = fields.Float(
        "Quantité de préparation reçue", readonly=True, copy=False,
        digits='Product Unit of Measure',
        help="Technique : la dernière quantité de préparation reçue de la caisse "
             "pour cette ligne ; seule sa hausse (un nouvel envoi) augmente la "
             "quantité envoyée.")

    @api.model_create_multi
    def create(self, vals_list):
        if not ecrit_par_le_serveur(self.env):
            vals_list = [sans_champs_ligne_serveur(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        if ecrit_par_le_serveur(self.env):
            return super().write(vals)
        vals = sans_champs_ligne_serveur(vals)
        retraits = []
        if 'qty' in vals and not dans_la_synchro(self.env):
            reste = max(regles._nombre(vals['qty']), 0.0)
            for ligne in self._aite_lignes_envoyees():
                if float_compare(ligne.aite_qte_envoyee, reste, precision_digits=PRECISION) > 0:
                    retraits.append((ligne, ligne.aite_qte_envoyee - reste, reste,
                                     ligne.order_id._aite_prix_ttc(ligne)))
        res = super().write(vals)
        for ligne, retrait, reste, prix in retraits:
            ligne.order_id._aite_tracer_retrait(ligne, retrait, prix)
            ligne.with_context(**contexte_serveur()).write({'aite_qte_envoyee': reste})
        return res

    def unlink(self):
        traces = []
        if not dans_la_synchro(self.env):
            for ligne in self._aite_lignes_envoyees():
                traces.append(ligne.order_id._aite_valeurs_annulation(
                    ligne.uuid, ligne.product_id, ligne.full_product_name,
                    ligne.order_id._aite_prix_ttc(ligne), ligne.aite_qte_envoyee,
                    'retrait_sans_code', serveur=ligne.order_id._aite_employe_de_saisie()))
        res = super().unlink()
        if traces:
            self.env['aite.restaurant.annulation'].sudo().create(traces)
        return res

    def _aite_lignes_envoyees(self):
        """Les lignes qui portent encore un envoi, sur une addition en cours
        d'une caisse au service à table contrôlé."""
        return self.filtered(
            lambda ligne: ligne.aite_qte_envoyee > 0
            and ligne.order_id.state == 'draft'
            and ligne.order_id.config_id
            and ligne.order_id.config_id._aite_actif())
