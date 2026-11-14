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

Incrément 3 : la table (``TestToursTable``) — personnes, numéro inconnu,
vente sans table, réunion ; et, depuis sa revue, l'addition quittée par un
onglet enregistrée au nom de qui l'a remplie (T19, ``AiteSaisieOngletTour``).
Les tours de l'incrément 2 vérifient aussi le journal des saisies.
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

    def _saisies(self, additions):
        """Le journal des saisies des additions : (produit, quantité, employé),
        dans l'ordre où le serveur l'a écrit."""
        saisies = self.env['aite.restaurant.saisie'].search(
            [('order_id', 'in', additions.ids)], order='id')
        return [(s.produit_nom, s.quantite, s.employe_nom) for s in saisies]


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursVerrou(AiteToursModeCommon):
    """Incrément 2 : le code et le plan verrouillé ; les gestes réservés."""

    def test_verrou(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteVerrouTour', login='pos_user')
        addition = self._addition_table_5()
        self.assertEqual(addition.state, 'draft')
        self.assertEqual(addition.lines.product_id.mapped('name'), ["Coca-Cola"])
        # L'envoi est enregistré sur le serveur, au nom d'Awa : le journal
        # des saisies (incrément 3) et l'employé de l'addition.
        self.assertIn(addition.lines.uuid, addition.last_order_preparation_change)
        self.assertEqual(addition.employee_id, self.employes["Awa"])
        self.assertEqual(self._saisies(addition), [("Coca-Cola", 1.0, "Awa")])
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
        # REST-02 critère 1 : « encaissée par » est la caissière identifiée à
        # la validation, « ouverte par » reste la serveuse (incrément 3).
        self.assertEqual(addition.employee_id, self.employes["Carine"])
        self.assertEqual(addition.aite_encaissee_par_id, self.employes["Carine"])
        self.assertEqual(addition.aite_ouverte_par_id, self.employes["Awa"])
        self.assertEqual(self._saisies(addition), [("Coca-Cola", 1.0, "Awa")])

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
        # T19 : le Coca-Cola d'Awa est enregistré à son nom avant que Fanta
        # tape son code sur « J'encaisse ».
        self.assertEqual(self._saisies(self._addition_table_5()), [("Coca-Cola", 1.0, "Awa")])

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


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursTable(AiteToursModeCommon):
    """Incrément 3 : la table — personnes, qui a ouvert, saisi ; numéro
    inconnu, vente sans table (PROF-04-P1)."""

    def _additions(self, domaine):
        return self.env['pos.order'].search(
            [('config_id', '=', self.pos_config.id)] + domaine, order='id')

    def test_personnes(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePersonnesTour', login='pos_user')
        awa = self.employes["Awa"]

        def table(numero, etat='draft'):
            return self._additions([('table_id.table_number', '=', numero),
                                    ('state', '=', etat)])

        # Table 5 : ouverte à 4, passée à 6, divisée ; l'origine garde 6 personnes.
        table_5 = table(5)
        self.assertEqual(len(table_5), 1)
        self.assertEqual(table_5.customer_count, 6)
        self.assertEqual(table_5.aite_ouverte_par_id, awa)
        self.assertTrue(table_5.aite_heure_ouverture)
        self.assertEqual(table_5.lines.product_id.mapped('name'), ["Water"])
        # La part « 5B » : 0 personne, l'origine, son heure et « ouverte par ».
        part = self._additions([('aite_origine_uuid', '=', table_5.uuid)])
        self.assertEqual(len(part), 1)
        self.assertEqual(part.floating_order_name, "5B")
        self.assertEqual(part.customer_count, 0)
        self.assertEqual(part.aite_heure_ouverture, table_5.aite_heure_ouverture)
        self.assertEqual(part.aite_ouverte_par_id, awa)
        self.assertEqual(part.lines.product_id.mapped('name'), ["Coca-Cola"])
        self.assertEqual(part.lines.qty, 2)
        # Réunion 3 + 4 : la table 2 a 7 personnes et l'heure de la table la
        # plus ancienne (la table 4, ouverte avant elle).
        table_2 = table(2)
        table_4 = table(4, 'cancel')
        self.assertEqual(table_2.customer_count, 7)
        self.assertEqual(len(table_4), 1)
        self.assertEqual(table_2.aite_heure_ouverture, table_4.aite_heure_ouverture)
        self.assertEqual(sorted(table_2.lines.product_id.mapped('name')), ["Coca-Cola", "Water"])
        # Journal des saisies : ce qu'Awa a ajouté, une fois ; ni la division
        # ni la réunion ne sont des saisies.
        saisies = self.env['aite.restaurant.saisie'].search(
            [('config_id', '=', self.pos_config.id)])
        self.assertEqual(saisies.employe_id, awa)
        self.assertEqual(sum(saisies.mapped('quantite')), 5)
        self.assertFalse(saisies.filtered(lambda s: s.order_id == part))
        self.assertEqual(saisies.filtered(lambda s: s.order_id == table_2).mapped(
            'produit_nom'), ["Coca-Cola"])

    def test_vente_sans_table_decochee(self):
        self.assertFalse(self.pos_config.aite_vente_sans_table)
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteVenteSansTableTour', login='pos_user')
        numero = self._additions([('floating_order_name', '=', "99")])
        self.assertEqual(len(numero), 1)
        self.assertEqual(numero.state, 'draft')
        self.assertFalse(numero.table_id)
        self.assertEqual(numero.customer_count, 2)
        self.assertEqual(numero.aite_ouverte_par_id, self.employes["Awa"])
        self.assertTrue(numero.aite_heure_ouverture)
        self.assertFalse(self._additions([('floating_order_name', '=', "98")]))

    def test_vente_sans_table_cochee(self):
        self.pos_config.aite_vente_sans_table = True
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteVenteSansTableCocheeTour', login='pos_user')
        vente = self._additions([('table_id', '=', False)])
        self.assertEqual(len(vente), 1)
        self.assertEqual(vente.customer_count, 0)
        self.assertEqual(vente.aite_ouverte_par_id, self.employes["Carine"])
        self.assertEqual(vente.lines.product_id.mapped('name'), ["Coca-Cola"])

    def test_reunion(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteReunionTour', login='pos_user')

        def table(numero):
            return self._additions([('table_id.table_number', '=', numero),
                                    ('state', '=', 'draft')])

        # R19 : rien n'a été réuni à la table de Carine.
        table_2 = table(2)
        self.assertEqual(table_2.aite_ouverte_par_id, self.employes["Carine"])
        self.assertEqual(table_2.customer_count, 2)
        self.assertEqual(table_2.lines.product_id.mapped('name'), ["Coca-Cola"])
        table_5 = table(5)
        self.assertEqual(table_5.customer_count, 4)
        self.assertEqual(table_5.lines.product_id.mapped('name'), ["Coca-Cola"])
        # La part « 5B » portée sur la table 4 : 2 personnes, son origine,
        # l'heure de la table 5 ; jamais enregistrée à table à 0 personne.
        part = table(4)
        self.assertEqual(part.aite_origine_uuid, table_5.uuid)
        self.assertEqual(part.customer_count, 2)
        self.assertEqual(part.aite_heure_ouverture, table_5.aite_heure_ouverture)
        self.assertEqual(part.lines.product_id.mapped('name'), ["Water"])
        self.assertFalse(part.message_ids.filtered(lambda m: "0 personne" in (m.body or '')))
        self.assertFalse(self.env['aite.restaurant.saisie'].search_count(
            [('order_id', '=', part.id)]))

    def test_saisie_quittee_par_un_onglet(self):
        """T19 (revue de l'incrément 3, constat bloquant n° 2) : l'addition
        quittée par un onglet est enregistrée au nom de qui l'a remplie, et
        rien ne passe au nom de Carine quand elle touche « Table »."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteSaisieOngletTour', login='pos_user')
        table_5 = self._addition_table_5()
        self.assertEqual(sorted(table_5.lines.product_id.mapped('name')), ["Coca-Cola", "Water"])
        self.assertEqual(self._saisies(table_5), [("Coca-Cola", 1.0, "Awa"), ("Water", 1.0, "Paul")])
        self.assertFalse(self.env['aite.restaurant.saisie'].search_count(
            [('config_id', '=', self.pos_config.id), ('employe_nom', '=', "Carine")]))


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursAnnulation(AiteToursModeCommon):
    """Incrément 4 : verrou après envoi, code d'un responsable, motifs,
    journal des annulations (AiteAnnulationTour, AiteAnnulerTableTour,
    AiteDeplacementTour, AiteFermetureTour). Moussa (2222, serveur) tape son
    code dans la fenêtre d'annulation : R8."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employes["Moussa"] = cls.env['hr.employee'].create({
            'name': "Moussa", 'pin': '2222', 'aite_niveau_caisse': 'serveur',
            'company_id': cls.env.company.id})

    def _journal(self, domaine=None):
        return self.env['aite.restaurant.annulation'].search(
            [('config_id', '=', self.pos_config.id)] + (domaine or []), order='id')

    def _table(self, numero, etat=None):
        domaine = [('config_id', '=', self.pos_config.id),
                   ('table_id.table_number', '=', numero)]
        if etat:
            domaine.append(('state', '=', etat))
        return self.env['pos.order'].search(domaine, order='id desc', limit=1)

    def test_annulation(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAnnulationTour', login='pos_user')
        addition = self._addition_table_5()
        self.assertEqual(addition.state, 'draft')
        ligne = addition.lines
        self.assertEqual(ligne.product_id.name, "Coca-Cola")
        self.assertEqual(ligne.qty, 1)
        self.assertEqual(ligne.aite_qte_envoyee, 1)
        trace = self._journal()
        self.assertEqual(len(trace), 1, trace.mapped('type_annulation'))
        self.assertEqual(trace.type_annulation, 'produit')
        self.assertTrue(trace.autorisee)
        self.assertEqual(trace.quantite, 2)
        self.assertEqual(trace.superieur_id, self.employes["Paul"])
        self.assertEqual(trace.serveur_id, self.employes["Awa"])
        self.assertEqual(trace.motif_id, self.env.ref('aite_pos_restaurant.motif_erreur_saisie'))
        self.assertEqual(trace.table_nom, "5")
        # La 4ᵉ, saisie puis retirée avant tout enregistrement : ni saisie ni
        # annulation (Q34).
        self.assertEqual(self._saisies(addition), [("Coca-Cola", 3.0, "Awa")])
        self.assertFalse(self._journal([('type_annulation', '=', 'retrait_sans_code')]))

    def test_annuler_la_table(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAnnulerTableTour', login='pos_user')
        table_5 = self._table(5)
        self.assertEqual(table_5.state, 'cancel')
        traces = self._journal([('order_id', '=', table_5.id)])
        self.assertEqual(sorted(traces.mapped('produit_nom')), ["Coca-Cola", "Water"])
        self.assertEqual(set(traces.mapped('type_annulation')), {'table'})
        self.assertEqual(set(traces.mapped('superieur_nom')), {"Paul"})
        self.assertEqual(set(traces.mapped('serveur_nom')), {"Awa"})
        self.assertEqual(set(traces.mapped('motif_nom')), {"Client parti"})
        table_4 = self._table(4)
        self.assertEqual(table_4.state, 'cancel')
        traces_4 = self._journal([('order_id', '=', table_4.id)])
        self.assertEqual(traces_4.mapped('produit_nom'), ["Coca-Cola"])
        self.assertEqual(traces_4.superieur_nom, "Paul")
        self.assertEqual(traces_4.serveur_nom, "Paul")
        self.assertFalse(self._journal([('type_annulation', '=', 'annulation_sans_code')]))

    def test_deplacement(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteDeplacementTour', login='pos_user')
        self.assertFalse(self._journal(), "ni la division ni la réunion ne sont des annulations")
        absorbee = self._table(5, 'cancel')
        self.assertTrue(absorbee)
        self.assertTrue(absorbee.aite_fusionnee)
        table_4 = self._table(4, 'draft')
        self.assertEqual(sum(table_4.lines.mapped('qty')), 3)
        self.assertEqual(sum(table_4.lines.mapped('aite_qte_envoyee')), 3)
        part = self.env['pos.order'].search([('config_id', '=', self.pos_config.id),
                                             ('floating_order_name', '=', "5B")])
        self.assertEqual(part.lines.product_id.mapped('name'), ["Water"])
        self.assertEqual(part.lines.aite_qte_envoyee, 1)
        # Les saisies : ce qu'Awa a ajouté, une fois.
        saisies = self.env['aite.restaurant.saisie'].search(
            [('config_id', '=', self.pos_config.id)])
        self.assertEqual(sum(saisies.mapped('quantite')), 4)

    def test_fermeture(self):
        session = self._ouvrir_la_caisse()
        self.start_pos_tour('AiteFermetureTour', login='pos_user')
        self.assertEqual(session.state, 'closed')
        self.assertEqual(session.aite_fermee_par_id, self.employes["Paul"])
        traces = self._journal([('session_id', '=', session.id)])
        self.assertEqual(len(traces), 2)
        self.assertEqual(set(traces.mapped('type_annulation')), {'fermeture'})
        self.assertEqual(sorted(traces.mapped('produit_nom')), ["Coca-Cola", "Water"])
        self.assertEqual(set(traces.mapped('superieur_nom')), {"Paul"})
        self.assertEqual(set(traces.order_id.mapped('state')), {'cancel'})

    def test_plus_moins(self):
        """Revue de l'incrément 4, constats 1 et 2 : « +/- » ne crée pas de
        ligne négative, et retire d'abord la part pas encore envoyée, comme
        ⌫ ; une annulation sur une ligne qui a encore une part pas envoyée ne
        la fait pas passer pour envoyée. La caisse et le serveur restent
        d'accord."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteMoinsTour', login='pos_user')
        addition = self._addition_table_5()
        self.assertEqual(addition.state, 'draft')
        self.assertEqual(addition.lines.product_id.mapped('name'), ["Coca-Cola"])
        ligne = addition.lines
        self.assertEqual((ligne.qty, ligne.aite_qte_envoyee, ligne.aite_qte_preparation),
                         (2, 2, 2))
        traces = self._journal()
        self.assertEqual(traces.mapped('type_annulation'), ['produit', 'produit'])
        self.assertEqual(traces.mapped('quantite'), [1, 1])
        self.assertEqual(set(traces.mapped('superieur_nom')), {"Paul"})
        self.assertEqual(set(traces.mapped('serveur_nom')), {"Awa"})

    def test_ardoise_sans_mode_ardoise(self):
        """AH-02 en mode : sans mode « ardoise » sur la caisse, pas de bouton,
        même pour le manager."""
        if 'is_aite_credit' not in self.env['pos.payment.method']._fields:
            self.skipTest("aite_pos_credit n'est pas installé")
        self.assertFalse(self.pos_config.payment_method_ids.filtered('is_aite_credit'))
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteArdoiseSansModeTour', login='pos_user')
