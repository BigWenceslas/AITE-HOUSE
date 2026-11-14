# -*- coding: utf-8 -*-
"""La caisse « Restaurant » créée juste après le plan comptable (partie 4.4).

Sur une base neuve, Odoo charge le plan comptable à la fin du chargement du
registre, après les crochets d'installation (``account/models/ir_module.py``,
``_register_hook``) : le crochet du module ne trouve alors aucun journal. La
caisse est créée ici, après ``super()``.

Seulement au **premier** chargement du plan de la société (elle n'avait pas
encore de plan) : un rechargement, ou le passage à une autre localisation,
ne crée jamais une caisse ni un journal sans geste de l'utilisateur, même si
le manager a entre-temps décoché « Service à table contrôlé » partout. Une
société créée plus tard (ou une succursale, qu'Odoo charge à la suite de sa
société mère) reçoit donc sa propre caisse au chargement de son plan, si
elle a déjà un entrepôt : Odoo 18 n'en crée d'office que pour la première
société de la base (et dans ses tests) ; sinon l'avertissement ci-dessous
est écrit et la caisse se crée à la main (notes de version, Limites).
"""
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    def _load(self, template_code, company, install_demo, force_create=True):
        company = company or self.env.company
        premier_chargement = not company.chart_template
        res = super()._load(template_code, company, install_demo, force_create)
        if not premier_chargement:
            return res
        try:
            # Point de sauvegarde : un échec ici ne doit pas défaire le plan
            # comptable ; il est journalisé (avertissement), pour ne pas
            # passer inaperçu.
            with self.env.cr.savepoint():
                self.env['pos.config']._aite_preparer_caisse(company)
        except Exception:
            _logger.warning(
                "Restaurant : caisse « Restaurant » non créée pour la société %s.",
                company.name, exc_info=True)
        return res
