# -*- coding: utf-8 -*-
"""Chapitre 4 — La réservation en ligne.

Source : fiche de recette n° 5 « La réservation en ligne » (client sur le
site public, sans compte : page de réservation, choix d'un espace, créneaux
libres, coordonnées, page de remerciement avec la référence, demande de
séjour).

Libellés relevés dans : aite_website_booking/views/website_templates.xml
(« Réserver en ligne », cartes, « Voir les créneaux », « ← Tous les espaces »,
« Voir ce jour », « Créneaux disponibles », « Vos coordonnées » et ses
placeholders, « Réserver ce créneau », mention de l'acompte, page « Merci ! »
pour un créneau et pour un séjour, « Demande de séjour », « Envoyer la
demande »), aite_slot_booking/data/slot_sequence_data.xml (référence
CRN/AAAA/NNNN : préfixe propre aux créneaux et année sur quatre chiffres
depuis la livraison 4, écart n° 61 ; les séjours gardent RES/AAAA/NNNN).
L'en-tête du site (logo, menus) est celui du site de l'établissement : il est
rejoué neutre, au nom de l'hôtel de démonstration, par ecrans.site (menus
« Accueil », « Réservation », « Contactez-nous » d'Odoo, téléphone de l'hôtel
de la série, demo.TEL_HOTEL). « Confirmation immédiate par e-mail » et « Un
e-mail de confirmation vous a été envoyé. » ne s'affichent que si l'envoi
automatique est actif (écart n° 49) : c'est le réglage par défaut
(aite_slot_booking/models/res_config_settings.py:33-37), et Claire donne son
e-mail.

Données harmonisées avec scenarios/t08_site_web.py (le même parcours, en
tutoriel) : tarifs des salons 15 000 et 25 000 FCFA / heure (ceux du
tutoriel 9) ; Claire Durand (+33 6 39 98 21 47, plage réservée à la fiction ;
claire.durand@exemple.fr) réserve le salon VIP Wouri pour le samedi
17/10/2026 à 16:00, référence CRN/2026/0131 (demo.CRENEAU_SALON) ; créneaux
libres du 17/10 (12:00-14:00 et 19:00-21:00 déjà vendus) ; sa demande de
séjour du 20 au 23/10 devient RES/2026/0224 (départ à 12:00, l'heure de
l'hôtel, écart n° 58).
"""

TEL_CLAIRE = '+33 6 39 98 21 47'
TARIF_SALON, TARIF_VVIP = '15 000 FCFA / heure', '25 000 FCFA / heure'


import demo
from ecrans import e, entree, s_vue, site
from moteur import anneau, clic, classe, pause, saisir, vue

NOM, ROLE = demo.POSTES['client']


def s_carte(ident, titre, texte, bouton_, contour=False, prix=None):
    px = '<div class="px">%s</div>' % e(prix) if prix else ''
    return ('<div class="s-carte" id="%s"><div class="h">%s</div><div class="p">%s</div>%s'
            '<div class="s-bouton%s" id="%s-bt">%s</div></div>'
            % (ident, e(titre), e(texte), px, ' contour' if contour else '', ident, e(bouton_)))


ACCUEIL = s_vue('c4-accueil', (
    '<div class="s-h1">Réserver en ligne</div><div class="s-p">Disponibilités en temps réel — confirmation immédiate '
    'par e-mail.</div><div class="s-cartes">%s%s%s</div>'
    % (s_carte('c4-vip', 'Espaces VIP & VVIP', "Salons privés à l'heure, pour vos rencontres et célébrations.",
               'Choisir un espace'),
       s_carte('c4-spa', 'SPA & Coiffure', 'Soins et rendez-vous coiffure homme & femme.', 'Prendre rendez-vous'),
       s_carte('c4-ch', 'Chambres & Suites', 'Votre séjour, confirmé par notre réception.', 'Demander un séjour'))),
    initiale=True)

ESPACES = s_vue('c4-espaces', (
    '<div class="s-h1">Espaces VIP & VVIP</div><div class="s-cartes">%s%s%s</div>'
    % (s_carte('c4-e1', 'Salon VIP Wouri', 'Ouvert de 09:00 à 23:00', 'Voir les créneaux', True, TARIF_SALON),
       s_carte('c4-e2', 'Salon VIP Sanaga', 'Ouvert de 09:00 à 23:00', 'Voir les créneaux', True, TARIF_SALON),
       s_carte('c4-e3', 'Salon VVIP Bonabéri', 'Ouvert de 10:00 à 23:00', 'Voir les créneaux', True, TARIF_VVIP))))

