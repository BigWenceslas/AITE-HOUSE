# -*- coding: utf-8 -*-
"""Les familles de la carte (demandes du restaurant de Douala, 18.0.1.0.14).

* L'imprimante « Autre » : la case « Prend tout ce qu'aucune autre
  imprimante ne prend » sur l'imprimante de préparation, sa phrase « ce qui
  va se passer », au plus une par caisse, lue par la caisse au démarrage.
* Les familles orphelines : sur le formulaire de l'imprimante (et dans les
  réglages de la caisse), la liste des familles de la carte qu'aucune
  imprimante ne prend, quand la caisse n'a pas d'imprimante « Autre ».
* L'envoi direct aux Epson en Wi-Fi : la dépendance à pos_epson_printer.
* « Grouper les produits par famille sur l'addition et le ticket » : le
  réglage de la caisse, décoché d'office, avec sa phrase.

Le routage des bons et le rendu des tickets sont vérifiés par les tours
(``TestToursFamilles``, ``TestToursAdditionFamilles``).
"""
from odoo.exceptions import ValidationError
from odoo.modules.module import get_manifest
from odoo.tests import tagged

from .common import RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestFamilles(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Famille = cls.env['pos.category']
        cls.plats = Famille.create({'name': "Plats AITE", 'sequence': 10})
        cls.grillades = Famille.create({'name': "Grillades", 'parent_id': cls.plats.id})
        cls.pizzas_burgers = Famille.create({'name': "Pizzas & burgers", 'sequence': 11})
        cls.pizzas = Famille.create({'name': "Pizzas", 'parent_id': cls.pizzas_burgers.id})
        cls.pastas = Famille.create({'name': "Pastas", 'parent_id': cls.pizzas_burgers.id})
        cls.desserts = Famille.create({'name': "Desserts", 'sequence': 12})
        cls.vide = Famille.create({'name': "Famille sans produit", 'sequence': 14})
        cls.bar = Famille.create({'name': "Bar AITE", 'sequence': 13})
        vins = Famille.create({'name': "Vins", 'parent_id': cls.bar.id})
        cls.vins_blancs = Famille.create({'name': "Vins blancs", 'parent_id': vins.id})
        Produit = cls.env['product.product']
        for nom, famille in (("Poulet braisé", cls.grillades), ("Pizza Marguerite", cls.pizzas),
                             ("Penne", cls.pastas), ("Glace vanille", cls.desserts),
                             ("Vin blanc", cls.vins_blancs), ("Pain maison", None)):
            Produit.create({'name': nom, 'available_in_pos': True, 'list_price': 1000,
                            'pos_categ_ids': [(6, 0, famille.ids if famille else [])]})
        Imprimante = cls.env['pos.printer']
        cls.chaud = Imprimante.create({
            'name': "Chaud", 'product_categories_ids': [(6, 0, cls.plats.ids)]})
        cls.pizza = Imprimante.create({
            'name': "Pizza", 'product_categories_ids': [(6, 0, cls.pizzas.ids)]})
        cls.imprimante_bar = Imprimante.create({
            'name': "Bar", 'product_categories_ids': [(6, 0, cls.bar.ids)]})
        cls.config.write({
            'is_order_printer': True,
            'printer_ids': [(6, 0, (cls.chaud | cls.pizza | cls.imprimante_bar).ids)],
        })

    def _autre(self, nom="Autre"):
        return self.env['pos.printer'].create({'name': nom, 'aite_prend_le_reste': True})

    # ------------------------------------------------------- l'imprimante « Autre »

    def test_case_autre_decochee_d_office(self):
        self.assertFalse(self.chaud.aite_prend_le_reste)
        champ = self.env['pos.printer']._fields['aite_prend_le_reste']
        self.assertEqual(champ.string, "Prend tout ce qu'aucune autre imprimante ne prend")

    def test_phrase_de_la_case_autre(self):
        autre = self._autre()
        self.assertIn("aucune autre imprimante de la caisse", autre.aite_prend_le_reste_phrase)
        self.assertIn("jamais perdu", autre.aite_prend_le_reste_phrase)
        self.assertIn("une seule imprimante « Autre » par caisse", autre.aite_prend_le_reste_phrase)
        self.assertIn("seulement les familles cochées", self.chaud.aite_prend_le_reste_phrase)

    def test_une_seule_autre_par_caisse(self):
        premiere, seconde = self._autre("Autre"), self._autre("Autre 2")
        self.config.printer_ids = [(4, premiere.id)]
        with self.assertRaises(ValidationError) as erreur, self.env.cr.savepoint():
            self.config.printer_ids = [(4, seconde.id)]
        self.assertIn("une seule imprimante « Autre »", str(erreur.exception))
        self.assertIn("Autre 2", str(erreur.exception))
        # Cocher la case sur une imprimante d'une caisse qui en a déjà une.
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.chaud.aite_prend_le_reste = True
        # Deux caisses, une « Autre » chacune : permis.
        self.config.printer_ids = [(3, premiere.id)]
        self.config.printer_ids = [(4, seconde.id)]
        self.assertIn(seconde, self.config.printer_ids)

    def test_la_caisse_recoit_la_case(self):
        self.assertIn('aite_prend_le_reste',
                      self.env['pos.printer']._load_pos_data_fields(self.config.id))

    def test_le_formulaire_de_l_imprimante(self):
        arch = self.env['pos.printer'].get_view(
            self.env.ref('point_of_sale.view_pos_printer_form').id, 'form')['arch']
        for champ in ('aite_prend_le_reste', 'aite_prend_le_reste_phrase',
                      'aite_familles_orphelines'):
            self.assertIn('name="%s"' % champ, arch)

    # ------------------------------------------------------- familles orphelines

    def test_familles_orphelines(self):
        """Sans imprimante « Autre » : les desserts, les pastas (sous-famille
        de « Pizzas & burgers », dont seules les pizzas sont prises) et les
        produits sans famille ; ni ce qui est pris (Plats et ses
        sous-familles, Vins blancs sous Bar), ni une famille sans produit."""
        texte = self.chaud.aite_familles_orphelines
        for attendu in ("Desserts", "Pizzas & burgers / Pastas", "sans famille"):
            self.assertIn(attendu, texte)
        for absent in ("Plats AITE", "Grillades", "Vins blancs", "Bar AITE",
                       "Famille sans produit", "Pizzas & burgers / Pizzas"):
            self.assertNotIn(absent, texte)
        self.assertIn("« Autre »", texte)
        # Le même avertissement dans les réglages de la caisse.
        self.assertEqual(self.config.aite_familles_orphelines, texte)

    def test_pas_d_orphelines_avec_autre(self):
        self.config.printer_ids = [(4, self._autre().id)]
        self.assertFalse(self.chaud.aite_familles_orphelines)
        self.assertFalse(self.config.aite_familles_orphelines)

    def test_pas_d_orphelines_quand_tout_est_pris(self):
        self.imprimante_bar.product_categories_ids = [
            (4, self.desserts.id), (4, self.pastas.id)]
        self.env['product.product'].search([('name', '=', "Pain maison")]).pos_categ_ids = [
            (6, 0, self.desserts.ids)]
        orphelines = self.config.aite_familles_orphelines or ""
        for absent in ("Desserts", "Pastas", "Pain maison"):
            self.assertNotIn(absent, orphelines)

    def test_imprimante_d_aucune_caisse(self):
        seule = self.env['pos.printer'].create({'name': "Seule"})
        self.assertFalse(seule.aite_familles_orphelines)

    # ------------------------------------------------------- Epson en Wi-Fi

    def test_envoi_direct_aux_epson(self):
        """Les tablettes impriment sans boîtier IoT sur les Epson TM-m30III :
        le module dépend de pos_epson_printer (type « Epson » et adresse IP
        sur l'imprimante)."""
        self.assertIn('pos_epson_printer', get_manifest('aite_pos_restaurant')['depends'])
        self.assertIn('epson_epos', dict(
            self.env['pos.printer']._fields['printer_type'].selection))

    # ------------------------------------------------------- l'addition groupée

    def test_grouper_decoche_d_office(self):
        caisse = self.env['pos.config'].create({'name': "Bar de la terrasse"})
        self.assertFalse(caisse.aite_grouper_familles)
        self.assertFalse(self.config.aite_grouper_familles)

    def test_reglage_grouper_dans_les_reglages(self):
        arch = self.env['res.config.settings'].get_view(
            self.env.ref('point_of_sale.res_config_settings_view_form').id, 'form')['arch']
        self.assertIn('name="pos_aite_grouper_familles"', arch)
        self.assertIn("Grouper les produits par famille sur l'addition et le ticket", arch)
        self.assertIn("Sous-total", arch)
        self.assertIn('name="pos_aite_familles_orphelines"', arch)

    # ------------------------------------------------------- relectures de 18.0.1.0.14

    def test_orphelines_pendant_la_saisie(self):
        """Relecture (code, 1) : sur le formulaire de l'imprimante, le cadre
        orange suit la saisie, avant tout enregistrement. Cocher « Bar » sur
        Chaud laisse les desserts orphelins : le cadre reste ; cocher
        « Desserts » les retire du cadre ; cocher la case « Autre » l'efface."""
        from odoo.tests import Form
        with Form(self.chaud) as formulaire:
            formulaire.product_categories_ids.add(self.bar)
            self.assertTrue(formulaire.aite_familles_orphelines,
                            "le cadre disparaît pendant la saisie")
            self.assertIn("Desserts", formulaire.aite_familles_orphelines)
            formulaire.product_categories_ids.add(self.desserts)
            self.assertNotIn("Desserts", formulaire.aite_familles_orphelines or "")
            self.assertIn("Pastas", formulaire.aite_familles_orphelines)
            formulaire.aite_prend_le_reste = True
            self.assertFalse(formulaire.aite_familles_orphelines)
            formulaire.aite_prend_le_reste = False
            formulaire.product_categories_ids.remove(self.desserts.id)
            formulaire.product_categories_ids.remove(self.bar.id)
        # Rien n'est enregistré de travers : en base, le cadre est le même.
        self.assertIn("Desserts", self.chaud.aite_familles_orphelines)

    def test_autre_hors_mode(self):
        """Relectures (code 2, terrain 2) : l'imprimante « Autre » n'agit
        qu'au service à table contrôlé. Sur une caisse hors de ce mode,
        l'avertissement reste, et dit que la case n'y fait rien ; la phrase
        de la case le dit aussi."""
        autre = self._autre()
        caisse = self.env['pos.config'].create({
            'name': "Bar piscine", 'module_pos_restaurant': True,
            'is_order_printer': True,
            'printer_ids': [(6, 0, (self.imprimante_bar | autre).ids)]})
        self.assertFalse(caisse._aite_actif())
        texte = caisse.aite_familles_orphelines
        self.assertTrue(texte, "l'avertissement est masqué hors mode")
        self.assertIn("Desserts", texte)
        self.assertIn("service à table contrôlé", texte)
        self.assertIn("Autre", texte)
        self.assertIn("Desserts", autre.aite_familles_orphelines)
        self.assertIn("service à table contrôlé seulement", autre.aite_prend_le_reste_phrase)
        # En mode, l'« Autre » couvre tout : pas d'avertissement.
        self.config.printer_ids = [(4, autre.id)]
        self.assertTrue(self.config._aite_actif())
        self.assertFalse(self.config.aite_familles_orphelines)

    def test_orphelines_familles_restreintes(self):
        """Relecture (code, 3) : une caisse aux familles restreintes ne cite
        que les familles qu'elle vend (et pas les produits sans famille,
        qu'elle ne charge pas)."""
        self.config.write({
            'limit_categories': True,
            'iface_available_categ_ids': [(6, 0, (self.plats | self.desserts).ids)]})
        texte = self.config.aite_familles_orphelines or ""
        self.assertIn("Desserts", texte)
        for absent in ("Pastas", "sans famille", "Pain maison"):
            self.assertNotIn(absent, texte)
        # Tout ce que la caisse vend est pris : pas d'avertissement.
        self.chaud.product_categories_ids = [(4, self.desserts.id)]
        self.assertFalse(self.config.aite_familles_orphelines)

    def test_phrase_grouper_dit_quand_sort_le_ticket(self):
        """Relecture (terrain, 1) : au service à table contrôlé, l'écran
        « Paiement réussi » est sauté ; le ticket final groupé ne sort au
        paiement que si « Impression automatique du reçu » est coché. La
        phrase du réglage le dit, et dit comment le réimprimer."""
        aide = self.env['pos.config']._fields['aite_grouper_familles'].help
        self.assertIn("Impression automatique du reçu", aide)
        self.assertIn("Commandes", aide)
        arch = self.env['res.config.settings'].get_view(
            self.env.ref('point_of_sale.res_config_settings_view_form').id, 'form')['arch']
        self.assertIn("Impression automatique du reçu", arch)
