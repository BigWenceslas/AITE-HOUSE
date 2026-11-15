# -*- coding: utf-8 -*-
"""Tutoriel 16 — Service à table contrôlé : la mise en place.

Le premier des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant,
aite_pos_analytics, aite_pos_analytics_hr). Un restaurant SANS hôtel
(aite_pos_restaurant/__manifest__.py:119, 126 ; docs/INSTALLATION.md §9) :
autre établissement, autre société et autre barre d'applications que les
tutoriels 1 à 15 (demo.RESTO, demo.SOCIETE_RESTO ; barres relevées sur la
base « restaurant seul », ecrans.APPS_PROFIL['resto_*']).

Personnages : l'administrateur d'Odoo (AITE, demo.ADMIN_RESTO) pour les
réglages du Point de Vente, qui lui sont réservés (point_of_sale/views/
res_config_settings_views.xml:21, groups="point_of_sale.group_pos_manager"
et menu « Paramètres » réservé à base.group_system ; docs/INSTALLATION.md
§9.5 : « réservés à l'administrateur d'Odoo (AITE) ») ; puis la manager du
restaurant (demo.POSTES_RESTO['manager'], Edwige Bilongo), gestionnaire des
employés et administratrice du Point de Vente (INSTALLATION.md §9.5), pour
la fiche employé et les motifs. La pastille passe de l'un à l'autre à
l'étape 3 (ecrans.css_personnage). Storyboard : scratchpad videos_resto/
storyboards/t16.md (adapté : voir « Écarts au storyboard » plus bas).

Abréviations : R/ = addons/aite_pos_restaurant/ ; O/ = ../odoo18/addons/.
Toutes les phrases du produit sont relues dans le code au chargement
(``source``, analyse du fichier Python sans Odoo) : une phrase changée dans
le module fait échouer la construction de la vidéo au lieu de la rendre
fausse.

Écrans et libellés :

1-2. Point de Vente → Configuration → Paramètres (compte de l'administrateur,
   avatar « A », barre ecrans.APPS_PROFIL['resto_admin']) ; modèle visuel :
   captures/restaurant/25. Panneau « Enregistrer », « Ignorer »,
   « Paramètres », « Rechercher… » (O/web/i18n/fr.po:5629-5630, 2205-2206,
   5761-5762) ; barre de gauche : Paramètres généraux, Inventaire,
   Facturation, Employés, Point de Vente (capture 25) ; bande d'en-tête
   « Point de Vente », caisse « Restaurant », « + Nouvelle boutique »
   (O/point_of_sale/i18n/fr.po:5661-5662, 167-168 ; NOM_CAISSE,
   R/models/pos_config.py:81 ; O/web/…/settings/setting_header.xml:4) ;
   bloc « Mode restaurant » (fr.po:6680-6681). Réglages, dans l'ordre de la
   vue (R/views/res_config_settings_views.xml:28-61 posés après « Est un
   bar/restaurant », puis O/pos_restaurant/views/res_config_settings_views.
   xml:9-34) :
   - « Est un bar/restaurant » ☑ (fr.po:3792-3793) ;
   - « Service à table contrôlé » ☑ et AIDE_MODE (R/models/pos_config.py:
     13-22, 90-91) ; cochée d'office sur la caisse posée à l'installation
     (pos_config.py:192-199, REGLAGES_DU_MODE) ;
   - « Délai avant l'orange (minutes) », 60, et sa phrase (pos_config.py:
     52-57, 70-78, 100-102 ; R/models/res_config_settings.py:21-29) ;
   - « Autoriser la vente sans table » ☐ et AIDE_VENTE_SANS_TABLE
     (pos_config.py:35, 40-48, 92-94) ;
   - « Refuser la vente des produits épuisés » ☑ et AIDE_REFUS_EPUISE
     (pos_config.py:37, 59-67, 103-105) ;
   - « Plan des salles & des tables » (?), « Créer un plan de salle et
     attribuer des commandes à des tables », « Salles », étiquette « Salle »,
     lien « Salles » (O/pos_restaurant/i18n/fr.po:551-552, 400-401, 546-547 ;
     NOM_SALLE, pos_config.py:82, 200) ;
   - « Manger sur place / À emporter » ☐ et sa phrase (fr.po:427-428,
     155-163) ; « Impression du reçu avant le paiement » ☑ (posé par la
     case : iface_printbill, pos_config.py:32) et « Autoriser l'impression
     du reçu avant le paiement » (fr.po:422-423, 178-179).
   Le défilement s'arrête sur cette rangée ; la suivante est posée sous le
   bord de la page, pour que la page continue comme dans Odoo : « Autoriser
   le partage d'addition » ☑ (posé par la case : iface_splitbill,
   pos_config.py:31), « ? » de la documentation, « Partager le total ou les
   lignes de commande » (fr.po:167-168, 1147-1148 ; O/pos_restaurant/views/
   res_config_settings_views.xml:35-37). À côté d'elle viendrait
   « Réservation de table », marquée « Enterprise » sur Community (O/web/
   static/src/webclient/settings_form_view/highlight_text/
   form_label_highlight_text.xml:6-7), qu'on ne montre pas. Le filet d'un
   réglage ne descend pas plus bas que lui (capture 25).
3-4. Employés → la fiche de Loïc (compte de la manager, avatar « E », barre
   ecrans.APPS_PROFIL['resto_manager'], menus ecrans.MENUS_MUK['employes']) ;
   modèle visuel : captures/restaurant/24. Fiche d'Odoo (O/hr/views/
   hr_employee_views.xml:58-110 ; libellés de la capture 24) et groupe
   « Caisse du restaurant » (R/views/hr_employee_views.xml:11-44) : « Niveau
   en caisse » et ses valeurs (R/models/hr_employee.py:34-36 ;
   R/models/regles.py:23-28), sa phrase AIDE_NIVEAU (hr_employee.py:11-18),
   « Code caisse » et AIDE_CODE (hr_employee.py:19-24). Le code est proposé
   dès qu'on choisit un niveau, s'il n'y en a pas encore (hr_employee.py:
   69-79) ; la vidéo ouvre la fiche de Loïc, enregistrée sans niveau (pas
   la création d'une fiche : voir les écarts au storyboard). Boutons
   d'enregistrement de la fiche modifiée (nuage, croix :
   O/web/static/src/views/form/form_status_indicator/
   form_status_indicator.xml:6-26). Compteur « 5 / 6 » : le module Employés
   crée aussi la fiche du compte administrateur (O/hr/data/hr_data.xml:9-16),
   rangée avant l'équipe (relevé sur la base du restaurant : 6 fiches).
5. Point de Vente → Configuration → Motifs d'annulation (compte de la
   manager ; menu réservé au responsable du Point de Vente,
   R/views/restaurant_menus.xml:21-24 ; relevé sur la base du restaurant).
   Liste modifiable « Motifs d'annulation » (R/views/restaurant_motif_views.
   xml:11-16, 32) : poignée, « Motif », « Précision obligatoire »
   (R/models/restaurant_motif.py:20-25) ; les cinq motifs posés d'office,
   « Autre » seul avec la précision (R/data/restaurant_motif_data.xml:8-28,
   noupdate="1") ; « Ajouter une ligne » (O/web/i18n/fr.po:657-658).
   On y passe par un fondu, sans cliquer sur l'application (le clic ouvrirait
   le tableau de bord du Point de Vente, qu'on ne rejoue pas) ; l'anneau
   désigne « Configuration » dans la barre, et la légende donne le chemin.
6. La caisse plein écran, plan « Salle » verrouillé, caisse pas encore
   ouverte : bandeau « La caisse est fermée… » et « Ouvrir la caisse »
   (R/static/src/utils/messages.js:98-100 ; R/static/src/overrides/
   floor_screen.xml:21-26), fenêtre « Votre code pour ouvrir la caisse »
   (messages.js:74 ; R/static/src/components/code_popup/code_popup.xml:
   10-37), légende (messages.js:150-163). Modèle visuel : capture 01 : la
   fenêtre s'ouvre sous la ligne de texte du bandeau, qui reste lisible
   (ecrans.resto_code, haut=205) ; elle s'ouvre seule à l'affichage du plan,
   et par le bouton « Ouvrir la caisse » (R/static/src/overrides/
   floor_screen.js:5, 51-53), que la vidéo montre. Les douze tables : le
   plan que le manager saisit avant le premier service (l'installation ne
   pose qu'une salle d'une table : INSTALLATION.md §9.4 ; §9.6, point 3),
   comme la voix le dit.

Règles dites par la voix et les bulles :
- la case pose la connexion par code, le contrôle des prix, les remises
  désactivées (REGLAGES_DU_MODE, pos_config.py:26-38 ; phrase de la case) ;
- « à régler avant la première ouverture » : INSTALLATION.md §9.4 (la
  phrase « Se change seulement caisse fermée » est trompeuse : écart) ;
- la phrase du délai suit le nombre tapé : res_config_settings.py:21-29,
  recette R69 ;
- un code déjà pris est refusé sans nommer le collègue : hr_employee.py:
  42-67 (message « Le code … est déjà celui d'un autre employé »), R03 ;
- sans niveau, l'employé n'apparaît pas sur la caisse : AIDE_NIVEAU,
  hr_employee.py:107-111 ;
- aucun courriel demandé aux employés : INSTALLATION.md §9.6, notes de
  version :84 ;
- les motifs : aide de l'action (restaurant_motif_views.xml:38) ; une mise
  à niveau ne les remet pas (noupdate) ;
- le plan est l'écran de repos, tout retour au plan oublie l'employé :
  notes de version §1, règle 2 (docs/NOTES_DE_VERSION_restaurant_lot1.md:
  40-42) ;
- ce qui reste au manager avant le premier service (la carte, le plan de
  salle, le stock de départ) : INSTALLATION.md §9.6, points 2 à 4 ; la
  phrase du refus des épuisés (pos_config.py:65-66). La vidéo ne dit donc
  pas que la caisse est « prête » : les règles sont posées ;
- « avec ses deux modes de paiement et sa salle » : INSTALLATION.md §9.4
  (Espèces, Mobile Money, salle « Salle ») ;
- l'addition peut s'imprimer avant le paiement : iface_printbill posé par la
  case (pos_config.py:32 ; AIDE_MODE : « partage et impression de
  l'addition »).

Écarts au storyboard (décidés en construisant le socle, puis à la relecture) :
- l'équipe de la série est celle de demo.EQUIPE_RESTO (Edwige, Prisca, Loïc,
  Inès, Landry) : « Yannick », « Nathalie », « Onana » et « Abena » sont
  déjà dans le dépôt ;
- étape 2 : pas de coupe vers le bloc « Paiement » (sa deuxième rangée
  n'est pas relevée) : le bloc « Mode restaurant » défile jusqu'à
  « Impression du reçu avant le paiement » ;
- étape 3 : la fiche existante de Loïc, sans niveau, comme la capture 24
  (l'en-tête, le bouton intelligent et l'avatar d'une fiche neuve ne sont
  relevés sur aucune capture) ;
- étape 5 : un fondu vers la liste des motifs (le tableau de bord du Point
  de Vente n'est pas rejoué) ;
- la fin dit « Caisse de restaurant sur Odoo 18 » (demo.SOUS_MARQUE_RESTO)
  au lieu de « Suite hôtelière sur Odoo 18 ».

Le garde-fou relit les phrases à la fois dans les constantes Python et dans
les vues XML (R/views/res_config_settings_views.xml, R/views/
hr_employee_views.xml) : la construction échoue si l'une change sans
l'autre.
"""

