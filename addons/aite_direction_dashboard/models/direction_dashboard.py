# -*- coding: utf-8 -*-
"""
Direction — Vue consolidée (LAVERANDAH).

ORCHESTRATEUR : ce modèle n'invente aucune formule métier. Il appelle,
côté serveur, les moteurs des quatre tableaux de bord spécialisés —
``aite.pos.dashboard``, ``aite.pos.credit.dashboard``,
``aite.stock.dashboard``, ``aite.purchase.dashboard`` — et n'ajoute que
la couche TRANSVERSALE : cash à risque, position nette clients /
fournisseurs, série d'encours reconstituée, échéancier fournisseurs en
tranches, liste d'actions du gérant.

Cette couche transversale est écrite en fonctions PURES (@staticmethod,
entrées / sorties en types simples) : les tests les extraient et les
exécutent telles quelles, sans Odoo.

Conventions de filtres (contrat avec le JS) :
  * date_from / date_to : 'YYYY-MM-DD' (bornes du sélecteur) ;
  * config_id : id pos.config ou None (toutes caisses) ;
  * tranche : None | 'matin' | 'am' | 'soir' | 'nuit' — convertie en
    hour_from / hour_to pour aite.pos.dashboard (borne haute INCLUSIVE,
    passage minuit géré par le moteur POS) ;
  * weekdays : liste ISO (1 = lundi … 7 = dimanche) ou None.
La caisse, la tranche et les jours ne s'appliquent qu'aux DONNÉES DE
VENTE (la caisse s'applique aussi au crédit, qui la connaît) ; les
photos (encours, dettes, stock) les ignorent — c'est le contrat
« période vs photo » du prototype validé.
"""
from datetime import date, timedelta

from odoo import api, fields, models

TRANCHES = {
    'matin': (6, 11),    # 6 h 00 → 11 h 59
    'am': (12, 17),      # 12 h 00 → 17 h 59
    'soir': (18, 22),    # 18 h 00 → 22 h 59
    'nuit': (23, 5),     # 23 h 00 → 5 h 59 (passage minuit)
}

AGE_BUCKETS = ((0, 30, '0_30'), (31, 60, '31_60'),
               (61, 90, '61_90'), (91, None, '90p'))


