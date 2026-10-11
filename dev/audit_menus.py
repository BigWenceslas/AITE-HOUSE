# Audit « novice » : tous les menus du module Hôtel, à froid (base vierge).
import json
root = env.ref('aite_hotel_management.menu_hotel_root'); menus = env['ir.ui.menu'].search([('id', 'child_of', root.id)]).sorted(lambda m: m.complete_name)
issues = []
seen = 0
for m in menus:
    if not m.action:
        continue
    act = m.action
    if act._name != 'ir.actions.act_window':
        continue
    seen += 1
    # 1. l'action s'exécute (modèle, vues, domaine, contexte) sans erreur
    try:
        model = env[act.res_model]
        views = act._get_action_dict().get('views') or []
        for vid, vtype in act.views if act.views else []:
            pass
        # chargement des vues comme le client web
        model.get_views([(False, vt) for vt in act.view_mode.split(',')], options={'toolbar': False})
        # domaine et contexte évaluables (vides sur base neuve)
        dom = act.domain and eval(act.domain, {'context_today': lambda: __import__('datetime').date.today(), 'datetime': __import__('datetime'), 'relativedelta': __import__('dateutil.relativedelta').relativedelta.relativedelta, 'uid': env.uid}) or []
        cnt = model.search_count(dom) if act.res_model not in ('aite.police.register.wizard', 'aite.hk.assign.wizard') else 0
    except Exception as e:
        issues.append(("ERREUR", m.complete_name, str(e)[:120])); continue
    # 2. un état vide doit expliquer quoi faire
    help_txt = (act.help or "")
    if act.target != 'new' and cnt == 0 and ('o_view_nocontent' not in help_txt or len(help_txt) < 120):
        issues.append(("ÉTAT VIDE MUET", m.complete_name, "aucune aide (%d car.)" % len(help_txt)))
    # 3. libellés anglais résiduels dans le menu
    if any(w in m.name for w in ("Room", "Board", "Guest", "Task", "Report")):
        issues.append(("ANGLAIS", m.complete_name, m.name))
print("menus audités :", seen)
for i in issues:
    print("  ✗ %-16s %s — %s" % i)
if not issues:
    print("  ✓ aucun problème : chaque écran s'ouvre et explique quoi faire quand il est vide")
