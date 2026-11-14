# -*- coding: utf-8 -*-
"""Les ventes par famille, sous-famille et sous-sous-famille (REST-23-P1 ;
spécification du restaurant, partie 5.4).

Les familles sont les catégories de caisse (celles de l'écran de commande) :
une catégorie sans parent est une famille ; ses enfants, des sous-familles ;
leurs enfants, des sous-sous-familles. Un article rangé plus bas compte sous
son ancêtre de troisième niveau ; un article rangé dans plusieurs catégories
ne compte que dans la première (ordre de la caisse : séquence, nom) ; un
article sans catégorie de caisse garde ses ventes, sans famille. La somme des
sous-totaux d'un niveau est toujours le total.

Le rapport d'avant ne change pas : le tableau croisé s'ouvre toujours par
catégorie de produit ; les familles s'ajoutent à la recherche et aux
regroupements (une base hôtelière sans restaurant garde ses rapports).
"""
from lxml import etree

from odoo.tests import tagged
from odoo.tools.safe_eval import safe_eval

from .common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosFamilles(PosAnalyticsCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Famille = cls.env['pos.category']
        cls.boissons = Famille.create({'name': "Boissons (familles)", 'sequence': 1})
        cls.alcool = Famille.create({'name': "Alcoolisé (familles)", 'parent_id': cls.boissons.id})
        cls.bieres = Famille.create({'name': "Bières (familles)", 'parent_id': cls.alcool.id})
        cls.vins = Famille.create({'name': "Vins (familles)", 'parent_id': cls.alcool.id})
        cls.soft = Famille.create({'name': "Non alcoolisé (familles)",
                                   'parent_id': cls.boissons.id})
        cls.sodas = Famille.create({'name': "Sodas (familles)", 'parent_id': cls.soft.id,
                                    'sequence': 1})
        cls.blondes = Famille.create({'name': "Blondes (familles)", 'parent_id': cls.bieres.id})
        cls.plats = Famille.create({'name': "Plats (familles)", 'sequence': 2})

        def article(nom, prix, familles):
            return cls.env['product.product'].create({
                'name': nom, 'type': 'consu', 'available_in_pos': True,
                'categ_id': cls.categ.id, 'list_price': prix, 'standard_price': prix / 2,
                'taxes_id': [(5, 0, 0)], 'pos_categ_ids': [(6, 0, familles.ids)]})

        cls.biere = article("Bière (familles)", 1000.0, cls.bieres)
        cls.vin = article("Vin (familles)", 8000.0, cls.vins)
        cls.soda = article("Soda (familles)", 500.0, cls.sodas)
        cls.blonde = article("Blonde (familles)", 1200.0, cls.blondes)
        cls.plat = article("Plat (familles)", 6500.0, cls.plats)
        cls.cafe = article("Café (familles)", 300.0, cls.env['pos.category'])
        # Rangé dans deux familles : la première est « Sodas » (séquence 1),
        # avant « Plats » (séquence 2).
        cls.formule = article("Jus maison (familles)", 700.0, cls.plats | cls.sodas)
        cls.Report = cls.env['aite.pos.daily.report']

    def _ventes(self):
        self._sale([(self.biere, 2, 1000.0), (self.vin, 1, 8000.0), (self.soda, 3, 500.0)])
        self._sale([(self.blonde, 1, 1200.0), (self.plat, 2, 6500.0), (self.cafe, 4, 300.0)])
        self._sale([(self.formule, 1, 700.0)])

    def _domaine(self):
        return [('session_id', '=', self.session.id)]

    def _par(self, champ, domaine=None):
        lignes = self.Report.read_group(self._domaine() + (domaine or []),
                                        ['price_subtotal:sum', 'qty:sum'], [champ])
        return {(ligne[champ] or (False, False))[0]: ligne['price_subtotal'] for ligne in lignes}

    def _total(self):
        return self.Report.read_group(self._domaine(), ['price_subtotal:sum'], [])[0][
            'price_subtotal']

    def test_boissons_additionne_ses_sous_familles(self):
        """REST-23 critère 1 : bières, vins et sodas sous « Boissons »."""
        self._ventes()
        par_famille = self._par('famille_n1_id')
        self.assertEqual(par_famille[self.boissons.id], 2000 + 8000 + 1500 + 1200 + 700)
        par_sous_famille = self._par('famille_n2_id', [('famille_n1_id', '=', self.boissons.id)])
        self.assertEqual(par_sous_famille, {self.alcool.id: 2000 + 8000 + 1200,
                                            self.soft.id: 1500 + 700})
        self.assertEqual(sum(par_sous_famille.values()), par_famille[self.boissons.id])

    def test_la_somme_des_sous_totaux_est_le_total(self):
        """REST-23 critère 4 : chaque article n'est compté qu'une fois, à
        chaque niveau ; ceux qui n'ont pas de famille restent au total."""
        self._ventes()
        total = self._total()
        self.assertEqual(total, 2000 + 8000 + 1500 + 1200 + 13000 + 1200 + 700)
        for champ in ('famille_n1_id', 'famille_n2_id', 'famille_n3_id'):
            with self.subTest(niveau=champ):
                self.assertEqual(sum(self._par(champ).values()), total)
        self.assertEqual(self.Report.search_count(self._domaine()), 7)

    def test_un_article_dans_deux_familles_compte_dans_la_premiere(self):
        self._ventes()
        lignes = self.Report.search(self._domaine() + [('product_id', '=', self.formule.id)])
        self.assertEqual(len(lignes), 1)
        self.assertEqual((lignes.famille_n1_id, lignes.famille_n2_id, lignes.famille_n3_id),
                         (self.boissons, self.soft, self.sodas))
        self.assertEqual(self._par('famille_n1_id')[self.plats.id], 13000)

    def test_un_article_au_quatrieme_niveau_compte_sous_son_ancetre(self):
        self._ventes()
        ligne = self.Report.search(self._domaine() + [('product_id', '=', self.blonde.id)])
        self.assertEqual((ligne.famille_n1_id, ligne.famille_n2_id, ligne.famille_n3_id),
                         (self.boissons, self.alcool, self.bieres))

    def test_une_famille_sans_parent_et_un_article_sans_famille(self):
        """« Plats » n'a pas de parent : c'est une famille, sans sous-famille.
        Le café n'a pas de catégorie de caisse : ses ventes restent, sans
        famille."""
        self._ventes()
        plat = self.Report.search(self._domaine() + [('product_id', '=', self.plat.id)])
        self.assertEqual((plat.famille_n1_id, plat.famille_n2_id, plat.famille_n3_id),
                         (self.plats, self.env['pos.category'], self.env['pos.category']))
        cafe = self.Report.search(self._domaine() + [('product_id', '=', self.cafe.id)])
        self.assertEqual(len(cafe), 1)
        self.assertFalse(cafe.famille_n1_id | cafe.famille_n2_id | cafe.famille_n3_id)
        self.assertEqual(cafe.price_subtotal, 1200)
        self.assertEqual(self._par('famille_n1_id')[False], 1200)

    def _recherche_famille(self, valeur, choisie=False):
        """Le champ « Famille » de la recherche : le texte tapé (« Rechercher
        Famille pour : … »), ou une famille choisie dans la liste (Odoo
        remplace alors « ilike » par « = », raw_value = son identifiant)."""
        vue = self.Report.get_views([(False, 'search')])['views']['search']['arch']
        champs = etree.fromstring(vue).xpath("//field[@string='Famille']")
        self.assertEqual(len(champs), 1)
        filtre = champs[0].get('filter_domain')
        if choisie:
            filtre = filtre.replace("'ilike'", "'='")
        domaine = safe_eval(filtre, {'self': str(valeur), 'raw_value': valeur})
        return self.Report.search(self._domaine() + domaine).product_id

    def test_le_champ_famille_trouve_une_famille_a_tout_niveau(self):
        """Le manager tape « Non alcoolisé » ou « Bières » sans savoir à quel
        niveau la famille se trouve (REST-23 critère 2)."""
        self._ventes()
        self.assertEqual(self._recherche_famille("Non alcoolisé (familles)"),
                         self.soda | self.formule)
        self.assertEqual(self._recherche_famille("Bières (familles)"), self.biere | self.blonde)
        self.assertEqual(self._recherche_famille("Boissons (familles)"),
                         self.biere | self.vin | self.soda | self.blonde | self.formule)
        self.assertEqual(self._recherche_famille(self.alcool.id, choisie=True),
                         self.biere | self.vin | self.blonde)

    def test_libelles_et_regroupements(self):
        champs = self.Report.fields_get(['famille_n1_id', 'famille_n2_id', 'famille_n3_id'])
        self.assertEqual([champs[nom]['string'] for nom in (
            'famille_n1_id', 'famille_n2_id', 'famille_n3_id')],
            ["Famille", "Sous-famille", "Sous-sous-famille"])
        self.assertEqual({champs[nom]['relation'] for nom in champs}, {'pos.category'})
        vue = etree.fromstring(self.Report.get_views([(False, 'search')])['views']['search'][
            'arch'])
        groupes = {f.get('name'): (f.get('string'), safe_eval(f.get('context')).get('group_by'))
                   for f in vue.xpath("//filter[@context]")}
        self.assertEqual(groupes['grp_famille'], ("Famille", 'famille_n1_id'))
        self.assertEqual(groupes['grp_sous_famille'], ("Sous-famille", 'famille_n2_id'))
        self.assertEqual(groupes['grp_sous_sous_famille'],
                         ("Sous-sous-famille", 'famille_n3_id'))

    def test_le_rapport_d_avant_ne_change_pas(self):
        """Une base hôtelière sans restaurant garde son rapport : il s'ouvre
        par catégorie de produit, avec les mêmes mesures."""
        action = self.env.ref('aite_pos_analytics.action_pos_daily_report')
        self.assertEqual(safe_eval(action.context), {'group_by': ['categ_id']})
        self.assertEqual(action.view_mode, 'pivot,graph,list')
        pivot = etree.fromstring(self.Report.get_views([(False, 'pivot')])['views']['pivot'][
            'arch'])
        self.assertEqual([(n.get('name'), n.get('type')) for n in pivot.xpath('//field')],
                         [('date', 'row'), ('categ_id', 'col'), ('price_subtotal', 'measure'),
                          ('total_cost', 'measure'), ('margin', 'measure'),
                          ('margin_rate', 'measure')])
        self.assertIsInstance(self.Report._aite_colonnes_supplementaires(), str)

    def test_la_vue_lit_les_ventes_pas_encore_ecrites(self):
        """Vue SQL : les ventes payées encore en mémoire (pas encore écrites
        en base) sont lues (flush du modèle source, règle de CLAUDE.md)."""
        commande = self.env['pos.order'].create({
            'session_id': self.session.id, 'company_id': self.company.id,
            'amount_tax': 0.0, 'amount_total': 3000.0, 'amount_paid': 3000.0,
            'amount_return': 0.0,
            'lines': [(0, 0, {'product_id': self.biere.id, 'qty': 3, 'price_unit': 1000.0,
                              'price_subtotal': 3000.0, 'price_subtotal_incl': 3000.0})],
        })
        self.env.flush_all()
        commande.write({'state': 'paid'})
        regroupe = self.Report.read_group([('order_id', '=', commande.id)],
                                          ['price_subtotal:sum', 'qty:sum'], [])[0]
        self.assertEqual((regroupe['price_subtotal'], regroupe['qty']), (3000.0, 3.0))
        commande.lines.write({'qty': 2, 'price_subtotal': 2000.0})
        self.biere.product_tmpl_id.write({'pos_categ_ids': [(6, 0, self.vins.ids)]})
        lignes = self.Report.search([('order_id', '=', commande.id)])
        self.assertEqual(len(lignes), 1)
        self.assertEqual((lignes.qty, lignes.famille_n3_id), (2.0, self.vins))
