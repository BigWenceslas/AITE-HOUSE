# -*- coding: utf-8 -*-
"""
Générateur du jeu d'essai opérationnel.

Les fichiers XML du module posent le **référentiel** (établissement,
chambres, catalogue, clients, réservations, folios, fidélité, stock).
Ce générateur y ajoute ce qu'un fichier statique ne sait pas produire :

* des **profils utilisateurs** métier pour jouer les parcours
  (réception, gouvernante, caisse, magasin, direction) ;
* les **moyens de paiement** « Ardoise » et « Note de chambre » sur la
  caisse de démonstration ;
* le **catalogue des services hôteliers** et des **tarifs saisonniers** ;
* des **ardoises clients** d'âges variés, avec remboursements partiels,
  pour peupler la balance âgée et le recouvrement ;
* des **notes de chambre en attente** de rattachement ;
* des **tâches de gouvernante** cohérentes avec l'occupation du jour ;
* des **commandes d'achat** et des **consignes fournisseurs**.

Tout est **relatif à la date d'installation** et **idempotent** : relancer
la génération ne duplique rien. Les volumes se règlent par le dictionnaire
``SCALE`` — ``generate_all(scale='small')`` pour un jeu léger.
"""
import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# Repère posé sur chaque enregistrement produit, pour l'idempotence.
MARKER = "[démo]"

SCALE = {
    'small': {'credits': 6, 'pending': 2, 'purchases': 3, 'hk_tasks': 4,
              'pos_days': 5, 'pos_orders_per_day': 4},
    'normal': {'credits': 18, 'pending': 5, 'purchases': 8, 'hk_tasks': 12,
               'pos_days': 21, 'pos_orders_per_day': 8},
    'large': {'credits': 60, 'pending': 12, 'purchases': 25, 'hk_tasks': 30,
              'pos_days': 60, 'pos_orders_per_day': 14},
}

# Répartition horaire des ventes : deux pics, midi et soir — de quoi
# donner du relief à la heatmap et aux « heures de pointe ».
SALE_HOURS = [11, 12, 12, 13, 13, 14, 18, 19, 19, 20, 20, 21, 21, 22]

# Profils métier : (clé, nom, login, groupes XML-ID).
DEMO_USERS = [
    ('reception', "Awa Diallo (Réception)", 'demo.reception', [
        'base.group_user',
        'aite_hotel_management.group_hotel_user',
        'aite_slot_booking.group_slot_user',
    ]),
    ('housekeeping', "Fanta Souaré (Gouvernante)", 'demo.gouvernante', [
        'base.group_user',
        'aite_hotel_management.group_hotel_housekeeping',
    ]),
    ('cashier', "Ibrahima Sylla (Caisse)", 'demo.caisse', [
        'base.group_user',
        'point_of_sale.group_pos_user',
        'aite_pos_credit.group_pos_credit_user',
    ]),
    ('stock', "Moussa Camara (Magasin)", 'demo.magasin', [
        'base.group_user',
        'stock.group_stock_user',
    ]),
    ('manager', "Aminata Bah (Direction)", 'demo.direction', [
        'base.group_user',
        'aite_hotel_management.group_hotel_manager',
        'point_of_sale.group_pos_manager',
        'aite_pos_credit.group_pos_credit_manager',
        'aite_pos_analytics.group_aite_pos_analytics_manager',
        'stock.group_stock_manager',
        'purchase.group_purchase_manager',
        'account.group_account_invoice',
    ]),
]

HOTEL_SERVICES = [
    ("Petit-déjeuner buffet", 'restaurant', 35000.0),
    ("Dîner à la carte", 'restaurant', 85000.0),
    ("Minibar — boissons", 'minibar', 15000.0),
    ("Blanchisserie — chemise", 'laundry', 12000.0),
    ("Blanchisserie — costume", 'laundry', 45000.0),
    ("Transfert aéroport", 'transport', 150000.0),
    ("Massage en chambre", 'spa', 120000.0),
    ("Location de salle de réunion", 'other', 350000.0),
]


