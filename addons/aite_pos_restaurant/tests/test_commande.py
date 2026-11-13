# -*- coding: utf-8 -*-
"""La table côté serveur : personnes, qui a ouvert, heure d'ouverture, qui a
encaissé, champs protégés, traces (spécification, parties 3.1 et 4.2 ;
incrément 3).

Chaque addition passe par le chemin de la caisse (``sync_from_ui``, aide
``_commande_caisse``), jamais par un ``create`` direct (périmètre 5.4,
point 11).
"""
from datetime import timedelta
from unittest.mock import patch

from lxml import etree

from odoo import fields
from odoo.tests import tagged

from .common import Addition, RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestCommande(RestaurantCommon):

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()
        self.especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]

    def _table_12(self, personnes=4, ouverte_par=None):
        """Awa touche la table 12 libre, tape son code et répond « 4 » : la
        caisse enregistre aussitôt l'addition, sans produit."""
        addition = Addition(self.table_12, personnes, ouverte_par or self.awa)
        commande = self._commande_caisse(addition, ouverte_par or self.awa)
        return addition, commande

    def _notes(self, commande):
        return ' '.join(commande.message_ids.mapped('body'))

    # ------------------------------------------------------------------
    # Ouverture de la table
    # ------------------------------------------------------------------

    def test_table_ouverte_sans_produit(self):
        avant = fields.Datetime.now()
        _addition, commande = self._table_12()
        self.assertEqual(commande.state, 'draft')
        self.assertFalse(commande.lines)
        self.assertEqual(commande.table_id, self.table_12)
        self.assertEqual(commande.customer_count, 4)
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        self.assertTrue(commande.aite_heure_ouverture)
        # À l'horloge du serveur.
        self.assertGreaterEqual(commande.aite_heure_ouverture, avant)
        self.assertLessEqual(commande.aite_heure_ouverture, fields.Datetime.now())

    def test_heure_plus_recente_ignoree_plus_ancienne_gardee(self):
        addition, commande = self._table_12()
        heure = commande.aite_heure_ouverture
        addition.valeurs['aite_heure_ouverture'] = fields.Datetime.to_string(
            heure + timedelta(minutes=10))
        self._commande_caisse(addition, self.awa)
        self.assertEqual(commande.aite_heure_ouverture, heure)
        # Réunion : la caisse envoie l'heure la plus ancienne des deux tables.
        ancienne = heure - timedelta(minutes=30)
        addition.valeurs['aite_heure_ouverture'] = fields.Datetime.to_string(ancienne)
        self._commande_caisse(addition, self.awa, deplacement=True)
        self.assertEqual(commande.aite_heure_ouverture, ancienne)

    def test_heure_dans_le_futur_ignoree_a_l_ouverture(self):
        addition = Addition(self.table_12, 4, self.awa)
        addition.valeurs['aite_heure_ouverture'] = fields.Datetime.to_string(
            fields.Datetime.now() + timedelta(hours=2))
        commande = self._commande_caisse(addition, self.awa)
        self.assertLessEqual(commande.aite_heure_ouverture, fields.Datetime.now())

    def test_ouverte_par_fige(self):
        addition, commande = self._table_12()
        addition.valeurs['aite_ouverte_par_id'] = self.moussa.id
        self._commande_caisse(addition, self.moussa)
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        # Écriture directe par le compte de la caisse : refusée de même.
        commande.with_user(self.compte_caisse).write({'aite_ouverte_par_id': self.moussa.id})
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)

    def test_part_d_une_division_garde_l_origine(self):
        """La part « 12B » reçoit, de la caisse, l'origine, l'heure et
        « ouverte par » de la table 12 ; elle a 0 personne."""
        _addition, origine = self._table_12()
        part = Addition(personnes=0, ouverte_par=self.awa, nom="12B")
        part.valeurs['aite_origine_uuid'] = origine.uuid
        part.valeurs['aite_heure_ouverture'] = fields.Datetime.to_string(
            origine.aite_heure_ouverture)
        part.ajouter(self.castel, 1)
        commande = self._commande_caisse(part, self.awa, deplacement=True)
        self.assertEqual(commande.aite_origine_uuid, origine.uuid)
        self.assertEqual(commande.aite_heure_ouverture, origine.aite_heure_ouverture)
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        self.assertEqual(commande.customer_count, 0)
        # L'origine est figée, comme « ouverte par ».
        part.valeurs['aite_origine_uuid'] = 'autre'
        self._commande_caisse(part, self.awa)
        self.assertEqual(commande.aite_origine_uuid, origine.uuid)

    def test_table_a_zero_personne_ramenee_a_un(self):
        addition = Addition(self.table_12, 0, self.awa)
        commande = self._commande_caisse(addition, self.awa)
        self.assertEqual(commande.customer_count, 1)
        self.assertTrue(commande.aite_heure_ouverture)
        self.assertIn("0 personne", self._notes(commande))
        self.assertEqual(addition.valeurs['customer_count'], 1)

    # ------------------------------------------------------------------
    # Champs que le serveur seul écrit
    # ------------------------------------------------------------------

    def test_champs_du_serveur_ignores(self):
        addition, commande = self._table_12()
        uuid = addition.ajouter(self.castel, 2)
        commande = self._commande_caisse(
            addition, self.awa,
            en_plus={'aite_encaissee_par_id': self.fanta.id, 'aite_tables': 5,
                     'aite_qte_envoyee': 9},
            en_plus_lignes={'aite_qte_envoyee': 9, 'aite_qte_preparation': 9})
        self.assertFalse(commande.aite_encaissee_par_id)
        ligne = commande.lines.filtered(lambda l: l.uuid == uuid)
        self.assertEqual(ligne.aite_qte_envoyee, 0)
        self.assertEqual(ligne.aite_qte_preparation, 0)
        # Une commande de ligne [1, id, …] : même chose.
        addition.changer(uuid, 3)
        self._commande_caisse(addition, self.awa,
                              en_plus_lignes={'aite_qte_envoyee': 9})
        self.assertEqual(ligne.aite_qte_envoyee, 0)

    def test_ecriture_directe_ignoree(self):
        addition, commande = self._table_12()
        uuid = addition.ajouter(self.castel, 2)
        addition.envoyer()
        self._commande_caisse(addition, self.awa)
        ligne = commande.lines.filtered(lambda l: l.uuid == uuid)
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        ligne.with_user(self.compte_caisse).write({'aite_qte_envoyee': 0, 'aite_qte_preparation': 0})
        self.assertEqual(ligne.aite_qte_envoyee, 2)
        self.assertEqual(ligne.aite_qte_preparation, 2)
        commande.with_user(self.compte_caisse).write({
            'aite_encaissee_par_id': self.fanta.id,
            'aite_heure_ouverture': fields.Datetime.to_string(
                commande.aite_heure_ouverture - timedelta(hours=3))})
        self.assertFalse(commande.aite_encaissee_par_id)
        self.assertEqual(commande.aite_heure_ouverture,
                         fields.Datetime.to_datetime(addition.valeurs['aite_heure_ouverture']))

    # ------------------------------------------------------------------
    # Envoi : la quantité verrouillée
    # ------------------------------------------------------------------

    def test_envoi_verrouille_la_quantite_envoyee(self):
        addition, commande = self._table_12()
        uuid = addition.ajouter(self.castel, 3)
        self._commande_caisse(addition, self.awa)
        ligne = commande.lines
        self.assertEqual(ligne.aite_qte_envoyee, 0, "saisi, pas encore envoyé")
        addition.envoyer()
        self._commande_caisse(addition, self.awa)
        self.assertEqual(ligne.aite_qte_envoyee, 3)
        self.assertEqual(ligne.aite_qte_preparation, 3)
        addition.changer(uuid, 4)
        self._commande_caisse(addition, self.awa)
        self.assertEqual(ligne.aite_qte_envoyee, 3, "la 4ᵉ n'est pas encore partie")
        addition.envoyer()
        self._commande_caisse(addition, self.awa)
        self.assertEqual(ligne.aite_qte_envoyee, 4)

    # ------------------------------------------------------------------
    # Encaissement
    # ------------------------------------------------------------------

    def test_encaissee_par(self):
        addition, commande = self._table_12()
        addition.ajouter(self.castel, 2)
        addition.envoyer()
        self._commande_caisse(addition, self.awa)
        self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)
        self.assertEqual(commande.state, 'paid')
        self.assertEqual(commande.aite_encaissee_par_id, self.carine)
        # REST-02 critère 1 : « ouverte par » reste la serveuse.
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        self.assertNotIn("n'a pas le droit d'encaisser", self._notes(commande))

    def test_encaissement_par_un_serveur_accepte_et_note(self):
        addition, commande = self._table_12()
        addition.ajouter(self.castel, 1)
        self._commande_caisse(addition, self.moussa, etat='paid', payer=self.especes)
        self.assertEqual(commande.state, 'paid')
        self.assertEqual(commande.aite_encaissee_par_id, self.moussa)
        self.assertIn("Moussa", self._notes(commande))
        self.assertIn("n'a pas le droit d'encaisser", self._notes(commande))

    def test_vente_sans_table_sur_une_caisse_qui_ne_l_ouvre_pas(self):
        self.assertFalse(self.config.aite_vente_sans_table)
        addition = Addition(personnes=0, ouverte_par=self.carine)
        addition.ajouter(self.castel, 1)
        commande = self._commande_caisse(addition, self.carine, etat='paid',
                                         payer=self.especes)
        self.assertEqual(commande.state, 'paid')
        self.assertIn("vente sans table", self._notes(commande))

    def test_numero_inconnu_n_est_pas_une_vente_sans_table(self):
        """T11 : un numéro tapé qui n'est pas sur le plan ouvre une table à ce
        nom, avec ses personnes ; ce n'est pas une vente sans table."""
        addition = Addition(personnes=2, ouverte_par=self.awa, nom="99")
        commande = self._commande_caisse(addition, self.awa)
        self.assertEqual(commande.floating_order_name, "99")
        self.assertEqual(commande.customer_count, 2)
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        self.assertTrue(commande.aite_heure_ouverture)
        addition.ajouter(self.castel, 1)
        self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)
        self.assertNotIn("vente sans table", self._notes(commande))

    def test_remboursement_sans_le_droit_note(self):
        addition, commande = self._table_12()
        addition.ajouter(self.castel, 1)
        self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)
        retour = Addition(personnes=0, ouverte_par=self.carine)
        uuid = retour.ajouter(self.castel, -1)
        remboursement = self._commande_caisse(
            retour, self.carine, etat='paid', payer=self.especes,
            en_plus_lignes={'refunded_orderline_id': commande.lines.id})
        self.assertEqual(remboursement.state, 'paid')
        self.assertTrue(remboursement.lines.filtered(lambda l: l.uuid == uuid).refunded_orderline_id)
        self.assertIn("rembourser", self._notes(remboursement))
        self.assertNotIn("vente sans table", self._notes(remboursement))

    def test_caisse_hors_mode_non_touchee(self):
        """Une caisse de restaurant dont la case est décochée : ni heure, ni
        « encaissée par », ni quantité verrouillée, ni saisie."""
        temoin = self.env['pos.config'].create({
            'name': "Bar témoin", 'module_pos_restaurant': True, 'module_pos_hr': True,
            'payment_method_ids': [(6, 0, self.cash_pm1.copy({
                'name': "Espèces témoin",
                'journal_id': self.env['account.journal'].create({
                    'name': "Caisse témoin", 'type': 'cash', 'code': 'CTEMO'}).id,
            }).ids)],
        })
        self._ouvrir_session(temoin)
        addition = Addition(temoin.floor_ids.table_ids[:1], 3)
        addition.ajouter(self.castel, 2)
        addition.envoyer()
        commande = self._commande_caisse(addition, self.awa, config=temoin)
        self.assertFalse(commande.aite_heure_ouverture)
        self.assertEqual(commande.lines.aite_qte_envoyee, 0)
        self._commande_caisse(addition, self.carine, etat='paid',
                              payer=temoin.payment_method_ids, config=temoin)
        self.assertEqual(commande.state, 'paid')
        self.assertFalse(commande.aite_encaissee_par_id)
        self.assertFalse(self.env['aite.restaurant.saisie'].search_count(
            [('order_id', '=', commande.id)]))

    # ------------------------------------------------------------------
    # Revue de l'incrément 3 : la clé « écriture du serveur » posée par la
    # caisse (constat bloquant n° 1). Le contexte d'une requête de la caisse
    # est transmis tel quel au serveur : une valeur qu'il peut contenir
    # n'autorise rien.
    # ------------------------------------------------------------------

    def _table_envoyee(self):
        addition, commande = self._table_12()
        uuid = addition.ajouter(self.castel, 3)
        addition.envoyer()
        self._commande_caisse(addition, self.awa)
        ligne = commande.lines.filtered(lambda l: l.uuid == uuid)
        self.assertEqual(ligne.aite_qte_envoyee, 3)
        return addition, commande, ligne

    def test_cle_du_serveur_forgee_sur_une_ligne(self):
        _addition, _commande, ligne = self._table_envoyee()
        ligne.with_user(self.compte_caisse).with_context(aite_ecriture_serveur=True).write(
            {'aite_qte_envoyee': 0, 'aite_qte_preparation': 0})
        self.assertEqual(ligne.aite_qte_envoyee, 3)
        self.assertEqual(ligne.aite_qte_preparation, 3)

    def test_cle_du_serveur_forgee_sur_l_addition(self):
        _addition, commande, _ligne = self._table_envoyee()
        heure = commande.aite_heure_ouverture
        commande.with_user(self.compte_caisse).with_context(aite_ecriture_serveur=True).write({
            'aite_encaissee_par_id': self.fanta.id,
            'aite_ouverte_par_id': self.moussa.id,
            'aite_heure_ouverture': fields.Datetime.to_string(heure + timedelta(hours=1)),
        })
        self.assertFalse(commande.aite_encaissee_par_id)
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        self.assertEqual(commande.aite_heure_ouverture, heure)

    def test_cle_du_serveur_forgee_a_la_creation(self):
        """Une addition et une ligne créées directement par le compte de la
        caisse, avec la clé : « encaissée par » et la quantité envoyée ne
        sont pas posés."""
        vals = {
            'session_id': self.session.id, 'company_id': self.company.id,
            'amount_tax': 0, 'amount_total': 0, 'amount_paid': 0, 'amount_return': 0,
            'aite_encaissee_par_id': self.fanta.id,
        }
        caisse = self.env['pos.order'].with_user(self.compte_caisse)
        self.assertFalse(caisse.create(dict(vals)).aite_encaissee_par_id)
        forgee = caisse.with_context(aite_ecriture_serveur=True).create(dict(vals))
        self.assertFalse(forgee.aite_encaissee_par_id)
        ligne = self.env['pos.order.line'].with_user(self.compte_caisse).with_context(
            aite_ecriture_serveur=True).create({
                'order_id': forgee.id, 'product_id': self.castel.id, 'qty': 2,
                'price_unit': 1000.0, 'price_subtotal': 2000.0,
                'price_subtotal_incl': 2000.0, 'aite_qte_envoyee': 2,
                'aite_qte_preparation': 2})
        self.assertEqual(ligne.aite_qte_envoyee, 0)
        self.assertEqual(ligne.aite_qte_preparation, 0)

    def test_cle_du_serveur_dans_la_synchronisation(self):
        """La synchronisation elle-même envoyée avec la clé : les champs du
        serveur restent retirés de la charge, et le serveur écrit ce qu'il
        calcule (la saisie de Moussa, au nom de Moussa)."""
        addition, commande, ligne = self._table_envoyee()
        uuid = next(iter(addition.lignes))
        addition.changer(uuid, 4)
        donnees = {'aite_encaissee_par_id': self.fanta.id,
                   'aite_ouverte_par_id': self.moussa.id}
        PosOrder = type(self.env['pos.order'])
        origine = PosOrder.sync_from_ui

        def forgee(modele, orders):
            return origine(modele.with_context(aite_ecriture_serveur=True), orders)

        with patch.object(PosOrder, 'sync_from_ui', forgee):
            self._commande_caisse(addition, self.moussa, en_plus=donnees,
                                  en_plus_lignes={'aite_qte_envoyee': 0,
                                                  'aite_qte_preparation': 0})
        self.assertFalse(commande.aite_encaissee_par_id)
        self.assertEqual(commande.aite_ouverte_par_id, self.awa)
        self.assertEqual(ligne.aite_qte_envoyee, 3)
        self.assertEqual(ligne.qty, 4)
        saisies = self.env['aite.restaurant.saisie'].search(
            [('order_id', '=', commande.id)], order='id')
        self.assertEqual(saisies.mapped('employe_nom'), ["Awa", "Moussa"])
        self.assertEqual(saisies.mapped('quantite'), [3, 1])

    # ------------------------------------------------------------------
    # Revue de l'incrément 3, constat n° 9 : le bouton « Saisies » suit le
    # mode de la caisse, pas « Ouverte par »
    # ------------------------------------------------------------------

    def test_saisies_d_une_addition_sans_ouverte_par(self):
        """Une addition de la caisse au service à table contrôlé sans
        « ouverte par » (copie ancienne, addition ouverte avant la mise à
        niveau) a des saisies : le bouton reste visible du manager."""
        addition = Addition(self.table_12, 2)
        addition.ajouter(self.castel, 1)
        commande = self._commande_caisse(addition, self.awa)
        self.assertFalse(commande.aite_ouverte_par_id)
        self.assertTrue(commande.aite_mode_restaurant)
        action = commande.with_user(self.compte_manager).action_aite_saisies()
        self.assertEqual(self.env['aite.restaurant.saisie'].search_count(action['domain']), 1)
        vue = etree.fromstring(self.env['pos.order'].get_view(
            self.env.ref('point_of_sale.view_pos_pos_form').id, 'form')['arch'])
        bouton = vue.xpath("//button[@name='action_aite_saisies']")
        self.assertEqual(len(bouton), 1)
        self.assertEqual(bouton[0].get('invisible'), 'not aite_mode_restaurant')


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestVenteSansTableCochee(RestaurantCommon):
    """La case « Autoriser la vente sans table » se coche caisse fermée
    (revue de l'incrément 3, constat n° 11) : une vente sans table ouverte
    sur une caisse où elle est cochée n'est pas notée."""

    def test_case_cochee_pas_de_note(self):
        self.config.aite_vente_sans_table = True
        self._ouvrir_session()
        especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]
        addition = Addition(personnes=0, ouverte_par=self.carine)
        addition.ajouter(self.castel, 1)
        commande = self._commande_caisse(addition, self.carine, etat='paid', payer=especes)
        self.assertEqual(commande.state, 'paid')
        self.assertNotIn("vente sans table", ' '.join(commande.message_ids.mapped('body')))

