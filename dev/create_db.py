# -*- coding: utf-8 -*-
"""Crée une base Odoo comme l'écran de création de base (restaurant, partie 6.4).

Pays Cameroun, langue fr_FR, sans données de démonstration : la société naît
en FCFA (XAF) et le plan comptable camerounais se charge à la première
installation d'un module comptable.

Usage (depuis la racine du dépôt, Odoo 18 à côté dans ../odoo18) :
    PYTHONPATH=../odoo18 $PYTHON dev/create_db.py dev/odoo_tours.conf aite_rest_<rôle>

Les chemins relatifs du fichier de configuration (dev/odoo_tours.conf) sont lus
depuis le dossier d'Odoo, comme pour ``odoo-bin`` lancé dans ../odoo18.

La base est jetable : la supprimer à la fin avec
    dropdb -h localhost -U odoo -w aite_rest_<rôle>
"""
import os
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage : create_db.py <fichier de configuration> <nom de la base>")
    conf = os.path.abspath(sys.argv[1])
    nom = sys.argv[2]

    import odoo
    from odoo.tools import config
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(odoo.__file__))))
    config.parse_config(['-c', conf])
    from odoo.service import db
    # (nom, démonstration, langue, mot de passe admin, identifiant, pays, téléphone)
    db.exp_create_database(nom, False, 'fr_FR', 'admin', 'admin', 'CM', '')
    print("Base créée :", nom)


if __name__ == '__main__':
    main()
