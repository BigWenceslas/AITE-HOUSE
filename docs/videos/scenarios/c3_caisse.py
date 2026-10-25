# -*- coding: utf-8 -*-
"""Chapitre 3 — Ardoises clients et recouvrement.

Source : fiche de recette n° 3 « Ardoises clients et recouvrement » (caisse :
tableau de bord Recouvrement, liste des ardoises, filtre « Ouvertes », fiche,
assistant de remboursement, ardoise réglée, refus d'accès aux réservations).

Libellés relevés dans : aite_pos_credit/static/src/xml/dashboard.xml
(tableau de bord « POS Crédit — Recouvrement » : cartes et sous-titres,
accordés depuis la livraison 4 — « 4 remboursements », « 1 ardoise ouverte »,
« 5 débiteurs actifs », « En retard (+30 j) », écarts n° 41-44),
static/src/js/views/dashboard_view.js (sous-titre de l'encours « flux
période : … », netFlowSub :201-205 ; variations « ▲ +12,1 % vs période
précédente » et, pour les nouvelles ardoises, une baisse en vert :
deltaOf(…, false), :184-199, écart n° 62), static/src/js/services/utils.js
(fmtPct « 19,8 % », fmtDays « 18,0 j », fmtAge « 104 j »),
models/pos_credit_dashboard.py (balance âgée en 4 tranches :287-294 ;
get_evolution, mois abrégés sans l'année « mai » … « oct. » :508-534),
views/pos_credit_views.xml (liste, colonne « Caisse d'origine » :13-18,
fiche, boutons « Enregistrer un remboursement » / « Annuler » réservés à une
ardoise ouverte, « Rouvrir » à une ardoise annulée, :43-54 : une ardoise
réglée n'a plus de bouton d'en-tête ; statusbar Ouverte / Réglée, onglets),
static/src/xml/dashboard.xml:63-75 (rangée « Caisse », une pastille par
caisse),
models/pos_credit.py (Origine « Point de vente », sévérités Récente / En
retard / Critique), wizard/pos_credit_repay_wizard*.py|xml (« Enregistrer un
remboursement », moyens de paiement, bouton « Encaisser »). Menus du profil
Caisse relevés sur une base de recette (load_menus). Le refus reprend le
message d'Odoo 18 et les groupes qui lisent aite.hotel.reservation
(aite_hotel_management/security/ir.model.access.csv).

Données harmonisées avec scenarios/t10_ardoises.py (indicateurs(True), qui
contrôle ces chiffres par assert) : ARD/0024 d'Armand Mvogo, ouverte le
18/08/2026 sur la commande « Bar de la terrasse/0884 », 20 000 FCFA remboursés
en espèces le 01/10 (et non plus le 30/09 : depuis la livraison 4, « Ce mois »
commence le 1er à Douala, écart n° 38, et t10 date ce remboursement du 01/10
pour que les quatre remboursements restent dans la période), réglée le 14/10 à
15:30 en Orange Money (OM261014.1530.A55120). Le tableau de bord et la liste
sont lus le 14/10 avant ce règlement : encours 150 000 FCFA (les cinq ardoises
de demo.py), flux de la période 18 500 − 37 000 = −18 500 FCFA, recouvré
37 000 FCFA en 4 remboursements (01/10, 02/10, 06/10, 10/10), ▲ +12,1 % contre
33 000 FCFA du 17 au 30/09, nouvelles ardoises 18 500 FCFA (1), ▼ 63,0 %
contre 50 000 FCFA, en vert (une baisse est une bonne nouvelle), taux 19,8 %,
101 500 FCFA en retard (67,7 %), 2 ardoises réglées en 18,0 j ; balance âgée
48 500 / 71 500 / 0 / 30 000 FCFA ; évolution sur six mois (nouvelles
ardoises, recouvré) celle de t10 avant les deux opérations du tutoriel ;
comme scenarios/t15_direction.py. Numéro de commande selon la règle des
tickets du bar (caisse ouverte le 04/05, ~8,3 tickets par jour).

Le remboursement validé est tracé (champs suivis et chatter, verrouillés
après validation : aite_pos_credit/models/pos_credit_payment.py:42-84,
ECARTS n° 20). L'écriture comptable n'est passée que si le réglage
« Comptabiliser les remboursements » est coché, décoché par défaut
(models/res_config_settings.py:39-44 et :60-64) : la vidéo ne la promet pas.

« ? » d'aide (form_label.xml:6, hors mode debug) sur la fiche ARD/0024, pour
les cinq champs qui portent un help= : « Origine », « Total commande », « Payé
comptant à la vente » (affichés dès que la commande POS d'origine est
renseignée : views/pos_credit_views.xml:85-88), « Montant initial » et « Âge
(jours) » (models/pos_credit.py:34-42, :55-66, :84-87, :113-116), comme
scenarios/t10_ardoises.py ; aucun dans l'assistant de remboursement. Total
commande 74 500 FCFA − payé comptant 10 000 FCFA = montant initial 64 500 FCFA.
Graisse des libellés (form_controller.scss:589-600) : en gras les champs
modifiables (Client, Date d'ouverture ; en graisse normale une fois
l'ardoise réglée, readonly="state != 'open'", comme t10) ; « Montant initial » en graisse
normale, en lecture seule dès le premier remboursement (readonly="state !=
'open' or payment_count > 0") ; « Caisse d'origine », many2one en lecture
seule sans no_open, s'affiche en lien.
"""

