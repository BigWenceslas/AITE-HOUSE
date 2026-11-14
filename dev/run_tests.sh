#!/bin/bash
# ============================================================================
# AITE HOUSE — lance toute la batterie de tests
#   1. tests purs (sans Odoo)        : tests/vague1/test_*.py, tests/socle/test_*.py,
#                                      tests/restaurant/test_*.py
#   2. scénarios « utilisateur novice » joués dans odoo-bin shell sur la base
#      de développement (chaque scénario fait un rollback à la fin)
#   3. audit des menus (chaque écran s'ouvre, chaque état vide explique quoi faire)
# Usage : dev/run_tests.sh            tout (hôtel : base aite_dev)
#         dev/run_tests.sh pure       tests purs seulement
#         dev/run_tests.sh scenario   scénarios de l'hôtel seulement
#         dev/run_tests.sh audit      audit des menus seulement
#         dev/run_tests.sh restaurant restaurant seul (base aite_resto, créée par
#                                     dev/setup_env.sh --restaurant) : tests purs,
#                                     scénario tests/restaurant/scenario_restaurant.py,
#                                     audit des menus ; refuse une base hôtelière ou
#                                     sans aite_pos_restaurant (dev/etat_base.py)
# Variables : ODOO_DIR, ODOO_DB (aite_dev ; aite_resto en mode restaurant),
#             ODOO_CONF (dev/odoo.conf), PYTHON
# Code de sortie : 0 si tout est vert.
# ============================================================================
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ODOO_DIR=${ODOO_DIR:-$ROOT/../odoo18}
WHAT=${1:-all}
if [ "$WHAT" = restaurant ]; then
  ODOO_DB=${ODOO_DB:-aite_resto}
else
  ODOO_DB=${ODOO_DB:-aite_dev}
fi
PYTHON=${PYTHON:-python3}
ODOO_CONF=${ODOO_CONF:-$ROOT/dev/odoo.conf}
FAIL=0

shell() {  # joue un script dans odoo-bin shell, affiche la sortie utile
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ODOO_CONF" -d "$ODOO_DB" --no-http < "$1" 2>&1 \
     | grep -vE "^(INFO|WARNING|DEBUG)|odoo\.(modules|sql_db|service|addons)|^\s*$")
}

purs() {  # tests purs d'un dossier : affiche le résumé, échoue si la dernière ligne n'est pas « OK »
  local r
  r=$(cd "$ROOT" && "$PYTHON" -m unittest discover -s "$1" -p "test_*.py" 2>&1 | tail -3)
  echo "$r"
  echo "$r" | tail -1 | grep -q '^OK' || FAIL=1
}

scenario() {  # joue un scénario novice, échoue s'il ne finit pas par « 0 KO »
  local out
  printf '\n\033[1;35m▶ Scénario %s (base %s)\033[0m\n' "$(basename "${1%.py}")" "$ODOO_DB"
  out=$(shell "$1")
  echo "$out" | grep -E "^(═|  ✓|  ✗|RÉSULTAT|  KO)" | sed -n '1,400p'
  echo "$out" | grep -q "RÉSULTAT : .* 0 KO" || { FAIL=1; echo "$out" | grep -iE "error|traceback" | head -5; }
}

if [ "$WHAT" = all ] || [ "$WHAT" = pure ] || [ "$WHAT" = restaurant ]; then
  printf '\n\033[1;35m▶ Tests purs — vague 1\033[0m\n'
  purs tests/vague1
  printf '\n\033[1;35m▶ Tests purs — restaurant\033[0m\n'
  purs tests/restaurant
  printf '\n\033[1;35m▶ Tests purs — socle (12 modules)\033[0m\n'
  for f in "$ROOT"/tests/socle/test_*.py; do
    r=$(cd "$ROOT/tests/socle" && "$PYTHON" -m unittest "$(basename "${f%.py}")" 2>&1 | tail -1)
    printf '  %-36s %s\n' "$(basename "$f")" "$r"
    [ "$r" = OK ] || FAIL=1
  done
fi

if [ "$WHAT" = all ] || [ "$WHAT" = scenario ] || [ "$WHAT" = restaurant ]; then
  [ -f "$ODOO_CONF" ] || { echo "✗ $ODOO_CONF absent — lancer dev/setup_env.sh"; exit 1; }
fi

if [ "$WHAT" = restaurant ]; then
  # La base du restaurant, et elle seule (un ODOO_DB hérité du shell, par
  # exemple aite_dev, ne doit pas être pris pour elle) : dev/etat_base.py.
  ETAT=$(cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ODOO_CONF" -d "$ODOO_DB" --no-http \
           < "$ROOT/dev/etat_base.py" 2>/dev/null | sed -n 's/^ETAT_BASE=//p')
  case "$ETAT" in
    restaurant) ;;
    hotel)
      echo "✗ La base « $ODOO_DB » est une base hôtelière : le mode restaurant se joue sur la base"
      echo "   du restaurant (ODOO_DB=aite_resto dev/run_tests.sh restaurant, ou sans ODOO_DB)."
      exit 1 ;;
    sans_restaurant)
      echo "✗ La base « $ODOO_DB » n'a pas le restaurant (aite_pos_restaurant) : créez la base"
      echo "   du restaurant avec dev/setup_env.sh --restaurant."
      exit 1 ;;
    *)
      echo "✗ La base « $ODOO_DB » n'existe pas (ou ne répond pas) : créez-la avec"
      echo "   dev/setup_env.sh --restaurant."
      exit 1 ;;
  esac
fi

if [ "$WHAT" = all ] || [ "$WHAT" = scenario ]; then
  for s in scenario_city_tax scenario_registry scenario_housekeeping scenario_kpi; do
    scenario "$ROOT/tests/vague1/$s.py"
  done
fi

if [ "$WHAT" = restaurant ]; then
  scenario "$ROOT/tests/restaurant/scenario_restaurant.py"
fi

if [ "$WHAT" = all ] || [ "$WHAT" = audit ] || [ "$WHAT" = restaurant ]; then
  printf '\n\033[1;35m▶ Audit des menus (base %s)\033[0m\n' "$ODOO_DB"
  out=$(shell "$ROOT/dev/audit_menus.py")
  echo "$out" | grep -E "menus audités|✓|✗"
  echo "$out" | grep -q "✓ aucun problème" || FAIL=1
fi

echo
[ $FAIL = 0 ] && echo "✔ TOUT EST VERT" || echo "✗ DES TESTS ÉCHOUENT"
exit $FAIL
