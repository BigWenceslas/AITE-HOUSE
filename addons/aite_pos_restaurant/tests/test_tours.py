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

Incrément 6 : un service complet de bout en bout (``TestToursParcours``,
``AiteParcoursTour``), qui mesure les touches de la partie 1.2.
"""
import json
from uuid import uuid4

from odoo import fields
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
@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursTableOuverte(AiteToursModeCommon):
    """Une table déjà ouverte ne redemande pas les personnes à une autre
    personne ni à un autre poste (constat du client)."""

    def test_table_deja_ouverte(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteTableOuverteTour', login='pos_user')
        additions = self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id), ('table_id.table_number', '=', 2),
            ('state', '=', 'draft')])
        self.assertEqual(len(additions), 1)
        self.assertEqual(additions.customer_count, 2)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursAdditionPart(AiteToursModeCommon):
    """L'addition d'une part divisée s'imprime (constat du client)."""

    def test_addition_d_une_part(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionPartTour', login='pos_user')

    def test_addition_de_toutes_les_parts(self):
        """« Addition » sur une table divisée montre et imprime toutes les
        additions encore ouvertes du groupe : l'origine, ses parts et la part
        d'une part ; une part payée n'y figure plus (constat du client,
        table 7B)."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionToutesLesPartsTour', login='pos_user')
        additions = self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id),
            ('floating_order_name', '=', '5BB')])
        self.assertEqual(additions.mapped('state'), ['paid'])

    def test_addition_sans_division(self):
        """Sans division, « Addition » garde l'aperçu d'Odoo, pour cette
        addition seule."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionSansDivisionTour', login='pos_user')

    def test_addition_d_une_part_deplacee(self):
        """Une part portée sur une table libre est l'addition de cette table :
        « Addition » sur chacune des deux tables ne montre que la sienne."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionPartDeplaceeTour', login='pos_user')

    def test_addition_apres_rechargement(self):
        """Une part intermédiaire payée (5B) : après un rechargement, 5BB
        reste avec la table 5 ; une imprimante en panne au second ticket ne
        fait reprendre que l'addition non imprimée."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionApresRechargementTour', login='pos_user')
        par_nom = {
            nom: self.env['pos.order'].search([
                ('config_id', '=', self.pos_config.id), ('floating_order_name', '=', nom)])
            for nom in ('5B', '5BB')}
        origine = self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id), ('table_id.table_number', '=', 5)])
        self.assertEqual(par_nom['5B'].state, 'paid')
        self.assertEqual(par_nom['5BB'].state, 'draft')
        self.assertEqual(par_nom['5BB'].aite_origine_uuid, par_nom['5B'].uuid)
        # La clé du groupe : l'addition divisée la première fois, la table 5.
        self.assertEqual(par_nom['5B'].aite_groupe_uuid, origine.uuid)
        self.assertEqual(par_nom['5BB'].aite_groupe_uuid, origine.uuid)


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


