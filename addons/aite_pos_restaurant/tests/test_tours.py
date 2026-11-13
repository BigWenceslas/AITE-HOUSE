# -*- coding: utf-8 -*-
"""Tours de la caisse (spécification, partie 6.3).

Incrément 1 : un tour de fumée. La caisse s'ouvre avec le module installé et
``PosStore.aiteActif`` suit la case « Service à table contrôlé ». Il prouve
aussi que les tours tournent sur ce poste (``websocket-client`` présent : sans
lui, un tour est ignoré, pas en échec).

Incrément 2 : le code et le plan verrouillé (``AiteVerrouTour``,
``AiteOuvertureTour``, ``AiteDroitsTour``, ``AitePaiementTour``) et l'ardoise
réservée au manager (``AiteArdoiseTour``, AH-02, si ``aite_pos_credit`` est
installé). Chaque tour est suivi de vérifications côté serveur.

Correctifs de la revue de l'incrément 2 (``TestToursCorrectifs``) : chaque
tour reproduit un défaut trouvé par la revue, écrit avant sa correction.
"""
from odoo.tests import tagged

from odoo.addons.pos_restaurant.tests.test_frontend import TestFrontendCommon

from odoo.addons.aite_pos_restaurant.models.pos_config import REGLAGES_DU_MODE


