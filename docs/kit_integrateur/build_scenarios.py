# -*- coding: utf-8 -*-
"""Produit le cahier des scénarios de test du kit intégrateur, à partir de
scenarios_test.py (même dossier) :

  AITE_Scenarios_Test_Restaurant_v18.0.1.0.14.xlsx  (openpyxl)
  AITE_Scenarios_Test_Restaurant_v18.0.1.0.14.pdf   (weasyprint)

    python3 docs/kit_integrateur/build_scenarios.py            # les deux
    python3 docs/kit_integrateur/build_scenarios.py --xlsx     # le classeur seul

Le PDF demande weasyprint (pip install weasyprint) ; sans lui, seul le
classeur est produit et le script le dit.
"""
import html
import math
import re
import os
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from scenarios_test import (DATE_VERIFICATION, FONCTIONS, IMPRIMANTES, PERSONNES, PRIX,  # noqa: E402
                            SCENARIOS, VERSION)

NOM = "AITE_Scenarios_Test_Restaurant_v%s" % VERSION
VIOLET, ORANGE, GRIS, TRAIT, BLANC = "902C8F", "ED9720", "F3F1F4", "D9D2DB", "FFFFFF"
POLICE = "Calibri"
STATUTS = ["OK", "KO", "S.O.", "Bloqué"]
NOM_F = {code: nom for code, nom, _ in FONCTIONS}
MODULE_F = {code: module for code, _, module in FONCTIONS}

MODE_EMPLOI = [
    ("À quoi sert ce cahier",
     "Vérifier chez le client, après la mise à niveau, les nouvelles fonctionnalités de la caisse du "
     "restaurant (aite_pos_restaurant 18.0.1.0.11 à 18.0.1.0.14) et de la carte Le Messager "
     "(18.0.1.3.5 et 18.0.1.3.6). Il ne teste rien d'autre."),
    ("Avant de commencer",
     "1. La mise à niveau est faite sur chaque base (guide de l'intégrateur, procédure du serveur). "
     "2. Choisissez un moment sans service : les tests envoient de vrais bons en cuisine et "
     "enregistrent de vraies ventes. 3. Si possible, jouez sur une copie de la base (base de recette) ; "
     "sinon, prévenez le gérant : les ventes de test resteront dans les rapports du jour. "
     "4. Ayez sous la main les codes d'un serveur, d'une caissière, d'un chef de salle et du manager."),
    ("Comment jouer un scénario",
     "Lisez le prérequis et les données. Faites chaque étape dans l'ordre : une action, puis vérifiez "
     "que vous voyez exactement ce qui est écrit (mêmes mots, mêmes montants). Les libellés entre « » "
     "sont ceux de l'écran. Les montants sont en FCFA, les dates au format JJ/MM/AAAA."),
    ("Comment noter le résultat",
     "OK : tout ce qui est écrit est vu. KO : une seule différence suffit ; écrivez dans « Observations » "
     "l'étape et ce que vous avez vu (une photo de l'écran aide). S.O. (sans objet) : le scénario ne "
     "s'applique pas chez ce client (ex. Odoo n'est pas en https). Bloqué : impossible de le jouer "
     "(dites pourquoi). Remplissez aussi « Testeur » et « Date »."),
    ("Ordre conseillé",
     "Les blocs A à G dans l'ordre : A (contrôles après la mise à niveau), B (réglage des imprimantes), "
     "C (envoi), D (notes), E (addition), F (paiement à parts égales), G (non-régression). Plusieurs "
     "scénarios reprennent la table du précédent : ne sautez pas d'étape."),
    ("Noms et tables",
     "Les prénoms, codes et numéros de table sont ceux de la base de démonstration. Chez le client, "
     "prenez un employé réel du même niveau et toute table libre ; écrivez dans « Observations » la "
     "table utilisée. Si un mode de paiement porte un autre nom, prenez l'équivalent."),
    ("Prix du client",
     "Les montants attendus viennent des prix de la carte de démonstration (tableau « Prix de "
     "référence »). Avant de commencer, comparez ces prix à ceux de la caisse du client. Si un prix "
     "diffère, refaites le calcul avec le prix du client : ce n'est pas un KO. Notez dans "
     "« Observations » le prix utilisé et le montant obtenu."),
    ("Textes d'Odoo en anglais",
     "Les boutons de modèles des fenêtres de note (Wait, To Serve, Emergency, No Dressing) sont créés "
     "par Odoo en anglais : ce n'est pas un KO. Le guide (4.6) explique comment les renommer."),
    ("Après la recette",
     "Archivez le produit de test « Bougie d'anniversaire » (ST-05). Remettez les réglages choisis par "
     "le gérant. Envoyez le classeur rempli à AITE. Un KO : ne pas improviser de correction, appeler AITE."),
]


