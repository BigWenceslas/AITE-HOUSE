# -*- coding: utf-8 -*-
"""Produit, à partir de scenarios.py :
- <sortie>/index.html (le cahier, à passer à weasyprint par build.sh) ;
- docs/guides/AITE_Scenarios_Integrateur.xlsx (le classeur à cocher).

Contrôles (sortie en erreur si l'un échoue) :
- chaque cas des domaines D, F, H, I, J, K, R de recette/cas_de_test.py est
  couvert par au moins une étape, ou écarté dans CAS_ECARTES avec sa raison ;
- un cas écarté n'est pas aussi cité par une étape ; chaque cas cité existe ;
- chaque capture citée existe (captures/<dossier>/<fichier>) ;
- chaque renvoi « écran #k » désigne la k-ième capture du même scénario ;
- identifiants de scénarios uniques, parties connues.

Usage : python3 generer.py <dossier de sortie>
"""
import html
import os
import re
import sys
from collections import OrderedDict

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, '..', '..', '..', '..'))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(RACINE, 'recette'))

import scenarios as S  # noqa: E402
import cas_de_test  # noqa: E402

DOMAINES = "DFHIJKR"
CAPTURES = os.path.join(RACINE, 'captures')
XLSX = os.path.join(RACINE, 'docs', 'guides', 'AITE_Scenarios_Integrateur.xlsx')
PARTIES = OrderedDict((p, (t, m)) for p, t, m in S.PARTIES)
NOMS_DOMAINES = {d: n for d, n, _m in cas_de_test.DOMAINES}


# --------------------------------------------------------------- contrôles
def cas_du_perimetre():
    return OrderedDict((c[0], c) for c in cas_de_test.CAS if c[1] in DOMAINES)


def couverture():
    tous = cas_du_perimetre()
    vus = OrderedDict((k, []) for k in tous)
    inconnus = []
    for sc in S.SCENARIOS:
        for i, (_g, _a, cas) in enumerate(sc['etapes'], 1):
            for c in cas.split():
                if c not in vus:
                    inconnus.append((sc['id'], i, c))
                    continue
                vus[c].append("%s.%d" % (sc['id'], i))
    return tous, vus, inconnus


def numeros_ecrans():
    n, table = 0, {}
    for sc in S.SCENARIOS:
        for k, (fichier, _l) in enumerate(sc['captures'], 1):
            n += 1
            table[(sc['id'], k)] = n
    return table


def verifier():
    tous, vus, inconnus = couverture()
    erreurs = []
    ids = [sc['id'] for sc in S.SCENARIOS]
    if len(ids) != len(set(ids)):
        erreurs.append("identifiants en double : %s" % sorted({i for i in ids if ids.count(i) > 1}))
    for sc in S.SCENARIOS:
        if sc['partie'] not in PARTIES:
            erreurs.append("%s : partie inconnue %s" % (sc['id'], sc['partie']))
    if inconnus:
        erreurs.append("cas inconnus : %s" % inconnus)
    for cid in S.CAS_ECARTES:
        if cid not in tous:
            erreurs.append("cas écarté inconnu : %s" % cid)
        elif vus[cid]:
            erreurs.append("cas écarté mais joué : %s (%s)" % (cid, vus[cid]))
    manquants = [k for k, v in vus.items() if not v and k not in S.CAS_ECARTES]
    if manquants:
        erreurs.append("cas non couverts : %s" % ", ".join(manquants))
    for sc in S.SCENARIOS:
        for fichier, _l in sc['captures']:
            if not os.path.exists(os.path.join(CAPTURES, fichier)):
                erreurs.append("capture absente : captures/%s" % fichier)
        for g, a, _c in sc['etapes']:
            for k in re.findall(r"écran #(\d+)", g + " " + a):
                if not 1 <= int(k) <= len(sc['captures']):
                    erreurs.append("%s : « écran #%s » sans capture" % (sc['id'], k))
            if re.search(r"écran \d", g + " " + a):
                erreurs.append("%s : écrire « écran #k » (rang de la capture dans le scénario)" % sc['id'])
    if erreurs:
        sys.exit("✗ " + "\n✗ ".join(erreurs))
    return tous, vus


# ------------------------------------------------------------------- texte
def ecrans_absolus(sc, texte, ecrans):
    return re.sub(r"écran #(\d+)", lambda m: "écran %d" % ecrans[(sc['id'], int(m.group(1)))], texte)


