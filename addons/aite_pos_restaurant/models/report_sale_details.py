# -*- coding: utf-8 -*-
"""Le rapport de fermeture : tables, personnes et annulations (REST-25
critère 5, Q51, REST-22 ; spécification, partie 5.3 ; incrément 6).

``get_sale_details`` d'Odoo sert les deux gabarits qui l'impriment : celui de
la caisse (« Imprimer le rapport », ``point_of_sale.SaleDetailsReport``) et
celui de la gestion (rapport de session et « Détails des ventes »,
``point_of_sale.pos_session_sales_details``). On y ajoute, sur les mêmes
additions réglées (le domaine d'Odoo : la session du rapport, ou la période
et les caisses choisies) :

- ``aite_tables``, ``aite_personnes``, ``aite_sans_table`` : les sommes des
  compteurs de « Personnes et tables » (partie 5.2) ;
- ``aite_annulations`` (table, produit, quantité, montant, motif, autorisée
  par) et ``aite_annulations_total`` : le journal des annulations de la
  session, ou de la période et des caisses ; il est lu en ``sudo()`` (le
  compte de la caisse ne le lit pas), dans les sociétés de l'utilisateur ;
- ``aite_restaurant`` : vrai si le rapport porte sur une caisse au service à
  table contrôlé ; les gabarits n'affichent ces lignes que dans ce cas (une
  caisse de bar ou une boutique garde le rapport d'Odoo).

Le rapport par employé de ``pos_hr`` hérite de ce rapport et passe
``employee_id`` : les tables sont celles des additions de l'employé (le
domaine de pos_hr), les annulations celles qu'il a demandées.

Le chef de salle n'a rien à rédiger : il signe le rapport.
"""
from odoo import _, api, models


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False,
                         session_ids=False, **kwargs):
        donnees = super().get_sale_details(date_start, date_stop, config_ids, session_ids,
                                           **kwargs)
        donnees.update(self._aite_restaurant(date_start, date_stop, config_ids, session_ids,
                                             **kwargs))
        return donnees

    @api.model
    def _aite_restaurant(self, date_start, date_stop, config_ids, session_ids, **kwargs):
        """Les lignes du restaurant, sur les additions mêmes du rapport."""
        if not session_ids:
            date_start, date_stop = self._get_date_start_and_date_stop(date_start, date_stop)
        commandes = self.env['pos.order'].search(
            self._get_domain(date_start, date_stop, config_ids, session_ids, **kwargs))
        sessions = self.env['pos.session'].browse(session_ids or []).exists()
        caisses = commandes.config_id | sessions.config_id \
            | self.env['pos.config'].browse(config_ids or []).exists()
        actif = any(caisse._aite_actif() for caisse in caisses)

        domaine = [('company_id', 'in', self.env.companies.ids)]
        if session_ids:
            domaine.append(('session_id', 'in', list(session_ids)))
        else:
            domaine += [('date', '>=', date_start), ('date', '<=', date_stop)]
            if config_ids:
                domaine.append(('config_id', 'in', list(config_ids)))
        if kwargs.get('employee_id'):
            domaine.append(('serveur_id', '=', kwargs['employee_id']))
        natures = dict(self.env['aite.restaurant.annulation']._fields[
            'type_annulation']._description_selection(self.env))
        annulations = []
        quantite = montant = 0.0
        devise = self.env.company.currency_id
        for trace in self.env['aite.restaurant.annulation'].sudo().search(
                domaine, order='date, id'):
            motif = trace.motif_nom or natures.get(trace.type_annulation) or ''
            if trace.commentaire:
                motif = _("%(motif)s\u00a0: %(precision)s", motif=motif,
                          precision=trace.commentaire)
            annulations.append({
                'table': trace.table_nom or '',
                'produit': trace.produit_nom or '',
                'quantite': trace.quantite,
                'montant': trace.montant,
                'motif': motif,
                'autorisee_par': trace.superieur_nom or '',
            })
            quantite += trace.quantite
            montant += trace.montant
        return {
            'aite_restaurant': actif,
            'aite_tables': sum(commandes.mapped('aite_tables')),
            'aite_personnes': sum(commandes.mapped('aite_personnes')),
            'aite_sans_table': sum(commandes.mapped('aite_sans_table')),
            'aite_annulations': annulations,
            'aite_annulations_total': {'quantite': quantite, 'montant': devise.round(montant)},
        }