import ast
import os
import xml.etree.ElementTree as ET

import demo
from ecrans import (APPS_PROFIL, MENUS_MUK, TITRES_RESTO, bloc_reglages, css_personnage, e, etiquettes, fenetre_muk,
                    fenetre_resto, fiche_employe, lien_fleche, navigateur, page_reglages, reglage, resto_code, resto_plan,
                    resto_salle, vue_liste)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, choisir, clic, classe, curseur, defiler, montrer, ouvrir, pause, survol

R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'addons', 'aite_pos_restaurant'))


def source(relatif, nom):
    """Une constante de texte du module, lue dans son fichier (analyse, sans importer Odoo)."""
    with open(os.path.join(R, relatif), encoding='utf-8') as f:
        arbre = ast.parse(f.read())
    for noeud in arbre.body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t16 : %s introuvable dans %s' % (nom, relatif))


AIDE_MODE = source('models/pos_config.py', 'AIDE_MODE')
AIDE_VENTE_SANS_TABLE = source('models/pos_config.py', 'AIDE_VENTE_SANS_TABLE')
AIDE_REFUS_EPUISE = source('models/pos_config.py', 'AIDE_REFUS_EPUISE')
AIDE_DELAI = source('models/pos_config.py', 'AIDE_DELAI').format(delai='%d minutes' % demo.DELAI_ORANGE)
AIDE_NIVEAU = source('models/hr_employee.py', 'AIDE_NIVEAU')
AIDE_CODE = source('models/hr_employee.py', 'AIDE_CODE')
NIVEAUX = [lib for _cle, lib in source('models/regles.py', 'NIVEAUX')]
assert NIVEAUX == ['Serveur', 'Caissière', 'Chef de salle ou superviseur', 'Manager']
assert source('models/pos_config.py', 'NOM_CAISSE') == demo.CAISSE_RESTO
assert source('models/pos_config.py', 'NOM_SALLE') == demo.SALLE_RESTO
with open(os.path.join(R, 'data', 'restaurant_motif_data.xml'), encoding='utf-8') as _f:
    _motifs = _f.read()
