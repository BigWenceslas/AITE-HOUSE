#!/bin/sh
# Serveur Odoo de développement AITE HOUSE : dev/srv.sh start|stop|restart|status|log
# Variables (modifiables dans l'environnement) :
#   ODOO_DIR  dossier du clone Odoo 18          (défaut : <racine>/../odoo18)
#   ODOO_DB   base de données                   (défaut : aite_dev)
#   ODOO_CONF fichier de configuration          (défaut : dev/odoo.conf)
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ODOO_DIR=${ODOO_DIR:-$ROOT/../odoo18}
ODOO_DB=${ODOO_DB:-aite_dev}
PYTHON=${PYTHON:-python3}
ODOO_CONF=${ODOO_CONF:-$ROOT/dev/odoo.conf}
PID=$ROOT/dev/odoo.pid
LOG=$ROOT/dev/odoo_server.log

case "$1" in
  stop|restart)
    if [ -f "$PID" ]; then kill "$(cat "$PID")" 2>/dev/null; rm -f "$PID"; sleep 2; fi ;;
esac
case "$1" in
  start|restart)
    [ -f "$ODOO_CONF" ] || { echo "Config absente : $ODOO_CONF (lancer dev/setup_env.sh)"; exit 1; }
    cd "$ODOO_DIR" && setsid nohup "$PYTHON" odoo-bin -c "$ODOO_CONF" -d "$ODOO_DB" \
        --db-filter="^$ODOO_DB$" --pidfile="$PID" > "$LOG" 2>&1 < /dev/null &
    sleep 12
    curl -s -o /dev/null -w "serveur HTTP %{http_code} — http://localhost:8069 (base $ODOO_DB)\n" http://localhost:8069/web/login ;;
  status)
    if [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null; then echo "en marche (pid $(cat "$PID"))"; else echo "arrêté"; fi ;;
  log)
    tail -n 60 "$LOG" ;;
  stop)
    echo "arrêté" ;;
  *)
    echo "usage : $0 start|stop|restart|status|log" ;;
esac
