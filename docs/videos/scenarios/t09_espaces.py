# -*- coding: utf-8 -*-
"""Tutoriel 9 — Espaces & Prestations : un seul planning, sans double réservation.

La réceptionniste (Mireille Ateba, demo.POSTES) ouvre le tableau de bord
Espaces & Prestations : salons VIP / VVIP, cabines SPA, fauteuils de coiffure
et comptoir pressing sur un seul planning. Elle réserve un massage pour une
cliente en séjour (la fin et le montant se calculent seuls), le confirme (le
créneau est bloqué, l'e-mail part), voit refuser un salon déjà réservé, passe
le soin en « Réalisée » (report automatique au folio du séjour), rend un dépôt
pressing (« Marquer retiré ») et retrouve le bilan du soir sur le tableau de
bord.

Profil rejoué : Réception (aite_hotel_management.group_hotel_user), comme le
compte demo.reception de la base MuK. Menus de la barre : ceux de la
réception (capture de demo.reception, base aite_muk, et scenarios/
t03_folio.py) ; applications : ecrans.APPS_PROFIL['reception']. Le menu
« Espaces & Prestations » n'offre à la réception que « Tableau de bord » et
« Réservations » : « Configuration » est réservé au Responsable
(addons/aite_slot_booking/views/slot_menus.xml:4-38) ; la réception lit les
ressources et prestations, crée et modifie les réservations
(security/ir.model.access.csv:2-7).

Sources des libellés et des règles (addons/aite_slot_booking, relevés mot pour
mot) :

- Tableau de bord : static/src/xml/dashboard.xml:21-27 (« Espaces &
  Prestations », « Planning des créneaux · SPA, coiffure, pressing, espaces
  VIP / VVIP », « + Nouvelle réservation »), :30-68 (lignes « Jour » ‹ date ›
  « Aujourd'hui », « Période stats », « Famille » « Toutes », « Ressource »
  « Toutes », affichée s'il y a plus d'une ressource), :78-96 (« Activité de la
  période », cartes « CA prestations réalisées » / « N réalisée(s) », « Taux de
  remplissage » / « x h réservées / y h ouvrées », « No-show » / « N
  rendez-vous manqué(s) », « Retraits pressing en attente » / « N
  réservation(s) à venir »), :99-127 (« Planning du » + jour ISO, un couloir
  par ressource, bloc au nom du client, « x/y créneaux libres »), :131-141
  (« Répartition & remplissage », « CA réalisé par famille (période) »,
  « Remplissage par ressource ») ; static/src/js/services/utils.js:5-53
  (couleurs, libellés d'état, formats montant « 38 000 FCFA », pourcentage
  « 14,2 % », heures « 15,5 h », périodes « Aujourd'hui », « Cette semaine »,
  « Ce mois ») ; static/src/js/views/slot_dashboard_view.js:194-231
  (position des blocs, graduations toutes les 2 h, créneaux libres = créneaux
  entièrement vides), :260-316 (anneau légende à droite, barres horizontales
  graduées 0–100 %) ; static/src/scss/slot_dashboard.scss:154-161 et :190-196
  (titres et libellés en majuscules), :378-396 (couloirs, bloc bleu #185FA5
  confirmé, vert #0F6E56 réalisé, texte « créneaux libres » vert) ;
  models/slot_dashboard.py:22-25 (pastilles de famille : #714B67, #0F6E56,
  #185FA5, #854F0B, #888780), :123-176 (CA = réalisées, remplissage =
  heures confirmées + réalisées ÷ amplitude × capacité, no-show, retraits
  pressing toutes périodes confondues), :206-246 (anneau et barres) ;
  models/booking_resource.py:9-15 (cinq familles), :106-142 (grille de
  créneaux). Les chiffres du tableau de bord sont CALCULÉS dans ce fichier
  par les mêmes formules, à partir des réservations rejouées (RESAS).
- Fiche de réservation : views/booking_booking_views.xml:36-93 (boutons
  « Confirmer », « Réalisée », « Renvoyer l'e-mail », « Reporter au folio »,
  « Marquer retiré », « No-show », « Annuler » et leurs conditions ; barre
  d'état « Brouillon / Confirmée / Réalisée » ; champs Client, Téléphone,
  Ressource, Prestation, Quantité (pressing seulement), Origine | Début, Fin,
  Durée (h) (float_time), Montant, Prix manuel ; groupes « Pressing »
  (Retrait prévu, Retiré) et « Séjour (note de chambre) » (Folio du séjour,
  Ligne de folio) ; « Note interne… ») ; models/booking_booking.py:36-119
  (libellés, aides « ? », « Nouveau », origine « Comptoir »), :62-67 (seules
  les prestations de la famille de la ressource sont proposées), :125-138
  (prix : manuel > prestation × quantité > heures × tarif horaire),
  :205-209 (la prestation et le début remplissent la fin), :260-282 (conflit :
  « Conflit : « … » est complète sur ce créneau (capacité 1). », contrôlé au
  passage en Confirmée), :300-307 (Confirmer envoie l'e-mail si le réglage
  est actif), :333-345 (Réalisée reporte au folio ouvert unique du client,
  réglage actif par défaut), :370-373 (Marquer retiré), :379-426 (ligne de
  folio « <prestation> — <référence> », une seule fois), :432-450 (no-show
  automatique après le délai de grâce) ; data/slot_sequence_data.xml:6-7
  (RES/26/0158) ; data/mail_template_data.xml:3-33 (objet « <société> —
  Confirmation <réf.> », « Bonjour …, », « Votre réservation est confirmée : »,
  Référence, Ressource, Prestation, Début dd/MM/yyyy HH:mm, Fin HH:mm, Montant,
  « À très bientôt, ») ; data/ir_cron_data.xml:3-11 (tâche toutes les heures) ;
  models/res_config_settings.py:20-35 (6 heures, report au folio et e-mail
  actifs par défaut) ; views/booking_booking_views.xml:3-30 et :111-153
  (liste « Réservations de créneaux » : colonnes, couleurs, badge d'état,
  somme du Montant, filtre « Aujourd'hui » par défaut).
- Odoo 18 (../odoo18) : addons/web/static/src/core/errors/error_dialogs.xml:4-12
  et i18n/fr.po (« Erreur de validation », « Fermer ») ; addons/mail/i18n/fr.po
  (« %s créé ») ; addons/web/static/src/views/fields/badge/badge_field.js:26-38
  (badge gris d'un brouillon) ; list_renderer.js (somme avec la devise).
- Fenêtre MuK, fiche et discussion : captures prises en lecture seule sur la
  base aite_muk avec demo.reception (fiche RES/26/0286 pressing, RES/26/0282
  salon, RES/26/0324 no-show : « Envoyer message », « Note », « Suivre »,
  suivi « Confirmée → No-show (État) » ; liste groupée par état ; menu
  déroulant « Tableau de bord » / « Réservations ») ; ref_muk/049 à 052.

Douleurs de l'accroche : recette/cas_de_test.py B03 (priorité 1 « Empêcher la
double réservation d'un créneau ») et docs/guides/AITE_HOUSE_plaquette_
commerciale.pdf p.8 (« Le planning des ressources évite les doubles
réservations ») ; B04 (« Rattacher une prestation au folio d'une chambre ») et
docs/guides/AITE_Guide_Espaces_Prestations.pdf §3.4 ; guide §3.2 (« sinon le
robot de nuit le fera après le délai de grâce ») et booking_booking.py:268-277
(une réservation confirmée compte dans le conflit tant qu'elle n'est pas en
no-show) ; guide §3.3 (« le tableau de bord compte les dépôts en attente de
retrait ») ; guide §4 (« pour voir ce qui tourne et ce qui dort ») et B07.

Résultats : 5 familles (booking_resource.py:9-15) ; 3 automatismes actifs dès
l'installation (res_config_settings.py:20-35) ; 69 tests Odoo du module
(tests/test_booking.py 35, test_grid.py 20, test_folio_posting.py 14 ;
docs/GUIDE_TESTS.md:30).

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, Estelle
Ngono chambre 204, FOL/2026/0214, +237 677 41 28 90, estelle.ngono@exemple.cm ;
Martin Ebode en séjour, FOL/2026/0209 comme au tutoriel 3 ; Patrick Nkoulou,
Brigitte Essomba ; réceptionniste Mireille Ateba). Les autres noms (Paul
Essomba, Famille Ndjock, Linda Ewané, Rachel Bilong, Yves Tchana, Boris Kamga,
Carine Mbappé) sont ceux, fictifs, du chapitre 6 (scenarios/c6_direction.py).
Ressources, catalogue et tarifs sont fictifs (salons Wouri, Sanaga, Bonabéri
comme au chapitre 6). La journée rejouée est le jeudi 15/10/2026.

Écarts relevés, rejoués tels quels (voir le rapport) :
1. « Planning du 2026-10-15 » : date ISO (dashboard.xml:99), contre la règle
   des dates %d/%m/%Y (déjà ECARTS.md n° 3).
2. « No-show » en anglais : état, bouton, carte, filtre (booking_booking.py:93,
   booking_booking_views.xml:50,124, dashboard.xml:89).
3. « Conflit : « Salon VIP Wouri » est complète… » : message au féminin pour
   toute ressource (booking_booking.py:279-282).
4. Message de création d'Odoo « Réservation de créneau (espace / prestation)
   créé » : accord masculin de la traduction standard (mail/i18n/fr.po).
5. Les réservations de créneau (RES/26/0158) et d'hôtel (RES/2026/0214)
   partagent le préfixe « RES/ » (slot_sequence_data.xml:6).
"""

