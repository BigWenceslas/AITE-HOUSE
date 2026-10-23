# -*- coding: utf-8 -*-
"""Écarts non bloquants relevés en tournant les vidéos (ECARTS.md).

n° 37 (dates lisibles du tableau de bord), n° 66 (aide de l'écran vide
« Remboursements »), n° 74 (mode de paiement « Ardoise client » créé à
l'installation).
"""
from datetime import date
from unittest.mock import patch

from odoo.tests import tagged

from .common import CreditCommon
from .. import hooks


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditEcartsErgonomie(CreditCommon):

    # ------------------------------------------------------------------
    # N° 74 — le post_init_hook crée le mode « Ardoise client »
    # ------------------------------------------------------------------

    def _credit_methods(self, company=None):
        return self.env['pos.payment.method'].search([
            ('is_aite_credit', '=', True),
            ('company_id', '=', (company or self.company).id),
        ])

    def _has_receivable(self, company=None):
        company = company or self.company
        return bool(self.env['account.account'].search_count([
            ('account_type', '=', 'asset_receivable'),
            ('company_ids', 'in', company.id),
        ]))

    def test_installation_cree_le_mode_ardoise(self):
        """Base installée : la société dotée d'un plan comptable a son mode
        « Ardoise client » (sans dépendre du jeu de démonstration)."""
        self.assertTrue(self._has_receivable(),
                        "La base de test doit porter un plan comptable.")
        methods = self._credit_methods()
        self.assertTrue(methods, "Aucun mode « ardoise » après installation.")
        self.assertIn("Ardoise client", methods.mapped('name'))
        # Preuve que c'est le hook qui l'a créé : le jeu de démonstration
        # (aite_demo_data, installé dans le même passage) crée aussi un mode
        # « Ardoise client » s'il n'en trouve pas, mais sans « Identifier le
        # client ». Le nom seul ne prouvait rien.
        hooked = methods.filtered(
            lambda m: m.name == "Ardoise client" and m.split_transactions)
        self.assertTrue(hooked, "Le mode « Ardoise client » ne vient pas du "
                                "post_init_hook (« Identifier le client » "
                                "décoché).")
        self.assertEqual(hooked[:1].type, 'pay_later')

    def test_hook_sur_base_vierge(self):
        """Société sans mode ardoise : le hook le crée, de type « Compte
        client », sur un compte client, et l'ajoute aux caisses."""
        self._credit_methods().write({'active': False})
        self.company.pos_credit_account_id = False
        config = self.env['pos.config'].create({
            'name': "Caisse sans ardoise (hook)",
        })

        hooks.post_init_hook(self.env)

        method = self._credit_methods()
        self.assertEqual(len(method), 1)
        self.assertEqual(method.name, "Ardoise client")
        self.assertEqual(method.type, 'pay_later')
        self.assertTrue(method.split_transactions)
        self.assertEqual(method.receivable_account_id.account_type,
                         'asset_receivable')
        self.assertEqual(self.company.pos_credit_account_id,
                         method.receivable_account_id)
        self.assertIn(method, config.payment_method_ids)

    def test_hook_sans_plan_comptable(self):
        """Base neuve : Odoo 18 charge le plan comptable APRÈS les hooks
        d'installation. Le mode est créé quand même, sans compte imposé (la
        créance va au compte client de chaque client)."""
        self._credit_methods().write({'active': False})
        self.company.pos_credit_account_id = False
        Account = type(self.env['account.account'])
        Company = type(self.env['res.company'])
        with patch.object(Company, '_get_pos_credit_account',
                          lambda rec, partner=None: rec.env['account.account']), \
                patch.object(Account, 'search',
                             lambda rec, domain, *a, **k: rec.browse()):
            hooks.post_init_hook(self.env)
        method = self._credit_methods()
        self.assertEqual(len(method), 1)
        self.assertEqual(method.name, "Ardoise client")
        self.assertTrue(method.split_transactions)
        self.assertFalse(method.receivable_account_id)
        self.assertFalse(self.company.pos_credit_account_id)

    def test_hook_idempotent(self):
        self._credit_methods().write({'active': False})
        hooks.post_init_hook(self.env)
        hooks.post_init_hook(self.env)
        self.assertEqual(len(self._credit_methods()), 1)

    def test_hook_journalise_un_echec(self):
        """Un échec n'interrompt pas l'installation, mais il est journalisé
        (il était avalé sans trace)."""
        with patch.object(hooks, '_setup_company',
                          side_effect=ValueError("plan comptable absent")):
            with self.assertLogs('odoo.addons.aite_pos_credit.hooks',
                                 level='WARNING') as logs:
                hooks.post_init_hook(self.env)
        self.assertIn("Ardoise client", "\n".join(logs.output))

    # ------------------------------------------------------------------
    # N° 66 — aide de l'écran vide « Remboursements »
    # ------------------------------------------------------------------

    def test_aide_ecran_vide_remboursements(self):
        action = self.env.ref('aite_pos_credit.action_aite_pos_credit_payment')
        help_txt = action.help or ""
        self.assertIn('o_view_nocontent', help_txt)
        self.assertGreaterEqual(len(help_txt), 120)
        # L'aide dit quoi faire : le geste réel de la fiche ardoise.
        self.assertIn("Enregistrer un remboursement", help_txt)

    # ------------------------------------------------------------------
    # N° 37 — dates du tableau de bord au format jj/mm/aaaa
    # ------------------------------------------------------------------

    def test_dates_lisibles_du_tableau_de_bord(self):
        credit = self._credit(80000.0, date_open=date(2026, 9, 20))
        self._repay(credit, 30000.0, date=date(2026, 10, 5))
        Dash = self.env['aite.pos.credit.dashboard']

        recent = Dash.get_recent_payments('2026-10-01', '2026-10-31')
        row = next(r for r in recent if r['credit_ref'] == credit.name)
        self.assertEqual(row['date_label'], "05/10/2026")
        # La date ISO reste fournie : c'est le contrat du cockpit Direction.
        self.assertEqual(row['date'], "2026-10-05")

        top = Dash.get_top_debtors(limit=50)
        debtor = next(r for r in top if r['partner_id'] == self.client_a.id)
        self.assertEqual(debtor['last_payment_label'], "05/10/2026")
        self.assertEqual(debtor['last_payment'], "2026-10-05")

    def test_debiteur_sans_remboursement(self):
        self._credit(15000.0, partner=self.client_b)
        top = self.env['aite.pos.credit.dashboard'].get_top_debtors(limit=50)
        debtor = next(r for r in top if r['partner_id'] == self.client_b.id)
        self.assertFalse(debtor['last_payment'])
        self.assertEqual(debtor['last_payment_label'], "")
