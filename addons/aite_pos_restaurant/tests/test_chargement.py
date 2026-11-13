# -*- coding: utf-8 -*-
"""Ce que la caisse reçoit au démarrage (spécification, parties 3.3, 4.2, 6.2).

Le compte de la caisse n'a aucun droit sur les Employés : le niveau, réservé
aux RH, est lu par le serveur en ``sudo()`` et injecté (T5). Ajouté à la
liste des champs, il lèverait une erreur d'accès et la caisse recevrait une
liste d'employés vide.
"""
from odoo.tests import tagged

from odoo.addons.aite_pos_restaurant.models import regles

from .common import RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestChargement(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sans_niveau = cls.env['hr.employee'].create({
            'name': "Comptable", 'pin': '9090', 'company_id': cls.company.id})
        cls.awa.barcode = 'AWA-0001'

    def _employes(self, donnees):
        return {e['name']: e for e in donnees['hr.employee']['data']}

    def test_le_compte_de_la_caisse_n_a_pas_les_droits_rh(self):
        self.assertFalse(self.compte_caisse.has_group('hr.group_hr_user'))

    def test_les_employes_a_niveau_arrivent_en_caisse(self):
        donnees = self._charger_caisse()
        self.assertNotIn('error', donnees['hr.employee'])
        employes = self._employes(donnees)
        self.assertEqual(set(employes),
                         {"Awa", "Moussa", "Carine", "Paul", "Fanta"})

    def test_niveau_role_et_badge(self):
        employes = self._employes(self._charger_caisse())
        attendu = {
            "Awa": ('serveur', 'cashier'),
            "Moussa": ('serveur', 'cashier'),
            "Carine": ('caissiere', 'cashier'),
            "Paul": ('superviseur', 'cashier'),
            "Fanta": ('manager', 'manager'),
        }
        for nom, (niveau, role) in attendu.items():
            with self.subTest(employe=nom):
                self.assertEqual(employes[nom]['_aite_niveau'], niveau)
                self.assertEqual(employes[nom]['_role'], role)
                self.assertIs(employes[nom]['_barcode'], False)
                self.assertTrue(employes[nom]['_pin'])
                self.assertNotIn('aite_niveau_caisse', employes[nom])

    def test_le_superviseur_ne_recoit_pas_les_droits_avances(self):
        """Mis dans « Employés avec accès avancé », Paul reste « cashier » :
        c'est son niveau qui décide, pas la liste de pos_hr."""
        self.config.advanced_employee_ids = [(4, self.paul.id)]
        employes = self._employes(self._charger_caisse())
        self.assertEqual(employes["Paul"]['_role'], 'cashier')

    def test_employe_sans_code_absent(self):
        """Un employé à niveau sans code (donnée ancienne, importée sans
        passer par la fiche) n'arrive pas en caisse."""
        self.env.cr.execute("UPDATE hr_employee SET pin = NULL WHERE id = %s",
                            [self.moussa.id])
        self.moussa.invalidate_recordset(['pin'])
        employes = self._employes(self._charger_caisse())
        self.assertNotIn("Moussa", employes)
        self.assertIn("Awa", employes)

    def test_le_tableau_des_droits_est_envoye(self):
        session = self._charger_caisse()['pos.session']['data'][0]
        self.assertEqual(session['_aite_droits'], regles.DROITS)
        self.assertEqual(session['_aite_niveaux'],
                         ['serveur', 'caissiere', 'superviseur', 'manager'])
        self.assertEqual(session['_aite_delai_retour_plan'],
                         regles.DELAI_RETOUR_PLAN)

    def test_une_caisse_hors_mode_n_est_pas_touchee(self):
        autre = self.env['pos.config'].create({
            'name': "Boutique",
            'module_pos_hr': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces boutique",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse boutique", 'type': 'cash',
                    'code': 'CBOUT'}).id,
            }).ids)],
        })
        self.assertFalse(autre.aite_mode_restaurant)
        donnees = self._charger_caisse(autre)
        employes = self._employes(donnees)
        self.assertIn("Comptable", employes)
        self.assertNotIn('_aite_niveau', employes["Awa"])
        self.assertTrue(employes["Awa"]['_barcode'], "le badge reste lu hors mode")
        self.assertNotIn('_aite_droits', donnees['pos.session']['data'][0])


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestModesReserves(RestaurantCommon):
    """AH-02 (incrément 2) : les modes « payer plus tard » sont réservés au
    manager en caisse. ``is_room_charge`` (note de chambre d'
    ``aite_hotel_pos_link``) n'étant pas chargé en caisse, c'est le serveur
    qui marque chaque mode (``_aite_reserve_manager``)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Methode = cls.env['pos.payment.method']
        cls.ardoise = Methode.create({'name': "Ardoise client", 'company_id': cls.company.id})
        cls.methodes = cls.ardoise
        cls.note_de_chambre = Methode
        if 'is_room_charge' in Methode._fields:
            cls.note_de_chambre = Methode.create({
                'name': "Note de chambre", 'is_room_charge': True,
                'company_id': cls.company.id})
            cls.methodes |= cls.note_de_chambre
        cls.config.payment_method_ids = [(4, m.id) for m in cls.methodes]

    def _modes(self, config=None):
        config = config or self.config
        config.open_ui()
        donnees = config.current_session_id.with_user(self.compte_caisse).load_data(
            ['pos.config', 'pos.payment.method'])
        return {m['id']: m for m in donnees['pos.payment.method']['data']}

    def test_l_ardoise_est_reservee_au_manager(self):
        self.assertEqual(self.ardoise.type, 'pay_later')
        modes = self._modes()
        self.assertIs(modes[self.ardoise.id]['_aite_reserve_manager'], True)

    def test_seuls_les_modes_payer_plus_tard_sont_reserves(self):
        """Espèces, banque : proposés à toute personne qui encaisse ; tout
        mode « payer plus tard » (ici aussi « Pay Later » de la caisse de
        test d'Odoo) : réservé, sauf la note de chambre."""
        modes = self._modes()
        reserves = self.config.payment_method_ids.filtered(
            lambda m: m.type == 'pay_later') - self.note_de_chambre
        self.assertIn(self.ardoise, reserves)
        self.assertTrue(self.config.payment_method_ids - reserves - self.note_de_chambre)
        for methode in self.config.payment_method_ids:
            with self.subTest(mode=methode.name):
                self.assertIs(modes[methode.id]['_aite_reserve_manager'],
                              methode in reserves)

    def test_la_note_de_chambre_reste_proposee(self):
        if not self.note_de_chambre:
            self.skipTest("aite_hotel_pos_link n'est pas installé")
        modes = self._modes()
        self.assertIs(modes[self.note_de_chambre.id]['_aite_reserve_manager'], False)

    def test_hors_mode_aucune_marque(self):
        self.config.aite_mode_restaurant = False
        modes = self._modes()
        self.assertNotIn('_aite_reserve_manager', modes[self.ardoise.id])
