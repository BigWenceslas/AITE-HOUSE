# -*- coding: utf-8 -*-
"""Relevé d'ardoises imprimable (QWeb → PDF).

Deux points d'entrée, un seul document :

* depuis la **fiche du client** (``res.partner``) : ses ardoises ouvertes
  — toutes, quelle que soit leur date, puisqu'elles sont dues — et celles
  réglées sur la période ;
* depuis la **liste des ardoises** (``aite.pos.credit``) : les ardoises
  sélectionnées, regroupées par client (un relevé par client).

La période vient de ``data`` (``date_from`` / ``date_to``, pour un
assistant futur) ; à défaut elle court du 1er du mois — ou de la plus
ancienne ardoise listée si elle est antérieure — à aujourd'hui. Les
ardoises annulées ne figurent jamais sur un relevé : elles ne sont pas
dues. Les lectures passent par les droits de l'utilisateur (règles
multi-sociétés comprises) : sans profil POS Crédit, pas de relevé.
"""
from odoo import api, fields, models


class AitePosCreditStatement(models.AbstractModel):
    _name = 'aite.pos.credit.statement'
    _description = "Relevé d'ardoises (calcul commun)"

    # ------------------------------------------------------------------
    # Calcul pur (sans ORM)
    # ------------------------------------------------------------------

    @staticmethod
    def _format_number(amount, decimals=0):
        """« 1 250 000 » : milliers séparés par une espace insécable,
        décimales (s'il y en a) après une virgule."""
        text = "{:,.{d}f}".format(round(amount or 0.0, decimals), d=decimals)
        return text.replace(",", "\N{NO-BREAK SPACE}").replace(".", ",")

    def _format_amount(self, amount, currency):
        """Montant en toutes lettres de la devise : « 60 000 FCFA » pour
        le franc CFA (XAF / XOF), le symbole de la devise sinon."""
        if currency.name in ('XAF', 'XOF'):
            label = "FCFA"
        else:
            label = currency.symbol or currency.name or ""
        number = self._format_number(amount, currency.decimal_places or 0)
        return (number + "\N{NO-BREAK SPACE}" + label).strip()

    @staticmethod
    def _format_date(value):
        return value.strftime('%d/%m/%Y') if value else ""

    # ------------------------------------------------------------------
    # Construction du relevé
    # ------------------------------------------------------------------

    def _period(self, data, credits=None):
        """Bornes ``date`` de la période (voir la docstring du module)."""
        data = data or {}
        today = fields.Date.context_today(self)
        date_to = fields.Date.to_date(data.get('date_to')) or today
        date_from = fields.Date.to_date(data.get('date_from'))
        if not date_from:
            date_from = today.replace(day=1)
            dates = [d for d in (credits or self.env['aite.pos.credit'])
                     .mapped('date_open') if d]
            if dates:
                date_from = min(date_from, min(dates))
        if date_from > date_to:
            date_from, date_to = date_to, date_from
        return date_from, date_to

    def _last_payment_date(self, credit):
        dates = credit.payment_ids.filtered(
            lambda p: p.state == 'posted').mapped('date')
        return max(dates) if dates else False

    def _in_period(self, credit, date_from, date_to):
        """Ouverte → toujours (elle est due) si ouverte avant la fin de la
        période ; réglée → si ouverte ou soldée dans la période."""
        if credit.state == 'open':
            return credit.date_open <= date_to
        if credit.state == 'paid':
            if date_from <= credit.date_open <= date_to:
                return True
            last = self._last_payment_date(credit)
            return bool(last and date_from <= last <= date_to)
        return False

    def _statement_line(self, credit):
        # La référence de la commande d'origine se lit en sudo : le
        # caissier POS Crédit n'a pas forcément les droits Ventes / POS.
        origin = ""
        pos_order = credit.sudo().order_id
        sale_order = credit.sudo().sale_order_id
        if pos_order:
            origin = pos_order.pos_reference or pos_order.name or ""
        elif sale_order:
            origin = sale_order.name or ""
        states = dict(credit._fields['state']._description_selection(
            self.env))
        return {
            'id': credit.id,
            'date': self._format_date(credit.date_open),
            'name': credit.name,
            'origin': origin,
            'state': states.get(credit.state, credit.state),
            'amount': credit.amount_total,
            'paid': credit.amount_paid,
            'residual': credit.amount_residual if credit.state == 'open'
            else 0.0,
        }

    def _statement(self, partner, credits, date_from, date_to):
        credits = credits.filtered(
            lambda c: self._in_period(c, date_from, date_to)
        ).sorted(lambda c: (c.date_open, c.name or "", c.id))
        lines = [self._statement_line(c) for c in credits]
        company = credits[:1].company_id or self.env.company
        currency = company.currency_id
        total_amount = sum(line['amount'] for line in lines)
        total_paid = sum(line['paid'] for line in lines)
        total_due = sum(line['residual'] for line in lines)
        money = self._format_amount
        return {
            'partner': partner,
            'company': company,
            'currency': currency,
            'lines': lines,
            'date_from': self._format_date(date_from),
            'date_to': self._format_date(date_to),
            'date_from_raw': fields.Date.to_string(date_from),
            'date_to_raw': fields.Date.to_string(date_to),
            'printed_on': self._format_date(fields.Date.context_today(self)),
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_due': total_due,
            'open_count': sum(1 for c in credits if c.state == 'open'),
            'fmt': {
                'lines': [{
                    'amount': money(line['amount'], currency),
                    'paid': money(line['paid'], currency),
                    'residual': money(line['residual'], currency),
                } for line in lines],
                'total_amount': money(total_amount, currency),
                'total_paid': money(total_paid, currency),
                'total_due': money(total_due, currency),
            },
        }

    def _values(self, docs, statements, data):
        return {
            'doc_ids': docs.ids,
            'doc_model': docs._name,
            'docs': docs,
            'data': data,
            'statements': statements,
        }


