# -*- coding: utf-8 -*-
"""Plan de recette AITE HOUSE — PDF signable (WeasyPrint)."""
import base64
import os
from collections import Counter

from cas_de_test import CAS, DOMAINES

DOM_NOM = {c: n for c, n, _ in DOMAINES}
DOM_MOD = {c: m for c, _, m in DOMAINES}
PRIO = {1: ("Critique", "p-r"), 2: ("Majeur", "p-a"), 3: ("Mineur", "p-g")}
cnt = Counter(x[1] for x in CAS)
pcnt = Counter(x[2] for x in CAS)

logo = ""
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("RECETTE_OUT", HERE)
for p in (os.path.join(HERE, "logo_aite.jpg"), "logo_aite.jpg"):
    if os.path.exists(p):
        logo = ('<img src="data:image/jpeg;base64,%s" style="height:12mm"/>'
                % base64.b64encode(open(p, 'rb').read()).decode())
        break

CSS = """
@page { size: A4; margin: 14mm 14mm 16mm;
  @bottom-center { content: "AITE Consulting SARL — Cahier de recette AITE HOUSE — page " counter(page) " / " counter(pages);
    font-family: 'DejaVu Sans'; font-size: 7pt; color: #8A949C; } }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 9.5pt;
  color: #37414A; line-height: 1.45; }
h1 { font-size: 20pt; color: #0A4C5C; margin-bottom: 1mm; }
h2 { font-size: 12.5pt; color: #0F6478; margin: 6mm 0 2.5mm;
  border-bottom: .5mm solid #DFE8EC; padding-bottom: 1.2mm; }
h3 { font-size: 10pt; color: #0A4C5C; margin: 4mm 0 1.5mm; }
p { margin-bottom: 2.2mm; text-align: justify; }
b { color: #0A4C5C; }
.hd { display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1mm solid #0F6478; padding-bottom: 3mm; margin-bottom: 5mm; }
.sub { font-size: 10pt; color: #5A6670; }
.meta { font-size: 8pt; color: #8A949C; margin-top: 1mm; }
table { width: 100%; border-collapse: collapse; font-size: 8.4pt;
  margin: 2.5mm 0; }
th { background: #0A4C5C; color: #fff; text-align: left; padding: 1.6mm 2mm;
  font-size: 7.6pt; text-transform: uppercase; letter-spacing: .3pt; }
td { border-bottom: .25mm solid #E6ECEF; padding: 1.5mm 2mm;
  vertical-align: top; }
tr:nth-child(even) td { background: #F7FAFB; }
td.c, th.c { text-align: center; }
.pill { display: inline-block; border-radius: 2mm; padding: .3mm 1.8mm;
  font-size: 7pt; font-weight: 700; }
.p-r { background: #F6E0DE; color: #C0392B; }
.p-a { background: #F8ECD8; color: #B0761C; }
.p-g { background: #DFF0E6; color: #2E7D4F; }
.p-v { background: #EFE2F2; color: #7A2E86; }
.box { border: .35mm solid #DFE8EC; border-left: 1.4mm solid #0F6478;
  border-radius: 2mm; padding: 3mm 4mm; margin: 3mm 0; background: #F7FAFB; }
.box.v { border-left-color: #7A2E86; }
.krow { display: flex; gap: 3mm; margin: 3mm 0; }
.k { flex: 1; border: .35mm solid #E3E9EC; border-left: 1.3mm solid #0F6478;
  border-radius: 1.6mm; padding: 2mm 2.6mm; }
.k.r { border-left-color: #C0392B; } .k.a { border-left-color: #E6A23C; }
.k.g { border-left-color: #38A169; }
.klbl { font-size: 6pt; font-weight: 700; color: #7C8790;
  letter-spacing: .3pt; }
.kval { font-size: 14pt; font-weight: 800; margin-top: .5mm; }
.ksub { font-size: 6.4pt; color: #7C8790; }
ul { margin: 0 0 2.5mm 5mm; } li { margin-bottom: 1.2mm; }
.sign { display: flex; gap: 6mm; margin-top: 6mm; }
.sig { flex: 1; border: .35mm solid #CBD6DC; border-radius: 2mm;
  padding: 3mm; min-height: 34mm; }
.sig b { display: block; font-size: 9pt; margin-bottom: 1mm; }
.sig span { font-size: 7.4pt; color: #7C8790; }
.page-break { page-break-before: always; }
"""

