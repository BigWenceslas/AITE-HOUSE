# -*- coding: utf-8 -*-
"""Chapitre 2 — Le tour des chambres.

Source : fiche de recette n° 2 « Le tour des chambres » (gouvernante :
tâches du jour, recouche démarrée puis terminée, état des chambres, refus
d'accès aux folios), complétée par le cahier de recette, domaine P
(aite_housekeeping : tableau des chambres, « Ma journée » sur téléphone,
inspection avec checklist, panne qui bloque la chambre, remise en vente).

Libellés relevés dans : aite_housekeeping/views/hotel_room_views.xml (carte
du tableau des chambres, boutons « Commencer », « Terminé », « Conforme »,
« À refaire », « À nettoyer », clé « Signaler un problème »),
models/hotel_room.py (_hint_for : « À nettoyer », « À inspecter par la
gouvernante », « Propre — prête pour l'arrivée », « Hors service — ne pas
vendre »), views/housekeeping_task_views.xml et models/housekeeping_task.py
(« Ma journée », « Je commence », « C'est fait », « Passer la checklist »,
libellés des tâches, inspection « Tout cocher » / « Valider l'inspection »),
data/housekeeping_data.xml (les 8 points de contrôle),
wizard/report_issue_wizard*.py|xml (« Signaler un problème »). Le refus
d'accès reprend le message d'Odoo 18 en français et les groupes de
aite_hotel_management/security/hotel_security.xml.
"""

import demo
from ecrans import (assistant, bouton, carte, e, entree, erreur_acces, fenetre, icone, interrupteur, m_champ, m_champs,
                    telephone, vue_kanban)
from moteur import anneau, cacher, choisir, clic, classe, etat, fermer, montrer, ouvrir, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['gouvernante']
AMINA, ROSE = demo.EQUIPIERES


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
C102 = carte_chambre('c2-102', '102', 'À nettoyer', 'Standard · Rez-de-chaussée', equipiere=AMINA,
                     boutons=[bouton('c2-102-go', 'Commencer', 'primaire', 'play')])
C105 = carte_chambre('c2-105', '105', 'À nettoyer', 'Standard · Rez-de-chaussée', equipiere=ROSE,
                     boutons=[bouton('c2-105-go', 'Commencer', 'primaire', 'play')])
C102_INSP = carte_chambre('c2-102i', '102', 'À inspecter par la gouvernante', 'Standard · Rez-de-chaussée',
                          equipiere=AMINA, boutons=[bouton('c2-102-ok', 'Conforme', 'vert', 'coche'),
                                                    bouton('c2-102-ko', 'À refaire', 'rouge-contour')],
                          classe_='masque')
C102_REDO = carte_chambre('c2-102r', '102', 'À nettoyer', 'Standard · Rez-de-chaussée', equipiere=AMINA,
                          boutons=[bouton('c2-102r-go', 'Commencer', 'primaire', 'play')], classe_='masque')
C201 = carte_chambre('c2-201', '201', 'Nettoyage en cours', 'Confort · 1er étage', client='Martin Ebode', equipiere=ROSE,
                     boutons=[bouton('c2-201-done', 'Terminé', 'vert', 'coche')])
C203 = carte_chambre('c2-203', '203', 'Propre — prête pour l\'arrivée', 'Confort · 1er étage', client='Joël Kamga',
                     arrivee='Arrivée prévue 14h00', boutons=[bouton('c2-203-sale', 'À nettoyer', 'blanc')],
                     panne='masque')
C204 = carte_chambre('c2-204', '204', 'Propre — client présent', 'Confort · 1er étage', client=demo.CLIENT,
                     boutons=[bouton('c2-204-sale', 'À nettoyer', 'blanc')])

TABLEAU = vue_kanban('c2-tableau', 'Tableau des chambres', [
    ('À nettoyer', '2', ['<div class="pile">%s%s</div>' % (C102, C102_REDO), C105], 'c2-col-1'),
    ('Nettoyage en cours', '1', [C201], 'c2-col-2'),
    ('À inspecter', '0', [C102_INSP], 'c2-col-3'),
    ('Propre', '2', [C203, C204], 'c2-col-4')], initiale=True)

# ------------------------------------------------------ Ma journée (téléphone) --
def tache_tel(ident, chambre, libelle, client, etat_, genre, bouton_html):
    return ('<div class="tel-carte" id="%s"><div class="h"><span>Chambre %s</span><span class="puce %s" id="%s-etat">%s</span></div>'
            '<div class="s">%s</div>%s%s</div>'
            % (ident, e(chambre), genre, ident, e(etat_), e(libelle),
               '<div class="p">%s%s</div>' % (icone('personne'), e(client)) if client else '', bouton_html))


TACHE_102 = tache_tel('c2-t102', '102 [STD]', 'Recouche complète (départ)', None, 'À faire', 'orange',
                      '<div class="tel-bt violet" id="c2-t102-go">%sJe commence</div>'
                      '<div class="tel-bt vert masque" id="c2-t102-fin" style="margin-top:-54px">%sC\'est fait</div>'
                      % (icone('play'), icone('coche')))