assert all('<field name="name">%s</field>' % m in _motifs for m in demo.MOTIFS_RESTO)


def _une_ligne(texte):
    return ' '.join((texte or '').split())


# Ce que l'écran affiche vient des VUES (attribut ``help`` des réglages, texte de la fiche employé), qui recopient
# les constantes Python : les deux sont relus, et la construction échoue s'ils divergent (une phrase changée dans
# la vue seule ne passe pas). R/views/res_config_settings_views.xml:29-60 ; R/views/hr_employee_views.xml:13-42.
_REGLAGES_XML = {n.get('id'): n
                 for n in ET.parse(os.path.join(R, 'views', 'res_config_settings_views.xml')).iter('setting')}
for _id_xml, _titre, _aide in (('aite_mode_restaurant', 'Service à table contrôlé', AIDE_MODE),
                               ('aite_delai_alerte', "Délai avant l'orange (minutes)", None),
                               ('aite_vente_sans_table', 'Autoriser la vente sans table', AIDE_VENTE_SANS_TABLE),
                               ('aite_refus_epuise', 'Refuser la vente des produits épuisés', AIDE_REFUS_EPUISE)):
    assert _REGLAGES_XML[_id_xml].get('string') == _titre, ('t16 : libellé changé dans la vue', _id_xml)
    assert _une_ligne(_REGLAGES_XML[_id_xml].get('help')) == (_aide or ''), \
        ('t16 : phrase changée dans la vue', _id_xml)
