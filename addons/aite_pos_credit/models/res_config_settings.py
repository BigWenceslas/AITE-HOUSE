# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    """
    Paramètres comptables du module POS Crédit, rattachés à la société.

    On expose ici les comptes et journaux utilisés pour matérialiser les
    ardoises et leurs remboursements en comptabilité OHADA :

    * ``credit_account_id`` : compte client (411) sur lequel l'encours est
      porté. Par défaut, le compte client par défaut de la société.
    * ``credit_journal_id`` : journal de contrepartie pour les écritures de
      remboursement (encaissement).

    Ces réglages restent optionnels : si rien n'est défini, le module se
    rabat sur les comptes par défaut d'Odoo (compte client de la fiche
    partenaire, journal de banque/caisse).
    """
    _inherit = 'res.config.settings'

    pos_credit_account_id = fields.Many2one(
        'account.account',
        string="Compte client (ardoises)",
        related='company_id.pos_credit_account_id',
        readonly=False,
        domain="[('account_type', '=', 'asset_receivable')]",
        help="Compte 411 utilisé pour porter l'encours des ardoises POS.",
    )
    pos_credit_journal_id = fields.Many2one(
        'account.journal',
        string="Journal des remboursements",
        related='company_id.pos_credit_journal_id',
        readonly=False,
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="Journal utilisé pour comptabiliser les remboursements d'ardoise.",
    )
    pos_credit_auto_entries = fields.Boolean(
        string="Comptabiliser les remboursements",
        related='company_id.pos_credit_auto_entries',
        readonly=False,
        help="Génère automatiquement l'écriture comptable (411) à la "
             "validation d'un remboursement.",
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    pos_credit_account_id = fields.Many2one(
        'account.account',
        string="Compte client (ardoises)",
        domain="[('account_type', '=', 'asset_receivable')]",
    )
    pos_credit_journal_id = fields.Many2one(
        'account.journal',
        string="Journal des remboursements d'ardoise",
        domain="[('type', 'in', ('bank', 'cash'))]",
    )
    pos_credit_auto_entries = fields.Boolean(
        string="Comptabiliser les remboursements d'ardoise",
        default=False,
    )

    def _get_pos_credit_account(self, partner=None):
        """
        Retourne le compte client à utiliser pour une ardoise.

        Priorité : compte configuré sur la société → compte client de la
        fiche partenaire → False (laisse Odoo gérer).
        """
        self.ensure_one()
        if self.pos_credit_account_id:
            return self.pos_credit_account_id
        if partner:
            account = partner.with_company(self).property_account_receivable_id
            if account:
                return account
        return self.env['account.account']
