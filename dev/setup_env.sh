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
#          dev/setup_env.sh --muk        + thème MuK (muk_web_theme, Odoo Community) : barre
#                                        des applications, couleurs ; c'est l'habillage des
#                                        vidéos et des captures de référence (docs/videos/)
#          dev/setup_env.sh --restaurant restaurant seul, sans hôtel (~2 min) : base aite_resto
#                                        créée comme l'écran de création (dev/create_db.py :
#                                        Cameroun, fr_FR, sans démonstration), modules du
#                                        restaurant (pos_restaurant, pos_hr, aite_pos_restaurant,
#                                        aite_pos_credit, aite_pos_analytics ; la passerelle
#                                        aite_pos_analytics_hr s'installe seule), graine
#                                        dev/seeds/seed_restaurant.py ; ni socle hôtelier ni
#                                        graine LAVERANDAH (--all est ignoré)
# Variables : PYTHON (interpréteur, ex. venv Python 3.12), ODOO_DIR (clone), PG_HOST (défaut : /tmp = socket local ;
#             mettre localhost pour un service système), ODOO_DB (aite_dev ; aite_resto avec
#             --restaurant ; une base existante doit être du bon genre — hôtel ou
#             restaurant —, sinon le script s'arrête sans rien y installer : dev/etat_base.py),
#             MUK_DIR (clone des modules MuK IT, LGPL-3 ; défaut : à côté de ce dossier)
# ============================================================================
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ODOO_DIR=${ODOO_DIR:-$ROOT/../odoo18}
PG_HOST=${PG_HOST:-/tmp}
PYTHON=${PYTHON:-python3}
MUK_DIR=${MUK_DIR:-$ROOT/../muk_addons}
ALL=0; MUK=0; RESTO=0
for a in "$@"; do
  case "$a" in --all) ALL=1 ;; --muk) MUK=1 ;; --restaurant) RESTO=1 ;; esac
done
if [ $RESTO = 1 ]; then ODOO_DB=${ODOO_DB:-aite_resto}; else ODOO_DB=${ODOO_DB:-aite_dev}; fi
PIPFLAGS=""; "$PYTHON" -m pip install --help 2>/dev/null | grep -q break-system-packages && PIPFLAGS="--break-system-packages"

step() { printf '\n\033[1;35m▶ %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- 1. Odoo 18
step "1/6 Odoo 18 Community → $ODOO_DIR"
if [ ! -f "$ODOO_DIR/odoo-bin" ]; then
  git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git "$ODOO_DIR"
else
  echo "déjà présent"
fi
# Thème MuK : dépôt public de MuK IT (muk-it/odoo-modules), branche 18.0. Seul
# muk_web_theme est installé (avec ses dépendances muk_web_appsbar, _chatter,
# _colors, _dialog) ; sur Odoo Enterprise, le module équivalent est
# muk_web_enterprise_theme. Le thème habille l'interface sans rien changer aux
# modules AITE : il ne fait pas partie de la livraison (addons/).
if [ $MUK = 1 ] && [ ! -f "$MUK_DIR/muk_web_theme/__manifest__.py" ]; then
  git clone --depth 1 --branch 18.0 https://github.com/muk-it/odoo-modules.git "$MUK_DIR"
fi

# ------------------------------------------------------- 2. dépendances Python
step "2/6 dépendances Python"
# Les épingles de requirements.txt visent des distributions précises ; on les
# retire (sauf exclusions connues) pour installer ce que pip trouve.
# websocket-client : sans lui, les tours de la caisse (tests Odoo HttpCase)
# sont IGNORÉS sans erreur (« 0 failed » sans rien avoir joué).
sed -E 's/[[:space:]]*[=<>~!;].*//' "$ODOO_DIR/requirements.txt" | grep -viE '^(ofxparse|rl-renderpm|psycopg2|python-ldap|pypiwin32|\s*)$' | sort -u > /tmp/aite_req.txt
"$PYTHON" -m pip install -q $PIPFLAGS -r /tmp/aite_req.txt psycopg2-binary lxml_html_clean openpyxl websocket-client
python3 -c "import odoo" 2>/dev/null || true
echo "ok"

# ---------------------------------------------------------- 3. PostgreSQL
step "3/6 PostgreSQL (hôte : $PG_HOST)"
# PostgreSQL : si aucun serveur n'écoute, créer un cluster local :
#   sudo -u postgres /usr/lib/postgresql/16/bin/initdb -D $ROOT/../pg/data
#   sudo -u postgres /usr/lib/postgresql/16/bin/pg_ctl -D $ROOT/../pg/data \
#        -o "-k /tmp -p 5432" -l $ROOT/../pg/pg.log start
# Requête administrateur : rôle postgres sur $PG_HOST, sinon utilisateur système
# postgres sur $PG_HOST, sinon sur le socket local par défaut (authentification
# « peer », sans mot de passe : cas d'un service système fraîchement démarré).
psql_admin() {
  case "$PG_MODE" in
    tcp)  psql -w -h "$PG_HOST" -p 5432 -U postgres -Atc "$1" ;;
    hote) su postgres -c "psql -w -h '$PG_HOST' -p 5432 -Atc \"$1\"" ;;
    sock) su postgres -c "psql -w -p 5432 -Atc \"$1\"" ;;
  esac
}
PG_MODE=""
for m in tcp hote sock; do
  if [ "$(PG_MODE=$m psql_admin 'select 1' 2>/dev/null)" = 1 ]; then PG_MODE=$m; break; fi
