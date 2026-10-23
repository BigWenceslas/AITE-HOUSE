# -*- coding: utf-8 -*-
"""Mise à niveau d'une base livrée (LAVERANDAH, livraison 2).

La tâche planifiée quotidienne est une donnée ``noupdate`` : renommée dans
le code (« non-présentations » au lieu de « no-show », ECARTS n° 42), elle
gardait son ancien nom anglais sur une base déjà installée. Le script de
migration 18.0.1.0.7 la renomme, sans toucher à un nom choisi par le client.
"""
import importlib.util
import os

from odoo.modules.module import get_module_path
from odoo.tests import TransactionCase, tagged

OLD_NAME = "Hôtel : tâches quotidiennes (no-show, ménage)"
NEW_NAME = "Hôtel : tâches quotidiennes (non-présentations, ménage)"


def load_migration(module, version, script='post-migrate'):
    """Charge ``migrations/<version>/<script>.py`` comme le fait Odoo."""
    path = os.path.join(get_module_path(module), 'migrations', version,
                        script + '.py')
    spec = importlib.util.spec_from_file_location(
        '%s_mig_%s' % (module, version.replace('.', '_')), path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


@tagged('post_install', '-at_install', 'aite_hotel')
class TestMigrationCronName(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.migration = load_migration('aite_hotel_management', '18.0.1.0.7')
        cls.cron = cls.env.ref('aite_hotel_management.ir_cron_hotel_daily')
        cls.env['res.lang']._activate_lang('fr_FR')

    def _set_name(self, name):
        """État d'une base livrée : le nom en source et en français."""
        self.cron.ir_actions_server_id.update_field_translations(
            'name', {'en_US': name, 'fr_FR': name})

    def test_ancien_nom_renomme_dans_toutes_les_langues(self):
        self._set_name(OLD_NAME)
        self.migration.migrate(self.env.cr, '18.0.1.0.3')
        self.cron.invalidate_recordset(['name'])
        self.cron.ir_actions_server_id.invalidate_recordset(['name'])
        self.assertEqual(self.cron.with_context(lang='en_US').name, NEW_NAME)
        self.assertEqual(self.cron.with_context(lang='fr_FR').name, NEW_NAME)

    def test_nom_choisi_par_le_client_conserve(self):
        self._set_name("Nuit : clôture de l'hôtel")
        self.migration.migrate(self.env.cr, '18.0.1.0.3')
        self.cron.invalidate_recordset(['name'])
        self.cron.ir_actions_server_id.invalidate_recordset(['name'])
        self.assertEqual(self.cron.with_context(lang='fr_FR').name,
                         "Nuit : clôture de l'hôtel")

    def test_installation_neuve_ignoree(self):
        """``version`` vide = installation : rien à migrer."""
        self._set_name(OLD_NAME)
        self.migration.migrate(self.env.cr, None)
        self.cron.invalidate_recordset(['name'])
        self.cron.ir_actions_server_id.invalidate_recordset(['name'])
        self.assertEqual(self.cron.with_context(lang='fr_FR').name, OLD_NAME)
