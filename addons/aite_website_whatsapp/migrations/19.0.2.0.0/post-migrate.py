# -*- coding: utf-8 -*-
""" Reprise des réglages de la version 19.0.1 (module de données).

La 19.0.1 déclarait ses réglages en champs personnalisés ``x_aite_wa_*``
sur ``website``. La 19.0.2 les remplace par des champs Python. Ce script
recopie les valeurs saisies dans les nouvelles colonnes ; Odoo supprime
ensuite les anciens champs, devenus orphelins, en fin de mise à jour.

Il ne s'exécute que lors d'une mise à niveau depuis la 19.0.1 installée
comme module classique (dossier dans l'addons_path).
"""
import logging

from odoo import SUPERUSER_ID, api
from odoo.tools import SQL

_logger = logging.getLogger(__name__)

# ancienne colonne -> nouvelle colonne (types identiques : booléen, texte,
# jsonb pour les champs traduisibles)
COLUMNS = {
    'x_aite_wa_active': 'aite_whatsapp_enabled',
    'x_aite_wa_message': 'aite_whatsapp_message',
    'x_aite_wa_label': 'aite_whatsapp_label',
}


def migrate(cr, version):
    cr.execute(SQL(
        "SELECT column_name FROM information_schema.columns"
        " WHERE table_schema = current_schema()"
        " AND table_name = %s AND column_name LIKE %s",
        'website', 'x\\_aite\\_wa\\_%',
    ))
    existing = {row[0] for row in cr.fetchall()}
    if not existing:
        return

    assignments = [
        SQL("%s = %s", SQL.identifier(new), SQL.identifier(old))
        for old, new in COLUMNS.items() if old in existing
    ]
    if 'x_aite_wa_phone' in existing:
        # La 19.0.1 lisait tous les chiffres comme un numéro international
        # (« 237 6 99 00 00 00 » valait +237…). La 19.0.2 n'accepte sans
        # « + » ni « 00 » qu'un numéro local qu'elle sait compléter : on
        # rend donc son « + » à un numéro qui commence par un chiffre non
        # nul, pour qu'il garde le sens qu'il avait.
        assignments.append(SQL(
            "aite_whatsapp_number = CASE"
            " WHEN x_aite_wa_phone ~ '^[[:space:](]*[1-9]'"
            " THEN '+' || btrim(x_aite_wa_phone)"
            " ELSE x_aite_wa_phone END"
        ))
    if 'x_aite_wa_left' in existing:
        assignments.append(SQL(
            "aite_whatsapp_position = CASE WHEN x_aite_wa_left THEN 'left' ELSE 'right' END"
        ))
    if not assignments:
        return

    cr.execute(SQL("UPDATE website SET %s", SQL(", ").join(assignments)))
    _logger.info(
        "aite_website_whatsapp : réglages WhatsApp repris pour %s site(s) "
        "depuis les champs x_aite_wa_* de la version 19.0.1.", cr.rowcount)

    # Signaler un bouton actif dont le numéro n'est plus reconnu : il ne
    # s'afficherait plus, sans autre message.
    env = api.Environment(cr, SUPERUSER_ID, {})
    for website in env['website'].search([('aite_whatsapp_enabled', '=', True)]):
        if not website.aite_whatsapp_url:
            _logger.warning(
                "aite_website_whatsapp : le numéro WhatsApp « %s » du site "
                "« %s » n'est pas reconnu ; le bouton reste masqué. Le "
                "ressaisir au format international (+237 …) dans Site Web → "
                "Configuration → Paramètres.",
                website.aite_whatsapp_number, website.name)