import demo
from ecrans import APPS_PROFIL, ICONES, e, entree, fenetre_muk, graphe_anneau, navigateur, vue_libre, vue_tdb
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, choisir, clic, classe, defiler, fermer, montrer, ouvrir, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['reception']
JOUR = '15/10/2026'
JOUR_ISO = '2026-10-15'
CLIENT, TEL = demo.CLIENT, demo.CLIENT_TEL
MENUS = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
         'Fidélité', 'Gouvernante']
PARENT_TDB = 'Espaces & Prestations — Tableau de bord'
PARENT_LISTE = 'Réservations de créneaux'
CREE = 'Réservation de créneau (espace / prestation) créé'


def _id(ident):
    return ' id="%s"' % ident if ident else ''


def ico(svg, classe_='ico'):
    return '<span class="%s">%s</span>' % (classe_, svg)


def fcfa(montant):
    return '{:,}'.format(int(round(montant))).replace(',', ' ') + ' FCFA'


def virgule(x):
    """Un nombre à une décimale, virgule française, sans « ,0 » (utils.js:30-40)."""
    r = int(x * 10 + 0.5) / 10.0
    return ('%g' % r).replace('.', ',')


# ------------------------------------------------------------- icônes --
# Redessinées ici (fa-cog, cloud, undo, fa-calendar, fa-list…) : ecrans.ICONES
# n'a pas ces glyphes, on ne le modifie pas.
ROUAGE = ('<svg viewBox="0 0 24 24" fill="#495057"><path d="M10.3 2h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 1.9 '
          '2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 1.5-2.2-.8-1.9'
          'L2 13.7v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8z"/><circle cx="12" cy="12" r="3.4" fill="#fff"/></svg>')
NUAGE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round"><path d="M7 18h10.5a4 4 0 00.6-7.95A6 6 0 006.3 9.2 4.5 4.5 0 007 18z"/>'
         '<path d="M12 16v-6M9.5 12.5L12 10l2.5 2.5"/></svg>')
DEFAIRE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
           'stroke-linejoin="round"><path d="M9 7H4V2"/><path d="M4.5 7A8 8 0 1112 20"/></svg>')
CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" '
       'height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>')
LISTE_I = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="5" width="18" height="2.4"/><rect x="3" y="10.8" '
           'width="18" height="2.4"/><rect x="3" y="16.6" width="18" height="2.4"/></svg>')
ENVELOPPE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2.5 5h19v14h-19z" opacity=".001"/><path d="M3 5.5h18v1.2'
             'l-9 6-9-6zM3 8.6l9 6 9-6V18.5H3z"/></svg>')
NOTE_I = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 3h16v12l-6 6H4z"/><path d="M14 21v-6h6" fill="#fff" '
          'opacity=".5"/></svg>')
FLECHE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
          'stroke-linejoin="round"><path d="M4 12h15M14 7l5 5-5 5"/></svg>')

# -------------------------------------------------- les ressources --
FAMILLES = [('space', 'Espace VIP / VVIP', '#714B67'), ('spa', 'SPA', '#0F6E56'), ('hair', 'Coiffure', '#185FA5'),
            ('pressing', 'Pressing', '#854F0B'), ('other', 'Autre', '#888780')]
LIB_FAMILLE = dict((k, l) for k, l, _ in FAMILLES)
COUL_FAMILLE = dict((k, c) for k, _, c in FAMILLES)
# (clé, nom, famille, couleur, ouverture, fermeture, pas en minutes, capacité, tarif horaire)
RESSOURCES = [
    ('wouri', 'Salon VIP Wouri', 'space', '#714B67', 9, 23, 60, 1, 15000),
    ('sanaga', 'Salon VIP Sanaga', 'space', '#714B67', 9, 23, 60, 1, 15000),
    ('bonaberi', 'Salon VVIP Bonabéri', 'space', '#714B67', 10, 23, 60, 1, 25000),
    ('spa1', 'Cabine SPA 1', 'spa', '#0F6E56', 9, 21, 30, 1, 0),
    ('spa2', 'Cabine SPA 2', 'spa', '#0F6E56', 9, 21, 30, 1, 0),
    ('fh1', 'Fauteuil homme 1', 'hair', '#185FA5', 9, 20, 30, 1, 0),
    ('ff1', 'Fauteuil femme 1', 'hair', '#185FA5', 9, 20, 30, 1, 0),
    ('pressing', 'Comptoir pressing', 'pressing', '#854F0B', 8, 19, 30, 2, 0),
]
RES = dict((r[0], r) for r in RESSOURCES)

# Les réservations du jeudi 15/10/2026 : (n°, client, ressource, prestation,
# début, fin, montant, état à 11 h, à 16 h, le soir). « done » réalisée,
# « confirmed » confirmée, « draft » brouillon, None : pas encore créée.
RESAS = [
    ('0141', 'Martin Ebode', 'pressing', 'Chemise', 8.5, 9.0, 4800, 'done', 'done', 'done'),
    ('0138', 'Yves Tchana', 'fh1', 'Coupe homme', 9.0, 9.5, 6200, 'done', 'done', 'done'),
    ('0145', 'Linda Ewané', 'spa1', 'Massage relaxant 60 min', 10.0, 11.0, 27000, 'done', 'done', 'done'),
    ('0142', 'Carine Mbappé', 'ff1', 'Tresses (forfait 2 h)', 10.0, 12.0, 19000, 'confirmed', 'done', 'done'),
    ('0133', 'Paul Essomba', 'sanaga', '', 11.0, 14.0, 45000, 'confirmed', 'done', 'done'),
    ('0150', 'Rachel Bilong', 'spa2', 'Soin du visage éclat', 14.0, 15.0, 23000, 'confirmed', 'done', 'done'),
    ('0158', CLIENT, 'spa1', 'Massage relaxant 60 min', 15.0, 16.0, 27000, None, 'confirmed', 'done'),
    ('0153', 'Boris Kamga', 'fh1', 'Coupe homme', 17.0, 17.5, 6200, 'confirmed', 'confirmed', 'confirmed'),
    ('0127', 'Patrick Nkoulou', 'wouri', '', 19.0, 22.0, 45000, 'confirmed', 'confirmed', 'confirmed'),
    ('0119', 'Famille Ndjock', 'bonaberi', '', 19.0, 23.0, 100000, 'confirmed', 'confirmed', 'confirmed'),
    ('0159', 'Brigitte Essomba', 'wouri', '', 20.0, 23.0, 45000, None, 'draft', 'draft'),
]
MATIN, APREM, SOIR = 7, 8, 9
RETRAITS = {MATIN: 3, SOIR: 2}      # dépôts pressing non retirés, toutes périodes (celui de Martin compris le matin)


def hhmm(h):
    return '%02d:%02d' % (int(h), int(round((h - int(h)) * 60)))


def actives(moment):
    return [r for r in RESAS if r[moment] in ('confirmed', 'done')]


def creneaux_libres(cle, moment):
    """La grille de booking_resource.py:106-142 : un créneau n'est libre que s'il est vide."""
    _, _, _, _, ouv, ferm, pas, cap, _ = RES[cle]
    occupe = [(r[4], r[5]) for r in actives(moment) if r[2] == cle]
    step = pas / 60.0
    h, libres, total = float(ouv), 0, 0
    while h + step <= ferm + 1e-6:
        used = sum(1 for s, f in occupe if s < h + step and f > h)
        total += 1
        libres += 1 if used == 0 else 0
        h += step
    return libres, total


def indicateurs(moment):
    """Les cartes « Activité de la période » (slot_dashboard.py:123-176), période « Aujourd'hui »."""
    faites = [r for r in RESAS if r[moment] == 'done']
    confirmees = [r for r in RESAS if r[moment] == 'confirmed']
    heures = sum(r[5] - r[4] for r in faites + confirmees)
    ouvrees = sum((r[5] - r[4]) * r[7] for r in RESSOURCES)
    return {'ca': fcfa(sum(r[6] for r in faites)), 'faites': len(faites), 'confirmees': len(confirmees),
            'remp': virgule(min(100.0, heures / ouvrees * 100)) + ' %',
            'heures': '%s h réservées / %s h ouvrées' % (virgule(heures), virgule(ouvrees)),
            'retraits': RETRAITS[moment]}


