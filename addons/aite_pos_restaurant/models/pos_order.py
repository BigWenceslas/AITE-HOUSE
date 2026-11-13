# -*- coding: utf-8 -*-
"""L'addition côté serveur : qui a ouvert la table, quand, qui a encaissé,
qui a saisi quoi, ce qui est parti (spécification, T9, T11, T19, parties 3.1
et 4.2 ; incrément 3).

Le serveur écrit tout ce que la caisse lui envoie (``_process_order``) et
n'appelle jamais ``pos.order.line._is_field_accepted`` : les champs qu'il
tient seul sont donc retirés de la charge reçue (addition et commandes de
ligne), et des écritures directes du compte de la caisse.

- « Ouverte par » et « Addition d'origine » sont posés par la caisse à la
  création de l'addition, puis figés ;
- l'heure d'ouverture est posée par le serveur, à sa propre horloge, à la
  première synchronisation qui porte au moins une personne ; ensuite il
  n'accepte qu'une heure plus ancienne (réunion : la plus ancienne des deux
  tables ; part « 12B » : celle de l'origine) ;
- « Encaissée par » est l'employé de l'addition au moment du paiement (pos_hr
  y met la personne qui valide) ;
- à chaque synchronisation, chaque hausse de quantité d'une ligne va au
  journal des saisies, au nom de la personne identifiée sur le poste
  (contexte ``aite_employee_id`` posé par la caisse ; à défaut, l'employé de
  l'addition), sauf pendant une division ou une réunion (contexte
  ``aite_deplacement``) ; ce qui est parti (``aite_qte_envoyee``) suit les
  envois ;
- rien n'est refusé à la synchronisation (une erreur bloquerait toutes les
  synchronisations suivantes du poste, paiements compris) : un encaissement,
  un remboursement ou une vente sans table hors des droits, une table à 0
  personne, sont notés dans l'historique de l'addition.

Hors du service à table contrôlé, rien de tout cela : la caisse n'est pas
touchée.
"""
import json
import logging

from odoo import _, api, fields, models
from odoo.tools import float_compare

from . import regles
from .pos_order_line import CHAMPS_LIGNE_SERVEUR
from .pos_session import contexte_serveur, ecrit_par_le_serveur

_logger = logging.getLogger(__name__)

# Écrits par le serveur seul : retirés de toute charge reçue. Les compteurs
# de « Personnes et tables » (incrément 6) et « Réunie à une autre table »
# (incrément 4) sont déjà dans la liste : la caisse ne les écrira jamais. Le
# mode de la caisse, lu sur la caisse, ne s'écrit jamais par l'addition.
CHAMPS_SERVEUR = (
    'aite_encaissee_par_id', 'aite_heure_ouverture', 'aite_fusionnee',
    'aite_tables', 'aite_personnes', 'aite_sans_table', 'aite_articles',
    'aite_mode_restaurant',
)
# Posés par la caisse à la création, puis figés.
CHAMPS_FIGES = ('aite_ouverte_par_id', 'aite_origine_uuid')
ETATS_REGLES = ('paid', 'done', 'invoiced')
PRECISION = 6