import demo
from ecrans import (MENUS_MUK, NBSP, age, assistant, bouton, cell_puce, champ, compte, cp_fiche, deux_colonnes, e, entree,
                    erreur_acces, fcfa, fenetre, graphe_barres, graphes, groupe, jours, kpi, lien, m_champ, m_champs,
                    mois_abrege, num, onglets, pct, statusbar, table, tdb_entete, tdb_filtres, tdb_section, titre_fiche,
                    toast, vue_fiche, vue_liste, vue_tdb)
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, defiler, etat, fermer, montrer, notifier,
                    ouvrir, pause, saisir, survol, texte, vue)

NOM, ROLE = demo.POSTES['caisse']
MENUS = MENUS_MUK['pos_credit']
VS = 'vs période précédente'        # libellé des variations (dashboard_view.js:194-195)


def aide(html):
    """Le « ? » qu'Odoo 18 pose après le libellé d'un champ qui porte une aide (help= du modèle ; form_label.xml:6) :
    ajouté au libellé d'un ecrans.champ, dont le premier span est le libellé."""
    assert html.startswith('<div class="ch">')
    return html.replace('</span>', '<sup class="c3-aide">?</sup></span>', 1)

def libelle_id(html, ident):
    """Un id sur le libellé d'un ecrans.champ, pour le passer en graisse normale quand le champ devient en lecture
    seule (ardoise réglée : partner_id et date_open, readonly="state != 'open'", pos_credit_views.xml:73-76)."""
    assert html.startswith('<div class="ch"><span class="l gras">')
    return html.replace('<span class="l gras">', '<span class="l gras" id="%s">' % ident, 1)

# ------------------------------------------------------------ Recouvrement --
# Le matin du 14/10, période « Ce mois » (01/10 → 14/10) : les chiffres de t10_ardoises.indicateurs(True).
ENCOURS, RECOUVRE, NOUVELLES, RETARD = 150000, 37000, 18500, 101500
AGING = [48500, 71500, 0, 30000]                       # 0–30 j, 30–60 j, 60–90 j, +90 j (âge au 14/10)
AGING_COLORS = ['#3B6D11', '#854F0B', '#A32D2D', '#5e1b1b']     # utils.js:38
# get_evolution, mai → octobre : nouvelles ardoises (rouge) et recouvré (vert), avant les opérations de t10.
OUVERTES_MOIS = [38000, 44000, 52000, 82500, 107000, NOUVELLES]
RECOUVRE_MOIS = [22000, 41000, 46000, 13000, 33000, RECOUVRE]
assert sum(AGING) == ENCOURS


def flux(n):
    """netFlowSub (dashboard_view.js:201-205) : « flux période : » + « + » d'un flux positif + montant."""
    return 'flux période : %s%s' % ('+' if n > 0 else '', fcfa(n, tdb=True))


