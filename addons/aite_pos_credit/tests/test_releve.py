# -*- coding: utf-8 -*-
"""Relevé d'ardoises imprimable (recette de novembre 2026, cas F13).

Le crédit clients n'avait aucun document à remettre au client : le
relevé liste, sur une période, ses ardoises ouvertes et celles réglées,
avec la date, le ticket ou la commande d'origine, le montant, le réglé,
le reste et le total dû, en FCFA et en dates jj/mm/aaaa. Il s'imprime
depuis la fiche du client et depuis la liste des ardoises (un relevé par
client quand la sélection mêle plusieurs clients).
"""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import CreditCommon

PARTNER_REPORT = 'aite_pos_credit.action_report_releve_ardoises_partner'
CREDIT_REPORT = 'aite_pos_credit.action_report_releve_ardoises'
NBSP = '\N{NO-BREAK SPACE}'


@tagged('post_install', '-at_install', 'aite_credit')
class TestReleveArdoises(CreditCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env.user)
        cls.client_empty = cls.env['res.partner'].create({
            'name': "Client sans ardoise",
        })
        cls.cashier = cls.env['res.users'].create({
            'name': "Caissier relevé",
            'login': 'caissier.releve.test',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('aite_pos_credit.group_pos_credit_user').id,
            ])],
        })
        cls.outsider = cls.env['res.users'].create({
            'name': "Sans profil crédit (relevé)",
            'login': 'outsider.releve.test',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    def setUp(self):
        super().setUp()
        # Client A : une ardoise ouverte en partie remboursée, une réglée,
        # une annulée (jamais sur le relevé). Client B : une ardoise.
        self.open_a = self._credit(100000.0, days_ago=10)
        self._repay(self.open_a, 40000.0)
        self.paid_a = self._credit(25000.0, days_ago=5)
        self._repay(self.paid_a, 25000.0,
                    date=self.today - timedelta(days=5))
        self.cancelled_a = self._credit(15000.0, days_ago=3)
        self.cancelled_a.action_cancel()
        self.open_b = self._credit(30000.0, partner=self.client_b,
                                   days_ago=2)

    def _values(self, report, docids, data=None, user=None):
        Report = self.env['ir.actions.report']
        if user:
            Report = Report.with_user(user)
        report = Report._get_report(report)
        model = self.env['report.%s' % report.report_name]
        if user:
            model = model.with_user(user)
        return model._get_report_values(docids, data=data)

    def _html(self, report, docids, user=None):
        Report = self.env['ir.actions.report']
        if user:
            Report = Report.with_user(user)
        html, _fmt = Report._render_qweb_html(report, docids)
        return html.decode()

    def _money(self, amount):
        return self.env['report.aite_pos_credit.report_releve_partner'] \
            ._format_amount(amount, self.company.currency_id)

    # ------------------------------------------------------------------
    # Les actions d'impression
    # ------------------------------------------------------------------

    def test_print_menu_of_the_client_and_of_the_slates(self):
        """« Imprimer → Relevé d'ardoises » sur la fiche client et sur la
        liste des ardoises, réservé aux utilisateurs POS Crédit."""
        user_group = self.env.ref('aite_pos_credit.group_pos_credit_user')
        for xmlid, model in ((PARTNER_REPORT, 'res.partner'),
                             (CREDIT_REPORT, 'aite.pos.credit')):
            with self.subTest(rapport=xmlid):
                report = self.env.ref(xmlid)
                self.assertEqual(report.name, "Relevé d'ardoises")
                self.assertEqual(report.model, model)
                self.assertEqual(report.binding_model_id.model, model)
                self.assertEqual(report.binding_type, 'report')
                self.assertEqual(report.groups_id, user_group)

    # ------------------------------------------------------------------
    # Contenu et montants
    # ------------------------------------------------------------------

    def test_statement_of_a_client_lists_open_and_paid_slates(self):
        values = self._values(PARTNER_REPORT, self.client_a.ids)
        self.assertEqual(len(values['statements']), 1)
        st = values['statements'][0]
        self.assertEqual(st['partner'], self.client_a)
        names = [line['name'] for line in st['lines']]
        # Ordre chronologique : la plus ancienne d'abord ; l'annulée absente.
        self.assertEqual(names, [self.open_a.name, self.paid_a.name])
        first, second = st['lines']
        self.assertEqual((first['amount'], first['paid'], first['residual']),
                         (100000.0, 40000.0, 60000.0))
        self.assertEqual((second['amount'], second['paid'],
                          second['residual']), (25000.0, 25000.0, 0.0))
        self.assertEqual(first['state'], "Ouverte")
        self.assertEqual(second['state'], "Réglée")
        self.assertEqual(st['total_amount'], 125000.0)
        self.assertEqual(st['total_paid'], 65000.0)
        self.assertEqual(st['total_due'], 60000.0)
        # Dates jj/mm/aaaa ; période couvrant la plus ancienne ardoise.
        self.assertEqual(first['date'], (self.today - timedelta(days=10))
                         .strftime('%d/%m/%Y'))
        self.assertEqual(st['date_to'], self.today.strftime('%d/%m/%Y'))
        self.assertLessEqual(
            fields.Date.to_date(values['statements'][0]['date_from_raw']),
            self.today - timedelta(days=10))

    def test_statement_renders_with_header_amounts_and_dates(self):
        html = self._html(PARTNER_REPORT, self.client_a.ids)
        self.assertIn("Relevé d'ardoises", html)
        self.assertIn("Client Ardoise A", html)
        self.assertIn(self.company.name, html)
        self.assertIn(self.open_a.name, html)
        self.assertIn(self.paid_a.name, html)
        self.assertNotIn(self.cancelled_a.name, html)
        self.assertIn(self._money(60000.0), html)
        self.assertIn(self._money(125000.0), html)
        self.assertIn((self.today - timedelta(days=10)).strftime('%d/%m/%Y'),
                      html)
        self.assertIn("Total dû", html)

    def test_period_given_by_the_caller(self):
        """Une période explicite : l'ouverte reste (elle est due), la
        réglée hors période disparaît."""
        date_from = self.today - timedelta(days=1)
        values = self._values(PARTNER_REPORT, self.client_a.ids, data={
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(self.today),
        })
        st = values['statements'][0]
        self.assertEqual([line['name'] for line in st['lines']],
                         [self.open_a.name])
        self.assertEqual(st['total_due'], 60000.0)
        self.assertEqual(st['date_from'], date_from.strftime('%d/%m/%Y'))

    def test_client_without_slate_gets_a_clean_empty_statement(self):
        values = self._values(PARTNER_REPORT, self.client_empty.ids)
        st = values['statements'][0]
        self.assertEqual(st['lines'], [])
        self.assertEqual(st['total_due'], 0.0)
        html = self._html(PARTNER_REPORT, self.client_empty.ids)
        self.assertIn("Client sans ardoise", html)
        self.assertIn("Aucune ardoise sur la période", html)
        self.assertIn(self._money(0.0), html)

    def test_selection_of_slates_is_grouped_by_client(self):
        credits = self.open_a | self.paid_a | self.open_b
        values = self._values(CREDIT_REPORT, credits.ids)
        by_partner = {st['partner']: st for st in values['statements']}
        self.assertEqual(set(by_partner), {self.client_a, self.client_b})
        self.assertEqual(by_partner[self.client_a]['total_due'], 60000.0)
        self.assertEqual(by_partner[self.client_b]['total_due'], 30000.0)
        self.assertEqual(
            [line['name'] for line in by_partner[self.client_b]['lines']],
            [self.open_b.name])
        html = self._html(CREDIT_REPORT, credits.ids)
        self.assertEqual(html.count("Relevé d'ardoises</h2>"), 2)

    def test_a_selected_cancelled_slate_is_left_out(self):
        values = self._values(CREDIT_REPORT,
                              (self.cancelled_a | self.open_b).ids)
        self.assertEqual([st['partner'] for st in values['statements']],
                         [self.client_b])

    def test_origin_order_is_shown(self):
        """Colonne « Ticket / commande » : la commande d'origine."""
        order = self.env['sale.order'].create({
            'partner_id': self.client_a.id,
        })
        credit = self._credit(12000.0, source='sale',
                              sale_order_id=order.id)
        Report = self.env['report.aite_pos_credit.report_releve_partner']
        self.assertEqual(Report._statement_line(credit)['origin'],
                         order.name)
        self.assertEqual(Report._statement_line(self.open_a)['origin'], "")
        html = self._html(PARTNER_REPORT, self.client_a.ids)
        self.assertIn(order.name, html)

    # ------------------------------------------------------------------
    # Montants en FCFA
    # ------------------------------------------------------------------

    def test_amounts_are_written_in_fcfa(self):
        Report = self.env['report.aite_pos_credit.report_releve_partner']
        xaf = self.env.ref('base.XAF')
        self.assertEqual(Report._format_amount(60000.0, xaf),
                         "60%s000%sFCFA" % (NBSP, NBSP))
        self.assertEqual(Report._format_amount(1250000.0, xaf),
                         "1%s250%s000%sFCFA" % (NBSP, NBSP, NBSP))
        self.assertEqual(Report._format_amount(0.0, xaf),
                         "0%sFCFA" % NBSP)

    # ------------------------------------------------------------------
    # Droits
    # ------------------------------------------------------------------

    def test_a_pos_credit_user_prints_the_statement(self):
        html = self._html(PARTNER_REPORT, self.client_a.ids,
                          user=self.cashier)
        self.assertIn(self.open_a.name, html)
        html = self._html(CREDIT_REPORT, self.open_b.ids, user=self.cashier)
        self.assertIn(self.open_b.name, html)

    def test_a_user_without_pos_credit_rights_cannot(self):
        with self.assertRaises(AccessError):
            self._html(PARTNER_REPORT, self.client_a.ids, user=self.outsider)
