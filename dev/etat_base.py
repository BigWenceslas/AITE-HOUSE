# -*- coding: utf-8 -*-
"""Ce qu'est une base, avant que dev/setup_env.sh ou dev/run_tests.sh n'y
touche (joué dans odoo-bin shell) :

    ETAT_BASE=hotel            le socle hôtelier (aite_hotel_management) est installé
    ETAT_BASE=restaurant       le restaurant (aite_pos_restaurant) est installé, sans hôtel
    ETAT_BASE=sans_restaurant  ni l'un ni l'autre

Une base absente n'écrit rien (odoo-bin shell s'arrête sur l'erreur de
connexion). Les deux scripts s'en servent pour refuser une variable ODOO_DB
héritée du shell : « --restaurant » ne doit jamais installer le restaurant et
sa graine dans la base hôtelière.
"""
Modules = env['ir.module.module'].sudo()


def installe(nom):
    return bool(Modules.search_count([('name', '=', nom), ('state', '=', 'installed')]))


if installe('aite_hotel_management'):
    print("ETAT_BASE=hotel")
elif installe('aite_pos_restaurant'):
    print("ETAT_BASE=restaurant")
else:
    print("ETAT_BASE=sans_restaurant")