class AiteDirectionDashboard(models.AbstractModel):
    _name = 'aite.direction.dashboard'
    _description = "Direction — vue consolidée (orchestrateur)"

    # ==================================================================
    # Couche transversale PURE (extraite et rejouée par les tests)
    # ==================================================================

    @staticmethod
    def _rows(raw):
        """
        Normalise une réponse moteur en LISTE de lignes.

        Certains moteurs renvoient la liste nue, d'autres l'enveloppent
        (ex. ``get_coverage_by_category`` → ``{'rows': [...], ...}``).
        Accepte liste, dict avec clé ``rows``, ou None.
        """
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            rows = raw.get('rows')
            if isinstance(rows, list):
                return rows
        return []

    @staticmethod
    def _hours_for(tranche):
        """'soir' → (18, 22) ; inconnu / None → (None, None)."""
        return TRANCHES.get(tranche, (None, None))

    @staticmethod
    def _cash_at_risk(late_amount, coulage):
        """Ardoises en retard + coulage de la période — jamais négatif."""
        return max(0.0, (late_amount or 0.0)) + max(0.0, (coulage or 0.0))

    @staticmethod
    def _net_position(outstanding, supplier_debt):
        """
        Crédits clients − dettes fournisseurs.

        :returns: (solde, lecture) — lecture ∈ 'clients' (les clients
            vous financent… rare), 'fournisseurs', 'equilibre'.
        """
        net = (outstanding or 0.0) - (supplier_debt or 0.0)
        if abs(net) < 1.0:
            return 0.0, 'equilibre'
        return net, ('clients' if net > 0 else 'fournisseurs')

    @staticmethod
    def _age_bucket(days):
        """Ancienneté en jours → clé de tranche ('0_30' … '90p')."""
        d = max(0, int(days or 0))
        for lo, hi, key in AGE_BUCKETS:
            if hi is None or d <= hi:
                if d >= lo or key == '0_30':
                    return key
        return '90p'

    @staticmethod
    def _bucket_supplier_invoices(rows, today):
        """
        Factures fournisseurs ouvertes → échéancier + miroir.

        :param rows: [{'amount', 'date' 'YYYY-MM-DD', 'planned'
            'YYYY-MM-DD'|None, 'days_late': int}]
        :param today: 'YYYY-MM-DD'
        :returns: dict {
            'schedule': {'overdue', 'w0', 'w1', 'w2', 'w3p'} montants,
            'schedule_counts': idem en nombre,
            'aging': {'0_30','31_60','61_90','90p'} sur la date de
            facture (miroir fournisseurs)}
        """
        t = fields.Date.to_date(today)
        sched = {'overdue': 0.0, 'w0': 0.0, 'w1': 0.0, 'w2': 0.0,
                 'w3p': 0.0}
        counts = {k: 0 for k in sched}
        aging = {'0_30': 0.0, '31_60': 0.0, '61_90': 0.0, '90p': 0.0}
        for r in rows or []:
            amt = float(r.get('amount') or 0.0)
            if (r.get('days_late') or 0) > 0:
                key = 'overdue'
            else:
                planned = r.get('planned')
                if not planned:
                    key = 'w3p'
                else:
                    dp = fields.Date.to_date(planned)
                    delta = (dp - t).days
                    if delta < 0:
                        key = 'overdue'
                    elif delta <= 6:
                        key = 'w0'
                    elif delta <= 13:
                        key = 'w1'
                    elif delta <= 20:
                        key = 'w2'
                    else:
                        key = 'w3p'
            sched[key] += amt
            counts[key] += 1
            dref = r.get('date')
            age = (t - fields.Date.to_date(dref)).days if dref else 0
            aging[AiteDirectionDashboard._age_bucket(age)] += amt
        return {'schedule': sched, 'schedule_counts': counts,
                'aging': aging}

    @staticmethod
    def _encours_series(current, rows):
        """
        Encours d'ardoises fin de mois, reconstitué à rebours.

        encours(m) = encours(m+1) − (opened − recovered)(m+1) ;
        dernier point = encours actuel.

        :param rows: [{'period', 'opened', 'recovered'}] chronologiques
        :returns: [{'period', 'outstanding'}]
        """
        out, run = [], float(current or 0.0)
        for r in reversed(rows or []):
            out.append({'period': r.get('period'),
                        'outstanding': max(0.0, run)})
            run -= float(r.get('opened') or 0.0) \
                - float(r.get('recovered') or 0.0)
        out.reverse()
        return out

    @staticmethod
    def _zip_trends(pos_rows, bill_rows, encours_rows):
        """
        Aligne CA / achats / encours par période (clé 'period').
        Les périodes absentes d'une source valent 0.
        """
        periods, seen = [], set()
        for src in (pos_rows, bill_rows, encours_rows):
            for r in src or []:
                p = r.get('period')
                if p and p not in seen:
                    seen.add(p)
                    periods.append(p)
        periods = periods[-6:]
        ca = {r['period']: r.get('ca', 0.0) for r in pos_rows or []}
        bills = {r['period']: r.get('bills', 0.0)
                 for r in bill_rows or []}
        enc = {r['period']: r.get('outstanding', 0.0)
               for r in encours_rows or []}
        return [{'period': p, 'ca': ca.get(p, 0.0),
                 'bills': bills.get(p, 0.0),
                 'outstanding': enc.get(p, 0.0)} for p in periods]

    @staticmethod
    def _penalty_rows(stock_rows, limit=4):
        """
        Références en Rupture / Critique, les plus pénalisantes d'abord.

        Perte estimée / jour = ventes moy. jour × prix de vente si les
        deux sont connus, sinon repli sur la valeur immobilisée.
        """
        picked = []
        for r in stock_rows or []:
            if r.get('status') not in ('Rupture', 'Critique'):
                continue
            vday = float(r.get('vday') or 0.0)
            price = float(r.get('price') or r.get('list_price') or 0.0)
            loss = vday * price
            picked.append({
                'name': r.get('name', ''),
                'status': r.get('status'),
                'couv': float(r.get('couv') or 0.0),
                'cmd': float(r.get('cmd') or 0.0),
                'loss_day': loss,
                'value': float(r.get('value') or 0.0),
            })
        picked.sort(key=lambda x: (-x['loss_day'], -x['value']))
        return picked[:limit]

    @staticmethod
    def _build_actions(inp):
        """
        Liste d'actions du gérant, à partir d'agrégats simples.

        :param inp: dict {
            'debtors': [{'name','outstanding','max_age'}],
            'overdue_amount', 'overdue_count',
            'week_bills': [{'partner','amount','planned'}],
            'penalties': sortie de _penalty_rows,
            'cmd_value', 'cmd_refs',
            'coul_pct', 'coul_seuil', 'coul_amount',
            'gap_net', 'price_up': [{'name','partner','delta_pct'}],
            'ann_amount', 'ann_count', 'rem_amount', 'rem_pct'}
        :returns: {'sections': [{key,title,priority,source,rows:[{label,
            amount,hint,action}]}], 'count': N}
        """
        S = []

        def sec(key, title, prio, source, rows):
            rows = [r for r in rows if r]
            if rows:
                S.append({'key': key, 'title': title, 'priority': prio,
                          'source': source, 'rows': rows})

        deb = [{'label': "Relancer %s" % d.get('name', ''),
                'amount': d.get('outstanding', 0.0),
                'hint': "%d j" % int(d.get('max_age') or 0),
                'action': 'credit'}
               for d in (inp.get('debtors') or [])
               if (d.get('max_age') or 0) > 30][:3]
        sec('credit', "Ardoises anciennes", 'urgent', "Crédit", deb)

        rows = []
        if inp.get('overdue_amount'):
            rows.append({'label': "Régulariser %d facture(s) échue(s)"
                         % int(inp.get('overdue_count') or 0),
                         'amount': inp['overdue_amount'],
                         'hint': "échu", 'action': 'purchase'})
        rows += [{'label': "Payer %s" % b.get('partner', ''),
                  'amount': b.get('amount', 0.0),
                  'hint': b.get('planned') or '',
                  'action': 'purchase'}
                 for b in (inp.get('week_bills') or [])[:3]]
        sec('purchase', "Fournisseurs", 'urgent', "Achats", rows)

        rows = [{'label': "Commander %s" % p['name'],
                 'amount': p['loss_day'],
                 'hint': ("perd / jour" if p['loss_day']
                          else p['status'].lower()),
                 'action': 'stock'} for p in
                (inp.get('penalties') or [])[:2]]
        if inp.get('cmd_value'):
            rows.append({'label': "Lancer la commande suggérée "
                         "(%d réfs)" % int(inp.get('cmd_refs') or 0),
                         'amount': inp['cmd_value'], 'hint': "sous seuil",
                         'action': 'stock'})
        sec('stock', "Stock", 'urgent', "Stock", rows)

        rows = []
        if (inp.get('coul_pct') or 0.0) > (inp.get('coul_seuil') or 0.0):
            rows.append({'label': "Coulage au-dessus du seuil "
                         "(%.1f %% > %.0f %%)" % (inp['coul_pct'],
                                                  inp['coul_seuil']),
                         'amount': inp.get('coul_amount', 0.0),
                         'hint': "inventaire tournant",
                         'action': 'stock'})
        if (inp.get('gap_net') or 0.0) < 0:
            rows.append({'label': "Écarts d'inventaire négatifs",
                         'amount': abs(inp['gap_net']),
                         'hint': "contrôler", 'action': 'stock'})
        sec('coulage', "Coulage & écarts", 'watch', "Stock", rows)

        rows = []
        if inp.get('ann_count'):
            rows.append({'label': "Annulations / retours : %d ticket(s)"
                         % int(inp['ann_count']),
                         'amount': inp.get('ann_amount', 0.0),
                         'hint': "par caisse", 'action': 'pos'})
        if (inp.get('rem_pct') or 0.0) >= 3.0:
            rows.append({'label': "Remises élevées (%.1f %% du CA)"
                         % inp['rem_pct'],
                         'amount': inp.get('rem_amount', 0.0),
                         'hint': "par vendeur", 'action': 'pos'})
        sec('pos', "Caisse", 'watch', "POS", rows)

        rows = [{'label': "Renégocier %s" % p.get('name', ''),
                 'amount': None,
                 'hint': "%+.0f %% · %s" % (p.get('delta_pct') or 0.0,
                                            p.get('partner', '')),
                 'action': 'purchase'}
                for p in (inp.get('price_up') or [])[:2]]
        sec('prices', "Prix d'achat", 'watch', "Achats", rows)

        return {'sections': S,
                'count': sum(len(s['rows']) for s in S)}

    # ==================================================================
    # Helpers internes (env)
    # ==================================================================

    def _pos_filters(self, tranche, weekdays):
        hf, ht = self._hours_for(tranche)
        f = {'compare': True}
        if hf is not None:
            f.update(hour_from=hf, hour_to=ht)
        if weekdays:
            f['weekdays'] = [int(w) for w in weekdays]
        return f

    def _engines(self):
        e = self.env
        return (e['aite.pos.dashboard'], e['aite.pos.credit.dashboard'],
                e['aite.stock.dashboard'], e['aite.purchase.dashboard'])

    def _heatmap(self, date_from, date_to, config_id=None):
        """CA par (jour ISO, heure) sur le report POS — dégradation
        douce si les champs n'existent pas."""
        Report = self.env['aite.pos.daily.report']
        if 'hour' not in Report._fields or 'weekday' not in Report._fields:
            return []
        domain = [('date', '>=', date_from), ('date', '<=', date_to)]
        if config_id:
            domain.append(('config_id', '=', int(config_id)))
        rows = Report.read_group(
            domain, ['price_subtotal'], ['weekday', 'hour'], lazy=False)
        return [{'weekday': int(r.get('weekday') or 0),
                 'hour': int(r.get('hour') or 0),
                 'ca': r.get('price_subtotal') or 0.0} for r in rows]

    # ==================================================================
    # RPC
    # ==================================================================

    @api.model
    def get_meta(self):
        pos, cred, stock, pur = self._engines()
        company = self.env.company
        cur = company.currency_id
        configs = self.env['pos.config'].search_read(
            [('company_id', 'in', (False, company.id))], ['name'])
        cats = self.env['pos.category'].search_read(
            [('parent_id', '=', False)], ['name'])
        return {
            'company': company.name,
            'currency': {'symbol': cur.symbol,
                         'position': cur.position},
            'configs': configs,
            'pos_categories': cats,
            'locations': stock.get_locations(),
            'suppliers': pur.get_suppliers(),
            'today': fields.Date.context_today(self).isoformat(),
        }

    @api.model
    def get_overview(self, date_from, date_to, config_id=None,
                     tranche=None, weekdays=None):
        pos, cred, stock, pur = self._engines()
        f = self._pos_filters(tranche, weekdays)
        p = pos.get_kpis(date_from, date_to, config_id=config_id,
                         filters=f)
        c = cred.get_kpis(date_from, date_to, config_id=config_id)
        aging_c = self._rows(cred.get_aging(config_id=config_id))
        s = stock.get_kpis(date_from, date_to)
        a = pur.get_kpis(date_from, date_to)
        inv = self._rows(pur.get_open_invoices())
        today = fields.Date.context_today(self).isoformat()
        buckets = self._bucket_supplier_invoices(inv, today)
        risk = self._cash_at_risk(c.get('late_amount'), s.get('pertes'))
        net, net_side = self._net_position(
            c.get('outstanding'), a.get('encours'))

        pos_ev = self._rows(pos.get_monthly_evolution(
            (fields.Date.context_today(self)
             - timedelta(days=183)).isoformat(), today,
            config_id=config_id))
        flux = self._rows(pur.get_flux_months(6))
        cred_ev = self._rows(cred.get_evolution(6,
                                                config_id=config_id))
        enc = self._encours_series(c.get('outstanding'), cred_ev)
        trends = self._zip_trends(pos_ev, flux, enc)

        aging_clients = {'0_30': 0.0, '31_60': 0.0,
                         '61_90': 0.0, '90p': 0.0}
        late_clients = 0
        for r in (aging_c or []):
            # Le moteur Crédit expose désormais la clé de tranche ; on la
            # reprend telle quelle. Le repli par bornes ne sert plus que
            # si un module tiers renvoie un format plus ancien.
            key = r.get('key')
            if key not in aging_clients:
                lo = int(r.get('min') or 0)
                hi = r.get('max')
                key = ('90p' if lo >= 90
                       else '61_90' if lo >= 60
                       else '31_60' if lo >= 30
                       else '0_30' if hi not in (None, False)
                       else '90p')
            aging_clients[key] += r.get('amount', 0.0)
            if key != '0_30':
                late_clients += r.get('count', 0)
        return {
            'pos': p, 'credit': c, 'stock': s, 'purchase': a,
            'cash_risk': risk,
            'cash_risk_parts': {'late': c.get('late_amount', 0.0),
                                'coulage': s.get('pertes', 0.0)},
            'net_position': net, 'net_side': net_side,
            'supplier_buckets': buckets,
            'aging_clients': aging_clients,
            'trends': trends,
            'badges': {
                'credit': late_clients,
                'stock': (s.get('rupt_count', 0)
                          + s.get('crit_count', 0)),
                'purchase': a.get('retard_count', 0),
            },
        }

    @api.model
    def get_pos_tab(self, date_from, date_to, config_id=None,
                    tranche=None, weekdays=None):
        pos, cred, _s, _a = self._engines()
        f = self._pos_filters(tranche, weekdays)
        k = pos.get_kpis(date_from, date_to, config_id=config_id,
                         filters=f)
        c = cred.get_kpis(date_from, date_to, config_id=config_id)
        return {
            'kpis': k,
            'top_products': self._rows(pos.get_top_products(
                date_from, date_to, limit=5, config_id=config_id)),
            'categories': self._rows(pos.get_category_breakdown(
                date_from, date_to, config_id=config_id)),
            'payments': self._rows(pos.get_payment_breakdown(
                date_from, date_to, config_id=config_id)),
            'heatmap': self._heatmap(date_from, date_to, config_id),
            'new_credits': {'amount': c.get('opened_amount', 0.0),
                            'count': c.get('new_credits', 0),
                            'pct': (c.get('opened_amount', 0.0)
                                    / k['ca'] * 100.0)
                            if k.get('ca') else 0.0},
        }

    @api.model
    def get_credit_tab(self, date_from, date_to, config_id=None,
                       source=None):
        _p, cred, _s, _a = self._engines()
        k = cred.get_kpis(date_from, date_to, config_id=config_id,
                          source=source)
        ev = self._rows(cred.get_evolution(6, config_id=config_id,
                                           source=source))
        return {
            'kpis': k,
            'aging': self._rows(cred.get_aging(
                config_id=config_id, source=source)),
            'top_debtors': self._rows(cred.get_top_debtors(
                limit=5, config_id=config_id, source=source)),
            'recent_payments': self._rows(cred.get_recent_payments(
                date_from, date_to, limit=5, config_id=config_id)),
            'evolution': self._encours_series(k.get('outstanding'), ev),
        }

    @api.model
    def get_stock_tab(self, date_from, date_to, location_id=None,
                      categ_id=None):
        _p, _c, stock, _a = self._engines()
        rows = self._rows(stock.get_stock_list(
            location_id=location_id, categ_id=categ_id))
        return {
            'kpis': stock.get_kpis(date_from, date_to,
                                   location_id=location_id,
                                   categ_id=categ_id),
            'by_category': self._rows(stock.get_stock_by_category(
                location_id=location_id)),
            'coverage': self._rows(stock.get_coverage_by_category(
                location_id=location_id, categ_id=categ_id)),
            'top_value': self._rows(stock.get_top_value(
                limit=5, location_id=location_id, categ_id=categ_id)),
            'penalties': self._penalty_rows(rows),
        }

    @api.model
    def get_purchase_tab(self, date_from, date_to, supplier_id=None):
        _p, _c, _s, pur = self._engines()
        inv = self._rows(pur.get_open_invoices(supplier_id=supplier_id))
        today = fields.Date.context_today(self).isoformat()
        claims = pur.get_claims(supplier_id=supplier_id)
        return {
            'kpis': pur.get_kpis(date_from, date_to,
                                 supplier_id=supplier_id),
            'buckets': self._bucket_supplier_invoices(inv, today),
            'week_bills': sorted(
                [r for r in inv if 0 <= self._days_until(
                    r.get('planned'), today) <= 6
                 and not (r.get('days_late') or 0) > 0],
                key=lambda r: r.get('planned') or '9999')[:5],
            'overdue_bills': [r for r in inv
                              if (r.get('days_late') or 0) > 0][:5],
            'suppliers': self._rows(pur.get_supplier_rows(
                date_from, date_to))[:6],
            'price_moves': self._rows(pur.get_price_moves(
                supplier_id=supplier_id, limit=5)),
            'claims': claims,
        }

    @staticmethod
    def _days_until(planned, today):
        if not planned:
            return 999
        return (fields.Date.to_date(planned)
                - fields.Date.to_date(today)).days

    @api.model
    def get_actions(self, date_from, date_to, config_id=None):
        pos, cred, stock, pur = self._engines()
        p = pos.get_kpis(date_from, date_to, config_id=config_id,
                         filters={'compare': False})
        s = stock.get_kpis(date_from, date_to)
        a = pur.get_kpis(date_from, date_to)
        inv = self._rows(pur.get_open_invoices())
        today = fields.Date.context_today(self).isoformat()
        rows = self._rows(stock.get_stock_list())
        price_up = [{'name': m.get('name'), 'partner': m.get('partner'),
                     'delta_pct': ((m.get('p1') or 0.0)
                                   / (m.get('p0') or 1.0) - 1.0) * 100.0}
                    for m in self._rows(pur.get_price_moves(limit=8))
                    if (m.get('p1') or 0.0) > (m.get('p0') or 0.0)]
        inp = {
            'debtors': self._rows(cred.get_top_debtors(
                limit=6, config_id=config_id)),
            'overdue_amount': a.get('retard', 0.0),
            'overdue_count': a.get('retard_count', 0),
            'week_bills': sorted(
                [r for r in inv if 0 <= self._days_until(
                    r.get('planned'), today) <= 6
                 and not (r.get('days_late') or 0) > 0],
                key=lambda r: r.get('planned') or '9999'),
            'penalties': self._penalty_rows(rows, limit=3),
            'cmd_value': s.get('cmd_value', 0.0),
            'cmd_refs': s.get('seuil_count', 0),
            'coul_pct': s.get('coul_pct', 0.0),
            'coul_seuil': s.get('coul_seuil', 2.0),
            'coul_amount': s.get('pertes', 0.0),
            'gap_net': s.get('gap_net', 0.0),
            'price_up': price_up,
            'ann_amount': 0.0, 'ann_count': 0,
            'rem_amount': 0.0, 'rem_pct': 0.0,
        }
        return self._build_actions(inp)
