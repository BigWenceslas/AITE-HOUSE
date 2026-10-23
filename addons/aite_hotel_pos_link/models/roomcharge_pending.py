# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RoomchargePending(models.Model):
    """
    Notes de chambre en attente de rattachement : la réception choisit
    le folio et valide — le report réutilise le même chemin idempotent
    que le rattachement automatique.
    """
    _name = 'aite.roomcharge.pending'
    _description = "Note de chambre en attente"
    _order = 'create_date desc'

    # Nom affiché (fil d'Ariane, liens) : le numéro du ticket. Sans lui, la
    # fiche s'intitulait « aite.roomcharge.pending,12 ». Champ stocké : la
    # réception, sans droit sur la caisse, n'a pas à lire ``pos.order``.
    name = fields.Char(
        string="Ticket", related='order_id.name', store=True, readonly=True)
    order_id = fields.Many2one(
        'pos.order', string="Commande POS", required=True,
        ondelete='cascade', index=True,
    )
    partner_id = fields.Many2one('res.partner', string="Client")
    company_id = fields.Many2one(
        related='order_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one(
        related='order_id.currency_id', readonly=True)
    amount = fields.Monetary(
        string="Montant", currency_field='currency_id', readonly=True)
    note = fields.Char(string="Motif", readonly=True)
    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio choisi",
        domain="[('state', '=', 'open')]",
    )
    # Folios proposés à la réception : ceux des séjours commencés (client
    # arrivé, ou parti sans que son folio soit facturé), et seulement ceux du
    # client du ticket s'il en a. Avant, la liste offrait tous les folios
    # ouverts de tous les clients, y compris ceux des réservations à venir.
    folio_candidate_ids = fields.Many2many(
        'aite.hotel.folio', string="Folios proposés",
        compute='_compute_folio_candidate_ids',
    )
    state = fields.Selection(
        selection=[('todo', "À rattacher"), ('done', "Rattachée")],
        string="État", default='todo', required=True, index=True,
    )

    @api.depends('partner_id', 'company_id')
    def _compute_folio_candidate_ids(self):
        Folio = self.env['aite.hotel.folio']
        for rec in self:
            # Séjours commencés : « Arrivé », mais aussi « Parti » — le départ
            # avec « Générer la facture » décoché laisse le folio ouvert, et
            # une consommation du dernier soir doit encore pouvoir s'y
            # ajouter. Seuls les séjours pas encore commencés (brouillon,
            # confirmé) sont écartés ; un folio facturé n'est plus « open ».
            started = Folio.search([
                ('state', '=', 'open'),
                ('reservation_id.state', 'in', ('checked_in', 'checked_out')),
                ('company_id', '=', (rec.company_id or self.env.company).id),
            ])
            mine = started.filtered(
                lambda f: rec.partner_id and f.partner_id == rec.partner_id)
            # Client sans séjour commencé (ticket pris au nom d'un invité,
            # d'une société…) : la réception garde le choix parmi les séjours
            # commencés plutôt qu'une liste vide.
            rec.folio_candidate_ids = mine or started

    def action_resolve(self):
        for rec in self:
            if rec.state == 'done':
                continue
            if not rec.folio_id:
                raise UserError(_("Choisissez d'abord un folio ouvert."))
            if rec.folio_id.state != 'open':
                raise UserError(_(
                    "Le folio %(f)s n'est plus ouvert.",
                    f=rec.folio_id.name))
            # Lecture technique du ticket en ``sudo()`` : la réception
            # tranche la file sans avoir de droit sur la caisse (même règle
            # que ``_aite_post_to_folio``).
            order = rec.order_id.sudo()
            if order.aite_folio_line_id:
                rec.state = 'done'
                continue
            if order._aite_post_to_folio(rec.folio_id, rec.amount):
                rec.state = 'done'
                # Complète le client si la commande n'en avait pas
                if not rec.partner_id:
                    rec.partner_id = rec.folio_id.partner_id.id
        return True


class HotelFolio(models.Model):
    _inherit = 'aite.hotel.folio'

    # Choisir un folio en tapant le nom du client (file d'attente des notes
    # de chambre, et tout champ « Folio »).
    _rec_names_search = ['name', 'partner_id.name']

    @api.depends('name', 'partner_id.name')
    @api.depends_context('aite_folio_with_partner')
    def _compute_display_name(self):
        """Référence suivie du client quand l'écran le demande (contexte
        ``aite_folio_with_partner``) : « FOL/2026/0012 — Mballa Jean »."""
        super()._compute_display_name()
        if not self.env.context.get('aite_folio_with_partner'):
            return
        for folio in self:
            if folio.name and folio.partner_id:
                folio.display_name = "%s — %s" % (
                    folio.name, folio.partner_id.name)
