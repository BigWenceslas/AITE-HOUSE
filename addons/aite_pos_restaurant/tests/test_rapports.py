# -*- coding: utf-8 -*-
"""Les rapports du restaurant (spécification, parties 3.4, 5 et 6.2).

Incrément 4 : le rapport des annulations (REST-22) et le profil de lecture
du chef de salle (AH-05) — il lit les annulations sans aucun droit sur la
caisse : il ne peut ni ouvrir une session ni voir la configuration.

Incrément 6 : « Personnes et tables » (REST-25-P1, REST-02 critère 4 ; partie
5.2) — quatre compteurs calculés et stockés sur l'addition, lus par une vue
croisée de l'écran des commandes ; le rapport de fermeture (REST-25 critère 5,
Q51, REST-22 ; partie 5.3) — tables, personnes, ventes sans table et
annulations de la session, imprimés depuis la caisse et depuis la gestion.
Chaque addition passe par le chemin de la caisse (``_commande_caisse``).
"""
import datetime
from types import SimpleNamespace
from uuid import uuid4

import pytz
from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.tools.safe_eval import safe_eval

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


class RapportsCommon(RestaurantCommon):
    """Une session ouverte par Carine ; l'encaissement en espèces."""

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()
        self.especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]
        self.table_3 = self.table_12.copy({'table_number': 3})

    def _table(self, table, personnes, produits, ouverte_par=None, encaissee_par=None,
               payer=True, nom=False):
        """Une table ouverte (code, personnes), servie, puis encaissée par
        Carine : ``produits`` = [(produit, quantité)]."""
        addition = Addition(table, personnes, ouverte_par or self.awa, nom=nom)
        for produit, quantite in produits:
            addition.ajouter(produit, quantite)
        addition.envoyer()
        commande = self._commande_caisse(addition, ouverte_par or self.awa)
        if payer:
            self._commande_caisse(addition, encaissee_par or self.carine, etat='paid',
                                  payer=self.especes)
        return addition, commande


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestPersonnesEtTables(RapportsCommon):
    """« Personnes et tables » (REST-25-P1, REST-02 critère 4 ; partie 5.2)."""

    MESURES = ['aite_tables:sum', 'aite_personnes:sum', 'aite_sans_table:sum',
               'aite_articles:sum', 'amount_total:sum']

    def _rapport(self, groupby=(), domaine=None):
        """Ce que lit le manager : l'action « Personnes et tables » (son
        domaine), sur la session du test."""
        action = self.env.ref('aite_pos_restaurant.action_personnes_tables')
        domaine = safe_eval(action.domain or '[]') + [('session_id', '=', self.session.id)] \
            + (domaine or [])
        lignes = self.env['pos.order'].with_user(self.compte_manager).read_group(
            domaine, self.MESURES, list(groupby), lazy=False)
        if groupby:
            return lignes
        ligne = lignes[0]
        return (ligne['aite_tables'], ligne['aite_personnes'], ligne['aite_sans_table'],
                ligne['amount_total'])

    def test_trois_tables_de_2_4_et_7_personnes(self):
        """REST-25 critère 1 : 3 tables, 13 personnes et 130 000 FCFA sur la
        même page."""
        self._table(self.table_7, 2, [(self.poulet, 4)])
        self._table(self.table_12, 4, [(self.poulet, 8)])
        self._table(self.table_3, 7, [(self.poulet, 8)])
        self.assertEqual(self._rapport(), (3, 13, 0, 130000.0))
        self.assertEqual(self.config.currency_id, self.company.currency_id)

    def test_une_table_divisee_compte_une_fois(self):
        """REST-25 critère 3 : une table de 6 divisée en deux additions compte
        pour 1 table et 6 personnes (la part « 12B » a 0 personne)."""
        addition, origine = self._table(self.table_12, 6, [(self.castel, 4)], payer=False)
        part = Addition(personnes=0, ouverte_par=self.awa, nom="12B")
        part.valeurs['aite_origine_uuid'] = origine.uuid
        part.ajouter(self.castel, 2)
        uuid = next(iter(addition.lignes))
        addition.changer(uuid, 2)
        self._commande_caisse(addition, self.awa, deplacement=True)
        self._commande_caisse(part, self.awa, deplacement=True)
        self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)
        commande_part = self._commande_caisse(part, self.carine, etat='paid', payer=self.especes)
        self.assertEqual((commande_part.aite_tables, commande_part.aite_personnes,
                          commande_part.aite_sans_table), (0, 0, 0))
        self.assertEqual(self._rapport(), (1, 6, 0, 4000.0))

    def test_une_reunion_additionne_les_personnes(self):
        """REST-25-P1 : la table 7 (3 personnes) réunie à la table 12
        (4 personnes) : 1 table, 7 personnes ; l'addition absorbée est
        annulée, elle ne compte pas."""
        _t7, table_7 = self._table(self.table_7, 3, [(self.castel, 2)], payer=False)
        t12, table_12 = self._table(self.table_12, 4, [(self.poulet, 1)], payer=False)
        t12.ajouter(self.castel, 2)
        t12.valeurs['customer_count'] = 7
        self._commande_caisse(t12, self.awa, deplacement=True)
        caisse = self.env['pos.order'].with_user(self.compte_caisse)
        caisse.aite_marquer_fusion(table_7.id)
        table_7.with_user(self.compte_caisse).action_pos_order_cancel()
        self._commande_caisse(t12, self.carine, etat='paid', payer=self.especes)
        self.assertEqual(table_12.customer_count, 7)
        self.assertEqual(self._rapport(), (1, 7, 0, 8500.0))

    def test_un_numero_inconnu_compte_comme_une_table(self):
        """Q25, T11 : « 99 » tapé, 2 personnes : une table."""
        _addition, commande = self._table(None, 2, [(self.castel, 1)], nom="99")
        self.assertEqual(commande.floating_order_name, "99")
        self.assertEqual(self._rapport(), (1, 2, 0, 1000.0))

    def test_ouverte_ou_annulee_ne_compte_pas(self):
        """REST-25 critère 4 : une table encore ouverte et une table annulée
        ne sont pas comptées."""
        self._table(self.table_7, 3, [(self.castel, 1)], payer=False)
        _addition, annulee = self._table(self.table_12, 2, [(self.castel, 1)], payer=False)
        annulee.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(annulee.state, 'cancel')
        self.assertEqual(self._rapport(), (0, 0, 0, False))

    def test_un_remboursement_ne_compte_pas(self):
        """Un remboursement n'est ni une table ni une vente sans table."""
        _addition, commande = self._table(self.table_12, 2, [(self.castel, 1)])
        retour = Addition(personnes=0, ouverte_par=self.fanta)
        retour.ajouter(self.castel, -1)
        lien = {'refunded_orderline_id': commande.lines.id}
        remboursement = self._commande_caisse(retour, self.fanta, etat='paid',
                                              payer=self.especes, en_plus_lignes=lien)
        self.assertEqual(remboursement.state, 'paid')
        self.assertEqual((remboursement.aite_tables, remboursement.aite_personnes,
                          remboursement.aite_sans_table, remboursement.aite_articles),
                         (0, 0, 0, 0.0))
        self.assertEqual(self._rapport(), (1, 2, 0, 0.0))

    def test_une_vente_sans_table_est_comptee_a_part(self):
        """Q76 : une vente sans table compte 0 personne, à part ; deux tables
        de 4 et 2 personnes et trois ventes sans table (REST-25 critère 6)."""
        self._table(self.table_7, 4, [(self.castel, 1)])
        self._table(self.table_12, 2, [(self.castel, 1)])
        for _i in range(3):
            vente = Addition(personnes=0, ouverte_par=self.carine)
            vente.ajouter(self.castel, 1)
            self._commande_caisse(vente, self.carine, etat='paid', payer=self.especes)
        self.assertEqual(self._rapport(), (2, 6, 3, 5000.0))

    def test_articles_vendus(self):
        """La quantité vendue (Q50 : le rapport donne les deux) : la somme des
        quantités de l'addition."""
        _addition, commande = self._table(self.table_12, 4, [(self.castel, 3),
                                                             (self.poulet, 2)])
        self.assertEqual(commande.aite_articles, 5.0)
        ligne = self._rapport(groupby=['session_id'])[0]
        self.assertEqual(ligne['aite_articles'], 5.0)

    def test_les_compteurs_suivent_l_addition(self):
        """Le nombre de personnes changé en cours de table (« 6 personnes ») :
        les compteurs suivent ; ceux que la caisse enverrait sont ignorés."""
        addition, commande = self._table(self.table_12, 4, [(self.castel, 1)], payer=False)
        self.assertEqual((commande.aite_tables, commande.aite_personnes), (1, 4))
        addition.valeurs['customer_count'] = 6
        self._commande_caisse(addition, self.awa, en_plus={
            'aite_tables': 9, 'aite_personnes': 99, 'aite_sans_table': 9, 'aite_articles': 99})
        self.assertEqual((commande.aite_tables, commande.aite_personnes,
                          commande.aite_sans_table, commande.aite_articles), (1, 6, 0, 1.0))
        commande.with_user(self.compte_caisse).write({'aite_personnes': 50})
        self.assertEqual(commande.aite_personnes, 6)

    def test_par_serveur_et_par_caissiere(self):
        """REST-02 critère 4 : regroupé par « Ouverte par » (Awa, Moussa) et
        par « Encaissée par » (Carine) ; par session (Q54)."""
        self._table(self.table_7, 2, [(self.castel, 1)], ouverte_par=self.awa)
        self._table(self.table_12, 5, [(self.castel, 2)], ouverte_par=self.moussa)
        par_serveur = {ligne['aite_ouverte_par_id'][1]: ligne['aite_personnes']
                       for ligne in self._rapport(groupby=['aite_ouverte_par_id'])}
        self.assertEqual(par_serveur, {"Awa": 2, "Moussa": 5})
        par_caissiere = {ligne['aite_encaissee_par_id'][1]: ligne['aite_tables']
                         for ligne in self._rapport(groupby=['aite_encaissee_par_id'])}
        self.assertEqual(par_caissiere, {"Carine": 2})
        par_session = self._rapport(groupby=['session_id'])
        self.assertEqual([(ligne['aite_tables'], ligne['aite_personnes'])
                          for ligne in par_session], [(2, 7)])

    def test_action_vue_croisee_et_menu(self):
        """L'écran : vue croisée par jour, mesures Tables, Personnes, Ventes
        sans table, Articles, Total ; périodes comme les annulations, « Aujourd'hui »
        d'office (REST-24) ; regroupements ; aide d'écran vide ; menu Point de
        Vente → Analyse → « Personnes et tables », pour le manager."""
        action = self.env.ref('aite_pos_restaurant.action_personnes_tables')
        self.assertEqual(action.name, "Personnes et tables")
        self.assertEqual(action.res_model, 'pos.order')
        self.assertEqual(action.view_mode.split(',')[0], 'pivot')
        self.assertEqual(safe_eval(action.domain), [('state', 'in', ('paid', 'done', 'invoiced'))])
        self.assertIn('search_default_aujourd_hui', action.context)
        self.assertIn('o_view_nocontent', action.help)
        self.assertGreaterEqual(len(action.help), 120)
        Commandes = self.env['pos.order'].with_user(self.compte_manager)
        vues = Commandes.get_views(
            [(vue.view_id.id, vue.view_mode) for vue in action.view_ids]
            + [(action.search_view_id.id, 'search')])
        pivot = etree.fromstring(vues['views']['pivot']['arch'])
        self.assertEqual([(n.get('name'), n.get('interval')) for n in pivot.xpath(
            "//field[@type='row']")], [('date_order', 'day')])
        self.assertEqual([n.get('name') for n in pivot.xpath("//field[@type='measure']")],
                         ['aite_tables', 'aite_personnes', 'aite_sans_table', 'aite_articles',
                          'amount_total'])
        champs = vues['models']['pos.order']['fields']
        self.assertEqual([champs[nom]['string'] for nom in (
            'aite_tables', 'aite_personnes', 'aite_sans_table', 'aite_articles')],
            ["Tables", "Personnes", "Ventes sans table", "Articles"])
        recherche = etree.fromstring(vues['views']['search']['arch'])
        filtres = recherche.xpath("//filter/@name")
        for nom in ('aujourd_hui', 'cette_semaine', 'ce_mois', 'cette_annee', 'periode',
                    'par_jour', 'par_session', 'par_ouverte_par', 'par_encaissee_par'):
            with self.subTest(filtre=nom):
                self.assertIn(nom, filtres)
        self.assertEqual(recherche.xpath("//filter[@name='periode']/@date"), ['date_order'])
        # Revue de 6a, constat 5 : la liste montre les compteurs, pas celle
        # des commandes d'Odoo (Réf., Session, Point de vente, Statut…).
        liste = etree.fromstring(vues['views']['list']['arch'])
        visibles = [n.get('name') for n in liste.xpath('//field')
                    if not n.get('column_invisible') and n.get('optional') != 'hide']
        self.assertEqual(visibles, ['date_order', 'table_id', 'aite_personnes', 'aite_articles',
                                    'aite_ouverte_par_id', 'aite_encaissee_par_id',
                                    'amount_total'])
        self.assertEqual(liste.xpath("//field[@name='amount_total']/@widget"), ['monetary'])
        for nom in ('aite_tables', 'aite_personnes', 'aite_sans_table', 'aite_articles',
                    'amount_total'):
            with self.subTest(somme=nom):
                self.assertTrue(liste.xpath("//field[@name='%s']/@sum" % nom))
        self.assertNotEqual(vues['views']['list']['id'],
                            self.env.ref('point_of_sale.view_pos_order_tree').id)
        # Le pivot de la gestion d'Odoo reste celui d'Odoo.
        self.assertNotEqual(Commandes.get_views([(False, 'pivot')])['views']['pivot']['id'],
                            vues['views']['pivot']['id'])
        menu = self.env.ref('aite_pos_restaurant.menu_personnes_tables')
        self.assertEqual(menu.parent_id, self.env.ref('point_of_sale.menu_point_rep'))
        self.assertEqual(menu.action, action)
        self.assertIn(menu.id, self.env['ir.ui.menu'].with_user(
            self.compte_manager)._visible_menu_ids())
        self.assertNotIn(menu.id, self.env['ir.ui.menu'].with_user(
            self.compte_caisse)._visible_menu_ids())

    # ------------------------------------------------------------------
    # Revue de 6a, constat 6 : les bornes des périodes (REST-24)
    # ------------------------------------------------------------------

    FUSEAU = 'Africa/Douala'

    def _bornes(self, vue, filtre, jour):
        """Le domaine d'une période de la recherche, évalué comme le client
        web (py.js) le fait pour ``jour`` (``context_today()``) à l'heure de
        l'utilisateur (``to_utc()`` : de l'heure locale vers UTC)."""
        fuseau = pytz.timezone(self.FUSEAU)

        class Instant(datetime.datetime):
            def to_utc(self):
                return fuseau.localize(self.replace(tzinfo=None)).astimezone(
                    pytz.utc).replace(tzinfo=None)

        arch = etree.fromstring(self.env['pos.order'].get_views(
            [(vue.id, 'search')])['views']['search']['arch'])
        domaine = arch.xpath("//filter[@name='%s']/@domain" % filtre)[0]
        return safe_eval(domaine, {
            'context_today': lambda: jour, 'relativedelta': relativedelta,
            'datetime': SimpleNamespace(datetime=Instant, time=datetime.time,
                                        date=datetime.date)})

    def test_les_bornes_des_periodes(self):
        """« Aujourd'hui » de minuit à minuit, « Cette semaine » du lundi au
        dimanche, « Ce mois » du 1er au dernier jour, « Cette année » du 1er
        janvier au 31 décembre, à l'heure de Douala (UTC+1) : la borne de
        début est minuit à Douala, 23 h la veille en UTC."""
        vue = self.env.ref('aite_pos_restaurant.view_pos_order_search_personnes_tables')

        def local(jour, mois, annee):
            """Minuit à Douala, en UTC."""
            return datetime.datetime(annee, mois, jour) - datetime.timedelta(hours=1)

        cas = [
            # jour, filtre, début (local), fin exclue (local)
            (datetime.date(2026, 11, 14), 'aujourd_hui', (14, 11, 2026), (15, 11, 2026)),
            (datetime.date(2026, 11, 14), 'cette_semaine', (9, 11, 2026), (16, 11, 2026)),
            (datetime.date(2026, 11, 9), 'cette_semaine', (9, 11, 2026), (16, 11, 2026)),
            (datetime.date(2026, 11, 15), 'cette_semaine', (9, 11, 2026), (16, 11, 2026)),
            (datetime.date(2026, 11, 1), 'cette_semaine', (26, 10, 2026), (2, 11, 2026)),
            (datetime.date(2026, 12, 31), 'cette_semaine', (28, 12, 2026), (4, 1, 2027)),
            (datetime.date(2026, 11, 14), 'ce_mois', (1, 11, 2026), (1, 12, 2026)),
            (datetime.date(2026, 12, 31), 'ce_mois', (1, 12, 2026), (1, 1, 2027)),
            (datetime.date(2026, 11, 14), 'cette_annee', (1, 1, 2026), (1, 1, 2027)),
            (datetime.date(2027, 1, 1), 'cette_annee', (1, 1, 2027), (1, 1, 2028)),
        ]
        for jour, filtre, debut, fin in cas:
            with self.subTest(jour=jour.strftime('%d/%m/%Y'), filtre=filtre):
                self.assertEqual(self._bornes(vue, filtre, jour), [
                    ('date_order', '>=', local(*debut).strftime('%Y-%m-%d %H:%M:%S')),
                    ('date_order', '<', local(*fin).strftime('%Y-%m-%d %H:%M:%S'))])
        # Les mêmes périodes que le rapport des annulations (incrément 4).
        annulations = self.env.ref('aite_pos_restaurant.view_restaurant_annulation_search')

        def domaine(arch, filtre):
            texte = etree.fromstring(arch).xpath("//filter[@name='%s']/@domain" % filtre)[0]
            return ' '.join(texte.split())

        for filtre in ('aujourd_hui', 'cette_semaine', 'ce_mois', 'cette_annee'):
            with self.subTest(annulations=filtre):
                self.assertEqual(domaine(annulations.arch, filtre).replace("'date'", "'date_order'"),
                                 domaine(vue.arch, filtre))

    def test_des_ventes_de_part_et_d_autre_des_bornes(self):
        """Trois additions encaissées, datées autour de minuit à Douala, lues
        le samedi 14/11/2026 : celle du dimanche 08/11 à 23 h 30 (heure de
        Douala) est du mois mais pas de la semaine ; celle du lundi 09/11 à
        0 h 30 est de la semaine ; celle du dimanche 01/11 à 0 h 30 est du
        mois. Aucune n'est d'aujourd'hui."""
        vue = self.env.ref('aite_pos_restaurant.view_pos_order_search_personnes_tables')
        dates = ['2026-11-08 22:30:00', '2026-11-08 23:30:00', '2026-10-31 23:30:00']
        commandes = []
        for date_utc, table in zip(dates, (self.table_7, self.table_12, self.table_3)):
            _addition, commande = self._table(table, 2, [(self.castel, 1)])
            self.env.flush_all()
            self.env.cr.execute("UPDATE pos_order SET date_order = %s WHERE id = %s",
                                [date_utc, commande.id])
            commandes.append(commande)
        self.env['pos.order'].invalidate_model(['date_order'])
        action = self.env.ref('aite_pos_restaurant.action_personnes_tables')
        jour = datetime.date(2026, 11, 14)
        Commandes = self.env['pos.order'].with_user(self.compte_manager)

        def lues(filtre):
            return Commandes.search(safe_eval(action.domain) + [
                ('session_id', '=', self.session.id)] + self._bornes(vue, filtre, jour))

        dimanche, lundi, premier = commandes
        self.assertFalse(lues('aujourd_hui'))
        self.assertEqual(lues('cette_semaine'), lundi)
        self.assertEqual(lues('ce_mois'), dimanche | lundi | premier)
        self.assertEqual(lues('cette_annee'), dimanche | lundi | premier)


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestRapportDeFermeture(RapportsCommon):
    """Le rapport de fermeture (REST-25 critère 5, Q51, REST-22 ; partie 5.3) :
    tables, personnes, ventes sans table et annulations de la session, dans
    les données d'Odoo (« Imprimer le rapport » de la caisse, rapport de
    session de la gestion)."""

    def _journee(self):
        """Deux tables (2 et 4 personnes), une vente sans table ; Paul annule
        2 Castel « Erreur de saisie » ; Awa retire 1 Castel envoyée sans code."""
        motif = self.env.ref('aite_pos_restaurant.motif_erreur_saisie')
        self._table(self.table_7, 2, [(self.poulet, 1)])
        t12, table_12 = self._table(self.table_12, 4, [(self.castel, 5)], payer=False)
        uuid = next(iter(t12.lignes))
        reponse = self.env['pos.order'].with_user(self.compte_caisse).aite_autoriser_annulation(
            table_12.ids, [{'uuid': uuid, 'quantite': 2}], '4444', motif.id, False,
            self.awa.id, str(uuid4()), 'produit')
        self.assertNotIn('erreur', reponse)
        t12.changer(uuid, 3)
        for entree in t12.preparation['lines'].values():
            entree['quantity'] = 3
        self._commande_caisse(t12, self.awa)
        t12.changer(uuid, 2)
        self._commande_caisse(t12, self.awa)  # retrait sans code
        self._commande_caisse(t12, self.carine, etat='paid', payer=self.especes)
        vente = Addition(personnes=0, ouverte_par=self.carine)
        vente.ajouter(self.castel, 1)
        self._commande_caisse(vente, self.carine, etat='paid', payer=self.especes)
        return table_12

    def test_les_donnees_du_rapport_de_la_session(self):
        """Ce que reçoit « Imprimer le rapport » de la caisse : la session,
        sous le compte de la caisse (qui ne lit pas le journal des
        annulations)."""
        self._journee()
        Rapport = self.env['report.point_of_sale.report_saledetails'].with_user(
            self.compte_caisse)
        donnees = Rapport.get_sale_details(False, False, False, [self.session.id])
        self.assertTrue(donnees['aite_restaurant'])
        self.assertEqual((donnees['aite_tables'], donnees['aite_personnes'],
                          donnees['aite_sans_table']), (2, 6, 1))
        lignes = [(a['table'], a['produit'], a['quantite'], a['montant'], a['motif'],
                   a['autorisee_par']) for a in donnees['aite_annulations']]
        self.assertEqual(lignes, [
            ("12", "Castel", 2.0, 2000.0, "Erreur de saisie", "Paul"),
            ("12", "Castel", 1.0, 1000.0, "Retrait sans code", ""),
        ])
        self.assertEqual(donnees['aite_annulations_total'],
                         {'quantite': 3.0, 'quantite_texte': "3", 'montant': 3000.0})
        # Revue de 6a, constat 9 : la quantité est écrite par le serveur, dans
        # la langue de l'utilisateur, sans zéros inutiles (« 2 », « 1,5 »).
        self.assertEqual([a['quantite_texte'] for a in donnees['aite_annulations']], ["2", "1"])
        # REST-25 critère 2 : les quantités vendues de chaque produit (Odoo).
        vendus = {ligne['product_name']: ligne['quantity']
                  for categorie in donnees['products'] for ligne in categorie['products']}
        self.assertEqual(vendus, {"Castel": 3.0, "Poulet DG": 1.0})

    def test_une_quantite_decimale_s_ecrit_a_la_francaise(self):
        """Revue de 6a, constat 9 : 1,5 (et non « 1.5 ») ; 2 (et non « 2.0 ») ;
        1 000 avec le séparateur des milliers de la langue."""
        self.env['res.lang']._activate_lang('fr_FR')
        Rapport = self.env['report.point_of_sale.report_saledetails']
        francais = Rapport.with_context(lang='fr_FR')
        separateur = self.env['res.lang']._lang_get('fr_FR').thousands_sep
        self.assertEqual([francais._aite_quantite_texte(q) for q in (1.5, 2.0, 0.25, 1000.0)],
                         ["1,5", "2", "0,25", "1%s000" % separateur])
        self.assertEqual(Rapport.with_context(lang='en_US')._aite_quantite_texte(1.5), "1.5")

    def test_le_manager_ouvre_le_rapport_de_session(self):
        """Revue de 6a, constat 2 : le compte du manager (partie 4.4, avec le
        droit Facturation : décision à faire valider par AITE) ouvre le
        rapport de session d'une session qui a des ventes payées, et
        « Détails des ventes » de la période."""
        self._journee()
        self.assertTrue(self.compte_manager.has_group('account.group_account_invoice'))
        html, _format = self.env['ir.actions.report'].with_user(
            self.compte_manager)._render_qweb_html(
                'point_of_sale.sale_details_report', self.session.ids)
        self.assertIn('id="aite_restaurant"', html.decode())
        donnees = self.env['report.point_of_sale.report_saledetails'].with_user(
            self.compte_manager).get_sale_details(False, False, False, self.session.ids)
        self.assertEqual(donnees['aite_tables'], 2)

    def test_sans_facturation_odoo_refuse_le_rapport_de_session(self):
        """Pourquoi ce droit : dès qu'une session a une vente payée,
        get_sale_details d'Odoo lit les paiements comptables
        (account.payment, point_of_sale/models/report_sale_details.py) ; un
        Administrateur du Point de Vente avec Employés « Agent », sans le droit
        Facturation, reçoit une erreur d'accès. Si une version d'Odoo lève
        cette limite, ce test le dira : le droit ne sera plus nécessaire."""
        self._journee()
        sans_facturation = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': "Manager sans Facturation", 'login': 'aite_manager_sans_facturation',
            'company_id': self.company.id, 'company_ids': [(6, 0, self.company.ids)],
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('point_of_sale.group_pos_manager').id,
                self.env.ref('hr.group_hr_user').id,
            ])],
        })
        with self.assertRaises(AccessError):
            self.env['ir.actions.report'].with_user(sans_facturation)._render_qweb_html(
                'point_of_sale.sale_details_report', self.session.ids)

    def test_par_dates_et_par_caisse(self):
        """« Détails des ventes » de la gestion (période, caisses) : les mêmes
        additions, les annulations de la période."""
        self._journee()
        debut = fields.Datetime.to_string(fields.Datetime.now().replace(hour=0, minute=0, second=0))
        fin = fields.Datetime.to_string(fields.Datetime.now().replace(hour=23, minute=59, second=59))
        donnees = self.env['report.point_of_sale.report_saledetails'].with_user(
            self.compte_manager).get_sale_details(debut, fin, [self.config.id], False)
        self.assertEqual((donnees['aite_tables'], donnees['aite_personnes'],
                          donnees['aite_sans_table']), (2, 6, 1))
        self.assertEqual(len(donnees['aite_annulations']), 2)

    def test_le_rapport_imprime_depuis_la_gestion(self):
        """Le rapport de session (point_of_sale.pos_session_sales_details) :
        une partie « Tables et personnes » et la liste des annulations, que le
        chef de salle signe."""
        self._journee()
        html, _format = self.env['ir.actions.report'].with_user(
            self.compte_manager)._render_qweb_html(
                'point_of_sale.sale_details_report', self.session.ids)
        page = etree.fromstring(html, etree.HTMLParser())
        bloc = page.xpath("//div[@id='aite_restaurant']")
        self.assertEqual(len(bloc), 1)
        texte = ' '.join(' '.join(bloc[0].itertext()).split())
        for attendu in ("Tables et personnes", "Nombre de tables 2", "Nombre de personnes 6",
                        "Ventes sans table 1", "Annulations", "Erreur de saisie", "Paul",
                        "Retrait sans code", "Total"):
            with self.subTest(attendu=attendu):
                self.assertIn(attendu, texte)

    def test_une_caisse_hors_service_a_table_n_a_pas_ce_bloc(self):
        """Une caisse dont la case est décochée (bar, boutique) : le rapport
        d'Odoo, sans tables ni annulations."""
        temoin = self.env['pos.config'].create({
            'name': "Bar témoin", 'module_pos_restaurant': True, 'module_pos_hr': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces témoin",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse témoin", 'type': 'cash', 'code': 'CTEMO'}).id,
            }).ids)],
        })
        session = self._ouvrir_session(temoin)
        donnees = self.env['report.point_of_sale.report_saledetails'].get_sale_details(
            False, False, False, session.ids)
        self.assertFalse(donnees['aite_restaurant'])
        html, _format = self.env['ir.actions.report']._render_qweb_html(
            'point_of_sale.sale_details_report', session.ids)
        self.assertNotIn('aite_restaurant', str(html))

    def test_le_rapport_par_employe_de_pos_hr(self):
        """Revue de 6a, constat 3 : le rapport par employé de pos_hr (coché
        d'office dans l'assistant de la session) garde le rapport d'Odoo. Son
        gabarit pose les variables une à une, sans les nôtres :
        get_sale_details garde ses arguments et ne pose pas le bloc du
        restaurant (la spécification ne demande rien par employé)."""
        self._journee()
        Rapport = self.env['report.pos_hr.single_employee_sales_report']
        carine = Rapport.get_sale_details(False, False, False, self.session.ids,
                                          self.carine.id)
        self.assertEqual(carine['employee_name'], "Carine")
        self.assertFalse(carine.get('aite_restaurant'))
        self.assertNotIn('aite_annulations', carine)
        donnees = {'date_start': False, 'date_stop': False, 'config_ids': self.config.ids,
                   'session_ids': self.session.ids,
                   'employee_ids': (self.carine | self.awa).ids}
        # Le gabarit de pos_hr porte un t-key que la gestion ne connaît pas
        # (avertissement d'Odoo, sans rapport avec ce module).
        with mute_logger('odoo.addons.base.models.ir_qweb'):
            html, _format = self.env['ir.actions.report'].with_user(
                self.compte_manager)._render_qweb_html(
                    'pos_hr.multi_employee_sales_report_action', [], data=donnees)
        page = ' '.join(etree.fromstring(html, etree.HTMLParser()).itertext())
        self.assertIn("Carine", page)
        self.assertNotIn("Tables et personnes", page)
        # Le rapport de la session, lui, a le bloc.
        self.assertTrue(self.env['report.point_of_sale.report_saledetails'].get_sale_details(
            False, False, False, self.session.ids)['aite_restaurant'])