class AiteDemoGenerator(models.AbstractModel):
    """Moteur de génération du jeu d'essai opérationnel."""
    _name = 'aite.demo.generator'
    _description = "AITE — générateur de jeu d'essai"

    # ------------------------------------------------------------------
    # Point d'entrée
    # ------------------------------------------------------------------

    @api.model
    def generate_all(self, scale='normal'):
        """
        Produit l'ensemble du jeu opérationnel.

        :param scale: 'small', 'normal' ou 'large'
        :returns: dict {domaine: nombre d'enregistrements créés}
        """
        cfg = SCALE.get(scale) or SCALE['normal']
        created = {}
        created['users'] = len(self._generate_users())
        created['payment_methods'] = len(self._generate_payment_methods())
        created['hotel_services'] = len(self._generate_hotel_services())
        created['season_prices'] = len(self._generate_season_prices())
        created['pos_orders'] = len(self._generate_pos_orders(
            cfg['pos_days'], cfg['pos_orders_per_day']))
        created['credits'] = len(self._generate_credits(cfg['credits']))
        created['roomcharges'] = len(
            self._generate_pending_roomcharges(cfg['pending']))
        created['housekeeping'] = len(
            self._generate_housekeeping(cfg['hk_tasks']))
        created['purchases'] = len(
            self._generate_purchases(cfg['purchases']))
        created['deposits'] = len(self._generate_deposits())
        _logger.info("Jeu d'essai AITE généré (%s) : %s", scale, created)
        return created

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _company(self):
        return self.env.company

    def _today(self):
        return fields.Date.context_today(self)

    # Module fictif portant les identifiants externes des enregistrements
    # générés : c'est ce qui rend la génération idempotente et la purge
    # exacte, y compris pour les modèles sans champ libre (pos.session).
    _TAG_MODULE = '__aite_demo_gen__'

    def _tag(self, record, key):
        """Pose un identifiant externe sur un enregistrement généré."""
        self.env['ir.model.data'].sudo()._update_xmlids([{
            'xml_id': '%s.%s' % (self._TAG_MODULE, key),
            'record': record,
            'noupdate': True,
        }])
        return record

    def _tagged(self, model, key):
        """Retrouve un enregistrement généré par sa clé, sinon vide."""
        record = self.env.ref('%s.%s' % (self._TAG_MODULE, key),
                              raise_if_not_found=False)
        return record if record and record._name == model \
            else self.env[model].browse()

    def _tagged_all(self, model):
        """Tous les enregistrements générés d'un modèle."""
        data = self.env['ir.model.data'].sudo().search([
            ('module', '=', self._TAG_MODULE), ('model', '=', model),
        ])
        return self.env[model].sudo().browse(data.mapped('res_id')).exists()

    def _demo_partners(self, limit=None):
        """Clients du jeu d'essai (ceux posés par les fichiers XML)."""
        partners = self.env['res.partner'].search([
            ('is_company', '=', False),
            ('customer_rank', '>=', 0),
        ], order='id')
        demo = partners.filtered(lambda p: p.loyalty_move_ids)
        result = demo or partners
        return result[:limit] if limit else result

    def _hotel(self):
        return self.env.ref('aite_demo_data.hotel_main',
                            raise_if_not_found=False) \
            or self.env['aite.hotel.hotel'].search(
                [('company_id', '=', self._company().id)], limit=1)

    # ------------------------------------------------------------------
    # Utilisateurs métier
    # ------------------------------------------------------------------

    def _generate_users(self):
        """Un profil par métier, pour jouer et filmer les parcours."""
        Users = self.env['res.users'].sudo()
        created = Users.browse()
        for key, name, login, group_xmlids in DEMO_USERS:
            if Users.with_context(active_test=False).search_count(
                    [('login', '=', login)]):
                continue
            groups = self.env['res.groups'].browse()
            for xmlid in group_xmlids:
                group = self.env.ref(xmlid, raise_if_not_found=False)
                if group:
                    groups |= group
            if not groups:
                continue
            user = Users.create({
                'name': name,
                'login': login,
                # Mot de passe identique au login : base de DÉMONSTRATION.
                'password': login,
                'company_id': self._company().id,
                'company_ids': [(6, 0, [self._company().id])],
                'groups_id': [(6, 0, groups.ids)],
                'tz': 'Africa/Conakry',
            })
            created |= user
            _logger.info("Profil de démonstration créé : %s (%s)",
                         name, login)
        return created

    # ------------------------------------------------------------------
    # Moyens de paiement POS
    # ------------------------------------------------------------------

    def _generate_payment_methods(self):
        """Ardoise et Note de chambre sur la caisse de démonstration."""
        Method = self.env['pos.payment.method'].sudo()
        company = self._company()
        created = Method.browse()

        credit = Method.search([
            ('name', '=', "Ardoise client"),
            ('company_id', '=', company.id),
        ], limit=1)
        if not credit and 'is_aite_credit' in Method._fields:
            credit = Method.create({
                'name': "Ardoise client",
                'is_aite_credit': True,
                'company_id': company.id,
            })
            created |= credit

        roomcharge = Method.search([
            ('name', '=', "Note de chambre"),
            ('company_id', '=', company.id),
        ], limit=1)
        if not roomcharge and 'is_room_charge' in Method._fields:
            roomcharge = Method.create({
                'name': "Note de chambre",
                'is_room_charge': True,
                'company_id': company.id,
            })
            created |= roomcharge

        # Les rattacher à la caisse de démonstration.
        config = self._pos_config()
        methods = credit | roomcharge
        if config and methods:
            config.sudo().write({
                'payment_method_ids': [(4, m.id) for m in methods],
            })
        return created

    # ------------------------------------------------------------------
    # Catalogue hôtelier
    # ------------------------------------------------------------------

    def _generate_hotel_services(self):
        """Extras imputables au folio : restaurant, minibar, transferts…"""
        Service = self.env['aite.hotel.service'].sudo()
        company = self._company()
        created = Service.browse()
        for name, category, price in HOTEL_SERVICES:
            if Service.search_count([
                ('name', '=', name), ('company_id', '=', company.id),
            ]):
                continue
            created |= Service.create({
                'name': name,
                'category': category,
                'company_id': company.id,
                'price': price,
            })
        return created

    def _generate_season_prices(self):
        """Haute saison (fêtes) et basse saison, relatives à aujourd'hui."""
        Season = self.env['aite.hotel.season.price'].sudo()
        company = self._company()
        today = self._today()
        room_types = self.env['aite.hotel.room.type'].sudo().search(
            [('company_id', '=', company.id)])
        created = Season.browse()
        for room_type in room_types:
            plan = [
                (_("Haute saison — démo"),
                 today + timedelta(days=20), today + timedelta(days=50),
                 round(room_type.base_price * 1.25)),
                (_("Basse saison — démo"),
                 today + timedelta(days=120), today + timedelta(days=170),
                 round(room_type.base_price * 0.85)),
            ]
            for label, date_from, date_to, price in plan:
                if Season.search_count([
                    ('name', '=', label),
                    ('room_type_id', '=', room_type.id),
                ]):
                    continue
                created |= Season.create({
                    'name': label,
                    'room_type_id': room_type.id,
                    'date_from': date_from,
                    'date_to': date_to,
                    'price': price,
                })
        return created

    # ------------------------------------------------------------------
    # Ventes en caisse
    # ------------------------------------------------------------------

    def _generate_pos_orders(self, days, per_day):
        """
        Historique de ventes en caisse, une session close par jour.

        Sans commandes POS, le tableau de bord Ventes, la heatmap des
        heures de pointe, les marges et la rotation du stock restent
        vides — c'est ce que le jeu d'essai laissait de côté.
        """
        Order = self.env['pos.order'].sudo()
        Session = self.env['pos.session'].sudo()
        company = self._company()

        config = self._pos_config()
        if not config:
            return Order.browse()
        products = self._pos_products()
        method = self._cash_method(config)
        if not (products and method):
            return Order.browse()

        partners = self._demo_partners(limit=20)
        today = self._today()
        created = Order.browse()
        seq = 0

        for day_offset in range(days, 0, -1):
            day = today - timedelta(days=day_offset)
            key = 'pos_session_%s' % day.strftime('%Y%m%d')
            if self._tagged('pos.session', key):
                continue
            session = Session.create({
                'config_id': config.id,
                'user_id': self.env.user.id,
            })
            self._tag(session, key)
            session.write({
                'state': 'opened',
                'start_at': fields.Datetime.to_datetime(
                    '%s 08:00:00' % day),
            })

            for index in range(per_day):
                seq += 1
                hour = SALE_HOURS[seq % len(SALE_HOURS)]
                minute = (seq * 7) % 60
                # Panier de 1 à 3 articles, montants variés.
                lines = []
                total = 0.0
                for item in range(1 + seq % 3):
                    product = products[(seq + item) % len(products)]
                    qty = 1 + (seq + item) % 3
                    price = product.lst_price or 5000.0
                    subtotal = qty * price
                    total += subtotal
                    lines.append((0, 0, {
                        'product_id': product.id,
                        'qty': qty,
                        'price_unit': price,
                        'price_subtotal': subtotal,
                        'price_subtotal_incl': subtotal,
                    }))
                # Un ticket sur quatre est nominatif (fidélité).
                partner = partners[seq % len(partners)] \
                    if partners and seq % 4 == 0 else False
                order = Order.create({
                    'session_id': session.id,
                    'company_id': company.id,
                    'partner_id': partner.id if partner else False,
                    'date_order': fields.Datetime.to_datetime(
                        '%s %02d:%02d:00' % (day, hour, minute)),
                    'amount_tax': 0.0,
                    'amount_total': total,
                    'amount_paid': total,
                    'amount_return': 0.0,
                    'lines': lines,
                })
                self.env['pos.payment'].sudo().create({
                    'pos_order_id': order.id,
                    'payment_method_id': method.id,
                    'amount': total,
                })
                order.write({'state': 'paid'})
                created |= order

            # Clôture avec, une fois sur six, un écart de caisse à traiter.
            gap = 0.0
            if day_offset % 6 == 0:
                gap = -12500.0 if day_offset % 12 == 0 else 7500.0
            session.write({
                'state': 'closed',
                'stop_at': fields.Datetime.to_datetime(
                    '%s 23:30:00' % day),
                'cash_register_difference': gap,
            })
        self.env.flush_all()
        return created

    def _pos_config(self):
        config = self.env.ref('aite_demo_data.pos_config_boutique',
                              raise_if_not_found=False)
        if config:
            return config
        return self._ensure_pos_config()

    def _ensure_pos_config(self):
        """
        Caisse « Boutique (démo) », créée seulement si la comptabilité
        le permet.

        Odoo exige un journal de banque — donc un plan comptable — pour
        créer un point de vente. Déclarer la caisse en XML faisait donc
        échouer l'installation sur une société sans plan comptable ; on
        la crée ici, et on passe notre tour proprement sinon.
        """
        Config = self.env['pos.config'].sudo()
        company = self._company()
        existing = Config.search([
            ('name', '=', "Caisse Boutique (démo)"),
            ('company_id', '=', company.id),
        ], limit=1)
        if existing:
            return existing

        has_bank_journal = self.env['account.journal'].sudo().search_count([
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', company.id),
        ])
        if not has_bank_journal:
            _logger.warning(
                "Jeu d'essai : pas de journal de trésorerie sur « %s » — "
                "caisse de démonstration non créée. Installez un plan "
                "comptable puis relancez la génération.", company.name)
            return Config.browse()

        categ_xmlids = [
            'pos_cat_boutique', 'pos_cat_snacks', 'pos_cat_epicerie',
            'pos_cat_hygiene', 'pos_cat_artisanat', 'pos_cat_textile',
            'pos_cat_techno',
        ]
        categories = self.env['pos.category'].browse()
        for xmlid in categ_xmlids:
            categ = self.env.ref('aite_demo_data.%s' % xmlid,
                                 raise_if_not_found=False)
            if categ:
                categories |= categ
        vals = {
            'name': "Caisse Boutique (démo)",
            'company_id': company.id,
        }
        if categories:
            vals.update({
                'limit_categories': True,
                'iface_available_categ_ids': [(6, 0, categories.ids)],
            })
        try:
            return Config.create(vals)
        except Exception:  # noqa: BLE001
            _logger.exception(
                "Jeu d'essai : création de la caisse de démonstration "
                "impossible ; le reste du jeu reste disponible.")
            return Config.browse()

    def _pos_products(self):
        return self.env['product.product'].sudo().search([
            ('available_in_pos', '=', True),
            ('company_id', 'in', [self._company().id, False]),
        ], limit=30)

    def _cash_method(self, config):
        """Moyen de paiement comptant de la caisse (hors ardoise/folio)."""
        methods = config.payment_method_ids
        plain = methods.filtered(
            lambda m: not getattr(m, 'is_aite_credit', False)
            and not getattr(m, 'is_room_charge', False))
        if plain:
            return plain[0]
        journal = self.env['account.journal'].sudo().search([
            ('type', '=', 'cash'),
            ('company_id', '=', self._company().id),
        ], limit=1)
        if not journal:
            return self.env['pos.payment.method']
        method = self.env['pos.payment.method'].sudo().create({
            'name': "Espèces (démo)",
            'journal_id': journal.id,
            'company_id': self._company().id,
        })
        config.sudo().write({'payment_method_ids': [(4, method.id)]})
        return method

    # ------------------------------------------------------------------
    # Ardoises clients
    # ------------------------------------------------------------------

    def _generate_credits(self, count):
        """
        Ardoises réparties sur les quatre tranches d'ancienneté, dont
        certaines partiellement remboursées : la balance âgée, le taux de
        recouvrement et la liste des débiteurs sont ainsi tous peuplés.
        """
        Credit = self.env['aite.pos.credit'].sudo()
        Payment = self.env['aite.pos.credit.payment'].sudo()
        company = self._company()
        today = self._today()
        partners = self._demo_partners()
        if not partners:
            return Credit.browse()

        # (âge en jours, montant, part déjà remboursée)
        profile = [
            (3, 45000.0, 0.0), (12, 120000.0, 0.5), (25, 80000.0, 0.0),
            (38, 250000.0, 0.3), (47, 65000.0, 0.0), (55, 180000.0, 0.75),
            (68, 320000.0, 0.0), (75, 95000.0, 0.25), (88, 140000.0, 0.0),
            (102, 410000.0, 0.1), (130, 75000.0, 0.0), (160, 220000.0, 0.5),
        ]
        created = Credit.browse()
        for index in range(count):
            age, amount, paid_ratio = profile[index % len(profile)]
            partner = partners[index % len(partners)]
            note = "%s ardoise #%s" % (MARKER, index + 1)
            if Credit.search_count([('note', '=', note)]):
                continue
            credit = Credit.create({
                'partner_id': partner.id,
                'company_id': company.id,
                'amount_total': amount,
                'date_open': today - timedelta(days=age),
                'note': note,
            })
            created |= credit
            if paid_ratio > 0:
                Payment.create({
                    'credit_id': credit.id,
                    'amount': round(amount * paid_ratio),
                    'method': ('mtn', 'orange', 'cash')[index % 3],
                    'date': today - timedelta(days=max(1, age // 2)),
                    'note': "%s remboursement partiel" % MARKER,
                })
        return created

    # ------------------------------------------------------------------
    # Notes de chambre en attente
    # ------------------------------------------------------------------

    def _generate_pending_roomcharges(self, count):
        """
        File d'attente de la réception : consommations du bar qu'aucun
        folio n'a pu absorber automatiquement.
        """
        Pending = self.env['aite.roomcharge.pending'].sudo()
        Order = self.env['pos.order'].sudo()
        orders = Order.search(
            [('company_id', '=', self._company().id)], limit=count)
        created = Pending.browse()
        reasons = [
            _("Client non identifié"),
            _("Aucun folio ouvert"),
            _("2 folios ouverts"),
        ]
        for index, order in enumerate(orders):
            note = "%s %s" % (MARKER, reasons[index % len(reasons)])
            if Pending.search_count([('order_id', '=', order.id)]):
                continue
            created |= Pending.create({
                'order_id': order.id,
                'partner_id': order.partner_id.id or False,
                'amount': 15000.0 + index * 7500.0,
                'note': note,
            })
        return created

    # ------------------------------------------------------------------
    # Gouvernante
    # ------------------------------------------------------------------

    def _generate_housekeeping(self, count):
        """
        Tâches du jour cohérentes avec l'occupation : recouche sur les
        chambres libérées, ménage quotidien sur les chambres occupées,
        une inspection et une maintenance.
        """
        Task = self.env['aite.hotel.housekeeping'].sudo()
        hotel = self._hotel()
        if not hotel:
            return Task.browse()
        rooms = self.env['aite.hotel.room'].sudo().search(
            [('hotel_id', '=', hotel.id)], order='name')
        if not rooms:
            return Task.browse()

        today = self._today()
        plan = ['checkout_clean', 'daily_clean', 'daily_clean',
                'inspection', 'maintenance']
        created = Task.browse()
        for index in range(min(count, len(rooms))):
            room = rooms[index]
            task_type = plan[index % len(plan)]
            if Task.search_count([
                ('room_id', '=', room.id), ('date', '=', today),
                ('task_type', '=', task_type),
            ]):
                continue
            task = Task.create({
                'room_id': room.id,
                'task_type': task_type,
                'date': today,
                'priority': '1' if task_type == 'checkout_clean' else '0',
                'note': "%s tâche générée" % MARKER,
            })
            created |= task
            # Une tâche sur trois est déjà en cours, une sur cinq terminée.
            if index % 5 == 4:
                task.action_done()
            elif index % 3 == 2:
                task.action_start()
        return created

    # ------------------------------------------------------------------
    # Achats
    # ------------------------------------------------------------------

    def _generate_purchases(self, count):
        """
        Commandes fournisseurs échelonnées — dont des livraisons en
        retard — pour alimenter l'échéancier et l'OTIF.
        """
        Purchase = self.env['purchase.order'].sudo()
        company = self._company()
        today = self._today()

        suppliers = self._demo_suppliers()
        products = self.env['product.product'].sudo().search([
            ('purchase_ok', '=', True),
            ('is_storable', '=', True),
        ], limit=12)
        if not (suppliers and products):
            return Purchase.browse()

        created = Purchase.browse()
        for index in range(count):
            supplier = suppliers[index % len(suppliers)]
            origin = "%s achat #%s" % (MARKER, index + 1)
            if Purchase.search_count([('origin', '=', origin)]):
                continue
            days_ago = 5 + index * 7
            product = products[index % len(products)]
            cost = product.standard_price or 10000.0
            order = Purchase.create({
                'partner_id': supplier.id,
                'company_id': company.id,
                'origin': origin,
                'date_order': fields.Datetime.to_datetime(
                    str(today - timedelta(days=days_ago))),
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'name': product.display_name,
                    'product_qty': 10 + index * 5,
                    'price_unit': round(cost * (1.0 + 0.02 * index), 2),
                    'date_planned': fields.Datetime.to_datetime(
                        str(today - timedelta(days=max(0, days_ago - 4)))),
                })],
            })
            # Deux tiers confirmées, le reste en demande de prix.
            if index % 3 != 2:
                order.button_confirm()
            created |= order
        return created

    def _demo_suppliers(self):
        Partner = self.env['res.partner'].sudo()
        suppliers = Partner.search([('supplier_rank', '>', 0)], limit=5)
        if suppliers:
            return suppliers
        names = ["Brasserie de Guinée (démo)", "Grossiste Madina (démo)",
                 "Ferme Kindia (démo)", "Import Kaloum (démo)",
                 "Blanchisserie Pro (démo)"]
        created = Partner.browse()
        for name in names:
            created |= Partner.create({
                'name': name,
                'is_company': True,
                'supplier_rank': 1,
            })
        return created

    def _generate_deposits(self):
        """Consignes d'emballages immobilisées chez les fournisseurs."""
        Deposit = self.env['aite.purchase.deposit'].sudo()
        company = self._company()
        created = Deposit.browse()
        for index, supplier in enumerate(self._demo_suppliers()):
            if Deposit.search_count([
                ('partner_id', '=', supplier.id),
                ('company_id', '=', company.id),
            ]):
                continue
            created |= Deposit.create({
                'partner_id': supplier.id,
                'company_id': company.id,
                'qty': 20 + index * 15,
                'unit_value': 25000.0,
                'note': "%s consignes casiers" % MARKER,
            })
        return created

    # ------------------------------------------------------------------
    # Nettoyage
    # ------------------------------------------------------------------

    @api.model
    def purge_generated(self):
        """
        Retire ce que ``generate_all`` a produit (repère ``[démo]``).

        Deux exceptions volontaires :

        * le **référentiel** posé par les fichiers XML n'est pas touché —
          il part avec la désinstallation du module ;
        * l'**historique de caisse** est conservé : une vente encaissée
          porte des écritures comptables et des mouvements de stock, et
          Odoo en interdit la suppression. Le compte des sessions et des
          commandes conservées figure dans le rapport retourné.
        """
        counts = {}
        like = '%' + MARKER + '%'
        for model, field in [
            ('aite.pos.credit.payment', 'note'),
            ('aite.pos.credit', 'note'),
            ('aite.roomcharge.pending', 'note'),
            ('aite.hotel.housekeeping', 'note'),
            ('aite.purchase.deposit', 'note'),
        ]:
            records = self.env[model].sudo().search([(field, 'like', like)])
            counts[model] = len(records)
            records.unlink()
        orders = self.env['purchase.order'].sudo().search(
            [('origin', 'like', like)])
        counts['purchase.order'] = len(orders)
        orders.button_cancel()
        orders.unlink()

        # L'historique de caisse est CONSERVÉ : Odoo interdit — à juste
        # titre — de supprimer une vente encaissée, qui porte des
        # écritures et des mouvements de stock. La génération reste
        # idempotente de son côté (une session par jour, repérée par son
        # identifiant externe), donc relancer ne duplique rien.
        sessions = self._tagged_all('pos.session')
        counts['pos.session (conservées)'] = len(sessions)
        counts['pos.order (conservées)'] = self.env['pos.order'].sudo(
        ).search_count([('session_id', 'in', sessions.ids)])

        _logger.info("Jeu d'essai généré purgé : %s", counts)
        return counts
