# -*- coding: utf-8 -*-
from odoo.http import request

from odoo.addons.im_livechat.controllers.webclient import WebClient
from odoo.addons.mail.tools.discuss import Store


class AiteLivechatWebClient(WebClient):

    @classmethod
    def _process_request_for_all(cls, store: Store, name, params):
        super()._process_request_for_all(store, name, params)
        if name != "init_livechat":
            return
        # Le navigateur du visiteur demande s'il doit afficher la bulle. Le
        # natif répond oui s'il y a un chatbot ou un opérateur « en ligne » ;
        # un canal toujours joignable répond oui dès qu'il a un opérateur,
        # sauf sur les pages où une règle masque la bulle. Jamais l'inverse :
        # une réponse positive du natif n'est pas remise en cause.
        # sudo - im_livechat.channel: comme le natif, pour savoir si la bulle
        # doit s'afficher.
        channel = request.env["im_livechat.channel"].sudo().search([("id", "=", params)])
        if not channel or not channel._aite_is_always_reachable():
            return
        country_id = (
            # sudo - res.country: accessing user country is allowed.
            request.env["res.country"].sudo().search([("code", "=", code)], limit=1).id
            if (code := request.geoip.country_code)
            else None
        )
        url = request.httprequest.headers.get("Referer")
        # sudo - im_livechat.channel.rule: getting channel's rule is allowed.
        rule = request.env["im_livechat.channel.rule"].sudo().match_rule(params, url, country_id)
        if rule.action != "hide_button":
            store.add_global_values(livechat_available=True)