class AiteToursStockCommon(AiteToursModeCommon):
    """Les produits suivis en stock des tours de l'incrément 5 (sans test :
    une classe de tests n'hérite jamais d'une autre)."""

    def _produits(self):
        Produit = self.env['product.product']
        coca = Produit.search([('name', '=', "Coca-Cola")], limit=1)
        water = Produit.search([('name', '=', "Water")], limit=1)
        coca.write({'is_storable': True, 'barcode': '5449000000996'})
        self.assertFalse(water.is_storable)
        return coca, water

    def _entree(self, produit, quantite):
        """Le manager enregistre une entrée de stock (« Mettre la quantité à
        jour »), dans l'entrepôt de la caisse."""
        emplacement = self.pos_config.picking_type_id.warehouse_id.lot_stock_id
        quant = self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': produit.id, 'location_id': emplacement.id,
            'inventory_quantity': quantite})
        quant.action_apply_inventory()

    def _table(self, numero):
        return self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id),
            ('table_id.table_number', '=', numero)], order='id desc', limit=1)

    def _disponible(self, produit):
        return self.env['product.product'].with_user(self.pos_user).aite_stock_disponible(
            self.pos_config.id).get(produit.id)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursPlanStock(AiteToursStockCommon):
    """Incrément 5 : le plan en couleurs (REST-17 : AiteCouleursTour, joué
    avec un délai de 60 puis de 90 minutes) ; les produits épuisés (REST-19a :
    AiteEpuiseRefusTour, entrée de stock en Python, AiteEpuiseVenteTour)."""

    def _couleurs(self):
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteCouleursTour', login='pos_user')
        addition = self._addition_table_5()
        # REST-17 critère 3 : la table orange a été encaissée par Carine.
        self.assertEqual(addition.state, 'paid')
        self.assertTrue(addition.aite_heure_ouverture)
        self.assertEqual(addition.aite_encaissee_par_id, self.employes["Carine"])

    def test_couleurs(self):
        self.assertEqual(self.pos_config.aite_delai_alerte, 60)
        self._couleurs()

    def test_couleurs_delai_90(self):
        """REST-17 critère 4 : le délai porté à 90 minutes s'applique à
        l'ouverture suivante de la caisse."""
        self.pos_config.aite_delai_alerte = 90
        self._couleurs()

    def test_epuise(self):
        coca, water = self._produits()
        self.assertTrue(self.pos_config.aite_refus_epuise)
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpuiseRefusTour', login='pos_user')
        self.assertEqual(self._table(5).lines.product_id, water)
        # Entre les deux tours : une bouteille entre en stock.
        self._entree(coca, 1)
        self.start_pos_tour('AiteEpuiseVenteTour', login='pos_user')
        ligne = self._table(4).lines
        self.assertEqual(ligne.product_id, coca)
        self.assertEqual(ligne.qty, 1)
        self.assertEqual(ligne.aite_qte_envoyee, 1)
        self.assertEqual(self.env['product.product'].with_user(self.pos_user)
                         .aite_stock_disponible(self.pos_config.id)[coca.id], 0)

    def test_epuise_reglage_decoche(self):
        """« Refuser la vente des produits épuisés » décoché : un produit
        suivi se vend même à zéro."""
        coca, _water = self._produits()
        self.pos_config.aite_refus_epuise = False
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpuiseVenteTour', login='pos_user')
        self.assertEqual(self._table(4).lines.product_id, coca)
        self.assertEqual(self._table(4).lines.qty, 2)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursEpuiseCorrectifs(AiteToursStockCommon):
    """Revue de l'incrément 5 : chaque tour reproduit un constat, écrit avant
    sa correction. Le refus des produits épuisés est fait aux gestes qui
    ajoutent (toucher d'une carte, code-barres, pavé, fenêtre de
    configuration), jamais dans ``addLineToCurrentOrder`` que des boutons
    d'Odoo appellent pour scinder une ligne ; hors connexion, on vend (Q59)."""

    def test_pave(self):
        """Constat 1 : deux Coca-Cola en stock, « 5 » tapé au pavé est refusé,
        « 2 » passe."""
        coca, _water = self._produits()
        self._entree(coca, 2)
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpuisePaveTour', login='pos_user')
        ligne = self._table(5).lines
        self.assertEqual(ligne.product_id, coca)
        self.assertEqual(ligne.qty, 2)
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        self.assertEqual(self._disponible(coca), 0)

    def test_note_cuisine(self):
        """Constat 2 : la note cuisine sur une ligne en partie envoyée d'un
        produit au bout de son stock est posée, sans R11 ni erreur."""
        coca, _water = self._produits()
        self._entree(coca, 2)
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpuiseNoteTour', login='pos_user')
        lignes = self._table(5).lines
        self.assertEqual(lignes.product_id, coca)
        self.assertEqual(sum(lignes.mapped('qty')), 2)
        self.assertEqual(sorted(note or '' for note in lignes.mapped('note')),
                         ['', 'bien fraîche'])
        self.assertEqual(self._disponible(coca), 0)

    def test_variantes(self):
        """Constat 3 : « Jus » 33 cl à 0, 50 cl à 5 ; la variante choisie dans
        la fenêtre de configuration est contrôlée."""
        taille = self.env['product.attribute'].create({
            'name': "Taille", 'create_variant': 'always',
            'value_ids': [(0, 0, {'name': "33 cl"}), (0, 0, {'name': "50 cl"})]})
        modele = self.env['product.template'].create({
            'name': "Jus", 'available_in_pos': True, 'is_storable': True,
            'list_price': 900, 'taxes_id': [(6, 0, [])],
            'pos_categ_ids': [(4, self.env['pos.category'].search(
                [('name', '=', 'Drinks')], limit=1).id)],
            'attribute_line_ids': [(0, 0, {
                'attribute_id': taille.id, 'value_ids': [(6, 0, taille.value_ids.ids)]})]})
        jus_33, jus_50 = modele.product_variant_ids.sorted(
            lambda p: p.product_template_variant_value_ids.name)
        self.assertIn("33 cl", jus_33.display_name)
        self._entree(jus_50, 5)
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpuiseVarianteTour', login='pos_user')
        ligne = self._table(5).lines
        self.assertEqual(ligne.product_id, jus_50)
        self.assertEqual(ligne.qty, 1)
        self.assertEqual(self._disponible(jus_50), 4)
        self.assertEqual(self._disponible(jus_33), 0)

    def test_hors_connexion(self):
        """Constat 4 : hors connexion, ou relecture du stock en erreur, la
        caisse vend (Q59) ; ici les bouteilles sont retirées avant l'envoi."""
        coca, water = self._produits()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpuiseHorsConnexionTour', login='pos_user')
        self.assertEqual(self._table(5).lines.product_id, water)

    def test_duree_sur_l_ecran_de_commande(self):
        """Constat 7 : la durée de la phrase d'état suit la minuterie."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteDureeCommandeTour', login='pos_user')
        self.assertEqual(self._table(5).lines.product_id.name, "Water")


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursRapports(AiteToursModeCommon):
    """Incrément 6 : le rapport de fermeture imprimé depuis la caisse
    (« Imprimer le rapport », gabarit point_of_sale.SaleDetailsReport) porte
    les tables, les personnes, les ventes sans table et les annulations de la
    session (partie 5.3). Le tour rend le gabarit avec les données du serveur :
    il n'y a pas d'imprimante dans les tests."""

    def _synchroniser(self, session, table, personnes, produit, quantite, employe,
                      etat='draft', envoyer=True):
        """Une addition telle que la caisse l'envoie (sync_from_ui), sous le
        compte de la caisse."""
        maintenant = fields.Datetime.to_string(fields.Datetime.now())
        uuid_ligne = str(uuid4())
        total = produit.lst_price * quantite
        preparation = {'lines': {}, 'metadata': {}, 'generalNote': '', 'sittingMode': 'dine in'}
        if envoyer:
            preparation['lines'][uuid_ligne] = {
                'uuid': uuid_ligne, 'product_id': produit.id, 'name': produit.name,
                'note': '', 'quantity': quantite, 'attribute_value_ids': []}
        especes = self.pos_config.payment_method_ids.filtered('is_cash_count')[:1]
        donnees = {
            'uuid': str(uuid4()), 'name': "Commande %s" % uuid_ligne, 'session_id': session.id,
            'state': etat, 'user_id': self.pos_user.id,
            'pricelist_id': self.pos_config.pricelist_id.id, 'fiscal_position_id': False,
            'sequence_number': 1, 'to_invoice': False, 'date_order': maintenant,
            'amount_tax': 0.0, 'amount_total': total,
            'amount_paid': total if etat == 'paid' else 0.0, 'amount_return': 0.0,
            'last_order_preparation_change': json.dumps(preparation),
            'table_id': table.id, 'customer_count': personnes,
            'employee_id': employe.id, 'aite_ouverte_par_id': employe.id,
            'lines': [[0, 0, {
                'uuid': uuid_ligne, 'product_id': produit.id, 'qty': quantite,
                'price_unit': produit.lst_price, 'discount': 0.0, 'tax_ids': [(6, 0, [])],
                'price_subtotal': total, 'price_subtotal_incl': total,
                'full_product_name': produit.display_name}]],
            'payment_ids': [[0, 0, {'amount': total, 'name': maintenant,
                                    'payment_method_id': especes.id}]] if etat == 'paid' else [],
        }
        reponse = self.env['pos.order'].with_user(self.pos_user).with_context(
            config_id=self.pos_config.id, aite_employee_id=employe.id).sync_from_ui([donnees])
        return self.env['pos.order'].browse(reponse['pos.order'][0]['id']), uuid_ligne

    def test_rapport_de_fermeture_en_caisse(self):
        session = self._ouvrir_la_caisse()
        coca = self.env['product.product'].search([('name', '=', 'Coca-Cola')], limit=1)
        table_4 = self.env['restaurant.table'].search([
            ('floor_id.pos_config_ids', 'in', self.pos_config.ids), ('table_number', '=', 4)],
            limit=1)
        payee, _ligne = self._synchroniser(session, self.main_floor_table_5, 3, coca, 2,
                                           self.employes["Carine"], etat='paid')
        self.assertEqual((payee.state, payee.aite_tables, payee.aite_personnes), ('paid', 1, 3))
        ouverte, ligne = self._synchroniser(session, table_4, 2, coca, 1, self.employes["Awa"])
        reponse = self.env['pos.order'].with_user(self.pos_user).aite_autoriser_annulation(
            ouverte.ids, [{'uuid': ligne, 'quantite': 1}], '4444',
            self.env.ref('aite_pos_restaurant.motif_client_parti').id, False,
            self.employes["Awa"].id, str(uuid4()), 'produit')
        self.assertNotIn('erreur', reponse)
        self.start_pos_tour('AiteRapportFermetureTour', login='pos_user')


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursParcours(AiteToursStockCommon):
    """Incrément 6 : AiteParcoursTour (parties 1.2 et 6.3) — un service
    complet, de l'ouverture de la caisse à sa fermeture, puis le lendemain,
    réellement joué à l'écran ; chaque geste de la partie 1.2 compte ses
    touches (mesures écrites dans le journal du test). Ici, ce que le serveur
    a gardé du service."""

    def _additions(self, session, numero):
        return self.env['pos.order'].search([
            ('session_id', '=', session.id), ('table_id.table_number', '=', numero)],
            order='id')

    def test_parcours_complet(self):
        coca, water = self._produits()
        # Coca-Cola suivi en stock (10 bouteilles), Minute Maid suivi et
        # jamais rentré (épuisé), Water sans suivi ; des prix ronds.
        minute = self.env['product.product'].search([('name', '=', "Minute Maid")], limit=1)
        minute.is_storable = True
        coca.product_tmpl_id.list_price = 1000
        water.product_tmpl_id.list_price = 500
        self._entree(coca, 10)
        # La caisse est fermée : la caissière l'ouvre à l'écran.
        self.pos_config.with_user(self.pos_user).open_ui()
        session = self.pos_config.current_session_id
        self.assertEqual(session.state, 'opening_control')

        self.start_pos_tour('AiteParcoursTour', login='pos_user')

        employes = self.employes
        # L'ouverture et la fermeture, par code vérifié par le serveur ; les
        # espèces : 5 500 encaissées, 1 000 sorties.
        self.assertEqual(session.state, 'closed')
        self.assertEqual(session.aite_ouverte_par_id, employes["Carine"])
        self.assertEqual(session.aite_fermee_par_id, employes["Paul"])
        self.assertEqual(session.cash_register_balance_end_real, 4500)
        # Lignes d'espèces de la session : la sortie, puis, à la fermeture,
        # les encaissements en espèces.
        self.assertEqual(sorted(session.statement_line_ids.mapped('amount')), [-1000, 5500])
        # Six additions payées : la table 5 de bout en bout, la table 4
        # encaissée au poste d'Awa, la table 2 encaissée par Fanta (deux fois),
        # les deux parts de la table 4.
        payees = session.order_ids.filtered(lambda o: o.state in ('paid', 'done'))
        self.assertEqual(len(payees), 6, payees.mapped('name'))
        self.assertEqual(sum(payees.mapped('amount_total')), 5500)

        # La table 5 : ouverte par Awa, 6 personnes, encaissée par Carine.
        addition = self._additions(session, 5)[0]
        self.assertIn(addition.state, ('paid', 'done'))
        self.assertEqual(addition.aite_ouverte_par_id, employes["Awa"])
        self.assertEqual(addition.aite_encaissee_par_id, employes["Carine"])
        self.assertEqual(addition.customer_count, 6)
        self.assertEqual((addition.aite_tables, addition.aite_personnes), (1, 6))
        self.assertEqual(addition.amount_total, 1500)
        lignes = {l.product_id.name: l.qty for l in addition.lines}
        self.assertEqual(lignes, {"Coca-Cola": 1, "Water": 1})
        # Le produit épuisé n'a jamais été ajouté.
        self.assertFalse(self.env['pos.order.line'].search_count([('product_id', '=', minute.id)]))
        # Le journal des saisies : ce qu'Awa a ajouté et envoyé ; la Coca-Cola
        # saisie puis retirée avant tout enregistrement n'y est pas (Q34).
        saisies = {}
        for produit, quantite, employe in self._saisies(addition):
            self.assertEqual(employe, "Awa")
            saisies[produit] = saisies.get(produit, 0) + quantite
        self.assertEqual(saisies, {"Coca-Cola": 1, "Water": 2})

        # La table 4 : Paul seul a annulé le Water ; Carine a encaissé la
        # Coca-Cola au poste d'Awa ; puis deux parts encaissées par Carine ;
        # puis une table annulée par Paul seul.
        premiere, origine, annulee = self._additions(session, 4)
        # La part « 4B » n'a pas de table : elle garde son origine.
        part = self.env['pos.order'].search([('aite_origine_uuid', '=', origine.uuid)])
        self.assertIn(premiere.state, ('paid', 'done'))
        self.assertEqual(premiere.amount_total, 1000)
        self.assertEqual(premiere.aite_ouverte_par_id, employes["Awa"])
        self.assertEqual(premiere.aite_encaissee_par_id, employes["Carine"])
        self.assertEqual(sum(premiere.lines.filtered(
            lambda l: l.product_id == water).mapped('qty')), 0)
        self.assertFalse(origine.aite_origine_uuid)
        self.assertEqual((len(part), part.session_id), (1, session))
        self.assertEqual({(o.amount_total, o.aite_encaissee_par_id.name) for o in (origine, part)},
                         {(1000, "Carine"), (500, "Carine")})
        self.assertEqual(part.aite_ouverte_par_id, employes["Awa"])
        self.assertEqual(annulee.state, 'cancel')

        # La table 2 : ouverte par Awa, encaissée par Fanta (M1, « ouverte
        # par » figé) ; puis ouverte par Carine, reprise et encaissée par
        # Fanta ; le soir, annulée à la fermeture.
        table_2 = self._additions(session, 2)
        awa, carine, soir_2 = table_2
        self.assertEqual((awa.amount_total, awa.aite_ouverte_par_id, awa.aite_encaissee_par_id),
                         (1000, employes["Awa"], employes["Fanta"]))
        self.assertEqual(
            (carine.amount_total, carine.aite_ouverte_par_id, carine.aite_encaissee_par_id),
            (500, employes["Carine"], employes["Fanta"]))
        soir_5 = self._additions(session, 5)[1]
        self.assertEqual((soir_2.state, soir_5.state), ('cancel', 'cancel'))

        # Les annulations : deux produits (Paul et Awa sur la table 5, Paul
        # seul sur la table 4), une table (Paul seul), deux tables à la
        # fermeture ; toutes autorisées par Paul ; aucun retrait ni aucune
        # annulation sans code.
        traces = self.env['aite.restaurant.annulation'].search(
            [('session_id', '=', session.id)], order='id')
        self.assertEqual(sorted(traces.mapped('type_annulation')),
                         ['fermeture', 'fermeture', 'produit', 'produit', 'table'])
        self.assertTrue(all(traces.mapped('autorisee')))
        self.assertEqual(traces.mapped('superieur_id'), employes["Paul"])
        produit_5 = traces.filtered(lambda t: t.order_id == addition)
        self.assertEqual((produit_5.type_annulation, produit_5.produit_nom, produit_5.quantite),
                         ('produit', "Water", 1))
        self.assertEqual(produit_5.serveur_id, employes["Awa"])
        self.assertEqual(produit_5.motif_id, self.env.ref('aite_pos_restaurant.motif_erreur_saisie'))
        self.assertEqual(produit_5.montant, 500)
        produit_4 = traces.filtered(lambda t: t.order_id == premiere)
        self.assertEqual((produit_4.type_annulation, produit_4.produit_nom, produit_4.quantite),
                         ('produit', "Water", 1))
        # Le stock : quatre Coca-Cola vendues ; celle de la table annulée à la
        # fermeture ne sort pas ; l'épuisé reste à 0.
        self.assertEqual(self._disponible(coca), 6)
        self.assertEqual(self._disponible(minute), 0)

        # Le lendemain : Carine rouvre la caisse avec le fond de la veille,
        # Paul la ferme sans vente ; une nouvelle session attend le code.
        lendemain = self.env['pos.session'].search(
            [('config_id', '=', self.pos_config.id), ('id', '>', session.id)], order='id')
        self.assertEqual(len(lendemain), 2, lendemain.mapped('state'))
        self.assertEqual(lendemain[0].state, 'closed')
        self.assertEqual(lendemain[0].aite_ouverte_par_id, employes["Carine"])
        self.assertEqual(lendemain[0].aite_fermee_par_id, employes["Paul"])
        self.assertEqual((lendemain[0].cash_register_balance_start,
                          lendemain[0].cash_register_balance_end_real), (4500, 4500))
        self.assertFalse(lendemain[0].order_ids)
        self.assertEqual(lendemain[1].state, 'opening_control')
        self.assertEqual(self.pos_config.current_session_id, lendemain[1])


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursPartsEgales(AiteToursModeCommon):
    """Partager l'addition à parts égales (demande du Messager : « diviser
    la facture à part égale par le nombre de personnes qui doivent payer »).

    La caisse est en francs CFA (aucune décimale), comme au Messager ; trois
    modes : Cash, Bank et Mobile Money. Le ticket s'imprime à la validation
    (« Impression automatique du reçu ») sur une imprimante simulée par le
    tour. Coca-Cola 60 000, Water 40 000, Minute Maid 15 001."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        journal = cls.env['account.journal'].create({
            'name': "Mobile Money", 'code': 'MOMO', 'type': 'bank',
            'company_id': cls.env.company.id})
        cls.mobile_money = cls.env['pos.payment.method'].create({
            'name': "Mobile Money", 'journal_id': journal.id,
            'company_id': cls.env.company.id})
        cls.pos_config.write({
            'payment_method_ids': [(4, cls.mobile_money.id)],
            'iface_print_auto': True,
        })
        Produit = cls.env['product.product']
        for nom, prix in (("Coca-Cola", 60000), ("Water", 40000), ("Minute Maid", 15001)):
            Produit.search([('name', '=', nom)], limit=1).product_tmpl_id.list_price = prix

    def _en_francs_cfa(self):
        """La société et les listes de prix en francs CFA (comme le test
        « zero decimal places » d'Odoo)."""
        xaf = self.env.ref('base.XAF')
        xaf.active = True
        self.env.company.currency_id = xaf
        self.pos_config.available_pricelist_ids.write({'currency_id': xaf.id})
        self.assertEqual(xaf.decimal_places, 0)

    def _addition(self, numero):
        return self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id),
            ('table_id.table_number', '=', numero)], order='id desc', limit=1)

    def _paiements(self, addition):
        """Les paiements, sans la ligne de monnaie d'Odoo (`is_change`)."""
        return [(p.payment_method_id.name, p.amount)
                for p in addition.payment_ids.sorted('id') if not p.is_change]

    def test_parts_egales(self):
        """Table de 3 personnes, 100 000 FCFA : 33 333 en espèces, 33 333 par
        carte, 33 334 en Mobile Money ; une seule addition payée, qui garde
        ses personnes et « Ouverte par » / « Encaissée par »."""
        self._en_francs_cfa()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesTour', login='pos_user')
        addition = self._addition(5)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(addition.amount_total, 100000)
        self.assertEqual(self._paiements(addition),
                         [("Cash", 33333), ("Bank", 33333), ("Mobile Money", 33334)])
        self.assertEqual(addition.amount_return, 0)
        self.assertFalse(addition.payment_ids.filtered('is_change'))
        self.assertEqual(addition.aite_parts_egales, 3)
        self.assertEqual(addition.customer_count, 3)
        self.assertEqual(addition.aite_ouverte_par_id, self.employes["Awa"])
        self.assertEqual(addition.aite_encaissee_par_id, self.employes["Carine"])
        self.assertEqual(sorted(addition.lines.product_id.mapped('name')), ["Coca-Cola", "Water"])
        self.assertEqual(self.env['pos.order'].search_count([
            ('config_id', '=', self.pos_config.id), ('state', '!=', 'cancel')]), 1)

    def test_parts_egales_changer_d_avis(self):
        """La caissière choisit 2 au lieu des 3 personnes : 37 500 + 37 501 ;
        40 000 donnés en espèces pour la dernière part : 2 499 rendus."""
        self._en_francs_cfa()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesChangerTour', login='pos_user')
        addition = self._addition(4)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(self._paiements(addition), [("Bank", 37500), ("Cash", 40000)])
        self.assertEqual(addition.amount_return, 2499)
        # La monnaie de la dernière part : une seule ligne de rendu, en espèces.
        self.assertEqual([(p.payment_method_id.name, p.amount)
                          for p in addition.payment_ids if p.is_change], [("Cash", -2499)])
        self.assertEqual(addition.aite_parts_egales, 2)

    def test_parts_egales_annuler(self):
        """Un paiement avant le partage, retour au panier, puis « Annuler le
        partage » : Odoo reprend la main ; le ticket ne parle pas de partage."""
        self._en_francs_cfa()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesAnnulerTour', login='pos_user')
        addition = self._addition(2)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(self._paiements(addition),
                         [("Cash", 10000), ("Bank", 15000), ("Mobile Money", 30001)])
        self.assertEqual(addition.aite_parts_egales, 0)

    def test_parts_egales_arrondi_des_especes(self):
        """L'arrondi des espèces d'Odoo (pas de 25, espèces seulement) : les
        parts sont des multiples de 25, la dernière est arrondie par Odoo ;
        la validation passe sans « Rounding error »."""
        self._en_francs_cfa()
        self._arrondi_de_25()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesArrondiTour', login='pos_user')
        addition = self._addition(5)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(self._paiements(addition),
                         [("Cash", 33325), ("Bank", 33325), ("Cash", 33350)])
        self.assertEqual(addition.aite_parts_egales, 3)


    # Après la revue

    def test_parts_egales_monnaie_d_une_part(self):
        """La 1re personne donne 50 000 en espèces pour une part de 33 333 :
        la caisse dit « Monnaie à rendre : 16 667 » et enregistre 33 333 en
        espèces (ce qui reste dans le tiroir) ; la dernière part reste
        33 334. Une ligne ramenée à 0 ne compte pas ; la dernière part créée
        hors des boutons (comme « Mettre sur ardoise ») compte."""
        self._en_francs_cfa()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesMonnaieTour', login='pos_user')
        addition = self._addition(5)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(self._paiements(addition),
                         [("Cash", 33333), ("Bank", 33333), ("Mobile Money", 33334)])
        self.assertEqual(addition.amount_return, 0)
        self.assertFalse(addition.payment_ids.filtered('is_change'))
        self.assertEqual(addition.aite_parts_egales, 3)

    def _arrondi_de_25(self):
        arrondi = self.env['account.cash.rounding'].create({
            'name': "25 FCFA", 'rounding': 25, 'rounding_method': 'HALF-UP',
            'strategy': 'add_invoice_line',
            'profit_account_id': self.company_data['default_account_revenue'].id,
            'loss_account_id': self.company_data['default_account_expense'].id,
        })
        self.pos_config.write({'cash_rounding': True, 'rounding_method': arrondi.id,
                               'only_round_cash_method': True})

    def test_parts_egales_arrondi_reparti(self):
        """Arrondi de 25, 8 010 en 3 : 2 650 et 2 675 (les pas restants vont
        aux dernières personnes, pas tous au dernier), puis le reste,
        2 685, arrondi à 2 675 en espèces."""
        self._en_francs_cfa()
        self._arrondi_de_25()
        self.env['product.product'].search(
            [('name', '=', "Minute Maid")], limit=1).product_tmpl_id.list_price = 8010
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesArrondiRepartiTour', login='pos_user')
        addition = self._addition(5)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(self._paiements(addition),
                         [("Cash", 2650), ("Bank", 2675), ("Cash", 2675)])
        self.assertEqual(addition.aite_parts_egales, 3)

    def test_parts_egales_pourboire(self):
        """Un pourboire ajouté sur l'écran de paiement : le partage est
        oublié (les parts ne portent plus sur le bon total) et se refait."""
        self._en_francs_cfa()
        self.pos_config.write({
            'iface_tipproduct': True,
            'tip_product_id': self.env.ref('point_of_sale.product_product_tip').id,
        })
        self._ouvrir_la_caisse()
        self.start_pos_tour('AitePartsEgalesPourboireTour', login='pos_user')
        addition = self._addition(5)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(addition.amount_total, 105000)
        self.assertEqual(self._paiements(addition),
                         [("Cash", 33333), ("Bank", 35833), ("Mobile Money", 35834)])
        self.assertEqual(addition.aite_parts_egales, 2)