HEURES = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00', '18:00', '21:00', '22:00']     # libres le 17/10
CRENEAUX = ''.join('<span class="creneau" id="c4-h%s"><i></i>%s</span>' % (h[:2], h) for h in HEURES)
CRENEAU = s_vue('c4-creneau', (
    '<div class="s-form"><div class="s-p" style="margin-top:0">← Tous les espaces</div>'
    '<div class="s-h1" style="font-size:54px;margin-top:6px">Salon VIP Wouri</div><div class="s-p">%s</div>'
    '<div class="s-lab">Date</div><div style="display:flex;gap:10px;margin-top:8px;width:480px;align-items:flex-end">'
    '<div style="flex:1">%s</div><span class="bt" style="background:#212529;color:#fff;height:58px;flex:none;'
    'padding:0 20px" id="c4-voir">Voir ce jour</span></div>'
    '<div class="s-lab" style="font-size:24px;margin-top:22px">Créneaux disponibles</div><div class="creneaux">%s</div>'
    '<div class="s-lab" style="font-size:24px;margin-top:22px">Vos coordonnées</div><div class="s-ligne3">%s%s%s</div>'
    '<div class="s-gros-bt" id="c4-reserver">Réserver ce créneau</div>'
    '<div class="s-note">Acompte à régler au comptoir — Orange Money, MTN MoMo ou espèces.</div></div>'
    % (TARIF_SALON, entree('c4-date', 'jj/mm/aaaa'), CRENEAUX, entree('c4-nom', 'Nom complet'), entree('c4-tel', 'Téléphone'),
       entree('c4-mail', 'E-mail (confirmation)'))))

MERCI = s_vue('c4-merci', (
    '<div class="s-merci"><div class="h">Merci !</div>'
    '<div class="p">Votre réservation <b>%s</b> est <b>confirmée</b>.</div>'
    '<div class="q" style="color:var(--o-texte)">Salon VIP Wouri</div>'
    '<div class="q">Un e-mail de confirmation vous a été envoyé.</div>'
    '<div class="s-alerte" id="c4-acompte">L\'acompte se règle au comptoir à votre arrivée — <b>Orange Money, MTN MoMo '
    'ou espèces</b>.</div><div style="margin-top:22px"><span class="s-bouton contour" style="display:inline-flex;padding:0 22px">'
    'Retour aux réservations</span></div></div>' % e(demo.CRENEAU_SALON)))

SEJOUR = s_vue('c4-sejour', (
    '<div class="s-form"><div class="s-h1">Demande de séjour</div>'
    '<div class="s-p">Notre réception confirme votre chambre et vous rappelle rapidement.</div>'
    '<div class="s-ligne"><div><div class="s-lab">Arrivée</div>%s</div><div><div class="s-lab">Départ</div>%s</div></div>'
    '<div class="s-ligne" style="grid-template-columns:220px 1fr"><div><div class="s-lab">Adultes</div>%s</div>'
    '<div><div class="s-lab">Nom complet</div>%s</div></div>'
    '<div class="s-ligne"><div><div class="s-lab">Téléphone</div>%s</div><div><div class="s-lab">E-mail</div>%s</div></div>'
    '<div class="s-gros-bt" id="c4-envoyer">Envoyer la demande</div></div>'
    % (entree('c4-s-arr', 'jj/mm/aaaa'), entree('c4-s-dep', 'jj/mm/aaaa'), entree('c4-s-ad', '', '2'),
       entree('c4-s-nom', ''), entree('c4-s-tel', ''), entree('c4-s-mail', ''))))

MERCI_SEJOUR = s_vue('c4-merci2', (
    '<div class="s-merci"><div class="h">Merci !</div>'
    '<div class="p">Votre demande de séjour <b>RES/2026/0224</b> est bien transmise.</div>'
    '<div class="q" id="c4-rappel">Notre réception vous confirme la chambre et le tarif très rapidement.</div>'
    '<div style="margin-top:22px"><span class="s-bouton contour" style="display:inline-flex;padding:0 22px">'
    'Retour aux réservations</span></div></div>'))

