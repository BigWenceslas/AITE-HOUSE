# -*- coding: utf-8 -*-
"""
Tests de la note de chambre POS → folio (aite_hotel_pos_link).

Extraction du code réel : ``_room_charge_amount`` (somme des paiements
marqués), ``_match_decision`` (report direct / file d'attente),
``_pos_folio_line_vals`` (contrat de ligne du PMS) — puis miroirs du
flux complet : motifs d'attente, idempotence, résolution par la
réception.
"""
import os
import re
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
SRC = os.path.join(ADDONS, 'aite_hotel_pos_link', 'models', 'pos_order.py')


def _extract(names):
    src = open(SRC, encoding='utf-8').read()
    ns = {}
    for name in names:
        m = re.search(
            r'^    def %s\(.*?(?=^    @staticmethod|^    @api\.|'
            r'^    # -{10,}|^    def )' % name,
            src, re.S | re.M)
        assert m, "%s introuvable" % name
        exec(compile(textwrap.dedent(m.group(0)), SRC, 'exec'), ns)
    return ns


_ns = _extract(['_room_charge_amount', '_match_decision',
                '_pos_folio_line_vals'])
_room_charge_amount = _ns['_room_charge_amount']
_match_decision = _ns['_match_decision']
_pos_folio_line_vals = _ns['_pos_folio_line_vals']


class TestRoomChargeAmount(unittest.TestCase):

    def test_paiement_mixte(self):
        # 15 000 en espèces + 30 000 note de chambre → 30 000 reportés
        pairs = [(False, 15000), (True, 30000)]
        self.assertEqual(_room_charge_amount(pairs), 30000)

    def test_plusieurs_lignes_note(self):
        pairs = [(True, 12000), (True, 8000), (False, 5000)]
        self.assertEqual(_room_charge_amount(pairs), 20000)

    def test_aucune_ligne_note(self):
        pairs = [(False, 15000), (False, 30000)]
        self.assertEqual(_room_charge_amount(pairs), 0.0)

    def test_commande_vide(self):
        self.assertEqual(_room_charge_amount([]), 0.0)

    def test_montant_none_tolere(self):
        self.assertEqual(_room_charge_amount([(True, None)]), 0.0)


class TestMatchDecision(unittest.TestCase):

    def test_client_et_folio_unique(self):
        self.assertEqual(_match_decision(True, 1), 'post')

    def test_client_sans_folio(self):
        self.assertEqual(_match_decision(True, 0), 'pending')

    def test_plusieurs_folios(self):
        # Deux séjours ouverts (famille) → la réception tranche
        self.assertEqual(_match_decision(True, 2), 'pending')
        self.assertEqual(_match_decision(True, 3), 'pending')

    def test_client_non_identifie(self):
        # Même avec un folio trouvé par erreur, sans client → attente
        self.assertEqual(_match_decision(False, 1), 'pending')
        self.assertEqual(_match_decision(False, 0), 'pending')


class TestFolioLineVals(unittest.TestCase):

    def test_contrat_pms(self):
        vals = _pos_folio_line_vals(9, 55, "POS Shop/0042",
                                    '2026-07-20', 47500)
        self.assertEqual(vals['folio_id'], 9)
        self.assertEqual(vals['line_type'], 'service')
        self.assertEqual(vals['product_id'], 55)
        self.assertEqual(vals['quantity'], 1)
        self.assertEqual(vals['price_unit'], 47500)


class TestFluxComplet(unittest.TestCase):
    """Miroir du flux serveur : garde d'état, idempotence, motifs."""

    PAID = ('paid', 'done', 'invoiced')

    def process(self, state, already_line, already_pending, pairs,
                has_partner, folio_count):
        """Reproduit _aite_process_room_charge pas à pas."""
        if already_line or already_pending:
            return 'skip_idempotent'
        if state not in self.PAID:
            return 'skip_state'
        amount = _room_charge_amount(pairs)
        if amount <= 0:
            return 'skip_zero'
        return _match_decision(has_partner, folio_count)

    def test_nominal_report(self):
        self.assertEqual(
            self.process('paid', False, False, [(True, 30000)], True, 1),
            'post')

    def test_idempotence(self):
        self.assertEqual(
            self.process('paid', True, False, [(True, 30000)], True, 1),
            'skip_idempotent')
        self.assertEqual(
            self.process('paid', False, True, [(True, 30000)], True, 1),
            'skip_idempotent')

    def test_commande_non_reglee(self):
        self.assertEqual(
            self.process('draft', False, False, [(True, 30000)], True, 1),
            'skip_state')

    def test_sans_note_de_chambre(self):
        self.assertEqual(
            self.process('paid', False, False, [(False, 30000)], True, 1),
            'skip_zero')

    def test_ambigu_va_en_attente(self):
        self.assertEqual(
            self.process('paid', False, False, [(True, 30000)], True, 2),
            'pending')
        self.assertEqual(
            self.process('paid', False, False, [(True, 30000)], False, 0),
            'pending')

    def test_motif_attente(self):
        def reason(has_partner, n):
            if not has_partner:
                return 'no_partner'
            if n == 0:
                return 'no_folio'
            return 'multi_folio'
        self.assertEqual(reason(False, 0), 'no_partner')
        self.assertEqual(reason(True, 0), 'no_folio')
        self.assertEqual(reason(True, 3), 'multi_folio')

    def test_resolution_reception(self):
        # La réception choisit un folio ouvert → report + done ;
        # folio refermé entre-temps → erreur (miroir action_resolve).
        def resolve(folio_state, already_line):
            if folio_state != 'open':
                return 'error_closed'
            if already_line:
                return 'done_noop'
            return 'posted_done'
        self.assertEqual(resolve('open', False), 'posted_done')
        self.assertEqual(resolve('open', True), 'done_noop')
        self.assertEqual(resolve('paid', False), 'error_closed')


if __name__ == '__main__':
    unittest.main(verbosity=1)