_FICHE_XML = [_une_ligne(''.join(n.itertext()))
              for n in ET.parse(os.path.join(R, 'views', 'hr_employee_views.xml')).iter('div')
              if n.get('class') == 'text-muted']
assert _FICHE_XML == [AIDE_NIVEAU, AIDE_CODE], 't16 : phrase de la fiche employé changée dans la vue'

# La phrase sous « Niveau en caisse », découpée en ses cinq phrases (jointes par une espace : le texte reste
# celui du code) pour les désigner l'une après l'autre.
PHRASES_NIVEAU = [p if p.endswith('.') else p + '.' for p in AIDE_NIVEAU.split('. ')]
assert ' '.join(PHRASES_NIVEAU) == AIDE_NIVEAU and len(PHRASES_NIVEAU) == 5

ADMIN, ROLE_ADMIN, INITIALE_ADMIN = demo.ADMIN_RESTO
MANAGER, ROLE_MANAGER = demo.POSTES_RESTO['manager']
LOIC = next(e_ for e_ in demo.EQUIPE_RESTO if e_[0] == demo.POSTES_RESTO['serveur'][0])
NOM_LOIC, CODE_LOIC = LOIC[1], LOIC[3]
# Le compteur de la fiche de Loïc : les fiches sont rangées par nom (O/hr/models/hr_employee.py:29, _order = 'name')
# et le module Employés crée aussi celle du compte administrateur, au nom de son contact (O/hr/data/hr_data.xml:9-16,
# employee_admin ; relevé sur la base du restaurant : 6 fiches, dont celle de l'administrateur). Elle se range avant
# l'équipe (« AITE Consulting » ici, « Administrator » sur la base) : Loïc est la 5ᵉ des 6. Elle n'est jamais
# montrée.
FICHES = sorted([ADMIN] + [x[1] for x in demo.EQUIPE_RESTO])
RANG_LOIC = FICHES.index(NOM_LOIC) + 1
assert (RANG_LOIC, len(FICHES)) == (5, 6)

# ====================================================== 1-2. les réglages --
SALLE_HTML = ('<div class="rg-ligne"><span>Salles</span>%s</div>%s'
              % (etiquettes([demo.SALLE_RESTO]), lien_fleche('Salles')))