# L'en-tête partagé (ecrans.site) : « Accueil », « Réservation », « Contactez-nous » et demo.TEL_HOTEL.
ECRAN = site('app-c4', [ACCUEIL, ESPACES, CRENEAU, MERCI, SEJOUR, MERCI_SEJOUR], 'Complexe Hôtelier')

CHAPITRE = {
    'court': 'Site web',
    'poste': 'Client, sur le site public',
    'titre': 'La réservation en ligne',
    'personne': (NOM, ROLE),
    'objectif': "Réserver un espace depuis le site public, sans compte, recevoir la confirmation, puis demander "
                "un séjour.",
    'voix': "Quatrième chapitre : le client, sur le site web de l'hôtel. Claire réserve un salon sans créer de "
            "compte, puis demande une chambre.",
    'app': 'app-c4',
    'ecran': ECRAN,
    'vues_initiales': {'site': 'c4-accueil'},
    'etapes': [
        {'titre': 'La page de réservation', 'texte': 'Espaces, SPA et coiffure, chambres : sans compte, sans mot de passe.',
         'voix': "La page Réserver en ligne est publique : pas de compte, pas de mot de passe. Trois entrées : "
                 "les salons privés, le spa et la coiffure, et les chambres.",
         'gestes': [pause(0.5), anneau('#c4-vip', d=1.0), anneau('#c4-spa', d=1.0), anneau('#c4-ch', d=1.0)]},
        {'titre': 'Choisir un espace', 'texte': 'Seuls les espaces ouverts à la réservation en ligne apparaissent.',
         'voix': "Claire choisit un espace. Seuls les salons ouverts à la réservation en ligne apparaissent, avec "
                 "leurs horaires et leur prix à l'heure.",
         'gestes': [clic('#c4-vip-bt'), vue('c4-espaces', 'site'), pause(0.5), anneau('#c4-e1', d=1.4),
                    clic('#c4-e1-bt')]},
        {'titre': 'Les créneaux libres', 'texte': 'La grille du jour ne montre que ce qui est encore disponible.',
         'voix': "Elle choisit une date : la grille ne montre que les créneaux encore libres. Elle coche seize "
                 "heures.",
         'gestes': [vue('c4-creneau', 'site'), saisir('c4-date', '17/10/2026'), clic('#c4-voir'), pause(0.3),
                    clic('#c4-h16'), classe('#c4-h16', ajouter=['coche'])]},
        {'titre': 'Se présenter et réserver', 'texte': 'Nom, téléphone, e-mail : la confirmation part toute seule.',
         'voix': "Puis ses coordonnées : nom, téléphone, e-mail pour la confirmation. Un clic sur Réserver ce "
                 "créneau ; l'acompte se réglera au comptoir, en Orange Moni, MTN MoMo ou espèces.",
         'gestes': [saisir('c4-nom', NOM), saisir('c4-tel', TEL_CLAIRE),
                    saisir('c4-mail', 'claire.durand@exemple.fr'), clic('#c4-reserver')]},
        {'titre': 'Réservation confirmée', 'texte': 'La référence prouve que la réservation est déjà au back-office.',
         'voix': "La page de remerciement affiche la référence de la réservation : elle est déjà dans le planning "
                 "des espaces, côté back-office, et l'e-mail de confirmation est parti.",
         'gestes': [vue('c4-merci', 'site'), pause(0.6), anneau('#c4-merci .p b', d=1.4), anneau('#c4-acompte', d=1.4)]},
        {'titre': 'Demander un séjour', 'texte': 'Dates, occupation, coordonnées : la réception rappelle.',
         'voix': "Pour une chambre, Claire envoie une demande de séjour : dates, nombre d'adultes et coordonnées. "
                 "La demande arrive à la réception en brouillon, prête à confirmer.",
         'gestes': [vue('c4-sejour', 'site'), saisir('c4-s-arr', '20/10/2026'), saisir('c4-s-dep', '23/10/2026'),
                    saisir('c4-s-nom', NOM), saisir('c4-s-tel', TEL_CLAIRE),
                    saisir('c4-s-mail', 'claire.durand@exemple.fr'), clic('#c4-envoyer'),
                    vue('c4-merci2', 'site'), anneau('#c4-merci2 .p b', d=1.4)]},
    ],
}
