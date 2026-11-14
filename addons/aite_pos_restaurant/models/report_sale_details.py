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
  chaque quantité est aussi écrite par le serveur (``quantite_texte``), dans
  la langue de l'utilisateur et sans zéros inutiles (« 2 », « 1,5 ») ;
- ``aite_restaurant`` : vrai si le rapport porte sur une caisse au service à
  table contrôlé ; les gabarits n'affichent ces lignes que dans ce cas (une
  caisse de bar ou une boutique garde le rapport d'Odoo).

Le rapport par employé de ``pos_hr`` (``employee_id``, coché d'office dans
l'assistant de la session) garde le rapport d'Odoo : son gabarit pose les
variables une à une, sans les nôtres, et la spécification ne demande rien par
employé ; on n'y ajoute donc rien.

Le chef de salle n'a rien à rédiger : il signe le rapport.

Limite d'Odoo : dès qu'une session a une vente payée, ``get_sale_details``
lit les paiements comptables (``account.payment``) ; le compte qui ouvre le
rapport depuis la gestion doit avoir le droit Facturation (comme le compte de
la caisse, partie 4.4).
"""
from odoo import _, api, models


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False,
                         session_ids=False, **kwargs):
        donnees = super().get_sale_details(date_start, date_stop, config_ids, session_ids,
                                           **kwargs)
        if kwargs.get('employee_id'):
            # Rapport par employé de pos_hr : le rapport d'Odoo, tel quel.
            donnees['aite_restaurant'] = False
            return donnees
        donnees.update(self._aite_restaurant(date_start, date_stop, config_ids, session_ids,
                                             **kwargs))
        return donnees

    @api.model
    def _aite_quantite_texte(self, quantite):
        """Une quantité écrite dans la langue de l'utilisateur, sans zéros
        inutiles : « 2 », « 1,5 », « 1 000 » en français (« 1.5 » en
        anglais)."""
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        gabarit = '%.{}f'.format(precision)
        langue = self.env['res.lang']._lang_get(self.env.lang or self.env.user.lang or 'en_US')
        if langue:
            texte, virgule = langue.format(gabarit, quantite or 0.0, grouping=True), \
                langue.decimal_point
        else:  # langue absente de la base : l'écriture de Python
            texte, virgule = gabarit % (quantite or 0.0), '.'
        if virgule and virgule in texte:
            entier, decimales = texte.rsplit(virgule, 1)
            decimales = decimales.rstrip('0')
            texte = entier + (virgule + decimales if decimales else '')
        return texte

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
        natures = dict(self.env['aite.restaurant.annulation']._fields[
            'type_annulation']._description_selection(self.env))
        annulations = []
        quantite = montant = 0.0
        devise = self.env.company.currency_id
        for trace in self.env['aite.restaurant.annulation'].sudo().search(
                domaine, order='date, id'):
            motif = trace.motif_nom or natures.get(trace.type_annulation) or ''
            if trace.commentaire:
                motif = _("%(motif)s : %(precision)s", motif=motif,
                          precision=trace.commentaire)
            annulations.append({
                'table': trace.table_nom or '',
                'produit': trace.produit_nom or '',
                'quantite': trace.quantite,
                'quantite_texte': self._aite_quantite_texte(trace.quantite),
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
            'aite_annulations_total': {
                'quantite': quantite, 'quantite_texte': self._aite_quantite_texte(quantite),
                'montant': devise.round(montant)},
        }
