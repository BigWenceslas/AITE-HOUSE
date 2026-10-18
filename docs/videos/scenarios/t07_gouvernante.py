# -*- coding: utf-8 -*-
"""Tutoriel 7 — Gouvernante, ménage et maintenance (pilote du format marketing).

Sources : ROADMAP.md (F01 tableau des chambres, « Ma journée » mobile,
inspection checklist 8 points ; F02 signaler un problème, chambre hors
service, remise en vente automatique) ; libellés des écrans repris du
chapitre 2 de la vidéo de présentation (scenarios/c2_gouvernante.py, dont
l'en-tête cite les vues et modèles d'aite_housekeeping).
"""

import demo
from ecrans import APPS_PROFIL, fenetre_muk, navigateur
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, choisir, clic, classe, etat, fermer, montrer, ouvrir, pause, saisir, texte, vue
from scenarios import c2_gouvernante as c2

NOM, ROLE = demo.POSTES['gouvernante']
AMINA = demo.EQUIPIERES[0]

ECRAN = navigateur(fenetre_muk('app-t7', 'Hôtel', ['Gouvernante'], [c2.TABLEAU, c2.PANNES], actif='Gouvernante',
                               societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5',
                               apps=APPS_PROFIL['gouvernante'], app_active='Hôtel',
                               calques=c2.TELEPHONE + c2.INSPECTION + c2.PROBLEME))

