# -*- coding: utf-8 -*-
"""Recette : une fois la carte posée, les produits appartiennent au client.

Le client (base de production du restaurant Le Messager) corrige ses produits
— à la main ou par un import Excel (colonne « id » =
__aite_messager__.produit_<clé>) — puis met souvent le module à niveau, à
chaque livraison. Une mise à niveau (ou le menu « Poser la carte Le
Messager ») rejoue data/carte.py : elle ne doit plus jamais remettre un nom,
un prix, un coût, une famille, ni retirer de la caisse un produit ajouté par
le client, ni faire revenir un produit qu'il a archivé, retiré ou supprimé.
"""
import ast
import json
import os
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged

CLE_PARAMETRE = 'aite_resto_carte_messager.elements_poses'


CHEMIN_CARTE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'carte.py')


def _carte_du_script():
    """PLATS et BOISSONS de data/carte.py, lus sans jouer le script."""
    chemin = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'carte.py')
    with open(chemin, encoding='utf-8') as fichier:
        arbre = ast.parse(fichier.read())
    utiles = ('A_VALIDER', 'HORS_CARTE', 'COUT_ESTIME', 'PLATS', 'BOISSONS')
    noeuds = [n for n in arbre.body if isinstance(n, ast.Assign)
              and any(isinstance(c, ast.Name) and c.id in utiles for c in n.targets)]
    contexte = {}
    exec(compile(ast.Module(body=noeuds, type_ignores=[]), chemin, 'exec'), contexte)  # noqa: S102
    return contexte['PLATS'], contexte['BOISSONS']


