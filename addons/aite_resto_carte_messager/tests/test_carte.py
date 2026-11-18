# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from odoo.addons.aite_resto_carte_messager import jouer_carte


@tagged('post_install', '-at_install', 'aite_carte_messager')
class TestCarteMessager(TransactionCase):

    def test_carte_posee_et_rejouable(self):
        Produits = self.env['product.template']
        self.assertEqual(Produits.search_count([('name', '=', 'Pizza Marguerite Grand')]), 1)
        medoc = Produits.search([('name', '=', 'Médoc')])
        self.assertEqual((medoc.list_price, medoc.standard_price, medoc.is_storable), (20000, 9500, True))
        self.assertFalse(medoc.taxes_id, "aucune taxe sur les produits")
        self.assertFalse(Produits.search([('name', '=', 'Poulet DG')]).standard_price,
                         "aucun coût inventé pour un plat")
        avant = Produits.search_count([])
        jouer_carte(self.env)
        self.assertEqual(Produits.search_count([]), avant, "rejouer ne crée rien")

    def test_societe_non_renommee(self):
        nom = self.env.company.name
        jouer_carte(self.env)
        self.assertEqual(self.env.company.name, nom)

    def test_salle_et_equipe(self):
        caisse = self.env['pos.config'].search([('aite_mode_restaurant', '=', True)], limit=1)
        self.assertGreaterEqual(len(caisse.floor_ids[:1].table_ids), 12)
        niveaux = set(self.env['hr.employee'].search([('aite_niveau_caisse', '!=', False)]).mapped('aite_niveau_caisse'))
        self.assertEqual(niveaux, {'serveur', 'caissiere', 'superviseur', 'manager'})
        for login in ('caisse', 'manager', 'chef'):
            self.assertTrue(self.env['res.users'].search_count([('login', '=', login)]), login)
        avant = self.env['hr.employee'].search_count([])
        jouer_carte(self.env)
        self.assertEqual(self.env['hr.employee'].search_count([]), avant, "rejouer ne crée rien")

    def test_comptes_avec_courriel(self):
        """Odoo écrit l'ouverture et la validation de la caisse au nom du compte
        connecté : sans courriel, « Impossible d'envoyer le message, veuillez
        configurer l'adresse e-mail de l'expéditeur » (constaté chez le client)."""
        for login in ('caisse', 'manager', 'chef'):
            user = self.env['res.users'].search([('login', '=', login)])
            self.assertTrue(user.email, login)
        # un compte de démonstration resté sans courriel est complété à la mise à niveau
        caisse = self.env['res.users'].search([('login', '=', 'caisse')])
        caisse.email = False
        jouer_carte(self.env)
        self.assertTrue(caisse.email)

    def test_manager_lit_les_ardoises(self):
        """Le tableau de bord Direction lit les ardoises : sans « POS Crédit », le
        manager de la démonstration recevait « Erreur d'accès » (aite.pos.credit)."""
        manager = self.env['res.users'].search([('login', '=', 'manager')])
        self.assertTrue(manager.has_group('aite_pos_credit.group_pos_credit_user'))
        manager.groups_id -= self.env.ref('aite_pos_credit.group_pos_credit_user')
        jouer_carte(self.env)
        self.assertTrue(manager.has_group('aite_pos_credit.group_pos_credit_user'))

    # ------------------------------------------------------------------
    # Recette : le coût des boissons revendues suit les achats (AVCO)
    # ------------------------------------------------------------------

    def _categorie(self, *chemin):
        categorie = self.env['product.category']
        for nom in chemin:
            categorie = self.env['product.category'].search(
                [('name', '=', nom), ('parent_id', '=', categorie.id or False)], limit=1)
        return categorie

    def test_boissons_en_cout_moyen(self):
        """« Bar » et toutes ses sous-familles en « Coût moyen (AVCO) » ; les
        plats restent en prix standard."""
        bar = self._categorie("Bar")
        self.assertTrue(bar)
        for categorie in self.env['product.category'].search([('id', 'child_of', bar.id)]):
            self.assertEqual(categorie.property_cost_method, 'average', categorie.complete_name)
        self.assertEqual(self._categorie("Plats").property_cost_method, 'standard')
        biere = self.env['product.template'].search([('name', '=', "Bière blonde 65 cl")])
        self.assertEqual(biere.cost_method, 'average')

    def _recevoir(self, produit, quantite, prix):
        """Une réception fournisseur validée (ce que fait un bon de commande reçu)."""
        entrepot = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        mouvement = self.env['stock.move'].create({
            'name': "Achat de test", 'product_id': produit.id, 'product_uom_qty': quantite,
            'product_uom': produit.uom_id.id, 'price_unit': prix,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': entrepot.lot_stock_id.id,
        })
        mouvement._action_confirm()
        mouvement.quantity = quantite
        mouvement.picked = True
        mouvement._action_done()

    def test_cout_suit_les_achats(self):
        """Bière blonde 65 cl : 48 en stock à 650 ; 48 achetées à 700 → coût
        moyen 675 ; rejouer la carte ne remet pas 650."""
        biere = self.env['product.template'].search([('name', '=', "Bière blonde 65 cl")])
        self.assertEqual((biere.standard_price, biere.qty_available), (650, 48))
        self._recevoir(biere.product_variant_id, 48, 700)
        self.assertEqual(biere.standard_price, 675)
        jouer_carte(self.env)
        self.assertEqual(biere.standard_price, 675, "le coût issu des achats n'est pas écrasé")

    # ------------------------------------------------------------------
    # Recette : la notification du bouton, lisible par un manager
    # ------------------------------------------------------------------

    def test_bilan_lisible_en_francais(self):
        action = self.env['pos.config']._aite_action_poser_carte_messager()
        message = action['params']['message']
        nb_familles = self.env['pos.category'].search_count([('id', 'child_of', self.env['pos.category'].search(
            [('name', 'in', ("Petit déjeuner", "Plats", "Pizzas & burgers", "Afternoon tea", "Bar")),
             ('parent_id', '=', False)]).ids)])
        self.assertIn("%s : Carte posée : 101 produits en %d familles ; salle : 12 tables ; "
                      "équipe : 7 employés, 3 comptes. Rien n'a été créé en double."
                      % (self.env.company.name, nb_familles), message)
        for technique in ("seed", "OK", "créés :", "en place", "|", "attendus"):
            self.assertNotIn(technique, message)