REGLAGES = bloc_reglages('Mode restaurant', [
    reglage('t16-ebr', 'Est un bar/restaurant', case=True),
    reglage('t16-stc', 'Service à table contrôlé', aide=AIDE_MODE, case=True),
    reglage('t16-delai', "Délai avant l'orange (minutes)",
            contenu='<div class="rg-champ" id="t16-delai-v">%d</div><div class="rg-aide" id="t16-delai-phrase">%s</div>'
                    % (demo.DELAI_ORANGE, e(AIDE_DELAI))),
    reglage('t16-vst', 'Autoriser la vente sans table', aide=AIDE_VENTE_SANS_TABLE, case=False),
    reglage('t16-refus', 'Refuser la vente des produits épuisés', aide=AIDE_REFUS_EPUISE, case=True),
    reglage('t16-plan-sal', 'Plan des salles & des tables',
            aide='Créer un plan de salle et attribuer des commandes à des tables', contenu=SALLE_HTML, point=True),
    reglage('t16-emporter', 'Manger sur place / À emporter',
            aide="Ajuster la taxe selon que les clients mangent sur place ou qu'ils optent pour un plat à emporter.",
            case=False),
    reglage('t16-impression', 'Impression du reçu avant le paiement',
            aide="Autoriser l'impression du reçu avant le paiement", case=True),
    # La rangée suivante, que le défilement laisse sous le bord de la page (la page continue, comme dans Odoo) :
    # « Autoriser le partage d'addition », cochée par la case (iface_splitbill, R/models/pos_config.py:31).
    reglage('t16-partage', "Autoriser le partage d'addition", aide='Partager le total ou les lignes de commande',
            case=True, point=True),
], identifiant='t16-bloc')
PAGE = page_reglages('t16-rg', [('Paramètres généraux', 'parametres'), ('Inventaire', 'inventaire'),
                                ('Facturation', 'facturation'), ('Employés', 'employes'),
                                ('Point de Vente', 'point-de-vente')],
                     'Point de Vente', ('Point de Vente', demo.CAISSE_RESTO, '+ Nouvelle boutique'), [REGLAGES],
                     initiale=True)
ADMIN_ECRAN = fenetre_muk('t16-adm', 'Point de Vente', MENUS_MUK['point_de_vente'], [PAGE], actif='Configuration',
                          societe=demo.SOCIETE_RESTO, initiale=INITIALE_ADMIN, avatar=demo.AVATARS_RESTO['A'],
                          apps=APPS_PROFIL['resto_admin'], app_active='Point de Vente')

# ================================================= 3-4. la fiche employé --
FICHE = fiche_employe('t16-fe', NOM_LOIC, NOM_LOIC[0], demo.AVATARS_RESTO[NOM_LOIC], pager='%d / %d' % (
    RANG_LOIC, len(FICHES)), aide_niveau=PHRASES_NIVEAU, aide_code=AIDE_CODE, options=[''] + NIVEAUX,
    initiale_vue=True)
EMPLOYES = fenetre_muk('t16-emp', 'Employés', MENUS_MUK['employes'], [FICHE], actif='Employés',
                       societe=demo.SOCIETE_RESTO, initiale=MANAGER[0], avatar=demo.AVATARS_RESTO[MANAGER.split()[0]],
                       apps=APPS_PROFIL['resto_manager'], app_active='Employés')
EMPLOYES = EMPLOYES.replace('class="app muk"', 'class="app muk masque"', 1)

# ======================================================= 5. les motifs --
POIGNEE = ('<span class="t16-poignee"><svg viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.6"/>'
           '<circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/>'
           '<circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></svg></span>')
CASE = '<span class="rg-case%s t16-case"%s><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" ' \
       'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span>'
LIGNES_MOTIFS = [{'id': 't16-m%d' % k, 'cellules': [(POIGNEE,), m, (CASE % (' coche' if m == 'Autre' else '',
                                                                          ' id="t16-m%d-prec"' % k),)]}
                 for k, m in enumerate(demo.MOTIFS_RESTO, 1)]
LIGNES_MOTIFS.append({'id': 't16-m-ajout', 'classe': 't16-ajout',
                      'cellules': [('<span></span>',), ('<span class="lien">Ajouter une ligne</span>',), ('<span></span>',)]})
MOTIFS = vue_liste('t16-motifs', "Motifs d'annulation", [('', '44px'), ('Motif', '1fr'), ('Précision obligatoire', '300px')],
                   LIGNES_MOTIFS, pager='1-5 / 5', initiale=True)
