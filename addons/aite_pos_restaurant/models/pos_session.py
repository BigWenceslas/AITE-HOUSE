# -*- coding: utf-8 -*-
"""Session de caisse : tableau des droits envoyé à la caisse, messages sans
courriel d'employé (spécification, T6, parties 3.3 et 4.2)."""
from odoo import models, _

from . import regles


class PosSession(models.Model):
    _inherit = 'pos.session'

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