def melange(moment):
    """CA réalisé par famille, du plus grand au plus petit (slot_dashboard.py:206-222)."""
    agg = {}
    for r in RESAS:
        if r[moment] == 'done':
            k = RES[r[2]][2]
            agg[k] = agg.get(k, 0) + r[6]
    return sorted(agg.items(), key=lambda kv: -kv[1])


def remplissage(moment):
    """Remplissage par ressource, trié (slot_dashboard.py:224-246)."""
    out = []
    for cle, nom, _, coul, ouv, ferm, _, cap, _ in RESSOURCES:
        h = sum(r[5] - r[4] for r in actives(moment) if r[2] == cle)
        out.append((nom, coul, min(100.0, h / ((ferm - ouv) * cap) * 100)))
    return sorted(out, key=lambda x: -x[2])


# ------------------------------------------------- le tableau de bord --
def puce_fam(couleur):
    return '<i class="t09-pt" style="background:%s"></i>' % couleur


def tableau_de_bord(k, moment, initiale=False):
    p = 't09-d%d' % k
    ind = indicateurs(moment)
    periode = ''.join('<span class="chip%s">%s</span>' % (' actif' if i == 0 else '', e(x))
                      for i, x in enumerate(["Aujourd'hui", 'Cette semaine', 'Ce mois']))
    familles = ''.join('<span class="chip">%s%s</span>' % (puce_fam(c), e(l)) for _, l, c in FAMILLES)
    ressources = ''.join('<span class="chip">%s%s</span>' % (puce_fam(r[3]), e(r[1])) for r in RESSOURCES)
    filtres = ('<div class="tdb-filtres t09-filtres">'
               '<div class="tdb-rang"><span class="tdb-lib">Jour</span><span class="chip t09-fl">‹</span>'
               '<span class="t09-date">%s%s</span><span class="chip t09-fl">›</span><span class="chip">Aujourd\'hui</span>'
               '<span class="t09-esp"></span><span class="tdb-lib t09-lib2">Période stats</span>%s</div>'
               '<div class="tdb-rang"><span class="tdb-lib">Famille</span><span class="chip actif">Toutes</span>%s</div>'
               '<div class="tdb-rang t09-rang-r"><span class="tdb-lib">Ressource</span><span class="chip actif">Toutes</span>'
               '%s</div></div>' % (JOUR, ico(CAL, 't09-cal'), periode, familles, ressources))
    tete = ('<div class="tdb-tete"><div><div class="tdb-titre">Espaces &amp; Prestations</div><div class="tdb-sous">'
            'Planning des créneaux · SPA, coiffure, pressing, espaces VIP / VVIP</div></div>'
            '<span class="bt primaire t09-nouv" id="%s-nouv">+ Nouvelle réservation</span></div>' % p)
    kpis = ('<div class="tdb-grille c4" id="%s-kpis">%s%s%s%s</div>' % (
        p,
        kpi(p + '-ca', 'CA prestations réalisées', ind['ca'], '%d réalisée(s)' % ind['faites'], 'violet'),
        kpi(p + '-remp', 'Taux de remplissage', ind['remp'], ind['heures'], 'bleu'),
        kpi(p + '-ns', 'No-show', '0 %', '0 rendez-vous manqué(s)', 'rouge'),
        kpi(p + '-pr', 'Retraits pressing en attente', str(ind['retraits']),
            '%d réservation(s) à venir' % ind['confirmees'], 'ambre')))
    couloirs = ''.join(couloir(p, i, r, moment) for i, r in enumerate(RESSOURCES))
    parts = [(LIB_FAMILLE[k_], v, COUL_FAMILLE[k_]) for k_, v in melange(moment)]
    graphes = ('<div class="tdb-grille c2 t09-gr">%s%s</div>' % (
        graphe_anneau(p + '-mix', 'CA réalisé par famille (période)', parts), barres(p + '-remp-g', moment)))
    contenu = (tete + filtres + '<div class="tdb-sect">Activité de la période</div>' + kpis
               + '<div class="tdb-sect">Planning du %s</div>' % JOUR_ISO
               + '<div class="t09-pl" id="%s-pl">%s</div>' % (p, couloirs)
               + '<div class="tdb-sect">Répartition &amp; remplissage</div>' + graphes)
    return vue_tdb('t09-tdb%d' % k, '<div class="t09" data-layout-allow-overflow id="t09-in%d">%s</div>' % (k, contenu),
                   initiale=initiale)


def kpi(ident, libelle, valeur, sous, accent):
    return ('<div class="kpi acc-%s" id="%s"><div class="kpi-l">%s</div><div class="kpi-v" id="%s-v">%s</div>'
            '<div class="kpi-s" id="%s-s">%s</div></div>' % (accent, ident, e(libelle), ident, e(valeur), ident, e(sous)))


def couloir(p, i, ressource, moment):
    cle, nom, _, coul, ouv, ferm, _, _, _ = ressource
    span = float(ferm - ouv)
    traits = ''.join('<i class="t09-tick" style="left:%.2f%%"></i>' % ((h - ouv) / span * 100)
                     for h in range(ouv, ferm + 1, 2))
    blocs = ''.join('<span class="t09-bloc %s" id="%s-b%s" style="left:%.2f%%;width:%.2f%%">%s</span>'
                    % ('ok' if r[moment] == 'done' else 'conf', p, r[0], (r[4] - ouv) / span * 100,
                       (r[5] - r[4]) / span * 100, e(r[1]))
                    for r in actives(moment) if r[2] == cle)
    libres, total = creneaux_libres(cle, moment)
    return ('<div class="t09-lane" id="%s-l%d"><span class="t09-ln">%s<span class="ell">%s</span></span>'
            '<div class="t09-track" id="%s-t%d">%s%s</div><span class="t09-libre" id="%s-x%d">%d/%d créneaux libres</span>'
            '</div>' % (p, i, puce_fam(coul), e(nom), p, i, traits, blocs, p, i, libres, total))


def barres(ident, moment):
    """Remplissage par ressource : barres horizontales (Chart.js, indexAxis 'y'), axe 0–100 %."""
    lignes = ''.join('<div class="t09-hb"><span class="l">%s</span><span class="p"><i style="width:%.1f%%;background:%s">'
                     '</i></span></div>' % (e(nom), max(v, 0.6), coul) for nom, coul, v in remplissage(moment))
    axe = ''.join('<span style="left:%d%%">%d %%</span>' % (v, v) for v in range(0, 101, 20))
    return ('<div class="g-carte t09-gb" id="%s"><div class="g-titre">Remplissage par ressource</div>'
            '<div class="t09-hbs">%s</div><div class="t09-hax"><span></span><span class="p">%s</span></div></div>'
            % (ident, lignes, axe))


TDB1 = tableau_de_bord(1, MATIN, initiale=True)
TDB2 = tableau_de_bord(2, SOIR)


# --------------------------------------------------------------- la fiche --
def ch(libelle, valeur_html, ident=None, saisie=True, aide=False, lien=False):
    """Un champ de fiche Odoo 18 : libellé foncé s'il se modifie, valeur soulignée."""
    return ('<div class="t09-ch"%s><span class="l%s">%s%s</span><span class="v%s%s">%s</span></div>'
            % (_id(ident), ' gras' if saisie else '', e(libelle), '<sup class="t09-aide">?</sup>' if aide else '',
               ' saisie' if saisie else '', ' lien' if lien else '', valeur_html))


def champ(ident, valeur='', placeholder=''):
    """Une valeur qui se saisit ou se remplit (geste saisir / choisir / texte sur ``<ident>-val``)."""
    return entree(ident, placeholder, valeur, classe='t09-in')


def bt(ident, libelle, style='gris', svg=None):
    return '<span class="bt %s"%s>%s%s</span>' % (style, _id(ident), ico(svg) if svg else '', e(libelle))


def case(ident, cochee=False):
    return '<span class="case%s"%s><i></i></span>' % (' coche' if cochee else '', _id(ident))


def message(auteur, quand, corps, ident=None, suite=False):
    """Un message de la discussion ; ``suite`` : regroupé sous le précédent (même auteur)."""
    if suite:
        return '<div class="t09-msg suite"%s><span></span><div class="t09-msg-t">%s</div></div>' % (_id(ident), corps)
    return ('<div class="t09-msg"%s><span class="t09-av">%s</span><div><div class="t09-msg-a"><b>%s</b> <small>%s</small>'
            '</div><div class="t09-msg-t">%s</div></div></div>' % (_id(ident), e(auteur[0]), e(auteur), e(quand), corps))


