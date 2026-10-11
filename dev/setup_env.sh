#!/bin/bash
# ============================================================================
# AITE HOUSE — mise en place de l'environnement de développement Odoo 18
# ----------------------------------------------------------------------------
# Reproduit l'environnement utilisé pour développer et tester la vague 1 :
#   1. clone d'Odoo 18 Community (branche 18.0) à côté de ce dossier
#   2. dépendances Python (requirements d'Odoo sans épingles + psycopg2-binary)
#   3. rôle PostgreSQL odoo/odoo (PostgreSQL doit tourner : service système
#      ou cluster local — voir « PostgreSQL » plus bas)
#   4. dev/odoo.conf généré depuis dev/odoo.conf.example
#   5. base aite_dev en français : socle + 3 modules vague 1 installés
#   6. jeu de données LAVERANDAH (dev/seeds/)
#
# Usage :  dev/setup_env.sh              socle + vague 1 (rapide, ~3 min)
#          dev/setup_env.sh --all        + les 11 autres modules (POS, stock…)
# Variables : PYTHON (interpréteur, ex. venv Python 3.12), ODOO_DIR (clone), PG_HOST (défaut : /tmp = socket local ;
#             mettre localhost pour un service système), ODOO_DB (aite_dev)
# ============================================================================
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ODOO_DIR=${ODOO_DIR:-$ROOT/../odoo18}
PG_HOST=${PG_HOST:-/tmp}
ODOO_DB=${ODOO_DB:-aite_dev}
PYTHON=${PYTHON:-python3}
ALL=0
for a in "$@"; do
  case "$a" in --all) ALL=1 ;; esac
done
PIPFLAGS=""; "$PYTHON" -m pip install --help 2>/dev/null | grep -q break-system-packages && PIPFLAGS="--break-system-packages"

step() { printf '\n\033[1;35m▶ %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- 1. Odoo 18
step "1/6 Odoo 18 Community → $ODOO_DIR"
if [ ! -f "$ODOO_DIR/odoo-bin" ]; then
  git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git "$ODOO_DIR"
else
  echo "déjà présent"
fi

# ------------------------------------------------------- 2. dépendances Python
step "2/6 dépendances Python"
# Les épingles de requirements.txt visent des distributions précises ; on les
# retire (sauf exclusions connues) pour installer ce que pip trouve.
sed -E 's/[=<>~!;].*//' "$ODOO_DIR/requirements.txt" | grep -viE '^(ofxparse|rl-renderpm|psycopg2|python-ldap|pypiwin32|\s*)$' | sort -u > /tmp/aite_req.txt
"$PYTHON" -m pip install -q $PIPFLAGS -r /tmp/aite_req.txt psycopg2-binary lxml_html_clean openpyxl
python3 -c "import odoo" 2>/dev/null || true
echo "ok"

# ---------------------------------------------------------- 3. PostgreSQL
step "3/6 PostgreSQL (hôte : $PG_HOST)"
# PostgreSQL : si aucun serveur n'écoute, créer un cluster local :
#   sudo -u postgres /usr/lib/postgresql/16/bin/initdb -D $ROOT/../pg/data
#   sudo -u postgres /usr/lib/postgresql/16/bin/pg_ctl -D $ROOT/../pg/data \
#        -o "-k /tmp -p 5432" -l $ROOT/../pg/pg.log start
if ! psql -h "$PG_HOST" -p 5432 -U postgres -Atc "select 1" >/dev/null 2>&1 \
   && ! su postgres -c "psql -h $PG_HOST -p 5432 -Atc 'select 1'" >/dev/null 2>&1; then
  echo "✗ PostgreSQL ne répond pas sur $PG_HOST:5432 — démarrez-le (voir commentaire ci-dessus) puis relancez."; exit 1
fi
PSQL="psql -h $PG_HOST -p 5432 -U postgres"
$PSQL -Atc "select 1" >/dev/null 2>&1 || PSQL="su postgres -c \"psql -h $PG_HOST -p 5432\""
eval $PSQL -Atc "\"select 1 from pg_roles where rolname='odoo'\"" | grep -q 1 \
  || eval $PSQL -c "\"create role odoo login createdb password 'odoo'\""
echo "rôle odoo prêt"

# ---------------------------------------------------------- 4. odoo.conf
step "4/6 dev/odoo.conf"
sed -e "s#__ODOO_DIR__#$ODOO_DIR#g" -e "s#__ROOT__#$ROOT#g" -e "s#__PG_HOST__#$PG_HOST#g" \
    "$ROOT/dev/odoo.conf.example" > "$ROOT/dev/odoo.conf"
mkdir -p "$ROOT/dev/filestore"
echo "écrit"

# ---------------------------------------------------------- 6. base
step "5/6 base $ODOO_DB (fr_FR)"
MODS="aite_hotel_management,aite_city_tax,aite_guest_registry,aite_housekeeping"
[ $ALL = 1 ] && MODS="$MODS,aite_slot_booking,aite_website_booking,aite_hotel_pos_link,aite_pos_credit,aite_loyalty,aite_pos_analytics,aite_stock_dashboard,aite_purchase_dashboard,aite_direction_dashboard,aite_exec_dashboard"
if eval $PSQL -Atc "\"select 1 from pg_database where datname='$ODOO_DB'\"" | grep -q 1; then
  echo "base existante — mise à niveau des modules AITE"
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" -u "$MODS" --stop-after-init 2>&1 | grep -E "ERROR|CRITICAL|Traceback" || true)
else
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" -i "$MODS" \
      --load-language=fr_FR --without-demo=all --stop-after-init 2>&1 | grep -E "ERROR|CRITICAL|Traceback" || true)
  # langue française pour tous les utilisateurs + admin/admin
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" --no-http <<'EOF' 2>/dev/null
env['res.lang']._activate_lang('fr_FR')
env['res.users'].search([]).write({'lang': 'fr_FR'})
env.ref('base.user_admin').write({'password': 'admin'})
env['res.partner'].search([]).write({'lang': 'fr_FR'})
env.cr.commit()
print("langue fr_FR, admin/admin")
EOF
)
fi

# ---------------------------------------------------------- 7. seeds
step "6/6 jeu de données LAVERANDAH"
for s in seed_laverandah seed_registry seed_housekeeping; do
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" --no-http < "$ROOT/dev/seeds/$s.py" 2>/dev/null | tail -1)
done

cat <<EOF

✔ Environnement prêt.
   Démarrer :   ODOO_DB=$ODOO_DB dev/srv.sh start      → http://localhost:8069  (admin / admin)
   Tests :      ODOO_DB=$ODOO_DB dev/run_tests.sh      (scénarios novice + tests purs + audit menus)
   Captures :   python3 tests/vague1/shots.py          (Playwright, serveur démarré)
EOF