@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursPartsEgalesHorsMode(AiteToursCommon):
    """Une caisse de restaurant hors « Service à table contrôlé » : pas de
    bouton « Partager à parts égales »."""

    def test_pas_de_partage_hors_mode(self):
        self.assertFalse(self.pos_config.aite_mode_restaurant)
        self.pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour('AitePartsEgalesHorsModeTour', login='pos_user')


class AiteToursBonsCommon(AiteToursModeCommon):
    """Les bons de préparation (18.0.1.0.13) : deux imprimantes, simulées par
    les tours (bons_tour.js) — « Cuisine » pour la famille Plats (Poulet DG,
    7 000, accompagnement Riz ou Frites, sans taxe) et « Bar » pour Drinks
    (Coca-Cola). La caisse est en français : les bons d'Odoo y affichent
    « New » et « Tableau 5 » (constat du Messager)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('fr_FR')
        cls.pos_user.lang = 'fr_FR'
        plats = cls.env['pos.category'].create({'name': "Plats", 'sequence': 3})
        accompagnement = cls.env['product.attribute'].create({
            'name': "Accompagnement", 'create_variant': 'no_variant', 'display_type': 'radio'})
        valeurs = cls.env['product.attribute.value'].create([
            {'name': "Riz", 'attribute_id': accompagnement.id},
            {'name': "Frites", 'attribute_id': accompagnement.id},
        ])
        cls.poulet = cls.env['product.template'].create({
            'name': "Poulet DG", 'list_price': 7000, 'available_in_pos': True,
            'taxes_id': [(5, 0, 0)], 'pos_categ_ids': [(4, plats.id)],
            'attribute_line_ids': [(0, 0, {
                'attribute_id': accompagnement.id, 'value_ids': [(6, 0, valeurs.ids)]})],
        })
        boissons = cls.env['product.product'].search([('name', '=', "Coca-Cola")], limit=1).pos_categ_ids
        Imprimante = cls.env['pos.printer']
        cls.cuisine = Imprimante.create({
            'name': "Cuisine", 'printer_type': 'epson_epos', 'epson_printer_ip': '127.0.0.1',
            'product_categories_ids': [(6, 0, plats.ids)]})
        cls.bar = Imprimante.create({
            'name': "Bar", 'printer_type': 'epson_epos', 'epson_printer_ip': '127.0.0.2',
            'product_categories_ids': [(6, 0, boissons.ids)]})
        cls.pos_config.write({
            'is_order_printer': True,
            'printer_ids': [(6, 0, (cls.cuisine | cls.bar).ids)],
        })

    def _table(self, numero):
        return self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id),
            ('table_id.table_number', '=', numero)], order='id desc', limit=1)

    def _unites_saisies(self, addition):
        """Le nombre de Poulet DG au journal des saisies de l'addition."""
        return sum(q for (nom, q, _e) in self._saisies(addition) if (nom or '').startswith("Poulet DG"))

    def _poulets(self, addition):
        lignes = addition.lines.filtered(lambda l: l.product_id.product_tmpl_id == self.poulet)
        return sorted((l.qty, l.note or '') for l in lignes)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursBons(AiteToursBonsCommon):
    """« Imprimer 3 fois d'un coup en cuisine » : la cuisine est réglée sur 3
    exemplaires, le bar sur 1."""

    def test_exemplaires(self):
        self.cuisine.aite_exemplaires = 3
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteBonsExemplairesTour', login='pos_user')
        addition = self._table(5)
        # 2 poulets envoyés, 1 annulé, 1 frites envoyé (imprimante en panne :
        # l'envoi est quand même enregistré, comme dans Odoo).
        self.assertEqual(sum(addition.lines.filtered(
            lambda l: l.product_id.product_tmpl_id == self.poulet).mapped('qty')), 2)

    def test_rendu_en_erreur(self):
        """Relecture : une erreur au rendu du bon donne l'alerte « Bon non
        imprimé » ; les autres imprimantes reçoivent leur bon."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteBonRenduEnErreurTour', login='pos_user')
        self.assertEqual(self._poulets(self._table(5)), [(1.0, '')])

    def test_panne_notification(self):
        """Relecture : cuisine injoignable, la notification dit que le bon
        de la cuisine n'est pas sorti ; l'envoi reste enregistré."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteBonPanneNotificationTour', login='pos_user')
        addition = self._table(5)
        self.assertEqual(sum(addition.lines.mapped('aite_qte_envoyee')), 2)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursNotes(AiteToursBonsCommon):
    """Les défauts des notes constatés au Messager (B1 à B6), un exemplaire
    par imprimante. Chaque tour reproduit un défaut, écrit avant sa
    correction."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        divers = cls.env['pos.category'].create({'name': "Divers", 'sequence': 9})
        cls.env['product.product'].create({
            'name': "Pain", 'list_price': 500, 'available_in_pos': True,
            'taxes_id': [(5, 0, 0)], 'pos_categ_ids': [(4, divers.id)]})

    def test_coupure(self):
        """B1 : la note posée sur l'unité de plus ne change ni la quantité ni
        le total, sur la caisse comme sur le serveur."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteCoupureTour', login='pos_user')
        addition = self._table(4)
        self.assertEqual(self._poulets(addition), [(1.0, 'bien cuit'), (3.0, '')])
        self.assertEqual(addition.amount_total, 28000)
        self.assertEqual(sum(addition.lines.mapped('aite_qte_envoyee')), 4)
        self.assertEqual(self._unites_saisies(addition), 4)

    def test_coupure_apres_synchro(self):
        """B1, relecture : l'addition a été enregistrée entre l'ajout du 4e
        poulet et la note. Le journal des saisies compte 4 poulets, pas 5."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteCoupureSynchroTour', login='pos_user')
        addition = self._table(4)
        self.assertEqual(self._poulets(addition), [(1.0, 'bien cuit'), (3.0, '')])
        self.assertEqual(addition.amount_total, 28000)
        self.assertEqual(self._unites_saisies(addition), 4, self._saisies(addition))
        self.assertFalse(self.env['aite.restaurant.annulation'].search(
            [('order_id', '=', addition.id)]), "la coupure n'est pas un retrait")

    def test_note_puis_plus_un(self):
        """Relecture : note sur un plat parti, puis une unité de plus au pavé :
        le bon dit « Nouveau 1 Poulet DG »."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNotePuisPlusUnTour', login='pos_user')
        addition = self._table(5)
        self.assertEqual(self._poulets(addition), [(4.0, 'bien cuit')])
        self.assertEqual(self._unites_saisies(addition), 4)

    def test_ignorer(self):
        """B2 : « Ignorer » ne coupe pas une ligne en partie envoyée."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteIgnorerTour', login='pos_user')
        self.assertEqual(self._poulets(self._table(4)), [(4.0, '')])

    def test_ignorer_note_du_plat(self):
        """B2 : « Ignorer » garde la note du plat."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteIgnorerNotePlatTour', login='pos_user')
        coca = self._table(4).lines.filtered(lambda l: l.product_id.name == "Coca-Cola")
        self.assertEqual(coca.note, "sans glaçon")

    def test_ignorer_note_generale(self):
        """B2 : « Ignorer » garde la note générale."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteIgnorerNoteGeneraleTour', login='pos_user')
        self.assertEqual(self._table(4).general_note, "Client pressé")

    def test_note_retiree(self):
        """Relecture : une note effacée sur un plat parti est annoncée au bar
        (« Note retirée : sans glaçon »)."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteRetireeTour', login='pos_user')
        coca = self._table(5).lines.filtered(lambda l: l.product_id.name == "Coca-Cola")
        self.assertFalse(coca.note)

    def test_note_generale_libelle(self):
        """Relecture : « Note générale », pas « Message », sur « J'envoie » et
        dans la notification."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteGeneraleLibelleTour', login='pos_user')
        self.assertEqual(self._table(5).general_note, "Client pressé")

    def test_note_au_client(self):
        """B3 : « Note au client » sur une ligne déjà envoyée."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteClientTour', login='pos_user')
        addition = self._table(4)
        self.assertEqual(addition.lines.customer_note, "Joyeux anniversaire")
        self.assertEqual(addition.amount_total, 7000)

    def test_note_generale_seule(self):
        """B4 : une note générale tapée seule est imprimée."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteNoteGeneraleSeuleTour', login='pos_user')
        self.assertEqual(self._table(2).general_note, "Allergie arachide")
        self.assertEqual(self._table(5).general_note, "Client pressé")

    def test_addition_sans_note_generale(self):
        """B5 : la note générale (pour la cuisine) n'est pas sur l'addition."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionSansNoteTour', login='pos_user')
        self.assertEqual(self._table(5).general_note, "Client pressé")

    def test_bon_en_francais(self):
        """B6 : « Nouveau », « Note », « Annulé », « Table 5 »."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteBonEnFrancaisTour', login='pos_user')
        self.assertEqual(self._poulets(self._table(5)), [(1.0, 'bien cuit')])


class AiteToursFamillesCommon(AiteToursModeCommon):
    """Les familles de la carte (18.0.1.0.14) : « ça imprime directement sur
    chaque imprimante selon son type : chaud, froid, bar, pizza et autre » et
    « au niveau de la facture, grouper les produits par famille ».

    La carte (sans taxe) : Plats > Grillades (Poulet braisé 7 000) ;
    Pizzas & burgers > Pizzas (Pizza Marguerite 5 000), Burgers (Burger
    maison 4 000) ; Desserts (Glace vanille 1 500) ; Bar > Vins > Vins blancs
    (Vin blanc au verre 3 000) ; Pain maison (500, sans famille). Trois
    imprimantes Epson, simulées par les tours (familles_tour.js) : Chaud
    (Plats, Burgers), Pizza (Pizzas), Bar (Bar, la famille de niveau 1
    seulement). Personne ne prend les desserts ni le pain."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('fr_FR')
        cls.pos_user.lang = 'fr_FR'
        Famille = cls.env['pos.category']
        cls.f_plats = Famille.create({'name': "Plats", 'sequence': 10})
        grillades = Famille.create({'name': "Grillades", 'parent_id': cls.f_plats.id})
        cls.f_pizzas_burgers = Famille.create({'name': "Pizzas & burgers", 'sequence': 11})
        pizzas = Famille.create({'name': "Pizzas", 'parent_id': cls.f_pizzas_burgers.id, 'sequence': 1})
        burgers = Famille.create({'name': "Burgers", 'parent_id': cls.f_pizzas_burgers.id, 'sequence': 2})
        cls.f_desserts = Famille.create({'name': "Desserts", 'sequence': 12})
        cls.f_bar = Famille.create({'name': "Bar", 'sequence': 13})
        vins = Famille.create({'name': "Vins", 'parent_id': cls.f_bar.id})
        vins_blancs = Famille.create({'name': "Vins blancs", 'parent_id': vins.id})
        Produit = cls.env['product.product']
        for nom, prix, famille in (("Poulet braisé", 7000, grillades), ("Pizza Marguerite", 5000, pizzas),
                                   ("Burger maison", 4000, burgers), ("Glace vanille", 1500, cls.f_desserts),
                                   ("Vin blanc au verre", 3000, vins_blancs), ("Pain maison", 500, None)):
            Produit.create({
                'name': nom, 'list_price': prix, 'available_in_pos': True, 'taxes_id': [(5, 0, 0)],
                'pos_categ_ids': [(6, 0, famille.ids if famille else [])]})
        Imprimante = cls.env['pos.printer']
        cls.chaud = Imprimante.create({
            'name': "Chaud", 'printer_type': 'epson_epos', 'epson_printer_ip': '127.0.0.1',
            'product_categories_ids': [(6, 0, (cls.f_plats | burgers).ids)]})
        cls.pizza = Imprimante.create({
            'name': "Pizza", 'printer_type': 'epson_epos', 'epson_printer_ip': '127.0.0.2',
            'product_categories_ids': [(6, 0, pizzas.ids)]})
        cls.bar = Imprimante.create({
            'name': "Bar", 'printer_type': 'epson_epos', 'epson_printer_ip': '127.0.0.3',
            'product_categories_ids': [(6, 0, cls.f_bar.ids)]})
        cls.pos_config.write({
            'is_order_printer': True,
            'printer_ids': [(6, 0, (cls.chaud | cls.pizza | cls.bar).ids)],
        })

    def _avec_autre(self):
        """L'imprimante « Autre » : « Prend tout ce qu'aucune autre imprimante
        ne prend », sans famille cochée, 2 exemplaires."""
        self.autre = self.env['pos.printer'].create({
            'name': "Autre", 'printer_type': 'epson_epos', 'epson_printer_ip': '127.0.0.4',
            'aite_prend_le_reste': True, 'aite_exemplaires': 2})
        self.pos_config.printer_ids = [(4, self.autre.id)]
        return self.autre

    def _table(self, numero):
        return self.env['pos.order'].search([
            ('config_id', '=', self.pos_config.id),
            ('table_id.table_number', '=', numero)], order='id desc', limit=1)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursFamilles(AiteToursFamillesCommon):
    """Les bons de préparation, famille par famille."""

    def test_famille_parente(self):
        """Cocher « Bar » (niveau 1) couvre Vins blancs (niveau 3) ; « Plats »
        couvre Grillades. Vérification du code d'Odoo (parentPosCategIds)."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteFamilleParenteTour', login='pos_user')

    def test_imprimante_autre(self):
        """Le dessert (famille non cochée) et le pain (sans famille) partent
        sur « Autre », jamais perdus ; l'annulation et la note générale
        suivent la même règle."""
        self._avec_autre()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteImprimanteAutreTour', login='pos_user')
        pain = self._table(5).lines.filtered(lambda l: l.product_id.name == "Pain maison")
        self.assertEqual(pain.qty, 1)
        self.assertEqual(pain.aite_qte_envoyee, 1)

    def test_epson_direct(self):
        """Sans boîtier IoT : « J'envoie » envoie le bon à l'imprimante Epson
        (requête ePOS à son adresse, au protocole de la page), sans fenêtre
        ni aperçu d'impression."""
        self._avec_autre()
        self.pos_config.printer_ids = [(6, 0, (self.chaud | self.autre).ids)]
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteEpsonDirectTour', login='pos_user')


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursAdditionFamilles(AiteToursFamillesCommon):
    """L'addition et le ticket groupés par famille, en francs CFA ; le
    ticket s'imprime à la validation (« Impression automatique du reçu »)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config.write({'iface_print_auto': True})

    def _en_francs_cfa(self):
        xaf = self.env.ref('base.XAF')
        xaf.active = True
        self.env.company.currency_id = xaf
        self.pos_config.available_pricelist_ids.write({'currency_id': xaf.id})

    def test_addition_groupee(self):
        """Addition, ticket final et réimpression : Plats, Pizzas & burgers,
        Bar, Autres, chacune avec son sous-total ; total et paiement
        inchangés."""
        self._en_francs_cfa()
        self.pos_config.aite_grouper_familles = True
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionFamillesTour', login='pos_user')
        addition = self._table(5)
        self.assertEqual(addition.state, 'paid')
        self.assertEqual(addition.amount_total, 26500)

    def test_addition_table_divisee(self):
        """La fenêtre des additions d'une table divisée : chaque addition est
        groupée."""
        self._en_francs_cfa()
        self.pos_config.aite_grouper_familles = True
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionFamillesDiviseeTour', login='pos_user')

    def test_reglage_decoche(self):
        """Réglage décoché (d'office) : le ticket d'Odoo, inchangé."""
        self._en_francs_cfa()
        self.assertFalse(self.pos_config.aite_grouper_familles)
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAdditionSansFamillesTour', login='pos_user')


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursFamillesRelecture(AiteToursFamillesCommon):
    """Les constats des relectures de 18.0.1.0.14 (routage et règles)."""

    def test_autre_seule_sans_famille(self):
        """Une « Autre » sans famille cochée, seule imprimante de la caisse :
        elle reçoit tout (le repère des plats sans famille compris)."""
        self._avec_autre()
        self.pos_config.printer_ids = [(6, 0, self.autre.ids)]
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAutreSeuleTour', login='pos_user')

    def test_ordre_des_familles(self):
        """À séquence égale, les familles de l'addition suivent leur nom."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteRegleOrdreFamillesTour', login='pos_user')

    def test_hors_cuisine(self):
        """Récompenses et lignes mères de menu ne partent pas seules sur
        « Autre »."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteRegleHorsCuisineTour', login='pos_user')

    def test_conseil_certificat(self):
        """En https, l'alerte de panne d'une Epson dit d'accepter son
        certificat."""
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteRegleCertificatTour', login='pos_user')


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestToursAdditionFamillesRelecture(AiteToursFamillesCommon):
    """Le pourboire : ni sur « Autre », ni dans la rubrique « Autres »."""

    def test_pourboire_hors_cuisine_et_hors_rubrique(self):
        xaf = self.env.ref('base.XAF')
        xaf.active = True
        self.env.company.currency_id = xaf
        self.pos_config.available_pricelist_ids.write({'currency_id': xaf.id})
        self.pos_config.write({
            'aite_grouper_familles': True,
            'iface_tipproduct': True,
            'tip_product_id': self.env.ref('point_of_sale.product_product_tip').id,
        })
        self._avec_autre()
        self._ouvrir_la_caisse()
        self.start_pos_tour('AiteAutreHorsCuisineTour', login='pos_user')
