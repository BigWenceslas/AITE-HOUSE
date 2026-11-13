# -*- coding: utf-8 -*-
"""18.0.2.0.6 — AH-01 : l'ardoise ne naît que d'une commande réglée et
s'annule avec elle.

Avant cette version, une addition enregistrée encore ouverte (service à
table : envoi en cuisine, retour au plan) avec un paiement « ardoise »
ouvrait déjà une dette ; annulée ensuite, elle la laissait ouverte. Le code
corrigé n'agit qu'à partir de maintenant ; ce script reprend l'existant :

* ardoise ouverte, sans aucun remboursement, dont la commande est annulée :
  annulée (ce que fait désormais l'annulation de la commande) ;
* ardoise ouverte dont la commande est annulée mais qui a déjà reçu un
  remboursement : laissée telle quelle et signalée (avertissement) ; le
  remboursement est à annuler d'abord, à la main ;
* ardoise ouverte rattachée à une commande encore ouverte : laissée telle
  quelle et signalée (avertissement) ; son montant suit les paiements saisis
  avant l'envoi, à contrôler quand la table sera réglée ou annulée.

Une ardoise sans commande peut avoir été saisie à la main : elle n'est ni
touchée ni signalée. Rien d'autre n'est modifié.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger('odoo.addons.aite_pos_credit.migrations')


def _references(credits):
    return ", ".join("%s (commande %s)" % (c.name, c.order_id.name or c.order_id.id)
                     for c in credits)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    ouvertes = env['aite.pos.credit'].search([
        ('state', '=', 'open'),
        ('order_id', '!=', False),
        ('order_id.state', 'in', ('cancel', 'draft')),
    ])
    sur_annulee = ouvertes.filtered(lambda c: c.order_id.state == 'cancel')
    a_annuler = sur_annulee.filtered(lambda c: not c.amount_paid)
    remboursees = sur_annulee - a_annuler
    sur_table_ouverte = ouvertes - sur_annulee

    if a_annuler:
        a_annuler.action_cancel()
        _logger.info(
            "POS Crédit (AH-01) : ardoises annulées avec leur commande "
            "annulée (%d) : %s.", len(a_annuler), _references(a_annuler))
    if remboursees:
        _logger.warning(
            "POS Crédit (AH-01) : ardoises encore ouvertes sur une commande "
            "annulée, déjà remboursées en partie (%d), à contrôler : annulez "
            "le remboursement, puis l'ardoise : %s.",
            len(remboursees), _references(remboursees))
    if sur_table_ouverte:
        _logger.warning(
            "POS Crédit (AH-01) : ardoises ouvertes sur une addition encore "
            "ouverte (%d), à contrôler quand la table sera réglée ou "
            "annulée : %s.", len(sur_table_ouverte), _references(sur_table_ouverte))
