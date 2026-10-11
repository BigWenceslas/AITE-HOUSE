#!/bin/bash
# ============================================================================
# AITE HOUSE — lance toute la batterie de tests
#   1. tests purs (sans Odoo)        : tests/vague1/test_*.py, tests/socle/test_*.py
#   2. scénarios « utilisateur novice » joués dans odoo-bin shell sur la base
#      de développement (chaque scénario fait un rollback à la fin)
#   3. audit des menus (chaque écran s'ouvre, chaque état vide explique quoi faire)
# Usage : dev/run_tests.sh            tout
#         dev/run_tests.sh pure       tests purs seulement
#         dev/run_tests.sh scenario   scénarios seulement
#         dev/run_tests.sh audit      audit des menus seulement
# Variables : ODOO_DIR, ODOO_DB (aite_dev), ODOO_CONF (dev/odoo.conf)
# Code de sortie : 0 si tout est vert.
# ============================================================================
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ODOO_DIR=${ODOO_DIR:-$ROOT/../odoo18}
ODOO_DB=${ODOO_DB:-aite_dev}
PYTHON=${PYTHON:-python3}
ODOO_CONF=${ODOO_CONF:-$ROOT/dev/odoo.conf}
WHAT=${1:-all}
FAIL=0

shell() {  # joue un script dans odoo-bin shell, affiche la sortie utile
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ODOO_CONF" -d "$ODOO_DB" --no-http < "$1" 2>&1 \
     | grep -vE "^(INFO|WARNING|DEBUG)|odoo\.(modules|sql_db|service|addons)|^\s*$")
}

if [ "$WHAT" = all ] || [ "$WHAT" = pure ]; then
  printf '\n\033[1;35m▶ Tests purs — vague 1\033[0m\n'
  (cd "$ROOT" && "$PYTHON" -m unittest discover -s tests/vague1 -p "test_*.py" 2>&1 | tail -3) || FAIL=1
  printf '\n\033[1;35m▶ Tests purs — socle (12 modules)\033[0m\n'
  for f in "$ROOT"/tests/socle/test_*.py; do
    r=$(cd "$ROOT/tests/socle" && "$PYTHON" -m unittest "$(basename "${f%.py}")" 2>&1 | tail -1)
    printf '  %-36s %s\n' "$(basename "$f")" "$r"
    [ "$r" = OK ] || FAIL=1
  done
fi

if [ "$WHAT" = all ] || [ "$WHAT" = scenario ]; then
  [ -f "$ODOO_CONF" ] || { echo "✗ $ODOO_CONF absent — lancer dev/setup_env.sh"; exit 1; }
  for s in scenario_city_tax scenario_registry scenario_housekeeping scenario_kpi; do
    printf '\n\033[1;35m▶ Scénario %s (base %s)\033[0m\n' "$s" "$ODOO_DB"
    out=$(shell "$ROOT/tests/vague1/$s.py")
    echo "$out" | grep -E "^(═|  ✓|  ✗|RÉSULTAT|  KO)" | sed -n '1,200p'
    echo "$out" | grep -q "RÉSULTAT : .* 0 KO" || { FAIL=1; echo "$out" | grep -iE "error|traceback" | head -5; }
  done
fi

if [ "$WHAT" = all ] || [ "$WHAT" = audit ]; then
  printf '\n\033[1;35m▶ Audit des menus\033[0m\n'
  out=$(shell "$ROOT/dev/audit_menus.py")
  echo "$out" | grep -E "menus audités|✓|✗"
  echo "$out" | grep -q "✓ aucun problème" || FAIL=1
fi

echo
[ $FAIL = 0 ] && echo "✔ TOUT EST VERT" || echo "✗ DES TESTS ÉCHOUENT"
exit $FAIL