def lignes_etapes(etapes, avec_numero=True):
    """« 1. action ⏎ → Vous devez voir : … »"""
    sortie = []
    for i, (action, voir) in enumerate(etapes, 1):
        sortie.append("%d. %s" % (i, action) if avec_numero else action)
        sortie.append("    → Vous devez voir : %s" % voir)
    return "\n".join(sortie)


def hauteur(textes_largeurs, ligne_pt=12.6, minimum=30):
    """Hauteur de ligne estimée : le texte le plus long, coupé à la largeur
    de sa colonne (en caractères, police 9)."""
    plus = 1
    for texte, largeur in textes_largeurs:
        par_ligne = max(8, largeur * 1.3)
        n = sum(max(1, math.ceil(len(morceau) / par_ligne)) for morceau in str(texte).split("\n"))
        plus = max(plus, n)
    return max(minimum, min(409, plus * ligne_pt + 6))


# ================================================================== XLSX
def construire_xlsx(chemin):
    wb = Workbook()
    fin = Side(style="thin", color=TRAIT)
    bord = Border(left=fin, right=fin, top=fin, bottom=fin)
    haut = Alignment(wrap_text=True, vertical="top")
    centre = Alignment(wrap_text=True, vertical="top", horizontal="center")

    # ---------------------------------------------------- Mode d'emploi
    me = wb.active
    me.title = "Mode d'emploi"
    me.sheet_view.showGridLines = False
    me.column_dimensions["A"].width = 2
    me.column_dimensions["B"].width = 30
    me.column_dimensions["C"].width = 32
    me.column_dimensions["D"].width = 30
    me.column_dimensions["E"].width = 40
    me["B2"] = "SCÉNARIOS DE TEST — RESTAURANT LE MESSAGER"
    me["B2"].font = Font(name=POLICE, size=18, bold=True, color=VIOLET)
    me["B3"] = ("Nouvelles fonctionnalités de la caisse du restaurant — aite_pos_restaurant %s, "
                "aite_resto_carte_messager 18.0.1.3.6 — Odoo 18 Community" % VERSION)
    me["B3"].font = Font(name=POLICE, size=11, bold=True, color=ORANGE)
    me["B4"] = "AITE Consulting · document destiné à l'intégrateur · %d scénarios" % len(SCENARIOS)
    me["B4"].font = Font(name=POLICE, size=9, color="666666")

    r = 6
    me.cell(r, 2, "IDENTIFICATION").font = Font(name=POLICE, bold=True, color=BLANC)
    for c in range(2, 6):
        me.cell(r, c).fill = PatternFill("solid", fgColor=VIOLET)
    r += 1
    for libelle in ("Client", "Base(s) testée(s)", "Adresse d'Odoo (http ou https)", "Testeur",
                    "Date de début (JJ/MM/AAAA)", "Date de fin (JJ/MM/AAAA)"):
        me.cell(r, 2, libelle).font = Font(name=POLICE, bold=True, size=10)
        valeur = "Restaurant Le Messager" if libelle == "Client" else ""
        cellule = me.cell(r, 3, valeur)
        cellule.fill = PatternFill("solid", fgColor="FFF6D6")
        me.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        for c in range(2, 6):
            me.cell(r, c).border = bord
        r += 1

    r += 1
    for titre, texte in MODE_EMPLOI:
        me.cell(r, 2, titre).font = Font(name=POLICE, bold=True, size=10, color=VIOLET)
        me.cell(r, 2).alignment = haut
        cellule = me.cell(r, 3, texte)
        cellule.alignment = haut
        cellule.font = Font(name=POLICE, size=10)
        me.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        me.row_dimensions[r].height = hauteur([(texte, 98)], ligne_pt=13.5)
        r += 1

    r += 1
    me.cell(r, 2, "LES PERSONNES DU TEST").font = Font(name=POLICE, bold=True, color=BLANC)
    for c in range(2, 6):
        me.cell(r, c).fill = PatternFill("solid", fgColor=VIOLET)
    r += 1
    for c, t in enumerate(("Rôle dans les scénarios", "Niveau en caisse", "Démo : prénom", "Démo : code"), 2):
        me.cell(r, c, t).font = Font(name=POLICE, bold=True, size=10)
        me.cell(r, c).fill = PatternFill("solid", fgColor=GRIS)
        me.cell(r, c).border = bord
    r += 1
    for ligne in PERSONNES:
        for c, t in enumerate(ligne, 2):
            me.cell(r, c, t).font = Font(name=POLICE, size=10)
            me.cell(r, c).border = bord
        r += 1

    r += 1
    me.cell(r, 2, "LES CINQ IMPRIMANTES (ST-06)").font = Font(name=POLICE, bold=True, color=BLANC)
    for c in range(2, 6):
        me.cell(r, c).fill = PatternFill("solid", fgColor=VIOLET)
    r += 1
    for c, t in enumerate(("Imprimante", "Adresse IP (exemple)", "Catégories de produit imprimées"), 2):
        me.cell(r, c, t).font = Font(name=POLICE, bold=True, size=10)
        me.cell(r, c).fill = PatternFill("solid", fgColor=GRIS)
        me.cell(r, c).border = bord
    me.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
    r += 1
    for nom, ip, familles in IMPRIMANTES:
        me.cell(r, 2, nom).font = Font(name=POLICE, size=10, bold=True)
        me.cell(r, 3, ip).font = Font(name=POLICE, size=10)
        me.cell(r, 4, familles).font = Font(name=POLICE, size=10)
        me.cell(r, 4).alignment = haut
        me.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        for c in range(2, 6):
            me.cell(r, c).border = bord
        me.row_dimensions[r].height = hauteur([(familles, 66)], ligne_pt=13.5, minimum=16)
        r += 1

    r += 1
    me.cell(r, 2, "PRIX DE RÉFÉRENCE (CARTE DE DÉMONSTRATION)").font = Font(name=POLICE, bold=True, color=BLANC)
    for c in range(2, 6):
        me.cell(r, c).fill = PatternFill("solid", fgColor=VIOLET)
    r += 1
    for c, t in enumerate(("Produit", "Prix (FCFA)", "Prix chez le client (FCFA)"), 2):
        me.cell(r, c, t).font = Font(name=POLICE, bold=True, size=10)
        me.cell(r, c).fill = PatternFill("solid", fgColor=GRIS)
        me.cell(r, c).border = bord
    me.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
    r += 1
    for nom, prix in PRIX:
        me.cell(r, 2, nom).font = Font(name=POLICE, size=10)
        me.cell(r, 3, prix).font = Font(name=POLICE, size=10)
        me.cell(r, 4).fill = PatternFill("solid", fgColor="FFF6D6")
        me.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        for c in range(2, 6):
            me.cell(r, c).border = bord
        r += 1

    r += 1
    me.cell(r, 2, "Fonctionnalités").font = Font(name=POLICE, bold=True, color=BLANC)
    for c in range(2, 6):
        me.cell(r, c).fill = PatternFill("solid", fgColor=VIOLET)
    r += 1
    for code, nom, module in FONCTIONS:
        me.cell(r, 2, code).font = Font(name=POLICE, size=10, bold=True)
        me.cell(r, 3, nom).font = Font(name=POLICE, size=10)
        me.cell(r, 3).alignment = haut
        me.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
        me.cell(r, 5, module).font = Font(name=POLICE, size=10)
        for c in range(2, 6):
            me.cell(r, c).border = bord
        me.row_dimensions[r].height = hauteur([(nom, 60)], ligne_pt=13.5, minimum=16)
        r += 1

    me.page_setup.orientation = "portrait"
    me.page_setup.paperSize = me.PAPERSIZE_A4
    me.page_setup.fitToWidth = 1
    me.page_setup.fitToHeight = 0
    me.sheet_properties.pageSetUpPr.fitToPage = True
    me.print_options.horizontalCentered = True
    me.page_margins.left = me.page_margins.right = 0.4
    me.oddFooter.center.text = "AITE Consulting — Scénarios de test Restaurant %s — Page &P / &N" % VERSION

    # ---------------------------------------------------------- Scénarios
    ws = wb.create_sheet("Scénarios")
    ws.sheet_view.showGridLines = False
    colonnes = [  # (titre, largeur)
        ("ID", 7), ("Fonctionnalité", 18), ("Version", 11), ("Rôle", 13),
        ("Prérequis et données", 32), ("Étapes : action → ce que vous devez voir", 70),
        ("Résultat attendu", 30), ("Résultat", 9), ("Observations", 26), ("Testeur", 11),
        ("Date", 11), ("Cas de recette", 10), ("Vérifié par AITE avant livraison", 22),
    ]
    ws["A1"] = "SCÉNARIOS DE TEST — Restaurant Le Messager — aite_pos_restaurant %s" % VERSION
    ws["A1"].font = Font(name=POLICE, size=14, bold=True, color=VIOLET)
    ws["A2"] = ("Une ligne = un scénario. Colonne « Résultat » : choisissez OK, KO, S.O. (sans objet) "
                "ou Bloqué dans la liste. Un KO : écrivez l'étape et ce que vous avez vu.")
    ws["A2"].font = Font(name=POLICE, size=9, italic=True, color="555555")
    ENTETE = 4
    for c, (titre, largeur) in enumerate(colonnes, 1):
        cellule = ws.cell(ENTETE, c, titre)
        cellule.font = Font(name=POLICE, size=10, bold=True, color=BLANC)
        cellule.fill = PatternFill("solid", fgColor=VIOLET)
        cellule.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cellule.border = bord
        ws.column_dimensions[get_column_letter(c)].width = largeur
    ws.row_dimensions[ENTETE].height = 30
    ws.freeze_panes = "B5"

    validation = DataValidation(type="list", formula1='"%s"' % ",".join(STATUTS), allow_blank=True,
                                showDropDown=False)
    validation.error = "Choisissez OK, KO, S.O. ou Bloqué."
    validation.errorTitle = "Résultat"
    validation.prompt = "OK, KO, S.O. (sans objet) ou Bloqué"
    validation.promptTitle = "Résultat"
    ws.add_data_validation(validation)

    r = ENTETE + 1
    bloc_courant = None
    lignes_scenarios = []
    for s in SCENARIOS:
        if s["bloc"] != bloc_courant:
            bloc_courant = s["bloc"]
            ws.cell(r, 1, bloc_courant).font = Font(name=POLICE, size=11, bold=True, color=VIOLET)
            for c in range(1, len(colonnes) + 1):
                ws.cell(r, c).fill = PatternFill("solid", fgColor=GRIS)
                ws.cell(r, c).border = bord
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(colonnes))
            ws.row_dimensions[r].height = 20
            r += 1
        fonction = "%s — %s" % (s["f"], NOM_F[s["f"]])
        prerequis = "Prérequis : %s\n\nDonnées : %s" % (s["prerequis"], s["donnees"])
        etapes = lignes_etapes(s["etapes"])
        valeurs = [s["id"], fonction, s["version"], s["role"], prerequis,
                   "%s\n\n%s" % (s["titre"].upper(), etapes), s["attendu"], None, None, None, None,
                   s["recette"], s["verifie"]]
        for c, v in enumerate(valeurs, 1):
            cellule = ws.cell(r, c, v)
            cellule.font = Font(name=POLICE, size=9, bold=(c == 1))
            cellule.alignment = centre if c in (1, 3, 8, 11, 12) else haut
            cellule.border = bord
        for c in (8, 9, 10, 11):
            ws.cell(r, c).fill = PatternFill("solid", fgColor="FFF6D6")
        ws.cell(r, 11).number_format = "DD/MM/YYYY"
        validation.add(ws.cell(r, 8))
        ws.row_dimensions[r].height = hauteur([
            (etapes + "\n\n" + s["titre"], colonnes[5][1]), (prerequis, colonnes[4][1]),
            (s["attendu"], colonnes[6][1]), (s["verifie"], colonnes[12][1]), (fonction, colonnes[1][1])])
        lignes_scenarios.append(r)
        r += 1
    derniere = r - 1
    vert = PatternFill("solid", fgColor="C6EFCE")
    rouge = PatternFill("solid", fgColor="FFC7CE")
    jaune = PatternFill("solid", fgColor="FFEB9C")
    plage = "H%d:H%d" % (ENTETE + 1, derniere)
    ws.conditional_formatting.add(plage, CellIsRule(operator="equal", formula=['"OK"'], fill=vert))
    ws.conditional_formatting.add(plage, CellIsRule(operator="equal", formula=['"KO"'], fill=rouge))
    ws.conditional_formatting.add(plage, CellIsRule(operator="equal", formula=['"Bloqué"'], fill=jaune))
    ws.auto_filter.ref = "A%d:%s%d" % (ENTETE, get_column_letter(len(colonnes)), derniere)

    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "%d:%d" % (ENTETE, ENTETE)
    ws.page_margins.left = ws.page_margins.right = 0.3
    ws.page_margins.top = 0.5
    ws.page_margins.bottom = 0.6
    ws.print_area = "A1:%s%d" % (get_column_letter(len(colonnes)), derniere)
    ws.oddFooter.center.text = "AITE Consulting — Scénarios de test Restaurant %s — Page &P / &N" % VERSION

    # ----------------------------------------------------------- Synthèse
    sy = wb.create_sheet("Synthèse")
    sy.sheet_view.showGridLines = False
    titres = ["Code", "Fonctionnalité", "Module et version", "Scénarios", "OK", "KO", "S.O.",
              "Bloqué", "Pas encore joués", "% OK (hors S.O.)"]
    largeurs = [7, 46, 30, 10, 8, 8, 8, 8, 10, 11]
    sy["A1"] = "SYNTHÈSE DE LA RECETTE — calculée d'après l'onglet « Scénarios »"
    sy["A1"].font = Font(name=POLICE, size=14, bold=True, color=VIOLET)
    for c, (t, l) in enumerate(zip(titres, largeurs), 1):
        cellule = sy.cell(3, c, t)
        cellule.font = Font(name=POLICE, size=10, bold=True, color=BLANC)
        cellule.fill = PatternFill("solid", fgColor=VIOLET)
        cellule.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
        cellule.border = bord
        sy.column_dimensions[get_column_letter(c)].width = l
    sy.row_dimensions[3].height = 30
    plage_f = "Scénarios!$B$%d:$B$%d" % (ENTETE + 1, derniere)
    plage_r = "Scénarios!$H$%d:$H$%d" % (ENTETE + 1, derniere)
    r = 4
    for code, nom, module in FONCTIONS:
        critere = '"%s —*"' % code
        sy.cell(r, 1, code)
        sy.cell(r, 2, nom)
        sy.cell(r, 3, module)
        sy.cell(r, 4, "=COUNTIF(%s,%s)" % (plage_f, critere))
        for c, statut in zip((5, 6, 7, 8), STATUTS):
            sy.cell(r, c, '=COUNTIFS(%s,%s,%s,"%s")' % (plage_f, critere, plage_r, statut))
        sy.cell(r, 9, "=D{0}-E{0}-F{0}-G{0}-H{0}".format(r))
        sy.cell(r, 10, '=IF(D{0}-G{0}=0,"",E{0}/(D{0}-G{0}))'.format(r))
        sy.cell(r, 10).number_format = "0%"
        for c in range(1, 11):
            sy.cell(r, c).border = bord
            sy.cell(r, c).font = Font(name=POLICE, size=10, bold=(c == 1))
            sy.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top",
                                                horizontal="left" if c in (2, 3) else "center")
        r += 1
    total = r
    sy.cell(total, 1, "Total")
    sy.cell(total, 2, "Toutes les fonctionnalités")
    for c in range(4, 10):
        lettre = get_column_letter(c)
        sy.cell(total, c, "=SUM(%s4:%s%d)" % (lettre, lettre, total - 1))
    sy.cell(total, 10, '=IF(D{0}-G{0}=0,"",E{0}/(D{0}-G{0}))'.format(total))
    sy.cell(total, 10).number_format = "0%"
    for c in range(1, 11):
        sy.cell(total, c).font = Font(name=POLICE, size=10, bold=True)
        sy.cell(total, c).fill = PatternFill("solid", fgColor=GRIS)
        sy.cell(total, c).border = bord
        sy.cell(total, c).alignment = Alignment(horizontal="left" if c in (2, 3) else "center")
    r = total + 2
    sy.cell(r, 2, "Verdict").font = Font(name=POLICE, size=11, bold=True, color=VIOLET)
    sy.cell(r, 3, '=IF(F{0}>0,"NON CONFORME : au moins un KO, appeler AITE",IF(H{0}+I{0}>0,'
                  '"EN COURS : scénarios bloqués ou pas encore joués","CONFORME"))'.format(total))
    sy.cell(r, 3).font = Font(name=POLICE, size=11, bold=True)
    sy.merge_cells(start_row=r, start_column=3, end_row=r, end_column=10)
    r += 2
    for libelle in ("Intégrateur (nom, signature)", "Gérant du restaurant (nom, signature)", "Date (JJ/MM/AAAA)"):
        sy.cell(r, 2, libelle).font = Font(name=POLICE, size=10, bold=True)
        sy.cell(r, 3).fill = PatternFill("solid", fgColor="FFF6D6")
        sy.merge_cells(start_row=r, start_column=3, end_row=r, end_column=10)
        sy.row_dimensions[r].height = 28
        r += 1
    sy.page_setup.orientation = "landscape"
    sy.page_setup.paperSize = sy.PAPERSIZE_A4
    sy.page_setup.fitToWidth = 1
    sy.page_setup.fitToHeight = 0
    sy.sheet_properties.pageSetUpPr.fitToPage = True
    sy.oddFooter.center.text = "AITE Consulting — Synthèse de la recette Restaurant %s" % VERSION

    wb.save(chemin)
    return len(lignes_scenarios)


