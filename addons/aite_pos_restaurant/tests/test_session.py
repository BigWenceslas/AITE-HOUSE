# -*- coding: utf-8 -*-
"""Messages de la caisse sans courriel d'employé (spécification, T6, parties
4.2 et 6.2 ; incrément 1).

Les serveurs du client n'ont pas d'adresse électronique. ``pos_hr`` signe
l'ouverture de la caisse au nom de l'employé identifié, et la caisse signe
chaque mouvement d'espèces au nom de son contact : sans adresse,
``message_post`` lève « Unable to send message, please configure the sender's
email address. ». Pour une sortie d'espèces, l'erreur arrive **après**
l'enregistrement du mouvement : la fenêtre ne se ferme pas et une seconde
sortie est saisie. Chaque test commence par le témoin (une caisse hors mode,
où l'erreur se produit), puis vérifie la caisse au service à table contrôlé.
"""
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestSessionSansCourriel(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Témoin : même caisse de restaurant, sans la case.
        cls.temoin = cls.env['pos.config'].create({
            'name': "Bar témoin",
            'module_pos_restaurant': True,
            'module_pos_hr': True,
            'payment_method_ids': [(6, 0, cls.cash_pm1.copy({
                'name': "Espèces témoin",
                'journal_id': cls.env['account.journal'].create({
                    'name': "Caisse témoin", 'type': 'cash',
                    'code': 'CTEMO'}).id,
            }).ids)],
        })

    def _sortie_especes(self, session, employe):
        """Ce que fait la fenêtre « Entrée ou sortie d'espèces » de pos_hr :
        le mouvement, puis le message signé par le contact de l'employé."""
        caisse = session.with_user(self.compte_caisse)
        caisse.try_cash_in_out('out', 2000.0, "Glace pour le bar", {
            'translatedType': 'out', 'employee_id': employe.id})
        caisse.log_partner_message(
            employe.work_contact_id.id, "Sortie de 2 000 F", 'CASH_DRAWER_ACTION')

    def test_les_employes_n_ont_pas_de_courriel(self):
        self.assertFalse(self.equipe.work_contact_id.filtered('email'))

    def test_temoin_sortie_d_especes_en_erreur(self):
        session = self._ouvrir_session(self.temoin)
        with self.assertRaises(UserError):
            self._sortie_especes(session, self.paul)

    def test_sortie_d_especes_sans_courriel(self):
        session = self._ouvrir_session()
        self._sortie_especes(session, self.paul)
        mouvement = session.statement_line_ids
        self.assertEqual(len(mouvement), 1)
        self.assertEqual(mouvement.amount, -2000.0)
        self.assertEqual(mouvement.employee_id, self.paul)
        note = session.message_ids.filtered(
            lambda m: m.author_id == self.paul.work_contact_id)
        self.assertEqual(len(note), 1)
        self.assertIn("Tiroir-caisse ouvert (Sortie de 2 000 F)", note.body)

    def test_annulation_d_un_comptage_sans_courriel(self):
        session = self._ouvrir_session()
        session.with_user(self.compte_caisse).log_partner_message(
            self.carine.work_contact_id.id, "Comptage", 'ACTION_CANCELLED')
        note = session.message_ids.filtered(
            lambda m: m.author_id == self.carine.work_contact_id)
        self.assertIn("Action annulée (Comptage)", note.body)

    def test_message_sans_contact(self):
        """Un employé sans contact de travail : la note est signée par le
        compte de la caisse, sans erreur."""
        session = self._ouvrir_session()
        session.with_user(self.compte_caisse).log_partner_message(
            False, "Tiroir", 'CASH_DRAWER_ACTION')
        self.assertTrue(session.message_ids.filtered(
            lambda m: "Tiroir-caisse ouvert (Tiroir)" in (m.body or '')))

    def test_temoin_ouverture_en_erreur(self):
        self.temoin.open_ui()
        session = self.temoin.current_session_id
        session.employee_id = self.carine
        with self.assertRaises(UserError):
            session.with_user(self.compte_caisse).set_opening_control(0, None)

    def test_ouverture_sans_courriel(self):
        self.config.open_ui()
        session = self.config.current_session_id
        session.employee_id = self.carine
        self.assertIsNone(session._get_message_author())
        session.with_user(self.compte_caisse).set_opening_control(0, None)
        self.assertEqual(session.state, 'opened')

    def test_message_de_fermeture_sans_courriel(self):
        session = self._ouvrir_session()
        session.employee_id = self.paul
        session.with_user(self.compte_caisse).post_close_register_message()
        self.assertTrue(session.message_ids.filtered(
            lambda m: m.author_id == self.compte_caisse.partner_id))
