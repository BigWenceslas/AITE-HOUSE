# -*- coding: utf-8 -*-
"""Chapitre 2 — Le tour des chambres.

Source : fiche de recette n° 2 « Le tour des chambres » (gouvernante :
tâches du jour, recouche démarrée puis terminée, état des chambres, refus
d'accès aux folios), complétée par le cahier de recette, domaine P
(aite_housekeeping : tableau des chambres, « Ma journée » sur téléphone,
inspection avec checklist, panne qui bloque la chambre, remise en vente).

Libellés relevés dans (livraison 4, écarts n° 37-77) :
aite_housekeeping/views/hotel_room_views.xml (carte du tableau des chambres :
boutons « Je commence » et « C'est fait », les mots de « Ma journée » au lieu
de « Commencer » / « Terminé », écart n° 51 ; « Conforme » et « À refaire »
réservés au profil « Gouvernante générale », écart n° 52 ; « À nettoyer »,
clé « Signaler un problème »), models/hotel_room.py (_hint_for : « À
nettoyer », « À inspecter par la gouvernante », « Propre — prête pour
l'arrivée », « Hors service — ne pas vendre » ; « Arrivée prévue 14:00 » et
non plus « 14h00 », relecture de l'intégration ; colonnes par group_expand,
écart n° 50), views/housekeeping_task_views.xml et models/housekeeping_task.py
(« Ma journée », « Je commence », « C'est fait », « Passer la checklist »,
libellés des tâches, état « Terminé » de la tâche, hotel_housekeeping.py:62-66,
inspection « Tout cocher » / « Valider l'inspection »),
data/housekeeping_data.xml (les 8 points de contrôle),
wizard/report_issue_wizard*.py|xml (« Signaler un problème »). Le refus
d'accès reprend le message d'Odoo 18 en français et les groupes de
aite_hotel_management/security/hotel_security.xml.

La journée rejouée est celle de scenarios/t07_gouvernante.py, le jeudi
15/10/2026 au matin (fiche d'harmonisation de la série), après la répartition
de t07 (103 → Clarisse, 104 → Sidonie, 202 → Clarisse, 204 → Sidonie, 401 →
Clarisse) : Martin Ebode en 104 [STD], dont Sidonie a commencé le ménage ;
Gaston Mbida attendu en 103 [STD] à 14:00 (« Recouche à faire » : à nettoyer
avant une arrivée, aite_housekeeping/models/hotel_room.py:84-87 ; « Arrivée
prévue 14:00 », :68-73), la recouche de Clarisse. « Ma journée » de Clarisse :
la 103 (« Recouche complète (départ) »), puis les ménages quotidiens de la 401
(Claire Durand) et de la 202 (Brigitte Essomba), dans l'ordre de t07. À
« C'est fait », la chambre passe « À inspecter » et sa tâche d'inspection est
créée sans affectation (aite_hotel_management/models/hotel_housekeeping.py
:107-146) : la carte ne montre plus d'équipière. L'inspection refusée renvoie
la 103 « Recouche à faire », chez Clarisse. Les 18 autres chambres sont
propres, triées par numéro (default_order="name") : 101, 102, 105 (hors
service toute la série, sur fond rouge, sans « À nettoyer »), 106 en tête de
la colonne « Propre ». La panne bloquante porte, comme dans t07, sur la 102,
libre et propre : elle sort une chambre libre de la vente
(maintenance_request.py:51-54). Colonnes dans l'ordre du travail, celui de la
sélection hk_state, toutes affichées même vides : À nettoyer, Nettoyage en
cours, À inspecter, Propre (group_expand, aite_housekeeping/models/
hotel_room.py:13-20 et :48-51, corrigé dans la livraison 4, écart n° 50) ;
les effectifs sont ceux des 20 chambres, seules les premières cartes sont
rejouées. Josiane a le profil « Gouvernante générale »
(security/housekeeping_security.xml) : elle voit « Conforme » et « À refaire »
sans le profil Réception (écart n° 52), sa barre ne porte que « Gouvernante »
(ecrans.MENUS_MUK['hotel_gouvernante']) et le tableau n'a pas de bouton
« Nouveau » (chambres en lecture et écriture seulement,
aite_hotel_management/security/ir.model.access.csv:10). Checklist : la case
s'intitule « OK » (housekeeping_task_views.xml:92-95). Titre de l'assistant :
« Signaler un problème — chambre %s » (hotel_room.py:149-159). Urgence de
l'assistant : « Important » par défaut (une étoile) ; Josiane choisit
« Urgent » (deux étoiles). La demande de maintenance prend la priorité
« Haute », trois étoiles sur la carte, et « Urgence : Urgent » est écrit en
tête de sa description (report_issue_wizard.py:25-50, ECARTS n° 15 c).
« Conforme » coche toute la checklist puis clôt l'inspection
(hotel_room.py:125-140, ECARTS n° 19). Pannes & réparations (Hôtel →
Gouvernante, menus.xml:19-21) s'ouvre filtré « À faire » (search_default_todo,
maintenance_views.xml:40-46) : « Réparé » et « Rebut » sont repliés, et la
demande passée à « Réparé » par le technicien, même sans profil hôtel, quitte
la liste ; la chambre revient en vente, à nettoyer, avec une tâche « Remise
en service après intervention », non affectée (maintenance_request.py:39-89,
ECARTS n° 15 a et b).
« ? » d'aide (form_label.xml:6, hors mode debug) dans « Signaler un
problème » sur les deux champs qui portent un help= : « Quel est le
problème ? », qui garde son propre point d'interrogation, et « La chambre ne
peut pas être vendue en l'état » (report_issue_wizard.py:11-18), comme
scenarios/t07_gouvernante.py.
"""