TUTORIEL = {
    'slug': 't07-gouvernante',
    'profil': 't07_gouvernante',
    'numero': 7,
    'titre': 'Gouvernante, ménage et maintenance',
    'fonction': 'Gouvernante & maintenance',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Le tour des chambres',
        'question': 'Quelles chambres sont *vraiment* prêtes pour ce soir ?',
        'douleurs': [('telephone', "« La 102 est prête ? » — on appelle l'étage"), ('cahier', 'Le ménage noté dans un cahier'),
                     ('alerte', 'La clim en panne… et la chambre vendue'), ('interrogation', 'Qui a fait quelle chambre ?'),
                     ('sablier', "L'inspection faite de mémoire"), ('cle', 'La réparation oubliée sur un papier')],
        'voix': "Quelles chambres sont vraiment prêtes pour ce soir ? Entre les appels à l'étage, le cahier de ménage "
                "et la panne notée sur un bout de papier, la gouvernante court après l'information.",
    },
    'revelation': {
        'promesse': "Chaque chambre a son état, chaque équipière son téléphone, chaque panne son suivi.",
        'voix': "Avec Aïte haousse, chaque chambre a son état, chaque équipière son téléphone, et chaque panne son suivi.",
    },
    'temps': ['Organiser', 'Contrôler', 'Réparer'],
    'app': 'app-t7',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 'c2-tableau'},
    'bulles': {
        'b-etat': "Une phrase d'état par carte : on comprend sans formation.",
        'b-tel': 'Un bouton par étape, sur le téléphone de l\'équipière.',
        'b-check': 'Un point non conforme renvoie la chambre en nettoyage, en urgence.',
        'b-hs': 'Chambre retirée de la vente tant que la panne est ouverte.',
    },
    'reactions': {
        'r-fin': "La chambre revient en vente toute seule, avec sa tâche de remise en service.",
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le tableau des chambres', 'texte': 'À nettoyer, en cours, à inspecter, propre : une colonne par état.',
         'voix': "Le tableau des chambres se lit d'un coup d'œil : à nettoyer, en cours, à inspecter, propre. Chaque carte "
                 "dit l'état en une phrase, le client présent et l'arrivée prévue.",
         'gestes': [pause(0.4), anneau('#c2-col-1', d=1.0), zoom('#c2-203', s=1.6, d=0.8),
                    bulle('b-etat', '#c2-203-hint', cote='droite', d=2.6), pause(2.2), dezoom(d=0.6)]},
        {'temps': 0, 'titre': "Ma journée, sur le téléphone", 'texte': 'Je commence, puis C\'est fait : la chambre passe à inspecter.',
         'voix': "Amina, l'équipière, ouvre Ma journée sur son téléphone. Un bouton par étape : Je commence, puis C'est "
                 "fait. La chambre passe aussitôt à inspecter, sous les yeux de la gouvernante.",
         'gestes': [ouvrir('c2-tel'), zoom('#c2-tel', s=1.35, d=0.7), bulle('b-tel', '#c2-t102-go', cote='droite', d=2.2),
                    clic('#c2-t102-go'), etat('#c2-t102-etat', 'En cours', 'info'), cacher('#c2-t102-go', d=0.2),
                    montrer('#c2-t102-fin', d=0.3, y=0), pause(0.6), clic('#c2-t102-fin'),
                    etat('#c2-t102-etat', 'Terminé', 'vert'), pause(0.4), dezoom(d=0.6), fermer('c2-tel'),
                    cacher('#c2-102', d=0.3), montrer('#c2-102i', d=0.4), texte('#c2-col-1-n', '(1)'),
                    texte('#c2-col-3-n', '(1)'), anneau('#c2-102i', d=1.2)]},
        {'temps': 1, 'titre': "L'inspection en huit points", 'texte': 'Conforme, ou retour en nettoyage avec la remarque.',
         'voix': "Pour inspecter, la gouvernante passe la checklist de huit points. Les serviettes manquent : le point "
                 "reste décoché avec sa remarque, et la chambre repart en nettoyage, en urgence, chez la même équipière.",
         'gestes': [anneau('#c2-102-ok', d=0.8), ouvrir('c2-as-insp'),
                    *[classe('#c2-ck%d' % i, ajouter=['on'], decale=0.05) for i in (0, 2, 3, 4, 5, 6, 7)],
                    choisir('c2-rq', 'serviettes manquantes'), zoom('#c2-rq', s=1.45, d=0.6),
                    bulle('b-check', '#c2-valider', cote='bas', d=2.2), pause(1.0), dezoom(d=0.5), clic('#c2-valider'),
                    fermer('c2-as-insp'), cacher('#c2-102i', d=0.3), montrer('#c2-102r', d=0.4),
                    texte('#c2-col-3-n', '(0)'), texte('#c2-col-1-n', '(2)'), anneau('#c2-102r', d=1.0)]},
        {'temps': 2, 'titre': 'Signaler une panne', 'texte': 'Depuis la carte de la chambre, en trois champs.',
         'voix': "Dans la deux cent trois, le climatiseur est en panne. La clé de la carte ouvre Signaler un problème ; "
                 "la case ne peut pas être vendue retire la chambre de la vente.",
         'gestes': [clic('#c2-203-cle'), ouvrir('c2-as-pb'), saisir('c2-pb', 'Climatiseur en panne'),
                    classe('#c2-bloque', ajouter=['coche']), anneau('#c2-bloque', d=1.0), clic('#c2-pb-ok'),
                    fermer('c2-as-pb'), classe('#c2-203', ajouter=['hors-service']),
                    texte('#c2-203-hint', 'Hors service — ne pas vendre'), montrer('#c2-203-panne', d=0.3, y=0),
                    zoom('#c2-203', s=1.6, d=0.7), bulle('b-hs', '#c2-203', cote='gauche', d=2.4), pause(2.0),
                    dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Pannes & réparations', 'texte': 'Réparé : la chambre revient seule en vente.',
         'voix': "La demande arrive dans l'application Maintenance. Quand le technicien la passe à Réparé, la chambre "
                 "revient toute seule en vente, avec une tâche de remise en service.",
         'gestes': [vue('c2-pannes'), pause(0.5), anneau('#c2-panne', d=1.0), cacher('#c2-panne', d=0.3),
                    montrer('#c2-panne-r', d=0.4), texte('#c2-m1-n', '(0)'), texte('#c2-m3-n', '(1)'),
                    anneau('#c2-panne-r', d=1.2), reaction('r-fin', d=3.0), pause(2.4)]},
    ],
    'resultats': {
        'titre': "Un hôtel où chaque chambre dit où elle en est",
        'cartes': [
            {'valeur': '8', 'compter': 8, 'unite': 'points', 'icone': 'coche',
             'texte': "de contrôle dans la checklist d'inspection, modifiables sans code"},
            {'valeur': '1', 'compter': 1, 'unite': 'bouton', 'icone': 'telephone',
             'texte': "par étape sur le téléphone de l'équipière : Je commence, C'est fait"},
            {'valeur': 'Auto', 'unite': '', 'icone': 'bouclier',
             'texte': 'Chambre en panne retirée de la vente, puis remise en vente à la réparation'},
        ],
        'voix': "Huit points de contrôle, un bouton par étape, et une chambre en panne retirée de la vente tant qu'elle "
                "n'est pas réparée : la gouvernante pilote, le terrain suit.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'La réservation en ligne',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 4, 'apres': 4.5},
}