done
if [ -z "$PG_MODE" ]; then
  echo "✗ PostgreSQL ne répond pas sur $PG_HOST:5432 — démarrez-le (voir commentaire ci-dessus) puis relancez."; exit 1
fi
psql_admin "select 1 from pg_roles where rolname='odoo'" | grep -q 1 \
  || psql_admin "create role odoo login createdb password 'odoo'" >/dev/null
echo "rôle odoo prêt"

# ---------------------------------------------------------- 4. odoo.conf
step "4/6 dev/odoo.conf"
# Un dev/odoo.conf qui portait déjà le thème MuK le garde : une base où le thème
# est installé (aite_dev) ne doit pas le perdre parce qu'on prépare une autre base.
GARDER_MUK=0
[ -f "$ROOT/dev/odoo.conf" ] && grep -q "^addons_path = .*$MUK_DIR" "$ROOT/dev/odoo.conf" && GARDER_MUK=1
sed -e "s#__ODOO_DIR__#$ODOO_DIR#g" -e "s#__ROOT__#$ROOT#g" -e "s#__PG_HOST__#$PG_HOST#g" \
    "$ROOT/dev/odoo.conf.example" > "$ROOT/dev/odoo.conf"
if [ $MUK = 1 ] || [ $GARDER_MUK = 1 ]; then
  sed -i "s#^addons_path = \(.*\)#addons_path = \1,$MUK_DIR#" "$ROOT/dev/odoo.conf"
fi
mkdir -p "$ROOT/dev/filestore"
echo "écrit"