# =================================================================== PDF
CSS = """
@page { size: A4; margin: 14mm 13mm 16mm 13mm;
  @bottom-center { content: "AITE CONSULTING — Scénarios de test · Restaurant %(v)s · Page " counter(page) " / " counter(pages);
    font-family: Carlito, "DejaVu Sans", sans-serif; font-size: 8pt; color: #666; } }
html { font-family: Carlito, "DejaVu Sans", sans-serif; font-size: 9.6pt; color: #222; line-height: 1.28; }
body { margin: 0; }
h1 { color: #902C8F; font-size: 21pt; margin: 1mm 0 0.5mm; }
h2 { color: #902C8F; font-size: 14pt; margin: 5mm 0 2mm; border-bottom: 0.6pt solid #d9d2db; padding-bottom: 1mm; break-after: avoid; }
h2.saut { break-before: page; margin-top: 0; }
.sous-titre { color: #ED9720; font-weight: bold; font-size: 11.5pt; margin: 0 0 3mm; }
.entete { display: flex; justify-content: space-between; align-items: flex-start; }
.entete img { width: 30mm; }
table { border-collapse: collapse; width: 100%%; }
table.info th, table.info td { border: 0.5pt solid #d9d2db; padding: 1.1mm 1.8mm; vertical-align: top; text-align: left; }
table.info th { background: #902C8F; color: white; }
table.info td.l { background: #f3f1f4; font-weight: bold; width: 42mm; }
table.ident td { border: 0.5pt solid #d9d2db; padding: 2.2mm 2mm; }
table.ident td.l { width: 52mm; background: #f3f1f4; font-weight: bold; }
p { margin: 1mm 0 1.8mm; }
.sc { border: 0.7pt solid #cdbfd0; border-radius: 1.5mm; margin: 0 0 4mm; break-inside: avoid; }
.sc.long { break-inside: auto; }
.sc-tete { background: #902C8F; color: white; padding: 1.4mm 2.5mm; display: flex; justify-content: space-between; align-items: baseline; border-radius: 1.3mm 1.3mm 0 0; }
.sc-tete .id { font-weight: bold; font-size: 11pt; }
.sc-tete .titre { font-weight: bold; font-size: 10.5pt; flex: 1; margin: 0 3mm; }
.sc-tete .f { font-size: 8.5pt; white-space: nowrap; }
.sc-meta { display: flex; gap: 3mm; padding: 1.4mm 2.5mm 0.6mm; font-size: 8.8pt; color: #333; flex-wrap: wrap; }
.sc-meta b { color: #902C8F; }
.sc-corps { padding: 0.8mm 2.5mm 2mm; }
.sc-corps .pre { background: #f6f3f7; padding: 1.2mm 2mm; margin: 0.8mm 0 1.5mm; font-size: 8.9pt; }
table.et th { background: #f3f1f4; color: #902C8F; font-size: 8.5pt; text-align: left; border: 0.5pt solid #d9d2db; padding: 0.8mm 1.5mm; }
table.et td { border: 0.5pt solid #d9d2db; padding: 1mm 1.5mm; vertical-align: top; font-size: 9pt; }
table.et tr { break-inside: avoid; }
table.et td.n { width: 5mm; text-align: center; font-weight: bold; color: #902C8F; }
table.et td.a { width: 44%%; }
table.et td.v { color: #1e5b33; }
table.et td.c { width: 7mm; text-align: center; }
.case { display: inline-block; width: 3.4mm; height: 3.4mm; border: 0.35mm solid #666; border-radius: 0.5mm; vertical-align: -0.6mm; }
.attendu { border-left: 1.4mm solid #ED9720; background: #fdf4e7; padding: 1.2mm 2.2mm; margin: 1.6mm 0 1.2mm; break-inside: avoid; }
.verifie { font-size: 8.2pt; color: #555; font-style: italic; margin: 0.6mm 0 1.4mm; }
.resultat { display: flex; gap: 5mm; align-items: center; border-top: 0.5pt dashed #bbb; padding-top: 1.6mm; font-size: 9.3pt; break-inside: avoid; }
.resultat .ligne { flex: 1; border-bottom: 0.5pt solid #999; height: 4mm; }
.obs { border-bottom: 0.5pt solid #999; height: 6mm; margin-top: 0.5mm; }
.bloc { color: #ED9720; font-weight: bold; text-transform: uppercase; letter-spacing: 0.04em; font-size: 10pt; margin: 3mm 0 2mm; break-after: avoid; }
table.syn th { background: #902C8F; color: white; font-size: 8.8pt; border: 0.5pt solid #d9d2db; padding: 1mm 1.5mm; }
table.syn td { border: 0.5pt solid #d9d2db; padding: 1.4mm 1.5mm; font-size: 9pt; }
table.syn td.c { text-align: center; }
"""


