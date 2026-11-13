# -*- coding: utf-8 -*-
"""Le journal des saisies : qui a saisi chaque produit (REST-02 critère 3,
Q14 ; spécification, T19, parties 3.2 et 4.2 ; incrément 3).

Le serveur écrit une ligne à chaque hausse de quantité d'une ligne de
l'addition, au nom de la personne identifiée sur le poste (contexte
``aite_employee_id`` posé par la caisse), sinon au nom de l'employé de
l'addition. Une division ou une réunion (contexte ``aite_deplacement``)
n'est pas une saisie. Le journal ne se modifie pas et ne s'efface pas.
"""
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import Addition, RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestSaisie(RestaurantCommon):

    def setUp(self):
        super().setUp()
        self.session = self._ouvrir_session()
        self.especes = self.config.payment_method_ids.filtered('is_cash_count')[:1]
        self.Saisie = self.env['aite.restaurant.saisie']

    def _saisies(self, commande):
        return self.Saisie.search([('order_id', '=', commande.id)], order='id')

    def test_deux_personnes_deux_saisies(self):
        addition = Addition(self.table_12, 4, self.awa)
        self._commande_caisse(addition, self.awa)
        uuid = addition.ajouter(self.castel, 2)
        commande = self._commande_caisse(addition, self.awa)
        addition.changer(uuid, 3)
        self._commande_caisse(addition, self.paul)
        saisies = self._saisies(commande)
        self.assertEqual(saisies.mapped('quantite'), [2, 1])
        self.assertEqual(saisies.mapped('employe_id'), self.awa | self.paul)
        self.assertEqual(saisies.mapped('employe_nom'), ["Awa", "Paul"])
        premiere = saisies[0]
        self.assertEqual(premiere.produit_id, self.castel)
        self.assertEqual(premiere.produit_nom, "Castel")
        self.assertEqual(premiere.table_nom, "12")
        self.assertEqual(premiere.ligne_uuid, uuid)
        self.assertEqual(premiere.config_id, self.config)
        self.assertEqual(premiere.company_id, self.company)
        self.assertEqual(premiere.order_ref, commande.pos_reference)
        self.assertTrue(premiere.date)

    def test_ouvrir_la_table_n_est_pas_une_saisie(self):
        addition = Addition(self.table_12, 4, self.awa)
        commande = self._commande_caisse(addition, self.awa)
        self.assertFalse(self._saisies(commande))
        # Resynchroniser sans changement : rien de plus.
        uuid = addition.ajouter(self.castel, 1)
        self._commande_caisse(addition, self.awa)
        self._commande_caisse(addition, self.awa)
        addition.changer(uuid, 1)
        self._commande_caisse(addition, self.awa)
        self.assertEqual(len(self._saisies(commande)), 1)

    def test_sans_contexte_l_employe_de_l_addition(self):
        """Poste verrouillé (synchronisation lancée par Odoo au retour au
        plan) : la saisie va à l'employé de l'addition, la dernière personne
        qui a ajouté un produit (pos_hr)."""
        addition = Addition(self.table_12, 4, self.awa)
        addition.ajouter(self.poulet, 1)
        commande = self._commande_caisse(addition, self.moussa, contexte=False)
        self.assertEqual(self._saisies(commande).employe_id, self.moussa)

    def test_baisse_et_retrait_ne_sont_pas_des_saisies(self):
        addition = Addition(self.table_12, 4, self.awa)
        uuid = addition.ajouter(self.castel, 3)
        commande = self._commande_caisse(addition, self.awa)
        addition.changer(uuid, 1)
        self._commande_caisse(addition, self.awa)
        addition.supprimer(uuid)
        self._commande_caisse(addition, self.awa)
        self.assertEqual(self._saisies(commande).mapped('quantite'), [3])

    def test_division_et_reunion_ne_sont_pas_des_saisies(self):
        # Table 12 : 3 Castel envoyées.
        table = Addition(self.table_12, 4, self.awa)
        castel = table.ajouter(self.castel, 3)
        table.envoyer()
        origine = self._commande_caisse(table, self.awa)
        # Division : 1 Castel passe dans la part « 12B » (Odoo synchronise
        # l'origine et la part ensemble, sous le contexte de déplacement).
        part = Addition(personnes=0, ouverte_par=self.awa, nom="12B")
        part.valeurs['aite_origine_uuid'] = origine.uuid
        castel_part = part.ajouter(self.castel, 1)
        part.preparation['lines'] = {castel_part: {
            'uuid': castel_part, 'product_id': self.castel.id, 'quantity': 1, 'note': ''}}
        part.preparation['metadata'] = dict(table.preparation['metadata'])
        table.changer(castel, 2)
        table.preparation['lines'][castel]['quantity'] = 2
        self._commande_caisse(table, self.awa, deplacement=True)
        commande_part = self._commande_caisse(part, self.awa, deplacement=True)
        self.assertEqual(origine.lines.aite_qte_envoyee, 2)
        self.assertEqual(commande_part.lines.aite_qte_envoyee, 1)
        # Réunion : la table 7 (2 Castel envoyées) est versée dans la table 12.
        table_7 = Addition(self.table_7, 3, self.awa)
        table_7.ajouter(self.castel, 2)
        table_7.envoyer()
        self._commande_caisse(table_7, self.awa)
        table.changer(castel, 4)
        table.preparation['lines'][castel]['quantity'] = 4
        self._commande_caisse(table, self.awa, deplacement=True)
        self.assertEqual(origine.lines.aite_qte_envoyee, 4)
        saisies = self.Saisie.search([('order_id', 'in', (origine | commande_part).ids)])
        self.assertEqual(saisies.mapped('quantite'), [3], "seule la saisie d'Awa à l'ouverture")

    def test_saisie_puis_encaissement_sans_envoi(self):
        addition = Addition(self.table_12, 2, self.awa)
        addition.ajouter(self.castel, 2)
        commande = self._commande_caisse(addition, self.carine, etat='paid', payer=self.especes)
        self.assertEqual(commande.state, 'paid')
        saisie = self._saisies(commande)
        self.assertEqual(saisie.quantite, 2)
        self.assertEqual(saisie.employe_id, self.carine)

    def test_journal_ni_modifie_ni_efface(self):
        addition = Addition(self.table_12, 4, self.awa)
        addition.ajouter(self.castel, 1)
        saisie = self._saisies(self._commande_caisse(addition, self.awa))
        admin = self.env.ref('base.user_admin')
        for qui in (saisie.with_user(self.compte_manager), saisie.with_user(admin),
                    saisie.sudo()):
            with self.subTest(qui=qui.env.user.name, su=qui.env.su):
                with self.assertRaises(UserError):
                    qui.write({'quantite': 5})
                with self.assertRaises(UserError):
                    qui.unlink()
        self.assertEqual(saisie.quantite, 1)

    def test_lecture_reservee_au_manager(self):
        addition = Addition(self.table_12, 4, self.awa)
        addition.ajouter(self.castel, 1)
        commande = self._commande_caisse(addition, self.awa)
        self.assertEqual(self.Saisie.with_user(self.compte_manager).search_count(
            [('order_id', '=', commande.id)]), 1)
        with self.assertRaises(AccessError):
            self.Saisie.with_user(self.compte_caisse).search([])

    def test_bouton_saisies_de_la_fiche(self):
        addition = Addition(self.table_12, 4, self.awa)
        addition.ajouter(self.castel, 1)
        commande = self._commande_caisse(addition, self.awa)
        action = commande.with_user(self.compte_manager).action_aite_saisies()
        self.assertEqual(action['res_model'], 'aite.restaurant.saisie')
        self.assertEqual(self.Saisie.search_count(action['domain']), 1)