def suivi(avant, apres, champ_='État'):
    return ('<span class="t09-suivi">• <span class="anc">%s</span><span class="sep">%s</span><span class="nouv">%s</span> '
            '<i>(%s)</i></span>' % (e(avant), ico(FLECHE, 't09-fl-i'), e(apres), e(champ_)))


def separateur(texte_):
    return '<div class="t09-sep"><span>%s</span></div>' % e(texte_)


def discussion(p, etats):
    """La discussion à droite (thème MuK) : « Envoyer message », « Note », « Suivre » ;
    le modèle n'hérite pas des activités (booking_booking.py:33). ``etats`` :
    ses contenus successifs, superposés (``<p>-ch<n>``)."""
    piles = ''.join('<div class="t09-ch-etat%s" id="%s-ch%d">%s</div>' % ('' if i == 0 else ' masque', p, i, h)
                    for i, h in enumerate(etats))
    return ('<div class="t09-chatter"><div class="t09-ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
            '<span class="bt gris">%sNote</span><span class="t09-ch-ic">%s</span><span class="t09-suivre">Suivre</span>'
            '</div><div class="t09-ch-fil">%s</div></div>'
            % (ico(ENVELOPPE, 't09-bi'), ico(NOTE_I, 't09-bi'), ICONES['loupe'], piles))


def fiche(p, parent, ref, pager, groupes, sb, gauche, droite, bas, etats_discussion, sale=False):
    """Une réservation de créneau : panneau, boutons et barre d'état, feuille, discussion.

    ``groupes`` : les bandes de boutons successives, superposées (``<p>-g<n>``) ;
    ``sb`` : (états visibles, index actif) ; ``sale`` : les icônes d'enregistrement
    d'une fiche modifiée (nuage, annuler)."""
    save = ('<span class="t09-save masque" id="%s-save"><span class="t09-si">%s</span><span class="t09-si">%s</span></span>'
            % (p, NUAGE, DEFAIRE)) if sale else ''
    cp = ('<div class="t09-f-cp"><span class="bt contour" id="%s-nv">Nouveau</span><div class="t09-fil">'
          '<span class="t09-parent" id="%s-par">%s</span><span class="t09-ref"><span id="%s-ref">%s</span>'
          '<span class="t09-rouage">%s</span>%s</span></div><span class="t09-pager" id="%s-pg">%s</span></div>'
          % (p, p, e(parent), p, e(ref), ROUAGE, save, p, e(pager)))
    bandes = ''.join('<div class="t09-bg%s" id="%s-g%d">%s</div>' % ('' if i == 0 else ' masque', p, i, ''.join(g))
                     for i, g in enumerate(groupes))
    etats, actif = sb
    barre = ''.join('<span class="t09-sb-e%s" id="%s-sb%d">%s</span>' % (' actif' if i == actif else '', p, i, e(x))
                    for i, x in enumerate(etats))
    hd = '<div class="t09-hd"><div class="t09-bts">%s</div><div class="t09-sb" id="%s-sb">%s</div></div>' % (
        bandes, p, barre)
    feuille = ('<div class="t09-feuille" id="%s-feuille"><div class="t09-f-titre" id="%s-titre">%s</div>'
               '<div class="t09-cols"><div id="%s-gauche">%s</div><div id="%s-droite">%s</div></div>%s'
               '<div class="t09-noteint">Note interne…</div></div>' % (p, p, e(ref), p, gauche, p, droite, bas))
    return vue_libre(p, '<div class="t09-f">%s<div class="t09-f-g">%s%s</div>%s</div>'
                     % (cp, hd, feuille, discussion(p, etats_discussion)))


def groupe_sejour(p, folio='', ligne_=''):
    return ('<div class="t09-grp" id="%s-sejour"><div class="t09-grp-t">Séjour (note de chambre)</div>%s%s</div>'
            % (p, ch('Folio du séjour', champ(p + '-folio', folio), aide=True),
               ch('Ligne de folio', '<span class="t09-lien" id="%s-ligne">%s</span>' % (p, e(ligne_)), saisie=False,
                  aide=True)))


SB = ['Brouillon', 'Confirmée', 'Réalisée']
CONFIRMEE = [bt('t09-spa-b-done', 'Réalisée', 'primaire'), bt(None, "Renvoyer l'e-mail"), bt(None, 'No-show'),
             bt(None, 'Annuler')]

# La réservation d'Estelle Ngono : créée depuis le tableau de bord, confirmée,
# puis rouverte depuis la liste et passée en Réalisée.
SPA = fiche(
    't09-spa', PARENT_TDB, 'Nouveau', '',
    [[bt('t09-spa-b-conf', 'Confirmer', 'primaire'), bt(None, 'Annuler')], CONFIRMEE, []],
    (SB, 0),
    ch('Client', champ('t09-spa-cli')) + ch('Téléphone', champ('t09-spa-tel'), saisie=False)
    + ch('Ressource', champ('t09-spa-res')) + ch('Prestation', champ('t09-spa-pre'), aide=True, ident='t09-spa-l-pre')
    + ch('Origine', 'Comptoir', saisie=False),
    ch('Début', champ('t09-spa-deb')) + ch('Fin', champ('t09-spa-fin'))
    + ch('Durée (h)', champ('t09-spa-dur', '00:00'), saisie=False)
    + ch('Montant', champ('t09-spa-mnt', '0 FCFA'), saisie=False, ident='t09-spa-l-mnt')
    + ch('Prix manuel', '0 FCFA', aide=True),
    groupe_sejour('t09-spa'),
    ['',
     separateur("Aujourd'hui") + message(NOM, "Aujourd'hui à 11:06", suivi('Brouillon', 'Confirmée'))
     + message(NOM, '', CREE, suite=True),
     separateur("Aujourd'hui") + message(NOM, "Aujourd'hui à 16:05", suivi('Confirmée', 'Réalisée'))
     + message(NOM, "Aujourd'hui à 11:06", suivi('Brouillon', 'Confirmée')) + message(NOM, '', CREE, suite=True)],
    sale=True)

# La prestation de spa : la liste ne propose que la famille SPA (domaine kind = kind).
PRESTATIONS_SPA = ['Massage relaxant 60 min', 'Massage deep tissue 90 min', 'Soin du visage éclat',
                   'Gommage corporel karité']
DEROULANT = ('<div class="t09-dd masque" id="t09-spa-dd" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
             % ''.join('<div class="t09-dd-i"%s>%s</div>' % (_id('t09-spa-dd%d' % i), e(x))
                       for i, x in enumerate(PRESTATIONS_SPA)))
SPA = SPA.replace('<span class="v saisie">%s</span></div>' % champ('t09-spa-pre'),
                  '<span class="v saisie t09-m2o">%s%s</span></div>' % (champ('t09-spa-pre'), DEROULANT), 1)

# La réservation du salon VIP Wouri pour Brigitte Essomba : refusée à la confirmation.
SALON = fiche(
    't09-salon', PARENT_TDB, 'Nouveau', '',
    [[bt('t09-salon-b-conf', 'Confirmer', 'primaire'), bt(None, 'Annuler')]],
    (SB, 0),
    ch('Client', champ('t09-salon-cli')) + ch('Téléphone', champ('t09-salon-tel'), saisie=False)
    + ch('Ressource', champ('t09-salon-res')) + ch('Prestation', champ('t09-salon-pre'), aide=True)
    + ch('Origine', 'Comptoir', saisie=False),
    ch('Début', champ('t09-salon-deb')) + ch('Fin', champ('t09-salon-fin'))
    + ch('Durée (h)', champ('t09-salon-dur', '00:00'), saisie=False)
    + ch('Montant', champ('t09-salon-mnt', '0 FCFA'), saisie=False, ident='t09-salon-l-mnt')
    + ch('Prix manuel', '0 FCFA', aide=True),
    groupe_sejour('t09-salon'),
    ['', separateur("Aujourd'hui") + message(NOM, "Aujourd'hui à 11:09", CREE)],
    sale=True)

