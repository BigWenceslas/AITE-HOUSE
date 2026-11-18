# -*- coding: utf-8 -*-
"""Le mode « Ardoise client » d'aite_pos_credit sur la caisse au service à
table contrôlé d'aite_pos_restaurant (recette : l'intégrateur devait
l'ajouter à la main).

Appelé à l'installation et à chaque mise à niveau (data/installer_data.xml),
et juste après le premier chargement du plan comptable d'une société
(account_chart_template.py : sur une base neuve, la caisse « Restaurant »
naît à ce moment-là, après les données des modules).

Le mode est celui d'aite_pos_credit : la case « Vente à crédit (ardoise) »
(``is_aite_credit``) le reconnaît ; il n'est jamais créé en double. Une
société qui n'en a aucun le reçoit comme à l'installation d'aite_pos_credit
(``hooks._setup_company``) ; un mode archivé l'a été volontairement : il
n'est ni recréé ni remis. Qui peut s'en servir à la caisse reste décidé par
les règles d'aite_pos_restaurant (``aitePeut('ardoise')`` : le manager).
Écriture technique, en ``sudo()``.
"""
import logging

from odoo import api, models

from odoo.addons.aite_pos_credit import hooks as hooks_ardoise

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _aite_restaurant_ajouter_ardoise(self, companies=None, creer=True):
        """Ajoute le mode d'ardoise de chaque société à ses caisses au service
        à table contrôlé qui ne l'ont pas. ``creer`` : créer le mode d'une
        société qui n'en a aucun (même archivé)."""
        Config = self.sudo()
        Methode = self.env['pos.payment.method'].sudo().with_context(active_test=False)
        for company in companies or self.env['res.company'].sudo().search([]):
            caisses = Config.search([('company_id', '=', company.id),
                                     ('aite_mode_restaurant', '=', True)])
            if not caisses:
                continue
            domaine = [('is_aite_credit', '=', True), ('company_id', '=', company.id)]
            ardoises = Methode.search(domaine)
            if not ardoises and creer:
                try:
                    with self.env.cr.savepoint():
                        hooks_ardoise._setup_company(Config.env, company)
                except Exception:
                    _logger.warning("Restaurant : mode « %s » non créé pour la société %s.",
                                    hooks_ardoise.CREDIT_METHOD_NAME, company.name, exc_info=True)
                ardoises = Methode.search(domaine)
            ardoise = ardoises.filtered('active')[:1]
            if not ardoise:
                if ardoises:
                    _logger.info("Restaurant : le mode d'ardoise de la société %s est archivé ; "
                                 "il n'est pas ajouté aux caisses.", company.name)
                continue
            for caisse in caisses.filtered(lambda c: ardoise not in c.payment_method_ids):
                try:
                    # Point de sauvegarde : une caisse dont la session est
                    # ouverte refuse un nouveau mode ; les autres le reçoivent.
                    with self.env.cr.savepoint():
                        caisse.payment_method_ids = [(4, ardoise.id)]
                    _logger.info("Restaurant : mode « %s » ajouté à la caisse %s.",
                                 ardoise.name, caisse.name)
                except Exception:
                    _logger.warning(
                        "Restaurant : mode « %s » non ajouté à la caisse %s (session ouverte ?) : "
                        "l'ajouter à la main, caisse fermée.", ardoise.name, caisse.name,
                        exc_info=True)
