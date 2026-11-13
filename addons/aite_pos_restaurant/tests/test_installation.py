# -*- coding: utf-8 -*-
"""Une caisse prête au premier lancement ; une caisse existante jamais
modifiée ; la case qui ne se décoche pas en douce (spécification, parties
2.2, 4.3, 4.4 et 6.2 ; message R31)."""
from lxml import etree

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.aite_pos_restaurant.hooks import post_init_hook

from .common import RestaurantCommon

R31 = ("Décochez d'abord « Service à table contrôlé » : sans les codes "
       "personnels, la caisse ne saurait plus qui fait quoi.")


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestInstallation(RestaurantCommon):

    def _restaurant(self, company=None):
        return self.env['pos.config'].search([
            ('company_id', '=', (company or self.company).id),
            ('name', '=', "Restaurant"),
        ])

    def _photo(self):
        """Ce qu'un nouvel appel ne doit pas multiplier."""
        domaine = [('company_id', '=', self.company.id)]
        return {
            'caisses': self.env['pos.config'].search_count(domaine),
            'modes': self.env['pos.payment.method'].search_count(domaine),
            'journaux': self.env['account.journal'].search_count(domaine),
            'salles': self.env['restaurant.floor'].search_count(
                [('pos_config_ids.company_id', '=', self.company.id)]),
        }

    # ------------------------------------------------------------------
    # La caisse « Restaurant » posée d'office
    # ------------------------------------------------------------------

    def test_caisse_restaurant_creee_avec_le_plan_comptable(self):
        """La société de test reçoit son plan comptable en début de test :
        la caisse est créée juste après, comme sur une base neuve."""
        restaurant = self._restaurant()
        self.assertEqual(len(restaurant), 1)
        self.assertTrue(restaurant.aite_mode_restaurant)
        self.assertTrue(restaurant._aite_actif())
        self.assertTrue(restaurant.module_pos_restaurant)
        self.assertTrue(restaurant.module_pos_hr)

    def test_reglages_poses_d_office(self):
        restaurant = self._restaurant()
        self.assertTrue(restaurant.restrict_price_control)
        self.assertFalse(restaurant.manual_discount)
        self.assertFalse(restaurant.module_pos_discount)
        self.assertTrue(restaurant.iface_splitbill)
        self.assertTrue(restaurant.iface_printbill)
        self.assertFalse(restaurant.order_edit_tracking)
        self.assertFalse(restaurant.iface_print_skip_screen)

    def test_especes_et_mobile_money_seuls(self):
        modes = self._restaurant().payment_method_ids
        self.assertEqual(sorted(modes.mapped('name')), ["Espèces", "Mobile Money"])
        especes = modes.filtered(lambda m: m.name == "Espèces")
        self.assertTrue(especes.is_cash_count)
        mobile = modes.filtered(lambda m: m.name == "Mobile Money")
        self.assertEqual(mobile.journal_id.type, 'bank')
        self.assertEqual(mobile.journal_id.name, "Mobile Money")
        self.assertFalse(modes.filtered('split_transactions'),
                         "pas de « Compte client » (Q56)")

    def test_la_salle_s_appelle_salle(self):
        self.assertEqual(self._restaurant().floor_ids.mapped('name'), ["Salle"])

    def test_rejouer_le_crochet_ne_cree_rien_de_plus(self):
        avant = self._photo()
        post_init_hook(self.env)
        self.env['pos.config']._aite_preparer_caisse(self.company)
        self.assertEqual(self._photo(), avant)
        self.assertEqual(len(self._restaurant()), 1)

    def test_une_nouvelle_societe_recoit_sa_caisse(self):
        """Une société créée ensuite (seconde adresse) : au premier
        chargement de son plan comptable, elle reçoit aussi sa caisse
        « Restaurant »."""
        autre = self._create_company(name="Second restaurant")
        self.assertTrue(autre.chart_template)
        restaurant = self._restaurant(autre)
        self.assertEqual(len(restaurant), 1)
        self.assertTrue(restaurant.aite_mode_restaurant)

    def test_recharger_le_plan_comptable_ne_cree_rien(self):
        """La caisse n'est posée qu'au premier chargement du plan comptable.
        Le manager a décoché la case partout (il arrête le mode) ; AITE
        recharge ensuite le plan comptable : aucune caisse, aucun journal,
        aucun mode de paiement n'apparaît (constat de revue n° 1)."""
        self._restaurant().aite_mode_restaurant = False
        self.config.aite_mode_restaurant = False
        avant = self._photo()
        self.env['account.chart.template'].try_loading(
            self.company.chart_template, company=self.company,
            install_demo=False, force_create=False)
        self.assertEqual(self._photo(), avant)
        self.assertEqual(len(self._restaurant()), 1)

    def test_une_caisse_existante_n_est_jamais_modifiee(self):
        """Société sans caisse au service à table contrôlé : le crochet
        crée « Restaurant » et laisse les autres caisses telles quelles."""
        self.config.aite_mode_restaurant = False
        self._restaurant().unlink()
        champs = ['module_pos_restaurant', 'module_pos_hr', 'aite_mode_restaurant',
                  'manual_discount', 'restrict_price_control', 'iface_print_skip_screen',
                  'payment_method_ids', 'name']
        existantes = self.config | self.other_currency_config
        avant = existantes.read(champs)
        post_init_hook(self.env)
        self.assertEqual(existantes.read(champs), avant)
        self.assertEqual(len(self._restaurant()), 1)
        self.assertTrue(self._restaurant().aite_mode_restaurant)

    def test_aucune_dependance_hoteliere(self):
        """AH-12 : le module s'installe sans le socle hôtelier."""
        module = self.env['ir.module.module'].search(
            [('name', '=', 'aite_pos_restaurant')])
        a_voir, vus = module, self.env['ir.module.module']
        while a_voir:
            vus |= a_voir
            a_voir = a_voir.dependencies_id.depend_id - vus
        self.assertFalse(vus.filtered(lambda m: m.name.startswith('aite_hotel')))

    # ------------------------------------------------------------------
    # La case « Service à table contrôlé »
    # ------------------------------------------------------------------

    def test_r31_employes_ne_se_decoche_pas(self):
        with self.assertRaises(ValidationError) as erreur:
            self.config.module_pos_hr = False
        self.assertEqual(erreur.exception.args[0], R31)

    def test_r31_restaurant_ne_se_decoche_pas(self):
        with self.assertRaises(ValidationError) as erreur:
            self.config.module_pos_restaurant = False
        self.assertEqual(erreur.exception.args[0], R31)

    def test_decocher_la_case_puis_les_employes(self):
        self.config.aite_mode_restaurant = False
        self.config.module_pos_hr = False
        self.assertFalse(self.config._aite_actif())

    def test_la_case_ne_change_pas_pendant_une_session(self):
        self._ouvrir_session()
        with self.assertRaises(UserError):
            self.config.aite_mode_restaurant = False
        self.assertTrue(self.config.aite_mode_restaurant)

    def test_la_vente_sans_table_ne_change_pas_pendant_une_session(self):
        """Revue de l'incrément 3, constat n° 11 : les postes gardent la
        valeur chargée à l'ouverture, le serveur juge les ventes sans table
        sur la valeur enregistrée ; la case se change donc caisse fermée,
        comme celle du mode."""
        self._ouvrir_session()
        with self.assertRaises(UserError):
            self.config.aite_vente_sans_table = True
        self.assertFalse(self.config.aite_vente_sans_table)
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        reglage = etree.fromstring(arch).xpath("//setting[@id='aite_vente_sans_table']")[0]
        self.assertEqual(reglage.xpath(".//field[@name='pos_aite_vente_sans_table']/@readonly"),
                         ['pos_has_active_session'])
        self.assertIn("Se change seulement caisse fermée.", reglage.get('help'))

    def test_listes_de_pos_hr_ignorees_mais_pas_videes(self):
        self.config.basic_employee_ids = [(6, 0, self.awa.ids)]
        donnees = self._charger_caisse()
        noms = {e['name'] for e in donnees['hr.employee']['data']}
        self.assertEqual(noms, {"Awa", "Moussa", "Carine", "Paul", "Fanta"})
        self.assertEqual(self.config.basic_employee_ids, self.awa)

    # ------------------------------------------------------------------
    # Les réglages : la case, son effet immédiat et sa phrase
    # ------------------------------------------------------------------

    def test_cocher_la_case_pose_les_reglages(self):
        """À l'écran, avant enregistrement : cocher la case règle d'office
        les cases de la partie 4.4 (onchange des réglages)."""
        caisse = self.env['pos.config'].create({
            'name': "Terrasse",
            'module_pos_restaurant': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces terrasse",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse terrasse", 'type': 'cash',
                    'code': 'CTERR'}).id,
            }).ids)],
            'iface_splitbill': False,
            'iface_printbill': False,
            'manual_discount': True,
            'restrict_price_control': False,
            'order_edit_tracking': True,
            'iface_print_skip_screen': True,
        })
        Reglages = self.env['res.config.settings']
        self.assertIn('pos_aite_mode_restaurant', Reglages._onchange_methods)
        reglages = Reglages.new({'pos_config_id': caisse.id})
        self.assertFalse(reglages.pos_aite_mode_restaurant)
        self.assertFalse(reglages.pos_module_pos_hr)
        reglages.pos_aite_mode_restaurant = True
        reglages._onchange_pos_aite_mode_restaurant()
        self.assertTrue(reglages.pos_module_pos_hr)
        self.assertTrue(reglages.pos_restrict_price_control)
        self.assertFalse(reglages.pos_manual_discount)
        self.assertFalse(reglages.pos_module_pos_discount)
        self.assertTrue(reglages.pos_iface_splitbill)
        self.assertTrue(reglages.pos_iface_printbill)
        self.assertFalse(reglages.pos_order_edit_tracking)
        self.assertFalse(reglages.pos_iface_print_skip_screen)
        # Rien n'est écrit tant que le manager n'enregistre pas.
        self.assertFalse(caisse.aite_mode_restaurant)
        self.assertTrue(caisse.manual_discount)

    def test_decocher_la_case_ne_change_rien_d_autre(self):
        reglages = self.env['res.config.settings'].new({'pos_config_id': self.config.id})
        reglages.pos_aite_mode_restaurant = False
        reglages._onchange_pos_aite_mode_restaurant()
        self.assertTrue(reglages.pos_module_pos_hr)

    def test_la_phrase_dit_ce_qui_va_se_passer(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        vue = etree.fromstring(arch)
        reglage = vue.xpath("//setting[@id='aite_mode_restaurant']")
        self.assertEqual(len(reglage), 1)
        self.assertIn("Coché : chaque employé tape son code à 4 chiffres",
                      reglage[0].get('help'))
        self.assertIn("Se change seulement caisse fermée.", reglage[0].get('help'))
        self.assertEqual(reglage[0].xpath(".//field/@name"),
                         ['pos_aite_mode_restaurant'])

    def test_la_case_suit_est_un_bar_restaurant(self):
        """La phrase dit « ci-dessous » : la case vient juste après « Est un
        bar/restaurant », et tout ce qu'elle cite (connexion par code,
        contrôle des prix, remises, partage et impression de l'addition)
        est plus bas sur la page (constat de revue n° 6)."""
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        vue = etree.fromstring(arch)
        bloc = vue.xpath("//block[@id='restaurant_section']")[0]
        reglages = bloc.xpath("./setting")
        restaurant = [i for i, r in enumerate(reglages)
                      if r.xpath("./field[@name='pos_module_pos_restaurant']")]
        self.assertEqual(len(restaurant), 1)
        self.assertEqual(reglages[restaurant[0] + 1].get('id'), 'aite_mode_restaurant')
        ordre = {element: rang for rang, element in enumerate(vue.iter())}
        case = vue.xpath("//setting[@id='aite_mode_restaurant']")[0]
        for champ in ('pos_module_pos_hr', 'pos_restrict_price_control',
                      'pos_manual_discount', 'pos_module_pos_discount',
                      'pos_iface_splitbill', 'pos_iface_printbill'):
            with self.subTest(champ=champ):
                element = vue.xpath("//field[@name='%s']" % champ)[0]
                self.assertGreater(ordre[element], ordre[case])

    def test_la_case_reste_visible_tant_qu_elle_est_cochee(self):
        """Décocher « Est un bar/restaurant » ne masque pas la case encore
        cochée : R31 demande de la décocher d'abord, elle doit rester à
        l'écran (constat de revue n° 3). Une fois décochée, elle disparaît
        avec le restaurant."""
        # La société de test des tests du Point de Vente a des taxes « sur
        # les encaissements » sans le réglage comptable correspondant :
        # l'onchange comptable d'Odoo l'écrit en avertissement à l'ouverture
        # de la page. Sans rapport avec ce test ; on ne l'écrit pas au journal.
        with mute_logger('odoo.tests.form.onchange'):
            reglages = Form(self.env['res.config.settings'])
        reglages.pos_config_id = self.config
        self.assertTrue(reglages.pos_aite_mode_restaurant)
        reglages.pos_module_pos_restaurant = False
        reglages.pos_aite_mode_restaurant = False  # visible : modifiable
        with self.assertRaises(AssertionError):
            reglages.pos_aite_mode_restaurant = True  # masquée de nouveau

    def test_listes_et_previsualisation_masquees_en_mode(self):
        """La caisse en mode ignore les listes « droits de base / avancés » et
        l'option « Ignorer l'écran de prévisualisation » : elles sont
        masquées dans les réglages (partie 4.3)."""
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        vue = etree.fromstring(arch)
        for champ in ('pos_basic_employee_ids', 'pos_advanced_employee_ids',
                      'pos_iface_print_skip_screen'):
            with self.subTest(champ=champ):
                parent = vue.xpath("//field[@name='%s']/.." % champ)[0]
                self.assertEqual(parent.get('invisible'), 'pos_aite_mode_restaurant')
