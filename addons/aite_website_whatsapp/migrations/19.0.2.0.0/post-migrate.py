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

from odoo.tools import SQL

_logger = logging.getLogger(__name__)

# ancienne colonne -> nouvelle colonne (types identiques : booléen, texte,
# jsonb pour les champs traduisibles)
COLUMNS = {
    'x_aite_wa_active': 'aite_whatsapp_enabled',
    'x_aite_wa_phone': 'aite_whatsapp_number',
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
