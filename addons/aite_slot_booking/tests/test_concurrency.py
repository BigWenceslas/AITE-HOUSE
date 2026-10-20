# -*- coding: utf-8 -*-
"""Écart n° 32 (partie créneaux) : deux confirmations simultanées.

Deux réceptionnistes (ou deux visiteurs du site) confirment au même
instant deux brouillons sur le même créneau d'une ressource de capacité 1.
Chaque transaction travaille sur sa photo de la base (REPEATABLE READ) :
sans verrou, aucune ne voit la réservation de l'autre et le créneau est
vendu deux fois.

Le test a besoin de deux vraies transactions concurrentes : il travaille
donc sur des curseurs indépendants du curseur de test, valide (commit) ses
données de départ et les supprime à la fin.
"""
from datetime import datetime, timedelta

import psycopg2.errors

from odoo import SUPERUSER_ID, api, fields
from odoo.exceptions import ValidationError
from odoo.sql_db import db_connect
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_slot')
class TestSlotConcurrentConfirm(TransactionCase):

    def _env(self, cr):
        return api.Environment(cr, SUPERUSER_ID, {'tracking_disable': True})

    def _cursor(self):
        return db_connect(self.env.cr.dbname).cursor()

    def test_simultaneous_confirmations_cannot_double_book(self):
        # ── Données de départ, validées pour être vues des deux côtés ──
        with self._cursor() as cr:
            env = self._env(cr)
            company = env.company
            resource = env['aite.booking.resource'].create({
                'name': "Salon concurrence",
                'kind': 'space',
                'company_id': company.id,
                'capacity': 1,
                'open_hour': 0.0,
                'close_hour': 24.0,
                'slot_minutes': '60',
            })
            partner = env['res.partner'].create(
                {'name': "Client concurrence"})
            # Créneau d'une heure dans 3 jours, aligné sur toute heure
            # pleine quel que soit le fuseau (pas d'une heure, 0 h – 24 h).
            day = datetime.combine(
                fields.Date.today() + timedelta(days=3),
                datetime.min.time()) + timedelta(hours=12)
            vals = {
                'resource_id': resource.id,
                'partner_id': partner.id,
                'company_id': company.id,
                'start': day,
                'stop': day + timedelta(hours=1),
            }
            b1 = env['aite.slot.booking'].create(dict(vals))
            b2 = env['aite.slot.booking'].create(dict(vals))
            ids = {'res': resource.id, 'partner': partner.id,
                   'b1': b1.id, 'b2': b2.id}
            cr.commit()

        try:
            cr_a = self._cursor()
            cr_b = self._cursor()
            try:
                env_a, env_b = self._env(cr_a), self._env(cr_b)
                # La transaction B a déjà lu la base (photo prise) quand
                # A confirme : c'est la situation de deux requêtes HTTP
                # parallèles.
                env_b['aite.slot.booking'].browse(ids['b2']).state
                env_a['aite.slot.booking'].browse(ids['b1']).action_confirm()
                env_a.flush_all()
                cr_a.commit()

                refused = False
                try:
                    env_b['aite.slot.booking'].browse(
                        ids['b2']).action_confirm()
                    env_b.flush_all()
                    cr_b.commit()
                except (ValidationError,
                        psycopg2.errors.SerializationFailure,
                        psycopg2.errors.LockNotAvailable):
                    # Odoo rejoue la requête sur une erreur de concurrence :
                    # au second passage, la confirmation de A est visible et
                    # le conflit est refusé proprement.
                    refused = True
                    cr_b.rollback()
            finally:
                cr_a.close()
                cr_b.close()

            with self._cursor() as cr:
                confirmed = self._env(cr)['aite.slot.booking'].search_count([
                    ('resource_id', '=', ids['res']),
                    ('state', '=', 'confirmed'),
                ])
            self.assertTrue(refused, "la seconde confirmation doit échouer")
            self.assertEqual(confirmed, 1, "créneau vendu deux fois")
        finally:
            with self._cursor() as cr:
                env = self._env(cr)
                env['aite.slot.booking'].browse(
                    [ids['b1'], ids['b2']]).unlink()
                env['aite.booking.resource'].browse(ids['res']).unlink()
                env['res.partner'].browse(ids['partner']).unlink()
                cr.commit()