# Le dépôt pressing de Martin Ebode, réalisé ce matin, reporté sur son folio.
PRESSING = fiche(
    't09-pres', PARENT_LISTE, 'RES/26/0141', '11 / 11',
    [[bt('t09-pres-b-ret', 'Marquer retiré')], []],
    (SB, 2),
    ch('Client', champ('t09-pres-cli', 'Martin Ebode')) + ch('Téléphone', '+237 655 18 72 40', saisie=False)
    + ch('Ressource', champ('t09-pres-res', 'Comptoir pressing'))
    + ch('Prestation', champ('t09-pres-pre', 'Chemise'), aide=True)
    + ch('Quantité', champ('t09-pres-qte', '4'), aide=True, ident='t09-pres-l-qte')
    + ch('Origine', 'Comptoir', saisie=False),
    ch('Début', champ('t09-pres-deb', JOUR + ' 08:30:00')) + ch('Fin', champ('t09-pres-fin', JOUR + ' 09:00:00'))
    + ch('Durée (h)', '00:30', saisie=False)
    + ch('Montant', '<span id="t09-pres-mnt">4 800 FCFA</span>', saisie=False, ident='t09-pres-l-mnt')
    + ch('Prix manuel', '0 FCFA', aide=True),
    '<div class="t09-grp" id="t09-pres-pg-g"><div class="t09-grp-t">Pressing</div>%s%s</div>'
    % (ch('Retrait prévu', champ('t09-pres-rp', JOUR + ' 18:00:00')),
       ch('Retiré', case('t09-pres-retire'), ident='t09-pres-l-ret'))
    + groupe_sejour('t09-pres', 'FOL/2026/0209', 'Chemise — RES/26/0141'),
    [separateur("Aujourd'hui") + message(NOM, "Aujourd'hui à 08:36", suivi('Confirmée', 'Réalisée'))
     + message(NOM, "Aujourd'hui à 08:34", suivi('Brouillon', 'Confirmée')) + message(NOM, '', CREE, suite=True)])

# --------------------------------------------------- la liste du jour --
ETAT_LISTE = {'done': ('Réalisée', 't09-ok', 'ok'), 'confirmed': ('Confirmée', 't09-info', 'info'),
              'draft': ('Brouillon', 't09-muet', 'gris')}
COLS = [('Référence', '146px'), ('Début', '208px'), ('Client', '1fr'), ('Ressource', '206px'), ('Famille', '176px'),
        ('Prestation', '1.25fr'), ('Montant', '150px', 'd'), ('État', '124px')]
GAB = '40px ' + ' '.join(c[1] for c in COLS)


def ligne_liste(r, moment):
    n, cli, cle, pre, deb, _, mnt = r[:7]
    lib, cl_ligne, cl_badge = ETAT_LISTE[r[moment]]
    return ('<div class="ligne %s" id="t09-l-%s" style="grid-template-columns:%s"><span class="cb"></span>'
            '<span class="ell">RES/26/%s</span><span class="ell">%s %s:00</span><span class="ell">%s</span>'
            '<span class="ell">%s</span><span class="ell">%s</span><span class="ell">%s</span><span class="d">%s</span>'
            '<span><span class="t09-badge %s" id="t09-l-%s-e">%s</span></span></div>'
            % (cl_ligne, n, GAB, n, JOUR, hhmm(deb), e(cli), e(RES[cle][1]), e(LIB_FAMILLE[RES[cle][2]]), e(pre),
               fcfa(mnt), cl_badge, n, e(lib)))


def ordre_liste():
    """L'ordre de la liste : « start desc, id desc » (booking_booking.py:34)."""
    return sorted(RESAS, key=lambda r: (-r[4], -int(r[0])))


CP_LISTE = ('<div class="cp t09-cp"><span class="bt primaire">Nouveau</span><span class="titre">%s</span>'
            '<span class="t09-rouage">%s</span><div class="recherche t09-rech"><span class="loupe">%s</span>'
            '<span class="facette"><span class="fic">%s</span><span class="ell">Aujourd\'hui</span><span class="fx">×</span>'
            '</span><span class="ph">Rechercher…</span><span class="deroule">▾</span></div>'
            '<span class="pager">1-11 / 11</span><span class="t09-vues"><i class="on">%s</i><i>%s</i></span></div>'
            % (e(PARENT_LISTE), ROUAGE, ICONES['loupe'], ICONES['filtre'], LISTE_I, CAL))
TETE_LISTE = ('<div class="tete" style="grid-template-columns:%s"><span class="cb"></span>%s</div>'
              % (GAB, ''.join('<span class="ell%s">%s</span>' % (' d' if len(c) > 2 else '', e(c[0])) for c in COLS)))
LISTE = vue_libre('t09-liste', CP_LISTE + '<div class="liste t09-liste">%s%s<div class="total" style="grid-template-columns:'
                  '%s"><span></span><span></span><span></span><span></span><span></span><span></span><span></span>'
                  '<span class="d">%s</span><span></span></div></div>'
                  % (TETE_LISTE, ''.join(ligne_liste(r, APREM) for r in ordre_liste()), GAB,
                     fcfa(sum(r[6] for r in RESAS))))

# -------------------------------------------------------------- calques --
# Le téléphone de la cliente : l'e-mail de confirmation (mail_template_data.xml:3-33).
LIGNES_MAIL = [('Référence', 'RES/26/0158'), ('Ressource', 'Cabine SPA 1'), ('Prestation', 'Massage relaxant 60 min'),
               ('Début', JOUR + ' 15:00'), ('Fin', '16:00'), ('Montant', '27 000 FCFA')]
TELEPHONE = ('<div class="voile masque" id="t09-tel-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
             '<div class="tel masque t09-tel" id="t09-tel" data-layout-allow-overlap data-layout-allow-occlusion>'
             '<div class="tel-ecran t09-mail"><div class="t09-mail-h"><span class="t09-ret">‹</span></div>'
             '<div class="t09-mail-o" id="t09-mail-o">%s — Confirmation RES/26/0158</div>'
             '<div class="t09-mail-c"><p>Bonjour %s,</p><p>Votre réservation est <b>confirmée</b> :</p>'
             '<div class="t09-mail-t">%s</div><p>À très bientôt,<br>%s</p></div></div></div>'
             % (e(demo.SOCIETE), e(CLIENT),
                ''.join('<div><b>%s</b><span>%s</span></div>' % (e(a), e(b)) for a, b in LIGNES_MAIL), e(demo.SOCIETE)))

ERREUR = ('<div class="voile masque" id="t09-err-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
          '<div class="modale masque t09-modale" id="t09-err" style="top:200px;width:1060px;margin-left:-530px" '
          'data-layout-allow-overlap data-layout-allow-occlusion>'
          '<div class="m-tete"><span>Erreur de validation</span><span class="m-x">%s</span></div>'
          '<div class="m-corps"><p class="t09-err-p" id="t09-err-p">Conflit : « Salon VIP Wouri » est complète sur ce '
          'créneau (capacité 1).</p></div><div class="m-pied">%s</div></div>'
          % (ICONES['x'], bt('t09-err-ok', 'Fermer', 'primaire')))

# Le menu « Espaces & Prestations » de la réception : Tableau de bord, Réservations.
MENU_ESP = ('<span class="menu actif t09-m" id="t09-m-esp">Espaces &amp; Prestations<span class="t09-mdd masque" '
            'id="t09-mdd"><span id="t09-mdd-tdb">Tableau de bord</span><span id="t09-mdd-resa">Réservations</span>'
            '</span></span>')

ECRAN = navigateur(fenetre_muk('t09-app', 'Hôtel', MENUS, [TDB1, SPA, SALON, LISTE, PRESSING, TDB2],
                               actif='Espaces & Prestations', societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5',
                               apps=APPS_PROFIL['reception'], app_active='Hôtel', calques=TELEPHONE + ERREUR))
_menu = '<span class="menu actif">Espaces &amp; Prestations</span>'
assert ECRAN.count(_menu) == 1
ECRAN = ECRAN.replace(_menu, MENU_ESP)


def naviguer(entree_, apres):
    """Espaces & Prestations → entrée du menu, puis ce qui s'affiche (``apres`` : gestes)."""
    return [clic('#t09-m-esp', fx=0.45, d=0.5, puis=0.1), montrer('#t09-mdd', d=0.2, y=-6),
            clic('#t09-mdd-%s' % entree_, d=0.4, puis=0.1), cacher('#t09-mdd', d=0.15)] + list(apres)


