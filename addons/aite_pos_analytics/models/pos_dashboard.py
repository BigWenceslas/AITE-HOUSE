# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _


class PosAnalyticsDashboard(models.AbstractModel):
    """
    Fournisseur de données pour le dashboard OWL.

    Ce modèle abstrait expose des méthodes RPC consommables par le client
    OWL. L'avantage par rapport à un appel direct ``read_group`` côté JS :

    * Centralisation de la logique métier (seuils, classements, format).
    * Réutilisation par un futur rapport PDF / export Excel.
    * Tests unitaires Python plus simples qu'avec du JS.

    Toutes les méthodes acceptent une plage ``date_from`` / ``date_to`` au
    format ISO (string ``YYYY-MM-DD``) et un ``config_id`` optionnel pour
    filtrer sur un point de vente précis.
    """
    _name = 'aite.pos.dashboard'
    _description = "POS Analytics — Data Provider"

    # -------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------

    def _parse_period(self, date_from, date_to):
        """
        Bornes de période, en deux ``datetime`` (fin exclusive).

        Convention commune à toute la suite AITE : une période illisible
        — champ vidé, saisie partielle, appel sans paramètre — retombe
        sur le **mois courant** plutôt que d'interrompre la consultation.
        Des bornes inversées sont remises dans l'ordre.
        """
        try:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d')
            dt_to = datetime.strptime(date_to, '%Y-%m-%d')
        except (TypeError, ValueError):
            today = fields.Date.context_today(self)
            dt_from = datetime.combine(today.replace(day=1),
                                       datetime.min.time())
            dt_to = datetime.combine(today, datetime.min.time())
        if dt_from > dt_to:
            dt_from, dt_to = dt_to, dt_from
        # Borne haute exclusive : le jour de fin est inclus dans la période.
        return dt_from, dt_to + timedelta(days=1)

    def _base_domain(self, date_from, date_to, config_id=None,
                     hour_from=None, hour_to=None, weekdays=None):
        """
        Domaine commun appliqué aux requêtes sur ``aite.pos.daily.report``.

        Filtres optionnels :
          * ``hour_from`` / ``hour_to`` : plage horaire en heures pleines
            [0-23]. La borne haute est INCLUSIVE (ex. 18→23 garde les
            commandes de 18h00 à 23h59). Gère le passage minuit si
            ``hour_from`` > ``hour_to`` (ex. 22→2 = nuit).
          * ``weekdays`` : liste d'entiers ISO 1=lundi … 7=dimanche.
        """
        dt_from, dt_to = self._parse_period(date_from, date_to)
        domain = [
            ('date', '>=', dt_from),
            ('date', '<', dt_to),
        ]
        if config_id:
            domain.append(('config_id', '=', int(config_id)))

        # --- Filtre plage horaire ---
        if hour_from is not None and hour_to is not None:
            h_from, h_to = int(hour_from), int(hour_to)
            if h_from <= h_to:
                # Plage simple dans la même journée : [h_from, h_to]
                domain += [('hour', '>=', h_from), ('hour', '<=', h_to)]
            else:
                # Plage à cheval sur minuit (ex. 22h → 2h) :
                # hour >= h_from OU hour <= h_to
                domain += ['|', ('hour', '>=', h_from), ('hour', '<=', h_to)]

        # --- Filtre jours de semaine ---
        if weekdays:
            wd = [int(d) for d in weekdays if d]
            if wd:
                domain.append(('dow', 'in', wd))

        return domain

    def _company_currency(self):
        return self.env.company.currency_id

    # -------------------------------------------------------------------
    # API publique
    # -------------------------------------------------------------------

    def _aggregate_kpis(self, domain):
        """
        Agrège les indicateurs bruts (CA, CMV, marge, qté, nb commandes)
        sur un domaine ``aite.pos.daily.report`` donné.

        Retourne un dict de valeurs brutes (sans ratios), réutilisable
        pour la période courante comme pour la période de comparaison.
        """
        Report = self.env['aite.pos.daily.report']
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'total_cost:sum',
                    'margin:sum', 'qty:sum'],
            groupby=[],
        )
        agg = rows[0] if rows else {}
        ca = agg.get('price_subtotal') or 0.0
        cost = agg.get('total_cost') or 0.0
        margin = agg.get('margin') or 0.0
        qty = agg.get('qty') or 0.0

        # Nb de commandes distinctes via read_group sur order_id
        order_rows = Report.read_group(
            domain, fields=['order_id'], groupby=['order_id'], lazy=False,
        )
        order_count = len(order_rows)

        return {
            'ca': ca, 'cost': cost, 'margin': margin,
            'qty': qty, 'order_count': order_count,
        }

    def _previous_period(self, date_from, date_to):
        """
        Période de comparaison immédiatement précédente, de même durée.
        Ex. 01/06→30/06 (30 j) → 02/05→31/05.

        Les bornes passent par ``_parse_period`` : une période illisible
        est d'abord ramenée au mois courant, et la comparaison porte donc
        toujours sur la période réellement affichée.

        :returns: (prev_from, prev_to) au format 'YYYY-MM-DD'.
        """
        dt_from, dt_to_excl = self._parse_period(date_from, date_to)
        d_to = dt_to_excl - timedelta(days=1)          # borne inclusive
        span = (d_to - dt_from).days + 1               # période inclusive
        prev_to = dt_from - timedelta(days=1)
        prev_from = prev_to - timedelta(days=span - 1)
        return prev_from.strftime('%Y-%m-%d'), prev_to.strftime('%Y-%m-%d')

    @staticmethod
    def _delta_pct(current, previous):
        """Variation % entre deux valeurs. None si pas de base de comparaison."""
        if previous in (0, 0.0, None):
            return None
        return (current - previous) / previous * 100.0

    @api.model
    def get_kpis(self, date_from, date_to, config_id=None, filters=None):
        """
        KPIs principaux du dashboard, enrichis.

        ``filters`` (dict optionnel, rétro-compatible) peut contenir :
          * hour_from / hour_to : plage horaire [0-23]
          * weekdays            : liste ISO 1=lundi … 7=dimanche
          * compare             : bool — calcule les variations vs période
                                  précédente de même durée (défaut True)

        :returns: dict avec CA, marge, CMV, qty, nb commandes, taux marge,
                  ratio CMV/CA, panier moyen, CA/jour, marge/commande,
                  coût/unité, et variations ``*_delta`` vs N-1.
        """
        filters = filters or {}
        hour_from = filters.get('hour_from')
        hour_to = filters.get('hour_to')
        weekdays = filters.get('weekdays')
        compare = filters.get('compare', True)

        domain = self._base_domain(
            date_from, date_to, config_id,
            hour_from=hour_from, hour_to=hour_to, weekdays=weekdays,
        )
        cur = self._aggregate_kpis(domain)
        ca, cost = cur['ca'], cur['cost']
        margin, qty = cur['margin'], cur['qty']
        order_count = cur['order_count']

        dt_from, dt_to = self._parse_period(date_from, date_to)
        days = max(1, (dt_to - dt_from).days)

        result = {
            'ca': ca,
            'cost': cost,
            'margin': margin,
            'margin_rate': (margin / ca * 100.0) if ca else 0.0,
            'cmv_rate': (cost / ca * 100.0) if ca else 0.0,
            'qty': qty,
            'order_count': order_count,
            'average_basket': (ca / order_count) if order_count else 0.0,
            'ca_per_day': ca / days,
            'cost_per_unit': (cost / qty) if qty else 0.0,
            'margin_per_order': (margin / order_count) if order_count else 0.0,
            'days': days,
            'currency_id': self._company_currency().id,
            # placeholders, remplis ci-dessous si compare
            'ca_delta': None, 'margin_delta': None,
            'cost_delta': None, 'order_count_delta': None,
        }

        if compare:
            prev_from, prev_to = self._previous_period(date_from, date_to)
            prev_domain = self._base_domain(
                prev_from, prev_to, config_id,
                hour_from=hour_from, hour_to=hour_to, weekdays=weekdays,
            )
            prev = self._aggregate_kpis(prev_domain)
            result.update({
                'ca_delta': self._delta_pct(ca, prev['ca']),
                'margin_delta': self._delta_pct(margin, prev['margin']),
                'cost_delta': self._delta_pct(cost, prev['cost']),
                'order_count_delta': self._delta_pct(
                    order_count, prev['order_count']),
                'prev_from': prev_from,
                'prev_to': prev_to,
            })

        return result

    @api.model
    def get_top_products(self, date_from, date_to, limit=8, config_id=None):
        """Top N articles par CA, avec CA, marge, taux."""
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(date_from, date_to, config_id)
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'margin:sum',
                    'total_cost:sum', 'qty:sum'],
            groupby=['product_id'],
            orderby='price_subtotal desc',
            limit=limit,
        )
        result = []
        for r in rows:
            ca = r.get('price_subtotal') or 0.0
            margin = r.get('margin') or 0.0
            cost = r.get('total_cost') or 0.0
            prod_id, prod_name = r['product_id'] or (False, _("(sans produit)"))
            result.append({
                'product_id': prod_id,
                'name': prod_name,
                'ca': ca,
                'cost': cost,
                'margin': margin,
                'margin_rate': (margin / ca * 100.0) if ca else 0.0,
                'qty': r.get('qty') or 0.0,
            })
        return result

    @api.model
    def get_category_breakdown(self, date_from, date_to, config_id=None):
        """Stats agrégées par catégorie POS."""
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(date_from, date_to, config_id)
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'margin:sum',
                    'total_cost:sum', 'qty:sum'],
            groupby=['categ_id'],
            orderby='price_subtotal desc',
        )
        total_ca = sum(r.get('price_subtotal') or 0.0 for r in rows)
        result = []
        for r in rows:
            ca = r.get('price_subtotal') or 0.0
            margin = r.get('margin') or 0.0
            cat = r.get('categ_id')
            cat_id, cat_name = cat if cat else (False, _("(sans catégorie)"))

            # Compter le nb d'articles distincts dans la catégorie
            nb_articles = self.env['aite.pos.daily.report'].read_group(
                domain + [('categ_id', '=', cat_id)],
                fields=['product_id'],
                groupby=['product_id'],
                lazy=False,
            )
            result.append({
                'categ_id': cat_id,
                'name': cat_name,
                'ca': ca,
                'cost': r.get('total_cost') or 0.0,
                'margin': margin,
                'margin_rate': (margin / ca * 100.0) if ca else 0.0,
                'qty': r.get('qty') or 0.0,
                'articles': len(nb_articles),
                'pct_ca': (ca / total_ca * 100.0) if total_ca else 0.0,
            })
        return result

    # ------------------------------------------------------------------
    # Évolution du CA par catégorie (v2.1.0)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_category_series(months_data, top=5):
        """
        Construit les séries mensuelles par catégorie (fonction PURE,
        extraite et exécutée telle quelle par les tests).

        :param months_data: liste (un élément par mois, ordre chrono) de
            dicts ``{categ_id: {'name': str, 'ca': float}}``
        :param top: nombre de catégories affichées en propre ; le reste
            est regroupé dans « Autres »
        :returns: liste de séries ``{'categ_id', 'name', 'values': [...]}``
            triées par CA total décroissant, « Autres » (categ_id=0) en
            dernier si non vide. Les mois sans vente d'une catégorie
            valent 0.0.
        """
        totals = {}
        names = {}
        for month in months_data:
            for cid, d in month.items():
                totals[cid] = totals.get(cid, 0.0) + (d.get('ca') or 0.0)
                names[cid] = d.get('name') or ""
        ranked = sorted(totals.items(), key=lambda kv: -kv[1])
        top_ids = [cid for cid, _ca in ranked[:top]]
        rest_ids = [cid for cid, _ca in ranked[top:]]

        series = []
        for cid in top_ids:
            series.append({
                'categ_id': cid,
                'name': names.get(cid, ""),
                'values': [
                    (m.get(cid) or {}).get('ca') or 0.0
                    for m in months_data
                ],
            })
        if rest_ids:
            series.append({
                'categ_id': 0,
                'name': "Autres",
                'values': [
                    sum((m.get(cid) or {}).get('ca') or 0.0
                        for cid in rest_ids)
                    for m in months_data
                ],
            })
        return series

    @api.model
    def get_category_evolution(self, months=6, config_id=None, top=5):
        """
        CA mensuel par catégorie sur les N derniers mois — le « suivi »
        temporel : quelles familles montent, lesquelles s'essoufflent.
        Les catégories au-delà du top N sont regroupées en « Autres ».
        """
        Report = self.env['aite.pos.daily.report']
        today = fields.Date.context_today(self)
        periods = []
        y, m = today.year, today.month
        for _i in range(months):
            periods.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        periods.reverse()
        MONTHS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                     'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

        labels = []
        months_data = []
        for (yy, mm) in periods:
            start = datetime(yy, mm, 1).date()
            end = (datetime(yy + (mm == 12), (mm % 12) + 1, 1).date()
                   - timedelta(days=1))
            labels.append("%s %s" % (MONTHS_FR[mm - 1], str(yy)[2:]))
            domain = self._base_domain(
                fields.Date.to_string(start),
                fields.Date.to_string(end), config_id)
            rows = Report.read_group(
                domain, fields=['price_subtotal:sum'],
                groupby=['categ_id'], lazy=False)
            month = {}
            for r in rows:
                cat = r.get('categ_id')
                cid, cname = cat if cat else (0, _("(sans catégorie)"))
                if cid == 0:
                    # Fusionner « sans catégorie » avec « Autres » plus tard
                    cid, cname = -1, _("(sans catégorie)")
                month[cid] = {
                    'name': cname,
                    'ca': r.get('price_subtotal') or 0.0,
                }
            months_data.append(month)

        series = self._build_category_series(months_data, top=top)
        return {'labels': labels, 'series': series}

    @api.model
    def get_monthly_evolution(self, date_from, date_to, config_id=None):
        """Évolution CA / CMV / Marge mois par mois."""
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(date_from, date_to, config_id)
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'margin:sum', 'total_cost:sum'],
            groupby=['date:month'],
            orderby='date asc',
        )
        return [{
            'period': r.get('date:month', ''),
            'ca': r.get('price_subtotal') or 0.0,
            'cost': r.get('total_cost') or 0.0,
            'margin': r.get('margin') or 0.0,
        } for r in rows]

    @api.model
    def get_rankings(self, date_from, date_to, config_id=None):
        """
        Trois classements pour le module "Classements produits" :
        - Top bières par quantité
        - Meilleures marges (taux %)
        - Articles moins vendus
        """
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(date_from, date_to, config_id)

        # Top bières (filtre sur libellé catégorie contenant "bière")
        # NB : la classification repose sur le nommage des catégories
        # produit. Pour LAVERANDAH, créer une catégorie "Bières" dans
        # Inventaire > Configuration > Catégories de produits, et y
        # rattacher les articles concernés.
        beer_categs = self.env['product.category'].search([
            '|', ('name', 'ilike', 'bière'), ('name', 'ilike', 'biere')
        ])
        beers = []
        if beer_categs:
            rows = Report.read_group(
                domain + [('categ_id', 'in', beer_categs.ids)],
                fields=['qty:sum', 'price_subtotal:sum'],
                groupby=['product_id'],
                orderby='qty desc',
                limit=8,
            )
            for r in rows:
                pid, pname = r['product_id'] or (False, '')
                beers.append({
                    'product_id': pid, 'name': pname,
                    'qty': r.get('qty') or 0.0,
                    'ca': r.get('price_subtotal') or 0.0,
                })

        # Meilleures marges — on filtre les produits avec CA significatif
        # pour éviter le bruit des micro-ventes à 100% de marge.
        all_products = Report.read_group(
            domain + [('price_subtotal', '>', 100)],
            fields=['price_subtotal:sum', 'margin:sum'],
            groupby=['product_id'],
            lazy=False,
        )
        best_margins = []
        for r in all_products:
            ca = r.get('price_subtotal') or 0.0
            mg = r.get('margin') or 0.0
            rate = (mg / ca * 100.0) if ca else 0.0
            pid, pname = r['product_id'] or (False, '')
            best_margins.append({
                'product_id': pid, 'name': pname,
                'ca': ca, 'margin': mg, 'margin_rate': rate,
            })
        best_margins.sort(key=lambda x: x['margin_rate'], reverse=True)
        best_margins = best_margins[:8]

        # Moins vendus (qty > 0)
        rows = Report.read_group(
            domain + [('qty', '>', 0)],
            fields=['qty:sum'],
            groupby=['product_id'],
            orderby='qty asc',
            limit=8,
        )
        low_sellers = []
        for r in rows:
            pid, pname = r['product_id'] or (False, '')
            low_sellers.append({
                'product_id': pid, 'name': pname,
                'qty': r.get('qty') or 0.0,
            })

        return {
            'top_beers': beers,
            'best_margins': best_margins,
            'low_sellers': low_sellers,
        }

    @api.model
    def get_products_full(self, date_from, date_to, config_id=None):
        """Table complète de tous les articles avec stats."""
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(date_from, date_to, config_id)
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'margin:sum',
                    'total_cost:sum', 'qty:sum'],
            groupby=['product_id', 'categ_id'],
            lazy=False,
            orderby='price_subtotal desc',
        )
        result = []
        for r in rows:
            ca = r.get('price_subtotal') or 0.0
            margin = r.get('margin') or 0.0
            pid, pname = r['product_id'] or (False, '')
            cid, cname = r['categ_id'] or (False, '')
            result.append({
                'product_id': pid, 'name': pname,
                'category_id': cid, 'category': cname,
                'ca': ca,
                'cost': r.get('total_cost') or 0.0,
                'margin': margin,
                'margin_rate': (margin / ca * 100.0) if ca else 0.0,
                'qty': r.get('qty') or 0.0,
            })
        return result

    @api.model
    def get_sessions(self, date_from, date_to, config_id=None):
        """Liste des sessions de la période avec métriques."""
        dt_from, dt_to = self._parse_period(date_from, date_to)
        domain = [
            ('start_at', '>=', dt_from),
            ('start_at', '<', dt_to),
        ]
        if config_id:
            domain.append(('config_id', '=', int(config_id)))

        sessions = self.env['pos.session'].search(domain, order='start_at desc')
        return [{
            'id': s.id,
            'name': s.name,
            'start_at': fields.Datetime.to_string(s.start_at) if s.start_at else None,
            'stop_at': fields.Datetime.to_string(s.stop_at) if s.stop_at else None,
            'config_id': s.config_id.id,
            'config_name': s.config_id.name,
            'state': s.state,
            'user_id': s.user_id.id,
            'user_name': s.user_id.name,
            'total_ca': s.total_ca,
            'total_margin': s.total_margin,
            'margin_rate': s.margin_rate,
            'order_count': s.order_count_computed,
            'average_basket': s.average_basket,
            'cash_difference': s.cash_register_difference,
            'severity': s.cash_discrepancy_severity,
        } for s in sessions]

    @api.model
    def get_cash_discrepancies(self, date_from, date_to, config_id=None):
        """Sessions avec écart de caisse, ordonnées par sévérité."""
        sessions = self.get_sessions(date_from, date_to, config_id)
        # On garde celles dont l'écart n'est pas 0
        discrepancies = [s for s in sessions if (s['cash_difference'] or 0) != 0]
        # Tri : critique > élevé > modéré > excédent
        severity_order = {'high': 0, 'med': 1, 'low': 2, 'over': 3, 'none': 4}
        discrepancies.sort(key=lambda s: (severity_order.get(s['severity'], 9),
                                          -abs(s['cash_difference'] or 0)))

        total_neg = sum(s['cash_difference'] for s in discrepancies
                       if s['cash_difference'] < 0)
        total_pos = sum(s['cash_difference'] for s in discrepancies
                       if s['cash_difference'] > 0)
        count_neg = sum(1 for s in discrepancies if s['cash_difference'] < 0)

        return {
            'sessions': discrepancies,
            'total_negative': total_neg,
            'total_positive': total_pos,
            'count_negative': count_neg,
            'count_positive': len(discrepancies) - count_neg,
            'average_negative': (total_neg / count_neg) if count_neg else 0.0,
            'largest_negative': min(
                (s['cash_difference'] for s in discrepancies
                 if s['cash_difference'] < 0),
                default=0,
            ),
        }

    @api.model
    def get_payment_breakdown(self, date_from, date_to, config_id=None):
        """Répartition par mode de paiement."""
        dt_from, dt_to = self._parse_period(date_from, date_to)
        Payment = self.env['pos.payment']
        domain = [
            ('payment_date', '>=', dt_from),
            ('payment_date', '<', dt_to),
        ]
        if config_id:
            domain.append(('session_id.config_id', '=', int(config_id)))

        rows = Payment.read_group(
            domain,
            fields=['amount:sum'],
            groupby=['payment_method_id'],
            orderby='amount desc',
        )
        total = sum(r.get('amount') or 0.0 for r in rows)
        return [{
            'method_id': r['payment_method_id'][0] if r['payment_method_id'] else False,
            'method_name': r['payment_method_id'][1] if r['payment_method_id'] else _("Inconnu"),
            'amount': r.get('amount') or 0.0,
            'count': r.get('__count') or 0,
            'pct': ((r.get('amount') or 0.0) / total * 100.0) if total else 0.0,
        } for r in rows]

    @api.model
    def get_product_detail(self, product_id, date_from, date_to, config_id=None):
        """Détail d'un article pour le panneau slide-over."""
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(date_from, date_to, config_id) + [
            ('product_id', '=', int(product_id))
        ]
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'margin:sum',
                    'total_cost:sum', 'qty:sum'],
            groupby=['product_id', 'categ_id'],
            lazy=False,
        )
        if not rows:
            return None
        r = rows[0]
        ca = r.get('price_subtotal') or 0.0
        margin = r.get('margin') or 0.0
        cost = r.get('total_cost') or 0.0
        qty = r.get('qty') or 0.0
        pid, pname = r['product_id']
        cid, cname = r['categ_id'] or (False, '')
        return {
            'product_id': pid, 'name': pname,
            'category_id': cid, 'category': cname,
            'ca': ca, 'cost': cost, 'margin': margin,
            'margin_rate': (margin / ca * 100.0) if ca else 0.0,
            'qty': qty,
            'price_avg': (ca / qty) if qty else 0.0,
            'cost_avg': (cost / qty) if qty else 0.0,
            'margin_avg': (margin / qty) if qty else 0.0,
        }

    # -------------------------------------------------------------------
    # Analyse par caisse (point de vente) + dimensions temporelles
    # -------------------------------------------------------------------

    # Palette stable pour colorer chaque caisse de façon déterministe.
    _CAISSE_PALETTE = [
        '#714B67', '#185FA5', '#3B6D11', '#854F0B',
        '#0F6E56', '#A32D2D', '#1D9E75', '#BA7517',
    ]

    @api.model
    def get_caisse_breakdown(self, date_from, date_to, config_id=None,
                             filters=None):
        """
        Performance détaillée par caisse (``pos.config``).

        Calcule pour chaque point de vente le CA, la marge, le CMV, le
        taux de marge, le nb de commandes, le panier moyen, la quantité,
        la part du CA total et l'écart de caisse cumulé sur la période.

        Répond directement à la demande « sur une période donnée,
        déterminer la marge totale ET par caisse ».

        :returns: dict {
            'caisses': [ {...} ],           # une entrée par caisse
            'total': {...},                 # ligne de total
        }
        """
        filters = filters or {}
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(
            date_from, date_to, config_id,
            hour_from=filters.get('hour_from'),
            hour_to=filters.get('hour_to'),
            weekdays=filters.get('weekdays'),
        )

        # Agrégats CA / marge / CMV / qté par config en un seul read_group
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum', 'margin:sum',
                    'total_cost:sum', 'qty:sum'],
            groupby=['config_id'],
            orderby='price_subtotal desc',
            lazy=False,
        )

        # Nb commandes distinctes par config (read_group 2 niveaux)
        order_rows = Report.read_group(
            domain,
            fields=['order_id'],
            groupby=['config_id', 'order_id'],
            lazy=False,
        )
        orders_by_config = defaultdict(set)
        for r in order_rows:
            cfg = r.get('config_id')
            cfg_id = cfg[0] if cfg else False
            if r.get('order_id'):
                oid = r['order_id'][0] if isinstance(r['order_id'], (list, tuple)) else r['order_id']
                orders_by_config[cfg_id].add(oid)

        # Écart de caisse cumulé par config : somme sur les sessions de la
        # période. ``cash_register_difference`` est un champ CALCULÉ
        # NON-STOCKÉ (Odoo 18) — on ne peut donc pas l'agréger en SQL via
        # read_group. On lit les sessions puis on somme côté Python.
        dt_from, dt_to = self._parse_period(date_from, date_to)
        sess_domain = [
            ('start_at', '>=', dt_from),
            ('start_at', '<', dt_to),
        ]
        if config_id:
            sess_domain.append(('config_id', '=', int(config_id)))
        sessions = self.env['pos.session'].search(sess_domain)
        ecart_by_config = defaultdict(float)
        for sess in sessions:
            cfg_id = sess.config_id.id if sess.config_id else False
            ecart_by_config[cfg_id] += sess.cash_register_difference or 0.0

        total_ca = sum(r.get('price_subtotal') or 0.0 for r in rows)

        caisses = []
        for idx, r in enumerate(rows):
            cfg = r.get('config_id')
            cfg_id, cfg_name = cfg if cfg else (False, _("(sans caisse)"))
            ca = r.get('price_subtotal') or 0.0
            margin = r.get('margin') or 0.0
            cost = r.get('total_cost') or 0.0
            qty = r.get('qty') or 0.0
            oc = len(orders_by_config.get(cfg_id, ()))
            caisses.append({
                'config_id': cfg_id,
                'name': cfg_name,
                'color': self._CAISSE_PALETTE[idx % len(self._CAISSE_PALETTE)],
                'ca': ca,
                'margin': margin,
                'cost': cost,
                'qty': qty,
                'margin_rate': (margin / ca * 100.0) if ca else 0.0,
                'order_count': oc,
                'average_basket': (ca / oc) if oc else 0.0,
                'pct_ca': (ca / total_ca * 100.0) if total_ca else 0.0,
                'cash_difference': ecart_by_config.get(cfg_id, 0.0),
            })

        total_margin = sum(c['margin'] for c in caisses)
        total_cost = sum(c['cost'] for c in caisses)
        total_qty = sum(c['qty'] for c in caisses)
        total_orders = sum(c['order_count'] for c in caisses)
        total_ecart = sum(c['cash_difference'] for c in caisses)

        return {
            'caisses': caisses,
            'total': {
                'ca': total_ca,
                'margin': total_margin,
                'cost': total_cost,
                'qty': total_qty,
                'margin_rate': (total_margin / total_ca * 100.0) if total_ca else 0.0,
                'order_count': total_orders,
                'average_basket': (total_ca / total_orders) if total_orders else 0.0,
                'cash_difference': total_ecart,
            },
            'currency_id': self._company_currency().id,
        }

    @api.model
    def get_hourly_heatmap(self, date_from, date_to, config_id=None,
                           filters=None):
        """
        Matrice CA par (jour de semaine × heure) pour la heatmap.

        :returns: dict {
            'matrix': [[...24...] x 7],   # lignes = lundi..dimanche
            'max': float,                  # valeur max (pour l'échelle)
            'hours': [0..23],
            'days': ['Lun'..'Dim'],
        }
        """
        filters = filters or {}
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(
            date_from, date_to, config_id,
            hour_from=filters.get('hour_from'),
            hour_to=filters.get('hour_to'),
            weekdays=filters.get('weekdays'),
        )
        rows = Report.read_group(
            domain,
            fields=['price_subtotal:sum'],
            groupby=['dow', 'hour'],
            lazy=False,
        )

        # Matrice 7 x 24 initialisée à 0
        matrix = [[0.0] * 24 for _ in range(7)]
        max_val = 0.0
        for r in rows:
            dow = r.get('dow')
            hour = r.get('hour')
            if dow is None or hour is None:
                continue
            d = int(dow) - 1   # ISO 1..7 → index 0..6
            h = int(hour)
            if 0 <= d < 7 and 0 <= h < 24:
                val = r.get('price_subtotal') or 0.0
                matrix[d][h] = val
                if val > max_val:
                    max_val = val

        return {
            'matrix': matrix,
            'max': max_val,
            'hours': list(range(24)),
            'days': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        }

    @api.model
    def get_time_insights(self, date_from, date_to, config_id=None,
                          filters=None):
        """
        Indicateurs temporels synthétiques : meilleure tranche horaire
        (créneau de 2h) et jour de semaine le plus rentable.

        :returns: dict {
            'best_hour_slot': {'label': '20h-22h', 'ca': ..., 'pct': ...},
            'best_weekday': {'label': 'Samedi', 'ca': ..., 'margin': ...},
        }
        """
        filters = filters or {}
        Report = self.env['aite.pos.daily.report']
        domain = self._base_domain(
            date_from, date_to, config_id,
            hour_from=filters.get('hour_from'),
            hour_to=filters.get('hour_to'),
            weekdays=filters.get('weekdays'),
        )

        # Par heure
        hour_rows = Report.read_group(
            domain, fields=['price_subtotal:sum'],
            groupby=['hour'], lazy=False,
        )
        ca_by_hour = {}
        total_ca = 0.0
        for r in hour_rows:
            h = r.get('hour')
            if h is None:
                continue
            v = r.get('price_subtotal') or 0.0
            ca_by_hour[int(h)] = v
            total_ca += v

        # Meilleur créneau de 2h glissant
        best_slot = None
        best_slot_ca = -1.0
        for h in range(24):
            slot_ca = ca_by_hour.get(h, 0.0) + ca_by_hour.get((h + 1) % 24, 0.0)
            if slot_ca > best_slot_ca:
                best_slot_ca = slot_ca
                best_slot = h
        best_hour_slot = None
        if best_slot is not None and best_slot_ca > 0:
            best_hour_slot = {
                'label': "%dh-%dh" % (best_slot, (best_slot + 2) % 24),
                'ca': best_slot_ca,
                'pct': (best_slot_ca / total_ca * 100.0) if total_ca else 0.0,
            }

        # Par jour de semaine
        DAY_NAMES = {
            1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi",
            5: "Vendredi", 6: "Samedi", 7: "Dimanche",
        }
        dow_rows = Report.read_group(
            domain, fields=['price_subtotal:sum', 'margin:sum'],
            groupby=['dow'], lazy=False,
        )
        best_weekday = None
        best_wd_ca = -1.0
        for r in dow_rows:
            d = r.get('dow')
            if d is None:
                continue
            v = r.get('price_subtotal') or 0.0
            if v > best_wd_ca:
                best_wd_ca = v
                best_weekday = {
                    'label': DAY_NAMES.get(int(d), str(d)),
                    'ca': v,
                    'margin': r.get('margin') or 0.0,
                }

        return {
            'best_hour_slot': best_hour_slot,
            'best_weekday': best_weekday,
        }

    @api.model
    def get_pos_configs(self):
        """Liste des points de vente accessibles, avec couleur stable."""
        configs = self.env['pos.config'].search([])
        return [{
            'id': c.id,
            'name': c.name,
            'color': self._CAISSE_PALETTE[idx % len(self._CAISSE_PALETTE)],
        } for idx, c in enumerate(configs)]

    @api.model
    def get_dashboard_meta(self):
        """Métadonnées globales : devise, format, configs accessibles."""
        company = self.env.company
        return {
            'currency_id': company.currency_id.id,
            'currency_name': company.currency_id.name,
            'currency_symbol': company.currency_id.symbol,
            'currency_position': company.currency_id.position,
            'configs': self.get_pos_configs(),
            'company_name': company.name,
        }