import demo
from ecrans import (MENUS_MUK, assistant, bouton, carte, e, entree, erreur_acces, fenetre, icone, interrupteur, m_champ,
                    m_champs, telephone, vue_kanban)
from moteur import animer, anneau, cacher, choisir, clic, classe, etat, fermer, montrer, ouvrir, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['gouvernante']


def aide(html):
    """Le « ? » qu'Odoo 18 pose après le libellé d'un champ qui porte une aide (help= du modèle ; form_label.xml:6) :
    ajouté au libellé d'un ecrans.m_champ, dont le premier span est le libellé."""
    assert html.startswith('<div class="m-ch"')
    return html.replace('</span>', '<sup class="c2-aide">?</sup></span>', 1)

EQ1, EQ2 = demo.EQUIPIERES


def carte_chambre(ident, numero, hint, type_etage, client=None, arrivee=None, equipiere=None, boutons=(), panne=None,
                  classe_=''):
    """Une carte du tableau des chambres, dans l'ordre de la vue kanban. ``panne`` : le nombre de
    pannes ouvertes ; ``'masque'`` pose le badge caché, révélé quand la panne est signalée."""
    badge = ''
    if panne:
        badge = '<span class="badge-panne%s" id="%s-panne">%s1</span>' % (
            ' masque' if panne == 'masque' else '', ident, icone('cle'))
    lignes = '<div class="hint" id="%s-hint">%s</div><div class="mini">%s</div>' % (ident, e(hint), e(type_etage))
    if client:
        lignes += '<div class="lg">%s%s</div>' % (icone('personne'), e(client))
    if arrivee:
        lignes += '<div class="lg info">%s%s</div>' % (icone('horloge'), e(arrivee))
    if equipiere:
        lignes += '<div class="lg">%s%s</div>' % (icone('personne'), e(equipiere))
    bts = ''.join(boutons) + bouton(ident + '-cle', '', 'rouge-contour', 'cle')
    return carte(ident, '<div class="num-ch"><span>%s</span>%s</div>%s<div class="bts">%s</div>'
                 % (e(numero), badge, lignes, bts), classe_)


# ------------------------------------------------- Tableau des chambres --
# La journée de t07 (REPARTITION, tâches triées étage puis chambre, équipières par nom) : 103 → Clarisse,
# 104 → Sidonie, 202 → Clarisse, 204 → Sidonie, 401 → Clarisse. Sidonie a commencé la 104 ; la 103 de Gaston
# Mbida attend sa recouche. Les autres chambres sont propres (18 sur 20, la 105 hors service comprise) ; le
# kanban les trie par numéro (default_order="name", hotel_room_views.xml:14) : 101, 102, 105, 106… en tête de la
# colonne « Propre », la suite sous le bas de l'écran.
STD = 'Standard · Rez-de-chaussée'
GASTON, ARR_103 = 'Gaston Mbida', 'Arrivée prévue 14:00'
CACHE = ' style="display:none"'          # une carte retirée de sa colonne ne laisse pas de trou
C103 = carte_chambre('c2-103', '103', 'Recouche à faire', STD, client=GASTON, arrivee=ARR_103, equipiere=EQ1,
                     boutons=[bouton('c2-103-go', 'Je commence', 'primaire', 'play')])
