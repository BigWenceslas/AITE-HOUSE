# -*- coding: utf-8 -*-
"""Socle commun des tests de la caisse du restaurant (spécification, partie 6.2).

La caisse de test de ``TestPoSCommon`` passe en « Service à table contrôlé ».
Cinq employés aux quatre niveaux, **sans courriel** (le client n'en a pas pour
ses serveurs) : Awa 1111 et Moussa 2222 (serveurs), Carine 3333 (caissière),
Paul 4444 (chef de salle), Fanta 5555 (manager).

Deux comptes Odoo, comme les pose AITE (partie 4.4) :
* le compte de la caisse : « Utilisateur » du Point de Vente, avec un courriel
  et le droit Facturation (sans lui, les entrées et sorties d'espèces
  échouent) ; aucun droit sur les Employés ;
* le compte du manager : Administrateur du Point de Vente et Employés
  « Agent » (il saisit les niveaux et les codes).
"""
from odoo.addons.point_of_sale.tests.common import TestPoSCommon


class RestaurantCommon(TestPoSCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.basic_config
        cls.config.write({
            'module_pos_restaurant': True,
            'module_pos_hr': True,
            'aite_mode_restaurant': True,
        })

        Employe = cls.env['hr.employee']

        def employe(nom, code, niveau):
            return Employe.create({
                'name': nom,
                'pin': code,
                'aite_niveau_caisse': niveau,
                'company_id': cls.company.id,
            })

        cls.awa = employe("Awa", '1111', 'serveur')
        cls.moussa = employe("Moussa", '2222', 'serveur')
        cls.carine = employe("Carine", '3333', 'caissiere')
        cls.paul = employe("Paul", '4444', 'superviseur')
        cls.fanta = employe("Fanta", '5555', 'manager')
        cls.equipe = cls.awa | cls.moussa | cls.carine | cls.paul | cls.fanta

        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.compte_caisse = Users.create({
            'name': "Caisse du restaurant",
            'login': 'aite_caisse_resto',
            'email': 'caisse@restaurant.example',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('point_of_sale.group_pos_user').id,
                cls.env.ref('account.group_account_invoice').id,
            ])],
        })
        cls.compte_manager = Users.create({
            'name': "Manager du restaurant",
            'login': 'aite_manager_resto',
            'email': 'manager@restaurant.example',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('point_of_sale.group_pos_manager').id,
                cls.env.ref('hr.group_hr_user').id,
            ])],
        })

    # ------------------------------------------------------------------
    # Aides
    # ------------------------------------------------------------------

    def _ouvrir_session(self, config=None, code='3333'):
        """Session ouverte comme le fait la caisse : en mode, le code d'une
        personne qui peut ouvrir (Carine par défaut) est vérifié par le
        serveur (``aite_ouvrir_caisse``), puis le contrôle d'ouverture
        d'Odoo est validé (incrément 2)."""
        config = config or self.config
        config.open_ui()
        session = config.current_session_id
        caisse = session.with_user(self.compte_caisse)
        if config._aite_actif():
            self.assertNotIn('erreur', caisse.aite_ouvrir_caisse(code))
        caisse.set_opening_control(0, None)
        return session

    def _charger_caisse(self, config=None, user=None):
        """Ce que la caisse reçoit au démarrage : ``load_data`` sous le
        compte de la caisse (sans droit sur les Employés)."""
        config = config or self.config
        config.open_ui()
        session = config.current_session_id
        donnees = session.with_user(user or self.compte_caisse).load_data(
            ['pos.config', 'hr.employee'])
        return donnees
