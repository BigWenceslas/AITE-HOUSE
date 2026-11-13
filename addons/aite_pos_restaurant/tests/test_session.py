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
            lambda m: m.author_id == self.carine.work_contact_id
            and "Action annulée" in (m.body or ''))
        self.assertEqual(len(note), 1)
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
        caisse = session.with_user(self.compte_caisse)
        caisse.aite_ouvrir_caisse('3333')  # incrément 2 : le code d'abord
        caisse.set_opening_control(0, None)
        self.assertEqual(session.state, 'opened')

    def test_message_de_fermeture_sans_courriel(self):
        session = self._ouvrir_session()
        session.employee_id = self.paul
        session.with_user(self.compte_caisse).post_close_register_message()
        self.assertTrue(session.message_ids.filtered(
            lambda m: m.author_id == self.compte_caisse.partner_id))


# ----------------------------------------------------------------------
# Incrément 2 : ouverture et fermeture par code vérifié par le serveur,
# espèces réservées (spécification T8, parties 4.2 et 6.2)
# ----------------------------------------------------------------------

R1 = "Code inconnu. Retapez votre code."
R3 = ("La caisse n'est pas encore ouverte. La caissière ou un chef de salle "
      "doit l'ouvrir avec son code.")
R13 = "Seul un chef de salle ou le manager ferme la caisse."
R15 = "Seul un chef de salle ou le manager peut sortir ou entrer des espèces."


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestOuvertureFermeture(RestaurantCommon):
    """La caisse ne lit jamais ``pos.session.employee_id`` comme preuve :
    chaque poste le réécrit à chaque code tapé. L'ouverture et la fermeture
    passent par deux requêtes à code, et les gardes serveur refusent tout
    autre chemin, avant que la session change d'état."""

    def _session_en_controle(self):
        self.config.open_ui()
        session = self.config.current_session_id
        self.assertEqual(session.state, 'opening_control')
        return session, session.with_user(self.compte_caisse)

    def _refus(self, fonction, *args):
        with self.assertRaises(UserError) as erreur:
            fonction(*args)
        return erreur.exception.args[0]

    # --- Ouverture ---------------------------------------------------

    def test_un_serveur_n_ouvre_pas_la_caisse(self):
        session, caisse = self._session_en_controle()
        # Le refus est rendu à la caisse, qui l'affiche (pas d'erreur levée).
        self.assertEqual(caisse.aite_ouvrir_caisse('1111'), {'erreur': R3})
        self.assertFalse(session.aite_ouverte_par_id)
        self.assertEqual(session.state, 'opening_control')

    def test_code_inconnu_a_l_ouverture(self):
        _session, caisse = self._session_en_controle()
        self.assertEqual(caisse.aite_ouvrir_caisse('9999'), {'erreur': R1})
        self.assertEqual(caisse.aite_ouvrir_caisse(False), {'erreur': R1})

    def test_un_employe_archive_n_ouvre_pas(self):
        _session, caisse = self._session_en_controle()
        self.carine.active = False
        self.assertEqual(caisse.aite_ouvrir_caisse('3333'), {'erreur': R1})

    def test_la_caissiere_ouvre_la_caisse(self):
        session, caisse = self._session_en_controle()
        reponse = caisse.aite_ouvrir_caisse('3333')
        self.assertEqual(reponse, {'id': self.carine.id, 'name': "Carine"})
        caisse.set_opening_control(0, None)
        self.assertEqual(session.state, 'opened')
        self.assertEqual(session.aite_ouverte_par_id, self.carine)
        note = session.message_ids.filtered(
            lambda m: "Caisse ouverte par Carine" in (m.body or ''))
        self.assertEqual(len(note), 1)
        self.assertEqual(note.author_id, self.carine.work_contact_id)

    def test_le_chef_de_salle_et_le_manager_ouvrent_aussi(self):
        """Le dernier code accepté avant le contrôle d'ouverture est celui
        qui ouvre la caisse."""
        session, caisse = self._session_en_controle()
        self.assertEqual(caisse.aite_ouvrir_caisse('4444')['id'], self.paul.id)
        self.assertEqual(caisse.aite_ouvrir_caisse('5555')['id'], self.fanta.id)
        caisse.set_opening_control(0, None)
        self.assertEqual(session.aite_ouverte_par_id, self.fanta)

    def test_ouvrir_sans_code_est_refuse(self):
        """Le contrôle d'ouverture d'Odoo appelé sans notre requête (copie
        de poste ancienne, requête forgée) : refus R3, session inchangée."""
        session, caisse = self._session_en_controle()
        self.assertEqual(self._refus(caisse.set_opening_control, 0, None), R3)
        self.assertEqual(session.state, 'opening_control')

    def test_deux_postes_a_l_ouverture(self):
        """Le second poste tape un code alors que le premier a déjà ouvert :
        rien ne change, la caisse reste ouverte par Carine ; le poste
        apprend que la caisse est déjà ouverte."""
        session, caisse = self._session_en_controle()
        caisse.aite_ouvrir_caisse('3333')
        caisse.set_opening_control(0, None)
        self.assertEqual(caisse.aite_ouvrir_caisse('5555'), {'deja_ouverte': True})
        self.assertEqual(session.aite_ouverte_par_id, self.carine)
        self.assertEqual(session.state, 'opened')

    def test_la_caisse_ne_peut_pas_ecrire_qui_a_ouvert(self):
        """Champs écrits par le serveur seul : une écriture directe par le
        compte de la caisse est ignorée."""
        session, caisse = self._session_en_controle()
        caisse.write({'aite_ouverte_par_id': self.awa.id,
                      'aite_fermee_par_id': self.awa.id,
                      'aite_autorisation_id': self.carine.id})
        self.assertFalse(session.aite_ouverte_par_id)
        self.assertFalse(session.aite_fermee_par_id)
        self.assertFalse(session.aite_autorisation_id)
        self.assertEqual(self._refus(caisse.set_opening_control, 0, None), R3)

    def test_hors_mode_l_ouverture_ne_change_pas(self):
        temoin = self.env['pos.config'].create({
            'name': "Boutique témoin",
            'module_pos_hr': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces boutique",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse boutique", 'type': 'cash',
                    'code': 'CBTQ'}).id,
            }).ids)],
        })
        temoin.open_ui()
        session = temoin.current_session_id
        session.with_user(self.compte_caisse).set_opening_control(0, None)
        self.assertEqual(session.state, 'opened')
        session.with_user(self.compte_caisse).try_cash_in_out(
            'out', 500.0, "Monnaie", {'translatedType': 'out', 'employee_id': self.awa.id})
        self.assertEqual(len(session.statement_line_ids), 1)

    # --- Espèces -----------------------------------------------------

    def _sortie(self, session, employe_id):
        session.with_user(self.compte_caisse).try_cash_in_out(
            'out', 1000.0, "Glace", {'translatedType': 'out', 'employee_id': employe_id})

    def test_un_serveur_ou_la_caissiere_ne_sortent_pas_d_especes(self):
        session = self._ouvrir_session()
        for employe in (self.awa, self.carine):
            with self.subTest(employe=employe.name):
                self.assertEqual(self._refus(self._sortie, session, employe.id), R15)
        self.assertEqual(self._refus(self._sortie, session, False), R15)
        self.assertFalse(session.statement_line_ids)

    def test_le_chef_de_salle_sort_des_especes(self):
        session = self._ouvrir_session()
        self._sortie(session, self.paul.id)
        self._sortie(session, self.fanta.id)
        self.assertEqual(len(session.statement_line_ids), 2)

    # --- Fermeture ---------------------------------------------------

    def test_la_caissiere_ne_ferme_pas(self):
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        caisse.aite_fermer_caisse('4444')
        self.assertEqual(session.aite_autorisation_id, self.paul)
        # Carine tape ensuite son code : refus, et l'autorisation de Paul
        # n'est plus valable. Le refus est rendu, pas levé : une erreur
        # annulerait la remise à vide.
        self.assertEqual(caisse.aite_fermer_caisse('3333'), {'erreur': R13})
        self.assertFalse(session.aite_autorisation_id)
        self.assertEqual(self._refus(caisse.post_closing_cash_details, 0), R13)
        self.assertEqual(caisse.aite_fermer_caisse('1111'), {'erreur': R13})
        caisse.aite_fermer_caisse('4444')
        self.assertEqual(caisse.aite_fermer_caisse('0000'), {'erreur': R1})
        self.assertFalse(session.aite_autorisation_id)
        self.assertFalse(session.aite_fermee_par_id)
        self.assertFalse(session.message_ids.filtered(
            lambda m: "Caisse fermée par Carine" in (m.body or '')))

    def test_fermer_sans_code_est_refuse_avant_le_changement_d_etat(self):
        """Sans notre requête, chaque étape de la fenêtre de fermeture
        d'Odoo est refusée, et la session reste ouverte (sinon elle
        resterait bloquée en « contrôle de fermeture »)."""
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        self.assertEqual(self._refus(caisse.post_closing_cash_details, 0), R13)
        self.assertEqual(session.state, 'opened')
        self.assertEqual(
            self._refus(caisse.update_closing_control_state_session, "fin"), R13)
        self.assertEqual(session.state, 'opened')
        self.assertEqual(self._refus(caisse.close_session_from_ui), R13)
        self.assertEqual(session.state, 'opened')

    def test_paul_ferme_alors_qu_un_autre_poste_a_ecrit_awa(self):
        """Deux postes : le poste de Paul tape son code, puis le poste
        d'Awa réécrit ``employee_id`` (pos_hr le fait à chaque code tapé).
        La fermeture reste celle de Paul : le champ partagé n'est pas lu."""
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        caisse.write({'employee_id': self.paul.id})  # poste de Paul
        reponse = caisse.aite_fermer_caisse('4444')
        self.assertEqual(reponse, {'id': self.paul.id, 'name': "Paul"})
        caisse.write({'employee_id': self.awa.id})   # poste d'Awa
        self.assertTrue(caisse.post_closing_cash_details(0)['successful'])
        caisse.update_closing_control_state_session("Fin du service")
        self.assertEqual(session.state, 'closing_control')
        self.assertTrue(caisse.close_session_from_ui()['successful'])
        self.assertEqual(session.state, 'closed')
        self.assertEqual(session.aite_fermee_par_id, self.paul)
        self.assertTrue(session.message_ids.filtered(
            lambda m: "Caisse fermée par Paul" in (m.body or '')))

    def test_la_fermeture_depuis_la_gestion_n_est_pas_controlee(self):
        """Fermée par un compte Odoo depuis la gestion : aucun code."""
        session = self._ouvrir_session()
        session.action_pos_session_closing_control()
        self.assertEqual(session.state, 'closed')

    def test_le_code_tape_n_ecrit_pas_l_historique(self):
        """``employee_id`` sans suivi : chaque code tapé sur un poste
        n'ajoute pas une ligne à l'historique de la session."""
        session = self._ouvrir_session()
        avant = len(session.message_ids)
        for employe in (self.awa, self.paul, self.carine):
            session.with_user(self.compte_caisse).write({'employee_id': employe.id})
        # Le suivi d'Odoo écrit ses lignes au moment de valider la transaction.
        self.env.flush_all()
        self.env.cr.precommit.run()
        session.invalidate_recordset(['message_ids'])
        self.assertEqual(len(session.message_ids), avant)


