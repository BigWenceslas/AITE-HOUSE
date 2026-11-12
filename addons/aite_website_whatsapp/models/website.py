# -*- coding: utf-8 -*-
import re
from urllib.parse import quote

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

# Bornes de la norme E.164 : indicatif pays + numéro national, 15 chiffres
# au plus ; les plus courts (Sainte-Hélène, Niue…) en comptent 7.
WHATSAPP_MIN_DIGITS = 7
WHATSAPP_MAX_DIGITS = 15


class Website(models.Model):
    _inherit = 'website'

    aite_whatsapp_enabled = fields.Boolean(
        string="Bouton WhatsApp",
        help="Affiche le bouton WhatsApp sur toutes les pages du site.",
    )
    aite_whatsapp_number = fields.Char(
        string="Numéro WhatsApp",
        help="Numéro au format international (+237 6 99 00 00 00). Un "
             "numéro local (699 00 00 00) est complété par l'indicatif du "
             "pays de la société du site quand la bibliothèque phonenumbers "
             "est installée sur le serveur.",
    )
    aite_whatsapp_message = fields.Char(
        string="Message pré-rempli",
        translate=True,
        help="Texte déjà saisi dans la discussion à son ouverture ; le "
             "visiteur peut le modifier avant l'envoi. Vide : discussion "
             "vierge.",
    )
    aite_whatsapp_label = fields.Char(
        string="Texte d'accroche",
        translate=True,
        help="Court texte affiché à côté du bouton sur ordinateur (ex. : "
             "« Une question ? Écrivez-nous »). Vide : icône seule.",
    )
    aite_whatsapp_position = fields.Selection(
        selection=[
            ('right', "En bas à droite"),
            ('left', "En bas à gauche"),
        ],
        string="Position du bouton",
        default='right',
        required=True,
    )
    aite_whatsapp_url = fields.Char(
        string="Lien WhatsApp",
        compute='_compute_aite_whatsapp_url',
        help="Lien wa.me ouvert par le bouton, dans la langue du visiteur.",
    )

    @api.depends('aite_whatsapp_number', 'aite_whatsapp_message',
                 'company_id.country_id')
    @api.depends_context('lang')
    def _compute_aite_whatsapp_url(self):
        for website in self:
            digits = website._aite_whatsapp_digits()
            if not digits:
                website.aite_whatsapp_url = False
                continue
            url = f'https://wa.me/{digits}'
            if website.aite_whatsapp_message:
                # wa.me attend un texte encodé en %XX (espaces en %20).
                url += '?text=' + quote(website.aite_whatsapp_message, safe='')
            website.aite_whatsapp_url = url

    def _aite_whatsapp_digits(self):
        """ Numéro au format attendu par wa.me : chiffres seuls, indicatif
        pays compris, sans « + » ni « 00 » (ex. : ``237699000000``).

        Un numéro local est complété par l'indicatif du pays de la société
        du site, via la bibliothèque ``phonenumbers`` quand elle est
        installée. Faute de pouvoir l'analyser (bibliothèque absente,
        métadonnées périmées, société sans pays), seul un numéro saisi au
        format international (« +… » ou « 00… ») est retenu tel quel : un
        numéro local renvoie une chaîne vide, que la contrainte refuse,
        plutôt qu'un lien vers un mauvais correspondant.
        """
        self.ensure_one()
        number = (self.aite_whatsapp_number or '').strip()
        if not number:
            return ''
        country = self.company_id.sudo().country_id
        try:
            # Sans phonenumbers, phone_format renvoie la saisie inchangée.
            number = phone_validation.phone_format(
                number, country.code or None, country.phone_code or None,
                force_format='E164',
            )
        except UserError:
            pass
        digits = re.sub(r'[^0-9]', '', number)
        if re.match(r'[\s(]*\+', number):
            return digits
        if digits.startswith('00'):
            return digits[2:]
        return ''

    @api.constrains('aite_whatsapp_enabled', 'aite_whatsapp_number')
    def _check_aite_whatsapp_number(self):
        for website in self:
            number = (website.aite_whatsapp_number or '').strip()
            if not number:
                if website.aite_whatsapp_enabled:
                    raise ValidationError(self.env._(
                        "Renseignez le numéro WhatsApp du site « %(website)s » "
                        "pour afficher le bouton.",
                        website=website.name,
                    ))
                continue
            digits = website._aite_whatsapp_digits()
            if not WHATSAPP_MIN_DIGITS <= len(digits) <= WHATSAPP_MAX_DIGITS:
                raise ValidationError(self.env._(
                    "Le numéro WhatsApp « %(number)s » n'est pas reconnu : "
                    "saisissez-le au format international, avec l'indicatif "
                    "du pays, par exemple +237 6 99 00 00 00.",
                    number=website.aite_whatsapp_number,
                ))
