# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import api, fields, models

from odoo.addons.mail.tools.discuss import Store


class DiscussChannelMember(models.Model):
    _inherit = 'discuss.channel.member'

    def _compute_message_unread(self):
        super()._compute_message_unread()
        # Le message d'absence est signé de l'opérateur, mais publié pendant
        # son absence : ce n'est pas un message qu'il lui reste à lire. Un
        # message du visiteur compte pour un non lu, pas pour deux.
        livechat_members = self.filtered(
            lambda member: member.partner_id and member.channel_id.channel_type == 'livechat')
        if not livechat_members.ids:
            return
        self.env.cr.execute("""
            SELECT member.id, COUNT(message.id)
              FROM discuss_channel_member member
              JOIN mail_message message
                ON message.res_id = member.channel_id
               AND message.model = 'discuss.channel'
             WHERE member.id IN %s
               AND message.message_type = 'auto_comment'
               AND message.author_id = member.partner_id
               AND message.id >= member.new_message_separator
          GROUP BY member.id
        """, [tuple(livechat_members.ids)])
        for member_id, count in self.env.cr.fetchall():
            member = self.browse(member_id)
            member.message_unread_counter = max(member.message_unread_counter - count, 0)

    @api.autovacuum
    def _gc_unpin_livechat_sessions(self):
        """ Nettoyage quotidien d'Odoo (même règle que le natif) : une
        conversation du chat dont un membre a tout lu et n'est pas revenu
        depuis un jour est retirée de son interface et close.

        En plus : pour un canal toujours joignable, une conversation qui
        attend encore la réponse d'un opérateur, ou dont la réponse n'a pas
        encore été vue par le visiteur, reste ouverte jusqu'à 7 jours après
        son dernier message. L'opérateur peut répondre, le visiteur revenir
        la lire. (La règle d'Odoo est reprise ici, sans appel à l'originale :
        elle ne permet pas d'écarter des conversations.) """
        kept = self.env['discuss.channel']._aite_sessions_kept_open()
        members = self.env['discuss.channel.member'].search([
            ('is_pinned', '=', True),
            ('last_seen_dt', '<=', datetime.now() - timedelta(days=1)),
            ('channel_id.channel_type', '=', 'livechat'),
            ('channel_id', 'not in', kept.ids),
        ])
        sessions_to_be_unpinned = members.filtered(lambda m: m.message_unread_counter == 0)
        sessions_to_be_unpinned.write({'unpin_dt': fields.Datetime.now()})
        sessions_to_be_unpinned.channel_id.livechat_end_dt = fields.Datetime.now()
        for member in sessions_to_be_unpinned:
            Store(bus_channel=member._bus_channel()).add(
                member.channel_id,
                {"close_chat_window": True, "livechat_end_dt": fields.Datetime.now()},
            ).bus_send()