TACHE_204 = tache_tel('c2-t204', '204 [CFT]', 'Ménage quotidien (client présent)', demo.CLIENT, 'À faire', 'orange',
                      '<div class="tel-bt violet">%sJe commence</div>' % icone('play'))
TELEPHONE = telephone('c2-tel', 'Ma journée', TACHE_102 + TACHE_204)

# ------------------------------------------------------------- Inspection --
POINTS = ['Lit refait, draps propres', 'Salle de bain nettoyée, serviettes changées', 'Sol balayé et lavé',
          'Poubelles vidées', 'Savon, papier, eau de courtoisie réapprovisionnés', 'Minibar vérifié et recomplété',
          'Climatiseur, lumières et télécommande fonctionnent', 'Aucune odeur, aucun objet oublié']
LIGNES = ''.join('<div class="check"><span>%s</span><span class="ell">%s</span><span class="rq">%s</span></div>'
                 % (interrupteur('c2-ck%d' % i), e(p),
                    '<span id="c2-rq"><span class="ph" id="c2-rq-ph"></span><span class="val" id="c2-rq-val"></span></span>'
                    if i == 1 else '')
                 for i, p in enumerate(POINTS))
INSPECTION = assistant('c2-as-insp', 'Inspection — chambre 102', (
    '<div style="font-size:32px;margin-bottom:6px">Chambre <span style="color:var(--o-prim)">102 [STD]</span></div>'
    '<div class="m-aide">Inspection — passer la checklist · contrôle <span id="c2-ctrl">0 / 8</span><br>'
    'Cochez chaque point conforme. Un point non coché renverra la chambre en nettoyage avec votre remarque.</div>'
    '<div class="check tete"><span>Conforme</span><span>Point de contrôle</span><span>Remarque</span></div>' + LIGNES),
    [('c2-tout', 'Tout cocher', 'gris', None), ('c2-valider', "Valider l'inspection", 'primaire', None),
     ('c2-fermer', 'Fermer', 'gris', None)], haut=26, largeur=1260)

# ------------------------------------------------------ Signaler un problème --
PROBLEME = assistant('c2-as-pb', 'Signaler un problème', m_champs([
    m_champ('Chambre', e('203 [CFT]')),
    m_champ('Quel est le problème ?', entree('c2-pb', 'Ex. : climatiseur en panne, fuite lavabo…')),
    m_champ('Urgence', '<span class="etoiles">%s%s%s</span>' % (icone('etoile'), icone('etoile'),
                                                                '<span class="ico" style="opacity:.25">%s</span>'
                                                                % '<svg viewBox="0 0 24 24" fill="#6C757D"><path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg>')),
    m_champ("La chambre ne peut pas être vendue en l'état", '<span class="case" id="c2-bloque"><i></i></span>'),
    m_champ('Précisions', entree('c2-precis', 'Précisions utiles au technicien'))]),
    [('c2-pb-ok', 'Envoyer à la maintenance', 'primaire', None), ('c2-pb-non', 'Annuler', 'gris', None)], haut=120)

# ------------------------------------------------------ Pannes & réparations --
PANNE = carte('c2-panne', '<div class="mini">203 [CFT]</div><div style="font-size:20px;font-weight:600;color:var(--o-texte);'
                          'margin-top:4px">Chambre 203 — Climatiseur en panne</div><div class="mini">Demandé par : %s</div>'
                          '<div class="lg" style="margin-top:6px">%s%s</div>' % (e(NOM), icone('etoile'), icone('etoile')))
PANNE_REPAREE = carte('c2-panne-r', '<div class="mini">203 [CFT]</div><div style="font-size:20px;font-weight:600;'
                                    'color:var(--o-texte);margin-top:4px">Chambre 203 — Climatiseur en panne</div>'
                                    '<div class="mini">Demandé par : %s</div>' % e(NOM), 'masque')
PANNES = vue_kanban('c2-pannes', 'Pannes & réparations', [
    ('Nouvelle demande', '1', [PANNE], 'c2-m1'), ('En cours', '0', [], 'c2-m2'),
    ('Réparé', '0', [PANNE_REPAREE], 'c2-m3')], facettes=[(None, 'À faire')])

REFUS = erreur_acces('c2-refus', 'Folio client (note de séjour)', 'aite.hotel.folio',
                     ['Gestion Hôtelière/Responsable', 'Gestion Hôtelière/Réception'])

