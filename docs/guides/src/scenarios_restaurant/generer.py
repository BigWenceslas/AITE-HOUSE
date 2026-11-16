# -*- coding: utf-8 -*-
"""Produit, à partir de scenarios.py :
- <sortie>/index.html (le cahier, à passer à weasyprint par build.sh) ;
- docs/guides/AITE_Restaurant_Scenarios_de_tests.xlsx (le classeur à cocher).

Contrôle au passage que chaque cas R01..R104 de recette/cas_de_test.py est
couvert par au moins une étape, que chaque cas cité existe, et que les
captures citées existent. Sort en erreur sinon.

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

CAPTURES = os.path.join(RACINE, 'captures', 'restaurant')
XLSX = os.path.join(RACINE, 'docs', 'guides', 'AITE_Restaurant_Scenarios_de_tests.xlsx')

PARTIES = OrderedDict([
    ("A", "Mise en place"),
    ("B", "Le service, rôle par rôle (jour 1)"),
    ("C", "Les rapports et l'ardoise (jour 2)"),
    ("D", "Installation et non-régression"),
])

# Le tableau des droits : lu dans le code (models/regles.py, Python pur).
_regles = {}
exec(open(os.path.join(RACINE, 'addons', 'aite_pos_restaurant', 'models', 'regles.py'),
          encoding='utf-8').read(), _regles)
GESTES = [
    ('servir', "Ouvrir ses tables, commander, envoyer, imprimer l'addition, changer les personnes"),
    ('table_collegue', "Toucher la table d'un collègue (encaisser, diviser, réunir…)"),
    ('ouvrir_caisse', "Ouvrir la caisse"),
    ('encaisser', "Encaisser"),
    ('rapport_ventes', "Imprimer le rapport (menu ≡, avec une imprimante)"),
    ('vente_sans_table', "Ouvrir une vente sans table (si le réglage l'autorise)"),
    ('annuler_envoye', "Annuler ce qui est parti (produit, table, tables à la fermeture)"),
    ('especes', "Entrée ou sortie d'espèces"),
    ('fermer_caisse', "Fermer la caisse"),
    ('fermer_avec_ecart', "Fermer au-delà de l'écart de caisse maximum (s'il est réglé)"),
    ('rembourser', "Rembourser une addition payée"),
    ('ardoise', "Mettre sur ardoise"),
    ('prix', "Changer un prix (touche « Prix »)"),
]
NIVEAUX = _regles['NIVEAUX']


def droits():
    lignes = []
    for geste, libelle in GESTES:
        assert geste in _regles['DROITS'], geste
        lignes.append((libelle, [_regles['autorise'](code, geste) for code, _l in NIVEAUX]))
    return lignes


# --------------------------------------------------------------- contrôles
def cas_r():
    return OrderedDict((c[0], c) for c in cas_de_test.CAS if c[1] == 'R')


def couverture():
    tous = cas_r()
    vus = OrderedDict((k, []) for k in tous)
    inconnus = []
    for sc in S.SCENARIOS:
        for i, (_g, _a, cas) in enumerate(sc['etapes'], 1):
            for c in cas.split():
                if c not in vus:
                    inconnus.append((sc['id'], i, c))
                    continue
                ref = "%s.%d" % (sc['id'], i)
                vus[c].append(ref)
    return tous, vus, inconnus


def numeros_ecrans():
    n, table = 0, {}
    for sc in S.SCENARIOS:
        for fichier, _l in sc['captures']:
            n += 1
            table[(sc['id'], fichier)] = n
    return table


def verifier():
    tous, vus, inconnus = couverture()
    erreurs = []
    if inconnus:
        erreurs.append("cas inconnus : %s" % inconnus)
    manquants = [k for k, v in vus.items() if not v]
    if manquants:
        erreurs.append("cas R non couverts : %s" % ", ".join(manquants))
    for sc in S.SCENARIOS:
        for fichier, _l in sc['captures']:
            if not os.path.exists(os.path.join(CAPTURES, fichier)):
                erreurs.append("capture absente : %s" % fichier)
    # Les renvois « écran n » du texte doivent tomber sur une capture du même scénario.
    ecrans = numeros_ecrans()
    for sc in S.SCENARIOS:
        siens = {n for (sid, _f), n in ecrans.items() if sid == sc['id']}
        for g, a, _c in sc['etapes']:
            for n in re.findall(r"écran (\d+)", g + " " + a):
                if int(n) not in siens:
                    erreurs.append("%s : « écran %s » ne désigne pas une de ses captures (%s)"
                                   % (sc['id'], n, sorted(siens)))
    if erreurs:
        sys.exit("✗ " + "\n✗ ".join(erreurs))
    return tous, vus


# ------------------------------------------------------------------- HTML
def typo(texte):
    """Échappe, puis espaces insécables devant : ; ? ! » et après «."""
    t = html.escape(texte, quote=False)
    t = re.sub(r" ([:;?!»])", " \\1", t)
    t = t.replace("« ", "« ")
    return t


def riche(texte):
    """Typo + guillemets en gras sombre (libellés de l'écran) + flèches de menu."""
    t = typo(texte)
    t = re.sub(r"« (.*?) »", r'<span class="ecran">«&#160;\1&#160;»</span>', t)
    t = t.replace(" → ", ' <span class="fleche">→</span> ')
    return t


def etiquette_cas(cas):
    return " ".join('<span class="cas">%s</span>' % c for c in cas.split()) or '<span class="sans">—</span>'


ENCADRES = {
    'reflexe': ("Bon réflexe", "reflexe"),
    'regle': ("Règle d'or", "regle"),
    'attention': ("À savoir", "attention"),
}


def html_scenario(sc, ecrans):
    cas = sorted({c for _g, _a, cs in sc['etapes'] for c in cs.split()})
    o = ['<section class="scenario" id="%s">' % sc['id'], '<div class="tete">']
    o.append('<h3><span class="sid">%s</span> %s</h3>' % (sc['id'], typo(sc['titre'])))
    o.append('<table class="meta">')
    for lib, val in [("Rôles", sc['roles']), ("Base", sc['base']), ("Quand", sc['quand']),
                     ("Prérequis", sc['prerequis'])]:
        o.append('<tr><th>%s</th><td>%s</td></tr>' % (lib, riche(val)))
    o.append('<tr><th>Cas couverts</th><td>%s</td></tr>' % (
        " ".join('<span class="cas">%s</span>' % c for c in cas) or "aucun cas R (contrôles complémentaires)"))
    o.append('</table>')
    o.append('<p class="but"><strong>Ce qu\'on vérifie.</strong> %s</p></div>' % riche(sc['but']))
    o.append('<table class="etapes"><thead><tr><th class="n">N°</th><th>Geste</th>'
             '<th>Résultat attendu</th><th class="c">Cas</th><th class="ok">OK</th></tr></thead><tbody>')
    for i, (g, a, c) in enumerate(sc['etapes'], 1):
        o.append('<tr><td class="n">%d</td><td>%s</td><td>%s</td><td class="c">%s</td>'
                 '<td class="ok"><span class="case"></span></td></tr>' % (i, riche(g), riche(a), etiquette_cas(c)))
    o.append('</tbody></table>')
    for genre, texte in sc['encadres']:
        titre, classe = ENCADRES[genre]
        o.append('<div class="encadre %s"><strong>%s —</strong> %s</div>' % (classe, titre, riche(texte)))
    for fichier, legende in sc['captures']:
        n = ecrans[(sc['id'], fichier)]
        o.append('<figure><img src="img/%s" alt="%s"/><figcaption>Écran %d — %s</figcaption></figure>'
                 % (fichier, html.escape(legende), n, typo(legende)))
    o.append('</section>')
    return "\n".join(o)


def html_document(tous, vus):
    ecrans = numeros_ecrans()
    nb_sc = len(S.SCENARIOS)
    nb_et = sum(len(sc['etapes']) for sc in S.SCENARIOS)
    o = []
    # Couverture
    o.append('<section class="couverture">')
    o.append('<img class="logo" src="img/logo_aite.jpg" alt="AITE Consulting"/>')
    o.append('<p class="surtitre">SCÉNARIOS DE TESTS — RECETTE</p>')
    o.append('<h1>AITE Restaurant</h1>')
    o.append('<p class="soustitre">%s</p>' % typo(
        "Le service à table contrôlé, de bout en bout, rôle par rôle : ce que le testeur touche, "
        "ce que l'écran doit dire"))
    o.append('<table class="fiche">')
    modules = "<br/>".join('%s <span class="version">%s</span> — %s' % (m, v, typo(r)) for m, v, r in S.MODULES)
    for lib, val in [
        ("Public visé", typo("Testeurs du client (manager, chef de salle, caissière, serveurs) et "
                             "chef de projet AITE ; aucune connaissance d'Odoo n'est demandée")),
        ("Modules", modules),
        ("Contenu", typo("%d scénarios, %d étapes ; les %d cas R du cahier de recette couverts "
                         "(tableau en annexe)" % (nb_sc, nb_et, len(tous)))),
        ("À cocher", typo("le classeur AITE_Restaurant_Scenarios_de_tests.xlsx (une ligne par étape)")),
        ("Illustrations", typo("captures réelles de l'application (base de démonstration du restaurant)")),
        ("Éditeur", "AITE CONSULTING — %s" % typo("Odoo 18 · version %s" % S.VERSION)),
    ]:
        o.append('<tr><th>%s</th><td>%s</td></tr>' % (lib, val))
    o.append('</table></section>')

    # 1. Principe
    o.append('<h2>1. Le principe</h2>')
    o.append('<p>%s</p>' % riche(
        "Chaque scénario se joue comme un vrai moment du service : un rôle, une suite de gestes, et "
        "pour chaque geste ce que l'écran doit montrer, avec ses mots exacts. Le testeur fait un seul "
        "geste par ligne, compare l'écran au résultat attendu, puis note OK ou KO dans le classeur "
        "(colonne « OK/KO ») ; un écart se décrit dans « Observations », avec l'heure et, si possible, "
        "une photo de l'écran."))
    o.append('<ol class="principe">')
    for t in [
        "Jouer les scénarios dans l'ordre : la partie B (jour 1) enchaîne un service complet, du "
        "matin à la fermeture ; la partie C se joue le lendemain, sur la même base.",
        "Ne rien faire d'autre sur la base pendant la recette : les chiffres attendus (tables, "
        "personnes, annulations) supposent que seuls les scénarios ont été joués.",
        "Les parties A et D se jouent avec AITE (installation, réglages) ; S19 à S22 sont "
        "indépendants et se jouent sur d'autres bases.",
        "Un résultat qui dépend d'un matériel absent (imprimante de cuisine, lecteur de codes-barres) "
        "se note « NA » (non applicable), pas KO.",
    ]:
        o.append('<li>%s</li>' % riche(t))
    o.append('</ol>')
    o.append('<div class="encadre regle"><strong>Règle d\'or —</strong> %s</div>' % riche(
        "Un KO se note tel quel, sans corriger la base à la main pour continuer : AITE a besoin de "
        "l'écran exact (message, chiffres) pour reproduire."))

    # 2. Avant de commencer
    o.append('<h2>2. Avant de commencer</h2>')
    o.append('<h4>Les bases</h4>')
    o.append('<table class="simple"><tr><th>Base</th><th>Comment la créer</th><th>Scénarios</th></tr>'
             '<tr><td>aite_resto</td><td>%s</td><td>S01 à S18, S22 (refus)</td></tr>'
             '<tr><td>aite_messager</td><td>%s</td><td>S21, S22 (rejeu)</td></tr>'
             '<tr><td>base vierge</td><td>%s</td><td>S19, S20, S22</td></tr></table>' % (
                 riche("dev/setup_env.sh --restaurant (AITE) : 12 tables, carte de démonstration, "
                       "équipe et comptes ci-dessous"),
                 riche("dev/setup_env.sh --restaurant --carte-messager : la carte d'un restaurant "
                       "client (« Restaurant Le Messager »), même salle, même équipe"),
                 riche("écran de création d'Odoo : pays Cameroun, Français, sans démonstration")))
    o.append('<h4>Les comptes Odoo</h4>')
    o.append('<table class="simple bloc"><tr><th>Identifiant / mot de passe</th><th>Nom</th><th>Rôle</th></tr>')
    for login, nom, role in S.COMPTES:
        o.append('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (typo(login), typo(nom), typo(role)))
    o.append('</table>')
    o.append('<h4>L\'équipe et ses codes (jeu d\'essai, noms fictifs)</h4>')
    o.append('<table class="simple bloc"><tr><th>Employé</th><th>Niveau en caisse</th><th>Code</th><th>Ce qu\'il peut faire</th></tr>')
    for nom, niveau, code, quoi in S.EQUIPE:
        o.append('<tr><td>%s</td><td>%s</td><td class="code">%s</td><td>%s</td></tr>' % (
            typo(nom), typo(niveau), code, typo(quoi)))
    o.append('</table>')
    o.append('<h4>Qui peut quoi (tableau des droits, lu dans le code)</h4>')
    o.append('<table class="simple droits"><tr><th>Geste</th>%s<th class="ok">OK</th></tr>' % "".join(
        '<th>%s</th>' % typo(l) for _c, l in NIVEAUX))
    for libelle, oui in droits():
        o.append('<tr><td>%s</td>%s<td class="ok"><span class="case"></span></td></tr>' % (
            typo(libelle), "".join('<td class="oui">✓</td>' if x else '<td class="non">—</td>' for x in oui)))
    o.append('</table>')
    o.append('<h4>Conventions de ce cahier</h4><ul class="conventions">')
    for t in [
        "« … » : un texte de l'écran, mot pour mot (bouton, titre, message).",
        "A → B → C : le chemin des menus de la gestion, à toucher dans cet ordre.",
        "≡ : le menu en haut à droite de la caisse ; ⌫ : la touche d'effacement du pavé.",
        "« taper 1001 » : les quatre chiffres d'un code, d'un trait ; le code est validé seul au "
        "quatrième.",
        "Montants en FCFA ; dates au format jj/mm/aaaa.",
    ]:
        o.append('<li>%s</li>' % riche(t))
    o.append('</ul>')

    # 3. Vue d'ensemble
    o.append('<h2 class="saut">3. Les scénarios en un coup d\'œil</h2>')
    o.append('<table class="simple sommaire"><thead><tr><th>N°</th><th>Scénario</th><th>Rôles</th>'
             '<th>Quand</th><th>Étapes</th><th>Cas R</th></tr></thead><tbody>')
    for p, titre in PARTIES.items():
        o.append('<tr class="partie"><td colspan="6">%s. %s</td></tr>' % (p, typo(titre)))
        for sc in [s for s in S.SCENARIOS if s['partie'] == p]:
            n_cas = len({c for _g, _a, cs in sc['etapes'] for c in cs.split()})
            o.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="nb">%d</td><td class="nb">%s</td></tr>' % (
                sc['id'], typo(sc['titre']), typo(sc['roles']), typo(sc['quand']), len(sc['etapes']),
                n_cas or "—"))
    o.append('</tbody></table>')

    # 4..7 Parties
    for k, (p, titre) in enumerate(PARTIES.items(), 4):
        o.append('<h2 class="partie">%d. %s</h2>' % (k, typo(titre)))
        for sc in [s for s in S.SCENARIOS if s['partie'] == p]:
            o.append(html_scenario(sc, ecrans))

    # FAQ
    o.append('<h2>8. Questions fréquentes pendant la recette</h2>')
    o.append('<table class="simple faq"><tr><th>Situation</th><th>Réponse</th></tr>')
    for q, r in S.FAQ:
        o.append('<tr><td>%s</td><td>%s</td></tr>' % (riche(q), riche(r)))
    o.append('</table>')

    # Annexe A : couverture
    o.append('<h2 class="annexe">Annexe A — Couverture des cas R01 à R104</h2>')
    o.append('<p>%s</p>' % riche(
        "Chaque cas du domaine R du cahier de recette (recette/cas_de_test.py) et les étapes qui le "
        "jouent (S04.8 = scénario S04, étape 8). Aucun cas n'est sans scénario."))
    o.append('<table class="simple couverture-r"><thead><tr><th>Cas</th><th>P</th><th>Intitulé</th><th>Étapes</th></tr></thead><tbody>')
    for cid, c in tous.items():
        o.append('<tr><td class="code">%s</td><td class="nb">%d</td><td>%s</td><td>%s</td></tr>' % (
            cid, c[2], typo(c[4]), ", ".join(vus[cid])))
    o.append('</tbody></table>')

    # Annexe B : notes pour AITE
    o.append('<h2 class="annexe-suite">Annexe B — Écarts relevés entre le cahier de recette et l\'écran</h2>')
    o.append('<p>%s</p>' % riche(
        "Relevés en rédigeant ces scénarios ; les scénarios suivent l'écran (le code et les "
        "traductions d'Odoo), pas le texte du cahier."))
    o.append('<table class="simple faq ecarts"><tr><th>Cas</th><th>Écart</th></tr>')
    for cas, t in ECARTS:
        o.append('<tr><td class="code">%s</td><td>%s</td></tr>' % (cas, riche(t)))
    o.append('</table>')

    corps = "\n".join(o)
    return ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>'
            '<title>%s</title><link rel="stylesheet" href="style.css"/></head><body>%s</body></html>'
            % (html.escape(S.TITRE), corps))