@tagged('post_install', '-at_install', 'aite_carte_messager')
class TestCarteDuClient(TransactionCase):

    def _produit(self, cle):
        return self.env.ref('__aite_messager__.produit_' + cle)

    def _famille(self, nom):
        return self.env['pos.category'].search([('name', '=', nom)], limit=1)

    def _categorie(self, nom):
        return self.env['product.category'].search([('name', '=', nom)], limit=1)

    def _mettre_a_niveau(self):
        """Ce que fait la mise à niveau du module (data/carte_data.xml)."""
        return "\n".join(self.env['pos.config']._aite_poser_carte_messager())

    def _jouer_version_suivante(self, remplacements, mode_module=True):
        """Joue data/carte.py modifié comme le serait une version suivante du
        module (``remplacements`` : [(ancien texte, nouveau texte)])."""
        with open(CHEMIN_CARTE, encoding='utf-8') as fichier:
            source = fichier.read()
        for ancien, nouveau in remplacements:
            self.assertIn(ancien, source)
            source = source.replace(ancien, nouveau, 1)
        contexte = {'env': self.env(su=True), 'MODE_MODULE': mode_module,
                    '__name__': 'aite_resto_carte_messager.carte'}
        exec(compile(source, CHEMIN_CARTE, 'exec'), contexte)  # noqa: S102
        return contexte

    def _base_posee_en_1_3_4(self):
        """Ce qu'avait une base posée en 18.0.1.3.4 : les identifiants des
        produits seulement (ni registre, ni identifiant de famille, de
        catégorie ou d'accompagnement)."""
        self.env['ir.config_parameter'].sudo().search([('key', '=', CLE_PARAMETRE)]).unlink()
        self.env['ir.model.data'].sudo().search([
            ('module', '=', '__aite_messager__'),
            ('model', '!=', 'product.template')]).unlink()

    # Une version suivante du module : une boisson dans une famille existante,
    # une nouvelle famille avec un produit, un nouvel accompagnement.
    LIMONADE = ("\nBOISSONS = [\n",
                "\nBOISSONS = [\n    (\"limonade_maison\", \"Limonade maison\", \"Sodas\", 1500, "
                "500, False, 0, None),\n")
    AJOUTS = [
        LIMONADE,
        ("\nBOISSONS = [\n",
         "\nBOISSONS = [\n    (\"virgin_mojito\", \"Virgin mojito\", \"Cocktails\", 3000, "
         "900, False, 0, None),\n"),
        ('("Sans alcool", [("Eaux", []),', '("Sans alcool", [("Cocktails", []), ("Eaux", []),'),
        ('\nACCOMPAGNEMENTS = ["Riz nature", "Riz Messager", "Frites plantain", "Frites pomme"]',
         '\nACCOMPAGNEMENTS = ["Riz nature", "Riz Messager", "Frites plantain", "Frites pomme", '
         '"Plantain mûr"]'),
    ]

    # ------------------------------------------------------------------
    # Base neuve : la carte complète est posée comme avant
    # ------------------------------------------------------------------

    def test_base_neuve_carte_complete(self):
        """L'installation a posé les 101 produits aux valeurs du script."""
        plats, boissons = _carte_du_script()
        self.assertEqual(len(plats) + len(boissons), 101)
        for cle, nom, famille, prix, *_reste in plats:
            produit = self._produit(cle)
            self.assertEqual((produit.name, produit.list_price, produit.pos_categ_ids.mapped('name'),
                              produit.categ_id.name, produit.available_in_pos, produit.active),
                             (nom, prix, [famille], famille, True, True), cle)
            self.assertFalse(produit.standard_price, "aucun coût inventé pour un plat : %s" % cle)
            self.assertFalse(produit.taxes_id, cle)
        for cle, nom, famille, prix, cout, suivi, depart, _note in boissons:
            produit = self._produit(cle)
            self.assertEqual((produit.name, produit.list_price, produit.standard_price,
                              produit.pos_categ_ids.mapped('name'), produit.is_storable,
                              produit.available_in_pos),
                             (nom, prix, cout, [famille], suivi, True), cle)
            if suivi:
                self.assertEqual(produit.qty_available, depart, cle)
        poulet = self._produit('poulet_dg')
        self.assertEqual(poulet.attribute_line_ids.value_ids.mapped('name'),
                         ["Riz nature", "Riz Messager", "Frites plantain", "Frites pomme"])
        self.assertTrue(self.env['ir.config_parameter'].sudo().get_param(CLE_PARAMETRE),
                        "la base retient ce que la carte a déjà posé")

    # ------------------------------------------------------------------
    # Les corrections du client restent
    # ------------------------------------------------------------------

    def _corriger(self):
        """Ce que fait le client (à la main ou par l'import Excel validé)."""
        medoc = self._produit('medoc')
        medoc.write({
            'name': "Médoc Château Larose 75 cl", 'list_price': 22000, 'standard_price': 10200,
            'pos_categ_ids': [(6, 0, self._famille("Vins blancs").ids)],
            'categ_id': self._categorie("Vins blancs").id,
            'description': "<p>Prix validé par le gérant le 20/11/2026.</p>",
            'is_storable': True,
        })
        poulet = self._produit('poulet_dg')
        poulet.write({'list_price': 5500, 'name': "Poulet DG maison",
                      'pos_categ_ids': [(6, 0, self._famille("Plats chauds").ids)]})
        return medoc, poulet

    def _verifier(self, medoc, poulet):
        self.assertEqual((medoc.name, medoc.list_price, medoc.standard_price),
                         ("Médoc Château Larose 75 cl", 22000, 10200))
        self.assertEqual(medoc.pos_categ_ids, self._famille("Vins blancs"))
        self.assertEqual(medoc.categ_id, self._categorie("Vins blancs"))
        self.assertIn("validé par le gérant", medoc.description)
        self.assertEqual((poulet.name, poulet.list_price), ("Poulet DG maison", 5500))
        self.assertEqual(poulet.pos_categ_ids, self._famille("Plats chauds"))
        Produits = self.env['product.template'].with_context(active_test=False)
        self.assertFalse(Produits.search_count([('name', 'in', ("Médoc", "Poulet DG"))]),
                         "un produit renommé n'est pas recréé sous son ancien nom")

    def test_mise_a_niveau_garde_les_corrections_du_client(self):
        medoc, poulet = self._corriger()
        avant = self.env['product.template'].with_context(active_test=False).search_count([])
        bilan = self._mettre_a_niveau()
        self._verifier(medoc, poulet)
        self.assertEqual(self.env['product.template'].with_context(active_test=False).search_count([]),
                         avant, "rien n'est créé")
        self.assertNotIn("remis", bilan)

    def test_base_posee_avant_le_registre(self):
        """Base posée en 18.0.1.3.4 (sans le registre de ce qui a été posé) :
        la première mise à niveau en 18.0.1.3.5 garde déjà les corrections."""
        self.env['ir.config_parameter'].sudo().search([('key', '=', CLE_PARAMETRE)]).unlink()
        medoc, poulet = self._corriger()
        self._mettre_a_niveau()
        self._verifier(medoc, poulet)

    def test_taxe_posee_par_le_client_reste(self):
        taxe = self.env['account.tax'].create({'name': "TVA test 19,25 %", 'amount': 19.25,
                                               'type_tax_use': 'sale'})
        biere = self._produit('biere_blonde_65_cl')
        biere.taxes_id = [(6, 0, taxe.ids)]
        self._mettre_a_niveau()
        self.assertEqual(biere.taxes_id, taxe)

    # ------------------------------------------------------------------
    # Les produits ajoutés par le client restent en caisse
    # ------------------------------------------------------------------

    def test_produit_ajoute_par_le_client_reste_en_caisse(self):
        mutzig = self.env['product.template'].create({
            'name': "Mützig 65 cl", 'available_in_pos': True, 'list_price': 1500,
            'pos_categ_ids': [(6, 0, self._famille("Bières").ids)],
            'categ_id': self._categorie("Bières").id})
        bilan = self._mettre_a_niveau()
        self.assertTrue(mutzig.available_in_pos, "le produit du client reste en caisse")
        self.assertNotIn("retiré", bilan)

    def test_castel_du_client_ne_bloque_pas(self):
        """Le client ajoute « Castel 65 cl » à ses bières (vendue partout à
        Douala) : la mise à niveau suivante ne prend pas sa base pour une
        « autre carte »."""
        castel = self.env['product.template'].create({
            'name': "Castel 65 cl", 'available_in_pos': True, 'list_price': 1500,
            'pos_categ_ids': [(6, 0, self._famille("Bières").ids)]})
        bilan = self._mettre_a_niveau()
        self.assertNotIn("n'est pas posée", bilan)
        self.assertIn("Carte posée", bilan)
        self.assertTrue(castel.available_in_pos)

    # ------------------------------------------------------------------
    # Ce que le client a retiré ne revient pas
    # ------------------------------------------------------------------

    def test_produit_archive_retire_ou_supprime_ne_revient_pas(self):
        gambas = self._produit('gambas')
        gambas.active = False
        crevettes = self._produit('crevettes')
        crevettes.available_in_pos = False
        self._produit('acai_bowl').unlink()
        Produits = self.env['product.template'].with_context(active_test=False)
        avant = Produits.search_count([])
        self._mettre_a_niveau()
        self.assertFalse(gambas.active, "un produit archivé par le client reste archivé")
        self.assertFalse(crevettes.available_in_pos, "un produit retiré de la caisse n'y revient pas")
        self.assertFalse(Produits.search_count([('name', '=', "Açaï Bowl")]),
                         "un produit supprimé par le client n'est pas recréé")
        self.assertEqual(Produits.search_count([]), avant)

    def test_nouveau_produit_d_une_version_suivante(self):
        """Un produit que la base n'a jamais reçu (ajouté au script dans une
        version suivante du module) est posé à la mise à niveau, aux valeurs
        du script, en caisse."""
        self._produit('the').unlink()
        parametre = self.env['ir.config_parameter'].sudo()
        recus = set(json.loads(parametre.get_param(CLE_PARAMETRE))) - {'produit:the'}
        parametre.set_param(CLE_PARAMETRE, json.dumps(sorted(recus)))
        bilan = self._mettre_a_niveau()
        the = self._produit('the')
        self.assertEqual((the.name, the.list_price, the.standard_price, the.available_in_pos),
                         ("Thé", 1000, 200, True))
        self.assertEqual(the.pos_categ_ids, self._famille("Café & thé"))
        self.assertIn("Créés cette fois : 1 produit", bilan)
        self.assertIn('produit:the', json.loads(parametre.get_param(CLE_PARAMETRE)))

    def test_base_1_3_4_recoit_les_ajouts_d_une_version_suivante(self):
        """Une base posée en 1.3.4 qui saute une livraison et passe directement
        à une version qui ajoute des produits, une famille, un accompagnement :
        elle les reçoit (seule la carte de la 1.3.4 est réputée reçue), et ce
        que le client a supprimé ne revient pas."""
        self._produit('acai_bowl').unlink()
        self._base_posee_en_1_3_4()
        self._jouer_version_suivante(self.AJOUTS)
        limonade = self.env.ref('__aite_messager__.produit_limonade_maison')
        self.assertEqual((limonade.list_price, limonade.pos_categ_ids, limonade.available_in_pos),
                         (1500, self._famille("Sodas"), True))
        mojito = self.env.ref('__aite_messager__.produit_virgin_mojito')
        self.assertEqual(mojito.pos_categ_ids.mapped('display_name'), ["Bar / Sans alcool / Cocktails"])
        self.assertIn("Plantain mûr",
                      self.env.ref('__aite_messager__.attribut_accompagnement').value_ids.mapped('name'))
        Produits = self.env['product.template'].with_context(active_test=False)
        self.assertFalse(Produits.search_count([('name', '=', "Açaï Bowl")]),
                         "un produit de la 1.3.4 supprimé par le client n'est pas recréé")
        self.assertIn('produit:limonade_maison',
                      json.loads(self.env['ir.config_parameter'].sudo().get_param(CLE_PARAMETRE)))

    def test_base_1_3_4_famille_parente_renommee(self):
        """Base 1.3.4 dont le client a renommé « Sans alcool » : ses
        sous-familles (sans identifiant en 1.3.4) sont retrouvées par leur
        nom, rien n'est recréé, un nouveau produit va dans sa sous-famille."""
        sans_alcool = self._famille("Sans alcool")
        sans_alcool.name = "Boissons fraîches"
        sodas = self._famille("Sodas")
        self._base_posee_en_1_3_4()
        familles = self.env['pos.category'].search_count([])
        self._jouer_version_suivante([self.LIMONADE])
        self.assertEqual(self.env.ref('__aite_messager__.famille_sodas'), sodas)
        self.assertEqual(sans_alcool.name, "Boissons fraîches")
        self.assertEqual(self.env['pos.category'].search_count([]), familles,
                         "ni « Sans alcool » ni ses sous-familles ne sont recréées")
        limonade = self.env.ref('__aite_messager__.produit_limonade_maison')
        self.assertEqual(limonade.pos_categ_ids, sodas)

    def test_graine_famille_renommee_reprend_son_nom(self):
        """Graine (odoo-bin shell, base de développement) : une famille
        renommée reprend le nom du script — pas de famille en double — et les
        produits ajoutés dedans quittent la caisse."""
        bieres = self._famille("Bières")
        bieres.name = "Nos bières"
        mutzig = self.env['product.template'].create({
            'name': "Mützig 65 cl", 'available_in_pos': True, 'list_price': 1500,
            'pos_categ_ids': [(6, 0, bieres.ids)]})
        with patch.object(self.env.cr, 'commit', lambda: None):
            self._jouer_version_suivante([], mode_module=False)
        self.assertEqual(bieres.name, "Bières")
        self.assertEqual(self.env['pos.category'].search_count([('name', 'in', ("Bières", "Nos bières"))]), 1)
        self.assertFalse(mutzig.available_in_pos, "la graine retire de la caisse ce qui n'est pas au script")

    def test_accompagnement_retire_par_le_client(self):
        poulet = self._produit('poulet_dg')
        poulet.attribute_line_ids.unlink()
        self._mettre_a_niveau()
        self.assertFalse(poulet.attribute_line_ids, "l'accompagnement retiré n'est pas remis")

    # ------------------------------------------------------------------
    # Familles, catégories : créer ce qui manque, jamais renommer ni re-ranger
    # ------------------------------------------------------------------

    def test_famille_renommee_par_le_client(self):
        bieres = self._famille("Bières")
        bieres.name = "Bières locales"
        categorie = self._categorie("Bières")
        categorie.name = "Bières locales"
        familles = self.env['pos.category'].search_count([])
        categories = self.env['product.category'].search_count([])
        self._mettre_a_niveau()
        self.assertEqual(bieres.name, "Bières locales")
        self.assertEqual(self.env['pos.category'].search_count([]), familles,
                         "la famille renommée n'est pas recréée sous l'ancien nom")
        self.assertEqual(self.env['product.category'].search_count([]), categories)

    def test_famille_rangee_par_le_client(self):
        whisky = self._famille("Whisky")
        whisky.write({'parent_id': False, 'sequence': 1})
        self._mettre_a_niveau()
        self.assertFalse(whisky.parent_id, "la famille re-rangée par le client reste à sa place")
        self.assertEqual(self.env['pos.category'].search_count([('name', '=', "Whisky")]), 1)

    def test_methode_de_cout_choisie_par_le_client(self):
        whisky = self._categorie("Whisky")
        whisky.property_cost_method = 'standard'
        self._mettre_a_niveau()
        self.assertEqual(whisky.property_cost_method, 'standard')

    # ------------------------------------------------------------------
    # Le bilan reste lisible
    # ------------------------------------------------------------------

    def test_bilan_dit_que_les_produits_sont_au_client(self):
        self._corriger()
        message = self.env['pos.config']._aite_action_poser_carte_messager()['params']['message']
        self.assertIn("Carte posée : 101 produits en", message)
        self.assertIn("Rien n'a été créé en double.", message)
        self.assertIn("ne modifie aucun de vos produits", message)
        for technique in ("seed", "OK", "créés :", "|", "attendus", "remis", "retiré"):
            self.assertNotIn(technique, message)

    # ------------------------------------------------------------------
    # L'addition groupée par famille (aite_pos_restaurant 18.0.1.0.14)
    # ------------------------------------------------------------------

    def _caisse(self):
        return self.env['pos.config'].search([('aite_mode_restaurant', '=', True)], order='id', limit=1)

    def test_addition_groupee_par_famille_cochee(self):
        """La carte coche « Grouper les produits par famille sur l'addition
        et le ticket » sur la caisse du restaurant, et le retient."""
        self.assertTrue(self._caisse().aite_grouper_familles)
        registre = json.loads(self.env['ir.config_parameter'].sudo().get_param(CLE_PARAMETRE))
        self.assertIn('reglage:grouper_familles', registre)

    def test_addition_groupee_choix_du_client_garde(self):
        """Le client décoche le réglage : une mise à niveau ne le recoche pas."""
        caisse = self._caisse()
        caisse.aite_grouper_familles = False
        self._mettre_a_niveau()
        self.assertFalse(caisse.aite_grouper_familles)

    def test_addition_groupee_base_posee_avant(self):
        """Une base posée avant 18.0.1.3.6 (le registre ne connaît pas le
        réglage) : la mise à niveau le coche une fois."""
        caisse = self._caisse()
        caisse.aite_grouper_familles = False
        parametre = self.env['ir.config_parameter'].sudo()
        registre = [e for e in json.loads(parametre.get_param(CLE_PARAMETRE))
                    if e != 'reglage:grouper_familles']
        parametre.set_param(CLE_PARAMETRE, json.dumps(registre))
        self._mettre_a_niveau()
        self.assertTrue(caisse.aite_grouper_familles)