# À « C'est fait », la tâche d'inspection est créée sans affectation (hotel_housekeeping.py:107-146) : la carte
# « À inspecter » ne montre plus d'équipière (assigned_to = la tâche du jour, hotel_room.py:59-73).
C103_INSP = carte_chambre('c2-103i', '103', 'À inspecter par la gouvernante', STD, client=GASTON, arrivee=ARR_103,
                          boutons=[bouton('c2-103-ok', 'Conforme', 'vert', 'coche'),
                                   bouton('c2-103-ko', 'À refaire', 'rouge-contour')], classe_='masque')
C104 = carte_chambre('c2-104', '104', 'Nettoyage en cours', STD, client='Martin Ebode', equipiere=EQ2,
                     boutons=[bouton('c2-104-done', "C'est fait", 'vert', 'coche')])
C101 = carte_chambre('c2-101', '101', 'Propre — libre', STD, boutons=[bouton('c2-101-sale', 'À nettoyer', 'blanc')])
C102 = carte_chambre('c2-102', '102', 'Propre — libre', STD, boutons=[bouton('c2-102-sale', 'À nettoyer', 'blanc')],
                     panne='masque')
# Réparée : la 102 revient en vente, « À nettoyer », avec sa tâche de remise en service, non affectée
# (maintenance_request.py:76-89).
C102_SALE = carte_chambre('c2-102s', '102', 'À nettoyer', STD, boutons=[bouton('c2-102s-go', 'Je commence', 'primaire',
                                                                                'play')], classe_='masque')
C105 = carte_chambre('c2-105', '105', 'Hors service — ne pas vendre', STD, classe_='hors-service')
C106 = carte_chambre('c2-106', '106', 'Propre — libre', STD, boutons=[bouton('c2-106-sale', 'À nettoyer', 'blanc')])
C107 = carte_chambre('c2-107', '107', 'Propre — libre', STD, boutons=[bouton('c2-107-sale', 'À nettoyer', 'blanc')])
C102_SALE = C102_SALE.replace('id="c2-102s"', 'id="c2-102s"' + CACHE, 1)


def plie(titre):
    """Une colonne repliée du kanban (étapes « Réparé » et « Rebut », fold) : le titre à la verticale."""
    return ('<div class="k-col" style="width:56px;display:flex;flex-direction:column;align-items:center;gap:14px">'
            '<span style="font-size:16px;color:var(--o-texte-2)">◂▸</span><b style="writing-mode:vertical-rl;'
            'font-size:21px;font-weight:500;color:var(--o-texte)">%s</b></div>' % e(titre))


# Colonnes dans l'ordre de la sélection hk_state (group_expand) : À nettoyer, Nettoyage en cours, À inspecter,
# Propre. La Gouvernante ne crée pas de chambre (accès 1,1,0,0, ir.model.access.csv:10) : pas de « Nouveau ».
TABLEAU = vue_kanban('c2-tableau', 'Tableau des chambres', [
    ('À nettoyer', '1', [C102_SALE, C103], 'c2-col-1'),
    ('Nettoyage en cours', '1', [C104], 'c2-col-2'),
    ('À inspecter', '0', [C103_INSP], 'c2-col-3'),
    ('Propre', '18', [C101, C102, C105, C106, C107], 'c2-col-4')], initiale=True, nouveau=False)

# ------------------------------------------------------ Ma journée (téléphone) --
def tache_tel(ident, chambre, libelle, client, etat_, genre, bouton_html):
    return ('<div class="tel-carte" id="%s"><div class="h"><span>Chambre %s</span><span class="puce %s" id="%s-etat">%s</span></div>'
            '<div class="s">%s</div>%s%s</div>'
            % (ident, e(chambre), genre, ident, e(etat_), e(libelle),
               '<div class="p">%s%s</div>' % (icone('personne'), e(client)) if client else '', bouton_html))


# Les tâches de Clarisse (t07 : la recouche de la 103, puis les ménages quotidiens de la 401 et de la 202, ordre
# « date desc, priority desc, id desc »).
TACHE_103 = tache_tel('c2-t103', '103 [STD]', 'Recouche complète (départ)', GASTON, 'À faire', 'orange',
                      '<div class="tel-bt violet" id="c2-t103-go">%sJe commence</div>'
                      '<div class="tel-bt vert masque" id="c2-t103-fin" style="margin-top:-54px">%sC\'est fait</div>'
                      % (icone('play'), icone('coche')))