dom_rows = "".join(
    "<tr><td class='c'><b>%s</b></td><td>%s</td><td>%s</td>"
    "<td class='c'>%d</td></tr>" % (c, n, m, cnt[c])
    for c, n, m in DOMAINES)

cas_rows = ""
cur = None
for cid, dom, prio, pre, scen, etapes, attendu in CAS:
    if dom != cur:
        cur = dom
        cas_rows += ("<tr><td colspan='5' style='background:#0F6478;"
                     "color:#fff;font-weight:800;font-size:8pt;"
                     "padding:1.8mm 2mm'>%s — %s &nbsp;·&nbsp; %s</td></tr>"
                     % (dom, DOM_NOM[dom], DOM_MOD[dom]))
    lbl, cls = PRIO[prio]
    cas_rows += (
        "<tr><td class='c'><b>%s</b></td><td><b>%s</b></td>"
        "<td class='c'><span class='pill %s'>%s</span></td>"
        "<td>%s</td><td>%s</td></tr>"
        % (cid, scen, cls, lbl, etapes.replace("\n", "<br/>"), attendu))

html = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<style>%s</style></head><body>

<div class="hd"><div><h1>Plan et cahier de recette</h1>
<div class="sub">AITE HOUSE — suite de gestion hôtelière sur Odoo 18</div>
<div class="meta">Version de septembre 2026 · 12 modules · %d scénarios de
test</div></div><div>%s</div></div>

<h2>1. Objet du document</h2>
<p>Ce document définit la démarche de recette fonctionnelle de la solution
<b>AITE HOUSE</b> et recense les scénarios de test à dérouler avant la mise
en production. Il est accompagné du classeur
<b>AITE_HOUSE_cahier_de_recette.xlsx</b>, qui sert de support de saisie des
résultats, de journal des anomalies et de tableau de bord d'avancement.</p>
<p>La recette est réalisée par le client, assisté par AITE Consulting, sur
un environnement dédié. Elle se conclut par le procès-verbal figurant en fin
de document.</p>

<div class="krow">
<div class="k"><div class="klbl">SCÉNARIOS</div><div class="kval">%d</div>
<div class="ksub">répartis sur 13 domaines</div></div>
<div class="k r"><div class="klbl">CRITIQUES</div><div class="kval">%d</div>
<div class="ksub">bloquent la mise en production</div></div>
<div class="k a"><div class="klbl">MAJEURS</div><div class="kval">%d</div>
<div class="ksub">à corriger avant démarrage</div></div>
<div class="k g"><div class="klbl">MINEURS</div><div class="kval">%d</div>
<div class="ksub">confort, à planifier</div></div>
</div>

<h2>2. Périmètre testé</h2>
<table><tr><th class="c">Code</th><th>Domaine fonctionnel</th>
<th>Module</th><th class="c">Cas</th></tr>%s</table>

<h2>3. Conditions préalables</h2>
<ul>
<li>Environnement de <b>recette dédié</b>, distinct de la production, avec
une sauvegarde préalable de la base.</li>
<li>Les 12 modules installés selon la procédure du fichier
<b>INSTALLATION.md</b>, dans l'ordre de dépendances indiqué.</li>
<li>Société paramétrée en <b>FCFA</b> (ou GNF), avec les modes de règlement
utilisés : espèces, Mobile Money, carte.</li>
<li>Jeu de données : <b>aite_demo_data</b> pour une recette de démonstration,
ou les données réelles reprises pour une recette client.</li>
<li>Au moins <b>deux profils utilisateurs</b> créés (un profil caisse, un
profil gérant) afin de tester le cloisonnement des droits.</li>
<li>Deux points de vente configurés et au moins deux chambres disponibles.</li>
</ul>

<h2>4. Déroulement et règles de gestion</h2>
<p>Les domaines sont déroulés dans l'ordre <b>A à M</b>, qui suit le parcours
réel de l'établissement : de la réservation d'une chambre jusqu'au pilotage
du gérant. Chaque cas est déclaré dans l'une des situations suivantes :</p>
<table><tr><th>Statut</th><th>Signification</th></tr>
<tr><td><span class="pill p-g">OK</span></td><td>Le résultat obtenu est
conforme au résultat attendu.</td></tr>
<tr><td><span class="pill p-r">KO</span></td><td>Le résultat diffère de
l'attendu — une anomalie est ouverte dans le classeur.</td></tr>
<tr><td><span class="pill p-a">Bloqué</span></td><td>Le cas n'a pas pu être
déroulé (dépendance en échec, environnement indisponible).</td></tr>
<tr><td><span class="pill p-v">Non applicable</span></td><td>La
fonctionnalité n'entre pas dans le périmètre retenu par le client.</td></tr>
</table>
<p>Toute anomalie est consignée dans l'onglet <b>Anomalies</b> avec sa
gravité (bloquante, majeure, mineure, cosmétique), sa date de détection et
son statut de correction. Après correction, le cas concerné est
<b>rejoué intégralement</b>, et les cas voisins du même domaine sont
contrôlés au titre de la non-régression.</p>

