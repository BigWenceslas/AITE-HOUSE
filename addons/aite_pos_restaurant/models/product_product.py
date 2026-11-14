# -*- coding: utf-8 -*-
"""Ce qui reste des produits suivis en stock, pour la caisse (spécification,
T20, parties 4.1 et 4.2 ; incrément 5, REST-19a et REST-19b critère 4).

Une seule requête pour toute la carte : pour chaque produit suivi (case
« Suivre l'inventaire », ``is_storable``) proposé en caisse, la quantité en
stock de l'entrepôt de la caisse **moins** ce qui est déjà parti en cuisine ou
au bar sur les additions encore ouvertes de cet entrepôt, tous postes et
toutes caisses confondus (``aite_qte_envoyee``, tenu par le serveur). La
caisse garde la réponse 60 secondes et retire elle-même ce qu'elle a saisi
sans l'envoyer sur l'addition en cours.

Ni un plat sans suivi, ni un kit de Fabrication (son stock est celui de ses
composants) n'y figurent : la caisse ne les refuse jamais. Le stock suppose le
mode « temps réel » de la société, réglage par défaut d'Odoo (une table
encaissée sort du stock aussitôt) ; un produit suivi vendu dans une formule
n'est pas contrôlé (partie 8.3).
"""
from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def aite_stock_disponible(self, config_id):
        """Requête de la caisse : ``{product_id: disponible}`` pour les
        produits suivis proposés en caisse. Le disponible peut être négatif
        (plus de bouteilles parties que de bouteilles en stock) : la caisse
        refuse tout ce qui n'a pas au moins une unité. Lecture seule, sous le
        compte de la caisse (il lit les produits, le stock et les additions)."""
        config = self.env['pos.config'].browse(int(config_id)).exists()
        if not config:
            return {}
        entrepot = config.picking_type_id.warehouse_id
        domaine = [
            ('is_storable', '=', True),
            ('available_in_pos', '=', True),
            '|', ('company_id', '=', False), ('company_id', '=', config.company_id.id),
        ]
        produits = self.with_company(config.company_id).search(domaine)
        if 'is_kits' in self._fields:  # Fabrication installée
            produits = produits.filtered(lambda p: not p.is_kits)
        if not produits:
            return {}
        contexte = {'warehouse_id': entrepot.id} if entrepot else {}
        en_stock = {
            produit.id: produit.qty_available
            for produit in produits.with_context(**contexte)
        }
        domaine_lignes = [
            ('order_id.state', '=', 'draft'),
            ('order_id.company_id', '=', config.company_id.id),
            ('product_id', 'in', produits.ids),
            ('aite_qte_envoyee', '>', 0),
        ]
        if entrepot:
            # Les caisses de cet entrepôt (recherche technique : le compte de
            # la caisse n'a pas à lire les types d'opération de stock).
            caisses = self.env['pos.config'].sudo().with_context(active_test=False).search([
                ('company_id', '=', config.company_id.id),
                ('picking_type_id.warehouse_id', '=', entrepot.id),
            ])
            domaine_lignes.append(('order_id.config_id', 'in', caisses.ids))
        partis = {
            produit.id: quantite
            for produit, quantite in self.env['pos.order.line']._read_group(
                domaine_lignes, ['product_id'], ['aite_qte_envoyee:sum'])
        }
        return {
            produit_id: quantite - partis.get(produit_id, 0.0)
            for produit_id, quantite in en_stock.items()
        }
