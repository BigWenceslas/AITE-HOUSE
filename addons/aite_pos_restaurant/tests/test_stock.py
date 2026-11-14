# -*- coding: utf-8 -*-
"""Les produits épuisés (spécification, parties 4.1, 4.2 et 6.2 ; incrément 5).

``product.product.aite_stock_disponible(config_id)`` est la seule requête de
la caisse pour le stock : pour chaque produit suivi (« Suivre l'inventaire »)
proposé en caisse, la quantité en stock de l'entrepôt de la caisse, **moins**
ce qui est déjà parti sur les tables encore ouvertes de cet entrepôt (REST-19b
critère 4, Q46). La caisse retire elle-même ce qu'elle a saisi sans l'envoyer.
Un produit sans suivi (un plat) n'y figure pas : il se vend toujours.

Les données passent par le chemin de la caisse (``sync_from_ui``, sous le
compte de la caisse) ; l'entrée de stock est faite comme le manager la fait
(« Mettre la quantité à jour » : inventaire appliqué).
"""
import logging
import time
from uuid import uuid4

from odoo.tests import tagged

from .common import Addition, RestaurantCommon

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestStock(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Produit = cls.env['product.product']
        # Une bière vendue à l'unité, suivie en stock (case « Suivre
        # l'inventaire ») ; le poulet DG du socle commun, lui, ne l'est pas.
        cls.biere = Produit.create({
            'name': "Guinness", 'type': 'consu', 'is_storable': True,
            'available_in_pos': True, 'list_price': 1200.0, 'taxes_id': [(5, 0, 0)]})
        cls.entrepot = cls.config.picking_type_id.warehouse_id
        cls.especes = cls.config.payment_method_ids.filtered('is_cash_count')[:1] \
            or cls.config.payment_method_ids[:1]

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()

    # ------------------------------------------------------------------
    # Aides
    # ------------------------------------------------------------------

    def _disponible(self, user=None):
        """Ce que la caisse reçoit (requête sous le compte de la caisse)."""
        return self.env['product.product'].with_user(user or self.compte_caisse) \
            .aite_stock_disponible(self.config.id)

    def _entree(self, produit, quantite, emplacement=None):
        """Le manager enregistre une entrée de stock : la quantité comptée
        devient ``quantite`` de plus."""
        emplacement = emplacement or self.entrepot.lot_stock_id
        Quant = self.env['stock.quant'].with_context(inventory_mode=True)
        quant = Quant.search([('product_id', '=', produit.id),
                              ('location_id', '=', emplacement.id)], limit=1)
        deja = quant.quantity if quant else 0.0
        if not quant:
            quant = Quant.create({'product_id': produit.id, 'location_id': emplacement.id})
        quant.inventory_quantity = deja + quantite
        quant.action_apply_inventory()

    def _table_envoyee(self, produit, quantite, table=None, envoyer=True):
        addition = Addition(table or self.table_12, 2, self.awa)
        uuid = addition.ajouter(produit, quantite)
        if envoyer:
            addition.envoyer()
        commande = self._commande_caisse(addition, self.awa)
        return addition, uuid, commande

    # ------------------------------------------------------------------
    # REST-19a : refus à zéro, de nouveau vendable après une entrée
    # ------------------------------------------------------------------

    def test_produit_suivi_a_zero(self):
        self.assertEqual(self._disponible().get(self.biere.id), 0)

    def test_envoyes_sur_une_table_ouverte_puis_entree_de_stock(self):
        """À 2 en stock, 2 envoyées sur une table ouverte : 0 (19b) ; après
        une entrée d'une bouteille : 1."""
        self._entree(self.biere, 2)
        self.assertEqual(self._disponible()[self.biere.id], 2)
        _addition, _uuid, commande = self._table_envoyee(self.biere, 2)
        self.assertEqual(commande.state, 'draft')
        self.assertEqual(commande.lines.aite_qte_envoyee, 2)
        self.assertEqual(self._disponible()[self.biere.id], 0)
        self._entree(self.biere, 1)
        self.assertEqual(self._disponible()[self.biere.id], 1)

    def test_saisi_pas_envoye_ne_compte_pas(self):
        """Ce qui est saisi sans être envoyé reste disponible pour le
        serveur : c'est la caisse qui le retire, sur sa propre addition."""
        self._entree(self.biere, 2)
        self._table_envoyee(self.biere, 2, envoyer=False)
        self.assertEqual(self._disponible()[self.biere.id], 2)

    def test_annulation_rend_disponible(self):
        """Une bouteille envoyée puis annulée avec le code d'un chef de salle
        redevient disponible (19b critère 6)."""
        self._entree(self.biere, 2)
        _addition, uuid, commande = self._table_envoyee(self.biere, 2)
        motif = self.env.ref('aite_pos_restaurant.motif_erreur_saisie')
        reponse = self.env['pos.order'].with_user(self.compte_caisse).aite_autoriser_annulation(
            commande.ids, [{'uuid': uuid, 'quantite': 1}], '4444', motif.id, False,
            self.awa.id, str(uuid4()), 'produit')
        self.assertNotIn('erreur', reponse)
        self.assertEqual(self._disponible()[self.biere.id], 1)

    def test_table_encaissee_compte_une_fois(self):
        """Encaissée, la table sort du stock (temps réel, réglage par défaut
        d'Odoo) et ne compte plus comme « partie » : pas de double décompte."""
        self._entree(self.biere, 3)
        addition, _uuid, commande = self._table_envoyee(self.biere, 2)
        self.assertEqual(self._disponible()[self.biere.id], 1)
        self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)
        self.assertEqual(commande.state, 'paid')
        self.assertEqual(self.biere.with_context(warehouse_id=self.entrepot.id).qty_available, 1)
        self.assertEqual(self._disponible()[self.biere.id], 1)

    def test_table_annulee_ne_compte_plus(self):
        self._entree(self.biere, 2)
        _addition, _uuid, commande = self._table_envoyee(self.biere, 2)
        commande.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(commande.state, 'cancel')
        self.assertEqual(self._disponible()[self.biere.id], 2)

    # ------------------------------------------------------------------
    # Ce qui n'est pas contrôlé
    # ------------------------------------------------------------------

    def test_plat_non_suivi_absent(self):
        """Le poulet DG n'est pas suivi en stock : il se vend toujours
        (REST-19 critère 3)."""
        self.assertFalse(self.poulet.is_storable)
        self.assertNotIn(self.poulet.id, self._disponible())

    def test_produit_pas_en_caisse_absent(self):
        cave = self.env['product.product'].create({
            'name': "Bouteille de la cave", 'type': 'consu', 'is_storable': True,
            'available_in_pos': False})
        self.assertNotIn(cave.id, self._disponible())

    def test_kit_absent(self):
        """Un kit (Fabrication) n'a pas de stock propre : il n'est pas
        contrôlé (son stock se lit dans ses composants)."""
        Produit = self.env['product.product']
        if 'is_kits' not in Produit._fields:
            self.skipTest("Fabrication (mrp) n'est pas installé")
        kit = Produit.create({'name': "Seau de 5 bières", 'type': 'consu', 'is_storable': True,
                              'available_in_pos': True})
        self.env['mrp.bom'].create({
            'product_tmpl_id': kit.product_tmpl_id.id, 'type': 'phantom',
            'bom_line_ids': [(0, 0, {'product_id': self.biere.id, 'product_qty': 5})]})
        self.assertTrue(kit.is_kits)
        self.assertNotIn(kit.id, self._disponible())

    def test_stock_d_un_autre_entrepot_ne_compte_pas(self):
        autre = self.env['stock.warehouse'].create({
            'name': "Entrepôt du traiteur", 'code': 'TRT', 'company_id': self.company.id})
        self._entree(self.biere, 10, emplacement=autre.lot_stock_id)
        self._entree(self.biere, 1)
        self.assertEqual(self._disponible()[self.biere.id], 1)

    # ------------------------------------------------------------------
    # La requête de la caisse
    # ------------------------------------------------------------------

    def test_une_requete_pour_tous_les_produits_suivis(self):
        """Une seule réponse pour toute la carte : produit → disponible."""
        self._entree(self.biere, 4)
        castel = self.castel
        castel.is_storable = True
        self._entree(castel, 6)
        disponible = self._disponible()
        self.assertEqual({k: disponible[k] for k in (self.biere.id, castel.id)},
                         {self.biere.id: 4, castel.id: 6})

    def test_temps_de_la_requete_200_produits(self):
        """Mesure demandée avant d'écrire la mémoire de 60 secondes (partie 7,
        incrément 5) : 200 produits suivis, 20 tables ouvertes avec des
        produits envoyés. Le temps est écrit au journal ; la borne n'est là
        que pour signaler une requête qui s'emballerait."""
        Produit = self.env['product.product']
        produits = Produit.create([{
            'name': "Boisson %03d" % i, 'type': 'consu', 'is_storable': True,
            'available_in_pos': True, 'list_price': 500.0, 'taxes_id': [(5, 0, 0)],
        } for i in range(200)])
        Quant = self.env['stock.quant'].with_context(inventory_mode=True)
        quants = Quant.create([{'product_id': p.id, 'location_id': self.entrepot.lot_stock_id.id,
                                'inventory_quantity': 24} for p in produits])
        quants.action_apply_inventory()
        Table = self.env['restaurant.table']
        salle = self.config.floor_ids[:1]
        for n in range(20):
            table = Table.create({'floor_id': salle.id, 'table_number': 100 + n, 'seats': 4})
            addition = Addition(table, 2, self.awa)
            for p in produits[n * 10:(n + 1) * 10]:
                addition.ajouter(p, 2)
            addition.envoyer()
            self._commande_caisse(addition, self.awa)
        self.env.flush_all()
        self.env.invalidate_all()
        debut = time.perf_counter()
        disponible = self._disponible()
        duree = (time.perf_counter() - debut) * 1000
        _logger.info("Restaurant : aite_stock_disponible, %d produits suivis, 20 tables "
                     "ouvertes : %.0f ms", len(disponible), duree)
        self.assertEqual(disponible[produits[0].id], 22)
        self.assertEqual(disponible[produits[199].id], 22)
        self.assertGreaterEqual(len(disponible), 200)
        self.assertLess(duree, 5000)
