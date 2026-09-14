# -*- coding: utf-8 -*-
from odoo import api, models


class WebsiteBookingHelper(models.AbstractModel):
    """
    Aides du tunnel de réservation en ligne.

    Les règles de validation et de recherche de créneaux sont des
    fonctions **pures** (extraites et exécutées par les tests) ; la
    création de client est le seul point d'écriture, en ``sudo``
    contrôlé.
    """
    _name = 'aite.website.booking'
    _description = "Réservation en ligne — helpers"

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _norm_phone(raw):
        """Normalise un téléphone saisi : chiffres et « + » de tête."""
        if not raw:
            return ''
        keep = []
        for i, ch in enumerate(str(raw).strip()):
            if ch.isdigit():
                keep.append(ch)
            elif ch == '+' and not keep:
                keep.append(ch)
        return ''.join(keep)

    @staticmethod
    def _validate_online_booking(name, phone, slot_ok):
        """
        Validation du formulaire public.

        :returns: '' si OK, sinon le premier code d'erreur :
            'name' (nom trop court), 'phone' (téléphone invalide,
            < 8 chiffres), 'slot' (créneau non choisi / plus libre).
        """
        if not name or len(str(name).strip()) < 2:
            return 'name'
        digits = [c for c in (phone or '') if c.isdigit()]
        if len(digits) < 8:
            return 'phone'
        if not slot_ok:
            return 'slot'
        return ''

    @staticmethod
    def _fit_starts(slots, k):
        """
        Créneaux de départ possibles pour une prestation occupant ``k``
        créneaux consécutifs : liste des index ``i`` tels que
        ``slots[i .. i+k-1]`` sont tous ``free``.
        """
        if k <= 0:
            return []
        out = []
        n = len(slots)
        for i in range(n - k + 1):
            if all(slots[i + j].get('state') == 'free'
                   for j in range(k)):
                out.append(i)
        return out

    # ------------------------------------------------------------------
    # Client (unique point d'écriture partenaire)
    # ------------------------------------------------------------------

    @api.model
    def find_or_create_partner(self, name, phone, email):
        """Retrouve le client par téléphone normalisé ou e-mail, sinon
        le crée — une fiche unique par client (règle du cahier)."""
        Partner = self.env['res.partner'].sudo()
        phone_n = self._norm_phone(phone)
        partner = Partner.browse()
        if phone_n:
            partner = Partner.search(
                [('phone', '=', phone_n)], limit=1)
        if not partner and email:
            partner = Partner.search(
                [('email', '=ilike', email.strip())], limit=1)
        if not partner:
            partner = Partner.create({
                'name': str(name).strip(),
                'phone': phone_n or False,
                'email': (email or '').strip() or False,
            })
        return partner
