# -*- coding: utf-8 -*-
"""La caisse au service à table contrôlé reçoit d'office le mode « Ardoise
client » d'aite_pos_credit (recette : l'intégrateur devait l'ajouter à la
main), à l'installation, à chaque mise à niveau et au premier chargement du
plan comptable d'une base neuve ; jamais en double."""
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_house_restaurant')
class TestArdoiseRestaurant(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.Methode = cls.env['pos.payment.method'].with_context(active_test=False)
        cls.restaurant = cls.env['pos.config'].search([
            ('company_id', '=', cls.company.id), ('aite_mode_restaurant', '=', True)])

    def _ardoises(self):
        return self.Methode.search([('is_aite_credit', '=', True),
                                    ('company_id', '=', self.company.id)])

    def _rejouer(self):
        """Ce que fait chaque mise à niveau du module (data/installer_data.xml)."""
        self.env['pos.config']._aite_restaurant_ajouter_ardoise()

    def test_caisse_restaurant_a_l_ardoise_d_office(self):
        """Base neuve installée d'un seul geste : la caisse « Restaurant »,
        créée après le plan comptable, propose « Ardoise client »."""
        self.assertTrue(self.restaurant, "la caisse au service à table contrôlé existe")
        ardoise = self._ardoises()
        self.assertEqual(len(ardoise), 1, "un seul mode d'ardoise dans la société")
        for caisse in self.restaurant:
            self.assertIn(ardoise, caisse.payment_method_ids, caisse.name)
        # Le mode d'aite_pos_credit, « payer plus tard » : réservé au manager
        # par les règles d'aite_pos_restaurant (aitePeut('ardoise')).
        self.assertEqual(ardoise.type, 'pay_later')
        self.assertTrue(ardoise.split_transactions, "« Identifier le client » coché")

    def test_rejouer_ne_double_rien(self):
        avant = (len(self._ardoises()), self.restaurant.mapped(lambda c: len(c.payment_method_ids)))
        self._rejouer()
        self._rejouer()
        self.assertEqual(
            (len(self._ardoises()), self.restaurant.mapped(lambda c: len(c.payment_method_ids))), avant)

    def test_ardoise_retiree_remise_a_la_mise_a_niveau(self):
        ardoise = self._ardoises()
        self.restaurant.write({'payment_method_ids': [(3, ardoise.id)]})
        self.assertNotIn(ardoise, self.restaurant.payment_method_ids)
        self._rejouer()
        self.assertIn(ardoise, self.restaurant.payment_method_ids)
        self.assertEqual(len(self._ardoises()), 1, "le mode existant est repris, pas recréé")

    def test_mode_cree_s_il_manque(self):
        """Une société sans aucun mode d'ardoise le reçoit (comme à
        l'installation d'aite_pos_credit), puis sa caisse au service à table."""
        ardoise = self._ardoises()
        self.restaurant.write({'payment_method_ids': [(3, ardoise.id)]})
        self.env['pos.config'].search([]).write({'payment_method_ids': [(3, ardoise.id)]})
        ardoise.unlink()
        self._rejouer()
        nouvelle = self._ardoises()
        self.assertEqual(len(nouvelle), 1)
        self.assertEqual(nouvelle.name, "Ardoise client")
        self.assertIn(nouvelle, self.restaurant.payment_method_ids)

    def test_ardoise_archivee_respectee(self):
        """Un mode d'ardoise archivé l'a été volontairement : ni recréé ni remis."""
        ardoise = self._ardoises()
        self.restaurant.write({'payment_method_ids': [(3, ardoise.id)]})
        ardoise.active = False
        self._rejouer()
        self.assertEqual(self._ardoises(), ardoise)
        self.assertFalse(self.restaurant.payment_method_ids.filtered('is_aite_credit'))

    def test_autre_caisse_non_touchee(self):
        """Seules les caisses au service à table contrôlé sont complétées."""
        bar = self.env['pos.config'].create({
            'name': "Bar de test", 'company_id': self.company.id,
            'payment_method_ids': [(6, 0, (self.Methode.search([
                ('company_id', '=', self.company.id), ('journal_id.type', '=', 'bank'),
                ('split_transactions', '=', False)], limit=1)).ids)]})
        self.assertFalse(bar.aite_mode_restaurant)
        self._rejouer()
        self.assertFalse(bar.payment_method_ids.filtered('is_aite_credit'))
