# -*- coding: utf-8 -*-
"""Tour de la caisse : « Mettre sur ardoise » hors service à table contrôlé.

Décision d'arbitrage sur AH-02 (incrément 4 du restaurant) : AH-02 avait
masqué le bouton d'ardoise sur toute caisse sans mode « ardoise », caisses de
l'hôtel comprises, alors qu'avant il affichait l'aide à la configuration.
Hors service à table contrôlé (``pos.aiteActif`` faux, ou absent quand
aite_pos_restaurant n'est pas installé), le comportement d'avant AH-02
revient exactement ; sur une caisse au service à table contrôlé, la règle
AH-02 reste (bouton pour le seul manager, et s'il existe un mode « ardoise »),
jouée par les tours d'aite_pos_restaurant.
"""
from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged('post_install', '-at_install', 'aite_pos_credit')
class TestArdoiseHorsMode(TestPointOfSaleHttpCommon):

    def test_bouton_affiche_sans_mode_ardoise(self):
        config = self.main_pos_config
        self.assertFalse(config.module_pos_restaurant)
        self.assertFalse(config.payment_method_ids.filtered('is_aite_credit'))
        if 'aite_mode_restaurant' in config._fields:
            self.assertFalse(config.aite_mode_restaurant)
        config.with_user(self.pos_user).open_ui()
        self.start_pos_tour('AiteArdoiseHorsModeTour', login='pos_user')
        # Rien n'a été encaissé : l'aide a été affichée, la vente attend.
        self.assertFalse(self.env['pos.order'].search_count([
            ('config_id', '=', config.id), ('state', 'in', ('paid', 'done', 'invoiced'))]))