def typo(texte):
    """Échappe, puis espaces insécables devant : ; ? ! » et après «."""
    t = html.escape(texte, quote=False)
    t = re.sub(r" ([:;?!»])", " \\1", t)
    t = t.replace("« ", "« ")
    return t


def riche(texte):
    t = typo(texte)
    t = re.sub(r"« (.*?) »", r'<span class="ecran">«&#160;\1&#160;»</span>', t)
    t = t.replace(" → ", ' <span class="fleche">→</span> ')
    return t


def etiquette_cas(cas):
    return " ".join('<span class="cas">%s</span>' % c for c in cas.split()) or '<span class="sans">—</span>'


ENCADRES = {'reflexe': ("Bon réflexe", "reflexe"), 'regle': ("Règle d'or", "regle"),
            'attention': ("À savoir", "attention")}


def cas_de(sc):
    return sorted({c for _g, _a, cs in sc['etapes'] for c in cs.split()},
                  key=lambda c: (c[0], int(c[1:])))


def html_scenario(sc, ecrans):
    cas = cas_de(sc)
    o = ['<section class="scenario" id="%s">' % sc['id'], '<div class="tete">']
    o.append('<h3><span class="sid">%s</span> %s%s</h3>' % (
        sc['id'], typo(sc['titre']), ('<span class="joue">%s</span>' % ("JOUÉ" if sc['joue'] == 'oui' else "JOUÉ EN PARTIE")) if sc.get('joue') else ''))
    o.append('<table class="meta">')
    for lib, val in [("Module", PARTIES[sc['partie']][1]), ("Rôle", sc['role']),
                     ("Base", sc['base']), ("Prérequis", sc['prerequis'])]:
        o.append('<tr><th>%s</th><td>%s</td></tr>' % (lib, riche(val)))
    o.append('<tr><th>Cas couverts</th><td>%s</td></tr>' % (
        " ".join('<span class="cas">%s</span>' % c for c in cas) or "aucun cas du cahier (contrôle de mise en service)"))
    o.append('</table>')
    o.append('<p class="but"><strong>Ce qu\'on vérifie.</strong> %s</p></div>' % riche(sc['but']))
    o.append('<table class="etapes"><thead><tr><th class="n">N°</th><th>Geste</th>'
             '<th>Résultat attendu</th><th class="c">Cas</th><th class="ok">OK</th></tr></thead><tbody>')
    for i, (g, a, c) in enumerate(sc['etapes'], 1):
        o.append('<tr><td class="n">%d</td><td>%s</td><td>%s</td><td class="c">%s</td>'
                 '<td class="ok"><span class="case"></span></td></tr>' % (
                     i, riche(ecrans_absolus(sc, g, ecrans)), riche(ecrans_absolus(sc, a, ecrans)),
                     etiquette_cas(c)))
    o.append('</tbody></table>')
    for genre, texte in sc['encadres']:
        titre, classe = ENCADRES[genre]
        o.append('<div class="encadre %s"><strong>%s —</strong> %s</div>' % (classe, titre, riche(texte)))
    figures = []
    for k, (fichier, legende) in enumerate(sc['captures'], 1):
        n = ecrans[(sc['id'], k)]
        figures.append('<figure><img src="img/%s" alt="%s"/><figcaption>Écran %d — %s</figcaption></figure>'
                       % (fichier.replace('/', '__'), html.escape(legende), n, typo(legende)))
    # Deux captures ou plus : côte à côte, deux par rangée (pas de page à moitié vide).
    if len(figures) == 1:
        o.extend(figures)
    for i in range(0, len(figures) if len(figures) > 1 else 0, 2):
        o.append('<div class="duo">%s</div>' % "".join(figures[i:i + 2]))
    o.append('</section>')
    return "\n".join(o)


