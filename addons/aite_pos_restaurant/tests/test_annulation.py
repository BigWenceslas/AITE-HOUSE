# -*- coding: utf-8 -*-
"""Annuler ce qui est parti : le verrou après envoi, le code d'un responsable
vérifié par le serveur, les motifs, le journal des annulations
(spécification, T9, T14, parties 3.2, 4.2 et 6.2 ; incrément 4).

Règle commune (partie 4.2) : ce qui passe par une requête à nous
(``aite_autoriser_annulation``) est **refusé** avec un message en français ;
ce qui arrive par la synchronisation ou par l'annulation d'addition d'Odoo
n'est **jamais refusé** : c'est tracé au journal (« Retrait sans code »,
« Annulation sans code »).

Chaque addition passe par le chemin de la caisse (``sync_from_ui``, aide
``_commande_caisse``), jamais par un ``create`` direct.
"""
from uuid import uuid4

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import Addition, RestaurantCommon

R8 = ("Ce code ne peut pas annuler. Il faut celui d'un chef de salle, d'un "
      "superviseur ou du manager.")
R24 = "Écrivez en quelques mots pourquoi."
R26 = "Ce produit vient d'être annulé sur un autre poste. Rien n'a changé ici."


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestAnnulation(RestaurantCommon):

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()
        self.Annulation = self.env['aite.restaurant.annulation']
        self.motif_erreur = self.env.ref('aite_pos_restaurant.motif_erreur_saisie')
        self.motif_parti = self.env.ref('aite_pos_restaurant.motif_client_parti')
        self.motif_autre = self.env.ref('aite_pos_restaurant.motif_autre')

    # ------------------------------------------------------------------
    # Aides
    # ------------------------------------------------------------------

    def _table_envoyee(self, quantite=3, produit=None, table=None):
        """Awa ouvre la table 12, saisit ``quantite`` Castel et touche
        « J'envoie »."""
        addition = Addition(table or self.table_12, 4, self.awa)
        self._commande_caisse(addition, self.awa)
        uuid = addition.ajouter(produit or self.castel, quantite)
        addition.envoyer()
        commande = self._commande_caisse(addition, self.awa)
        ligne = commande.lines.filtered(lambda l: l.uuid == uuid)
        self.assertEqual(ligne.aite_qte_envoyee, quantite)
        return addition, commande, ligne

    def _autoriser(self, commandes, lignes, code, motif=None, commentaire=False,
                   demandeur=None, demande=None, nature='produit'):
        """La requête de la fenêtre d'annulation, sous le compte de la
        caisse."""
        return self.env['pos.order'].with_user(self.compte_caisse).aite_autoriser_annulation(
            commandes.ids, lignes, code, (motif or self.motif_erreur).id, commentaire,
            (demandeur or self.awa).id, demande or str(uuid4()), nature)

    def _journal(self, commande=None):
        domaine = [('order_id', '=', commande.id)] if commande else []
        return self.Annulation.search(domaine, order='id')

    def _appliquer(self, addition, uuid, quantite):
        """La caisse applique la baisse autorisée et note ce qui est parti
        pour cette ligne (bon d'annulation), puis synchronise."""
        reste = addition.quantite(uuid) - quantite
        if reste > 0:
            addition.changer(uuid, reste)
            for entree in addition.preparation['lines'].values():
                if entree.get('uuid') == uuid:
                    entree['quantity'] = reste
        else:
            addition.supprimer(uuid)
            addition.preparation['lines'] = {
                cle: entree for cle, entree in addition.preparation['lines'].items()
                if entree.get('uuid') != uuid}
        from odoo import fields
        addition.preparation['metadata'] = {
            'serverDate': fields.Datetime.to_string(fields.Datetime.now())}
        return self._commande_caisse(addition, self.awa)

    # ------------------------------------------------------------------
    # Retrait sans code (synchronisation)
    # ------------------------------------------------------------------

    def test_retrait_sans_code(self):
        """Une baisse sous ce qui est parti, sans autorisation (contournement
        du pavé) : la synchronisation passe, et le serveur la trace."""
        addition, commande, ligne = self._table_envoyee(3)
        uuid = ligne.uuid
        addition.changer(uuid, 2)
        self._commande_caisse(addition, self.awa)
        self.assertEqual(ligne.qty, 2, "la synchronisation n'est jamais refusée")
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        trace = self._journal(commande)
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace.type_annulation, 'retrait_sans_code')
        self.assertFalse(trace.autorisee)
        self.assertEqual(trace.quantite, 1)
        self.assertEqual(trace.produit_id, self.castel)
        self.assertEqual(trace.produit_nom, "Castel")
        self.assertEqual(trace.prix_unitaire, 1000)
        self.assertEqual(trace.montant, 1000)
        self.assertEqual(trace.currency_id, self.company.currency_id)
        self.assertEqual(trace.serveur_id, self.awa)
        self.assertEqual(trace.serveur_nom, "Awa")
        self.assertFalse(trace.superieur_id)
        self.assertFalse(trace.superieur_nom)
        self.assertEqual(trace.table_nom, "12")
        self.assertEqual(trace.ligne_uuid, uuid)
        self.assertEqual(trace.config_id, self.config)
        self.assertEqual(trace.session_id, self.session)
        self.assertEqual(trace.company_id, self.company)

    def test_ligne_envoyee_retiree_sans_code(self):
        addition, commande, ligne = self._table_envoyee(3)
        addition.supprimer(ligne.uuid)
        self._commande_caisse(addition, self.awa)
        trace = self._journal(commande)
        self.assertEqual(trace.mapped('type_annulation'), ['retrait_sans_code'])
        self.assertEqual(trace.quantite, 3)
        self.assertEqual(trace.montant, 3000)
        self.assertEqual(trace.produit_nom, "Castel")

    def test_baisse_de_la_part_non_envoyee_libre(self):
        addition, commande, ligne = self._table_envoyee(3)
        addition.changer(ligne.uuid, 5)
        self._commande_caisse(addition, self.awa)
        addition.changer(ligne.uuid, 3)
        self._commande_caisse(addition, self.awa)
        self.assertFalse(self._journal(commande), "Q34 : ni code ni trace")
        self.assertEqual(ligne.aite_qte_envoyee, 3)

    def test_baisse_pendant_un_deplacement(self):
        addition, commande, ligne = self._table_envoyee(3)
        addition.changer(ligne.uuid, 2)
        addition.preparation['lines'][ligne.uuid]['quantity'] = 2
        self._commande_caisse(addition, self.awa, deplacement=True)
        self.assertFalse(self._journal(commande))
        self.assertEqual(ligne.aite_qte_envoyee, 2)

    # ------------------------------------------------------------------
    # La requête d'autorisation
    # ------------------------------------------------------------------

    def test_code_d_un_serveur_ou_d_une_caissiere_refuse(self):
        _addition, commande, ligne = self._table_envoyee(3)
        for code in ('2222', '3333', '9999', '12', False):
            with self.subTest(code=code):
                reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], code)
                self.assertEqual(reponse, {'erreur': R8})
        self.assertFalse(self._journal())
        self.assertEqual(ligne.aite_qte_envoyee, 3)

    def test_code_d_un_employe_archive_refuse(self):
        _addition, commande, ligne = self._table_envoyee(3)
        self.paul.active = False
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444')
        self.assertEqual(reponse, {'erreur': R8})

    def test_annulation_autorisee(self):
        addition, commande, ligne = self._table_envoyee(3)
        demande = str(uuid4())
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 2}], '4444',
                                  motif=self.motif_parti, demande=demande)
        self.assertEqual(reponse.get('superieur_id'), self.paul.id)
        self.assertEqual(reponse.get('superieur_nom'), "Paul")
        self.assertEqual(ligne.aite_qte_envoyee, 1, "le serveur baisse lui-même le verrou (T9)")
        self.assertEqual(ligne.qty, 3, "la quantité de la ligne est celle de la caisse")
        trace = self._journal(commande)
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace.type_annulation, 'produit')
        self.assertTrue(trace.autorisee)
        self.assertEqual(trace.quantite, 2)
        self.assertEqual(trace.montant, 2000)
        self.assertEqual(trace.serveur_id, self.awa)
        self.assertEqual(trace.serveur_nom, "Awa")
        self.assertEqual(trace.superieur_id, self.paul)
        self.assertEqual(trace.superieur_nom, "Paul")
        self.assertEqual(trace.motif_id, self.motif_parti)
        self.assertEqual(trace.motif_nom, "Client parti")
        self.assertEqual(trace.demande_uuid, demande)
        self.assertEqual(trace.ligne_uuid, ligne.uuid)
        self.assertEqual(trace.order_ref, commande.pos_reference)
        # La caisse applique la baisse : rien de plus au journal.
        self._appliquer(addition, ligne.uuid, 2)
        self.assertEqual(ligne.qty, 1)
        self.assertEqual(ligne.aite_qte_envoyee, 1)
        self.assertEqual(len(self._journal(commande)), 1)

    def test_tout_annuler_puis_retirer_la_ligne(self):
        addition, commande, ligne = self._table_envoyee(2)
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 2}], '4444')
        self.assertNotIn('erreur', reponse)
        self._appliquer(addition, ligne.uuid, 2)
        self.assertFalse(commande.lines)
        self.assertEqual(self._journal(commande).mapped('type_annulation'), ['produit'])

    def test_le_manager_annule(self):
        _addition, commande, ligne = self._table_envoyee(3)
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '5555')
        self.assertEqual(reponse.get('superieur_nom'), "Fanta")

    def test_meme_demande_deux_fois(self):
        """Une réponse perdue puis un nouvel essai, avec la même clé : une
        seule ligne au journal, une seule baisse."""
        _addition, commande, ligne = self._table_envoyee(3)
        demande = str(uuid4())
        lignes = [{'uuid': ligne.uuid, 'quantite': 2}]
        premiere = self._autoriser(commande, lignes, '4444', demande=demande)
        self.assertEqual(premiere.get('quantites'), {ligne.uuid: 2})
        # Renvoyée avec une autre quantité (le poste a perdu la réponse, puis
        # la fenêtre a été rouverte) : la première réponse, et ses quantités,
        # que la caisse applique.
        seconde = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444',
                                  demande=demande)
        self.assertEqual(seconde.get('superieur_id'), premiere.get('superieur_id'))
        self.assertEqual(seconde.get('quantites'), {ligne.uuid: 2})
        self.assertEqual(len(self._journal(commande)), 1)
        self.assertEqual(ligne.aite_qte_envoyee, 1)

    def test_reponse_perdue_la_copie_ne_releve_pas_le_verrou(self):
        """L'annulation est faite sur le serveur, la réponse se perd : le
        poste renvoie l'ancienne quantité (copie en retard). Le verrou ne
        remonte pas ; au nouvel essai, la baisse appliquée ne trace rien."""
        addition, commande, ligne = self._table_envoyee(3)
        demande = str(uuid4())
        lignes = [{'uuid': ligne.uuid, 'quantite': 1}]
        self._autoriser(commande, lignes, '4444', demande=demande)
        # Le poste n'a rien appliqué : il resynchronise sa copie (3, envoyé 3).
        addition.changer(ligne.uuid, 3)
        self._commande_caisse(addition, self.awa)
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        self.assertEqual(len(self._journal(commande)), 1)
        # Nouvel essai (même clé), puis la baisse appliquée.
        self._autoriser(commande, lignes, '4444', demande=demande)
        self._appliquer(addition, ligne.uuid, 1)
        self.assertEqual(ligne.qty, 2)
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        self.assertEqual(self._journal(commande).mapped('type_annulation'), ['produit'])

    def test_plus_que_l_envoye(self):
        _addition, commande, ligne = self._table_envoyee(2)
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 3}], '4444')
        self.assertEqual(reponse, {'erreur': R26})
        self.assertFalse(self._journal())
        self.assertEqual(ligne.aite_qte_envoyee, 2)

    def test_deux_postes_annulent_le_meme_produit(self):
        """Deux postes, deux demandes : la seconde arrive quand le produit
        vient d'être annulé (R26), rien n'est annulé deux fois."""
        _addition, commande, ligne = self._table_envoyee(2)
        lignes = [{'uuid': ligne.uuid, 'quantite': 2}]
        self.assertNotIn('erreur', self._autoriser(commande, lignes, '4444'))
        self.assertEqual(self._autoriser(commande, lignes, '5555'), {'erreur': R26})
        self.assertEqual(len(self._journal(commande)), 1)
        self.assertEqual(ligne.aite_qte_envoyee, 0)

    def test_addition_deja_encaissee(self):
        addition, commande, ligne = self._table_envoyee(2)
        especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]
        self._commande_caisse(addition, self.carine, etat='paid', payer=especes)
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444')
        self.assertEqual(reponse, {'erreur': R26})

    def test_motif_autre_sans_precision(self):
        _addition, commande, ligne = self._table_envoyee(2)
        lignes = [{'uuid': ligne.uuid, 'quantite': 1}]
        for vide in (False, '', '   '):
            with self.subTest(commentaire=vide):
                self.assertEqual(
                    self._autoriser(commande, lignes, '4444', motif=self.motif_autre,
                                    commentaire=vide),
                    {'erreur': R24})
        self.assertFalse(self._journal())
        reponse = self._autoriser(commande, lignes, '4444', motif=self.motif_autre,
                                  commentaire=" Verre cassé ")
        self.assertNotIn('erreur', reponse)
        trace = self._journal(commande)
        self.assertEqual(trace.motif_nom, "Autre")
        self.assertEqual(trace.commentaire, "Verre cassé")

    def test_motif_inconnu_refuse(self):
        _addition, commande, ligne = self._table_envoyee(2)
        reponse = self.env['pos.order'].with_user(self.compte_caisse).aite_autoriser_annulation(
            commande.ids, [{'uuid': ligne.uuid, 'quantite': 1}], '4444', 999999, False,
            self.awa.id, str(uuid4()), 'produit')
        self.assertIn('erreur', reponse)
        self.assertFalse(self._journal())

    def test_motif_archive_pendant_que_la_fenetre_est_ouverte(self):
        """Le manager archive un motif pendant qu'une fenêtre d'annulation
        l'affiche : le chef de salle qui le touche n'est pas refusé."""
        _addition, commande, ligne = self._table_envoyee(2)
        self.motif_parti.active = False
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444',
                                  motif=self.motif_parti)
        self.assertNotIn('erreur', reponse)
        self.assertEqual(self._journal(commande).motif_nom, "Client parti")

    def test_caisse_hors_mode(self):
        temoin = self.env['pos.config'].create({
            'name': "Bar témoin", 'module_pos_restaurant': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces témoin",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse témoin", 'type': 'cash', 'code': 'CTEMA'}).id,
            }).ids)],
        })
        self._ouvrir_session(temoin)
        addition = Addition(temoin.floor_ids.table_ids[:1], 3)
        uuid = addition.ajouter(self.castel, 2)
        addition.envoyer()
        commande = self._commande_caisse(addition, self.awa, config=temoin)
        reponse = self._autoriser(commande, [{'uuid': uuid, 'quantite': 1}], '4444')
        self.assertIn('erreur', reponse)
        commande.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(commande.state, 'cancel')
        self.assertFalse(self._journal(), "une caisse hors mode n'est pas tracée")

    # ------------------------------------------------------------------
    # Annuler une table, les tables à la fermeture
    # ------------------------------------------------------------------

    def _table_deux_produits(self):
        addition = Addition(self.table_12, 4, self.awa)
        castel = addition.ajouter(self.castel, 2)
        poulet = addition.ajouter(self.poulet, 1)
        addition.envoyer()
        addition.ajouter(self.castel, 1)  # saisie, pas envoyée : ni code ni trace
        commande = self._commande_caisse(addition, self.awa)
        return addition, commande, castel, poulet

    def test_annulation_de_l_addition_sans_autorisation(self):
        """« Annuler » d'Odoo sans notre fenêtre (copie de poste en retard,
        gestion, requête forgée) : jamais d'erreur (la synchronisation du
        poste resterait bloquée), une ligne « Annulation sans code » par
        produit envoyé."""
        _addition, commande, _castel, _poulet = self._table_deux_produits()
        commande.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(commande.state, 'cancel')
        traces = self._journal(commande)
        self.assertEqual(sorted(traces.mapped('produit_nom')), ["Castel", "Poulet DG"])
        self.assertEqual(set(traces.mapped('type_annulation')), {'annulation_sans_code'})
        self.assertFalse(any(traces.mapped('autorisee')))
        self.assertEqual(sorted(traces.mapped('quantite')), [1, 2])
        self.assertEqual(sum(traces.mapped('montant')), 2 * 1000 + 6500)
        self.assertEqual(set(traces.mapped('serveur_nom')), {"Awa"})
        # La caisse renvoie l'annulation à chaque synchronisation (liste
        # d'attente d'Odoo) : rien de plus.
        commande.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(len(self._journal(commande)), 2)

    def test_annulation_depuis_la_gestion(self):
        """Revue de l'incrément 4, constat 3 : « Cancel Order » de la gestion
        sur l'addition d'Awa (pos_hr remplit l'employé de toute addition) :
        la trace est au nom de l'utilisateur Odoo qui a annulé, pas d'Awa
        (partie 4.2 : « ou l'utilisateur Odoo s'il vient de la gestion »)."""
        _addition, commande, _castel, _poulet = self._table_deux_produits()
        self.assertEqual(commande.employee_id, self.awa, "le cas réel : l'employé est posé")
        commande.with_user(self.compte_manager).action_pos_order_cancel()
        traces = self._journal(commande)
        self.assertEqual(len(traces), 2)
        self.assertEqual(set(traces.mapped('serveur_nom')), {"Manager du restaurant"})
        self.assertFalse(traces.serveur_id, "aucun employé n'est accusé")

    def test_annulation_de_table_autorisee(self):
        _addition, commande, _castel, _poulet = self._table_deux_produits()
        reponse = self._autoriser(commande, False, '4444', motif=self.motif_parti,
                                  nature='table')
        self.assertNotIn('erreur', reponse)
        self.assertEqual(commande.lines.mapped('aite_qte_envoyee'), [0, 0, 0])
        commande.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(commande.state, 'cancel')
        traces = self._journal(commande)
        self.assertEqual(set(traces.mapped('type_annulation')), {'table'})
        self.assertEqual(sorted(traces.mapped('quantite')), [1, 2],
                         "seul ce qui est parti : la Castel saisie après n'est pas tracée")
        self.assertTrue(all(traces.mapped('autorisee')))
        self.assertEqual(set(traces.mapped('superieur_nom')), {"Paul"})
        self.assertEqual(set(traces.mapped('motif_nom')), {"Client parti"})

    def test_tables_annulees_a_la_fermeture(self):
        _addition, table_12, _castel, _poulet = self._table_deux_produits()
        table_7_copie = Addition(self.table_7, 2, self.moussa)
        table_7_copie.ajouter(self.castel, 1)
        table_7_copie.envoyer()
        table_7 = self._commande_caisse(table_7_copie, self.moussa)
        vide = self._commande_caisse(Addition(self.table_12.copy({'table_number': 13}), 2,
                                              self.awa), self.awa)
        commandes = table_12 | table_7 | vide
        reponse = self._autoriser(commandes, False, '4444', motif=self.motif_parti,
                                  demandeur=self.paul, nature='fermeture')
        self.assertNotIn('erreur', reponse)
        commandes.with_user(self.compte_caisse).action_pos_order_cancel()
        traces = self._journal()
        self.assertEqual(len(traces), 3)
        self.assertEqual(set(traces.mapped('type_annulation')), {'fermeture'})
        self.assertEqual(set(traces.mapped('serveur_nom')), {"Paul"})
        self.assertEqual(traces.order_id, table_12 | table_7)

    def test_fusion_n_est_pas_une_annulation(self):
        """« Déplacer ou réunir » vers une table occupée : la caisse marque
        l'addition absorbée avant de l'annuler."""
        _addition, commande, _castel, _poulet = self._table_deux_produits()
        self.env['pos.order'].with_user(self.compte_caisse).aite_marquer_fusion(commande.id)
        self.assertTrue(commande.aite_fusionnee)
        self.assertEqual(commande.lines.mapped('aite_qte_envoyee'), [0, 0, 0])
        commande.with_user(self.compte_caisse).action_pos_order_cancel()
        self.assertEqual(commande.state, 'cancel')
        self.assertFalse(self._journal())

    def test_fusion_forgee_par_une_ecriture(self):
        _addition, commande, _castel, _poulet = self._table_deux_produits()
        commande.with_user(self.compte_caisse).write({'aite_fusionnee': True})
        self.assertFalse(commande.aite_fusionnee)

    def test_remove_from_ui_trace(self):
        """``remove_from_ui`` (aucun appel par la caisse, mais une requête
        possible du compte de la caisse) : annulée (pos_self_order, installé
        avec le restaurant, l'annule avant qu'Odoo ne la supprime), tracée."""
        _addition, commande, _castel, _poulet = self._table_deux_produits()
        self.env['pos.order'].with_user(self.compte_caisse).remove_from_ui([commande.id])
        commande = commande.exists()
        self.assertTrue(not commande or commande.state == 'cancel')
        traces = self.Annulation.search([('order_ref', '=', _addition.record.pos_reference)])
        self.assertEqual(len(traces), 2)
        self.assertEqual(set(traces.mapped('type_annulation')), {'annulation_sans_code'})

    def test_suppression_d_une_addition_envoyee(self):
        """Une addition en cours supprimée depuis la gestion : la trace est
        écrite avant, et survit à la suppression."""
        addition, commande, _castel, _poulet = self._table_deux_produits()
        reference = commande.pos_reference
        commande.with_user(self.compte_manager).unlink()
        self.env.invalidate_all()
        traces = self.Annulation.search([('order_ref', '=', reference)])
        self.assertEqual(len(traces), 2)
        self.assertEqual(set(traces.mapped('type_annulation')), {'annulation_sans_code'})
        self.assertFalse(traces.order_id, "la trace survit à la suppression de l'addition")

    def test_ecriture_et_suppression_directes(self):
        """Le compte de la caisse a tous les droits sur les lignes : une
        baisse ou une suppression directe d'une ligne envoyée est tracée."""
        _addition, commande, castel, poulet = self._table_deux_produits()
        ligne_castel = commande.lines.filtered(lambda l: l.uuid == castel)
        ligne_poulet = commande.lines.filtered(lambda l: l.uuid == poulet)
        ligne_castel.with_user(self.compte_caisse).write({'qty': 1})
        ligne_poulet.with_user(self.compte_caisse).unlink()
        traces = self._journal(commande)
        self.assertEqual(traces.mapped('type_annulation'),
                         ['retrait_sans_code', 'retrait_sans_code'])
        self.assertEqual(traces.mapped('produit_nom'), ["Castel", "Poulet DG"])
        self.assertEqual(traces.mapped('quantite'), [1, 1])
        self.assertEqual(ligne_castel.aite_qte_envoyee, 1)

    def test_deux_postes_copie_ancienne(self):
        """Un second poste resté sur une copie ancienne, sans la ligne
        envoyée par le premier : il n'envoie pas sa suppression, rien n'est
        retiré ni tracé."""
        premier = Addition(self.table_12, 4, self.awa)
        commande = self._commande_caisse(premier, self.awa)
        second = Addition(self.table_12, 4, self.awa)
        second.uuid = premier.uuid
        second.valeurs = dict(premier.valeurs)
        uuid = premier.ajouter(self.castel, 2)
        premier.envoyer()
        self._commande_caisse(premier, self.awa)
        second.ajouter(self.poulet, 1)
        self._commande_caisse(second, self.moussa)
        ligne = commande.lines.filtered(lambda l: l.uuid == uuid)
        self.assertEqual(ligne.qty, 2)
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        self.assertFalse(self._journal())

    # ------------------------------------------------------------------
    # Le journal et les motifs
    # ------------------------------------------------------------------

    def test_journal_ni_modifie_ni_efface(self):
        _addition, commande, ligne = self._table_envoyee(2)
        self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444')
        trace = self._journal(commande)
        admin = self.env.ref('base.user_admin')
        for qui in (trace.with_user(self.compte_manager), trace.with_user(admin), trace.sudo()):
            with self.subTest(qui=qui.env.user.name, su=qui.env.su):
                with self.assertRaises(UserError):
                    qui.write({'quantite': 5})
                with self.assertRaises(UserError):
                    qui.unlink()
        self.assertEqual(trace.quantite, 1)

    def test_le_compte_de_la_caisse_ne_lit_ni_n_ecrit_le_journal(self):
        with self.assertRaises(AccessError):
            self.Annulation.with_user(self.compte_caisse).search([])
        with self.assertRaises(AccessError):
            self.Annulation.with_user(self.compte_caisse).create({'produit_nom': "Faux"})

    def test_cinq_motifs_poses_d_office(self):
        motifs = self.env['aite.restaurant.motif'].search([], order='sequence, id')
        self.assertEqual(motifs.mapped('name'), [
            "Erreur de saisie", "Client parti", "Plat refusé", "Produit manquant", "Autre"])
        self.assertEqual(motifs.filtered('precision_requise'), self.motif_autre)

    def test_motif_ajoute_pendant_le_service(self):
        """REST-12 critère 5 : la fenêtre lit les motifs à son ouverture."""
        Motif = self.env['aite.restaurant.motif'].with_user(self.compte_manager)
        nouveau = Motif.create({'name': "Offert par la maison", 'sequence': 3})
        self.motif_parti.with_user(self.compte_manager).active = False
        motifs = self.session.with_user(self.compte_caisse).aite_motifs_annulation()
        noms = [motif['name'] for motif in motifs]
        self.assertIn(nouveau.name, noms)
        self.assertNotIn("Client parti", noms)
        self.assertEqual(noms[-1], "Autre")
        autre = next(m for m in motifs if m['name'] == "Autre")
        self.assertTrue(autre['precision_requise'])
        self.assertEqual(set(autre), {'id', 'name', 'precision_requise'})
        with self.assertRaises(AccessError):
            nouveau.with_user(self.compte_manager).unlink()
        with self.assertRaises(AccessError):
            self.env['aite.restaurant.motif'].with_user(self.compte_caisse).search([])

    def test_bouton_annulations_de_la_fiche(self):
        _addition, commande, ligne = self._table_envoyee(2)
        self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444')
        action = commande.with_user(self.compte_manager).action_aite_annulations()
        self.assertEqual(action['res_model'], 'aite.restaurant.annulation')
        self.assertEqual(self.Annulation.with_user(self.compte_manager).search_count(
            action['domain']), 1)

    # ------------------------------------------------------------------
    # Revue de l'incrément 4 : constats corrigés (test d'abord)
    # ------------------------------------------------------------------

    def _ligne_directe(self, commande, produit, qty):
        """Une ligne créée par une requête directe du compte de la caisse."""
        prix = produit.lst_price
        return self.env['pos.order.line'].with_user(self.compte_caisse).create({
            'order_id': commande.id, 'product_id': produit.id, 'qty': qty,
            'price_unit': prix, 'price_subtotal': qty * prix,
            'price_subtotal_incl': qty * prix, 'full_product_name': produit.display_name,
            'tax_ids': [(6, 0, [])], 'uuid': str(uuid4())})

    def test_ligne_negative_synchronisee_tracee(self):
        """Constat 1 (bloquant) : « +/- » sur une ligne neuve donne une ligne
        négative qui baisse l'addition d'un produit déjà envoyé, sans code ni
        trace. La synchronisation n'est jamais refusée, mais la part négative
        d'une ligne qui n'est pas un remboursement est un « Retrait sans
        code », quel que soit le produit."""
        addition, commande, _ligne = self._table_envoyee(3)
        moins_castel = addition.ajouter(self.castel, -1)
        self._commande_caisse(addition, self.awa)
        trace = self._journal(commande)
        self.assertEqual(len(trace), 1, trace.mapped('type_annulation'))
        self.assertEqual(trace.type_annulation, 'retrait_sans_code')
        self.assertEqual(trace.quantite, 1)
        self.assertEqual(trace.montant, 1000)
        self.assertEqual(trace.produit_nom, "Castel")
        self.assertEqual(trace.ligne_uuid, moins_castel)
        self.assertEqual(trace.serveur_nom, "Awa")
        # La même ligne renvoyée sans changement : rien de plus.
        addition.envoyer()
        self._commande_caisse(addition, self.awa)
        self.assertEqual(len(self._journal(commande)), 1)
        # Une ligne négative d'un autre produit (jamais envoyé) : tracée aussi.
        moins_poulet = addition.ajouter(self.poulet, -2)
        self._commande_caisse(addition, self.awa)
        trace = self._journal(commande).filtered(lambda t: t.ligne_uuid == moins_poulet)
        self.assertEqual((trace.type_annulation, trace.quantite, trace.montant),
                         ('retrait_sans_code', 2, 13000))
        # Elle s'enfonce encore (-2 → -3) : la part de plus seulement.
        addition.changer(moins_poulet, -3)
        self._commande_caisse(addition, self.awa)
        traces = self._journal(commande).filtered(lambda t: t.ligne_uuid == moins_poulet)
        self.assertEqual(sorted(traces.mapped('quantite')), [1, 2])

    def test_ligne_negative_ecrite_directement_tracee(self):
        """Constat 1 : une ligne négative créée, ou une ligne passée en
        négatif, par une requête directe du compte de la caisse."""
        _addition, commande, _ligne = self._table_envoyee(3)
        creee = self._ligne_directe(commande, self.castel, -3)
        trace = self._journal(commande)
        self.assertEqual(len(trace), 1)
        self.assertEqual((trace.type_annulation, trace.quantite, trace.montant, trace.ligne_uuid),
                         ('retrait_sans_code', 3, 3000, creee.uuid))
        neuve = self._ligne_directe(commande, self.poulet, 1)
        self.assertEqual(len(self._journal(commande)), 1, "une ligne positive n'est pas tracée")
        neuve.with_user(self.compte_caisse).write({'qty': -2})
        trace = self._journal(commande).filtered(lambda t: t.ligne_uuid == neuve.uuid)
        self.assertEqual((trace.type_annulation, trace.quantite, trace.montant),
                         ('retrait_sans_code', 2, 13000))

    def test_remboursement_n_est_pas_un_retrait(self):
        """Une ligne de remboursement (``refunded_orderline_id``) est négative
        par nature : ni trace en cours, ni à l'encaissement."""
        addition = Addition(self.table_12, 2, self.awa)
        addition.ajouter(self.castel, 1)
        especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]
        commande = self._commande_caisse(addition, self.carine, etat='paid', payer=especes)
        retour = Addition(personnes=0, ouverte_par=self.fanta)
        retour.ajouter(self.castel, -1)
        lien = {'refunded_orderline_id': commande.lines.id}
        remboursement = self._commande_caisse(retour, self.fanta, en_plus_lignes=lien)
        self.assertEqual(remboursement.state, 'draft')
        self._commande_caisse(retour, self.fanta, etat='paid', payer=especes, en_plus_lignes=lien)
        self.assertEqual(remboursement.state, 'paid')
        self.assertFalse(self._journal())

    def test_annulation_par_l_action_de_la_gestion(self):
        """Constat 3 : l'action « Cancel Order » (menu Action de la liste ou
        de la fiche), lancée par le manager, puis par le compte de la caisse
        lui-même depuis la gestion : au nom de l'utilisateur Odoo."""
        action = self.env.ref('point_of_sale.pos_order_set_cancel')
        for compte in (self.compte_manager, self.compte_caisse):
            with self.subTest(compte=compte.name):
                _addition, commande, _castel, _poulet = self._table_deux_produits()
                action.with_user(compte).with_context(
                    active_model='pos.order', active_ids=commande.ids,
                    active_id=commande.id).run()
                self.assertEqual(commande.state, 'cancel')
                traces = self._journal(commande)
                self.assertEqual(len(traces), 2)
                self.assertEqual(set(traces.mapped('serveur_nom')), {compte.name})
                self.assertFalse(traces.serveur_id)

    def test_retrait_direct_depuis_la_gestion(self):
        """Constat 3 : une ligne envoyée baissée ou supprimée par le manager
        depuis la gestion : au nom de l'utilisateur Odoo ; par le compte de
        la caisse (requête de la caisse) : l'employé de l'addition."""
        _addition, commande, castel, poulet = self._table_deux_produits()
        ligne_castel = commande.lines.filtered(lambda l: l.uuid == castel)
        ligne_poulet = commande.lines.filtered(lambda l: l.uuid == poulet)
        ligne_castel.with_user(self.compte_manager).write({'qty': 1})
        ligne_poulet.with_user(self.compte_manager).unlink()
        traces = self._journal(commande)
        self.assertEqual(len(traces), 2)
        self.assertEqual(set(traces.mapped('serveur_nom')), {"Manager du restaurant"})
        self.assertFalse(traces.serveur_id)
        ligne_castel.with_user(self.compte_caisse).write({'qty': 0})
        trace = self._journal(commande) - traces
        self.assertEqual((trace.quantite, trace.serveur_nom), (1, "Awa"))

    def test_cle_rejouee_sur_une_autre_addition(self):
        """Constat 4 : une clé déjà enregistrée, renvoyée pour une autre
        addition ou une autre ligne (requête forgée) : refusée, rien n'est
        rendu de la première demande ni baissé."""
        _addition, commande, ligne = self._table_envoyee(3)
        demande = str(uuid4())
        self.assertNotIn('erreur', self._autoriser(
            commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444', demande=demande))
        _autre, table_7, ligne_7 = self._table_envoyee(3, table=self.table_7)
        incomplete = {'erreur': "Demande d'annulation incomplète."}
        reponse = self.env['pos.order'].with_user(self.compte_caisse).aite_autoriser_annulation(
            table_7.ids, [{'uuid': ligne_7.uuid, 'quantite': 3}], '0000', 999999, False,
            False, demande, 'produit')
        self.assertEqual(reponse, incomplete)
        self.assertEqual(ligne_7.aite_qte_envoyee, 3)
        # Même addition, autre ligne ; même addition, autre nature.
        poulet = commande.lines.create({
            'order_id': commande.id, 'product_id': self.poulet.id, 'qty': 1,
            'price_unit': 6500, 'price_subtotal': 6500, 'price_subtotal_incl': 6500,
            'full_product_name': "Poulet DG", 'uuid': str(uuid4())})
        self.assertEqual(self._autoriser(commande, [{'uuid': poulet.uuid, 'quantite': 1}],
                                         '4444', demande=demande), incomplete)
        self.assertEqual(self._autoriser(commande, False, '4444', demande=demande,
                                         nature='table'), incomplete)
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        self.assertEqual(len(self._journal()), 1)
        # La vraie demande renvoyée (réponse perdue) : toujours la première réponse.
        seconde = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 1}], '4444',
                                  demande=demande)
        self.assertEqual(seconde.get('quantites'), {ligne.uuid: 1})

    def test_meme_ligne_deux_fois_dans_une_demande(self):
        """Constat 5 : la même ligne deux fois dans ``lignes`` (requête
        forgée) : un refus en français, ni erreur de base de données, ni
        trace, ni baisse."""
        _addition, commande, ligne = self._table_envoyee(3)
        reponse = self._autoriser(commande, [{'uuid': ligne.uuid, 'quantite': 2},
                                             {'uuid': ligne.uuid, 'quantite': 2}], '4444')
        self.assertEqual(reponse, {'erreur': "Demande d'annulation incomplète."})
        self.assertFalse(self._journal())
        self.assertEqual(ligne.aite_qte_envoyee, 3)
