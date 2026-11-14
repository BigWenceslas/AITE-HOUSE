# -*- coding: utf-8 -*-
"""Session de caisse : tableau des droits envoyé à la caisse, messages sans
courriel d'employé, ouverture et fermeture par code vérifié par le serveur,
espèces réservées (spécification, T6, T8, parties 3.1, 3.3 et 4.2).

La caisse ne lit jamais ``employee_id`` comme preuve : chaque poste le
réécrit à chaque code tapé (``pos_hr``). L'ouverture et la fermeture passent
par deux requêtes à code (``aite_ouvrir_caisse``, ``aite_fermer_caisse``), et
les gardes ci-dessous refusent tout autre chemin venu de la caisse, **avant**
que la session change d'état. Le code accepté n'est qu'une autorisation
(``aite_autorisation_id``) : « Caisse ouverte par » et « Caisse fermée par »
sont écrits à l'ouverture et à la fermeture effectives, et l'abandon de la
fenêtre efface l'autorisation. Ouvrir ou fermer depuis la gestion, par un
responsable du Point de Vente, n'est pas contrôlé.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from . import regles

# Écrits par le serveur seul (requêtes à code) : retirés de toute écriture
# reçue, sauf quand notre propre code serveur écrit (``contexte_serveur``).
CHAMPS_PROTEGES = ('aite_ouverte_par_id', 'aite_fermee_par_id', 'aite_autorisation_id')
CONTEXTE_SERVEUR = 'aite_ecriture_serveur'
ETATS_DE_FERMETURE = ('closing_control', 'closed')

# Le contexte d'une requête de la caisse est transmis tel quel au serveur :
# une clé de contexte, quelle que soit sa valeur, peut donc venir du compte de
# la caisse lui-même (revue de l'incrément 3). La clé ne vaut que si elle
# porte ce jeton, un objet Python comparé par identité : une requête n'apporte
# que des textes, des nombres, des listes et des dictionnaires, jamais lui.
_JETON_SERVEUR = object()


def contexte_serveur():
    """Le contexte sous lequel notre code serveur écrit les champs protégés
    (``record.with_context(**contexte_serveur())``)."""
    return {CONTEXTE_SERVEUR: _JETON_SERVEUR}


def ecrit_par_le_serveur(env):
    """Vrai si l'écriture vient de notre code serveur, jamais d'une requête."""
    return env.context.get(CONTEXTE_SERVEUR) is _JETON_SERVEUR


class PosSession(models.Model):
    _inherit = 'pos.session'

    # pos_hr suit ce champ (tracking=True) : chaque code tapé sur un poste
    # écrirait une ligne dans l'historique de la session.
    employee_id = fields.Many2one(tracking=False)

    aite_ouverte_par_id = fields.Many2one(
        'hr.employee', string="Caisse ouverte par", readonly=True, copy=False,
        help="L'employé dont le code a ouvert la caisse, vérifié par le serveur.")
    aite_fermee_par_id = fields.Many2one(
        'hr.employee', string="Caisse fermée par", readonly=True, copy=False,
        help="L'employé dont le code a fermé la caisse, vérifié par le serveur.")
    # Le code tapé n'est qu'une autorisation : « ouverte par » et « fermée
    # par » ne sont écrits qu'à l'ouverture et à la fermeture effectives
    # (une fenêtre abandonnée ne laisse pas une caisse « fermée par » quelqu'un
    # alors qu'elle est encore en service).
    aite_autorisation_id = fields.Many2one(
        'hr.employee', string="Code vérifié, en attente", readonly=True, copy=False,
        help="Technique : l'employé dont le code vient d'être vérifié par le "
             "serveur pour ouvrir la caisse (caisse en contrôle d'ouverture) ou "
             "pour la fermer (caisse en service). Effacé à l'ouverture, à la "
             "fermeture, ou quand la fenêtre est abandonnée.")

    # ------------------------------------------------------------------
    # Écritures venues de la caisse
    # ------------------------------------------------------------------

    def _aite_controle_de_caisse(self):
        """Vrai si l'écriture vient d'un compte contrôlé (le compte de la
        caisse) : ni le superutilisateur (code d'Odoo en ``sudo()``), ni un
        responsable du Point de Vente, qui ouvre et ferme depuis la gestion
        sans code (T8)."""
        return not self.env.su and not self.env.user.has_group(
            'point_of_sale.group_pos_manager')

    @api.model_create_multi
    def create(self, vals_list):
        """Une session au service à table contrôlé commence toujours en
        contrôle d'ouverture, sans « ouverte par » (requête forgée)."""
        if not ecrit_par_le_serveur(self.env):
            controle = self._aite_controle_de_caisse()
            propres = []
            for vals in vals_list:
                vals = {champ: valeur for champ, valeur in vals.items()
                        if champ not in CHAMPS_PROTEGES}
                config = self.env['pos.config'].browse(vals.get('config_id')).exists()
                if controle and 'state' in vals and config and config._aite_actif():
                    del vals['state']
                propres.append(vals)
            vals_list = propres
        return super().create(vals_list)

    def write(self, vals):
        if not ecrit_par_le_serveur(self.env):
            vals = {champ: valeur for champ, valeur in vals.items()
                    if champ not in CHAMPS_PROTEGES}
            if 'state' in vals and self._aite_controle_de_caisse():
                self._aite_controler_changement_d_etat(vals['state'])
        return super().write(vals)

    def _aite_controler_changement_d_etat(self, etat):
        """Sous le compte de la caisse, une session au service à table
        contrôlé ne s'ouvre et ne se ferme qu'avec un code vérifié par le
        serveur, quel que soit le chemin (écriture directe, action de la
        gestion appelée depuis la caisse)."""
        for session in self:
            if not session.config_id._aite_actif() or session.state == etat:
                continue
            if etat == 'opened' and not (
                    session.state == 'opening_control' and session.aite_autorisation_id):
                raise UserError(session._aite_r3())
            if etat in ETATS_DE_FERMETURE and not (
                    session.state in ('opened', 'closing_control')
                    and session.aite_autorisation_id):
                raise UserError(session._aite_r13())

    # ------------------------------------------------------------------
    # Chargement en caisse, messages sans courriel
    # ------------------------------------------------------------------

    def _load_pos_data(self, data):
        """La caisse reçoit le tableau des droits, l'ordre des niveaux et le
        délai de retour au plan, comme ``_has_cash_move_perm`` : une seule
        source, ``regles.py``."""
        res = super()._load_pos_data(data)
        if self.config_id._aite_actif():
            session = res['data'][0]
            session['_aite_droits'] = dict(regles.DROITS)
            session['_aite_niveaux'] = [code for code, _libelle in regles.NIVEAUX]
            session['_aite_delai_retour_plan'] = regles.DELAI_RETOUR_PLAN
        return res

    def _get_message_author(self):
        """En mode, ``pos_hr`` ne signe plus l'ouverture et la fermeture au
        nom de l'employé : ses messages exigent un courriel, que les serveurs
        n'ont pas. La caisse ne lit d'ailleurs jamais ``employee_id`` comme
        preuve (T8)."""
        if self.config_id._aite_actif():
            return None
        return super()._get_message_author()

    def log_partner_message(self, partner_id, action, message_type):
        """Même texte qu'Odoo, écrit en note (``_message_log``), qui n'exige
        pas de courriel. Sans cela, une sortie d'espèces par un employé sans
        courriel échoue après l'enregistrement du mouvement : la fenêtre ne se
        ferme pas et une seconde sortie est saisie."""
        if not self.config_id._aite_actif():
            return super().log_partner_message(partner_id, action, message_type)
        if message_type == 'ACTION_CANCELLED':
            body = _("Action annulée (%s)", action)
        elif message_type == 'CASH_DRAWER_ACTION':
            body = _("Tiroir-caisse ouvert (%s)", action)
        else:
            body = action
        self._message_log(body=body, author_id=partner_id or None)

    # ------------------------------------------------------------------
    # Le code tapé, vérifié par le serveur (T8)
    # ------------------------------------------------------------------

    def _aite_r3(self):
        return _("La caisse n'est pas encore ouverte. La caissière ou un chef de "
                 "salle doit l'ouvrir avec son code.")

    def _aite_r13(self):
        return _("Seul un chef de salle ou le manager ferme la caisse.")

    def _aite_employe_par_code(self, code):
        """L'employé actif de la société, avec un niveau, dont le code vaut
        ``code`` (recherche en ``sudo()`` : le compte de la caisse ne lit
        pas les codes). Code inconnu → R1."""
        self.ensure_one()
        employe = self.env['hr.employee']
        if regles.code_valide(code):
            employe = employe.sudo().search([
                ('company_id', '=', self.config_id.company_id.id),
                ('aite_niveau_caisse', '!=', False),
                ('pin', '=', code),
            ], limit=1)
        if not employe:
            raise UserError(_("Code inconnu. Retapez votre code."))
        return employe

    def _aite_noter(self, texte, employe):
        """Note dans l'historique, au nom du contact de l'employé, sans
        courriel exigé (T6)."""
        self._message_log(body=texte, author_id=employe.work_contact_id.id or None)

    def _aite_autoriser(self, employe):
        self.with_context(**contexte_serveur()).write(
            {'aite_autorisation_id': employe.id if employe else False})

    def aite_ouvrir_caisse(self, code):
        """Requête de la caisse : la personne qui tape ``code`` peut-elle
        ouvrir la caisse ? Il faut le droit « ouvrir_caisse » (caissière et
        au-dessus). Le code accepté devient l'autorisation d'ouvrir ;
        « Caisse ouverte par » et la note sont écrits quand le contrôle
        d'ouverture d'Odoo est validé (``_set_opening_control_data``). Rend
        l'employé.

        Refus (code inconnu R1, niveau insuffisant R3) : **rendu**
        (``{'erreur': message}``), comme pour la fermeture ; la caisse
        l'affiche et la fenêtre du code attend un autre code.

        Caisse déjà ouverte (par un autre poste) : ``{'deja_ouverte': True}``,
        quel que soit le code, sans nom (le serveur ne dit pas à qui est un
        code) ; le poste se met à jour, rien n'est réécrit."""
        self.ensure_one()
        if not self.config_id._aite_actif():
            raise UserError(_("Cette caisse n'est pas au service à table contrôlé."))
        if self.state != 'opening_control':
            return {'deja_ouverte': True}
        try:
            employe = self._aite_employe_par_code(code)
        except UserError as erreur:
            self._aite_autoriser(False)
            return {'erreur': erreur.args[0]}
        if not regles.autorise(employe.aite_niveau_caisse, 'ouvrir_caisse'):
            self._aite_autoriser(False)
            return {'erreur': self._aite_r3()}
        self._aite_autoriser(employe)
        return {'id': employe.id, 'name': employe.name}

    def aite_fermer_caisse(self, code):
        """Requête de la caisse : la personne qui tape ``code`` peut-elle
        fermer la caisse ? Il faut le droit « fermer_caisse » (chef de salle
        et au-dessus). Le code accepté devient l'autorisation de fermer ;
        « Caisse fermée par » et la note sont écrits quand la caisse est
        effectivement fermée (``close_session_from_ui``). Rend l'employé.

        Refus (code inconnu R1, niveau insuffisant R13) : l'autorisation
        donnée plus tôt est effacée. Le refus est **rendu**
        (``{'erreur': message}``) et non levé : une erreur annulerait la
        remise à vide avec le reste de la requête (et Odoo l'écrirait au
        journal comme un avertissement). La caisse l'affiche comme les autres
        refus. Une caisse pas encore ouverte ne se ferme pas (R3)."""
        self.ensure_one()
        if not self.config_id._aite_actif():
            raise UserError(_("Cette caisse n'est pas au service à table contrôlé."))
        if self.state == 'opening_control':
            return {'erreur': self._aite_r3()}
        try:
            employe = self._aite_employe_par_code(code)
        except UserError as erreur:
            self._aite_autoriser(False)
            return {'erreur': erreur.args[0]}
        if not regles.autorise(employe.aite_niveau_caisse, 'fermer_caisse'):
            self._aite_autoriser(False)
            return {'erreur': self._aite_r13()}
        self._aite_autoriser(employe)
        return {'id': employe.id, 'name': employe.name}

    def aite_motifs_annulation(self):
        """Requête de la fenêtre d'annulation, à son ouverture : les motifs
        actifs, dans leur ordre (incrément 4). Lus en ``sudo()`` : le compte de
        la caisse n'a aucun droit sur les motifs ; un motif ajouté pendant le
        service est proposé à l'annulation suivante (REST-12 critère 5)."""
        motifs = self.env['aite.restaurant.motif'].sudo().search([])
        return [{'id': motif.id, 'name': motif.name,
                 'precision_requise': motif.precision_requise} for motif in motifs]

    def aite_abandonner_code(self):
        """Requête de la caisse : la fenêtre d'ouverture ou de fermeture a
        été abandonnée ; le code tapé n'autorise plus rien. Sans effet sur
        une caisse fermée."""
        for session in self:
            if session.state != 'closed' and session.aite_autorisation_id:
                session._aite_autoriser(False)
        return True

    # ------------------------------------------------------------------
    # Gardes : refus avant tout changement d'état (T8) ; « ouverte par » et
    # « fermée par » au moment effectif
    # ------------------------------------------------------------------

    def _aite_refus_fermeture(self):
        for session in self:
            if session.config_id._aite_actif() and (
                    not session.aite_autorisation_id
                    or session.state == 'opening_control'):
                raise UserError(session._aite_r13())

    def _set_opening_control_data(self, cashbox_value, notes):
        if not self.config_id._aite_actif():
            return super()._set_opening_control_data(cashbox_value, notes)
        employe = self.sudo().aite_autorisation_id  # nom et contact : lus en sudo()
        if not employe:
            raise UserError(self._aite_r3())
        res = super()._set_opening_control_data(cashbox_value, notes)
        self.with_context(**contexte_serveur()).write({
            'aite_ouverte_par_id': employe.id, 'aite_autorisation_id': False})
        self._aite_noter(_("Caisse ouverte par %s", employe.name), employe)
        return res

    def _cannot_close_session(self, bank_payment_method_diffs=None):
        """Appelé par ``post_closing_cash_details`` et
        ``close_session_from_ui`` (fenêtre de fermeture de la caisse)."""
        self._aite_refus_fermeture()
        return super()._cannot_close_session(bank_payment_method_diffs)

    def update_closing_control_state_session(self, notes):
        """Refus **avant** le passage en « contrôle de fermeture » : sinon la
        session y resterait bloquée."""
        self._aite_refus_fermeture()
        return super().update_closing_control_state_session(notes)

    def close_session_from_ui(self, bank_payment_method_diff_pairs=None):
        """La caisse est fermée : « Caisse fermée par » et la note, au nom de
        la personne dont le code a été vérifié."""
        res = super().close_session_from_ui(bank_payment_method_diff_pairs)
        if self.config_id._aite_actif() and self.state == 'closed' and self.aite_autorisation_id:
            employe = self.sudo().aite_autorisation_id
            self.with_context(**contexte_serveur()).write({
                'aite_fermee_par_id': employe.id, 'aite_autorisation_id': False})
            self._aite_noter(_("Caisse fermée par %s", employe.name), employe)
        return res

    def try_cash_in_out(self, _type, amount, reason, extras):
        """Entrée ou sortie d'espèces : l'employé est celui que le poste met
        dans ``extras`` (pos_hr), pas celui de la session. Il faut un employé
        actif de la société, avec le droit « especes » (chef de salle et
        au-dessus), sinon R15."""
        for session in self:
            if not session.config_id._aite_actif():
                continue
            employe = self.env['hr.employee'].sudo().browse(
                (extras or {}).get('employee_id') or []).exists()
            if (not employe
                    or not employe.active
                    or employe.company_id != session.config_id.company_id
                    or not regles.autorise(employe.aite_niveau_caisse, 'especes')):
                raise UserError(_(
                    "Seul un chef de salle ou le manager peut sortir ou entrer "
                    "des espèces."))
        return super().try_cash_in_out(_type, amount, reason, extras)