MOTIFS = MOTIFS.replace('<div class="liste">', '<div class="liste" id="t16-motifs-liste">', 1)
POS_MANAGER = fenetre_muk('t16-mpos', 'Point de Vente', MENUS_MUK['point_de_vente'], [MOTIFS], actif='Configuration',
                          societe=demo.SOCIETE_RESTO, initiale=MANAGER[0],
                          avatar=demo.AVATARS_RESTO[MANAGER.split()[0]], apps=APPS_PROFIL['resto_manager'],
                          app_active='Point de Vente')
POS_MANAGER = POS_MANAGER.replace('class="app muk"', 'class="app muk masque"', 1)
POS_MANAGER = POS_MANAGER.replace('<span class="menu actif">Configuration</span>',
                                  '<span class="menu actif" id="t16-mpos-conf">Configuration</span>', 1)
assert 'id="t16-mpos-conf"' in POS_MANAGER

# ======================================================= 6. la caisse --
PLAN = resto_plan('t16-plan', resto_salle('t16-plan'), delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO,
                  caisse_fermee=True, initiale=True)
CAISSE = fenetre_resto('t16-pos', [PLAN], calques=resto_code('t16-code', TITRES_RESTO['ouvrir']), cache=True)

APP = 't16-adm'
ECRAN = navigateur(ADMIN_ECRAN + EMPLOYES + POS_MANAGER + CAISSE)

CSS = ("/* -- la pastille : l'administrateur d'Odoo (AITE) jusqu'à l'étape 3, puis la manager -- */\n"
       + css_personnage('#tu-perso:not(.t16-moi)', ADMIN, ROLE_ADMIN, INITIALE_ADMIN) + """
/* -- 5. la liste des motifs : poignée et cases, « Ajouter une ligne » -- */
.t16-poignee { width: 22px; height: 22px; display: inline-flex; color: #ADB5BD; margin-left: 8px; }
.t16-case { margin-top: 0; justify-self: start; }
#t16-motifs .liste .ligne.t16-ajout { border-bottom: 0; }
#t16-motifs .liste .lien { color: var(--o-lien); }
""")

