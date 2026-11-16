# -*- coding: utf-8 -*-
# Carte du restaurant Le Messager : la source est le module
# addons/aite_resto_carte_messager (data/carte.py), que ce script joue dans
# odoo-bin shell (base de démonstration : la société y est renommée « Restaurant
# Le Messager »). Sur la base d'un client, installer plutôt le module depuis Apps.
#
# Usage :
#   PG_HOST=localhost PYTHON=../venv312/bin/python dev/setup_env.sh --restaurant --carte-messager
# ou :
#   cd ../odoo18 && $PYTHON odoo-bin shell -c ../AITE-HOUSE/dev/odoo.conf -d aite_messager \
#       --no-http < ../AITE-HOUSE/dev/seeds/seed_carte_messager.py
import os as _os
from odoo.modules.module import get_module_path as _chemin_module

_racine = _chemin_module('aite_resto_carte_messager')
if not _racine:
    raise SystemExit("✗ module aite_resto_carte_messager introuvable dans l'addons_path")
_source = _os.path.join(_racine, 'data', 'carte.py')
exec(compile(open(_source, encoding='utf-8').read(), _source, 'exec'), {'env': env, '__name__': 'seed'})
