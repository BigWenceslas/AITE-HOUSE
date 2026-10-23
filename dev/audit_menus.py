# Audit « novice » : tous les écrans AITE accessibles depuis un menu.
#
# Périmètre : toute entrée de menu dont l'action (ou le menu lui-même) est
# définie par un module AITE — l'application Hôtel, mais aussi POS Crédit,
# Direction et les écrans ajoutés aux applications standard (Point de Vente,
# Inventaire, Achats). Pour chacun : l'écran s'ouvre, un écran vide dit quoi
# faire (aide o_view_nocontent ≥ 120 caractères), le menu n'a pas de libellé
# anglais résiduel.
from odoo.tools.safe_eval import safe_eval, datetime, dateutil, time

Data = env['ir.model.data']


def module_of(record):
    """Module qui définit l'enregistrement (``aite_…``), sinon ''."""
    row = Data.search([('model', '=', record._name), ('res_id', '=', record.id)], limit=1)
    return row.module or ''


menus = env['ir.ui.menu'].search([]).sorted(lambda m: m.complete_name)
issues = []
seen = 0
for m in menus:
    if not m.action or m.action._name != 'ir.actions.act_window':
        continue
    act = m.action
    if not (module_of(act).startswith('aite_') or module_of(m).startswith('aite_')):
        continue
    seen += 1
    # 1. l'action s'exécute (modèle, vues, domaine) sans erreur
    try:
        model = env[act.res_model]
        model.get_views([(False, vt) for vt in act.view_mode.split(',')], options={'toolbar': False})
        ctx = {
            'context_today': lambda: datetime.date.today(), 'datetime': datetime,
            'relativedelta': dateutil.relativedelta.relativedelta, 'time': time,
            'uid': env.uid, 'user': env.user,
            'allowed_company_ids': env.companies.ids, 'company_id': env.company.id,
        }
        dom = safe_eval(act.domain, ctx) if act.domain else []
        cnt = model.search_count(dom) if act.target != 'new' else 1
    except Exception as e:
        issues.append(("ERREUR", m.complete_name, str(e)[:120]))
        continue
    # 2. un état vide doit expliquer quoi faire
    help_txt = act.help or ""
    if act.target != 'new' and cnt == 0 and ('o_view_nocontent' not in help_txt or len(help_txt) < 120):
        issues.append(("ÉTAT VIDE MUET", m.complete_name, "aucune aide (%d car.)" % len(help_txt)))
    # 3. libellés anglais résiduels dans le menu
    if any(w in m.name for w in ("Room", "Board", "Guest", "Task", "Report", "Dashboard", "Pending", "Settings")):
        issues.append(("ANGLAIS", m.complete_name, m.name))
print("menus audités :", seen)
for i in issues:
    print("  ✗ %-16s %s — %s" % i)
if not issues:
    print("  ✓ aucun problème : chaque écran s'ouvre et explique quoi faire quand il est vide")
