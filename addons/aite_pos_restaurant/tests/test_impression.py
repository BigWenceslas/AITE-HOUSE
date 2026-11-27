# -*- coding: utf-8 -*-
"""Le nombre d'exemplaires des bons de préparation (demande du Messager :
« imprimer 3 fois d'un coup en cuisine »).

Le réglage est porté par l'imprimante de préparation (``pos.printer``) :
« Nombre d'exemplaires du bon », 1 d'office, entre 1 et 5, avec la phrase
« ce qui va se passer » ; la caisse le reçoit au démarrage. Le rendu des bons
(« Exemplaire 2/3 », titres en français) est vérifié par les tours
(``TestToursBons``).
"""
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestImpression(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cuisine = cls.env['pos.printer'].create({'name': "Cuisine"})

    def test_un_exemplaire_d_office(self):
        self.assertEqual(self.cuisine.aite_exemplaires, 1)
        self.assertIn("un seul exemplaire", self.cuisine.aite_exemplaires_phrase)

    def test_entre_un_et_cinq(self):
        for nombre in (0, -1, 6, 10):
            with self.subTest(nombre=nombre), self.assertRaises(ValidationError) as erreur:
                with self.env.cr.savepoint():
                    self.cuisine.aite_exemplaires = nombre
            self.assertIn("entre 1 et 5", str(erreur.exception))
        for nombre in (1, 3, 5):
            self.cuisine.aite_exemplaires = nombre
            self.assertEqual(self.cuisine.aite_exemplaires, nombre)

    def test_la_phrase_dit_ce_qui_va_se_passer(self):
        self.cuisine.aite_exemplaires = 3
        phrase = self.cuisine.aite_exemplaires_phrase
        self.assertIn("Chaque nouveau bon envoyé à cette imprimante sort en 3 exemplaires "
                      "identiques", phrase)
        self.assertIn("Exemplaire 1/3", phrase)
        self.assertIn("Les annulations et les notes seules sortent en un exemplaire", phrase)

    def test_le_formulaire_de_l_imprimante(self):
        arch = self.env['pos.printer'].get_view(
            self.env.ref('point_of_sale.view_pos_printer_form').id, 'form')['arch']
        self.assertIn('name="aite_exemplaires"', arch)
        self.assertIn('name="aite_exemplaires_phrase"', arch)

    def test_la_caisse_recoit_le_reglage(self):
        self.cuisine.aite_exemplaires = 3
        self.config.write({'is_order_printer': True, 'printer_ids': [(6, 0, self.cuisine.ids)]})
        self.assertIn('aite_exemplaires',
                      self.env['pos.printer']._load_pos_data_fields(self.config.id))
        self.config.open_ui()
        donnees = self.config.current_session_id.with_user(self.compte_caisse).load_data(
            ['pos.config', 'pos.printer'])
        imprimantes = {p['name']: p for p in donnees['pos.printer']['data']}
        self.assertEqual(imprimantes["Cuisine"]['aite_exemplaires'], 3)
