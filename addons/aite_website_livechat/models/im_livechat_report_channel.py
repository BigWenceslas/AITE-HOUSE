# -*- coding: utf-8 -*-
import logging

from odoo import models
from odoo.tools import SQL

_logger = logging.getLogger(__name__)

# Sous-requête des messages de chaque conversation, dans le rapport natif.
_MESSAGES_FILTER = "WHERE M.res_id = C.id and M.model = 'discuss.channel'"


class ImLivechatReportChannel(models.Model):
    _inherit = 'im_livechat.report.channel'

    def _from(self) -> SQL:
        # Live Chat → Rapports → Sessions : le délai de première réponse et
        # le nombre de messages se calculent sur les messages de la
        # conversation. Le message d'absence (message automatique, signé de
        # l'opérateur) n'est pas une réponse : il est écarté, sinon chaque
        # conversation hors ligne aurait l'air répondue en une seconde.
        query = super()._from()
        if query.code.count(_MESSAGES_FILTER) != 1:
            _logger.warning(
                "aite_website_livechat : rapport du Live Chat modifié par Odoo, "
                "le message d'absence y compte comme une réponse.")
            return query
        code = query.code.replace(
            _MESSAGES_FILTER, f"{_MESSAGES_FILTER} AND M.message_type != 'auto_comment'")
        return SQL(code, *query.params)