TACHE_401 = tache_tel('c2-t401', '401 [VIP]', 'Ménage quotidien (client présent)', 'Claire Durand', 'À faire', 'orange',
                      '<div class="tel-bt violet">%sJe commence</div>' % icone('play'))
TACHE_202 = tache_tel('c2-t202', '202 [CFT]', 'Ménage quotidien (client présent)', 'Brigitte Essomba', 'À faire',
                      'orange', '<div class="tel-bt violet">%sJe commence</div>' % icone('play'))
TELEPHONE = telephone('c2-tel', 'Ma journée', TACHE_103 + TACHE_401 + TACHE_202)

# ------------------------------------------------------------- Inspection --
POINTS = ['Lit refait, draps propres', 'Salle de bain nettoyée, serviettes changées', 'Sol balayé et lavé',
          'Poubelles vidées', 'Savon, papier, eau de courtoisie réapprovisionnés', 'Minibar vérifié et recomplété',
          'Climatiseur, lumières et télécommande fonctionnent', 'Aucune odeur, aucun objet oublié']
LIGNES = ''.join('<div class="check"><span>%s</span><span class="ell">%s</span><span class="rq">%s</span></div>'
                 % (interrupteur('c2-ck%d' % i), e(p),
                    '<span id="c2-rq"><span class="ph" id="c2-rq-ph"></span><span class="val" id="c2-rq-val"></span></span>'
                    if i == 1 else '')
                 for i, p in enumerate(POINTS))
INSPECTION = assistant('c2-as-insp', 'Inspection — chambre 103', (
    '<div style="font-size:32px;margin-bottom:6px">Chambre <span style="color:var(--o-prim)">103 [STD]</span></div>'
    '<div class="m-aide">Inspection — passer la checklist · contrôle <span id="c2-ctrl">0 / 8</span><br>'
    'Cochez chaque point conforme. Un point non coché renverra la chambre en nettoyage avec votre remarque.</div>'
    # La colonne de la case s'intitule « OK » (string="OK", housekeeping_task_views.xml:92-95).
    '<div class="check tete"><span>OK</span><span>Point de contrôle</span><span>Remarque</span></div>' + LIGNES),
    [('c2-tout', 'Tout cocher', 'gris', None), ('c2-valider', "Valider l'inspection", 'primaire', None),
     ('c2-fermer', 'Fermer', 'gris', None)], haut=26, largeur=1260)

# ------------------------------------------------------ Signaler un problème --
# Étoile vide du widget priorité ; l'urgence « Important » (défaut) en allume une.
ETOILE_VIDE = ('<span class="ico" style="opacity:.25"><svg viewBox="0 0 24 24" fill="#6C757D"><path d="M12 2.5l2.9 6.3 '
               '6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg></span>')
PROBLEME = assistant('c2-as-pb', 'Signaler un problème — chambre 102', m_champs([
    m_champ('Chambre', e('102 [STD]')),
    aide(m_champ('Quel est le problème ?', entree('c2-pb', 'Ex. : climatiseur en panne, fuite lavabo…'))),
    m_champ('Urgence', '<span class="etoiles">%s<span class="pile" id="c2-et2">%s%s</span>%s</span>'
             % (icone('etoile'), ETOILE_VIDE, icone('etoile').replace('class="ico"', 'class="ico masque" id="c2-et2-on"', 1),
                ETOILE_VIDE)),
    aide(m_champ("La chambre ne peut pas être vendue en l'état", '<span class="case" id="c2-bloque"><i></i></span>')),
    m_champ('Précisions', entree('c2-precis', 'Précisions utiles au technicien'))]),
    [('c2-pb-ok', 'Envoyer à la maintenance', 'primaire', None), ('c2-pb-non', 'Annuler', 'gris', None)], haut=120)