class PosOrder(models.Model):
    _inherit = 'pos.order'

    aite_ouverte_par_id = fields.Many2one(
        'hr.employee', string="Ouverte par", readonly=True, copy=False,
        index='btree_not_null',
        help="L'employé qui a ouvert la table, reconnu par son code. Ne change "
             "plus ensuite.")
    aite_heure_ouverture = fields.Datetime(
        string="Heure d'ouverture", readonly=True, copy=False,
        help="Le moment où le nombre de personnes a été validé, à l'horloge du "
             "serveur. L'alerte orange se compte depuis cette heure, même après "
             "un déplacement, une division ou une réunion.")
    aite_encaissee_par_id = fields.Many2one(
        'hr.employee', string="Encaissée par", readonly=True, copy=False,
        help="L'employé qui a validé le paiement avec son code.")
    aite_origine_uuid = fields.Char(
        string="Addition d'origine", readonly=True, copy=False,
        help="Rempli sur une part née d'une division (12B).")
    # Le bouton « Saisies » de la fiche suit le mode de la caisse, et non
    # « Ouverte par » : une addition ouverte avant la mise à niveau, ou une
    # copie ancienne, a des saisies sans « ouverte par ».
    aite_mode_restaurant = fields.Boolean(
        related='config_id.aite_mode_restaurant', string="Service à table contrôlé")

    # ------------------------------------------------------------------
    # Champs protégés (partie 3.1)
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        if not ecrit_par_le_serveur(self.env):
            vals_list = [{champ: valeur for champ, valeur in vals.items()
                          if champ not in CHAMPS_SERVEUR} for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        if ecrit_par_le_serveur(self.env):
            return super().write(vals)
        vals = {champ: valeur for champ, valeur in vals.items() if champ not in CHAMPS_SERVEUR}
        figes = [champ for champ in CHAMPS_FIGES if champ in vals]
        if figes and len(self) > 1:
            for commande in self:
                commande.write(vals)
            return True
        if figes and self:
            vals = {champ: valeur for champ, valeur in vals.items()
                    if not (champ in figes and self[champ])}
        return super().write(vals)

    # ------------------------------------------------------------------
    # La synchronisation de la caisse
    # ------------------------------------------------------------------

    @api.model
    def _process_order(self, order, existing_order):
        config = (existing_order or self.env['pos.session'].browse(
            order.get('session_id')).exists()).config_id
        if len(config) != 1 or not config._aite_actif():
            return super()._process_order(order, existing_order)

        # 1. Ce que le serveur tient seul est retiré de la charge reçue.
        heure_recue = order.pop('aite_heure_ouverture', False)
        for champ in CHAMPS_SERVEUR + CHAMPS_LIGNE_SERVEUR:
            order.pop(champ, None)
        if existing_order:
            for champ in CHAMPS_FIGES:
                if existing_order[champ]:
                    order.pop(champ, None)
        for commande in order.get('lines') or []:
            if isinstance(commande, (list, tuple)) and len(commande) > 2 \
                    and isinstance(commande[2], dict):
                for champ in CHAMPS_LIGNE_SERVEUR:
                    commande[2].pop(champ, None)

        # 2. Photographie des lignes avant l'écriture.
        avant = {}
        if existing_order:
            for ligne in existing_order.lines:
                avant[ligne.uuid] = (ligne.qty, ligne.aite_qte_envoyee,
                                     ligne.aite_qte_preparation, ligne.product_id,
                                     ligne.full_product_name)
        etait_reglee = bool(existing_order) and existing_order.state in ETATS_REGLES

        order_id = super()._process_order(order, existing_order)

        commande = self.browse(order_id).with_context(**contexte_serveur())
        commande._aite_apres_synchronisation(avant, heure_recue, etait_reglee)
        return order_id

    def _aite_apres_synchronisation(self, avant, heure_recue, etait_reglee):
        """Après l'écriture d'Odoo : heure, personnes, « encaissée par »,
        journal des saisies, quantités parties, notes."""
        self.ensure_one()
        notes = []
        vals = {}

        # Une table à 0 personne est ramenée à 1 (l'étape « personnes » n'a
        # pas de zéro ; une copie ancienne ou forgée peut l'envoyer).
        personnes = self.customer_count
        if self.table_id and personnes < 1 and self.state != 'cancel':
            personnes = vals['customer_count'] = 1
            notes.append(_(
                "La table %(table)s est arrivée à 0 personne : ramenée à 1.",
                table=self.table_id.table_number))

        # L'heure d'ouverture, à l'horloge du serveur.
        maintenant = fields.Datetime.now()
        heure = self._aite_heure(heure_recue)
        actuelle = self.aite_heure_ouverture
        if heure and heure <= maintenant and (not actuelle or heure < actuelle):
            vals['aite_heure_ouverture'] = heure
        elif not actuelle and personnes >= 1:
            vals['aite_heure_ouverture'] = maintenant

        # « Encaissée par » : l'employé de l'addition au paiement.
        if self.state in ETATS_REGLES and not etait_reglee and not self.aite_encaissee_par_id:
            employe = self.employee_id
            if employe:
                vals['aite_encaissee_par_id'] = employe.id
            notes += self._aite_notes_d_encaissement(employe, personnes)

        if vals:
            self.write(vals)
        self._aite_bilan_des_lignes(avant)
        for note in notes:
            self._message_log(body=note)

    @api.model
    def _aite_heure(self, valeur):
        if not valeur:
            return False
        try:
            return fields.Datetime.to_datetime(valeur)
        except (TypeError, ValueError):
            _logger.info("Restaurant : heure d'ouverture illisible ignorée (%r).", valeur)
            return False

    def _aite_notes_d_encaissement(self, employe, personnes):
        """Ce qui est encaissé hors des droits n'est pas refusé (la
        synchronisation ne doit jamais échouer) : c'est noté."""
        notes = []
        niveau = employe.sudo().aite_niveau_caisse if employe else False
        nom = employe.name if employe else _("personne")
        remboursement = self._aite_est_un_remboursement()
        if employe and not regles.autorise(niveau, 'encaisser'):
            notes.append(_(
                "Encaissée par %(nom)s, qui n'a pas le droit d'encaisser.", nom=nom))
        if remboursement and not regles.autorise(niveau, 'rembourser'):
            notes.append(_(
                "Remboursement validé par %(nom)s, qui n'a pas le droit de rembourser.",
                nom=nom))
        if (not self.table_id and personnes < 1 and not self.aite_origine_uuid
                and not remboursement and not self.config_id.aite_vente_sans_table):
            notes.append(_(
                "Encaissée comme vente sans table, alors que cette caisse ne "
                "l'ouvre pas (case « Autoriser la vente sans table » décochée)."))
        return notes

    def _aite_est_un_remboursement(self):
        return bool(self.lines.filtered('refunded_orderline_id')) or \
            float_compare(self.amount_total, 0.0, precision_rounding=self.currency_id.rounding) < 0

    # ------------------------------------------------------------------
    # Lignes : saisies et quantités parties
    # ------------------------------------------------------------------

    def _aite_quantites_de_preparation(self, uuids):
        """La quantité de préparation de chaque ligne : la somme des
        ``quantity`` de ``last_order_preparation_change`` qui la désignent
        (par son ``uuid``, ou par une clé qui commence par lui : la clé peut
        porter la note)."""
        try:
            changement = json.loads(self.last_order_preparation_change or '{}')
        except ValueError:
            changement = {}
        entrees = (changement.get('lines') or {}) if isinstance(changement, dict) else {}
        quantites = dict.fromkeys(uuids, 0.0)
        for cle, entree in entrees.items():
            if not isinstance(entree, dict):
                continue
            uuid = entree.get('uuid')
            if uuid not in quantites:
                uuid = next((u for u in quantites if u and str(cle).startswith(u)), None)
            if uuid is not None:
                quantites[uuid] += regles._nombre(entree.get('quantity'))
        return quantites

    def _aite_employe_de_saisie(self):
        """La personne identifiée sur le poste (contexte posé par la caisse),
        sinon l'employé de l'addition (pos_hr : la dernière personne qui a
        ajouté un produit)."""
        identifiant = self.env.context.get('aite_employee_id')
        employe = self.env['hr.employee']
        if isinstance(identifiant, int) and identifiant:
            employe = employe.sudo().browse(identifiant).exists()
            if employe and employe.company_id and employe.company_id != self.company_id:
                employe = self.env['hr.employee']
        return employe or self.employee_id.sudo()

    def _aite_nom_table(self):
        if self.table_id:
            return str(self.table_id.table_number)
        return self.floating_order_name or ''

    def _aite_bilan_des_lignes(self, avant):
        """Chaque hausse de quantité d'une ligne, vue par le serveur depuis
        la synchronisation précédente, est une saisie.

        Limite (revue de l'incrément 3, à écrire dans les notes de version
        avec celles de la partie 8.3) : un second poste resté sur une copie
        ancienne qui renvoie une ligne plus basse, puis le premier poste qui
        renvoie la sienne, font noter deux fois la même unité. Le serveur ne
        distingue pas cette copie ancienne d'un vrai retrait suivi d'un ajout
        (« retirer puis rajouter », sans code ni trace, Q34) : plafonner la
        saisie au plus haut déjà noté ferait perdre l'ajout réel du second
        employé. Le journal garde donc chaque geste reçu."""
        deplacement = bool(self.env.context.get('aite_deplacement'))
        lignes = {ligne.uuid: ligne for ligne in self.lines}
        uuids = set(avant) | set(lignes)
        preparation = self._aite_quantites_de_preparation(uuids)
        employe = None
        saisies = []
        for uuid in uuids:
            ligne = lignes.get(uuid)
            qte_avant, envoyee, prep_avant, produit, nom = avant.get(
                uuid, (0.0, 0.0, 0.0, None, None))
            prep = preparation.get(uuid, 0.0)
            qte = ligne.qty if ligne else 0.0
            saisie, _retrait, nouvelle = regles.bilan_ligne(
                envoyee, prep_avant, prep, qte_avant, qte, deplacement)
            # Le retrait sans code va au journal des annulations (incrément 4).
            if ligne and (
                    float_compare(nouvelle, ligne.aite_qte_envoyee, precision_digits=PRECISION)
                    or float_compare(prep, ligne.aite_qte_preparation,
                                     precision_digits=PRECISION)):
                ligne.write({'aite_qte_envoyee': nouvelle, 'aite_qte_preparation': prep})
            if saisie > 0:
                if employe is None:
                    employe = self._aite_employe_de_saisie()
                produit = ligne.product_id if ligne else produit
                saisies.append({
                    'date': fields.Datetime.now(),
                    'company_id': self.company_id.id,
                    'config_id': self.config_id.id,
                    'order_id': self.id,
                    'order_ref': self.pos_reference or self.name,
                    'table_nom': self._aite_nom_table(),
                    'ligne_uuid': uuid,
                    'produit_id': produit.id if produit else False,
                    'produit_nom': (ligne.full_product_name if ligne else nom)
                    or (produit.display_name if produit else False),
                    'quantite': saisie,
                    'employe_id': employe.id or False,
                    'employe_nom': employe.name or False,
                })
        if saisies:
            self.env['aite.restaurant.saisie'].sudo().create(saisies)

    # ------------------------------------------------------------------
    # Fiche de l'addition
    # ------------------------------------------------------------------

    def action_aite_saisies(self):
        """Bouton « Saisies » de la fiche : le journal filtré sur l'addition."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'aite_pos_restaurant.action_restaurant_saisie')
        action['domain'] = [('order_id', '=', self.id)]
        action['context'] = {'create': False}
        return action
