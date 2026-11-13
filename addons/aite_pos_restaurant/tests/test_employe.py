# -*- coding: utf-8 -*-
"""REST-01 : un code de 4 chiffres, propre à chaque employé de la caisse
(spécification, parties 3.1, 4.2 et 6.2 ; message R23)."""
from unittest.mock import patch

from lxml import etree

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, tagged

from odoo.addons.aite_pos_restaurant.models import regles

from .common import RestaurantCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestEmploye(RestaurantCommon):

    def _creer(self, nom, code, niveau='serveur', user=None, company=None):
        Employe = self.env['hr.employee']
        if user:
            Employe = Employe.with_user(user)
        return Employe.create({
            'name': nom,
            'pin': code,
            'aite_niveau_caisse': niveau,
            'company_id': (company or self.company).id,
        })

    # ------------------------------------------------------------------
    # Refus (R23) : le message dit quoi faire
    # ------------------------------------------------------------------

    def test_niveau_sans_code_refuse(self):
        with self.assertRaises(ValidationError) as erreur:
            self._creer("Bertrand", False)
        self.assertEqual(
            erreur.exception.args[0],
            "Donnez un code à 4 chiffres à Bertrand : sans code, il ne peut "
            "pas utiliser la caisse.")

    def test_code_de_trois_chiffres_refuse(self):
        with self.assertRaises(ValidationError) as erreur:
            self._creer("Bertrand", '482')
        self.assertEqual(erreur.exception.args[0],
                         "Le code doit faire exactement 4 chiffres.")

    def test_code_avec_des_lettres_refuse(self):
        with self.assertRaises(ValidationError) as erreur:
            self._creer("Bertrand", '48a1')
        self.assertEqual(erreur.exception.args[0],
                         "Le code doit faire exactement 4 chiffres.")

    def test_code_deja_pris_refuse_sans_nommer_le_collegue(self):
        """Le manager (Employés « Agent ») donne à Moussa le code de Carine :
        refusé, et le message ne dit pas à qui est ce code."""
        with self.assertRaises(ValidationError) as erreur:
            self.moussa.with_user(self.compte_manager).write({'pin': '3333'})
        message = erreur.exception.args[0]
        self.assertEqual(
            message,
            "Le code 3333 est déjà celui d'un autre employé. Choisissez "
            "quatre autres chiffres : chaque employé a son propre code.")
        self.assertNotIn("Carine", message)

    def test_doublon_cree_par_le_manager_refuse(self):
        with self.assertRaises(ValidationError):
            self._creer("Bertrand", '1111', user=self.compte_manager)

    def test_doublon_par_un_employe_sans_droit_rh(self):
        """Spécification 6.2 : doublon créé par un utilisateur qui ne lit pas
        les codes des autres. Awa a un compte interne, sans droit sur les
        Employés ; le réglage RH « les employés modifient leurs propres
        données » est actif : dans ses préférences, elle se donne le code de
        Carine. Refusé (la recherche de la contrainte est en ``sudo()``),
        sans dire à qui est ce code (constat de revue n° 5)."""
        compte_awa = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': "Awa (compte)",
            'login': 'aite_awa_resto',
            'email': 'awa@restaurant.example',
            'company_id': self.company.id,
            'company_ids': [(6, 0, self.company.ids)],
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        self.awa.user_id = compte_awa
        self.env['ir.config_parameter'].sudo().set_param('hr.hr_employee_self_edit', True)
        self.assertFalse(compte_awa.has_group('hr.group_hr_user'))
        with self.assertRaises(AccessError):
            self.carine.with_user(compte_awa).read(['pin'])
        with self.assertRaises(ValidationError) as erreur:
            compte_awa.with_user(compte_awa).write({'pin': '3333'})
        self.assertEqual(
            erreur.exception.args[0],
            "Le code 3333 est déjà celui d'un autre employé. Choisissez "
            "quatre autres chiffres : chaque employé a son propre code.")
        self.assertNotIn("Carine", erreur.exception.args[0])
        compte_awa.with_user(compte_awa).write({'pin': '7171'})
        self.assertEqual(self.awa.pin, '7171')

    def test_doublon_dans_une_meme_creation_refuse(self):
        with self.assertRaises(ValidationError):
            self.env['hr.employee'].create([
                {'name': "Bertrand", 'pin': '6060', 'aite_niveau_caisse': 'serveur',
                 'company_id': self.company.id},
                {'name': "Bintou", 'pin': '6060', 'aite_niveau_caisse': 'serveur',
                 'company_id': self.company.id},
            ])

    def test_changement_de_societe_vers_un_code_pris_refuse(self):
        autre = self.env['res.company'].create({'name': "Autre restaurant"})
        employe = self._creer("Awa bis", '1111', company=autre)
        with self.assertRaises(ValidationError):
            employe.company_id = self.company

    def test_reactivation_d_un_archive_au_code_pris_refusee(self):
        ancien = self._creer("Ancien", '7777')
        ancien.action_archive()
        self._creer("Nouveau", '7777')  # le code est libre : l'ancien est parti
        with self.assertRaises(ValidationError):
            ancien.action_unarchive()

    def test_niveau_pose_apres_coup_controle_le_code(self):
        sans_niveau = self.env['hr.employee'].create({
            'name': "Plongeur", 'pin': '2222', 'company_id': self.company.id})
        with self.assertRaises(ValidationError):
            sans_niveau.aite_niveau_caisse = 'serveur'

    # ------------------------------------------------------------------
    # Ce qui reste permis
    # ------------------------------------------------------------------

    def test_meme_code_dans_une_autre_societe(self):
        autre = self.env['res.company'].create({'name': "Autre restaurant"})
        employe = self._creer("Awa bis", '1111', company=autre)
        self.assertEqual(employe.pin, '1111')

    def test_meme_code_sur_un_employe_sans_niveau(self):
        employe = self.env['hr.employee'].create({
            'name': "Comptable", 'pin': '1111', 'company_id': self.company.id})
        self.assertFalse(employe.aite_niveau_caisse)

    def test_employe_sans_niveau_ni_code(self):
        employe = self.env['hr.employee'].create({
            'name': "Jardinier", 'company_id': self.company.id})
        self.assertFalse(employe.pin)

    def test_dupliquer_un_employe_a_niveau(self):
        """« Dupliquer » la fiche d'Awa : la copie s'enregistre, sans niveau
        ni code (le code n'est jamais copié). Elle n'arrive donc pas en
        caisse tant que le manager ne lui a pas choisi un niveau, ce qui lui
        propose un code (constat de revue n° 4)."""
        copie = self.awa.with_user(self.compte_manager).copy()
        self.assertFalse(copie.aite_niveau_caisse)
        self.assertFalse(copie.pin)
        self.assertEqual(self.awa.aite_niveau_caisse, 'serveur')
        self.assertEqual(self.awa.pin, '1111')

    def test_aucun_courriel_demande(self):
        employe = self._creer("Bertrand", '8888')
        self.assertFalse(employe.work_email)
        self.assertFalse(employe.work_contact_id.email)

    # ------------------------------------------------------------------
    # Code proposé d'office
    # ------------------------------------------------------------------

    def test_code_propose_libre_et_a_quatre_chiffres(self):
        with patch.object(regles, 'code_libre', wraps=regles.code_libre) as espion:
            with Form(self.env['hr.employee'].with_user(self.compte_manager)) as fiche:
                fiche.name = "Bertrand"
                self.assertFalse(fiche.pin)
                fiche.aite_niveau_caisse = 'serveur'
                code = fiche.pin
        self.assertTrue(regles.code_valide(code), code)
        pris = set(espion.call_args.args[0])
        self.assertTrue({'1111', '2222', '3333', '4444', '5555'} <= pris)
        self.assertNotIn(code, pris)
        employe = self.env['hr.employee'].search([('name', '=', "Bertrand")])
        self.assertEqual(employe.pin, code)

    def test_code_deja_saisi_n_est_pas_remplace(self):
        with Form(self.env['hr.employee'].with_user(self.compte_manager)) as fiche:
            fiche.name = "Bertrand"
            fiche.pin = '6543'
            fiche.aite_niveau_caisse = 'caissiere'
            self.assertEqual(fiche.pin, '6543')

    # ------------------------------------------------------------------
    # La fiche : niveau et code sur la première page
    # ------------------------------------------------------------------

    def test_niveau_et_code_sur_la_premiere_page(self):
        arch = self.env['hr.employee'].with_user(self.compte_manager).get_view(
            view_type='form')['arch']
        fiche = etree.fromstring(arch)
        for champ in ('aite_niveau_caisse', 'pin'):
            with self.subTest(champ=champ):
                self.assertEqual(len(fiche.xpath("//field[@name='%s']" % champ)), 1)
                self.assertFalse(fiche.xpath("//notebook//field[@name='%s']" % champ))
        groupe = fiche.xpath("//group[@name='aite_caisse_restaurant']")
        self.assertEqual(len(groupe), 1)
        self.assertEqual(groupe[0].get('string'), "Caisse du restaurant")
        self.assertEqual(
            fiche.xpath("//field[@name='pin']")[0].get('string'), "Code caisse")
        texte = " ".join("".join(groupe[0].itertext()).split())
        self.assertIn("ne le communiquez qu'à l'employé", texte)
        self.assertIn("Vide : l'employé n'apparaît pas sur la caisse.", texte)