class ReportReleveArdoisesPartner(models.AbstractModel):
    """Relevé imprimé depuis la fiche (ou la liste) des clients."""
    _name = 'report.aite_pos_credit.report_releve_partner'
    _inherit = 'aite.pos.credit.statement'
    _description = "Relevé d'ardoises d'un client"

    @api.model
    def _get_report_values(self, docids, data=None):
        partners = self.env['res.partner'].browse(docids)
        Credit = self.env['aite.pos.credit']
        statements = []
        for partner in partners:
            credits = Credit.search([
                ('partner_id', '=', partner.id),
                ('company_id', '=', self.env.company.id),
                ('state', 'in', ('open', 'paid')),
            ])
            date_from, date_to = self._period(
                data, credits.filtered(lambda c: c.state == 'open'))
            statements.append(
                self._statement(partner, credits, date_from, date_to))
        return self._values(partners, statements, data)


class ReportReleveArdoises(models.AbstractModel):
    """Relevé imprimé depuis la liste des ardoises : un par client."""
    _name = 'report.aite_pos_credit.report_releve_ardoises'
    _inherit = 'aite.pos.credit.statement'
    _description = "Relevé des ardoises sélectionnées"

    @api.model
    def _get_report_values(self, docids, data=None):
        credits = self.env['aite.pos.credit'].browse(docids).exists() \
            .filtered(lambda c: c.state in ('open', 'paid'))
        # Lecture sous les droits de l'utilisateur (AccessError sinon).
        credits.check_access('read')
        date_from, date_to = self._period(data, credits)
        statements = []
        for partner in credits.mapped('partner_id').sorted(
                lambda p: (p.name or "", p.id)):
            statements.append(self._statement(
                partner, credits.filtered(lambda c: c.partner_id == partner),
                date_from, date_to))
        return self._values(credits, statements, data)