# Les pauses de chaque étape, calées sur la voix (secondes).
TUTORIEL = {
    'slug': 't16-restaurant-mise-en-place',
    'profil': 't16_restaurant_mise_en_place',
    'numero': 16,
    'titre': 'Service à table contrôlé : la mise en place',
    'fonction': 'Service à table contrôlé',
    'personnage': (MANAGER, ROLE_MANAGER),
    'accroche': {
        'kicker': 'Avant le premier service',
        # Les douleurs : docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md, REST-01 (:136-137 : code d'équipe, entrer sans
        # rien taper, deux employés avec le même code), REST-03 (:194 : l'annulation ouverte à tous), REST-04
        # (:208 : tout employé modifie un prix), §2 besoin 3 (:86 : le supérieur « s'en explique »).
        'question': 'Votre caisse sait-elle *qui* fait quoi ?',
        'douleurs': [('cle', 'Un seul code pour toute l\'équipe'),
                     ('personne', 'On entre en caisse sans taper de code'),
                     ('echange', 'Deux employés, le même code'),
                     ('corbeille', 'Tout le monde peut annuler'),
                     ('pieces', 'Des prix changés à la main'),
                     ('interrogation', 'Des annulations sans motif')],
        'voix': "Un code pour toute l'équipe, des prix changés à la main, des annulations sans motif : ce soir, qui a "
                "fait quoi à la caisse ?",
    },
    'revelation': {
        # La case : res_config_settings_views.xml:29-33 ; les quatre niveaux : regles.py:23-28 ; le code « propre à
        # cet employé », « la caisse sait ainsi qui a fait quoi » : AIDE_CODE.
        'promesse': 'Une case à cocher, quatre niveaux, un code à 4 chiffres par employé : la caisse sait qui a fait '
                    'quoi.',
        'voix': "Avec Aïte haousse, une case suffit : chacun son niveau, chacun son code.",
    },
    'temps': ['Régler', 'Identifier', 'Expliquer', 'Servir'],
    'app': APP,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't16-rg'},
    'bulles': {
        'b-pose': 'Cocher pose aussi la connexion par code, le contrôle des prix et les remises désactivées.',
        'b-fermee': 'Se change caisse fermée : à régler avant la première ouverture.',
        'b-phrase': 'Un autre délai ? La phrase suit le nombre tapé.',
        'b-unique': 'Un code déjà pris est refusé, sans nommer le collègue.',
        'b-vide': 'Sans niveau, l\'employé n\'apparaît pas sur la caisse.',
        'b-motif': 'Le chef de salle en touche un quand il annule un produit déjà envoyé.',
        'b-garde': 'Vos changements restent : une mise à niveau ne les remet pas.',
        'b-repos': 'Le plan est l\'écran de repos : tout retour au plan oublie l\'employé.',
    },
    'reactions': {
        'r-code': 'Chacun son code : fini le code d\'équipe.',
        'r-pret': 'Les règles sont posées.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Une case déjà cochée',
         'texte': 'La caisse « Restaurant » arrive à l\'installation, case « Service à table contrôlé » déjà cochée.',
         'voix': "À l'installation, Aïte haousse pose une caisse Restaurant, avec ses deux modes de paiement et sa "
                 "salle. Dans ses réglages, une "
                 "case est déjà cochée : Service à table contrôlé. La phrase dessous dit tout ce qui va se passer, et "
                 "ce que la case règle avec elle.",
         'gestes': [pause(0.5), anneau('#t16-rg-sel', d=1.4), pause(0.3), curseur('#t16-ebr-case', d=0.6),
                    anneau('#t16-ebr-case', d=0.9, avec=True), curseur('#t16-stc-case', d=0.5),
                    anneau('#t16-stc-case', d=1.2),
                    zoom('#t16-stc', s=1.5, d=0.9, fy=0.45), bulle('b-pose', '#t16-stc-aide', cote='gauche', d=3.0),
                    pause(2.8), bulle('b-fermee', '#t16-stc-aide', cote='gauche', d=2.8), pause(2.4), dezoom(d=0.6)]},
        {'temps': 0, 'titre': 'Chaque réglage dit ce qui va se passer',
         'texte': "Délai avant l'orange : 60 minutes ; vente sans table : fermée ; produits épuisés : refusés.",
         'voix': "Juste en dessous, chaque réglage a sa phrase : une table passe à l'orange après soixante minutes, la "
                 "vente sans table reste fermée, et un produit suivi en stock est refusé quand il est épuisé. "
                 "L'addition, elle, peut s'imprimer avant le paiement.",
         'gestes': [defiler('#t16-rg-defil', -420, d=1.0), pause(0.3), anneau('#t16-delai-v', d=1.2),
                    bulle('b-phrase', '#t16-delai-phrase', cote='droite', d=2.6), pause(2.2),
                    anneau('#t16-vst-case', d=1.4), pause(0.6),
                    defiler('#t16-rg-defil', -640, d=0.9), anneau('#t16-refus-case', d=1.6), pause(0.6),
                    curseur('#t16-impression-case', d=0.5), anneau('#t16-impression-case', d=1.4)]},
        {'temps': 1, 'titre': 'Un niveau, un code',
         'texte': 'Fiche employé : le « Niveau en caisse », et un « Code caisse » à 4 chiffres proposé d\'office. '
                  'Aucun courriel.',
         'voix': "Côté équipe, Edwige, la manager, ouvre la fiche de Loïc, son serveur. Dans la liste, elle choisit "
                 "son niveau en caisse : serveur. Aussitôt, un code à quatre chiffres, que personne d'autre n'a, est "
                 "proposé. Elle enregistre ; aucun courriel à donner.",
         'gestes': [montrer('#t16-emp', d=0.5, y=0), classe('#tu-perso', ajouter=['t16-moi'], avec=True),
                    pause(0.5), defiler('#t16-fe-defil', -470, d=1.0), pause(0.4),
                    clic('#t16-fe-niveau', fx=0.3, d=0.7), montrer('#t16-fe-liste', d=0.25, y=-8),
                    survol('#t16-fe-opt-1'), clic('#t16-fe-opt-1', fx=0.3, d=0.5),
                    cacher('#t16-fe-liste', d=0.15), choisir('t16-fe-niveau', NIVEAUX[0], avec=True),
                    montrer('#t16-fe-statut', d=0.2, y=0, avec=True), pause(0.5),
                    choisir('t16-fe-code', CODE_LOIC), curseur('#t16-fe-code', fx=0.8, d=0.5, avec=True),
                    anneau('#t16-fe-code', d=1.4),
                    bulle('b-unique', '#t16-fe-code', cote='droite', d=2.8), pause(1.9),
                    clic('#t16-fe-save', d=0.6), cacher('#t16-fe-statut', d=0.2),
                    reaction('r-code', d=2.6), pause(1.0)]},
        {'temps': 1, 'titre': 'Quatre niveaux, des gestes réservés',
         'texte': 'Serveur, caissière, chef de salle ou superviseur, manager : la fiche dit ce que chacun peut faire.',
         'voix': "La fiche dit aussi ce que chaque niveau peut faire. Le serveur ouvre ses tables, commande et "
                 "envoie. La caissière, en plus, ouvre la caisse et encaisse. Le chef de salle annule ce qui est "
                 "parti, sort des espèces et ferme. Le manager peut tout.",
         'gestes': [zoom('#t16-fe-niveau-aide', s=1.3, d=0.9, fx=0.5), pause(1.6), anneau('#t16-fe-aide-1', d=2.2),
                    anneau('#t16-fe-aide-2', d=2.2), anneau('#t16-fe-aide-3', d=2.8), anneau('#t16-fe-aide-4', d=1.6),
                    bulle('b-vide', '#t16-fe-aide-5', cote='bas', d=2.6), pause(2.2), dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Cinq motifs, déjà là',
         'texte': 'Point de Vente › Configuration › Motifs d\'annulation : cinq motifs posés d\'office ; « Autre » '
                  'demande une précision.',
         'voix': "Pour annuler ce qui est déjà parti, il faudra un motif. Cinq sont posés d'office : erreur de saisie, "
                 "client parti, plat refusé, produit manquant, et autre, avec une précision. Edwige peut les "
                 "renommer, ou en ajouter.",
         'gestes': [montrer('#t16-mpos', d=0.45, y=0), pause(0.3), curseur('#t16-mpos-conf', d=0.5),
                    anneau('#t16-mpos-conf', d=1.2), pause(0.2),
                    anneau('#t16-motifs-liste', d=2.6), pause(1.0), anneau('#t16-m5-prec', d=1.4),
                    bulle('b-motif', '#t16-m2', cote='bas', d=3.0), pause(2.4),
                    bulle('b-garde', '#t16-m-ajout', cote='bas', d=3.0), pause(2.0)]},
        {'temps': 3, 'titre': 'Le premier service',
         'texte': 'Sur la tablette : le plan de salle, verrouillé ; la caissière ouvre la caisse avec son code.',
         'voix': "Edwige saisit encore la carte, le plan de salle et le stock de départ. Sur la tablette, plus "
                 "d'écran à déverrouiller : le plan attend un code. Le matin, la caissière ouvre la caisse avec le "
                 "sien ; ensuite, chaque table commence par un code.",
         # Dans l'ordre de la voix : le plan saisi par Edwige, l'écran de repos (avant la fenêtre du code, que la
         # bulle couvrirait), le bandeau quand la caissière ouvre la caisse, puis la fenêtre du code. Elle s'ouvre
         # seule quand le plan s'affiche, et par « Ouvrir la caisse » (R/static/src/overrides/floor_screen.js:5,
         # 51-53 ; R/static/src/store/pos_store.js:693-718) : la vidéo montre le bouton.
         'gestes': [montrer('#t16-pos', d=0.5, y=0), pause(0.6), curseur('#t16-plan-carte', fx=0.8, fy=0.35, d=0.6),
                    anneau('#t16-plan-carte', d=2.0), pause(0.2),
                    bulle('b-repos', '#t16-plan-legende', cote='haut', d=3.0), pause(2.4),
                    anneau('#t16-plan-fermee', d=1.2), clic('#t16-plan-ouvrir', d=0.6), ouvrir('t16-code'), pause(0.6),
                    anneau('#t16-code-titre', d=1.4), pause(0.4), reaction('r-pret', d=2.6), pause(0.6)]},
    ],
    'resultats': {
        'titre': 'Les règles sont posées avant le premier service',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'case', 'icone': 'coche',
             'texte': 'pose la connexion par code, le contrôle des prix, les remises désactivées, le partage et '
                      'l\'impression de l\'addition'},
            {'valeur': '4', 'compter': 4, 'unite': 'niveaux', 'icone': 'personne',
             'texte': 'serveur, caissière, chef de salle ou superviseur, manager : un code à 4 chiffres chacun'},
            {'valeur': '5', 'compter': 5, 'unite': 'motifs d\'annulation', 'icone': 'liste',
             'texte': 'posés d\'office, à renommer ou compléter sans programmer'},
        ],
        'voix': "Une case, quatre niveaux, cinq motifs : les règles sont posées avant le premier service.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Ouvrir la caisse et servir une table',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : ouvrir la caisse "
                "et servir une table.",
    },
    'vignette': {'etape': 3, 'apres': 9.0},
}
