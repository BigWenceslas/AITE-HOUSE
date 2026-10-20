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

    @staticmethod
    def _slot_minutes_for(duration_min, step_min):
        """
        Durée réservée pour une prestation : arrondie au multiple
        supérieur du pas de la ressource (écart n° 34). Une prestation de
        90 min au pas d'une heure occupe deux créneaux (2 h) — c'est
        exactement ce que la grille propose (``k`` créneaux consécutifs) ;
        sans cet arrondi, la fin tombait hors grille et la réservation
        échouait à chaque fois.
        """
        step = step_min or 60
        duration = duration_min or step
        return max(1, -(-duration // step)) * step

    @staticmethod
    def _future_slots(slots, now_h):
        """Créneaux dont le début est encore à venir (``now_h`` : heure
        locale décimale, ou ``None`` pour un jour futur)."""
        if now_h is None:
            return list(slots)
        return [s for s in slots if s['start'] > now_h + 1e-6]

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
            partner = self._search_partner_by_phone(phone_n)
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

    @api.model
    def _search_partner_by_phone(self, phone_n):
        """Contact dont le téléphone (ou le mobile), une fois normalisé, est
        ``phone_n`` (écart n° 35). Les numéros saisis au comptoir gardent
        leurs espaces (« +33 6 12 48 90 31 ») : on présélectionne en base
        les fiches qui contiennent les mêmes chiffres dans le même ordre
        (séparateurs quelconques entre eux), puis on compare les numéros
        normalisés des deux côtés."""
        Partner = self.env['res.partner'].sudo()
        digits = [c for c in phone_n if c.isdigit()]
        if not digits:
            return Partner.browse()
        # Les 8 derniers chiffres suffisent à présélectionner (le préfixe
        # pays peut avoir été saisi « +33 » ou « 0033 »).
        pattern = '%' + '%'.join(digits[-8:]) + '%'
        fnames = [f for f in ('phone', 'mobile') if f in Partner._fields]
        domain = ['|'] * (len(fnames) - 1) + [
            (f, '=ilike', pattern) for f in fnames]
        for candidate in Partner.search(domain, order='id'):
            if any(self._norm_phone(candidate[f]) == phone_n
                   for f in fnames):
                return candidate
        return Partner.browse()