ECARTS = [
    ("R72", "Le cahier écrit « Mettre à jour la quantité » ; le bouton d'Odoo 18 s'appelle « Mettre "
            "la quantité à jour » (comme dans INSTALLATION §9.6)."),
    ("R73 R74", "« Inventaire → Rapports → Historique des mouvements » : le menu d'Odoo 18 en "
                "français est « Inventaire → Analyse → Historique des mouvements »."),
    ("R17", "« valider » : le bouton du sélecteur de table d'Odoo s'appelle « Aller à/au » "
            "(traduction d'Odoo)."),
    ("R19", "« AITE le coche (caisse fermée) » : après la première ouverture, Odoo garde toujours "
            "une session « Contrôle à l'ouverture » qui grise la case (notes, point 25). La partie "
            "« cochée » se joue donc sur une base dont la caisse n'a jamais été ouverte (S21)."),
    ("R80", "« Trois lignes » : le nombre dépend de la journée ; ici le jour 1 en produit sept "
            "(S14)."),
    ("R89", "Dates d'exemple en décembre 2026 : futures à la date de la recette ; S15 prend une "
            "période qui contient le jour 1."),
    ("R43", "« Bon d'annulation envoyé. » n'apparaît qu'avec une imprimante de cuisine ; il n'a "
            "jamais été vu (notes §8)."),
    ("R66 R67", "60 minutes et 10 minutes d'attente : S12 règle un délai de 2 minutes pour la "
                "couleur et garde 5 minutes pour le retour au plan ; la mesure à 60 minutes est à "
                "faire une fois en vrai service."),
    ("R21", "Le cahier attend « Il faut au moins une personne à table. » quand rien n'est tapé "
            "après « 9 et plus » ; la caisse ne l'affiche qu'une fois un 0 tapé (S04, étapes 5 "
            "et 6) : « Valider » grisé suffit à empêcher l'ouverture."),
    ("—", "La fenêtre d'espèces d'Odoo garde « Cash entrant » / « Cash sortant » et confirme par "
          "« Vous avez réussi à faire un out en espèces de 1 000 FCFA. » (« in » pour une entrée), "
          "alors que le menu ≡ dit « Entrée ou sortie d'espèces » : anglais résiduel (règle 6)."),
    ("—", "aite_resto_carte_messager n'a aucun cas dans le cahier de recette : S21 et S22 le "
          "couvrent sans référence R. Son refus sur une base à carte de démonstration montre au "
          "client un message technique (commande dev/setup_env.sh)."),
    ("—", "La passerelle aite_pos_analytics_hr nomme le regroupement « Serveur » dans le menu "
          "« Regrouper par » et le champ « Serveur (ouverte par) » (R102 cite le second)."),
]