# ------------------------------------------------------ Pannes & réparations --
# Hôtel → Gouvernante → Pannes & réparations, ouvert filtré « À faire » (étape non terminée, search_default_todo,
# maintenance_views.xml:40-46) : « Réparé » et « Rebut », étapes terminées et repliées, ne gardent pas la demande
# réparée, qui quitte la liste.
PANNE = carte('c2-panne', '<div class="mini">102 [STD]</div><div style="font-size:20px;font-weight:600;color:var(--o-texte);'
                          'margin-top:4px">Chambre 102 — Climatiseur en panne</div><div class="mini">Demandé par : %s</div>'
                          '<div class="lg" style="margin-top:6px" id="c2-panne-prio">%s%s%s</div>'
                          % (e(NOM), icone('etoile'), icone('etoile'), icone('etoile')))
PANNES = vue_kanban('c2-pannes', 'Pannes & réparations', [
    ('Nouvelle demande', '1', [PANNE], 'c2-m1'), ('En cours', '0', [], 'c2-m2')], facettes=[(None, 'À faire')])
assert PANNES.endswith('</div></div></div>')
PANNES = PANNES[:-12] + plie('Réparé') + plie('Rebut') + '</div></div>'

REFUS = erreur_acces('c2-refus', 'Folio client (note de séjour)', 'aite.hotel.folio',
                     ['Gestion Hôtelière/Responsable', 'Gestion Hôtelière/Réception'])

