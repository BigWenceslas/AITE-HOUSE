# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class AiteStockDashboard(models.AbstractModel):
    """
    Fournisseur de données du tableau de bord Stock & Inventaire.

    Principes de robustesse (leçons des modules AITE précédents) :

    * **Agrégations sûres** — ``read_group`` uniquement sur des champs
      stockés (``stock.quant.quantity``, quantité des mouvements) ; tout le
      reste est sommé en Python sur des ``search()``.
    * **Détection défensive des champs** — la quantité « faite » d'un
      mouvement a changé de nom selon les versions (``quantity`` vs
      ``quantity_done``/``qty_done``) : on détecte à l'exécution.
    * **Calcul pur et testable** — la logique par produit (point de
      commande, statut, classe de rotation) est isolée dans la méthode
      statique :meth:`_metrics`, sans dépendance à l'ORM ; les tests
      exécutent ce code exact.

    Conventions :

    * ``vday`` (ventes moyennes/jour) est calculé sur **30 jours
      glissants** (sorties vers clients), indépendamment de la période
      affichée, pour des alertes stables.
    * La période sélectionnée s'applique aux **flux** : entrées/sorties,
      écarts d'inventaire, casse, coulage, CA estimé.
    * L'encours de stock est une **photo présente** (quants).
    """
    _name = 'aite.stock.dashboard'
    _description = "AITE Stock — Data Provider (tableau de bord)"

    _LOC_PALETTE = [
        '#714B67', '#185FA5', '#3B6D11', '#854F0B',
        '#A32D2D', '#0F6E56', '#5B4B8A', '#B0655A',
    ]

    # ------------------------------------------------------------------
    # Calcul pur par produit (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _metrics(stock, vday, lead, cost,
                 sec_days, horizon_days, critical_days, dormant_days,
                 manual_threshold=0.0, alert_active=True):
        """
        Calcule les indicateurs d'une référence à partir de primitives.

        :param stock: quantité en stock (tous emplacements filtrés)
        :param vday: ventes moyennes / jour (30 j glissants)
        :param lead: délai de réapprovisionnement effectif (jours)
        :param cost: coût unitaire (standard_price)
        :param sec_days / horizon_days / critical_days / dormant_days:
            paramètres globaux de la société
        :param manual_threshold: seuil manuel (>0 remplace l'automatique)
        :param alert_active: False → référence ignorée des alertes
        :returns: dict {couv, seuil_auto, seuil, cmd, value, rot,
                        status, status_cls, classe, classe_cls, urgency}
        """
        couv = (stock / vday) if vday > 0 else 999.0
        # ceil sans import math : -(-x // 1)
        seuil_auto = float(-(-(vday * (lead + sec_days)) // 1))
        seuil = manual_threshold if manual_threshold > 0 else seuil_auto
        if alert_active:
            need = vday * (lead + horizon_days) - stock
            cmd = float(-(-need // 1)) if need > 0 else 0.0
        else:
            cmd = 0.0
        value = stock * cost
        rot = (vday * 30.0 / stock) if stock > 0 else 0.0

        if not alert_active:
            status, status_cls, urgency = 'Ignorée', 'gray', 4
        elif stock <= 0:
            status, status_cls, urgency = 'Rupture', 'red', 0
        elif couv < critical_days:
            status, status_cls, urgency = 'Critique', 'red', 1
        elif stock <= seuil:
            status, status_cls, urgency = 'Sous seuil', 'amber', 2
        else:
            status, status_cls, urgency = 'OK', 'teal', 3

        if couv >= dormant_days:
            classe, classe_cls = 'Dormant', 'red'
        elif rot >= 3.0:
            classe, classe_cls = 'Rapide', 'teal'
        elif rot >= 1.5:
            classe, classe_cls = 'Normale', 'blue'
        else:
            classe, classe_cls = 'Lente', 'amber'

        return {
            'couv': couv, 'seuil_auto': seuil_auto, 'seuil': seuil,
            'cmd': cmd, 'value': value, 'rot': rot,
            'status': status, 'status_cls': status_cls,
            'classe': classe, 'classe_cls': classe_cls,
            'urgency': urgency,
        }

    # ------------------------------------------------------------------
    # Helpers ORM
    # ------------------------------------------------------------------

    def _move_qty_field(self):
        """Nom du champ « quantité faite » sur stock.move selon la version."""
        Move = self.env['stock.move']
        for name in ('quantity', 'quantity_done'):
            f = Move._fields.get(name)
            if f is not None and getattr(f, 'store', False):
                return name
        return 'product_uom_qty'

    def _parse_period(self, date_from, date_to):
        try:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            dt_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            today = fields.Date.context_today(self)
            dt_from = today.replace(day=1)
            dt_to = today
        if dt_from > dt_to:
            dt_from, dt_to = dt_to, dt_from
        return dt_from, dt_to

    def _company_cfg(self):
        c = self.env.company
        return {
            'sec': c.aite_stock_security_days or 0,
            'hor': c.aite_stock_horizon_days or 7,
            'crit': c.aite_stock_critical_days or 3,
            'dorm': c.aite_stock_dormant_days or 60,
            'lead_default': c.aite_stock_default_lead_days or 3,
            'coul_seuil': c.aite_stock_coulage_threshold or 2.0,
        }

    def _internal_locations(self):
        return self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('company_id', 'in', [self.env.company.id, False]),
        ], order='complete_name')

    def _vday_map(self, days=30):
        """
        Ventes moyennes/jour par produit sur ``days`` jours glissants :
        mouvements faits vers un emplacement client.
        """
        Move = self.env['stock.move']
        qty_field = self._move_qty_field()
        date_from = fields.Datetime.now() - timedelta(days=days)
        rows = Move.read_group(
            [('state', '=', 'done'),
             ('date', '>=', date_from),
             ('company_id', '=', self.env.company.id),
             ('location_dest_id.usage', '=', 'customer')],
            fields=[qty_field + ':sum'],
            groupby=['product_id'],
            lazy=False,
        )
        out = {}
        for r in rows:
            pid = r['product_id'] and r['product_id'][0]
            if pid:
                out[pid] = (r.get(qty_field) or 0.0) / float(days)
        return out

    def _quant_maps(self, location_id=None):
        """
        Quantités par produit et répartition par emplacement interne.

        :returns: (stock_map {pid: qty filtrée}, byloc {pid: {loc_id: qty}})
        """
        Quant = self.env['stock.quant']
        domain = [
            ('location_id.usage', '=', 'internal'),
            ('company_id', '=', self.env.company.id),
        ]
        rows = Quant.read_group(
            domain, fields=['quantity:sum'],
            groupby=['product_id', 'location_id'], lazy=False,
        )
        stock_map = defaultdict(float)
        byloc = defaultdict(dict)
        for r in rows:
            pid = r['product_id'] and r['product_id'][0]
            lid = r['location_id'] and r['location_id'][0]
            qty = r.get('quantity') or 0.0
            if not pid:
                continue
            byloc[pid][lid] = byloc[pid].get(lid, 0.0) + qty
            if location_id:
                if lid == int(location_id):
                    stock_map[pid] += qty
            else:
                stock_map[pid] += qty
        return stock_map, byloc

    def _categ_children(self, categ_id):
        if not categ_id:
            return None
        return set(self.env['product.category'].search(
            [('id', 'child_of', int(categ_id))]).ids)

    # ------------------------------------------------------------------
    # Construction des lignes produit (source unique de vérité)
    # ------------------------------------------------------------------

    def _build_rows(self, location_id=None, categ_id=None):
        cfg = self._company_cfg()
        vday_map = self._vday_map()
        stock_map, byloc = self._quant_maps(location_id)
        categ_set = self._categ_children(categ_id)

        pids = set(stock_map.keys()) | set(vday_map.keys())
        if not pids:
            return [], cfg
        products = self.env['product.product'].browse(list(pids))

        rows = []
        for p in products:
            if not p.exists() or p.type not in ('product', 'consu'):
                # On suit les articles stockables ; « consu » toléré pour
                # les configurations où les boissons sont en consommable.
                if p.type != 'product':
                    continue
            if categ_set is not None and p.categ_id.id not in categ_set:
                continue
            stock = stock_map.get(p.id, 0.0)
            vday = vday_map.get(p.id, 0.0)
            if stock <= 0 and vday <= 0:
                continue
            lead = p.aite_lead_days or cfg['lead_default']
            m = self._metrics(
                stock, vday, lead, p.standard_price or 0.0,
                cfg['sec'], cfg['hor'], cfg['crit'], cfg['dorm'],
                p.aite_manual_threshold or 0.0,
                bool(p.aite_alert_active),
            )
            rows.append({
                'id': p.id,
                'tmpl_id': p.product_tmpl_id.id,
                'name': p.display_name,
                'categ_id': p.categ_id.id,
                'categ': p.categ_id.name or "",
                'cost': p.standard_price or 0.0,
                'list_price': p.lst_price or 0.0,
                'stock': stock,
                'value_sale': stock * (p.lst_price or 0.0),
                'by_location': byloc.get(p.id, {}),
                'vday': vday,
                'lead': lead,
                'manual_threshold': p.aite_manual_threshold or 0.0,
                'alert_active': bool(p.aite_alert_active),
                **m,
            })
        return rows, cfg

    # ------------------------------------------------------------------
    # API publique — référentiels
    # ------------------------------------------------------------------

    @api.model
    def get_meta(self):
        company = self.env.company
        cfg = self._company_cfg()
        return {
            'company_name': company.name,
            'currency_symbol': company.currency_id.symbol or 'F',
            'cfg': cfg,
            'is_manager': self.env.user.has_group('stock.group_stock_manager'),
        }

    @api.model
    def get_locations(self):
        locs = self._internal_locations()
        palette = self._LOC_PALETTE
        return [{
            'id': l.id,
            'name': l.display_name.split('/')[-1].strip() or l.name,
            'color': palette[i % len(palette)],
        } for i, l in enumerate(locs)]

    @api.model
    def get_categories(self):
        rows, _cfg = self._build_rows()
        seen = {}
        for r in rows:
            seen.setdefault(r['categ_id'], r['categ'])
        return [{'id': k, 'name': v} for k, v in
                sorted(seen.items(), key=lambda kv: kv[1] or "")]

    # ------------------------------------------------------------------
    # API publique — données
    # ------------------------------------------------------------------

    @api.model
    def get_kpis(self, date_from, date_to, location_id=None, categ_id=None):
        rows, cfg = self._build_rows(location_id, categ_id)
        dt_from, dt_to = self._parse_period(date_from, date_to)

        total_value = sum(r['value'] for r in rows)
        total_value_sale = sum(r['value_sale'] for r in rows)
        margin_value = total_value_sale - total_value
        margin_pct = (margin_value / total_value_sale * 100.0) \
            if total_value_sale > 0 else 0.0
        total_units = sum(r['stock'] for r in rows)
        total_vday = sum(r['vday'] for r in rows)
        couv_moy = (total_units / total_vday) if total_vday > 0 else 0.0

        rupt = [r for r in rows if r['status'] == 'Rupture']
        crit = [r for r in rows if r['status'] == 'Critique']
        seuil = [r for r in rows if r['status'] == 'Sous seuil']
        dorm = [r for r in rows if r['classe'] == 'Dormant']
        cmd_value = sum(r['cmd'] * r['cost'] for r in rows)
        rot_moy = (total_vday * 30.0 / total_units) if total_units > 0 else 0.0

        gaps = self._inventory_gaps(dt_from, dt_to, location_id, categ_id)
        pertes = sum(-g['value'] for g in gaps if g['value'] < 0)
        ca_est = self._estimated_revenue(dt_from, dt_to, categ_id)
        coul_pct = (pertes / ca_est * 100.0) if ca_est > 0 else 0.0

        flux = self._flux_period(dt_from, dt_to, categ_id)

        return {
            'total_value': total_value,
            'total_value_sale': total_value_sale,
            'margin_value': margin_value,
            'margin_pct': margin_pct,
            'refs_count': len(rows),
            'total_units': total_units,
            'couv_moy': couv_moy,
            'rupt_count': len(rupt),
            'crit_count': len(crit),
            'seuil_count': len(seuil),
            'cmd_value': cmd_value,
            'dorm_count': len(dorm),
            'dorm_value': sum(r['value'] for r in dorm),
            'rot_moy': rot_moy,
            'pertes': pertes,
            'ca_est': ca_est,
            'coul_pct': coul_pct,
            'coul_seuil': cfg['coul_seuil'],
            'gap_net': sum(g['value'] for g in gaps),
            'gap_refs': len(set(g['product_id'] for g in gaps)),
            'in_value': flux['in_value'],
            'out_value': flux['out_value'],
            'cfg': cfg,
        }

    @api.model
    def get_alerts(self, location_id=None, categ_id=None):
        rows, _cfg = self._build_rows(location_id, categ_id)
        rows.sort(key=lambda r: (r['urgency'], r['couv']))
        return rows

    @api.model
    def get_stock_list(self, location_id=None, categ_id=None):
        rows, _cfg = self._build_rows(location_id, categ_id)
        rows.sort(key=lambda r: (r['categ'] or "", -r['value']))
        # Clés d'emplacement en str pour survivre à la sérialisation JSON.
        for r in rows:
            r['by_location'] = {str(k): v for k, v in r['by_location'].items()}
        return rows

    @api.model
    def get_stock_by_category(self, location_id=None):
        rows, _cfg = self._build_rows(location_id)
        agg = defaultdict(float)
        for r in rows:
            agg[r['categ'] or _("Sans catégorie")] += r['value']
        out = [{'name': k, 'value': v} for k, v in agg.items()]
        out.sort(key=lambda x: -x['value'])
        return out

    @api.model
    def get_coverage_by_category(self, location_id=None, categ_id=None):
        rows, cfg = self._build_rows(location_id, categ_id)
        agg = defaultdict(lambda: {'stock': 0.0, 'vday': 0.0})
        for r in rows:
            key = r['categ'] or _("Sans catégorie")
            agg[key]['stock'] += r['stock']
            agg[key]['vday'] += r['vday']
        out = []
        for k, v in agg.items():
            couv = (v['stock'] / v['vday']) if v['vday'] > 0 else 0.0
            out.append({'name': k, 'couv': couv})
        out.sort(key=lambda x: -x['couv'])
        return {'rows': out, 'crit': cfg['crit'], 'dorm': cfg['dorm']}

    @api.model
    def get_top_value(self, limit=8, location_id=None, categ_id=None):
        rows, _cfg = self._build_rows(location_id, categ_id)
        rows.sort(key=lambda r: -r['value'])
        return [{'name': r['name'], 'value': r['value']}
                for r in rows[:limit]]

    @api.model
    def get_flux_months(self, months=6, categ_id=None):
        """Entrées (réceptions) vs sorties (clients) valorisées au coût."""
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
        out = []
        for (yy, mm) in periods:
            start = datetime(yy, mm, 1).date()
            end = (datetime(yy + (mm == 12), (mm % 12) + 1, 1).date()
                   - timedelta(days=1))
            flux = self._flux_period(start, end, categ_id)
            out.append({'period': MONTHS_FR[mm - 1],
                        'in_value': flux['in_value'],
                        'out_value': flux['out_value']})
        return out

    @api.model
    def get_coulage_series(self, months=6, categ_id=None):
        """Coulage mensuel (pertes / CA estimé) vs seuil."""
        cfg = self._company_cfg()
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
        out = []
        for (yy, mm) in periods:
            start = datetime(yy, mm, 1).date()
            end = (datetime(yy + (mm == 12), (mm % 12) + 1, 1).date()
                   - timedelta(days=1))
            gaps = self._inventory_gaps(start, end, None, categ_id)
            pertes = sum(-g['value'] for g in gaps if g['value'] < 0)
            ca = self._estimated_revenue(start, end, categ_id)
            pct = (pertes / ca * 100.0) if ca > 0 else 0.0
            out.append({'period': MONTHS_FR[mm - 1],
                        'pertes': pertes, 'pct': pct})
        return {'rows': out, 'seuil': cfg['coul_seuil']}

    @api.model
    def get_inventory_gaps(self, date_from, date_to,
                           location_id=None, categ_id=None):
        dt_from, dt_to = self._parse_period(date_from, date_to)
        gaps = self._inventory_gaps(dt_from, dt_to, location_id, categ_id)
        gaps.sort(key=lambda g: g['value'])
        return gaps

    @api.model
    def get_moves_journal(self, date_from, date_to, limit=80,
                          location_id=None, categ_id=None):
        dt_from, dt_to = self._parse_period(date_from, date_to)
        Move = self.env['stock.move']
        qty_field = self._move_qty_field()
        domain = [
            ('state', '=', 'done'),
            ('company_id', '=', self.env.company.id),
            ('date', '>=', fields.Datetime.to_string(
                datetime.combine(dt_from, datetime.min.time()))),
            ('date', '<=', fields.Datetime.to_string(
                datetime.combine(dt_to, datetime.max.time()))),
        ]
        categ_set = self._categ_children(categ_id)
        moves = Move.search(domain, order='date desc', limit=limit * 3)

        out = []
        totals = {'in': 0.0, 'out': 0.0, 'tr': 0.0, 'adj': 0.0}
        for mv in moves:
            if categ_set is not None and \
                    mv.product_id.categ_id.id not in categ_set:
                continue
            if location_id and int(location_id) not in (
                    mv.location_id.id, mv.location_dest_id.id):
                continue
            qty = getattr(mv, qty_field, 0.0) or 0.0
            cost = mv.product_id.standard_price or 0.0
            src, dst = mv.location_id, mv.location_dest_id
            if getattr(mv, 'is_inventory', False):
                mtype, cls = _("Ajustement inv."), 'amber'
                signed = qty if dst.usage == 'internal' else -qty
                totals['adj'] += signed * cost
            elif dst.scrap_location:
                mtype, cls = _("Casse / rebut"), 'red'
                signed = -qty
                totals['adj'] += signed * cost
            elif dst.usage == 'customer':
                mtype, cls = _("Vente / livraison"), 'prim'
                signed = -qty
                totals['out'] += qty * cost
            elif src.usage in ('supplier', 'inventory') and \
                    dst.usage == 'internal':
                mtype, cls = _("Réception"), 'teal'
                signed = qty
                totals['in'] += qty * cost
            elif src.usage == 'customer':
                mtype, cls = _("Retour client"), 'blue'
                signed = qty
                totals['in'] += qty * cost
            elif src.usage == 'internal' and dst.usage == 'internal':
                mtype, cls = _("Transfert"), 'blue'
                signed = qty
                totals['tr'] += qty
            else:
                mtype, cls = _("Autre"), 'gray'
                signed = qty if dst.usage == 'internal' else -qty
            out.append({
                'id': mv.id,
                'date': fields.Date.to_string(mv.date),
                'type': mtype, 'type_cls': cls,
                'product': mv.product_id.display_name,
                'qty': signed,
                'src': src.display_name, 'dst': dst.display_name,
                'value': signed * cost,
            })
            if len(out) >= limit:
                break
        return {'rows': out, 'totals': totals}

    @api.model
    def get_alert_products(self, location_id=None, categ_id=None):
        """Lignes éditables du modal de configuration."""
        rows, cfg = self._build_rows(location_id, categ_id)
        rows.sort(key=lambda r: (r['categ'] or "", r['name']))
        return {
            'cfg': cfg,
            'rows': [{
                'tmpl_id': r['tmpl_id'],
                'name': r['name'],
                'categ': r['categ'],
                'lead': r['lead'],
                'lead_raw': 0 if r['lead'] == cfg['lead_default'] and
                not r['manual_threshold'] else r['lead'],
                'manual_threshold': r['manual_threshold'],
                'alert_active': r['alert_active'],
                'seuil_auto': r['seuil_auto'],
            } for r in rows],
        }

    @api.model
    def save_alert_config(self, global_cfg, product_rows):
        """
        Enregistre la configuration des alertes.

        Réservé aux responsables inventaire : les valeurs globales vont sur
        la société, les réglages fins sur les fiches produit.
        """
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise AccessError(_(
                "Seul un responsable Inventaire peut modifier la "
                "configuration des alertes."))
        company = self.env.company.sudo()
        vals = {}
        mapping = {
            'sec': 'aite_stock_security_days',
            'hor': 'aite_stock_horizon_days',
            'crit': 'aite_stock_critical_days',
            'dorm': 'aite_stock_dormant_days',
            'lead_default': 'aite_stock_default_lead_days',
            'coul_seuil': 'aite_stock_coulage_threshold',
        }
        for key, fname in mapping.items():
            if key in (global_cfg or {}):
                vals[fname] = global_cfg[key]
        if vals:
            company.write(vals)

        Tmpl = self.env['product.template']
        for row in (product_rows or []):
            tmpl = Tmpl.browse(int(row.get('tmpl_id', 0)))
            if not tmpl.exists():
                continue
            tmpl.write({
                'aite_lead_days': int(row.get('lead_raw') or 0),
                'aite_manual_threshold': float(
                    row.get('manual_threshold') or 0.0),
                'aite_alert_active': bool(row.get('alert_active', True)),
            })
        return True

    # ------------------------------------------------------------------
    # Internes — flux, écarts, CA estimé
    # ------------------------------------------------------------------

    def _flux_period(self, dt_from, dt_to, categ_id=None):
        Move = self.env['stock.move']
        qty_field = self._move_qty_field()
        base = [
            ('state', '=', 'done'),
            ('company_id', '=', self.env.company.id),
            ('date', '>=', fields.Datetime.to_string(
                datetime.combine(dt_from, datetime.min.time()))),
            ('date', '<=', fields.Datetime.to_string(
                datetime.combine(dt_to, datetime.max.time()))),
        ]
        categ_set = self._categ_children(categ_id)

        def value_of(domain):
            total = 0.0
            for mv in Move.search(domain):
                if categ_set is not None and \
                        mv.product_id.categ_id.id not in categ_set:
                    continue
                qty = getattr(mv, qty_field, 0.0) or 0.0
                total += qty * (mv.product_id.standard_price or 0.0)
            return total

        in_value = value_of(base + [
            ('location_id.usage', '=', 'supplier'),
            ('location_dest_id.usage', '=', 'internal')])
        out_value = value_of(base + [
            ('location_dest_id.usage', '=', 'customer')])
        return {'in_value': in_value, 'out_value': out_value}

    def _inventory_gaps(self, dt_from, dt_to,
                        location_id=None, categ_id=None):
        """
        Écarts d'inventaire (moves ``is_inventory``) et casse (rebuts),
        signés et valorisés au coût.
        """
        Move = self.env['stock.move']
        qty_field = self._move_qty_field()
        base = [
            ('state', '=', 'done'),
            ('company_id', '=', self.env.company.id),
            ('date', '>=', fields.Datetime.to_string(
                datetime.combine(dt_from, datetime.min.time()))),
            ('date', '<=', fields.Datetime.to_string(
                datetime.combine(dt_to, datetime.max.time()))),
        ]
        categ_set = self._categ_children(categ_id)
        out = []

        def push(mv, signed_qty, gtype, cls):
            if categ_set is not None and \
                    mv.product_id.categ_id.id not in categ_set:
                return
            if location_id and int(location_id) not in (
                    mv.location_id.id, mv.location_dest_id.id):
                return
            cost = mv.product_id.standard_price or 0.0
            out.append({
                'id': mv.id,
                'date': fields.Date.to_string(mv.date),
                'product_id': mv.product_id.id,
                'product': mv.product_id.display_name,
                'qty': signed_qty,
                'value': signed_qty * cost,
                'gtype': gtype, 'gtype_cls': cls,
                'ref': mv.reference or mv.origin or "",
            })

        if 'is_inventory' in Move._fields:
            for mv in Move.search(base + [('is_inventory', '=', True)]):
                qty = getattr(mv, qty_field, 0.0) or 0.0
                signed = qty if mv.location_dest_id.usage == 'internal' \
                    else -qty
                push(mv, signed, _("Ajustement inv."), 'amber')

        for mv in Move.search(base + [
                ('location_dest_id.scrap_location', '=', True)]):
            qty = getattr(mv, qty_field, 0.0) or 0.0
            push(mv, -qty, _("Casse / rebut"), 'red')

        return out

    def _estimated_revenue(self, dt_from, dt_to, categ_id=None):
        """CA estimé = quantités livrées clients × prix de vente."""
        Move = self.env['stock.move']
        qty_field = self._move_qty_field()
        domain = [
            ('state', '=', 'done'),
            ('company_id', '=', self.env.company.id),
            ('location_dest_id.usage', '=', 'customer'),
            ('date', '>=', fields.Datetime.to_string(
                datetime.combine(dt_from, datetime.min.time()))),
            ('date', '<=', fields.Datetime.to_string(
                datetime.combine(dt_to, datetime.max.time()))),
        ]
        categ_set = self._categ_children(categ_id)
        total = 0.0
        for mv in Move.search(domain):
            if categ_set is not None and \
                    mv.product_id.categ_id.id not in categ_set:
                continue
            qty = getattr(mv, qty_field, 0.0) or 0.0
            total += qty * (mv.product_id.lst_price or 0.0)
        return total