<h2>5. Critères de prononcé</h2>
<div class="box"><b>Recette prononcée sans réserve</b> — 100 %% des cas
critiques en OK, aucune anomalie bloquante ouverte, aucune anomalie majeure
non planifiée.</div>
<div class="box"><b>Recette prononcée avec réserves</b> — tous les cas
critiques en OK ; les anomalies majeures et mineures restantes sont listées
en annexe avec une date de correction convenue entre les parties.</div>
<div class="box v"><b>Recette refusée</b> — au moins un cas critique en KO,
ou une anomalie bloquante ouverte. Une nouvelle session de recette est
planifiée après correction.</div>

<div class="page-break"></div>
<h2>6. Scénarios de test détaillés</h2>
<p>Les %d scénarios ci-dessous sont repris à l'identique dans le classeur de
recette, où ils sont complétés par les colonnes de saisie (statut, testeur,
date, anomalie). Les pré-requis de chaque cas figurent dans le classeur.</p>
<table><tr><th class="c">ID</th><th>Scénario</th><th class="c">Priorité</th>
<th>Étapes</th><th>Résultat attendu</th></tr>%s</table>

<div class="page-break"></div>
<h2>7. Procès-verbal de recette</h2>
<p>Le présent procès-verbal est établi à l'issue des tests décrits ci-dessus,
entre le client et AITE Consulting SARL.</p>
<table>
<tr><th>Élément</th><th>Valeur</th></tr>
<tr><td>Client / établissement</td><td>&nbsp;</td></tr>
<tr><td>Solution testée</td><td>AITE HOUSE — 12 modules, Odoo 18</td></tr>
<tr><td>Environnement et base</td><td>&nbsp;</td></tr>
<tr><td>Période de recette</td><td>du &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp; au</td></tr>
<tr><td>Cas déroulés / total</td><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; / %d</td></tr>
<tr><td>Cas en OK · en KO</td><td>&nbsp;</td></tr>
<tr><td>Anomalies ouvertes (bloquantes / majeures / mineures)</td>
<td>&nbsp;</td></tr>
</table>

<h3>Décision</h3>
<table><tr><th class="c">&nbsp;</th><th>Décision</th><th>Observations</th></tr>
<tr><td class="c">☐</td><td><b>Recette prononcée sans réserve</b></td>
<td>&nbsp;</td></tr>
<tr><td class="c">☐</td><td><b>Recette prononcée avec réserves</b></td>
<td>réserves listées en annexe</td></tr>
<tr><td class="c">☐</td><td><b>Recette refusée</b></td>
<td>nouvelle session à planifier</td></tr></table>

<h3>Réserves et engagements de correction</h3>
<div class="box" style="min-height:26mm">&nbsp;</div>

<div class="sign">
<div class="sig"><b>Pour le client</b>
<span>Nom et qualité :</span><br/><br/><span>Date :</span><br/><br/>
<span>Signature et cachet :</span></div>
<div class="sig"><b>Pour AITE Consulting SARL</b>
<span>Nom et qualité :</span><br/><br/><span>Date :</span><br/><br/>
<span>Signature et cachet :</span></div>
</div>

<p style="margin-top:6mm;font-size:7.5pt;color:#8A949C">AITE Consulting SARL
— Douala, Makepe Bloc F · info@aite-consulting.com ·
(+237) 673 373 367 / 656 801 098 · https://aite-consulting.com</p>

</body></html>""" % (CSS, len(CAS), logo, len(CAS), pcnt[1], pcnt[2],
                     pcnt[3], dom_rows, len(CAS), cas_rows, len(CAS))

open('plan_recette.html', 'w', encoding='utf-8').write(html)
import weasyprint
weasyprint.HTML(string=html).write_pdf(
    os.path.join(OUT_DIR, 'AITE_HOUSE_plan_de_recette.pdf'))
print("plan de recette écrit")
