# -*- coding: utf-8 -*-
"""L'employé dans les analyses AITE (AH-03 ; spécification du restaurant,
partie 5.5).

Toutes les additions d'un restaurant passent sous le même compte Odoo, celui
de la caisse : regrouper par compte ne dit plus qui a vendu. La passerelle
ajoute à l'analyse « Serveur (ouverte par) » — la personne qui a ouvert la
table, le vendeur d'un restaurant, qui n'encaisse pas (Q8, Q49, cas de
recette D12) — et « Encaissée par ». Le compte Odoo reste lisible, sous son
vrai nom (« Compte Odoo »).

Chaque addition passe par le chemin de la caisse (``_commande_caisse``).
"""
from lxml import etree

from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval
from odoo.tools.sql import column_exists

from odoo.addons.aite_pos_restaurant.tests.common import Addition, RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_analytics_hr')
class TestEmployeDansLesAnalyses(RestaurantCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Le lecteur des analyses : profil « Utilisateur — Analyses POS »,
        # sans aucun droit sur les Employés.
        cls.analyste = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': "Analyste du restaurant", 'login': 'aite_analyste_resto',
            'company_id': cls.company.id, 'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('aite_pos_analytics.group_aite_pos_analytics_user').id,
            ])],
        })

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()
        self.especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]
        self.Report = self.env['aite.pos.daily.report'].with_user(self.analyste)

    def _table(self, table, serveur, produit, quantite):
        """Une table ouverte et servie par ``serveur``, encaissée par Carine,
        sous le compte de la caisse."""
        addition = Addition(table, 2, serveur)
        addition.ajouter(produit, quantite)
        addition.envoyer()
        self._commande_caisse(addition, serveur)
        return self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)

    def _par(self, champ, domaine=None):
        lignes = self.Report.read_group(
            [('session_id', '=', self.session.id)] + (domaine or []),
            ['price_subtotal_incl:sum'], [champ])
        return {(ligne[champ] or (False, False))[1]: ligne['price_subtotal_incl']
                for ligne in lignes}

    def test_le_serveur_et_la_caissiere(self):
        """Awa et Moussa ouvrent chacun une table, Carine encaisse les deux,
        sous le même compte de caisse : « Serveur » distingue Awa et Moussa,
        « Encaissée par » donne Carine."""
        awa = self._table(self.table_7, self.awa, self.castel, 2)
        moussa = self._table(self.table_12, self.moussa, self.poulet, 1)
        self.assertEqual(awa.user_id | moussa.user_id, self.compte_caisse)
        self.assertEqual(self._par('serveur_id'), {"Awa": 2000.0, "Moussa": 6500.0})
        self.assertEqual(self._par('encaisse_par_id'), {"Carine": 8500.0})
        self.assertEqual(self._par('user_id'), {"Caisse du restaurant": 8500.0})
        ligne = self.Report.search([('order_id', '=', awa.id)])
        self.assertEqual(ligne.serveur_id.name, "Awa")
        self.assertEqual(ligne.encaisse_par_id.name, "Carine")
        # Les identifiants sont ceux des employés.
        self.assertEqual(ligne.serveur_id.id, self.awa.id)

    def test_une_caisse_sans_service_a_table_garde_l_employe_d_odoo(self):
        """Une caisse à codes hors service à table contrôlé : « Encaissée
        par » est l'employé d'Odoo (pos_hr) ; pas de serveur."""
        temoin = self.env['pos.config'].create({
            'name': "Bar témoin", 'module_pos_restaurant': True, 'module_pos_hr': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces témoin",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse témoin", 'type': 'cash', 'code': 'CTEMO'}).id,
            }).ids)],
        })
        session = self._ouvrir_session(temoin)
        addition = Addition(temoin.floor_ids.table_ids[:1], 2)
        addition.ajouter(self.castel, 3)
        commande = self._commande_caisse(addition, self.carine, etat='paid',
                                         payer=temoin.payment_method_ids, config=temoin)
        self.assertFalse(commande.aite_encaissee_par_id)
        ligne = self.Report.search([('order_id', '=', commande.id)])
        self.assertEqual(ligne.session_id, session)
        self.assertEqual((ligne.serveur_id.id, ligne.encaisse_par_id.id), (False, self.carine.id))

    def test_libelles_recherche_et_regroupements(self):
        champs = self.Report.fields_get(['serveur_id', 'encaisse_par_id', 'user_id'])
        self.assertEqual((champs['serveur_id']['string'], champs['serveur_id']['relation']),
                         ("Serveur (ouverte par)", 'hr.employee.public'))
        self.assertEqual((champs['encaisse_par_id']['string'],
                          champs['encaisse_par_id']['relation']),
                         ("Encaissée par", 'hr.employee.public'))
        self.assertEqual(champs['user_id']['string'], "Compte Odoo")
        vue = etree.fromstring(self.Report.get_views([(False, 'search')])['views']['search'][
            'arch'])
        self.assertEqual(vue.xpath("//field[@name='serveur_id']/@string"), ["Serveur"])
        self.assertTrue(vue.xpath("//field[@name='encaisse_par_id']"))
        groupes = {f.get('name'): (f.get('string'), safe_eval(f.get('context')).get('group_by'))
                   for f in vue.xpath("//filter[@context]")}
        self.assertEqual(groupes['grp_serveur'], ("Serveur", 'serveur_id'))
        self.assertEqual(groupes['grp_encaisse_par'], ("Encaissée par", 'encaisse_par_id'))
        self.assertEqual(groupes['grp_user'], ("Compte Odoo", 'user_id'))

    def test_la_passerelle_s_installe_seule_avec_le_restaurant(self):
        module = self.env['ir.module.module'].search([('name', '=', 'aite_pos_analytics_hr')])
        self.assertTrue(module.auto_install)
        self.assertEqual(set(module.dependencies_id.mapped('name')),
                         {'aite_pos_analytics', 'aite_pos_restaurant'})
        colonnes = self.env['aite.pos.daily.report']._aite_colonnes_supplementaires()
        self.assertIn('serveur_id', colonnes)
        self.assertIn('encaisse_par_id', colonnes)

    def test_desinstaller_la_passerelle_garde_l_analyse(self):
        """Désinstallée, la passerelle recrée la vue sans ses colonnes : la
        suppression des champs du restaurant (``DROP COLUMN … CASCADE``)
        n'emporte plus la vue de l'analyse AITE."""
        from odoo.addons.aite_pos_analytics_hr import uninstall_hook
        self._table(self.table_7, self.awa, self.castel, 2)
        self.env.flush_all()
        uninstall_hook(self.env)
        cr = self.env.cr
        self.assertFalse(column_exists(cr, 'aite_pos_daily_report', 'serveur_id'))
        self.assertTrue(column_exists(cr, 'aite_pos_daily_report', 'famille_n1_id'))
        cr.execute("SAVEPOINT aite_colonne")
        cr.execute("ALTER TABLE pos_order DROP COLUMN aite_ouverte_par_id CASCADE")
        cr.execute("SELECT count(*) FROM aite_pos_daily_report WHERE session_id = %s",
                   [self.session.id])
        self.assertEqual(cr.fetchone()[0], 1)
        cr.execute("ROLLBACK TO SAVEPOINT aite_colonne")

    def test_desinstaller_la_passerelle_garde_les_colonnes_des_autres(self):
        """Revue de 6a, constat 8 : désinstallée, la passerelle ne retire de la
        vue que ses propres colonnes ; celles qu'un autre module ajoute par le
        même point d'extension (simulé ici sur le module d'analyse) restent."""
        from unittest.mock import patch

        from odoo.addons.aite_pos_analytics.models.pos_analytics_report import (
            PosDailyReport as Analyse)
        from odoo.addons.aite_pos_analytics_hr import uninstall_hook
        with patch.object(Analyse, '_aite_colonnes_supplementaires',
                          lambda self: ", 1 AS aite_autre_colonne"):
            self.assertIn('serveur_id',
                          self.env['aite.pos.daily.report']._aite_colonnes_supplementaires())
            uninstall_hook(self.env)
        cr = self.env.cr
        self.assertTrue(column_exists(cr, 'aite_pos_daily_report', 'aite_autre_colonne'))
        self.assertFalse(column_exists(cr, 'aite_pos_daily_report', 'serveur_id'))
        self.assertFalse(column_exists(cr, 'aite_pos_daily_report', 'encaisse_par_id'))
        self.assertTrue(column_exists(cr, 'aite_pos_daily_report', 'famille_n1_id'))
