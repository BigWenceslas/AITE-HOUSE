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

Incrément 4 — annuler ce qui est parti (T9, T14, partie 4.2) :
- ``aite_autoriser_annulation`` est la requête de la fenêtre d'annulation :
  le code d'un responsable est vérifié par le serveur, le motif est exigé, la
  ligne du journal est écrite et le verrou (``aite_qte_envoyee``) baissé par
  le serveur lui-même ; une demande renvoyée avec la même clé rend la
  première réponse sans rien refaire ;
- ce qui arrive sans autorisation n'est jamais refusé, mais tracé au journal
  des annulations : une quantité envoyée qui baisse à la synchronisation
  (« Retrait sans code », hors division et réunion) et une addition qui porte
  encore des produits envoyés, annulée ou supprimée sans la fenêtre
  (« Annulation sans code ») — sauf l'addition absorbée par une réunion,
  marquée par la caisse (``aite_marquer_fusion``).

Hors du service à table contrôlé, rien de tout cela : la caisse n'est pas
touchée.
"""
import json
import logging

from odoo import _, api, fields, models
from odoo.tools import float_compare

from . import regles
from .pos_order_line import CHAMPS_LIGNE_SERVEUR, contexte_synchro
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
NATURES_AUTORISEES = ('produit', 'table', 'fermeture')


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
    aite_fusionnee = fields.Boolean(
        string="Réunie à une autre table", readonly=True, copy=False,
        help="Cette addition a été versée dans une autre table : son annulation "
             "n'est pas une annulation de produits.")

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
        if vals.get('state') == 'cancel':
            # Annulée par Odoo (caisse, fermeture, gestion), par une
            # synchronisation ou par remove_from_ui : jamais refusé, tracé.
            self._aite_tracer_annulation_sans_code()
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

    def unlink(self):
        """Une addition en cours supprimée (gestion, requête) : ce qui était
        parti est tracé avant la suppression ; la trace lui survit."""
        self.filtered(lambda commande: commande.state == 'draft') \
            ._aite_tracer_annulation_sans_code()
        return super().unlink()

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
                                     ligne.full_product_name,
                                     existing_order._aite_prix_ttc(ligne))
        etait_reglee = bool(existing_order) and existing_order.state in ETATS_REGLES

        # 3. L'écriture d'Odoo, sous le jeton de la synchronisation : les
        # lignes qu'elle baisse ou supprime sont jugées par le bilan
        # ci-dessous, pas tracées une seconde fois (pos_order_line.py).
        synchro = contexte_synchro()
        order_id = super(PosOrder, self.with_context(**synchro))._process_order(
            order, existing_order.with_context(**synchro) if existing_order else existing_order)

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
        la synchronisation précédente, est une saisie ; chaque baisse sous ce
        qui est parti, hors division et réunion, est un « Retrait sans code »
        (incrément 4).

        Limite (revue de l'incrément 3, à écrire dans les notes de version
        avec celles de la partie 8.3) : un second poste resté sur une copie
        ancienne qui renvoie une ligne plus basse, puis le premier poste qui
        renvoie la sienne, font noter deux fois la même unité. Le serveur ne
        distingue pas cette copie ancienne d'un vrai retrait suivi d'un ajout
        (« retirer puis rajouter », sans code ni trace, Q34) : plafonner la
        saisie au plus haut déjà noté ferait perdre l'ajout réel du second
        employé. Le journal garde donc chaque geste reçu."""
        deplacement = bool(self.env.context.get('aite_deplacement'))
        # Annulée par cette synchronisation : l'annulation a déjà été jugée
        # (write), les lignes ne sont plus suivies.
        annulee = self.state == 'cancel'
        lignes = {ligne.uuid: ligne for ligne in self.lines}
        uuids = set(avant) | set(lignes)
        preparation = self._aite_quantites_de_preparation(uuids)
        employe = None
        saisies = []
        retraits = []
        for uuid in uuids:
            ligne = lignes.get(uuid)
            qte_avant, envoyee, prep_avant, produit, nom, prix = avant.get(
                uuid, (0.0, 0.0, 0.0, None, None, None))
            prep = preparation.get(uuid, 0.0)
            qte = ligne.qty if ligne else 0.0
            saisie, retrait, nouvelle = regles.bilan_ligne(
                envoyee, prep_avant, prep, qte_avant, qte, deplacement)
            if ligne and not annulee and (
                    float_compare(nouvelle, ligne.aite_qte_envoyee, precision_digits=PRECISION)
                    or float_compare(prep, ligne.aite_qte_preparation,
                                     precision_digits=PRECISION)):
                ligne.write({'aite_qte_envoyee': nouvelle, 'aite_qte_preparation': prep})
            if retrait > 0 and not annulee:
                if employe is None:
                    employe = self._aite_employe_de_saisie()
                retraits.append(self._aite_valeurs_annulation(
                    uuid, ligne.product_id if ligne else produit,
                    (ligne.full_product_name if ligne else nom),
                    prix if prix is not None else self._aite_prix_ttc(ligne),
                    retrait, 'retrait_sans_code', serveur=employe))
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
        if retraits:
            self.env['aite.restaurant.annulation'].sudo().create(retraits)

    # ------------------------------------------------------------------
    # Le journal des annulations (incrément 4)
    # ------------------------------------------------------------------

    def _aite_prix_ttc(self, ligne):
        """Le prix unitaire TTC d'une ligne, remise comprise."""
        if not ligne:
            return 0.0
        if ligne.qty:
            return ligne.price_subtotal_incl / ligne.qty
        prix = ligne.price_unit * (1.0 - (ligne.discount or 0.0) / 100.0)
        taxes = ligne.tax_ids_after_fiscal_position
        if taxes:
            return taxes.compute_all(prix, ligne.order_id.currency_id, 1.0,
                                     product=ligne.product_id,
                                     partner=ligne.order_id.partner_id)['total_included']
        return prix

    def _aite_valeurs_annulation(self, uuid, produit, nom_produit, prix, quantite, nature,
                                 serveur=None, serveur_nom=None, superieur=None, motif=None,
                                 commentaire=False, demande=False):
        """Une ligne du journal des annulations pour cette addition. Les noms
        sont recopiés."""
        self.ensure_one()
        devise = self.company_id.currency_id
        prix = devise.round(prix or 0.0)
        return {
            'date': fields.Datetime.now(),
            'company_id': self.company_id.id,
            'config_id': self.config_id.id,
            'session_id': self.session_id.id,
            'order_id': self.id,
            'order_ref': self.pos_reference or self.name,
            'table_nom': self._aite_nom_table(),
            'produit_id': produit.id if produit else False,
            'produit_nom': nom_produit or (produit.display_name if produit else False),
            'quantite': quantite,
            'prix_unitaire': prix,
            'montant': devise.round(quantite * prix),
            'serveur_id': serveur.id if serveur else False,
            'serveur_nom': serveur_nom or (serveur.name if serveur else False),
            'superieur_id': superieur.id if superieur else False,
            'superieur_nom': superieur.name if superieur else False,
            'motif_id': motif.id if motif else False,
            'motif_nom': motif.name if motif else False,
            'commentaire': commentaire or False,
            'autorisee': bool(superieur),
            'type_annulation': nature,
            'ligne_uuid': uuid,
            'demande_uuid': demande or False,
        }

    def _aite_tracer_retrait(self, ligne, retrait, prix):
        """Une ligne envoyée baissée directement (hors synchronisation) :
        « Retrait sans code »."""
        self.ensure_one()
        self.env['aite.restaurant.annulation'].sudo().create(self._aite_valeurs_annulation(
            ligne.uuid, ligne.product_id, ligne.full_product_name, prix, retrait,
            'retrait_sans_code', serveur=self._aite_employe_de_saisie()))

    def _aite_tracer_annulation_sans_code(self):
        """Une addition en cours qui porte encore des produits envoyés,
        annulée sans la fenêtre d'annulation (sans autorisation de table ni
        réunion) : une ligne « Annulation sans code » par produit, et le
        verrou retombe. Jamais d'erreur : la synchronisation du poste, qui
        renvoie cette annulation à chaque fois, resterait bloquée.
        Demandée par : l'employé de l'addition, sinon le compte Odoo (gestion)."""
        traces = []
        for commande in self:
            if (commande.state != 'draft' or commande.aite_fusionnee
                    or not commande.config_id or not commande.config_id._aite_actif()):
                continue
            lignes = commande.lines.filtered(lambda ligne: ligne.aite_qte_envoyee > 0)
            if not lignes:
                continue
            employe = commande.employee_id.sudo()
            for ligne in lignes:
                traces.append(commande._aite_valeurs_annulation(
                    ligne.uuid, ligne.product_id, ligne.full_product_name,
                    commande._aite_prix_ttc(ligne), ligne.aite_qte_envoyee,
                    'annulation_sans_code', serveur=employe or None,
                    serveur_nom=False if employe else self.env.user.name))
            lignes.with_context(**contexte_serveur()).write({'aite_qte_envoyee': 0.0})
        if traces:
            self.env['aite.restaurant.annulation'].sudo().create(traces)

    def _aite_refus_annulation(self, message):
        return {'erreur': message}

    def _aite_r8(self):
        return _("Ce code ne peut pas annuler. Il faut celui d'un chef de salle, d'un "
                 "superviseur ou du manager.")

    def _aite_r26(self):
        return _("Ce produit vient d'être annulé sur un autre poste. Rien n'a changé ici.")

    @api.model
    def aite_autoriser_annulation(self, order_ids, lignes, code, motif_id, commentaire=False,
                                  demandeur_id=False, demande_uuid=False, nature='produit'):
        """Requête de la fenêtre d'annulation (T9 ; partie 4.2).

        - ``order_ids`` : les additions (une, ou les tables encore ouvertes à
          la fermeture), en cours, d'une même caisse au service à table
          contrôlé ;
        - ``lignes`` : pour un produit, ``[{'uuid', 'quantite'}]`` ; pour une
          table ou la fermeture, ``False`` : tout ce qui est parti, d'après le
          serveur ;
        - ``code`` : le code d'un employé actif de la société, au niveau
          « annuler_envoye » (chef de salle, superviseur, manager), sinon R8 ;
        - ``motif_id``, ``commentaire`` : le motif touché, sa précision (R24
          pour un motif qui l'exige) ;
        - ``demandeur_id`` : la personne identifiée sur le poste ;
        - ``demande_uuid`` : la clé de la demande ; une demande déjà
          enregistrée avec cette clé rend la première réponse, sans rien
          refaire (réponse perdue, nouvel essai) ;
        - ``nature`` : ``produit``, ``table`` ou ``fermeture``.

        Écrit les lignes du journal et baisse lui-même ``aite_qte_envoyee`` :
        une copie de poste en retard ne relève pas le verrou (seul un nouvel
        envoi le fait). Le refus est **rendu** (``{'erreur': message}``), comme
        pour l'ouverture et la fermeture de la caisse : la fenêtre l'affiche
        et rien n'est écrit. Rend ``{'superieur_id', 'superieur_nom',
        'quantites': {uuid de ligne: quantité annulée}}`` ; pour une demande
        renvoyée, les quantités de la première fois (la caisse applique
        celles-là)."""
        Journal = self.env['aite.restaurant.annulation'].sudo()
        if not demande_uuid or not isinstance(demande_uuid, str) \
                or nature not in NATURES_AUTORISEES:
            return self._aite_refus_annulation(_("Demande d'annulation incomplète."))
        deja = Journal.search([('demande_uuid', '=', demande_uuid)])
        if deja:
            return {'superieur_id': deja[0].superieur_id.id,
                    'superieur_nom': deja[0].superieur_nom,
                    'quantites': {trace.ligne_uuid: trace.quantite for trace in deja}}

        identifiants = [i for i in (order_ids or []) if isinstance(i, int)]
        commandes = self.browse(identifiants).exists()
        config = commandes.config_id
        if not commandes or len(config) != 1 or not config._aite_actif():
            return self._aite_refus_annulation(
                _("Cette caisse n'est pas au service à table contrôlé."))
        if len(commandes) != len(set(identifiants)) or \
                any(commande.state != 'draft' for commande in commandes):
            return self._aite_refus_annulation(self._aite_r26())

        employe = self.env['hr.employee']
        if regles.code_valide(code):
            employe = employe.sudo().search([
                ('company_id', '=', config.company_id.id),
                ('aite_niveau_caisse', '!=', False),
                ('pin', '=', code),
            ], limit=1)
        if not employe or not regles.autorise(employe.aite_niveau_caisse, 'annuler_envoye'):
            return self._aite_refus_annulation(self._aite_r8())

        motif = self.env['aite.restaurant.motif'].sudo().with_context(active_test=False) \
            .browse(motif_id if isinstance(motif_id, int) else []).exists()
        if not motif:
            return self._aite_refus_annulation(
                _("Motif inconnu : rouvrez la fenêtre d'annulation."))
        precision = commentaire.strip() if isinstance(commentaire, str) else ''
        if motif.precision_requise and not precision:
            return self._aite_refus_annulation(_("Écrivez en quelques mots pourquoi."))

        a_annuler = []
        if nature == 'produit':
            for demande in lignes or []:
                if not isinstance(demande, dict):
                    return self._aite_refus_annulation(self._aite_r26())
                quantite = regles._nombre(demande.get('quantite'))
                ligne = commandes.lines.filtered(lambda l: l.uuid == demande.get('uuid'))
                if len(ligne) != 1 or quantite <= 0 or float_compare(
                        quantite, ligne.aite_qte_envoyee, precision_digits=PRECISION) > 0:
                    return self._aite_refus_annulation(self._aite_r26())
                a_annuler.append((ligne, quantite))
            if not a_annuler:
                return self._aite_refus_annulation(self._aite_r26())
        else:
            a_annuler = [(ligne, ligne.aite_qte_envoyee) for ligne in commandes.lines
                         if ligne.aite_qte_envoyee > 0]

        demandeur = self.env['hr.employee'].sudo().browse(
            demandeur_id if isinstance(demandeur_id, int) else []).exists()
        if demandeur and demandeur.company_id and demandeur.company_id != config.company_id:
            demandeur = self.env['hr.employee']
        traces = []
        for ligne, quantite in a_annuler:
            commande = ligne.order_id
            traces.append(commande._aite_valeurs_annulation(
                ligne.uuid, ligne.product_id, ligne.full_product_name,
                commande._aite_prix_ttc(ligne), quantite, nature,
                serveur=demandeur or commande.employee_id.sudo() or None,
                superieur=employe, motif=motif, commentaire=precision,
                demande=demande_uuid))
            ligne.with_context(**contexte_serveur()).write(
                {'aite_qte_envoyee': max(ligne.aite_qte_envoyee - quantite, 0.0)})
        if traces:
            Journal.create(traces)
        return {'superieur_id': employe.id, 'superieur_nom': employe.name,
                'quantites': {ligne.uuid: quantite for ligne, quantite in a_annuler}}

    @api.model
    def aite_marquer_fusion(self, order_id):
        """Requête de la caisse, juste avant d'annuler l'addition absorbée par
        « Déplacer ou réunir » : ce n'est pas une annulation de produits.
        Déclaratif, comme l'identité dans pos_hr (partie 8.3)."""
        commande = self.browse(order_id if isinstance(order_id, int) else []).exists()
        if commande and commande.state == 'draft' and commande.config_id._aite_actif():
            commande.with_context(**contexte_serveur()).write({'aite_fusionnee': True})
            commande.lines.with_context(**contexte_serveur()).write({'aite_qte_envoyee': 0.0})
        return True

    # ------------------------------------------------------------------
    # Fiche de l'addition
    # ------------------------------------------------------------------

    def action_aite_annulations(self):
        """Bouton « Annulations » de la fiche : le journal filtré sur
        l'addition."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'aite_pos_restaurant.action_restaurant_annulation')
        action['domain'] = [('order_id', '=', self.id)]
        action['context'] = {'create': False}
        return action

    def action_aite_saisies(self):
        """Bouton « Saisies » de la fiche : le journal filtré sur l'addition."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'aite_pos_restaurant.action_restaurant_saisie')
        action['domain'] = [('order_id', '=', self.id)]
        action['context'] = {'create': False}
        return action
