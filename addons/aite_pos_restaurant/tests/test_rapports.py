# -*- coding: utf-8 -*-
"""Les rapports du restaurant (spécification, parties 3.4, 5 et 6.2).

Incrément 4 : le rapport des annulations (REST-22) et le profil de lecture
du chef de salle (AH-05) — il lit les annulations sans aucun droit sur la
caisse : il ne peut ni ouvrir une session ni voir la configuration.
Les compteurs « Personnes et tables » et le rapport de fermeture arrivent à
l'incrément 6.
"""
from uuid import uuid4

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import Addition, RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestRapportAnnulations(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.groupe_lecture = cls.env.ref('aite_pos_restaurant.group_lecture_rapports')
        cls.chef = Users.create({
            'name': "Chef de salle", 'login': 'aite_chef_resto',
            'company_id': cls.company.id, 'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [cls.groupe_lecture.id])],
        })

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()

    def _trois_annulations(self):
        """Trois annulations autorisées par Paul, sur trois tables."""
        motif = self.env.ref('aite_pos_restaurant.motif_erreur_saisie')
        for table, produit, quantite in ((self.table_12, self.castel, 2),
                                         (self.table_7, self.poulet, 1),
                                         (self.table_12.copy({'table_number': 3}),
                                          self.castel, 1)):
            addition = Addition(table, 2, self.awa)
            uuid = addition.ajouter(produit, quantite)
            addition.envoyer()
            commande = self._commande_caisse(addition, self.awa)
            reponse = self.env['pos.order'].with_user(self.compte_caisse) \
                .aite_autoriser_annulation(commande.ids, [{'uuid': uuid, 'quantite': quantite}],
                                           '4444', motif.id, False, self.awa.id,
                                           str(uuid4()), 'produit')
            self.assertNotIn('erreur', reponse)

    def test_trois_annulations_et_leur_total(self):
        self._trois_annulations()
        Annulation = self.env['aite.restaurant.annulation'].with_user(self.compte_manager)
        self.assertEqual(Annulation.search_count([]), 3)
        total = Annulation.read_group([], ['montant:sum', 'quantite:sum'], [])[0]
        self.assertEqual(total['montant'], 2 * 1000 + 6500 + 1000)
        self.assertEqual(total['quantite'], 4)

    def test_le_chef_de_salle_lit_les_annulations(self):
        """AH-05 : le profil de lecture lit les annulations, ne lit ni la
        caisse ni les commandes, et ne voit pas le menu Point de Vente."""
        self._trois_annulations()
        self.assertFalse(self.chef.has_group('point_of_sale.group_pos_user'))
        self.assertTrue(self.chef._is_internal())
        Annulation = self.env['aite.restaurant.annulation'].with_user(self.chef)
        lues = Annulation.search([])
        self.assertEqual(len(lues), 3)
        # Ce que montrent la liste et la vue croisée : des noms recopiés,
        # lisibles sans aucun droit sur les employés, la caisse ou les
        # commandes.
        vue = self.env.ref('aite_pos_restaurant.view_restaurant_annulation_list')
        champs = Annulation.get_views([(vue.id, 'list')])['models'][
            'aite.restaurant.annulation']['fields']
        lignes = Annulation.web_search_read([], {champ: {} for champ in champs
                                                 if champ not in ('currency_id',)})
        self.assertEqual(lignes['length'], 3)
        Annulation.read_group([], ['montant:sum'], ['motif_nom'])
        Annulation.read_group([], ['quantite:sum'], ['serveur_nom', 'superieur_nom',
                                                     'produit_nom', 'date:day'])
        for modele in ('pos.order', 'pos.config', 'pos.session'):
            with self.subTest(modele=modele):
                with self.assertRaises(AccessError):
                    self.env[modele].with_user(self.chef).search([])
        menus = self.env['ir.ui.menu'].with_user(self.chef)._visible_menu_ids()
        self.assertIn(self.env.ref('aite_pos_restaurant.menu_restaurant_root').id, menus)
        self.assertIn(self.env.ref('aite_pos_restaurant.menu_restaurant_annulation').id, menus)
        self.assertNotIn(self.env.ref('point_of_sale.menu_point_root').id, menus)
        # Ni effacer ni modifier (UserError, dont AccessError hérite).
        with self.assertRaises(UserError):
            lues[:1].with_user(self.chef).unlink()

    def test_le_manager_et_l_administrateur_ont_le_profil_de_lecture(self):
        self.assertTrue(self.compte_manager.has_group(
            'aite_pos_restaurant.group_lecture_rapports'))
        self.assertTrue(self.env.ref('base.user_admin').has_group(
            'aite_pos_restaurant.group_lecture_rapports'))
        self.assertFalse(self.compte_caisse.has_group(
            'aite_pos_restaurant.group_lecture_rapports'))
        menus = self.env['ir.ui.menu'].with_user(self.compte_manager)._visible_menu_ids()
        self.assertIn(self.env.ref('aite_pos_restaurant.menu_restaurant_motif').id, menus)

    def test_une_societe_ne_voit_que_ses_annulations(self):
        self._trois_annulations()
        autre = self.env['res.company'].create({'name': "Autre restaurant"})
        self.chef.write({'company_ids': [(4, autre.id)], 'company_id': autre.id})
        Annulation = self.env['aite.restaurant.annulation'].with_user(self.chef)
        self.assertEqual(Annulation.with_context(allowed_company_ids=autre.ids).search_count([]), 0)
        self.assertEqual(Annulation.with_context(
            allowed_company_ids=self.company.ids).search_count([]), 3)

    def test_aides_d_ecran_vide(self):
        """Règle 2 de CLAUDE.md : chaque écran vide dit quoi faire."""
        for xmlid in ('action_restaurant_annulation', 'action_restaurant_motif'):
            with self.subTest(action=xmlid):
                action = self.env.ref('aite_pos_restaurant.%s' % xmlid)
                self.assertIn('o_view_nocontent', action.help)
                self.assertGreaterEqual(len(action.help), 120)

    def test_periode_du_jour_par_defaut(self):
        action = self.env.ref('aite_pos_restaurant.action_restaurant_annulation')
        self.assertIn('search_default_aujourd_hui', action.context)