# ------------------------------------------------------------------- XLSX
def classeur(tous, vus):
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.datavalidation import DataValidation

    VIOLET, ORANGE = "902C8F", "ED9720"
    fin = Side(style="thin", color="BFBFBF")
    bord = Border(left=fin, right=fin, top=fin, bottom=fin)
    entete = Font(bold=True, color="FFFFFF")
    fond_entete = PatternFill("solid", fgColor=VIOLET)
    fond_sc = PatternFill("solid", fgColor="F3E6F3")
    haut = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()
    # Mode d'emploi
    me = wb.active
    me.title = "Mode d'emploi"
    lignes = [
        (S.TITRE, True),
        ("Version %s — AITE CONSULTING" % S.VERSION, False),
        ("", False),
        ("1. Jouer chaque étape de l'onglet « Scénarios » dans l'ordre : un geste par ligne.", False),
        ("2. Comparer l'écran à « Résultat attendu » ; écrire ce qu'on voit dans « Résultat obtenu » "
         "si c'est différent.", False),
        ("3. Choisir OK, KO ou NA (non applicable : matériel absent) dans la colonne « OK/KO ».", False),
        ("4. Décrire tout écart dans « Observations » (heure, poste, message exact).", False),
        ("5. L'onglet « Synthèse » compte les résultats par scénario ; « Couverture R » relie chaque "
         "cas du cahier de recette aux étapes.", False),
        ("", False),
        ("Bases : aite_resto (S01 à S18), aite_messager (S21), base vierge (S19, S20, S22).", False),
        ("Comptes : caisse/caisse, manager/manager, chef/chef, admin/admin.", False),
        ("Codes : Brice 1001 et Nadège 1002 (serveurs), Clarisse 2001 (caissière), Hervé 3001 "
         "(chef de salle), Sandrine 4001 (manager).", False),
        ("Le cahier illustré (PDF) donne les écrans attendus : AITE_Restaurant_Scenarios_de_tests.pdf.", False),
    ]
    for i, (t, gras) in enumerate(lignes, 1):
        c = me.cell(row=i, column=1, value=t)
        c.font = Font(bold=gras, size=14 if gras else 11, color=VIOLET if gras else "222222")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    me.column_dimensions['A'].width = 120

    # Scénarios
    ws = wb.create_sheet("Scénarios")
    colonnes = ["N°", "Scénario", "Rôle", "Prérequis", "Étapes", "Résultat attendu",
                "Cas de recette R liés", "Résultat obtenu", "OK/KO", "Observations"]
    largeurs = [8, 30, 22, 34, 50, 60, 14, 30, 8, 30]
    for j, (nom, l) in enumerate(zip(colonnes, largeurs), 1):
        c = ws.cell(row=1, column=j, value=nom)
        c.font, c.fill, c.border = entete, fond_entete, bord
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[c.column_letter].width = l
    ws.freeze_panes = "C2"
    dv = DataValidation(type="list", formula1='"OK,KO,NA"', allow_blank=True)
    ws.add_data_validation(dv)
    r = 2
    for sc in S.SCENARIOS:
        titre = "%s — %s" % (sc['id'], sc['titre'])
        c = ws.cell(row=r, column=1, value=sc['id'])
        ws.cell(row=r, column=2, value=titre)
        ws.cell(row=r, column=3, value=sc['roles'])
        ws.cell(row=r, column=4, value="%s (base : %s ; %s)" % (sc['prerequis'], sc['base'], sc['quand']))
        ws.cell(row=r, column=5, value="Ce qu'on vérifie : " + sc['but'])
        for j in range(1, 11):
            cc = ws.cell(row=r, column=j)
            cc.fill, cc.border, cc.alignment = fond_sc, bord, haut
            cc.font = Font(bold=True, color=VIOLET)
        r += 1
        for i, (g, a, cas) in enumerate(sc['etapes'], 1):
            valeurs = ["%s.%d" % (sc['id'], i), titre, sc['roles'], sc['prerequis'] if i == 1 else "",
                       g, a, cas.replace(" ", ", ") or "—", "", "", ""]
            for j, v in enumerate(valeurs, 1):
                cc = ws.cell(row=r, column=j, value=v)
                cc.border, cc.alignment = bord, haut
            dv.add(ws.cell(row=r, column=9))
            r += 1
    derniere = r - 1
    ws.auto_filter.ref = "A1:J%d" % derniere
    ws.conditional_formatting.add("I2:I%d" % derniere, FormulaRule(
        formula=['$I2="OK"'], fill=PatternFill("solid", fgColor="C6EFCE")))
    ws.conditional_formatting.add("I2:I%d" % derniere, FormulaRule(
        formula=['$I2="KO"'], fill=PatternFill("solid", fgColor="FFC7CE")))
    ws.conditional_formatting.add("I2:I%d" % derniere, FormulaRule(
        formula=['$I2="NA"'], fill=PatternFill("solid", fgColor="EDEDED")))
    ws.print_title_rows = "1:1"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # Synthèse
    sy = wb.create_sheet("Synthèse")
    tete = ["Scénario", "Titre", "Étapes", "OK", "KO", "NA", "Non joués", "Statut"]
    for j, (t, l) in enumerate(zip(tete, [10, 60, 9, 9, 9, 9, 11, 14]), 1):
        c = sy.cell(row=1, column=j, value=t)
        c.font, c.fill, c.border = entete, fond_entete, bord
        sy.column_dimensions[c.column_letter].width = l
    plage_a = "Scénarios!$A$2:$A$%d" % derniere
    plage_i = "Scénarios!$I$2:$I$%d" % derniere
    for k, sc in enumerate(S.SCENARIOS, 2):
        motif = '"%s.*"' % sc['id']
        vals = [sc['id'], sc['titre'], len(sc['etapes']),
                '=COUNTIFS(%s,%s,%s,"OK")' % (plage_a, motif, plage_i),
                '=COUNTIFS(%s,%s,%s,"KO")' % (plage_a, motif, plage_i),
                '=COUNTIFS(%s,%s,%s,"NA")' % (plage_a, motif, plage_i),
                '=C%d-D%d-E%d-F%d' % (k, k, k, k),
                '=IF(E%d>0,"KO",IF(G%d=0,"Terminé","En cours"))' % (k, k)]
        for j, v in enumerate(vals, 1):
            cc = sy.cell(row=k, column=j, value=v)
            cc.border = bord
    t = len(S.SCENARIOS) + 2
    sy.cell(row=t, column=1, value="Total").font = Font(bold=True)
    for j, col in enumerate("CDEFG", 3):
        cc = sy.cell(row=t, column=j, value="=SUM(%s2:%s%d)" % (col, col, t - 1))
        cc.font, cc.border = Font(bold=True), bord
    sy.freeze_panes = "A2"

    # Couverture R
    cv = wb.create_sheet("Couverture R")
    tete = ["Cas", "Priorité", "Prérequis du cahier", "Intitulé", "Étapes qui le jouent"]
    for j, (t2, l) in enumerate(zip(tete, [8, 9, 40, 55, 40]), 1):
        c = cv.cell(row=1, column=j, value=t2)
        c.font, c.fill, c.border = entete, fond_entete, bord
        cv.column_dimensions[c.column_letter].width = l
    for k, (cid, c) in enumerate(tous.items(), 2):
        for j, v in enumerate([cid, c[2], c[3], c[4], ", ".join(vus[cid])], 1):
            cc = cv.cell(row=k, column=j, value=v)
            cc.border, cc.alignment = bord, haut
    cv.freeze_panes = "A2"
    cv.auto_filter.ref = "A1:E%d" % (len(tous) + 1)

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
    print("scénarios : %d ; étapes : %d ; cas R couverts : %d/%d ; lignes du classeur : %d"
          % (len(S.SCENARIOS), nb_et, sum(1 for v in vus.values() if v), len(tous), lignes))


if __name__ == '__main__':
    main()