def e(texte):
    """Échappe le texte et pose des espaces insécables (« 33 333 FCFA », guillemets)."""
    t = html.escape(str(texte), quote=False)
    t = re.sub(r"(?<=\d) (?=\d{3}\b)", "\u00a0", t)
    t = t.replace("« ", "«\u00a0").replace(" »", "\u00a0»").replace(" FCFA", "\u00a0FCFA")
    for signe in (" :", " ;", " ?", " !"):
        t = t.replace(signe, "\u00a0" + signe[1])
    return t


def construire_html():
    parties = ["<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>",
               "<title>Scénarios de test — Restaurant %s</title>" % VERSION,
               "<meta name='author' content='AITE Consulting'>",
               "<style>%s</style></head><body>" % (CSS % {"v": VERSION})]
    # --- page 1 : mode d'emploi
    parties.append("<div class='entete'><div><h1>Scénarios de test</h1>"
                   "<div class='sous-titre'>Restaurant Le Messager — nouvelles fonctionnalités de la caisse "
                   "(aite_pos_restaurant %s, carte 18.0.1.3.6)</div></div>"
                   "<img src='../logo_aite.jpg' alt='AITE Consulting'></div>" % VERSION)
    parties.append("<table class='ident'>")
    for libelle, valeur in (("Client", "Restaurant Le Messager"), ("Base(s) testée(s)", ""),
                            ("Adresse d'Odoo (http / https)", ""), ("Testeur", ""),
                            ("Date (JJ/MM/AAAA)", "")):
        parties.append("<tr><td class='l'>%s</td><td>%s</td></tr>" % (e(libelle), e(valeur)))
    parties.append("</table>")
    parties.append("<h2>Mode d'emploi</h2><table class='info'>")
    for titre, texte in MODE_EMPLOI:
        parties.append("<tr><td class='l'>%s</td><td>%s</td></tr>" % (e(titre), e(texte)))
    parties.append("</table>")
    parties.append("<h2>Les personnes du test</h2><table class='info'><tr><th>Rôle</th><th>Niveau en caisse"
                   "</th><th>Démo : prénom</th><th>Démo : code</th></tr>")
    for ligne in PERSONNES:
        parties.append("<tr>%s</tr>" % "".join("<td>%s</td>" % e(x) for x in ligne))
    parties.append("</table>")
    parties.append("<h2>Les cinq imprimantes</h2><table class='info'><tr><th>Imprimante</th><th>Adresse IP "
                   "(exemple)</th><th>Catégories de produit imprimées</th></tr>")
    for ligne in IMPRIMANTES:
        parties.append("<tr>%s</tr>" % "".join("<td>%s</td>" % e(x) for x in ligne))
    parties.append("</table>")
    parties.append("<h2>Prix de référence</h2><table class='info'><tr><th>Produit (carte de démonstration)"
                   "</th><th>Prix (FCFA)</th><th>Prix chez le client (FCFA)</th></tr>")
    for nom, prix in PRIX:
        parties.append("<tr><td>%s</td><td>%s</td><td></td></tr>" % (e(nom), e(prix)))
    parties.append("</table>")
    # --- les scénarios
    bloc = None
    premier = True
    for s in SCENARIOS:
        if s["bloc"] != bloc:
            bloc = s["bloc"]
            if premier:
                parties.append("<h2>Les scénarios</h2>")
                premier = False
            parties.append("<div class='bloc'>%s</div>" % e(bloc))
        long = " long" if len(s["etapes"]) > 6 else ""
        parties.append("<div class='sc%s'>" % long)
        parties.append("<div class='sc-tete'><span class='id'>%s</span><span class='titre'>%s</span>"
                       "<span class='f'>%s · %s</span></div>"
                       % (e(s["id"]), e(s["titre"]), e(s["f"]), e(s["version"])))
        parties.append("<div class='sc-meta'><span><b>Fonctionnalité :</b> %s</span><span><b>Rôle :</b> %s</span>"
                       "<span><b>Recette :</b> %s</span></div>"
                       % (e(NOM_F[s["f"]]), e(s["role"]), e(s["recette"])))
        parties.append("<div class='sc-corps'><div class='pre'><b>Prérequis :</b> %s<br><b>Données :</b> %s</div>"
                       % (e(s["prerequis"]), e(s["donnees"])))
        parties.append("<table class='et'><tr><th>N°</th><th>Action</th><th>Vous devez voir</th><th>Vu</th></tr>")
        for i, (action, voir) in enumerate(s["etapes"], 1):
            parties.append("<tr><td class='n'>%d</td><td class='a'>%s</td><td class='v'>%s</td>"
                           "<td class='c'><span class='case'></span></td></tr>" % (i, e(action), e(voir)))
        parties.append("</table>")
        parties.append("<div class='attendu'><b>Résultat attendu :</b> %s</div>" % e(s["attendu"]))
        parties.append("<div class='verifie'>Vérifié par AITE avant livraison : %s</div>" % e(s["verifie"]))
        parties.append("<div class='resultat'><span><span class='case'></span> OK</span>"
                       "<span><span class='case'></span> KO</span><span><span class='case'></span> S.O.</span>"
                       "<span><span class='case'></span> Bloqué</span><span>Testeur :</span>"
                       "<span class='ligne'></span><span>Date :</span><span class='ligne' style='flex:0 0 26mm'></span></div>")
        parties.append("<div>Observations :</div><div class='obs'></div><div class='obs'></div>")
        parties.append("</div></div>")
    # --- synthèse
    parties.append("<h2 class='saut'>Synthèse de la recette</h2><table class='syn'><tr><th>Code</th>"
                   "<th>Fonctionnalité</th><th>Scénarios</th><th>OK</th><th>KO</th><th>S.O.</th>"
                   "<th>Bloqué</th></tr>")
    for code, nom, module in FONCTIONS:
        ids = [s["id"] for s in SCENARIOS if s["f"] == code]
        parties.append("<tr><td class='c'><b>%s</b></td><td>%s<br><span style='font-size:8pt;color:#666'>%s</span>"
                       "</td><td>%s</td><td></td><td></td><td></td><td></td></tr>"
                       % (e(code), e(nom), e(module), e(", ".join(ids))))
    parties.append("<tr><td></td><td><b>Total</b> (%d scénarios)</td><td></td><td></td><td></td><td></td><td></td>"
                   "</tr></table>" % len(SCENARIOS))
    parties.append("<p style='margin-top:5mm'><span class='case'></span> CONFORME &nbsp;&nbsp; <span class='case'>"
                   "</span> NON CONFORME (au moins un KO : appeler AITE) &nbsp;&nbsp; <span class='case'></span> "
                   "EN COURS</p>")
    parties.append("<table class='ident' style='margin-top:4mm'><tr><td class='l'>Intégrateur (nom, signature)</td>"
                   "<td style='height:14mm'></td></tr><tr><td class='l'>Gérant du restaurant (nom, signature)</td>"
                   "<td style='height:14mm'></td></tr><tr><td class='l'>Date (JJ/MM/AAAA)</td><td></td></tr></table>")
    parties.append("<p class='verifie' style='margin-top:4mm'>Tous les scénarios, sauf ST-15 (https), ont été joués "
                   "le %s sur une base de test (carte Le Messager posée à neuf, imprimantes Epson simulées au "
                   "niveau du réseau). Rien n'a été essayé sur une vraie imprimante Epson ni sur Odoo Enterprise."
                   "</p>" % DATE_VERIFICATION)
    parties.append("</body></html>")
    return "\n".join(parties)


def main():
    xlsx = os.path.join(ICI, NOM + ".xlsx")
    n = construire_xlsx(xlsx)
    print("Classeur :", xlsx, "(%d scénarios)" % n)
    if "--xlsx" in sys.argv:
        return
    source = os.path.join(ICI, "scenarios_test.html")
    with open(source, "w", encoding="utf-8") as f:
        f.write(construire_html())
    try:
        from weasyprint import HTML
    except ImportError:
        print("weasyprint absent : PDF non produit (HTML écrit : %s)" % source)
        return
    pdf = os.path.join(ICI, NOM + ".pdf")
    HTML(source, base_url=ICI).write_pdf(pdf)
    print("PDF :", pdf)


if __name__ == "__main__":
    main()