# ---------------------------------------------------------- 6. base
# Lignes d'erreur d'Odoo seulement (pas les messages « (ERROR/3) » de docutils).
erreurs_odoo() { grep -E "^[0-9-]+ [0-9:,]+ [0-9]+ (ERROR|CRITICAL) |Traceback" || true; }
# Ce qu'est une base existante (hotel, restaurant, sans_restaurant) : un ODOO_DB
# hérité du shell (export ODOO_DB=aite_dev) ne doit jamais recevoir le
# restaurant et sa graine, ni une base du restaurant le socle hôtelier.
etat_base() {
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" --no-http \
     < "$ROOT/dev/etat_base.py" 2>/dev/null | sed -n 's/^ETAT_BASE=//p') || true
}
if [ $RESTO = 1 ]; then
  # Restaurant seul (spécification du lot 1, partie 7, incrément 6) : aucun
  # module hôtelier ; aite_pos_analytics_hr (passerelle, auto_install) vient
  # avec aite_pos_restaurant et aite_pos_analytics.
  step "5/6 base $ODOO_DB (restaurant seul : Cameroun, fr_FR, sans démonstration)"
  MODS="pos_restaurant,pos_hr,aite_pos_restaurant,aite_pos_credit,aite_pos_analytics"
  if psql_admin "select 1 from pg_database where datname='$ODOO_DB'" | grep -q 1; then
    case "$(etat_base)" in
      restaurant) ;;
      hotel)
        echo "✗ La base « $ODOO_DB » est une base hôtelière (aite_hotel_management) : rien n'y est installé."
        echo "   La base du restaurant : ODOO_DB=aite_resto dev/setup_env.sh --restaurant (ou « unset ODOO_DB »)."
        exit 1 ;;
      *)
        echo "✗ La base « $ODOO_DB » existe sans le restaurant (aite_pos_restaurant) : rien n'y est installé."
        echo "   --restaurant n'installe le restaurant que dans une base qu'il crée : choisissez une autre"
        echo "   base (ODOO_DB=…), ou supprimez celle-ci (dropdb $ODOO_DB) et relancez."
        exit 1 ;;
    esac
    echo "base existante — mise à niveau des modules du restaurant"
    # -i de la passerelle : sur une base où aite_pos_restaurant et
    # aite_pos_analytics étaient déjà installés, Odoo ne l'installe pas seul.
    (cd "$ODOO_DIR" && "$PYTHON" odoo-bin -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" \
        -u "aite_pos_restaurant,aite_pos_credit,aite_pos_analytics" -i aite_pos_analytics_hr \
        --stop-after-init 2>&1 | erreurs_odoo)
  else
    # Comme l'écran de création de base : la société naît en FCFA, avec le
    # plan comptable camerounais (une base créée par « odoo-bin -d » sans pays
    # naîtrait en dollars).
    PYTHONPATH="$ODOO_DIR" "$PYTHON" "$ROOT/dev/create_db.py" "$ROOT/dev/odoo.conf" "$ODOO_DB"
    (cd "$ODOO_DIR" && "$PYTHON" odoo-bin -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" -i "$MODS" \
        --without-demo=all --stop-after-init 2>&1 | erreurs_odoo)
  fi
else
  step "5/6 base $ODOO_DB (fr_FR)"
  MODS="aite_hotel_management,aite_city_tax,aite_guest_registry,aite_housekeeping"
  [ $ALL = 1 ] && MODS="$MODS,aite_slot_booking,aite_website_booking,aite_hotel_pos_link,aite_pos_credit,aite_loyalty,aite_pos_analytics,aite_stock_dashboard,aite_purchase_dashboard,aite_direction_dashboard,aite_exec_dashboard"
  if psql_admin "select 1 from pg_database where datname='$ODOO_DB'" | grep -q 1; then
    if [ "$(etat_base)" = restaurant ]; then
      echo "✗ La base « $ODOO_DB » est la base du restaurant (sans hôtel) : le socle hôtelier n'y est pas installé."
      echo "   Pour l'hôtel : ODOO_DB=aite_dev dev/setup_env.sh (ou « unset ODOO_DB ») ;"
      echo "   pour le restaurant : dev/setup_env.sh --restaurant."
      exit 1
    fi
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
fi
if [ $MUK = 1 ]; then
  # -i : installe le thème s'il manque, le met à niveau sinon.
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" -i muk_web_theme \
      --stop-after-init 2>&1 | grep -E "ERROR|CRITICAL|Traceback" || true)
  echo "thème MuK installé"
fi

# ---------------------------------------------------------- 7. seeds
if [ $RESTO = 1 ]; then
  step "6/6 jeu de données du restaurant (salle, carte, équipe, comptes)"
  (cd "$ODOO_DIR" && "$PYTHON" odoo-bin shell -c "$ROOT/dev/odoo.conf" -d "$ODOO_DB" --no-http \
      < "$ROOT/dev/seeds/seed_restaurant.py" 2>/dev/null | tail -1)
  cat <<EOF

✔ Environnement du restaurant prêt (base $ODOO_DB).
   Démarrer :   ODOO_DB=$ODOO_DB dev/srv.sh start      → http://localhost:8069
                admin / admin (AITE) ; caisse, manager, chef : mot de passe = identifiant
   La caisse :  se connecter « caisse » → Point de Vente → carte « Restaurant » →
                « Ouvrir la caisse » ; codes : Clarisse 2001 (caissière, ouvre la caisse),
                Brice 1001 et Nadège 1002 (serveurs), Hervé 3001 (chef de salle),
                Sandrine 4001 (manager)
   Tests :      ODOO_DB=$ODOO_DB dev/run_tests.sh restaurant
   Captures :   jamais sur cette base (le parcours écrit des ventes et ferme la caisse) :
                sur une copie jetable, serveur arrêté —
                createdb -h $PG_HOST -U odoo -T $ODOO_DB ${ODOO_DB}_captures  (+ copie du filestore)
                ODOO_DB=${ODOO_DB}_captures dev/srv.sh start ; python3 tests/restaurant/shots.py
                (voir l'en-tête de tests/restaurant/shots.py)
EOF
else
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
fi