def html_document(tous, vus):
    ecrans = numeros_ecrans()
    nb_sc = len(S.SCENARIOS)
    nb_et = sum(len(sc['etapes']) for sc in S.SCENARIOS)
    nb_couverts = sum(1 for v in vus.values() if v)
    joues = [sc for sc in S.SCENARIOS if sc.get('joue')]
    o = ['<section class="couverture">',
         '<img class="logo" src="img/logo_aite.jpg" alt="AITE Consulting"/>',
         '<p class="surtitre">SCÉNARIOS DE TESTS — INTÉGRATEUR</p>',
         '<h1>AITE — Restaurant, stock, achats, Direction</h1>',
         '<p class="soustitre">%s</p>' % typo(
             "Installer, régler et recetter chez le client, de bout en bout : un geste par ligne, "
             "et ce que l'écran doit dire"),
         '<table class="fiche">']
    modules = "<br/>".join('%s <span class="version">%s</span> — %s' % (m, v, typo(r)) for m, v, r in S.MODULES)
    for lib, val in [
        ("Public visé", typo("Intégrateur junior (AITE ou partenaire) qui installe et met en service ; "
                             "aucune expérience d'Odoo n'est supposée")),
        ("Modules", modules),
        ("Contenu", typo("%d scénarios, %d étapes ; %d cas du cahier de recette couverts sur %d "
                         "(domaines D, F, H, I, J, K, R), %d écartés car ils exigent l'hôtel ; %d "
                         "scénarios joués (en entier ou en partie) avant publication" % (
                             nb_sc, nb_et, nb_couverts, len(tous), len(S.CAS_ECARTES), len(joues)))),
        ("À cocher", typo("le classeur AITE_Scenarios_Integrateur.xlsx (une ligne par étape)")),
        ("Compagnon", typo("le guide AITE_Guide_Integrateur.pdf (installation, paramétrage, dépannage)")),
        ("Éditeur", "AITE CONSULTING — %s" % typo("Odoo 18 · version %s" % S.VERSION)),
    ]:
        o.append('<tr><th>%s</th><td>%s</td></tr>' % (lib, val))
    o.append('</table></section>')

    o.append('<h2>1. Le principe</h2>')
    o.append('<p>%s</p>' % riche(
        "Chaque scénario se joue d'un bout à l'autre, dans l'ordre : un rôle, une suite de gestes, et "
        "pour chaque geste ce que l'écran doit montrer, avec ses mots exacts. L'intégrateur fait un "
        "seul geste par ligne, compare l'écran au résultat attendu et note OK ou KO dans le classeur "
        "(colonne « OK/KO ») ; un écart se décrit dans « Observations » avec l'heure, le compte "
        "utilisé et le message exact."))
    o.append('<ol class="principe">')
    for t in [
        "Partie A d'abord, sur une base neuve : elle crée la base de recette, pose la démonstration "
        "« Le Messager » (salle, équipe, comptes, carte) et installe les tableaux de bord.",
        "Puis les parties B à G dans l'ordre : chaque partie s'appuie sur les ventes, ardoises, "
        "stocks et factures des précédentes. Ne rien faire d'autre sur la base pendant ce temps.",
        "La partie H (non-régression) se joue après chaque mise à niveau, sur la copie de la base du "
        "client.",
        "Un résultat qui dépend d'un matériel absent (imprimante de cuisine, lecteur) ou d'un "
        "historique que la base n'a pas se note « NA », pas KO.",
        "Les scénarios marqués JOUÉ (ou JOUÉ EN PARTIE) ont été déroulés avant publication ; leurs "
        "chiffres sont ceux qu'on a vus à l'écran (annexe C).",
    ]:
        o.append('<li>%s</li>' % riche(t))
    o.append('</ol>')
    o.append('<div class="encadre regle"><strong>Règle d\'or —</strong> %s</div>' % riche(
        "Jamais sur la base de production : la recette se joue sur une base neuve ou une copie. Un "
        "KO se note tel quel, sans corriger la base à la main pour continuer."))

    o.append('<h2>2. Avant de commencer</h2>')
    o.append('<h4>Les comptes Odoo de la démonstration (posés par I02)</h4>')
    o.append('<table class="simple bloc"><tr><th>Identifiant / mot de passe</th><th>Nom</th><th>Rôle et droits</th></tr>')
    for login, nom, role in S.COMPTES:
        o.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (typo(login), typo(nom), typo(role)))
    o.append('</table>')
    o.append('<h4>L\'équipe de salle et ses codes (fictive)</h4>')
    o.append('<table class="simple bloc"><tr><th>Employé</th><th>Niveau en caisse</th><th>Code</th></tr>')
    for nom, niveau, code in S.EQUIPE:
        o.append('<tr><td>%s</td><td>%s</td><td class="code">%s</td></tr>' % (typo(nom), typo(niveau), code))
    o.append('</table>')
    o.append('<h4>Conventions</h4><ul class="conventions">')
    for t in [
        "« … » : un texte de l'écran, mot pour mot (menu, bouton, champ, message).",
        "A → B → C : le chemin des menus, à toucher dans cet ordre.",
        "≡ : le menu en haut à droite de la caisse ; ⌫ : la touche d'effacement du pavé.",
        "« taper 1001 » : les quatre chiffres d'un code, d'un trait.",
        "Montants en FCFA ; dates au format jj/mm/aaaa.",
    ]:
        o.append('<li>%s</li>' % riche(t))
    o.append('</ul>')

    o.append('<h2>3. Les scénarios en un coup d\'œil</h2>')
    o.append('<table class="simple sommaire"><thead><tr><th>N°</th><th>Scénario</th><th>Rôle</th>'
             '<th>Étapes</th><th>Cas</th><th>Joué</th></tr></thead><tbody>')
    for p, (titre, module) in PARTIES.items():
        o.append('<tr class="partie"><td colspan="6">%s. %s — %s</td></tr>' % (p, typo(titre), typo(module)))
        for sc in [s for s in S.SCENARIOS if s['partie'] == p]:
            o.append('<tr><td>%s</td><td>%s</td><td>%s</td><td class="nb">%d</td><td class="nb">%s</td>'
                     '<td class="nb">%s</td></tr>' % (
                         sc['id'], typo(sc['titre']), typo(sc['role']), len(sc['etapes']),
                         len(cas_de(sc)) or "—", "✓" if sc.get('joue') == 'oui' else ("½" if sc.get('joue') else "")))
    o.append('</tbody></table>')

    for k, (p, (titre, module)) in enumerate(PARTIES.items(), 4):
        o.append('<h2 class="partie">%d. %s</h2>' % (k, typo(titre)))
        for sc in [s for s in S.SCENARIOS if s['partie'] == p]:
            o.append(html_scenario(sc, ecrans))

    k = 4 + len(PARTIES)
    o.append('<h2>%d. Questions fréquentes pendant la recette</h2>' % k)
    o.append('<table class="simple faq"><tr><th>Situation</th><th>Réponse</th></tr>')
    for q, r in S.FAQ:
        o.append('<tr><td>%s</td><td>%s</td></tr>' % (riche(q), riche(r)))
    o.append('</table>')

    o.append('<h2 class="annexe">Annexe A — Couverture du cahier de recette</h2>')
    o.append('<p>%s</p>' % riche(
        "Chaque cas des domaines D, F, H, I, J, K et R de recette/cas_de_test.py et les étapes qui le "
        "jouent (B04.5 = scénario B04, étape 5). generer.py refuse de produire ce cahier si un cas "
        "n'a ni étape ni raison d'être écarté."))
    o.append('<table class="simple couverture-r"><thead><tr><th>Cas</th><th>P</th><th>Intitulé</th>'
             '<th>Étapes</th></tr></thead><tbody>')
    dom = None
    for cid, c in tous.items():
        if c[1] != dom:
            dom = c[1]
            o.append('<tr class="partie"><td colspan="4"><strong>%s — %s</strong></td></tr>' % (
                dom, typo(NOMS_DOMAINES[dom])))
        o.append('<tr><td class="code">%s</td><td class="nb">%d</td><td>%s</td><td>%s</td></tr>' % (
            cid, c[2], typo(c[4]), ", ".join(vus[cid]) or "<em>écarté (annexe B)</em>"))
    o.append('</tbody></table>')

    o.append('<h2>Annexe B — Cas écartés : ils exigent l\'hôtel</h2>')
    o.append('<table class="simple ecartes"><tr><th>Cas</th><th>Intitulé</th><th>Raison</th></tr>')
    for cid, raison in S.CAS_ECARTES.items():
        o.append('<tr><td class="code">%s</td><td>%s</td><td>%s</td></tr>' % (cid, typo(tous[cid][4]), riche(raison)))
    o.append('</table>')

    o.append('<h2>Annexe C — Les scénarios joués avant publication</h2>')
    o.append('<p>%s</p>' % riche(
        "Base jetable créée comme en I01 (Cameroun, Français, sans démonstration), Odoo 18 Community, "
        "navigateur piloté (Playwright) ; les captures de ce cahier viennent de ce passage ou de la "
        "base du restaurant AITE. Chiffres vus : table 4 = 2 Bière blonde 65 cl + 1 Soda 33 cl = "
        "4 000 FCFA, CMV 1 700, marge 2 300 ; stock Bière blonde 48 → 46 → 64 ; inventaire Bière brune "
        "24 → 20 (−2 800 FCFA) ; commande 24 × 700 = 16 800, reçue 18, facture 12 600 à 14 jours ; "
        "Direction : cash à risque 2 800, crédits − dettes −12 600."))
    o.append('<table class="simple"><tr><th>Scénario</th><th>Joué</th><th>Ce qui a été vu</th></tr>')
    for sc in joues:
        o.append('<tr><td>%s — %s</td><td>%s</td><td>%s</td></tr>' % (
            sc['id'], typo(sc['titre']), "en entier" if sc['joue'] == 'oui' else "en partie", riche(sc['vu'])))
    o.append('</table>')

    corps = "\n".join(o)
    return ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>'
            '<title>%s</title><link rel="stylesheet" href="style.css"/></head><body>%s</body></html>'
            % (html.escape(S.TITRE), corps))