def courbes(identifiant, titre, series, etiquettes, legende):
    """Le graphique « Nouvelles ardoises vs Recouvré (6 mois) » : deux courbes (Chart.js, tension 0.3, aire
    légère), révélées de gauche à droite comme ecrans.graphe_courbe ; légende en bas dans l'application."""
    w, h, haut = 760, 210, 120000.0
    traces = ''
    for valeurs, coul in series:
        pts = ['%.1f,%.1f' % (i * w / (len(valeurs) - 1), h - v * h / haut) for i, v in enumerate(valeurs)]
        traces += ('<path d="M0,%d L%s L%d,%d Z" fill="%s" fill-opacity=".10"/>'
                   '<polyline points="%s" fill="none" stroke="%s" stroke-width="3.5"/>'
                   % (h, ' L'.join(pts), w, h, coul, ' '.join(pts), coul))
    grille = ''.join('<line x1="0" x2="%d" y1="%d" y2="%d" stroke="#E5E7EB"/>' % (w, y, y) for y in range(0, h + 1, h // 5))
    leg = ''.join('<span style="display:inline-flex;align-items:center;gap:6px;margin-left:16px"><i style="width:14px;'
                  'height:4px;background:%s;display:inline-block"></i>%s</span>' % (c, e(l)) for l, c in legende)
    return ('<div class="g-carte"><div class="g-titre">%s<span style="float:right;font-size:14px;color:var(--o-texte-3)">'
            '%s</span></div><div class="g-zone"><svg viewBox="0 0 %d %d" preserveAspectRatio="none">%s%s</svg>'
            '<div class="cache-graphe" id="%s"></div></div><div class="g-lab">%s</div></div>'
            % (e(titre), leg, w, h, grille, traces, identifiant, ''.join('<span>%s</span>' % e(x) for x in etiquettes)))


# Les caisses du point de vente et leur pastille (pos_credit_dashboard.py:32-35, comme t10_ardoises.PALETTE).
CAISSES = {'Bar de la terrasse': '#714B67', 'Restaurant': '#185FA5', 'Boutique': '#3B6D11'}


def caisses(html):
    """La rangée « Caisse » (dashboard.xml:63-75) : chaque caisse porte sa pastille de couleur."""
    for nom, coul in CAISSES.items():
        puce_ = '<span class="chip">%s</span>' % e(nom)
        assert html.count(puce_) == 1
        html = html.replace(puce_, '<span class="chip"><i style="display:inline-block;width:10px;height:10px;'
                            'border-radius:50%%;background:%s;margin-right:8px"></i>%s</span>' % (coul, e(nom)))
    return html


RECOUVREMENT = vue_tdb('c3-dash', '<div id="c3-in">%s</div>' % (
    tdb_entete('POS Crédit — Recouvrement', 'Ardoises & remboursements · suivi des dettes clients')
    + caisses(tdb_filtres([('Période', ["Aujourd'hui", 'Cette semaine', 'Ce mois', 'Tout'], 2),
                           ('Origine', ['Toutes', 'Point de vente', 'Ventes'], 0),
                           ('Caisse', ['Toutes les caisses'] + list(CAISSES), 0)]))
    + tdb_section('Encours & recouvrement', [
        kpi('c3-k-enc', 'Encours total (dû)', fcfa(ENCOURS, tdb=True), flux(NOUVELLES - RECOUVRE), 'rouge'),
        kpi('c3-k-rec', 'Recouvré (période)', fcfa(RECOUVRE, tdb=True), compte(4, 'remboursement', 'remboursements'),
            'vert', (12.1, VS)),
        # Nouvelles ardoises : une hausse est mauvaise (deltaOf(…, false)), la baisse s'affiche en vert.
        kpi('c3-k-new', 'Nouvelles ardoises (période)', fcfa(NOUVELLES, tdb=True),
            compte(1, 'ardoise ouverte', 'ardoises ouvertes'), 'ambre', (-63.0, VS, True)),
        kpi('c3-k-taux', 'Taux de recouvrement', pct(RECOUVRE * 100.0 / (ENCOURS + RECOUVRE)),
            'recouvré / (encours + recouvré)', 'violet')])
    + tdb_section('Indicateurs de risque', [
        kpi('c3-k-moy', 'Ardoise moyenne', fcfa(ENCOURS / 5, tdb=True), compte(5, 'débiteur actif', 'débiteurs actifs')),
        kpi('c3-k-anc', 'Plus ancienne dette', age(104), 'Sylvie Mbarga'),
        kpi('c3-k-ret', 'En retard (+30 j)', fcfa(RETARD, tdb=True), pct(RETARD * 100.0 / ENCOURS) + " de l'encours"),
        kpi('c3-k-reg', 'Ardoises réglées (période)', '2', 'délai moyen ' + jours(18))])
    + graphes(graphe_barres('c3-g-age', "Balance âgée (aging) de l'encours",
                            [(round(v * 90.0 / max(AGING)), c) for v, c in zip(AGING, AGING_COLORS)],
                            etiquettes=['0–30 j', '30–60 j', '60–90 j', '+90 j']),
              courbes('c3-g-evo', 'Nouvelles ardoises vs Recouvré (6 mois)',
                      [(OUVERTES_MOIS, '#A32D2D'), (RECOUVRE_MOIS, '#3B6D11')], [mois_abrege(m) for m in range(5, 11)],
                      [('Nouvelles ardoises', '#A32D2D'), ('Recouvré', '#3B6D11')]))
    + '<div style="height:24px"></div>'), initiale=True)

# ---------------------------------------------------------------- Ardoises --
# Colonne « Caisse d'origine » (config_id, optional="show", pos_credit_views.xml:13-18) : la caisse de chaque
# ardoise, celle de t10_ardoises.ARDOISES.
COLS = [('Référence', '130px'), ('Client', '194px'), ('Origine', '156px'), ("Caisse d'origine", '186px'),
        ("Date d'ouv…", '140px'), ('Montant initial', '160px', 'd'), ('Déjà rembour…', '150px', 'd'),
        ('Reste dû', '146px', 'd'), ('Âge (j)', '84px', 'd'), ('Sévérité', '126px'), ('État', '1fr')]
CAISSE_ARD = {'ARD/0042': 'Bar de la terrasse', 'ARD/0039': 'Restaurant', 'ARD/0031': 'Bar de la terrasse',
              'ARD/0024': 'Bar de la terrasse', 'ARD/0017': 'Restaurant'}
LIGNES = []
for i, (ref, cli, date, mt, remb, reste, age, sev, genre) in enumerate(demo.ARDOISES):
    LIGNES.append({'id': 'c3-l%d' % i, 'classe': {'orange': 'retard', 'rouge': 'critique'}.get(genre, ''),
                   'cellules': [ref, cli, cell_puce('Point de vente', 'info'), CAISSE_ARD[ref], date, num(mt), num(remb),
                                num(reste), age, cell_puce(sev, genre), cell_puce('Ouverte', 'clair')]})
ARDOISES = vue_liste('c3-liste', 'Ardoises', COLS, LIGNES, facettes=[('c3-fac', 'Ouvertes')], pager='1-5 / 5',
                     total=['', '', '', '', '', '187 000 FCFA', '37 000 FCFA', '150 000 FCFA', '', '', ''])

# ------------------------------------------------------------------- Fiche --
REMB = table([('Date', '160px'), ('Moyen de paiement', '260px'), ('Réf. transaction', '1fr'), ('Montant', '170px', 'd'),
              ('Encaissé par', '220px'), ('État', '140px')],
             [('c3-r1', ['01/10/2026', 'Espèces', '', '20 000 FCFA', NOM, ('<span><span class="puce vert">Validé</span></span>',)])],
             identifiant='c3-remb')
NOUVEAU_REMB = ('<div class="t-ligne masque" id="c3-r2" style="grid-template-columns:160px 260px 1fr 170px 220px 140px">'
                '<span>14/10/2026</span><span>Orange Money</span><span class="ell">OM261014.1530.A55120</span>'
                '<span class="d">44 500 FCFA</span><span>%s</span><span><span class="puce vert">Validé</span></span></div>'
                % e(NOM))
FEUILLE = (
    titre_fiche('ARD/0024')
    + deux_colonnes(
        groupe('', [libelle_id(champ('Client', 'Armand Mvogo', gras=True), 'c3-l-cli'),
                    libelle_id(champ("Date d'ouverture", '18/08/2026', gras=True), 'c3-l-date'),
                    aide(champ('Origine', '<span class="puce gris">Point de vente</span>', html=True)),
                    champ('Commande POS d\'origine', 'Bar de la terrasse/0884', lien_=True),
                    champ("Caisse d'origine", 'Bar de la terrasse', lien_=True),
                    aide(champ('Total commande', '74 500 FCFA')), aide(champ('Payé comptant à la vente', '10 000 FCFA'))]),
        groupe('', [aide(champ('Montant initial', '64 500 FCFA')),
                    champ('Déjà remboursé', '20 000 FCFA', 'c3-deja'),
                    champ('Reste dû', '44 500 FCFA', 'c3-reste'), aide(champ('Âge (jours)', '57')),
                    champ('Sévérité', 'En retard', 'c3-sev')]))
    + onglets(['Remboursements', 'Note']) + REMB.replace('<div class="t-ajout">', NOUVEAU_REMB + '<div class="t-ajout">'))
FICHE = vue_fiche('c3-fiche', cp_fiche('Ardoises', 'ARD/0024', '4 / 5', stats=[('c3-st', 'billet', 'Remboursements', '1')]),
                  [bouton('c3-b-remb', 'Enregistrer un remboursement', 'primaire'), bouton('c3-b-ann', 'Annuler')],
                  statusbar('c3-sb', ['Ouverte', 'Réglée'], 0), FEUILLE)

ASSISTANT = assistant('c3-as', 'Enregistrer un remboursement', m_champs(
    [m_champ('Ardoise', e('ARD/0024')), m_champ('Client', e('Armand Mvogo')),
     m_champ('Reste dû actuel', e('44 500 FCFA'))],
    [m_champ('Montant à encaisser', entree('c3-mt', '', '44 500 FCFA')), m_champ('Moyen de paiement', entree('c3-moy', '', 'Espèces')),
     m_champ('Réf. transaction', entree('c3-ref', '')), m_champ('Date', e('14/10/2026'))]),
    [('c3-ok', 'Encaisser', 'primaire', None), ('c3-non', 'Annuler', 'gris', None)], haut=150)

REFUS = erreur_acces('c3-refus', 'Réservation hôtelière', 'aite.hotel.reservation',
                     ['Gestion Hôtelière/Gouvernante', 'Gestion Hôtelière/Responsable', 'Gestion Hôtelière/Réception'])

# Les menus de la barre (grille, nom de l'application, puis Recouvrement, Ardoises, Remboursements).
MENU_REC, MENU_ARD = '#app-c3 .o-haut .menu:nth-child(3)', '#app-c3 .o-haut .menu:nth-child(4)'
ECRAN = fenetre('app-c3', 'POS Crédit', MENUS, [RECOUVREMENT, ARDOISES, FICHE], actif='Recouvrement',
                societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#185FA5', calques=ASSISTANT + REFUS)

# Le « ? » d'aide, comme celui de scenarios/t01_reception.py (.t1-aide) ; presentation.py réunit le CSS des chapitres.
CSS = '.c3-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }'

CHAPITRE = {
    'court': 'Caisse',
    'poste': 'Caisse du bar',
    'titre': 'Ardoises clients et recouvrement',
    'personne': (NOM, ROLE),
    'objectif': "Suivre l'encours des clients, ouvrir une ardoise, enregistrer un remboursement et vérifier le solde.",
    'voix': "Troisième chapitre : la caisse du bar. Les clients habitués consomment à crédit sur une ardoise ; "
            "Hervé suit l'encours et encaisse les remboursements.",
    'app': 'app-c3',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 'c3-dash'},
    'etapes': [
        {'titre': 'Le tableau de bord Recouvrement', 'texte': "L'encours, ce qui rentre, et l'âge de la dette.",
         'voix': "Le tableau de bord Recouvrement donne l'encours total, ce qui a été recouvré ce mois, et surtout "
                 "l'âge de la dette : plus une ardoise vieillit, plus le risque d'impayé grandit.",
         'gestes': [compter('#c3-k-enc-v', 0, ENCOURS, d=1.1, apres=' FCFA'),
                    animer('#c3-g-age', {'scaleY': 0}, {'scaleY': 1}, d=1.0, avec=True),
                    animer('#c3-g-evo', {'scaleX': 1}, {'scaleX': 0}, d=1.4, avec=True),
                    anneau('#c3-k-ret', d=1.6, decale=0.4), defiler('#c3-in', -180, d=0.8),
                    anneau('#c3-g-age', d=1.8)]},
        {'titre': 'Les ardoises ouvertes', 'texte': 'Client, reste dû, âge et sévérité, en couleur.',
         'voix': "La liste des ardoises, filtrée sur les ouvertes, montre le reste dû et l'âge de chacune. Les "
                 "couleurs suivent la sévérité : récente, en retard, critique.",
         'gestes': [clic(MENU_ARD, d=0.6), classe(MENU_REC, retirer=['actif']), classe(MENU_ARD, ajouter=['actif']),
                    vue('c3-liste'), pause(0.4),
                    anneau('#c3-fac', d=1.0), anneau('#c3-l2 .puce.orange', d=1.0), anneau('#c3-l4 .puce.rouge', d=1.2),
                    survol('#c3-l3')]},
        {'titre': "Ouvrir l'ardoise", 'texte': 'Le reste dû, et le bouton pour encaisser.',
         'voix': "L'ardoise d'Armand Mvogo : soixante-quatre mille cinq cents francs au départ, vingt mille déjà "
                 "remboursés, quarante-quatre mille cinq cents encore dus.",
         'gestes': [clic('#c3-l3', fx=0.2), vue('c3-fiche'), pause(0.6), anneau('#c3-reste', d=1.4),
                    anneau('#c3-b-remb', d=1.2)]},
        {'titre': 'Enregistrer un remboursement', 'texte': 'Montant pré-rempli, moyen de paiement, référence.',
         'voix': "L'assistant pré-remplit le reste dû. Le client paie en Orange Moni : Hervé choisit le moyen de "
                 "paiement, saisit la référence de la transaction, et encaisse.",
         'gestes': [clic('#c3-b-remb'), ouvrir('c3-as'), anneau('#c3-mt', d=1.0), choisir('c3-moy', 'Orange Money'),
                    saisir('c3-ref', 'OM261014.1530.A55120'), clic('#c3-ok'), fermer('c3-as')]},
        {'titre': "L'ardoise est réglée", 'texte': 'Reste dû à zéro, ardoise Réglée, remboursement tracé.',
         'voix': "Le reste dû tombe à zéro et l'ardoise passe Réglée. Le remboursement est tracé avec son moyen de "
                 "paiement, la personne qui l'a encaissé et sa référence.",
         'gestes': [texte('#c3-reste', '0 FCFA'), texte('#c3-deja', '64 500 FCFA'), texte('#c3-sev', 'Réglée'),
                    classe('#c3-sb-0', retirer=['actif']), classe('#c3-sb-1', ajouter=['actif']),
                    # Réglée : plus aucun bouton d'en-tête (« Rouvrir » n'existe que pour une ardoise annulée).
                    cacher('#c3-fiche-ga', d=0.2), texte('#c3-st-v', '2'),
                    # Réglée : Client et Date d'ouverture passent en lecture seule, libellés en graisse normale (t10).
                    classe('#c3-l-cli', retirer=['gras'], avec=True), classe('#c3-l-date', retirer=['gras'], avec=True),
                    montrer('#c3-r2', d=0.4), anneau('#c3-sb', d=1.2),
                    # la feuille, plus longue de deux lignes (Total commande, Payé comptant), remonte pour que
                    # l'anneau de la nouvelle ligne reste dans la fenêtre
                    defiler('#c3-fiche-defil', -100, d=0.6, avec=True), anneau('#c3-r2', d=1.6)]},
        {'titre': "Hors de son périmètre", 'texte': 'La caisse n\'ouvre pas les réservations de l\'hôtel.',
         'voix': "La caisse n'a pas de droits sur l'hôtel. Si Hervé tente d'ouvrir une réservation, Odoo refuse "
                 "et nomme les profils autorisés.",
         'gestes': [ouvrir('c3-refus'), pause(0.6), anneau('#c3-refus .refus', d=2.0), clic('#c3-refus-ok'),
                    fermer('c3-refus')]},
    ],
}
