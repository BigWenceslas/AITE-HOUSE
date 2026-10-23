# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    """
    Seuils d'écart de caisse, par société.

    À la clôture, un manquant de caisse (montant compté inférieur au
    montant attendu) est classé « Modéré », « Élevé » ou « Critique »
    selon ces deux montants. Ils étaient des constantes du code
    (``pos.session.DISCREPANCY_THRESHOLD_*``) : la direction ne pouvait
    pas les adapter à la taille de sa caisse sans développeur (écart
    n° 67 ; données de référence modifiables sans code). Les constantes
    restent les valeurs par défaut, calibrées pour le FCFA.
    """
    _inherit = 'res.company'

    aite_pos_gap_med = fields.Monetary(
        string="Écart de caisse « Élevé » à partir de",
        currency_field='currency_id',
        default=100000.0,
        help="À la clôture d'une session, un manquant de caisse égal ou "
             "supérieur à ce montant classe la session « Élevé » dans "
             "l'onglet Écarts de caisse de l'analyse des ventes.",
    )
    aite_pos_gap_high = fields.Monetary(
        string="Écart de caisse « Critique » à partir de",
        currency_field='currency_id',
        default=200000.0,
        help="À la clôture d'une session, un manquant de caisse égal ou "
             "supérieur à ce montant classe la session « Critique » "
             "(rouge), à traiter en priorité.",
    )

    @api.constrains('aite_pos_gap_med', 'aite_pos_gap_high')
    def _check_aite_pos_gap_thresholds(self):
        for company in self:
            if not 0 < company.aite_pos_gap_med < company.aite_pos_gap_high:
                raise ValidationError(_(
                    "Le seuil « Élevé » d'écart de caisse doit être positif "
                    "et inférieur au seuil « Critique »."))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ``currency_id`` : devise de la société, posée sur les réglages par
    # le module Comptabilité (dépendance du Point de Vente).
    aite_pos_gap_med = fields.Monetary(
        related='company_id.aite_pos_gap_med', readonly=False,
        currency_field='currency_id')
    aite_pos_gap_high = fields.Monetary(
        related='company_id.aite_pos_gap_high', readonly=False,
        currency_field='currency_id')