CSS = """
#t09-app .o-haut { z-index: 6; font-size: 17px; gap: 22px; }
#t09-app .o-haut .nom-app { font-size: 21px; }
#t09-app .o-haut .menu.actif { font-weight: 600; }
.t09-m { position: relative; }
.t09-mdd { position: absolute; left: -16px; top: 42px; width: 280px; padding: 8px 0; border-radius: 6px; background: #fff;
  border: 1px solid #DEE2E6; box-shadow: 0 14px 34px rgba(0,0,0,.24); display: flex; flex-direction: column; }
.t09-mdd span { padding: 11px 22px; font-size: 18px; font-weight: 400; color: #212529; white-space: nowrap; }
.t09-pt { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 8px; flex: none; }
/* tableau de bord */
.t09 .tdb-tete { padding: 12px 22px; }
.t09 .tdb-titre { font-size: 25px; }
.t09 .tdb-sous { font-size: 16px; }
.t09-nouv { height: 40px; font-size: 18px; padding: 0 14px; }
.t09 .tdb-filtres { padding: 6px 22px; }
.t09 .tdb-rang { height: 50px; }
.t09 .tdb-rang.t09-rang-r { height: auto; padding: 6px 0; flex-wrap: wrap; row-gap: 8px; }
.t09 .tdb-lib { width: 150px; flex: none; font-size: 14px; color: #5F5E5A; }
.t09 .tdb-lib.t09-lib2 { width: auto; margin-right: 6px; }
.t09 .chip { height: 38px; font-size: 17px; color: #5F5E5A; }
.t09 .chip.actif { color: #fff; }
.t09-fl { width: 38px; justify-content: center; padding: 0; }
.t09-date { height: 38px; padding: 0 12px; border: 1px solid #DEE2E6; border-radius: 8px; display: inline-flex; align-items: center;
  gap: 18px; font-size: 17px; color: #212529; }
.t09-cal { width: 17px; height: 17px; display: inline-flex; color: #212529; }
.t09-cal svg { width: 17px; height: 17px; }
.t09-esp { flex: 1; }
.t09 .tdb-sect { margin: 14px 2px 8px; color: #57564F; }
.t09 .kpi { min-height: 0; padding: 13px 18px 12px; }
.t09 .kpi-l { font-size: 14px; }
.t09 .kpi-v { margin-top: 6px; font-size: 31px; color: #212529; }
.t09 .kpi-s { color: #5F666D; }
.t09-pl { background: #fff; border-radius: 12px; padding: 14px 18px; display: flex; flex-direction: column; gap: 9px; }
.t09-lane { display: grid; grid-template-columns: 214px 1fr 196px; column-gap: 12px; align-items: center; height: 42px; }
.t09-ln { display: flex; align-items: center; font-size: 17px; font-weight: 600; color: #46414E; min-width: 0; }
.t09-track { position: relative; height: 42px; background: #F6F4F3; border: 1px solid #E7E2DF; border-radius: 6px; overflow: hidden; }
.t09-tick { position: absolute; top: 0; bottom: 0; border-left: 1px dashed #DCD5D0; }
.t09-bloc { position: absolute; top: 4px; bottom: 4px; border-radius: 4px; color: #fff; font-size: 15px; font-weight: 500;
  line-height: 32px; padding: 0 7px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t09-bloc.conf { background: #185FA5; }
.t09-bloc.ok { background: #0F6E56; }
.t09-libre { font-size: 15px; color: #0F6E56; text-align: right; white-space: nowrap; }
.t09-gr .g-carte { height: 300px; }
.t09-gr .g-anneau { margin-top: 18px; gap: 60px; padding-left: 120px; }
.t09-gb { height: 300px; }
.t09-hbs { position: absolute; left: 20px; right: 26px; top: 54px; bottom: 40px; display: flex; flex-direction: column; }
.t09-hb { flex: 1; display: grid; grid-template-columns: 190px 1fr; column-gap: 10px; align-items: center; }
.t09-hb .l { font-size: 14px; color: #495057; text-align: right; white-space: nowrap; }
.t09-hb .p { position: relative; height: 100%; border-left: 1px solid #CED4DA;
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent calc(20% - 1px), #EEF0F2 calc(20% - 1px), #EEF0F2 20%); }
.t09-hb .p i { position: absolute; left: 0; top: 22%; bottom: 22%; border-radius: 0 3px 3px 0; }
.t09-hax { position: absolute; left: 20px; right: 26px; bottom: 12px; height: 22px; display: grid; grid-template-columns: 190px 1fr;
  column-gap: 10px; }
.t09-hax .p { position: relative; }
.t09-hax .p span { position: absolute; top: 2px; transform: translateX(-50%); font-size: 13px; color: #6C757D; white-space: nowrap; }
/* fiche */
.t09-f { position: absolute; inset: 0; background: #F8F9FA; color: #212529; }
.t09-f-cp { position: absolute; left: 0; right: 0; top: 0; height: 72px; display: flex; align-items: center; gap: 14px;
  padding: 0 20px; background: #fff; border-bottom: 1px solid #DEE2E6; }
.t09-f-cp .bt { height: 42px; font-size: 18px; }
.t09-fil { display: flex; flex-direction: column; line-height: 1.2; }
.t09-parent { font-size: 16px; color: #3F6A83; }
.t09-ref { font-size: 20px; display: inline-flex; align-items: center; gap: 8px; }
.t09-rouage { width: 17px; height: 17px; display: inline-flex; }
.t09-rouage svg { width: 17px; height: 17px; }
.t09-save { display: inline-flex; gap: 6px; margin-left: 4px; }
.t09-si { width: 22px; height: 22px; display: inline-flex; color: #4A7892; }
.t09-si:last-child { color: #6C757D; }
.t09-pager { margin-left: auto; font-size: 17px; color: #495057; }
.t09-f-g { position: absolute; left: 0; top: 72px; width: 1064px; bottom: 0; }
.t09-hd { position: relative; height: 56px; margin: 10px 0 0 20px; }
.t09-bts { position: relative; height: 42px; }
.t09-bg { position: absolute; left: 0; top: 0; display: flex; gap: 7px; }
.t09-bg .bt { height: 42px; font-size: 17px; padding: 0 12px; }
.t09-sb { position: absolute; right: 0; top: 0; display: flex; }
.t09-sb-e { height: 42px; padding: 0 20px 0 26px; display: flex; align-items: center; font-size: 17px; color: #495057;
  background: #E9ECEF; clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 0 100%, 12px 50%);
  margin-left: -4px; }
.t09-sb-e:first-child { padding-left: 16px; margin-left: 0; clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 0 100%); }
.t09-sb-e.actif { background: #DCE6EC; color: #212529; font-weight: 600; }
.t09-feuille { position: absolute; left: 20px; right: 0; top: 66px; bottom: 0; background: #fff; border: 1px solid #DEE2E6;
  border-bottom: 0; overflow: hidden; padding: 14px 24px 0; }
.t09-f-titre { font-size: 32px; font-weight: 500; margin-bottom: 10px; }
.t09-cols { display: grid; grid-template-columns: 1fr 1fr; column-gap: 36px; }
.t09-ch { display: grid; grid-template-columns: 150px 1fr; column-gap: 12px; align-items: center; min-height: 39px; font-size: 17px; }
.t09-grp .t09-ch { grid-template-columns: 190px 1fr; }
.t09-ch .l { color: #6C757D; white-space: nowrap; }
.t09-ch .l.gras { color: #212529; font-weight: 600; }
.t09-ch .v { position: relative; color: #212529; white-space: nowrap; min-height: 28px; display: flex; align-items: center; }
.t09-ch .v.saisie { border-bottom: 1px solid #DEE2E6; }
.t09-aide { margin-left: 3px; color: #4A7892; font-size: 12px; font-weight: 700; }
.t09-lien { color: #3F6A83; }
.entree.t09-in { margin: 0; height: 28px; padding: 0; border: 0; border-radius: 0; background: transparent; font-size: 17px; width: 100%; }
.entree.t09-in.focus { box-shadow: 0 2px 0 #4A7892; }
.entree.t09-in .ph, .entree.t09-in .val { left: 2px; font-weight: 400; }
.t09-grp { margin-top: 12px; }
.t09-grp-t { font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: .02em; color: #212529;
  padding-bottom: 6px; border-bottom: 1px solid #DEE2E6; margin-bottom: 4px; }
.t09-noteint { margin-top: 12px; padding: 8px 2px; font-size: 17px; color: #ADB5BD; border-bottom: 1px solid #EEF0F2; }
.t09-ch .case i { width: 20px; height: 20px; }
.t09-m2o { position: relative; }
.t09-dd { position: absolute; left: 0; top: 30px; width: 330px; z-index: 12; padding: 6px 0; background: #fff; border-radius: 4px;
  border: 1px solid #DEE2E6; box-shadow: 0 10px 24px rgba(0,0,0,.18); }
.t09-dd-i { height: 38px; display: flex; align-items: center; padding: 0 16px; font-size: 17px; color: #212529; white-space: nowrap; }
.t09-dd-i:first-child { background: #E9ECEF; }
/* discussion */
.t09-chatter { position: absolute; left: 1080px; right: 0; top: 72px; bottom: 0; padding: 12px 16px; background: #fff;
  border-left: 1px solid #DEE2E6; }
.t09-ch-bts { display: flex; gap: 6px; align-items: center; }
.t09-ch-bts .bt { height: 40px; font-size: 16px; padding: 0 11px; gap: 7px; }
.t09-bi { width: 16px; height: 16px; display: inline-flex; }
.t09-bi svg { width: 16px; height: 16px; }
.t09-ch-ic { margin-left: auto; width: 20px; height: 20px; display: inline-flex; }
.t09-ch-ic svg { width: 20px; height: 20px; }
.t09-suivre { margin-left: 14px; font-size: 16px; color: #495057; }
.t09-ch-fil { position: relative; margin-top: 8px; }
.t09-ch-etat { position: absolute; left: 0; right: 0; top: 0; }
.t09-sep { display: flex; align-items: center; gap: 12px; margin: 10px 0 4px; font-size: 13px; color: #6C757D; }
.t09-sep::before, .t09-sep::after { content: ''; flex: 1; height: 1px; background: #DEE2E6; }
.t09-msg { display: flex; gap: 12px; padding: 7px 0; }
.t09-msg.suite { padding-top: 0; }
.t09-msg.suite > span { width: 36px; flex: none; }
.t09-av { width: 36px; height: 36px; border-radius: 6px; background: #185FA5; color: #fff; display: flex; align-items: center;
  justify-content: center; font-weight: 700; flex: none; }
.t09-msg-a { font-size: 15px; color: #212529; }
.t09-msg-a small { font-size: 13px; color: #6C757D; margin-left: 4px; }
.t09-msg-t { margin-top: 3px; font-size: 16px; line-height: 1.38; color: #212529; }
.t09-suivi { display: inline-flex; align-items: center; gap: 4px; font-size: 15px; }
.t09-suivi .anc { color: #495057; }
.t09-suivi .sep { margin: 0 4px; color: #495057; }
.t09-fl-i { width: 16px; height: 16px; display: inline-flex; }
.t09-fl-i svg { width: 16px; height: 16px; }
.t09-suivi .nouv { color: #2E6F8E; }
.t09-suivi i { color: #6C757D; }
/* liste */
.t09-cp .titre { font-size: 23px; }
.t09-cp .bt { height: 42px; font-size: 18px; }
.t09-cp .t09-rouage { margin-left: -6px; }
.t09-rech { margin-left: 120px; width: 620px; height: 46px; font-size: 18px; }
.t09-rech .facette { height: 32px; font-size: 17px; }
.t09-cp .pager { font-size: 18px; }
.t09-vues { margin-left: 18px; display: flex; }
.t09-vues i { width: 46px; height: 40px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40; }
.t09-vues i + i { border-left: 1px solid #fff; }
.t09-vues i.on { background: #DCE6EC; box-shadow: inset 0 0 0 1px var(--muk-prim); }
.t09-vues svg { width: 19px; height: 19px; }
.t09-liste .tete { height: 48px; font-size: 17px; }
.t09-liste .ligne { height: 46px; font-size: 17px; }
.t09-liste .total { height: 48px; font-size: 17px; }
.t09-liste .ligne.t09-info { color: #0E7490; }
.t09-liste .ligne.t09-ok { color: #1E7B34; }
.t09-liste .ligne.t09-muet { color: #6C757D; }
.t09-badge { display: inline-flex; align-items: center; height: 26px; padding: 0 10px; border-radius: 999px; font-size: 14px;
  font-weight: 600; white-space: nowrap; }
.t09-badge.ok { background: #1E7B34; color: #fff; }
.t09-badge.info { background: #0E7490; color: #fff; }
.t09-badge.gris { background: #DEE2E6; color: #212529; }
.liste .ligne.survol { background: #E8EEF2; }
/* téléphone : l'e-mail reçu */
.t09-tel { top: 30px; height: 720px; }
.t09-mail { background: #fff; }
.t09-mail-h { height: 58px; display: flex; align-items: center; padding: 0 20px; border-bottom: 1px solid #EEF0F2; }
.t09-ret { font-size: 34px; color: #2E6F8E; line-height: 1; }
.t09-mail-o { padding: 18px 22px 14px; font-size: 22px; font-weight: 700; line-height: 1.3; color: #212529; border-bottom: 1px solid #EEF0F2; }
.t09-mail-c { padding: 14px 22px; font-family: Calibri, Arial, sans-serif; font-size: 18px; line-height: 1.45; color: #2B2A28; }
.t09-mail-c p { margin: 0 0 12px; }
.t09-mail-t { margin: 4px 0 14px; display: flex; flex-direction: column; gap: 6px; }
.t09-mail-t div { display: grid; grid-template-columns: 112px 1fr; column-gap: 10px; font-size: 17px; }
.t09-mail-t b { color: #714B67; }
/* fenêtre d'erreur */
.t09-modale .m-tete { height: 66px; }
.t09-err-p { font-size: 22px; line-height: 1.5; color: #212529; margin: 6px 0 10px; }
.t09-modale .m-pied .bt { height: 44px; font-size: 19px; }
"""