ECRAN = fenetre('app-c2', 'Hôtel', ['Gouvernante'], [TABLEAU, PANNES], actif='Gouvernante', societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#B0655A', calques=TELEPHONE + INSPECTION + PROBLEME + REFUS)

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
    'vues_initiales': {'odoo': 'c2-tableau'},
    'etapes': [
        {'titre': 'Le tableau des chambres', 'texte': 'À nettoyer, en cours, à inspecter, propre : une colonne par état.',
         'voix': "Le tableau des chambres se lit sans explication : à nettoyer, en cours, à inspecter, propre. "
                 "Chaque carte dit l'état en une phrase, le client présent, l'arrivée prévue et l'équipière.",
         'gestes': [pause(0.6), anneau('#c2-col-1', d=1.2), anneau('#c2-203-hint', d=1.4), anneau('#c2-203', d=1.4),
                    pause(0.4)]},
        {'titre': 'Ma journée, sur le téléphone', 'texte': 'Un bouton par étape : « Je commence », puis « C\'est fait ».',
         'voix': "Amina, l'équipière, ouvre Ma journée sur son téléphone. Un bouton par étape : Je commence, puis "
                 "C'est fait. Comme l'inspection est exigée, la chambre passe à inspecter.",
         'gestes': [ouvrir('c2-tel'), pause(0.6), clic('#c2-t102-go'), etat('#c2-t102-etat', 'En cours', 'info'),
                    cacher('#c2-t102-go', d=0.2), montrer('#c2-t102-fin', d=0.3, y=0), pause(0.8),
                    clic('#c2-t102-fin'), etat('#c2-t102-etat', 'Terminé', 'vert'), pause(0.6), fermer('c2-tel'),
                    cacher('#c2-102', d=0.3), montrer('#c2-102i', d=0.4), texte('#c2-col-1-n', '(1)'),
                    texte('#c2-col-3-n', '(1)'), anneau('#c2-102i', d=1.4)]},
        {'titre': "L'inspection avec checklist", 'texte': 'Un point non conforme renvoie la chambre en nettoyage, en urgence.',
         'voix': "Pour inspecter, deux boutons suffisent : Conforme ou À refaire. Ou bien la checklist de huit points : "
                 "les serviettes manquent, le point reste décoché avec sa remarque, et la chambre retourne en "
                 "nettoyage, en urgence, chez la même équipière.",
         'gestes': [anneau('#c2-102-ok', d=0.9), anneau('#c2-102-ko', d=0.9), ouvrir('c2-as-insp'),
                    *[classe('#c2-ck%d' % i, ajouter=['on'], decale=0.05) for i in (0, 2, 3, 4, 5, 6, 7)],
                    choisir('c2-rq', 'serviettes manquantes'), anneau('#c2-rq', d=1.2), clic('#c2-valider'),
                    fermer('c2-as-insp'), cacher('#c2-102i', d=0.3), montrer('#c2-102r', d=0.4),
                    texte('#c2-col-3-n', '(0)'), texte('#c2-col-1-n', '(2)'), anneau('#c2-102r', d=1.4)]},
        {'titre': 'Signaler une panne', 'texte': 'La chambre est retirée de la vente tant que la réparation n\'est pas faite.',
         'voix': "Dans la chambre deux cent trois, le climatiseur est en panne. La clé de la carte ouvre Signaler un "
                 "problème. La case « ne peut pas être vendue » retire la chambre de la vente.",
         'gestes': [clic('#c2-203-cle'), ouvrir('c2-as-pb'), saisir('c2-pb', 'Climatiseur en panne'),
                    classe('#c2-bloque', ajouter=['coche']), anneau('#c2-bloque', d=1.2), clic('#c2-pb-ok'),
                    fermer('c2-as-pb'), classe('#c2-203', ajouter=['hors-service']),
                    texte('#c2-203-hint', 'Hors service — ne pas vendre'), montrer('#c2-203-panne', d=0.3, y=0),
                    anneau('#c2-203', d=1.6)]},
        {'titre': 'Pannes & réparations', 'texte': 'Réparé : la chambre revient seule en vente, à nettoyer.',
         'voix': "La demande arrive dans l'application Maintenance. Quand le technicien la passe à Réparé, la chambre "
                 "revient toute seule en vente, avec une tâche de remise en service.",
         'gestes': [vue('c2-pannes'), pause(0.6), anneau('#c2-panne', d=1.2), cacher('#c2-panne', d=0.3),
                    montrer('#c2-panne-r', d=0.4), texte('#c2-m1-n', '(0)'), texte('#c2-m3-n', '(1)'),
                    anneau('#c2-panne-r', d=1.4), pause(0.3)]},
        {'titre': 'Ce qui ne la concerne pas', 'texte': 'Un lien vers un folio ? Odoo refuse et nomme les profils autorisés.',
         'voix': "Et si la gouvernante suit un lien vers un folio, Odoo refuse poliment : seuls les profils Réception "
                 "et Responsable y ont accès. Chacun reste dans son périmètre.",
         'gestes': [ouvrir('c2-refus'), pause(0.6), anneau('#c2-refus .refus', d=2.0), pause(0.6),
                    clic('#c2-refus-ok'), fermer('c2-refus')]},
    ],
}