# ------------------------------------------------------------------- XLSX
def classeur(tous, vus):
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.datavalidation import DataValidation

    VIOLET = "902C8F"
    fin = Side(style="thin", color="BFBFBF")
    bord = Border(left=fin, right=fin, top=fin, bottom=fin)
    entete = Font(bold=True, color="FFFFFF")
    fond_entete = PatternFill("solid", fgColor=VIOLET)
    fond_sc = PatternFill("solid", fgColor="F3E6F3")
    haut = Alignment(wrap_text=True, vertical="top")

    def tete(ws, noms, largeurs):
        for j, (nom, l) in enumerate(zip(noms, largeurs), 1):
            c = ws.cell(row=1, column=j, value=nom)
            c.font, c.fill, c.border = entete, fond_entete, bord
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            ws.column_dimensions[c.column_letter].width = l

    wb = Workbook()
    me = wb.active
    me.title = "Mode d'emploi"
    lignes = [
        (S.TITRE, True), ("Version %s — AITE CONSULTING" % S.VERSION, False), ("", False),
        ("1. Créer la base de recette (onglet Scénarios, partie A : I01, I02, I03), puis jouer les "
         "parties B à G dans l'ordre ; la partie H après chaque mise à niveau.", False),
        ("2. Un geste par ligne. Comparer l'écran à « Résultat attendu » ; écrire ce qu'on voit dans "
         "« Résultat obtenu » si c'est différent.", False),
        ("3. Choisir OK, KO ou NA (non applicable : matériel ou historique absent) dans « OK/KO ».", False),
        ("4. Décrire tout écart dans « Observations » (heure, compte, message exact).", False),
        ("5. « Synthèse » compte les résultats par scénario ; « Couverture » relie chaque cas du "
         "cahier de recette aux étapes ; « Cas écartés » dit pourquoi K01 à K04 ne se jouent pas ici.", False),
        ("", False),
        ("Comptes : caisse/caisse, manager/manager, chef/chef, admin/admin (mot de passe à changer).", False),
        ("Codes : Brice 1001, Nadège 1002, Loïc 1003 (serveurs) ; Clarisse 2001, Prisca 2002 "
         "(caissières) ; Hervé 3001 (chef de salle) ; Sandrine 4001 (manager).", False),
        ("Le cahier illustré : AITE_Scenarios_Integrateur.pdf ; le guide : AITE_Guide_Integrateur.pdf.", False),
    ]
    for i, (t, gras) in enumerate(lignes, 1):
        c = me.cell(row=i, column=1, value=t)
        c.font = Font(bold=gras, size=14 if gras else 11, color=VIOLET if gras else "222222")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    me.column_dimensions['A'].width = 120

    ws = wb.create_sheet("Scénarios")
    tete(ws, ["N°", "Module", "Scénario", "Rôle", "Prérequis", "Étapes", "Résultat attendu",
              "Cas liés", "Résultat obtenu", "OK/KO", "Observations"],
         [8, 22, 30, 22, 32, 48, 58, 14, 30, 8, 30])
    ws.freeze_panes = "D2"
    dv = DataValidation(type="list", formula1='"OK,KO,NA"', allow_blank=True)
    ws.add_data_validation(dv)
    ecrans = numeros_ecrans()
    r = 2
    for sc in S.SCENARIOS:
        titre = "%s — %s" % (sc['id'], sc['titre'])
        module = PARTIES[sc['partie']][1]
        valeurs = [sc['id'], module, titre, sc['role'],
                   "%s (base : %s)" % (sc['prerequis'], sc['base']), "Ce qu'on vérifie : " + sc['but'],
                   "", " ".join(cas_de(sc)), "", "", ""]
        for j, v in enumerate(valeurs, 1):
            cc = ws.cell(row=r, column=j, value=v)
            cc.fill, cc.border, cc.alignment = fond_sc, bord, haut
            cc.font = Font(bold=True, color=VIOLET)
        r += 1
        for i, (g, a, cas) in enumerate(sc['etapes'], 1):
            valeurs = ["%s.%d" % (sc['id'], i), module, titre, sc['role'],
                       sc['prerequis'] if i == 1 else "", ecrans_absolus(sc, g, ecrans),
                       ecrans_absolus(sc, a, ecrans), cas.replace(" ", ", ") or "—", "", "", ""]
            for j, v in enumerate(valeurs, 1):
                cc = ws.cell(row=r, column=j, value=v)
                cc.border, cc.alignment = bord, haut
            dv.add(ws.cell(row=r, column=10))
            r += 1
    derniere = r - 1
    ws.auto_filter.ref = "A1:K%d" % derniere
    for val, couleur in (("OK", "C6EFCE"), ("KO", "FFC7CE"), ("NA", "EDEDED")):
        ws.conditional_formatting.add("J2:J%d" % derniere, FormulaRule(
            formula=['$J2="%s"' % val], fill=PatternFill("solid", fgColor=couleur)))
    ws.print_title_rows = "1:1"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    sy = wb.create_sheet("Synthèse")
    tete(sy, ["Scénario", "Module", "Titre", "Étapes", "OK", "KO", "NA", "Non joués", "Statut"],
         [10, 26, 60, 9, 9, 9, 9, 11, 14])
    plage_a = "Scénarios!$A$2:$A$%d" % derniere
    plage_j = "Scénarios!$J$2:$J$%d" % derniere
    for k, sc in enumerate(S.SCENARIOS, 2):
        motif = '"%s.*"' % sc['id']
        vals = [sc['id'], PARTIES[sc['partie']][1], sc['titre'], len(sc['etapes']),
                '=COUNTIFS(%s,%s,%s,"OK")' % (plage_a, motif, plage_j),
                '=COUNTIFS(%s,%s,%s,"KO")' % (plage_a, motif, plage_j),
                '=COUNTIFS(%s,%s,%s,"NA")' % (plage_a, motif, plage_j),
                '=D%d-E%d-F%d-G%d' % (k, k, k, k),
                '=IF(F%d>0,"KO",IF(H%d=0,"Terminé","En cours"))' % (k, k)]
        for j, v in enumerate(vals, 1):
            sy.cell(row=k, column=j, value=v).border = bord
    t = len(S.SCENARIOS) + 2
    sy.cell(row=t, column=1, value="Total").font = Font(bold=True)
    for j, col in enumerate("DEFGH", 4):
        cc = sy.cell(row=t, column=j, value="=SUM(%s2:%s%d)" % (col, col, t - 1))
        cc.font, cc.border = Font(bold=True), bord
    sy.freeze_panes = "A2"

    cv = wb.create_sheet("Couverture")
    tete(cv, ["Cas", "Domaine", "Priorité", "Prérequis du cahier", "Intitulé", "Étapes qui le jouent"],
         [8, 30, 9, 40, 55, 40])
    for k, (cid, c) in enumerate(tous.items(), 2):
        etat = ", ".join(vus[cid]) or "écarté : exige l'hôtel (onglet Cas écartés)"
        for j, v in enumerate([cid, NOMS_DOMAINES[c[1]], c[2], c[3], c[4], etat], 1):
            cc = cv.cell(row=k, column=j, value=v)
            cc.border, cc.alignment = bord, haut
    cv.freeze_panes = "A2"
    cv.auto_filter.ref = "A1:F%d" % (len(tous) + 1)

    ec = wb.create_sheet("Cas écartés")
    tete(ec, ["Cas", "Intitulé", "Raison"], [8, 50, 90])
    for k, (cid, raison) in enumerate(S.CAS_ECARTES.items(), 2):
        for j, v in enumerate([cid, tous[cid][4], raison], 1):
            cc = ec.cell(row=k, column=j, value=v)
            cc.border, cc.alignment = bord, haut

    wb.save(XLSX)
    return derniere - 1


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICI, 'build')
    os.makedirs(sortie, exist_ok=True)
    tous, vus = verifier()
    with open(os.path.join(sortie, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_document(tous, vus))
    lignes = classeur(tous, vus)
    nb_et = sum(len(sc['etapes']) for sc in S.SCENARIOS)
    print("scénarios : %d ; étapes : %d ; cas couverts : %d/%d ; écartés : %d ; joués : %d ; "
          "lignes du classeur : %d" % (
              len(S.SCENARIOS), nb_et, sum(1 for v in vus.values() if v), len(tous),
              len(S.CAS_ECARTES), sum(1 for sc in S.SCENARIOS if sc.get('joue')), lignes))


if __name__ == '__main__':
    main()
