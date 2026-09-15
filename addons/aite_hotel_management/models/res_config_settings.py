# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    """
    Réglages hôteliers portés par la société.

    Comptabilité (mêmes principes que ``aite_pos_credit``) :

    * ``hotel_receivable_account_id`` : compte client (411) crédité par
      les règlements de folio ; à défaut, compte client du partenaire.
    * ``hotel_payment_journal_id`` : journal de trésorerie des
      encaissements ; à défaut, caisse pour les espèces, banque sinon.
    * ``hotel_auto_entries`` : active la génération des écritures.

    Automatisations :

    * ``hotel_send_confirmation`` : e-mail de confirmation auto.
    * ``hotel_auto_no_show`` + ``hotel_no_show_grace`` : bascule
      automatique en no-show après le délai de grâce (cron quotidien).
    * ``hotel_auto_daily_hk`` : ménage quotidien auto des chambres
      occupées.
    * ``hotel_inspection_required`` : la recouche passe la chambre en
      « à inspecter » plutôt que directement « propre ».
    """
    _inherit = 'res.company'

    hotel_receivable_account_id = fields.Many2one(
        'account.account',
        string="Compte client (hôtel)",
        domain="[('account_type', '=', 'asset_receivable')]",
    )
    hotel_payment_journal_id = fields.Many2one(
        'account.journal',
        string="Journal des encaissements hôtel",
        domain="[('type', 'in', ('bank', 'cash'))]",
    )
    hotel_auto_entries = fields.Boolean(
        string="Comptabiliser les règlements de folio",
        default=True,
    )
    hotel_send_confirmation = fields.Boolean(
        # Libellé qualifié : ``aite_slot_booking`` porte un booléen
        # homonyme sur res.company ; deux champs de même libellé rendent
        # l'écran Paramètres et les exports ambigus.
        string="E-mail de confirmation automatique des réservations hôtel",
        default=False,
    )
    hotel_auto_no_show = fields.Boolean(
        string="No-show automatique",
        default=False,
    )
    hotel_no_show_grace = fields.Integer(
        string="Délai de grâce no-show (heures)",
        default=24,
    )
    hotel_auto_daily_hk = fields.Boolean(
        string="Ménage quotidien automatique",
        default=True,
    )
    hotel_inspection_required = fields.Boolean(
        string="Inspection après recouche",
        default=False,
    )

    def _get_hotel_receivable_account(self, partner=None):
        """
        Compte client à créditer par un règlement de folio.

        Priorité : compte configuré sur la société → compte client de la
        fiche partenaire → recordset vide (Odoo gère).
        """
        self.ensure_one()
        if self.hotel_receivable_account_id:
            return self.hotel_receivable_account_id
        if partner:
            account = partner.with_company(
                self).property_account_receivable_id
            if account:
                return account
        return self.env['account.account']


class ResConfigSettings(models.TransientModel):
    """Exposition des réglages hôteliers dans Paramètres généraux."""
    _inherit = 'res.config.settings'

    hotel_receivable_account_id = fields.Many2one(
        'account.account',
        string="Compte client (hôtel)",
        related='company_id.hotel_receivable_account_id', readonly=False,
        domain="[('account_type', '=', 'asset_receivable')]",
        help="Compte 411 crédité par les règlements de folio.",
    )
    hotel_payment_journal_id = fields.Many2one(
        'account.journal',
        string="Journal des encaissements",
        related='company_id.hotel_payment_journal_id', readonly=False,
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="Journal de trésorerie des règlements de folio.",
    )
    hotel_auto_entries = fields.Boolean(
        string="Comptabiliser les règlements",
        related='company_id.hotel_auto_entries', readonly=False,
        help="Génère l'écriture débit trésorerie / crédit 411 à chaque "
             "règlement de folio.",
    )
    hotel_send_confirmation = fields.Boolean(
        string="Confirmation par e-mail automatique",
        related='company_id.hotel_send_confirmation', readonly=False,
        help="Envoie la confirmation au client dès qu'une réservation "
             "est confirmée (si un e-mail est renseigné).",
    )
    hotel_auto_no_show = fields.Boolean(
        string="No-show automatique",
        related='company_id.hotel_auto_no_show', readonly=False,
        help="Le cron quotidien bascule en no-show les réservations "
             "confirmées dont l'arrivée est dépassée du délai de grâce.",
    )
    hotel_no_show_grace = fields.Integer(
        string="Délai de grâce (heures)",
        related='company_id.hotel_no_show_grace', readonly=False,
    )
    hotel_auto_daily_hk = fields.Boolean(
        string="Ménage quotidien automatique",
        related='company_id.hotel_auto_daily_hk', readonly=False,
        help="Crée chaque matin une tâche de ménage pour chaque chambre "
             "occupée.",
    )
    hotel_inspection_required = fields.Boolean(
        string="Inspection après recouche",
        related='company_id.hotel_inspection_required', readonly=False,
        help="Après la recouche d'un départ, la chambre passe « à "
             "inspecter » au lieu de « propre ».",
    )