TUTORIEL = {
    'slug': 't09-espaces',
    'profil': 't09_espaces',
    'numero': 9,
    'titre': 'Espaces & Prestations : SPA, coiffure, salons VIP et pressing sur un seul planning, sans double réservation',
    'fonction': 'Espaces & Prestations',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Espaces & prestations',
        'question': 'Deux clients pour *un* seul salon ?',
        'douleurs': [('alerte', 'Le même salon vendu deux fois'),
                     ('document', 'Le massage oublié sur la note de chambre'),
                     ('sablier', 'Le rendez-vous manqué bloque la cabine'),
                     ('boite', 'Les dépôts pressing qui attendent'),
                     ('graphe', 'Quel espace rapporte, lequel dort ?')],
        'voix': "Deux clients pour un seul salon ? Un massage oublié sur la note de chambre, un rendez-vous manqué qui "
                "bloque la cabine : la réception perd le fil.",
    },
    'revelation': {
        'promesse': "Salons VIP, SPA, coiffure et pressing sur un seul planning. La fin et le prix se calculent seuls, "
                    "un créneau complet est refusé, la prestation passe sur la note de chambre.",
        'voix': "Avec Aïte haousse, salons, spa, coiffure et pressinng partagent un seul planninng.",
    },
    'temps': ['Voir', 'Réserver', 'Verrouiller', 'Clôturer'],
    'app': 't09-app',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't09-tdb1'},
    'bulles': {
        'b-libres': "Une ligne par ressource : les créneaux libres se lisent d'un coup d'œil.",
        'b-calcul': 'La fin et le montant viennent de la prestation : rien à calculer.',
        'b-mail': "Confirmée : le créneau est bloqué, l'e-mail part tout seul.",
        'b-folio': 'Reportée seule sur la note de chambre, une seule fois.',
        'b-absent': 'Client confirmé absent : No-show automatique, passé 6 h après la fin.',
    },
    'reactions': {
        'r-conflit': 'Le salon est déjà pris : impossible de le vendre deux fois.',
        'r-pressing': 'Quatre chemises, et le prix a suivi tout seul.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le planning du jour',
         'texte': 'Salons, cabines, fauteuils, comptoir : une ligne par ressource, chaque réservation à son heure.',
         'voix': "Sur le tableau de bord, Mireille voit toute sa journée : les salons VIP, les cabines de spa, les "
                 "fauteuils de coiffure et le comptoir de pressinng. Une ligne par ressource, chaque réservation à son "
                 "heure, et les créneaux encore libres.",
         'gestes': [pause(0.3), anneau('#t09-d1-kpis', d=1.6), pause(0.4), defiler('#t09-in1', -330, d=1.1),
                    zoom('#t09-d1-l3', s=1.45, fx=0.42), anneau('#t09-d1-t3', d=1.2),
                    bulle('b-libres', '#t09-d1-x3', cote='bas', d=3.0), pause(2.8), dezoom(d=0.6),
                    anneau('#t09-d1-l0', d=1.0), anneau('#t09-d1-l7', d=1.0)]},
        {'temps': 1, 'titre': 'Réserver un soin',
         'texte': 'Cliente, cabine, prestation, début : la fin et le montant se calculent seuls.',
         'voix': "Estelle Ngono, en chambre deux cent quatre, veut un massage à quinze heures. Mireille choisit la "
                 "cliente, la cabine, puis le soin : seules les prestations de spa sont proposées. Elle saisit l'heure "
                 "de début : la fin et le montant se remplissent tout seuls.",
         'gestes': [defiler('#t09-in1', 0, d=0.6), clic('#t09-d1-nouv', d=0.6), vue('t09-spa'),
                    clic('#t09-spa-cli', fx=0.3, d=0.5), choisir('t09-spa-cli', CLIENT),
                    montrer('#t09-spa-save', d=0.2, y=0, avec=True),
                    texte('#t09-spa-tel-val', TEL), clic('#t09-spa-res', fx=0.3, d=0.5),
                    choisir('t09-spa-res', 'Cabine SPA 1'), clic('#t09-spa-pre', fx=0.3, d=0.5),
                    montrer('#t09-spa-dd', d=0.25, y=-6), pause(0.9), clic('#t09-spa-dd0', d=0.4),
                    cacher('#t09-spa-dd', d=0.15), choisir('t09-spa-pre', 'Massage relaxant 60 min'),
                    texte('#t09-spa-mnt-val', '27 000 FCFA'),
                    clic('#t09-spa-deb', fx=0.3, d=0.5), saisir('t09-spa-deb', JOUR + ' 15:00:00', d=1.0),
                    texte('#t09-spa-fin-val', JOUR + ' 16:00:00'), texte('#t09-spa-dur-val', '01:00', avec=True),
                    zoom('#t09-spa-droite', s=1.45, fx=0.4), anneau('#t09-spa-droite', d=1.6),
                    bulle('b-calcul', '#t09-spa-l-mnt', cote='bas', d=2.8), pause(2.4), dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Confirmer : le créneau est bloqué',
         'texte': "La réservation passe en Confirmée ; l'e-mail de confirmation part tout seul.",
         'voix': "Un clic sur Confirmer : le créneau est bloqué, et la cliente reçoit aussitôt son imèle de "
                 "confirmation, avec l'heure, la cabine et le montant.",
         'gestes': [clic('#t09-spa-b-conf', d=0.6), cacher('#t09-spa-save', d=0.15),
                    texte('#t09-spa-titre', 'RES/26/0158'), texte('#t09-spa-ref', 'RES/26/0158', avec=True),
                    cacher('#t09-spa-g0', d=0.15), montrer('#t09-spa-g1', d=0.25, y=0, avec=True),
                    classe('#t09-spa-sb0', retirer=['actif']), classe('#t09-spa-sb1', ajouter=['actif']),
                    cacher('#t09-spa-ch0', d=0.1), montrer('#t09-spa-ch1', d=0.35, y=8),
                    anneau('#t09-spa-sb', d=1.1), ouvrir('t09-tel'),
                    bulle('b-mail', '#t09-tel', cote='gauche', d=3.2), anneau('#t09-mail-o', d=1.3),
                    pause(2.4), fermer('t09-tel')]},
        {'temps': 2, 'titre': 'Un salon déjà pris ? Refusé.',
         'texte': "À l'heure, au tarif horaire du salon ; un créneau complet est refusé à la confirmation.",
         'voix': "Brigitte Essomba veut le salon VIP Wouri ce soir, de vingt à vingt-trois heures. Sans prestation, "
                 "le tarif horaire fait le prix : quarante-cinq mille francs. Mais le salon est déjà réservé : la "
                 "confirmation est refusée, et le message dit pourquoi.",
         'gestes': [clic('#t09-spa-nv', d=0.5), vue('t09-salon'),
                    clic('#t09-salon-cli', fx=0.3, d=0.45), choisir('t09-salon-cli', 'Brigitte Essomba'),
                    montrer('#t09-salon-save', d=0.2, y=0, avec=True), texte('#t09-salon-tel-val', '+237 690 27 51 84'),
                    clic('#t09-salon-res', fx=0.3, d=0.45), choisir('t09-salon-res', 'Salon VIP Wouri'),
                    clic('#t09-salon-deb', fx=0.3, d=0.45), saisir('t09-salon-deb', JOUR + ' 20:00:00', d=0.8),
                    clic('#t09-salon-fin', fx=0.3, d=0.4), saisir('t09-salon-fin', JOUR + ' 23:00:00', d=0.8),
                    texte('#t09-salon-dur-val', '03:00'), texte('#t09-salon-mnt-val', '45 000 FCFA', avec=True),
                    anneau('#t09-salon-l-mnt', d=1.2), clic('#t09-salon-b-conf', d=0.5),
                    cacher('#t09-salon-save', d=0.1), texte('#t09-salon-titre', 'RES/26/0159'),
                    texte('#t09-salon-ref', 'RES/26/0159', avec=True), cacher('#t09-salon-ch0', d=0.05),
                    montrer('#t09-salon-ch1', d=0.05, y=0), ouvrir('t09-err'),
                    zoom('#t09-err', s=1.3, d=0.7), reaction('r-conflit', d=3.0), pause(2.8), dezoom(d=0.5),
                    clic('#t09-err-ok', d=0.4), fermer('t09-err')]},
        {'temps': 3, 'titre': 'Réalisée : sur la note de chambre',
         'texte': 'La prestation est reportée seule sur le folio du séjour, une seule fois.',
         'voix': "Seize heures, le massage est fait. Un clic sur Réalisée : la prestation est reportée toute seule "
                 "sur le folio de la chambre deux cent quatre, une seule fois. Elle sera réglée au départ, avec le "
                 "séjour.",
         'gestes': naviguer('resa', [vue('t09-liste'), pause(0.4)]) + [
             texte('#t09-spa-par', PARENT_LISTE), texte('#t09-spa-pg', '5 / 11', avec=True),
             classe('#t09-l-0158', ajouter=['survol']), clic('#t09-l-0158', fx=0.3, d=0.5), vue('t09-spa'),
             clic('#t09-spa-b-done', d=0.5), cacher('#t09-spa-g1', d=0.15),
             classe('#t09-spa-sb1', retirer=['actif']), classe('#t09-spa-sb2', ajouter=['actif']),
             texte('#t09-spa-folio-val', 'FOL/2026/0214'),
             texte('#t09-spa-ligne', 'Massage relaxant 60 min — RES/26/0158', avec=True),
             cacher('#t09-spa-ch1', d=0.1), montrer('#t09-spa-ch2', d=0.3, y=8),
             zoom('#t09-spa-sejour', s=1.5, fx=0.35), anneau('#t09-spa-sejour', d=1.6),
             bulle('b-folio', '#t09-spa-sejour', cote='haut', d=3.0), pause(2.6), dezoom(d=0.6)]},
        {'temps': 3, 'titre': 'Pressing : la quantité fait le prix',
         'texte': '4 chemises × 1 200 FCFA, déjà sur la note ; au retrait, Marquer retiré.',
         'voix': "Ce matin, Martin Ebode a déposé quatre chemises : le montant a suivi la quantité, et sa note de "
                 "chambre est déjà à jour. Ce soir, il les récupère : Marquer retiré, et le dépôt sort des retraits "
                 "en attente.",
         'gestes': [classe('#t09-l-0158', retirer=['survol', 't09-info'], ajouter=['t09-ok']),
                    classe('#t09-l-0158-e', retirer=['info'], ajouter=['ok']), texte('#t09-l-0158-e', 'Réalisée'),
                    clic('#t09-spa-par', d=0.5), vue('t09-liste'), pause(0.3),
                    classe('#t09-l-0141', ajouter=['survol']), clic('#t09-l-0141', fx=0.3, d=0.5),
                    vue('t09-pres'), anneau('#t09-pres-l-qte', d=1.3), anneau('#t09-pres-l-mnt', d=1.3),
                    reaction('r-pressing', d=2.8), anneau('#t09-pres-sejour', d=1.3), pause(0.6),
                    clic('#t09-pres-b-ret', d=0.5), cacher('#t09-pres-g0', d=0.15),
                    classe('#t09-pres-retire', ajouter=['coche']), anneau('#t09-pres-l-ret', d=1.2), pause(0.6)]},
        {'temps': 3, 'titre': 'Le bilan du soir',
         'texte': "Chiffre d'affaires, remplissage, retraits en attente ; un client absent passe seul en No-show.",
         'voix': "Le soir, le tableau de bord fait le bilan : chiffre d'affaires réalisé, remplissage, retraits en "
                 "attente. Et si un client confirmé ne vient pas, la réservation passe toute seule en rendez-vous "
                 "manqué, six heures après la fin du créneau.",
         'gestes': naviguer('tdb', [vue('t09-tdb2'), defiler('#t09-in2', -330, d=0.01)]) + [
             pause(0.3), anneau('#t09-d2-ca', d=1.3), anneau('#t09-d2-pr', d=1.2), anneau('#t09-d2-t3', d=1.2),
             zoom('#t09-d2-ns', s=1.4, fx=0.5, fy=0.6), bulle('b-absent', '#t09-d2-ns', cote='bas', d=3.2),
             pause(3.0), dezoom(d=0.6)]},
    ],
    'resultats': {
        'titre': 'Tous vos espaces, un seul planning',
        'cartes': [
            {'valeur': '5', 'compter': 5, 'unite': 'familles', 'icone': 'liste',
             'texte': 'salons VIP / VVIP, SPA, coiffure, pressing et autres ressources, sur un même planning'},
            {'valeur': '3', 'compter': 3, 'unite': 'automatismes', 'icone': 'eclair',
             'texte': "actifs dès l'installation : e-mail de confirmation, report au folio, no-show après 6 h"},
            {'valeur': '69', 'compter': 69, 'unite': 'tests', 'icone': 'bouclier',
             'texte': 'automatisés sur le moteur : créneaux, conflits, prix, report au folio, no-show'},
        ],
        'voix': "Cinq familles sur un seul planninng, trois automatismes actifs dès l'installation, et soixante-neuf "
                "tests automatisés sur le moteur de réservation.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Les ardoises clients',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 4, 'apres': 11.0},
}