ECRAN = fenetre('app-c2', 'Hôtel', MENUS_MUK['hotel_gouvernante'], [TABLEAU, PANNES], actif='Gouvernante',
                societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#B0655A', calques=TELEPHONE + INSPECTION + PROBLEME + REFUS)

# Le « ? » d'aide, comme celui de scenarios/t01_reception.py (.t1-aide) ; presentation.py réunit le CSS des chapitres.
# Une marge à droite des libellés de « Signaler un problème » : « La chambre ne peut pas être » ne touche plus la case.
CSS = '''
.c2-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }
#c2-as-pb .m-ch .l { padding-right: 16px; }
'''

CHAPITRE = {
    'court': 'Gouvernante',
    'poste': 'Gouvernante et équipières',
    'titre': 'Le tour des chambres',
    'personne': (NOM, ROLE),
    'objectif': "Voir l'état de chaque chambre, laisser les équipières travailler depuis leur téléphone, inspecter "
                "avec une checklist et signaler une panne qui bloque la vente.",
    'voix': "Deuxième chapitre : la gouvernante. Josiane suit l'état de chaque chambre, ses équipières travaillent "
            "depuis leur téléphone, et une panne retire la chambre de la vente.",
    'app': 'app-c2',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 'c2-tableau'},
    'etapes': [
        {'titre': 'Le tableau des chambres', 'texte': 'À nettoyer, en cours, à inspecter, propre : une colonne par état.',
         'voix': "Le tableau des chambres se lit sans explication : à nettoyer, en cours, à inspecter, propre. "
                 "Chaque carte dit l'état en une phrase, le client, l'arrivée prévue et l'équipière.",
         'gestes': [pause(0.6), anneau('#c2-col-1', d=1.2), anneau('#c2-103-hint', d=1.4), anneau('#c2-103', d=1.4),
                    pause(0.4)]},
        {'titre': 'Ma journée, sur le téléphone', 'texte': 'Un bouton par étape : « Je commence », puis « C\'est fait ».',
         'voix': "Clarisse, l'équipière, ouvre Ma journée sur son téléphone. Un bouton par étape : Je commence, puis "
                 "C'est fait. Comme l'inspection est exigée, la chambre passe à inspecter.",
         'gestes': [ouvrir('c2-tel'), pause(0.6), clic('#c2-t103-go'), etat('#c2-t103-etat', 'En cours', 'info'),
                    cacher('#c2-t103-go', d=0.2), montrer('#c2-t103-fin', d=0.3, y=0), pause(0.8),
                    clic('#c2-t103-fin'), etat('#c2-t103-etat', 'Terminé', 'vert'), pause(0.6), fermer('c2-tel'),
                    cacher('#c2-103', d=0.3), animer('#c2-103', {'display': 'block'}, {'display': 'none'}, d=0.05),
                    montrer('#c2-103i', d=0.4), texte('#c2-col-1-n', '(0)'),
                    texte('#c2-col-3-n', '(1)'), anneau('#c2-103i', d=1.4)]},
        {'titre': "L'inspection avec checklist", 'texte': 'Un point non conforme renvoie la chambre en nettoyage, en urgence.',
         'voix': "Pour inspecter, deux boutons suffisent : Conforme coche toute la checklist et clôt l'inspection, "
                 "À refaire renvoie la chambre en nettoyage. Ou bien la checklist de huit points : les serviettes manquent, le point reste décoché avec sa remarque, et la chambre retourne en "
                 "nettoyage, en urgence, chez la même équipière.",
         'gestes': [anneau('#c2-103-ok', d=0.9), anneau('#c2-103-ko', d=0.9), ouvrir('c2-as-insp'),
                    *[classe('#c2-ck%d' % i, ajouter=['on'], decale=0.05) for i in (0, 2, 3, 4, 5, 6, 7)],
                    choisir('c2-rq', 'serviettes manquantes'), anneau('#c2-rq', d=1.2), clic('#c2-valider'),
                    fermer('c2-as-insp'), cacher('#c2-103i', d=0.3),
                    # de retour « Recouche à faire », chez Clarisse (t07, « a_refaire »)
                    # (animer et non montrer : montrer cacherait la carte dès le début, immediateRender)
                    animer('#c2-103', {'display': 'none'}, {'display': 'block'}, d=0.05),
                    animer('#c2-103', {'autoAlpha': 0, 'y': 24}, {'autoAlpha': 1, 'y': 0}, d=0.4),
                    texte('#c2-col-3-n', '(0)'), texte('#c2-col-1-n', '(1)'), anneau('#c2-103', d=1.4)]},
        {'titre': 'Signaler une panne', 'texte': 'La chambre est retirée de la vente tant que la réparation n\'est pas faite.',
         'voix': "Dans la cent deux, libre ce jour-là, le climatiseur est en panne. La clé de la carte ouvre "
                 "Signaler un problème. Josiane passe l'urgence à Urgent, et la case « ne peut pas être vendue » "
                 "retire la chambre de la vente.",
         'gestes': [clic('#c2-102-cle'), ouvrir('c2-as-pb'), saisir('c2-pb', 'Climatiseur en panne'),
                    clic('#c2-et2', d=0.5), montrer('#c2-et2-on', d=0.2, y=0),
                    classe('#c2-bloque', ajouter=['coche']), anneau('#c2-bloque', d=1.2), clic('#c2-pb-ok'),
                    fermer('c2-as-pb'), classe('#c2-102', ajouter=['hors-service']),
                    texte('#c2-102-hint', 'Hors service — ne pas vendre'), montrer('#c2-102-panne', d=0.3, y=0),
                    # « À nettoyer » disparaît d'une chambre hors service (invisible="… or out_of_order").
                    animer('#c2-102-sale', {'display': 'inline-flex'}, {'display': 'none'}, d=0.05, avec=True),
                    anneau('#c2-102', d=1.6)]},
        {'titre': 'Pannes & réparations', 'texte': 'Priorité haute. Réparé : la chambre revient seule en vente, à nettoyer.',
         'voix': "La demande arrive dans Pannes et réparations, en priorité haute : trois étoiles. Quand le "
                 "technicien la passe à Réparé, elle quitte les demandes à faire, et la chambre revient toute seule en "
                 "vente, à nettoyer, avec une tâche de remise en service.",
         'gestes': [vue('c2-pannes'), pause(0.6), anneau('#c2-panne-prio', d=1.2), anneau('#c2-panne', d=1.0),
                    cacher('#c2-panne', d=0.4), texte('#c2-m1-n', '(0)'), pause(0.6),
                    # sur le tableau : la 102 quitte « Propre » (17) pour « À nettoyer » (2), sans badge de panne
                    cacher('#c2-102', d=0.05), animer('#c2-102', {'display': 'block'}, {'display': 'none'}, d=0.05),
                    animer('#c2-102s', {'display': 'none'}, {'display': 'block'}, d=0.05),
                    texte('#c2-col-1-n', '(2)'), texte('#c2-col-4-n', '(17)'), vue('c2-tableau'),
                    montrer('#c2-102s', d=0.4), anneau('#c2-102s', d=1.4), pause(0.3)]},
        {'titre': 'Ce qui ne la concerne pas', 'texte': 'Un lien vers un folio ? Odoo refuse et nomme les profils autorisés.',
         'voix': "Et si la gouvernante suit un lien vers un folio, Odoo refuse poliment : seuls les profils Réception "
                 "et Responsable y ont accès. Chacun reste dans son périmètre.",
         'gestes': [ouvrir('c2-refus'), pause(0.6), anneau('#c2-refus .refus', d=2.0), pause(0.6),
                    clic('#c2-refus-ok'), fermer('c2-refus')]},
    ],
}