class AiteToursCommon(TestFrontendCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Pas d'imprimante de préparation : un bon non imprimé ouvrirait la
        # fenêtre « Printing failed ».
        cls.pos_config.write({'printer_ids': [(5, 0, 0)], 'is_order_printer': False})
        # Compte de la caisse comme le pose AITE : courriel et Facturation.
        cls.pos_user.partner_id.email = 'pos_user@test.com'
        cls.pos_user.groups_id += cls.env.ref('account.group_account_invoice')
        Employe = cls.env['hr.employee']
        cls.employes = {}
        for nom, code, niveau in (("Awa", '1111', 'serveur'),
                                  ("Carine", '3333', 'caissiere'),
                                  ("Paul", '4444', 'superviseur'),
                                  ("Fanta", '5555', 'manager')):
            cls.employes[nom] = Employe.create({
                'name': nom, 'pin': code, 'aite_niveau_caisse': niveau,
                'company_id': cls.env.company.id})


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestTours(AiteToursCommon):

    def test_mode_actif(self):
        self.pos_config.write({'module_pos_hr': True, 'aite_mode_restaurant': True})
        self.pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour('AiteModeActifTour', login='pos_user')

    def test_mode_inactif(self):
        """Une caisse de restaurant dont la case est décochée (T16)."""
        self.assertFalse(self.pos_config.aite_mode_restaurant)
        self.pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour('AiteModeInactifTour', login='pos_user')


class AiteToursModeCommon(AiteToursCommon):
    """La caisse au service à table contrôlé, réglée comme lorsqu'on coche la
    case (partie 4.4)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config.write({
            'module_pos_hr': True,
            **REGLAGES_DU_MODE,
            'aite_mode_restaurant': True,
        })

    def _ouvrir_la_caisse(self):
        """La caisse ouverte le matin par Carine (requête à code, puis le
        contrôle d'ouverture d'Odoo)."""
        self.pos_config.with_user(self.pos_user).open_ui()
        session = self.pos_config.current_session_id.with_user(self.pos_user)
        session.aite_ouvrir_caisse('3333')
        session.set_opening_control(0, None)
        return session

    def _addition_table_5(self):
        return self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id),
            ('table_id', '=', self.main_floor_table_5.id),
        ], order='id desc', limit=1)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursVerrou(AiteToursModeCommon):
    """Incrément 2 : le code et le plan verrouillé ; les gestes réservés."""

    def test_verrou(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteVerrouTour', login='pos_user')
        addition = self._addition_table_5()
        self.assertEqual(addition.state, 'draft')
        self.assertEqual(addition.lines.product_id.mapped('name'), ["Coca-Cola"])
        # L'envoi est enregistré sur le serveur, au nom d'Awa (le journal
        # des saisies arrive à l'incrément 3).
        self.assertIn(addition.lines.uuid, addition.last_order_preparation_change)
        self.assertEqual(addition.employee_id, self.employes["Awa"])
        # Le déplacement abandonné n'a rien porté sur la table 2.
        self.assertFalse(self.env['pos.order'].search_count([
            ('config_id', '=', self.pos_config.id),
            ('table_id.table_number', '=', 2),
            ('state', '!=', 'cancel')]))

    def test_ouverture(self):
        self.pos_config.with_user(self.pos_user).open_ui()
        session = self.pos_config.current_session_id
        self.assertEqual(session.state, 'opening_control')
        self.start_pos_tour('AiteOuvertureTour', login='pos_user')
        self.assertEqual(session.state, 'opened')
        self.assertEqual(session.aite_ouverte_par_id, self.employes["Carine"])

    def test_droits(self):
        session = self._ouvrir_la_caisse()
        self.start_pos_tour('AiteDroitsTour', login='pos_user')
        # La caissière a été refusée à la fermeture : la caisse reste ouverte.
        self.assertEqual(session.state, 'opened')
        self.assertFalse(session.aite_fermee_par_id)
        self.assertFalse(session.statement_line_ids)

    def test_paiement(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePaiementTour', login='pos_user')
        addition = self._addition_table_5()
        self.assertEqual(addition.state, 'paid')
        # « Encaissée par » : l'employé identifié à la validation (pos_hr) ;
        # les champs AITE « ouverte par » et « encaissée par » arrivent à
        # l'incrément 3.
        self.assertEqual(addition.employee_id, self.employes["Carine"])

    def test_ardoise_reservee_au_manager(self):
        """AH-02 : le bouton « Mettre sur ardoise » et le mode « Ardoise
        client » n'apparaissent que pour le manager."""
        Methode = self.env['pos.payment.method']
        if 'is_aite_credit' not in Methode._fields:
            self.skipTest("aite_pos_credit n'est pas installé")
        ardoise = Methode.create({
            'name': "Ardoise client", 'is_aite_credit': True,
            'split_transactions': True, 'company_id': self.env.company.id})
        self.pos_config.payment_method_ids = [(4, ardoise.id)]
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteArdoiseTour', login='pos_user')


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursCorrectifs(AiteToursModeCommon):
    """Revue de l'incrément 2 : prise en main sur l'écran de paiement,
    déplacement après un abandon, caisse pas encore ouverte, onglets, deux
    postes à l'ouverture, écart de caisse à la fermeture."""

    def test_prise_en_main_au_paiement(self):
        """Une serveuse qui reprend la main sur le paiement revient à
        l'écran de commande ; la caissière qui reprend la main au manager ne
        voit plus le mode « payer plus tard » réservé (AH-02)."""
        ardoise = self.env['pos.payment.method'].create({
            'name': "Ardoise AITE", 'company_id': self.env.company.id})
        self.assertEqual(ardoise.type, 'pay_later')
        self.pos_config.payment_method_ids = [(4, ardoise.id)]
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePriseEnMainTour', login='pos_user')
        # Rien n'a été encaissé, ni mis sur le mode réservé.
        self.assertFalse(self.env['pos.order'].search_count([
            ('config_id', '=', self.pos_config.id),
            ('state', 'in', ('paid', 'done', 'invoiced'))]))
        self.assertFalse(self.env['pos.payment'].search_count([
            ('payment_method_id', '=', ardoise.id)]))

    def test_deplacement_apres_un_abandon(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteTransfertApresAbandonTour', login='pos_user')
        table_2 = self.env['restaurant.table'].search([
            ('floor_id', 'in', self.pos_config.floor_ids.ids), ('table_number', '=', 2)])
        addition = self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id), ('table_id', '=', table_2.id),
            ('state', '=', 'draft')])
        self.assertEqual(addition.lines.product_id.mapped('name'), ["Coca-Cola"])

    def test_avant_l_ouverture(self):
        self.pos_config.with_user(self.pos_user).open_ui()
        session = self.pos_config.current_session_id
        self.start_pos_tour('AiteAvantOuvertureTour', login='pos_user')
        self.assertEqual(session.state, 'opening_control')
        self.assertFalse(self.env['pos.order'].search_count([
            ('config_id', '=', self.pos_config.id)]))

    def test_onglet_d_une_addition_sans_table(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteOngletTour', login='pos_user')

    def _poste_en_retard(self, tour):
        self.pos_config.with_user(self.pos_user).open_ui()
        session = self.pos_config.current_session_id
        self.start_pos_tour(tour, login='pos_user')
        self.assertEqual(session.state, 'opened')
        self.assertEqual(session.aite_ouverte_par_id, self.employes["Carine"])

    def test_poste_en_retard_code(self):
        self._poste_en_retard('AiteRetardCodeTour')

    def test_poste_en_retard_table(self):
        self._poste_en_retard('AiteRetardTableTour')

    def test_poste_en_retard_bandeau(self):
        self._poste_en_retard('AiteRetardBandeauTour')

    def test_fermeture_au_dela_de_l_ecart(self):
        self.pos_config.write({'set_maximum_difference': True, 'amount_authorized_diff': 1.0})
        session = self._ouvrir_la_caisse()
        self.start_pos_tour('AiteFermetureEcartTour', login='pos_user')
        self.assertEqual(session.state, 'opened')
        # La fenêtre abandonnée : personne n'a fermé la caisse.
        self.assertFalse(session.aite_fermee_par_id)
        self.assertFalse(session.message_ids.filtered(
            lambda m: "Caisse fermée par" in (m.body or '')))