# ----------------------------------------------------------------------
# Correctifs de la revue de l'incrément 2 (chaque test reproduit un défaut
# trouvé par la revue, écrit avant sa correction)
# ----------------------------------------------------------------------


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestCorrectifsSession(RestaurantCommon):
    """« Ouverte par » et « fermée par » ne sont écrits qu'à l'ouverture et
    à la fermeture effectives ; le code tapé n'est qu'une autorisation, que
    l'abandon de la fenêtre efface. Un poste en retard n'est pas refusé
    quand la caisse est déjà ouverte. Les requêtes que le compte de la
    caisse pourrait forger ne contournent pas les gardes."""

    def _session_en_controle(self):
        self.config.open_ui()
        session = self.config.current_session_id
        return session, session.with_user(self.compte_caisse)

    def _refus(self, fonction, *args, **kwargs):
        with self.assertRaises(UserError) as erreur:
            fonction(*args, **kwargs)
        return erreur.exception.args[0]

    def _notes(self, session, texte):
        session.invalidate_recordset(['message_ids'])
        return session.message_ids.filtered(lambda m: texte in (m.body or ''))

    # --- Deux postes à l'ouverture (revue, constat 6) -----------------

    def test_poste_en_retard_caisse_deja_ouverte(self):
        """La caisse est ouverte par un autre poste ; Awa (serveuse) tape
        son code sur un poste qui la croit fermée : pas de R3, le poste
        apprend qu'elle est ouverte. Aucun nom n'est rendu, même pour un
        code inconnu (le serveur ne révèle pas à qui est un code)."""
        session, caisse = self._session_en_controle()
        caisse.aite_ouvrir_caisse('3333')
        caisse.set_opening_control(0, None)
        for code in ('1111', '4444', '9999', False):
            with self.subTest(code=code):
                self.assertEqual(caisse.aite_ouvrir_caisse(code), {'deja_ouverte': True})
        self.assertEqual(session.aite_ouverte_par_id, self.carine)
        self.assertEqual(len(self._notes(session, "Caisse ouverte par")), 1)

    # --- Ouverte par, fermée par : au moment effectif (constat 7) -----

    def test_le_code_seul_n_ecrit_pas_ouverte_par(self):
        session, caisse = self._session_en_controle()
        caisse.aite_ouvrir_caisse('3333')
        self.assertFalse(session.aite_ouverte_par_id)
        self.assertFalse(self._notes(session, "Caisse ouverte par"))
        caisse.set_opening_control(0, None)
        self.assertEqual(session.aite_ouverte_par_id, self.carine)
        self.assertEqual(len(self._notes(session, "Caisse ouverte par Carine")), 1)
        self.assertFalse(session.aite_autorisation_id)

    def test_ouverture_abandonnee(self):
        """Le contrôle d'ouverture d'Odoo abandonné (« Retour ») :
        l'autorisation est effacée, l'ouverture redemande un code."""
        session, caisse = self._session_en_controle()
        caisse.aite_ouvrir_caisse('3333')
        caisse.aite_abandonner_code()
        self.assertFalse(session.aite_autorisation_id)
        self.assertEqual(self._refus(caisse.set_opening_control, 0, None), R3)
        self.assertEqual(session.state, 'opening_control')

    def test_le_code_seul_n_ecrit_pas_fermee_par(self):
        """Paul tape son code : la session, encore ouverte, n'est pas
        « fermée par Paul » ; elle l'est une fois fermée, avec une seule
        note, même si la fenêtre de fermeture a été rouverte."""
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        caisse.aite_fermer_caisse('4444')
        caisse.aite_fermer_caisse('4444')  # fenêtre rouverte (espèces)
        self.assertEqual(session.state, 'opened')
        self.assertFalse(session.aite_fermee_par_id)
        self.assertFalse(self._notes(session, "Caisse fermée par"))
        self.assertTrue(caisse.post_closing_cash_details(0)['successful'])
        caisse.update_closing_control_state_session("Fin du service")
        self.assertTrue(caisse.close_session_from_ui()['successful'])
        self.assertEqual(session.state, 'closed')
        self.assertEqual(session.aite_fermee_par_id, self.paul)
        self.assertEqual(len(self._notes(session, "Caisse fermée par Paul")), 1)
        self.assertFalse(session.aite_autorisation_id)

    def test_fermeture_abandonnee(self):
        """La fenêtre de fermeture abandonnée : plus tard, sans nouveau
        code, aucune étape de la fermeture ne passe."""
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        caisse.aite_fermer_caisse('4444')
        caisse.aite_abandonner_code()
        self.assertFalse(session.aite_autorisation_id)
        self.assertEqual(self._refus(caisse.post_closing_cash_details, 0), R13)
        self.assertEqual(
            self._refus(caisse.update_closing_control_state_session, "fin"), R13)
        self.assertEqual(self._refus(caisse.close_session_from_ui), R13)
        self.assertEqual(session.state, 'opened')
        self.assertFalse(session.aite_fermee_par_id)

    def test_abandon_sur_une_caisse_fermee_ne_change_rien(self):
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        caisse.aite_fermer_caisse('4444')
        caisse.post_closing_cash_details(0)
        caisse.update_closing_control_state_session("Fin")
        caisse.close_session_from_ui()
        caisse.aite_abandonner_code()
        self.assertEqual(session.aite_fermee_par_id, self.paul)

    # --- Requêtes forgées par le compte de la caisse (constat 10) ------

    def test_etat_ecrit_directement_sans_code(self):
        session, caisse = self._session_en_controle()
        self.assertEqual(self._refus(caisse.write, {'state': 'opened'}), R3)
        self.assertEqual(session.state, 'opening_control')

    def test_fermeture_par_l_action_de_la_gestion_sans_code(self):
        """Le compte de la caisse appelle l'action de fermeture de la
        gestion depuis une caisse ouverte, sans code : refus R13. Le
        manager, lui, ferme depuis la gestion sans code."""
        session = self._ouvrir_session()
        caisse = session.with_user(self.compte_caisse)
        self.assertEqual(self._refus(caisse.action_pos_session_closing_control), R13)
        self.assertEqual(session.state, 'opened')
        session.with_user(self.compte_manager).action_pos_session_closing_control()
        self.assertEqual(session.state, 'closed')

    def test_session_creee_sans_ouverture_ni_etat(self):
        """Une session créée par le compte de la caisse sur une caisse au
        service à table contrôlé commence toujours en contrôle d'ouverture,
        sans « ouverte par »."""
        autre = self.other_currency_config
        autre.write({'module_pos_restaurant': True, 'module_pos_hr': True,
                     'aite_mode_restaurant': True})
        session = self.env['pos.session'].with_user(self.compte_caisse).create({
            'config_id': autre.id,
            'user_id': self.compte_caisse.id,
            'state': 'opened',
            'aite_ouverte_par_id': self.awa.id,
            'aite_autorisation_id': self.awa.id,
        })
        self.assertEqual(session.state, 'opening_control')
        self.assertFalse(session.aite_ouverte_par_id)
        self.assertFalse(session.aite_autorisation_id)

    def test_un_chef_de_salle_archive_ne_sort_pas_d_especes(self):
        session = self._ouvrir_session()
        self.paul.active = False
        self.assertEqual(self._refus(
            session.with_user(self.compte_caisse).try_cash_in_out,
            'out', 1000.0, "Glace", {'translatedType': 'out', 'employee_id': self.paul.id}), R15)
        self.assertFalse(session.statement_line_ids)
