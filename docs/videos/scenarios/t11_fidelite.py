# -*- coding: utf-8 -*-
"""Tutoriel 11 — Fidélité AITE : un seul capital de points, des VIP qui se révèlent seuls.

La directrice (Danielle Eyenga, demo.POSTES['direction'], groupe Responsable)
suit la fidélité de l'établissement : un ticket du bar rattaché à une cliente
donne ses points, le grand livre les range par origine, le statut Standard /
VIP / VVIP se recalcule une fois par jour, la fiche de la cliente porte son
badge, et une nuit offerte se retire du capital avec son motif. Le parcours
suit Estelle Ngono (demo.py), qui quitte la chambre 204 le 16/10/2026 : la
journée rejouée est le 16/10/2026.

Profil rejoué : Responsable (aite_hotel_management.group_hotel_manager), seul
profil qui voit « Ajuster des points » (aite_loyalty/views/loyalty_menus.xml
:21-26, security/ir.model.access.csv:4). Menus de l'application Hôtel et
barre MuK relevés sur le compte demo.direction de la base MuK (captures de
lecture prises pour ce tutoriel, comme ref_muk/053 à 056) ; applications :
ecrans.APPS_PROFIL['direction'].

Sources des libellés et des règles (relevés mot pour mot) :

- Menu Fidélité : aite_loyalty/views/loyalty_menus.xml:3-26 (« Fidélité »,
  « Mouvements de points », « Clients VIP / VVIP », « Ajuster des points »).
- Mouvements de points : aite_loyalty/views/loyalty_move_views.xml:3-19
  (liste sans création :7, ligne rouge si points < 0 :7, colonnes Date,
  Client, Origine, Référence, Montant de base, Points :8-13, total « Total
  points » :13, colonne Note masquée par défaut :14) ; recherche :20-35
  (« Gains », « Retraits », « Regrouper par » Client / Origine / Mois) ;
  action :36-46. Champs et ordre (date desc, id desc) : models/
  loyalty_move.py:40-65 ; libellés d'origine :12-20. Les groupes d'une
  sélection s'affichent dans l'ordre de la clé (hotel, manual, pos,
  slot_hair, slot_pressing, slot_spa, slot_space), vérifié sur la base MuK.
  Sommes de groupe d'un champ monétaire sans devise, à deux décimales :
  odoo18/addons/web/static/src/views/list/list_renderer.js:651-664 et
  core/currency.js:32-46 (voir écart 4). Panneau de recherche : « Filtres »,
  « Ajouter un filtre personnalisé », « Ajouter un groupe personnalisé »,
  « Favoris », « Enregistrer la recherche actuelle » (odoo18/addons/web/
  i18n/fr.po).
- Barème : models/loyalty_move.py:104-116 (_points_for : partie entière de
  montant ÷ 1 000 × taux, zéro sous le minimum) ; statut : :118-133
  (_tier_for) ; recalcul quotidien sur la fenêtre glissante :183-242,
  data/ir_cron_data.xml:3-11 (intervalle d'un jour) ; valeurs par défaut :
  models/res_config_settings.py:19-39 (1 point par 1 000, minimum 1 000,
  12 mois, VIP 500 000 et 10 visites, VVIP 2 000 000, 25 visites et 3
  familles). Les points de chaque ligne (journal et historique d'Estelle), son
  solde et ses deux changements de statut (VIP le 01/03/2026, VVIP le
  11/10/2026, recalcul rejoué jour par jour) sont calculés par ces deux
  fonctions, extraites du module à l'import (comme tests/socle/
  test_loyalty_logic.py), avec ces valeurs par défaut ; les totaux du
  regroupement par origine sont fixés à la main, cohérents avec le barème et
  bornés par les séquences visibles dans la série (voir « Données »).
- Ce que montre le grand livre : les ventes rattachées à un client identifié,
  au-dessus du minimum (hooks.py:38-41, loyalty_move.py:162-163) ; ce n'est
  pas le chiffre d'affaires d'un service (pas de ticket sans nom, taxe de
  séjour comprise, doubles comptes de l'écart 2). La voix dit donc « d'où
  viennent les points » et la directrice « où mes clients fidèles dépensent ».
- Attribution : models/hooks.py:21 et :32-48 (ticket payé avec un client,
  sinon rien), :78-99 (folio facturé), :110-125 (prestation réalisée) ;
  « Un ticket sans client identifié ne donne rien — le réflexe caisse « à
  quel nom ? » » : docs/guides/AITE_Guide_Fidelite.pdf p. 2 (§3).
- Clients VIP & VVIP : loyalty_move_views.xml:47-56 (titre « Clients VIP &
  VVIP », domaine VIP / VVIP, facette par défaut search_default_customer) ;
  facette « Factures clients » : odoo18/addons/account/views/
  partner_view.xml:341 et i18n/fr.po ; carte de contact d'Odoo 18 (image,
  nom, ville et pays, e-mail) : odoo18/odoo/addons/base/views/
  res_partner_views.xml:397-440 ; « Nouveau » et pagination : web/i18n/fr.po.
- Fiche du contact : aite_loyalty/views/res_partner_views.xml:8-22 (bouton
  « Points » fa-star masqué sans mouvement, badge « Statut client » orange
  pour VIP et rouge pour VVIP, « Statut depuis » masqué en Standard) ;
  models/res_partner.py:18-40 (solde = somme des mouvements, statut suivi
  dans l'historique, tracking=True :28) ; boutons « Séjours »
  (aite_hotel_management/views/res_partner_views.xml:9-14) et « Fiches »
  (aite_guest_registry/views/res_partner_views.xml:8-13) ; boutons
  « Facturé », « Achats », « Taux de livraisons dans les temps » / « Pas
  encore de données », « Lot/Numéros de série » et champs du contact
  (Particulier, Société, Nom de la société …, Rue..., Rue 2..., Ville, État,
  Code postal, Pays, N° TVA, / si non applicable, Poste, par ex. Directeur
  Commercial, Téléphone, Mobile, E-mail, Site Web, par ex.
  https://www.odoo.com, Titre, par ex. Monsieur, Langue, Étiquettes, onglets
  Contacts & Adresses, Ventes & Achats, Facturation, Notes internes,
  Ajouter) : traductions françaises du cœur d'Odoo 18 (base, account,
  purchase, purchase_stock, stock i18n/fr.po), disposition relevée sur la
  base MuK ; onglet « Hôtel » : aite_hotel_management/views/
  res_partner_views.xml:16-18 ; « French / Français » : odoo18/odoo/addons/
  base/data/res.lang.csv:31. Historique (« Envoyer message », « Note »,
  « Activités », ligne de suivi « ancien → nouveau (champ) ») : odoo18/
  addons/mail/static/src/core/web/message_patch.xml:12-20 ; la tâche
  planifiée écrit au nom d'OdooBot.
- Ajuster des points : wizard/loyalty_adjust_wizard_views.xml:7-22 (titre de
  la fenêtre = nom de l'action « Ajuster des points », « Motif » avec
  « Geste commercial, correction… », « Appliquer », « Annuler ») ;
  wizard/loyalty_adjust_wizard.py:15-38 (« Points (±) » et son aide, motif
  obligatoire, nombre nul refusé, solde négatif refusé, origine « Ajustement
  manuel », référence « Ajustement ») ; motif « Utilisation : … » pour
  tracer un avantage offert : AITE_Guide_Fidelite.pdf p. 3. Le module n'a ni
  catalogue de récompenses ni conversion points → nuit : la directrice choisit
  le nombre de points retirés (la voix dit qu'elle « décompte » la nuit, pas
  qu'une règle l'échange). La fenêtre
  ouverte depuis le menu se ferme sans recharger l'écran du dessous
  (odoo18/addons/web/static/src/webclient/actions/action_service.js
  :1382-1393) : la cliente rouvre « Points » pour voir le retrait.
- Points de <client> : models/res_partner.py:42-50 (« Points de %(p)s »,
  liste filtrée sur le client) ; total en pied de colonne : loyalty_move_
  views.xml:13.
- Caisse (écran de paiement d'Odoo 18) : odoo18/addons/point_of_sale/static/
  src/app/screens/payment_screen/payment_screen.xml:28-140 (« Client »,
  « Facture », « Retour », « Valider » grisé tant que rien n'est réglé) ;
  payment_status/payment_status.xml:4-20 (« Veuillez sélectionner un mode de
  paiement », « Monnaie ») ; liste des clients : screens/partner_list/
  partner_list.xml:4-58 (« Créer », « Recherche des clients... », Nom,
  Adresse, Contact, « Rechercher plus », « Ignorer ») et partner_line.xml
  :45-63 ; traductions : point_of_sale/i18n/fr.po. « Mettre sur ardoise » :
  aite_pos_credit/static/src/js/pos/payment_screen_button.xml:10-19 ;
  moyens « Ardoise client » et « Note de chambre » : aite_demo_data/models/
  demo_generator.py:295-312 ; « Espèces » : point_of_sale/i18n/fr.po
  (Cash). Référence d'un ticket : « <nom de la caisse>/<n° sur 4
  chiffres> » (point_of_sale/models/pos_config.py:476-486, comme
  « Caisse Boutique (démo)/0156 » sur ref_muk/054) ; prestations
  « RES/%(y)s/ » sur 4 chiffres (aite_slot_booking/data/
  slot_sequence_data.xml:3-8) ; folios « FOL/%(year)s/ »
  (aite_hotel_management/data/hotel_sequence_data.xml:17).
- Formats : dates %d/%m/%Y (res.lang.csv:31), montants « 12 500 FCFA »
  (devise XAF, symbole FCFA après le montant, sans décimale :
  odoo18/odoo/addons/base/data/res_currency_data.xml:476-483).

Douleurs de l'accroche : docs/etude_comparative/benchmark_pms.md:209
(programme de fidélité à paliers natif chez 1 PMS leader sur 10), :29
(Mews : fidélité via partenaires), :36 (Cloudbeds : partenariat Journey) ;
docs/guides/AITE_Guide_Fidelite.pdf p. 1 §1 (un capital unique pour le
restaurant, la boutique, le séjour, le SPA, la coiffure, le pressing, le
salon VIP), p. 3 §5 (« le statut reflète la relation réelle, pas un acquis
à vie »), p. 3 tableau (« Le client dit qu'il devrait être VIP » →
« l'historique fait foi » ; avantage offert tracé par un ajustement
« Utilisation : … »).

Promesse et résultats : un point par tranche de 1 000 FCFA (res_config_
settings.py:19-23), six familles de services pour un seul capital (loyalty_
move.py:12-19, hooks.py), trois statuts recalculés une fois par jour sur 12
mois glissants (loyalty_move.py:22-26, ir_cron_data.xml:8-9,
res_config_settings.py:24-25). « Une fois par jour » et non « chaque nuit » :
la tâche planifiée n'a pas d'heure fixe.

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, Estelle
Ngono, caissier Hervé Tchakounté, directrice Danielle Eyenga, Claire
Durand). FOL/2026/0214 vaut 112 800 FCFA au départ, comme au tutoriel 3 :
deux nuits Confort (90 000), 12 000 FCFA de taxe de séjour et quatre «
Petit-déjeuner buffet » à 2 700 FCFA (10 800), passé « Facturé » le 16/10 à
11:42 (t03_folio.py:137-141, :200-206, :428, :702) ; il rapporte donc 112
points, et « Facturé » sur la fiche cumule ses trois folios (96 000 + 144
000 + 112 800). Le script relit ce total dans t03_folio.py et s'arrête s'il
diverge. Le journal du 15/10 reprend les prestations réalisées du tutoriel 9
(t09_espaces.py:242-254 : Samuel Etoga au pressing, Yves Tchana, Linda
Ewané, Carine Ndongo, Paul Essomba, Rachel Bilong, et le massage de Brigitte
Essomba RES/26/0158 à 27 000 FCFA, reporté sur son folio FOL/2026/0210 :
t09:168-171, :249) et le départ de Claire Durand (RES/2026/0201, chambre
401, du 14 au 15/10 : t02_planning.py:259, :288 ; folio FOL/2026/0201 de
123 000 FCFA, soit une nuit VIP à 120 000 et 3 000 de taxe pour un adulte,
selon folio_resa de t03_folio.py:416-420). Estelle n'a donc aucune
prestation le 15/10 : son folio facturé (112 800 FCFA, t03) n'en porte
aucune. Séquences recalées sur la série : la caisse « Bar de la terrasse »
a ouvert le 04/05/2026 (t12_ventes.py:544) ; environ 8,3 tickets par jour
(108 du 01 au 13/10, t12_ventes.py:380), soit environ 1 350 au soir du 13/10 sur
les 1 440 tickets de toutes les caisses (t12_ventes.py:550) ; d'où les
tickets d'Estelle /0560 le 10/07 (son premier verre au bar), /0851 le
14/08, /1091 le 12/09, /1149 le 19/09, /1266 le 03/10 et /1375 le 16/10,
entre le /1360 du 14/10 au soir (Brigitte Essomba, t04_note_chambre.py) et
le /1377 du 16/10 à 22:41 (Martin Ebode, t04) ; prestations « RES/%(y)s/ »
(sans remise à zéro) vers RES/26/0140 au matin du 15/10 (t09:242-254),
environ 0,4 par jour depuis novembre 2025, sans réutiliser un numéro du
t09 ; folios FOL/2026/0084 le 22/02 et 0189 le 02/09. Les volumes du
regroupement par origine (348 mouvements, 22 968 points depuis novembre
2025) restent sous ces séquences ; ils ne peuvent pas suivre la tuile
« Points fidélité émis » du t15 (12 480 points du 30/09 au 14/10,
t15_direction.py:547), qui demanderait une centaine de folios sur la
période quand le t03 n'en compte que 211 depuis l'ouverture
(t03_folio.py:456). Autres clients fictifs ajoutés : Boris Ndzana (client
du bar), Carine Owona, Gaëlle Nkeng, Hugues Mbida, Nadège Abena, Pauline
Ekotto (t02_planning.py:254), Sandrine Mvondo, Thierry Etoundi ; Patrick
Nkoulou, Brigitte Essomba, Martin Ebode, Samuel Etoga et Paul Essomba
viennent des tutoriels 3, 4 et 9 ; téléphones de la plage de fiction de la
série (t10_ardoises.py, TELEPHONES ; demo.CLIENT_TEL). Les tickets du bar d'Estelle sont réglés
en espèces (voir écart 2).

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/053,
054, 055, 056, 602, 613 ; captures de lecture prises pour ce tutoriel sur la
base MuK (compte demo.direction) : menu Fidélité, panneau de recherche,
regroupement par origine, Clients VIP & VVIP sans la facette, fiche d'un
client VIP, « Points de … ».

Écarts relevés, rejoués tels quels (voir le rapport) :
1. « Clients VIP / VVIP » s'ouvre avec la facette « Factures clients »
   (search_default_customer, loyalty_move_views.xml:52 ; customer_rank > 0,
   account/views/partner_view.xml:341) : les VIP qui n'ont ni facture ni
   ticket de caisse dans une session clôturée (prestations seules :
   pos_session.py:1013-1015) n'apparaissent qu'une fois la facette retirée
   (10 cartes, puis 12).
2. La taxe de séjour rapporte des points (le folio est crédité sur son total,
   hooks.py:88) ; un ticket réglé en « Note de chambre » ou une prestation
   reportée au folio sont crédités deux fois (hooks.py:42-45, 87-90 ;
   aite_hotel_pos_link/models/pos_order.py:146-152 ; aite_slot_booking/
   models/booking_booking.py:340-342).
3. La carte des clients VIP et la liste n'affichent ni le statut ni les
   points, contrairement à l'aide de l'action (loyalty_move_views.xml:55).
4. Les sommes de groupe de « Montant de base » s'affichent avec « ,00 » en
   FCFA (formatage sans devise), alors que les lignes n'ont pas de décimale.
5. « Points de Estelle Ngono » : l'élision n'est pas faite
   (res_partner.py:45).
"""

import math
import os
import re
import textwrap
from datetime import date, timedelta

import demo
from ecrans import APPS_PROFIL, ICONES, e, entree, fenetre_muk, fenetre_pos, icone, navigateur, recherche, vue_libre
from marketing import bulle, dezoom, reaction, zoom
from moteur import (anneau, cacher, choisir, classe, clic, curseur, defiler, fermer, montrer, ouvrir, pause, saisir,
                    texte, vue)

NOM, ROLE = demo.POSTES['direction']
CAISSIER = demo.POSTES['caisse'][0]
CLIENTE = demo.CLIENT
BAR = 'Bar de la terrasse'
AUJOURDHUI = date(2026, 10, 16)
MENUS = ['Direction', 'Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente',
         'Facturation', 'Fidélité', 'Gouvernante', 'Configuration']

ICI = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(ICI, '..', '..', '..', 'addons', 'aite_loyalty', 'models', 'loyalty_move.py')


# ------------------------------------------------------ le vrai calcul --

def _fonction_du_module(nom):
    """Une méthode statique d'aite_loyalty (``_points_for``, ``_tier_for``),
    extraite du module et exécutée telle quelle."""
    with open(MODULE, encoding='utf-8') as f:
        src = f.read()
    m = re.search(r'^    def %s\(.*?(?=^    @|^    # -{10,})' % nom, src, re.S | re.M)
    ns = {'math': math}
    exec(compile(textwrap.dedent(m.group(0)), MODULE, 'exec'), ns)
    return ns[nom]


POINTS_POUR = _fonction_du_module('_points_for')
STATUT_POUR = _fonction_du_module('_tier_for')
# Valeurs par défaut de la société (res_config_settings.py:19-39).
TAUX, MINIMUM, FENETRE = 1.0, 1000.0, 12
CFG = {'vip_spend': 500000.0, 'vip_visits': 10, 'vvip_spend': 2000000.0, 'vvip_visits': 25, 'vvip_domains': 3}
ORIGINES = {'pos': 'Restaurant / Boutique (POS)', 'hotel': 'Hébergement (folio)', 'slot_space': 'Espace VIP / VVIP',
            'slot_spa': 'SPA', 'slot_hair': 'Coiffure', 'slot_pressing': 'Pressing', 'manual': 'Ajustement manuel'}
STATUTS = {'standard': 'Standard', 'vip': 'VIP', 'vvip': 'VVIP'}
MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
NBSP = ' '


def points(montant):
    return POINTS_POUR(montant, TAUX, MINIMUM)


def entier(n):
    """Un entier au format français d'Odoo (espace insécable des milliers)."""
    s = '{:,}'.format(abs(int(n))).replace(',', NBSP)
    return ('-' if n < 0 else '') + s


def fcfa(n):
    """Un montant en XAF, tel que l'affiche le champ monétaire : « 12 500 FCFA »."""
    return entier(n) + NBSP + 'FCFA'


def somme_groupe(n):
    """La somme d'un groupe, sans devise et à deux décimales (écart 4)."""
    return entier(n) + ',00'


def jma(d):
    return d.strftime('%d/%m/%Y')


# Les tickets de la caisse du bar, recalés sur la série : la caisse a ouvert le
# 04/05/2026 (t12_ventes.py:544) et vend environ 8,3 tickets par jour (108 du 01
# au 13/10, t12_ventes.py:380 ; environ 1 350 au soir du 13/10, sur les 1 440 de toutes
# les caisses, t12_ventes.py:550) : le n° d'un ticket du jour d tombe entre
# 8,3 × (d − 04/05) et 8,3 × (d − 04/05 + 1). Brigitte Essomba a le /1360 le
# 14/10 au soir, Martin Ebode le /1377 le 16/10 à 22:41 (t04_note_chambre.py).
# Estelle Ngono prend son premier verre au bar le 10/07.
OUVERTURE_BAR, PAR_JOUR = date(2026, 5, 4), 8.3
TICKETS_BAR = {date(2026, 7, 10): 560, date(2026, 8, 14): 851, date(2026, 9, 12): 1091, date(2026, 9, 19): 1149,
               date(2026, 10, 3): 1266, date(2026, 10, 16): 1375}
for _d, _n in TICKETS_BAR.items():
    _j = (_d - OUVERTURE_BAR).days
    assert PAR_JOUR * _j <= _n <= PAR_JOUR * (_j + 1), (_d, _n)


def ref_bar(n):
    """« Bar de la terrasse/1375 » : nom de la caisse, n° sur 4 chiffres (pos_config.py:476-486)."""
    return '%s/%04d' % (BAR, n)


# La séquence des prestations « RES/%(y)s/ » (sans remise à zéro annuelle :
# slot_sequence_data.xml:3-8), recalée sur t09_espaces.py:207-219 : le 15/10/2026,
# les réservations réalisées vont de RES/26/0133 à 0158, et la séquence en est
# vers 0140 au matin. Environ 0,4 réservation par jour depuis novembre 2025 ;
# un numéro déjà pris au t09 n'est jamais réutilisé.
NUMEROS_T09 = {119, 127, 133, 138, 141, 142, 145, 150, 153, 158, 159}


def ref_presta(d, n=None):
    """« RES/26/0137 » : la référence d'une prestation réalisée le jour ``d``."""
    if n is None:
        n = 140 - round(0.405 * (date(2026, 10, 15) - d).days)
        while n in NUMEROS_T09:
            n -= 1
    return 'RES/%02d/%04d' % (d.year % 100, n)


# --------------------------------------------- l'année d'Estelle Ngono --
# Elle habite Douala : réunions au salon VIP, spa, coiffure, pressing, un verre
# au bar après ses réunions depuis juillet, et trois séjours
# (folio = nuits + taxe de séjour ; le dernier avec ses quatre petits-déjeuners).
D = date
AUJOURDHUI_FOLIO = 112800                          # t03_folio.py:204-206, :428


def _folio_du_t03():
    """Le total TTC de FOL/2026/0214 au tutoriel 3, lu dans son scénario : si le
    t03 change, ce tutoriel le signale au lieu de diverger en silence."""
    with open(os.path.join(ICI, 't03_folio.py'), encoding='utf-8') as f:
        m = re.search(r"\('0214', CLIENT, (\d+),", f.read())
    return int(m.group(1)) if m else None


assert _folio_du_t03() in (None, AUJOURDHUI_FOLIO), 't11 : FOL/2026/0214 vaut %s au t03' % _folio_du_t03()
FOLIOS = {D(2026, 2, 22): ('FOL/2026/0084', 96000), D(2026, 9, 2): ('FOL/2026/0189', 144000),
          AUJOURDHUI: (demo.FOLIO, AUJOURDHUI_FOLIO)}
ANNEE = [
    (D(2025, 11, 14), 'slot_space', 90000), (D(2025, 11, 28), 'slot_hair', 12000),
    (D(2025, 12, 12), 'slot_space', 120000), (D(2025, 12, 20), 'slot_spa', 25000),
    (D(2026, 1, 16), 'slot_space', 120000), (D(2026, 1, 24), 'slot_hair', 12000),
    (D(2026, 2, 6), 'slot_pressing', 6000), (D(2026, 2, 13), 'slot_space', 120000),
    (D(2026, 2, 22), 'hotel', None), (D(2026, 2, 28), 'slot_spa', 25000), (D(2026, 3, 13), 'slot_space', 120000),
    (D(2026, 3, 28), 'slot_hair', 12000), (D(2026, 4, 10), 'slot_space', 120000), (D(2026, 4, 25), 'slot_spa', 25000),
    (D(2026, 5, 15), 'slot_space', 150000), (D(2026, 5, 22), 'slot_pressing', 7200),
    (D(2026, 5, 30), 'slot_hair', 12000), (D(2026, 6, 12), 'slot_space', 150000), (D(2026, 6, 27), 'slot_spa', 25000),
    (D(2026, 7, 10), 'slot_space', 90000), (D(2026, 7, 10), 'pos', 15000), (D(2026, 7, 25), 'slot_hair', 12000),
    (D(2026, 8, 14), 'slot_space', 120000), (D(2026, 8, 14), 'pos', 17500), (D(2026, 8, 29), 'slot_spa', 25000),
    (D(2026, 9, 2), 'hotel', None), (D(2026, 9, 12), 'slot_space', 150000), (D(2026, 9, 12), 'pos', 13500),
    (D(2026, 9, 19), 'pos', 15500), (D(2026, 9, 26), 'slot_hair', 12000), (D(2026, 10, 3), 'slot_spa', 25000),
    (D(2026, 10, 3), 'pos', 8500), (D(2026, 10, 10), 'slot_space', 150000),
    (AUJOURDHUI, 'hotel', None), (AUJOURDHUI, 'pos', 12500),
]


def _mouvements():
    """[(date, origine, référence, montant, points)], dans l'ordre de création."""
    mvts = []
    for d, origine, montant in ANNEE:
        if origine == 'hotel':
            ref, montant = FOLIOS[d]
        elif origine == 'pos':
            ref = ref_bar(TICKETS_BAR[d])
        else:
            ref = ref_presta(d)
        mvts.append((d, origine, ref, montant, points(montant)))
    return mvts


MVTS = _mouvements()
assert len({m[2] for m in MVTS}) == len(MVTS), 'deux mouvements sur la même référence'
RETRAIT = -1000                                   # « Utilisation : nuit offerte »
SOLDE = sum(m[4] for m in MVTS)                   # le solde avant la nuit offerte
SOLDE_APRES = SOLDE + RETRAIT


def _historique_statut():
    """Le recalcul quotidien (loyalty_move.recompute_tiers) rejoué jour par jour :
    chaque matin, les mouvements des 12 derniers mois (créés la veille au plus
    tard) donnent le statut. Rend [(jour, ancien, nouveau)]."""
    changements, statut = [], 'standard'
    jour = MVTS[0][0] + timedelta(days=1)
    while jour <= AUJOURDHUI:
        debut = jour.replace(year=jour.year - 1)
        fenetre = [m for m in MVTS if debut <= m[0] < jour and m[4] > 0]
        depenses = sum(m[3] for m in fenetre)
        visites = len({m[0] for m in fenetre})
        familles = len({m[1] for m in fenetre if m[1] != 'manual'})
        nouveau = STATUT_POUR(depenses, visites, familles, CFG)
        if nouveau != statut:
            changements.append((jour, statut, nouveau))
            statut = nouveau
        jour += timedelta(days=1)
    return changements


CHANGEMENTS = _historique_statut()
assert [(c[0], c[2]) for c in CHANGEMENTS] == [(D(2026, 3, 1), 'vip'), (D(2026, 10, 11), 'vvip')], CHANGEMENTS
DEPUIS = CHANGEMENTS[-1][0]                       # « Statut depuis »
DEPENSES_12M = sum(m[3] for m in MVTS)
assert DEPENSES_12M >= CFG['vvip_spend'] and SOLDE_APRES > 0


def court(d, annee=False):
    """Une date de l'historique, au format d'Odoo 18 en français : « 11 oct. 2026 »."""
    return '%d %s%s' % (d.day, MOIS[d.month - 1], (' %d' % d.year) if annee else '')


# ------------------------------------------------------------ icônes --
# Dessinées ici (fa-star, fa-cog, fa-truck, fa-pencil-square-o, oi-group…) :
# ecrans.ICONES n'a pas ces glyphes, on ne le modifie pas.
ETOILE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 '
          '3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg>')
ENGRENAGE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.3 2h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 '
             '1.9 2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 '
             '1.5-2.2-.8-1.9L2 13.7v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8z"/><circle cx="12" cy="12" r="3.4" '
             'fill="#fff"/></svg>')
CALQUES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">'
           '<path d="M12 3l9 4.5-9 4.5-9-4.5z" fill="currentColor"/><path d="M3 12l9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/></svg>')
CRAYON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">'
          '<path d="M11 4H5a1 1 0 00-1 1v14a1 1 0 001 1h14a1 1 0 001-1v-6"/><path d="M17.5 3.5l3 3L12 15H9v-3z"/></svg>')
CAMION = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 6h12v10H2zM14 9h4l3 3.5V16h-7z"/>'
          '<circle cx="6.5" cy="17.5" r="2.2" fill="#fff" stroke="currentColor" stroke-width="1.6"/>'
          '<circle cx="17" cy="17.5" r="2.2" fill="#fff" stroke="currentColor" stroke-width="1.6"/></svg>')
KANBAN = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="4" width="7.5" height="16" rx="1"/>'
          '<rect x="12.5" y="4" width="8.5" height="7.5" rx="1"/></svg>')
SILHOUETTE = ('<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMax slice"><rect width="100" height="100" '
              'fill="#E9ECEF"/><circle cx="50" cy="40" r="19" fill="#BFC5CC"/><path d="M12 104c2-25 19-38 38-38s36 13 '
              '38 38z" fill="#BFC5CC"/></svg>')
APPAREIL = ('<svg viewBox="0 0 48 48" fill="none" stroke="#ADB5BD" stroke-width="2.4" stroke-linejoin="round">'
            '<path d="M6 15h8l3-5h12l3 5h8v22H6z"/><circle cx="24" cy="25" r="7"/><circle cx="36" cy="34" r="7" '
            'fill="#fff"/><path d="M36 30.5v7M32.5 34h7"/></svg>')
ROBOT = ('<svg viewBox="0 0 40 40"><rect width="40" height="40" rx="6" fill="#3B4A5A"/><rect x="9" y="12" width="22" '
         'height="17" rx="7" fill="#fff"/><circle cx="16" cy="20.5" r="2.4" fill="#3B4A5A"/><circle cx="24" cy="20.5" '
         'r="2.4" fill="#3B4A5A"/><path d="M20 7v5" stroke="#fff" stroke-width="2"/></svg>')
LIVRE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h12a2 2 0 012 2v14H7a2 2 0 01-2-2z" '
         'opacity=".95"/><path d="M7 19h12v2H7a2 2 0 010-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>')
# le bouton des colonnes optionnelles au bout de l'en-tête (la colonne Note est
# optional="hide" : loyalty_move_views.xml:14 ; icône oi-settings-adjust :
# odoo18/addons/web/static/src/views/list/list_renderer.xml:48-51), dessiné
# comme au t06
REGLAGES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
            '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>')
AVION = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2.4 11.1L21.6 3.2l-5.4 17.6-4.7-6.3z"/></svg>'


def personnage(classe_, initiale, retirer=()):
    """La pastille du personnage passe à celui qui agit (comme au t04) : une
    classe sur #tu-perso, le nom et le rôle rendus par ::before / ::after."""
    return [classe('#tu-perso', ajouter=[classe_] if classe_ else [], retirer=list(retirer)),
            texte('#tu-perso .av', initiale, avec=True)]


def ico(svg, classe_='ico'):
    return '<span class="%s">%s</span>' % (classe_, svg)


def bt(ident, libelle, style='gris', svg=None, extra=''):
    return '<span class="bt %s%s"%s>%s%s</span>' % (style, extra, ' id="%s"' % ident if ident else '',
                                                     ico(svg) if svg else '', e(libelle))


def pager(texte_, ident=None):
    return ('<span class="pager"%s>%s</span><span class="t11-fl"><i>‹</i><i>›</i></span>'
            % (' id="%s"' % ident if ident else '', e(texte_)))


def vues_bt(actif=0):
    """Le sélecteur de vues d'une action kanban / liste."""
    return '<span class="t11-vues">%s</span>' % ''.join(
        '<i class="%s">%s</i>' % ('on' if i == actif else '', s) for i, s in enumerate((KANBAN, ICONES['liste'])))


# ----------------------------------------------------- la caisse du bar --
TICKET = 12500                                     # le total du ticket d'Estelle
# téléphones de la plage de fiction, ceux de t10_ardoises.py (TELEPHONES) et de t04_note_chambre.py
PROCHES = [('Boris Ndzana', 'Akwa Douala Cameroun', '+237 6 00 00 00 40', 'boris.ndzana@exemple.cm'),
           ('Brigitte Essomba', 'Bonamoussadi Douala Cameroun', '+237 6 00 00 00 32', 'brigitte.essomba@exemple.cm'),
           ('Carine Owona', 'Bali Douala Cameroun', '+237 6 00 00 00 41', 'carine.owona@exemple.cm'),
           (CLIENTE, 'Bonapriso Douala Cameroun', demo.CLIENT_TEL, demo.CLIENT_MAIL)]


def ligne_client(nom, adresse, tel, mail, ident=None):
    return ('<div class="t11-pr"%s><span><b>%s</b></span><span class="t11-pr-a">%s</span><span class="t11-pr-c">'
            '<span>%s%s</span><span>%s%s</span></span><span class="t11-pr-m">≡</span></div>'
            % (' id="%s"' % ident if ident else '', e(nom), e(adresse), ico(ICONES['telephone']), e(tel),
               ico(AVION), e(mail)))


TOUS = ''.join(ligne_client(*p) for p in PROCHES)
FILTRES_ = ligne_client(*PROCHES[3], ident='t11-pr-est') + '<div class="t11-plus"><span class="bt primaire">' \
                                                           'Rechercher plus</span></div>'
DIALOGUE = ('<div class="voile masque" id="t11-pdlg-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="t11-pdlg masque" id="t11-pdlg" data-layout-allow-overlap data-layout-allow-occlusion>'
            '<div class="t11-pdlg-h"><span class="bt primaire">Créer</span>%s</div>'
            '<div class="t11-pdlg-b"><div class="t11-pr t11-pr-t"><span>Nom</span><span>Adresse</span>'
            '<span>Contact</span><span></span></div><div class="pile"><div id="t11-pr-all">%s</div>'
            '<div class="masque" id="t11-pr-f">%s</div></div></div>'
            '<div class="t11-pdlg-p"><span class="bt gris">Ignorer</span></div></div>'
            % (entree('t11-pq', 'Recherche des clients...', classe='entree t11-pq'), TOUS, FILTRES_))

PAVE = ''.join('<span class="pk%s">%s</span>' % (c, e(t)) for t, c in (
    ('1', ''), ('2', ''), ('3', ''), ('+10', ' vert'), ('4', ''), ('5', ''), ('6', ''), ('+20', ' vert'), ('7', ''),
    ('8', ''), ('9', ''), ('+50', ' vert'), ('+/-', ' jaune'), ('0', ''), (',', ' rose'), ('⌫', ' rouge')))
MODES = ''.join('<div class="pos-mode" id="%s">%s<span>%s</span></div>' % (i, icone(ic), e(lib))
                for i, ic, lib in (('t11-esp', 'billet', 'Espèces'), ('t11-ndc', 'carte', 'Note de chambre'),
                                   ('t11-ard', 'carte', 'Ardoise client')))
PAIEMENT = (
    '<div class="vue initiale" id="t11-pay"><div class="pos-vente">'
    '<div class="pos-g"><div class="pos-modes">%s</div>'
    '<div class="pos-cf"><span id="t11-cli-bt">%s<span id="t11-cli-n">Client</span></span>'
    '<span>%sFacture<i></i></span></div>'
    '<div class="pos-ardoise">%sMettre sur ardoise</div><div class="pos-pave">%s</div>'
    '<div class="pos-rv"><span>Retour</span><span class="v t11-off" id="t11-valider">Valider</span></div></div>'
    '<div class="pos-d pos-pd"><div class="pos-du">%s</div>'
    '<div class="t11-pmsg" id="t11-pmsg">Veuillez sélectionner un mode de paiement</div>'
    '<div class="t11-pz"><div class="t11-pstat masque" id="t11-pstat"><span>Monnaie</span><span>%s</span></div>'
    '<div class="pos-pl t11-pl masque" id="t11-pl"><span>Espèces</span><span>%s</span><span class="x">×</span></div>'
    '</div></div></div></div>'
    % (MODES, icone('personne'), icone('document'), ico(LIVRE), PAVE, fcfa(TICKET), fcfa(0), fcfa(TICKET)))
# n° de suivi : session du 16/10 (00137) % 10 × 100 + 6e ticket du jour (/1370 à /1375) : pos_order.py:58-60
CAISSE = fenetre_pos('t11-pos', [PAIEMENT], CAISSIER, numero='706', calques=DIALOGUE)


# -------------------------------------------------- Mouvements de points --
COLS = '40px 142px 214px 290px 1fr 206px 104px 26px'
TETE = ('<div class="tete" style="grid-template-columns:%s"><span class="cb"></span><span>Date</span><span>Client</span>'
        '<span>Origine</span><span>Référence</span><span class="d">Montant de base</span><span class="d">Points</span>'
        '<span class="t11-opt">%s</span></div>' % (COLS, REGLAGES))


def ligne_mvt(ident, d, client, origine, ref, montant, pts, rouge=False):
    return ('<div class="ligne%s" id="%s" style="grid-template-columns:%s"><span class="cb"></span><span>%s</span>'
            '<span class="ell">%s</span><span class="ell">%s</span><span class="ell">%s</span><span class="d">%s</span>'
            '<span class="d" id="%s-pts">%s</span></div>'
            % (' t11-rouge' if rouge else '', ident, COLS, jma(d), e(client), e(ORIGINES[origine]), e(ref),
               fcfa(montant), ident, entier(pts)))


D15 = date(2026, 10, 15)
JOURNAL = [  # (date, client, origine, référence, montant) — du plus récent au plus ancien (date desc, id desc)
    (AUJOURDHUI, CLIENTE, 'pos', ref_bar(TICKETS_BAR[AUJOURDHUI]), TICKET),
    (AUJOURDHUI, 'Patrick Nkoulou', 'pos', ref_bar(TICKETS_BAR[AUJOURDHUI] - 1), 7500),
    (AUJOURDHUI, CLIENTE, 'hotel', demo.FOLIO, FOLIOS[AUJOURDHUI][1]),
    # le jeudi 15/10 : les prestations réalisées de t09_espaces.py:242-254, de la
    # dernière à la première (le massage de Brigitte Essomba, reporté sur
    # FOL/2026/0210 ; le pressing de Samuel Etoga), et le départ de Claire Durand
    # (RES/2026/0201, 401, 14-15/10 : t02_planning.py:259, :288 ; 120 000 + 3 000
    # de taxe : t03_folio.py:416-420)
    (D15, 'Brigitte Essomba', 'slot_spa', ref_presta(D15, 158), 27000),
    (D15, 'Rachel Bilong', 'slot_spa', ref_presta(D15, 150), 23000),
    (D15, 'Paul Essomba', 'slot_space', ref_presta(D15, 133), 45000),
    (D15, 'Carine Ndongo', 'slot_hair', ref_presta(D15, 142), 19000),
    (D15, 'Claire Durand', 'hotel', 'FOL/2026/0201', 123000),
    (D15, 'Linda Ewané', 'slot_spa', ref_presta(D15, 145), 27000),
    (D15, 'Yves Tchana', 'slot_hair', ref_presta(D15, 138), 6200),
    (D15, 'Samuel Etoga', 'slot_pressing', ref_presta(D15, 141), 4800),
]
assert JOURNAL[0][3] == MVTS[-1][2] and JOURNAL[2][3] == MVTS[-2][2]
assert not [m for m in MVTS if m[0] == D15], 'Estelle n\'a aucune prestation le 15/10 (massage : Brigitte, t09)'
# (origine, nombre de mouvements, somme des montants, somme des points) depuis
# les premiers mouvements (novembre 2025), dans l'ordre d'affichage d'Odoo 18
# (clé de la sélection). Les volumes restent sous les séquences visibles dans la
# série au 16/10/2026 : 211 folios en tout (t03_folio.py:456), environ 0,55
# par jour depuis FOL/2026/0084 le 22/02 ; environ 1 440 tickets depuis le
# 04/05 (t12_ventes.py:550), jusqu'à Bar de la terrasse/1377, Restaurant/0083
# et Boutique/0018 (t04_note_chambre.py, ATTENTE) ; prestations jusqu'à
# RES/26/0159 (t09_espaces.py:253). Les points d'un groupe
# ne dépassent jamais montant ÷ 1 000 (partie entière ligne par ligne).
GROUPES = [('hotel', 168, 19824000, 19790), ('manual', 5, None, -1650), ('pos', 54, 745200, 718),
           ('slot_hair', 30, 345000, 330), ('slot_pressing', 26, 140400, 128), ('slot_spa', 34, 870400, 862),
           ('slot_space', 31, 2790000, 2790)]
NB_MVTS = sum(g[1] for g in GROUPES)
for _o, _n, _m, _p in GROUPES:
    _connus = [m[3] for m in MVTS if m[1] == _o] + [j[4] for j in JOURNAL if j[2] == _o and j[1] != CLIENTE]
    assert _n >= len(_connus) and (_m is None or (_m >= sum(_connus) and _p <= _m // 1000)), _o
LIGNES_J = ''.join(ligne_mvt('t11-l%d' % i, d, c, o, r, m, points(m)) for i, (d, c, o, r, m) in enumerate(JOURNAL))

PANNEAU = ('<div class="t11-panneau masque" id="t11-panneau" data-layout-allow-overlap data-layout-allow-occlusion>'
           '<div><div class="t11-pt">%sFiltres</div><div>Gains</div><div>Retraits</div><hr>'
           '<div>Ajouter un filtre personnalisé</div></div>'
           '<div><div class="t11-pt">%sRegrouper par</div><div>Client</div><div id="t11-g-origine">Origine</div>'
           '<div class="t11-car">Mois<b>▾</b></div><hr><div class="t11-car">Ajouter un groupe personnalisé<b>▾</b></div></div>'
           '<div><div class="t11-pt t11-fav">%sFavoris</div><div class="t11-car ell">Enregistrer la recherche actuelle'
           '<b>▾</b></div></div></div>' % (ico(ICONES['filtre']), ico(CALQUES), ico(ETOILE)))
CP_LIVRE = ('<div class="cp"><span class="titre">Mouvements de points</span>%s%s%s</div>'
            % (ico(ENGRENAGE, 't11-gear'), recherche((), 't11-livre-rech'), pager('1-80 / %d' % NB_MVTS)))
LIVRE_V = vue_libre('t11-livre', CP_LIVRE + '<div class="liste">%s%s</div>%s' % (TETE, LIGNES_J, PANNEAU),
                    initiale=True)

# --------------------------------------------- regroupé par « Origine » --
TOTAL_PTS = sum(g[3] for g in GROUPES)
FACETTE_ORIG = ('<div class="recherche" id="t11-orig-rech">%s<span class="facette t11-fg"><span class="fic">%s</span>'
                '<span class="ell">Origine</span><span class="fx">×</span></span><span class="ph">Rechercher…</span>'
                '<span class="deroule">▾</span></div>' % (icone('loupe', 'loupe'), CALQUES))
CP_ORIG = ('<div class="cp"><span class="titre">Mouvements de points</span>%s%s%s</div>'
           % (ico(ENGRENAGE, 't11-gear'), FACETTE_ORIG, pager('1-7 / 7')))
LIGNES_G = ''.join(
    '<div class="t11-grp" id="t11-o-%s" style="grid-template-columns:%s"><span class="cb"></span>'
    '<span class="t11-gl">▸ %s (%d)</span><span class="d">%s</span><span class="d">%s</span></div>'
    % (o, COLS, e(ORIGINES[o]), n, somme_groupe(m) if m else '', entier(p)) for o, n, m, p in GROUPES)
ORIGINE_V = vue_libre('t11-origine', CP_ORIG + (
    '<div class="liste">%s<div id="t11-o-grps">%s</div><div class="total" id="t11-o-tot" style="grid-template-columns:%s">'
    '<span></span><span></span><span></span><span></span><span></span><span></span><span class="d">%s</span></div></div>'
    % (TETE, LIGNES_G, COLS, entier(TOTAL_PTS))))


# ----------------------------------------------- Clients VIP & VVIP --
# Les clients VIP et VVIP de l'établissement, dans l'ordre alphabétique de la
# vue ; ``facture`` : leur customer_rank est positif, donc ils restent visibles
# sous la facette « Factures clients » (customer_rank > 0, account/views/
# partner_view.xml:341). Une facture validée l'augmente (séjour facturé), et la
# clôture d'une session de caisse aussi, pour le client de chaque ticket non
# facturé (point_of_sale/models/pos_session.py:1013-1015) : les clients du bar
# y sont donc (Boris Ndzana, Patrick Nkoulou, Brigitte Essomba : ticket Bar de la
# terrasse/1360 au t04, ardoise ARD/0039), comme Pauline Ekotto, en 205 du 06 au
# 09/10 (t02_planning.py:254). Seules Carine Owona et Nadège Abena, servies
# uniquement en prestations et en espaces, n'y sont pas.
VIP = [('Boris Ndzana', 'boris.ndzana@exemple.cm', True), ('Brigitte Essomba', 'brigitte.essomba@exemple.cm', True),
       ('Carine Owona', 'carine.owona@exemple.cm', False), (CLIENTE, demo.CLIENT_MAIL, True),
       ('Gaëlle Nkeng', 'gaelle.nkeng@exemple.cm', True), ('Hugues Mbida', 'hugues.mbida@exemple.cm', True),
       ('Martin Ebode', 'martin.ebode@exemple.cm', True), ('Nadège Abena', 'nadege.abena@exemple.cm', False),
       ('Patrick Nkoulou', 'patrick.nkoulou@exemple.cm', True), ('Pauline Ekotto', 'pauline.ekotto@exemple.cm', True),
       ('Sandrine Mvondo', 'sandrine.mvondo@exemple.cm', True), ('Thierry Etoundi', 'thierry.etoundi@exemple.cm', True)]


def carte_vip(prefixe, nom, mail):
    ident = '%s-%s' % (prefixe, 'estelle' if nom == CLIENTE else re.sub(r'\W', '', nom.split()[0].lower()))
    return ('<div class="t11-kc" id="%s"><span class="t11-av">%s</span><div class="t11-kt"><b>%s</b>'
            '<span>Douala, Cameroun</span><span class="ell">%s</span></div></div>' % (ident, SILHOUETTE, e(nom), e(mail)))


def cp_vip(facette, pager_):
    f = [('t11-vipf-f', 'Factures clients')] if facette else []
    rech = recherche(f)
    if facette:
        rech = rech.replace('<span class="fx">×</span>', '<span class="fx" id="t11-vipf-fx">×</span>', 1)
    return ('<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">Clients VIP &amp; VVIP</span>'
            '%s%s%s%s</div>' % (ico(ENGRENAGE, 't11-gear'), rech, pager(pager_), vues_bt()))


FACTURES = [v for v in VIP if v[2]]
VIP_F = vue_libre('t11-vip-f', cp_vip(True, '1-%d / %d' % (len(FACTURES), len(FACTURES)))
                  + '<div class="t11-kg">%s</div>' % ''.join(carte_vip('t11-kf', n, m) for n, m, _ in FACTURES))
VIP_V = vue_libre('t11-vip', cp_vip(False, '1-%d / %d' % (len(VIP), len(VIP)))
                  + '<div class="t11-kg">%s</div>' % ''.join(carte_vip('t11-k', n, m) for n, m, _ in VIP))
RANG = [v[0] for v in VIP].index(CLIENTE) + 1


# ------------------------------------------------- la fiche d'Estelle --
def stat(ident, svg, libelle, valeur):
    return ('<span class="t11-stat"%s>%s<span class="t11-st"><span>%s</span>%s</span></span>'
            % (' id="%s"' % ident if ident else '', ico(svg, 't11-sic'), e(libelle),
               '<b%s>%s</b>' % (' id="%s-v"' % ident if ident else '', e(valeur)) if valeur is not None else ''))


SEJOURS = len(FOLIOS)
STATS = ''.join([stat(None, CRAYON, 'Facturé', fcfa(sum(m for _, m in FOLIOS.values()))),
                 stat(None, ICONES['carte'], 'Achats', '0'),
                 stat(None, CAMION, 'Taux de livraisons dans les temps', 'Pas encore de données'),
                 stat(None, ICONES['liste'], 'Lot/Numéros de série', None),
                 stat(None, ICONES['lit'], 'Séjours', str(SEJOURS)),
                 stat(None, ICONES['fiche'], 'Fiches', str(SEJOURS)),
                 stat('t11-st-pts', ETOILE, 'Points', entier(SOLDE))])
CP_FICHE = ('<div class="cp t11-cpf"><span class="bt contour">Nouveau</span><div class="fil"><span class="parent">'
            'Clients VIP &amp; VVIP</span><span class="ref">%s %s</span></div><div class="t11-stats">%s</div>%s</div>'
            % (e(CLIENTE), ico(ENGRENAGE, 't11-gear'), STATS, pager('%d / %d' % (RANG, len(VIP)))))


def champ_f(libelle, valeur='', ph=None, aide=False, ident=None, classe_=''):
    v = '<span class="t11-ph">%s</span>' % e(ph) if ph else valeur
    return ('<div class="t11-fc%s"%s><span class="l">%s%s</span><span class="v">%s</span></div>'
            % (classe_, ' id="%s"' % ident if ident else '', e(libelle), '<sup class="t11-aide">?</sup>' if aide else '',
               v))


GAUCHE_F = ('<div class="t11-adr"><div class="t11-fc"><span class="l t11-sel">Contact</span><span class="v">'
            '<span class="t11-u">Bonapriso</span><span class="t11-u t11-ph">Rue 2...</span>'
            '<span class="t11-trio"><span class="t11-u">Douala</span><span class="t11-u t11-ph">État</span>'
            '<span class="t11-u t11-ph ell">Code postal</span></span><span class="t11-u">Cameroun</span></span></div>'
            '%s</div>' % champ_f('N° TVA', ph='/ si non applicable', aide=True))
BADGE = ('<div id="t11-badge">%s%s</div>'
         % (champ_f('Statut client', '<span class="t11-badge">VVIP</span>'),
            champ_f('Statut depuis', jma(DEPUIS))))
DROITE_F = ''.join([champ_f('Poste', ph='par ex. Directeur Commercial'), champ_f('Téléphone', e(demo.CLIENT_TEL)),
                    champ_f('Mobile'), champ_f('E-mail', e(demo.CLIENT_MAIL)),
                    champ_f('Site Web', ph='par ex. https://www.odoo.com'), champ_f('Titre', ph='par ex. Monsieur'),
                    champ_f('Langue', 'French / Français', aide=True), BADGE,
                    champ_f('Étiquettes', ph='par ex. "B2B", "VIP", "Conseil", ...')])
FEUILLE = ('<div class="t11-feuille"><div class="t11-radio"><i class="on"></i>Particulier<i></i>Société</div>'
           '<div class="t11-photo">%s</div><div class="t11-nom">%s</div>'
           '<div class="t11-soc t11-ph">Nom de la société …</div>'
           '<div class="t11-cols"><div>%s</div><div>%s</div></div>'
           '<div class="onglets t11-ong"><span class="onglet actif">Contacts &amp; Adresses</span>'
           '<span class="onglet">Ventes &amp; Achats</span><span class="onglet">Facturation</span>'
           '<span class="onglet">Hôtel</span><span class="onglet">Notes internes</span></div>'
           '<span class="bt gris t11-ajout">Ajouter</span></div>' % (APPAREIL, e(CLIENTE), GAUCHE_F, DROITE_F))


def message_suivi(ident, jour, ancien, nouveau):
    return ('<div class="t11-sep"><span>%s</span></div><div class="t11-msg" id="%s"><span class="t11-bot">%s</span>'
            '<div><div class="t11-auteur"><b>OdooBot</b><small>%s, 06:12</small></div>'
            '<div class="t11-suivi">• <b class="t11-old">%s</b><span class="t11-fle">→</span><b class="t11-new">%s</b>'
            '<i>(Statut client)</i></div></div></div>'
            % (court(jour, True), ident, ROBOT, court(jour), STATUTS[ancien], STATUTS[nouveau]))


CHATTER = ('<div class="t11-chatter"><div class="ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
           '<span class="bt gris">Note</span><span class="bt gris">%sActivités</span></div>%s</div>'
           % (icone('message'), icone('horloge'),
              ''.join(message_suivi('t11-ch-m%d' % (i + 1), j, a, n)
                      for i, (j, a, n) in enumerate(reversed(CHANGEMENTS)))))
FICHE_V = vue_libre('t11-fiche', CP_FICHE + FEUILLE + CHATTER)

# ------------------------------------------------------- Ajuster des points --
AJUSTER = (
    '<div class="voile masque" id="t11-as-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque" id="t11-as" style="top:150px;width:1060px;margin-left:-530px" '
    'data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="m-tete"><span>Ajuster des points</span><span class="m-x">%s</span></div>'
    '<div class="m-corps"><div class="m-grille un">'
    '<div class="m-ch"><span class="l">Client</span><span class="v">%s</span></div>'
    '<div class="m-ch"><span class="l">Points (±)<sup class="t11-aide">?</sup></span><span class="v">%s</span></div>'
    '<div class="m-ch"><span class="l">Motif</span><span class="v">%s</span></div></div></div>'
    '<div class="m-pied">%s%s</div></div>'
    % (ICONES['x'], entree('t11-as-cli', '', classe='entree t11-ligne t11-m2o'),
       entree('t11-as-pts', '', '0', classe='entree t11-ligne'),
       entree('t11-as-mot', 'Geste commercial, correction…', classe='entree t11-ligne'),
       bt('t11-appl', 'Appliquer', 'primaire'), bt(None, 'Annuler')))

# ------------------------------------------------- Points de Estelle Ngono --
HISTO = [(AUJOURDHUI, 'manual', 'Ajustement', 0, RETRAIT)] + [(d, o, r, m, p) for d, o, r, m, p in reversed(MVTS)]
LIGNES_H = ''.join(ligne_mvt('t11-h%d' % i, d, CLIENTE, o, r, m, p, rouge=p < 0) for i, (d, o, r, m, p) in enumerate(HISTO))
HAUT_LISTE = 56 * len(HISTO) + 54
VISIBLE = 738 - 80 - 54
CP_HIST = ('<div class="cp"><div class="fil"><span class="parent">Clients VIP &amp; VVIP<i>/</i>%s</span>'
           '<span class="ref">Points de %s %s</span></div>%s%s</div>'
           % (e(CLIENTE), e(CLIENTE), ico(ENGRENAGE, 't11-gear'), recherche(), pager('1-%d / %d' % (len(HISTO), len(HISTO)))))
HIST_V = vue_libre('t11-hist', CP_HIST + (
    '<div class="liste t11-lh">%s</div><div class="t11-cadre"><div class="liste" id="t11-hist-defil">%s'
    '<div class="total" id="t11-h-tot" style="grid-template-columns:%s"><span></span><span></span><span></span><span>'
    '</span><span></span><span></span><span class="d">%s</span></div></div></div>'
    % (TETE, LIGNES_H, COLS, entier(SOLDE_APRES))))

# ---------------------------------------------------------------- la fenêtre --
DEROULANT = ('<div class="t11-dd masque" id="t11-dd" data-layout-allow-overlap data-layout-allow-occlusion>'
             '<div>Mouvements de points</div><div id="t11-dd-vip">Clients VIP / VVIP</div>'
             '<div id="t11-dd-adj">Ajuster des points</div></div>')
MUK = fenetre_muk('t11-app', 'Hôtel', MENUS, [LIVRE_V, ORIGINE_V, VIP_F, VIP_V, FICHE_V, HIST_V], actif='Fidélité',
                  societe=demo.SOCIETE, initiale=NOM[0], avatar='#854F0B', apps=APPS_PROFIL['direction'],
                  app_active='Hôtel', calques=AJUSTER)
_FID = '<span class="menu actif">Fidélité</span>'
assert MUK.count(_FID) == 1
MUK = MUK.replace(_FID, '<span class="menu actif t11-menu" id="t11-m-fid">Fidélité%s</span>' % DEROULANT)
ECRAN = navigateur(MUK + CAISSE)

CSS = """
/* la pastille du personnage : le caissier du bar, le temps de l'étape 1 */
#tu-perso.t11-pc > span:last-child { font-size: 0; }
#tu-perso.t11-pc > span:last-child::before { content: "@NOM@"; font-size: 21px; font-weight: 700; }
#tu-perso.t11-pc > span:last-child::after { content: " · @ROLE@"; font-size: 21px; white-space: pre; }
/* la barre de l'application Hôtel : neuf menus pour le Responsable */
#t11-app .o-haut { font-size: 16px; gap: 18px; z-index: 6; }
#t11-app .o-haut .nom-app { font-size: 21px; }
#t11-app .o-haut .societe { font-size: 16px; }
#t11-app .o-haut .menu.actif { font-weight: 600; }
.t11-menu { position: relative; }
.t11-dd { position: absolute; left: -16px; top: 40px; width: 300px; padding: 6px 0; background: #fff; border: 1px solid var(--o-filet);
  border-radius: 6px; box-shadow: 0 14px 34px rgba(0,0,0,.22); z-index: 29; }
.t11-dd div { height: 44px; display: flex; align-items: center; padding: 0 20px; font-size: 19px; font-weight: 400; color: var(--o-texte); white-space: nowrap; }
#t11-app .cp .titre { font-size: 24px; }
#t11-app .cp .pager { margin-left: auto; }
.t11-fl { display: flex; gap: 2px; margin-left: 12px; }
.t11-fl i { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40;
  font-style: normal; font-size: 24px; }
.t11-vues { display: flex; margin-left: 18px; }
.t11-vues i { width: 48px; height: 42px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40; }
.t11-vues i + i { border-left: 1px solid #fff; }
.t11-vues i.on { background: #DCE6EC; box-shadow: inset 0 0 0 1px var(--muk-prim); }
.t11-vues svg { width: 20px; height: 20px; }
.t11-gear { width: 18px; height: 18px; display: inline-flex; color: #343A40; margin-left: -6px; }
.t11-gear svg { width: 18px; height: 18px; }
#t11-app .cp .titre + .t11-gear { margin-left: 0; margin-right: 6px; }
.t11-opt { width: 20px; height: 20px; display: inline-flex; color: #495057; justify-self: end; }
.t11-opt svg { width: 20px; height: 20px; }
/* listes */
#t11-app .liste .tete span, #t11-app .liste .ligne span { white-space: nowrap; }
.liste .ligne.t11-rouge { color: #B02A37; }
.t11-panneau { position: absolute; left: 300px; top: 72px; width: 880px; padding: 18px 10px 18px; background: #fff; border: 1px solid var(--o-filet);
  border-radius: 6px; box-shadow: 0 14px 34px rgba(0,0,0,.2); display: grid; grid-template-columns: 1fr 1fr 1fr; z-index: 5; }
.t11-panneau > div { padding: 0 20px; border-left: 1px solid var(--o-filet); }
.t11-panneau > div:first-child { border-left: 0; }
.t11-panneau div div { height: 36px; display: flex; align-items: center; font-size: 18px; color: var(--o-texte); padding-left: 22px; white-space: nowrap; }
.t11-panneau .t11-pt { padding-left: 0; font-size: 20px; font-weight: 600; gap: 10px; margin-bottom: 4px; }
.t11-pt .ico { width: 18px; height: 18px; display: inline-flex; color: var(--o-texte); }
.t11-pt.t11-fav .ico { color: #E6A700; }
.t11-panneau hr { border: 0; border-top: 1px solid var(--o-filet); margin: 8px 0; }
.t11-car { justify-content: space-between; padding-right: 6px; }
.t11-car b { font-weight: 400; font-size: 14px; color: var(--o-texte-2); margin-left: 8px; }
.t11-fg .fic { padding: 6px; }
.t11-fg .fic svg { width: 18px; height: 18px; color: #fff; }
.t11-grp { display: grid; align-items: center; column-gap: 14px; padding: 0 22px 0 6px; height: 52px; border-bottom: 1px solid #EEF0F2;
  font-size: 19px; color: var(--o-texte); background: #fff; }
.t11-grp .t11-gl { grid-column: 2 / span 4; white-space: nowrap; }
/* Clients VIP & VVIP */
.t11-kg { position: absolute; left: 0; right: 0; top: 80px; padding: 16px 20px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.t11-kc { height: 112px; background: #fff; border: 1px solid var(--o-filet); display: flex; overflow: hidden; }
.t11-av { width: 104px; flex: none; display: block; }
.t11-av svg { width: 104px; height: 112px; display: block; }
.t11-kt { min-width: 0; padding: 12px 14px; display: flex; flex-direction: column; gap: 3px; font-size: 17px; color: var(--o-texte-2); }
.t11-kt b { font-size: 20px; font-weight: 700; color: var(--o-texte); margin-bottom: 2px; }
/* la fiche du contact */
.t11-cpf { gap: 12px; }
.t11-cpf .fil { width: 196px; flex: none; }
.t11-cpf .fil .ref { display: flex; align-items: center; gap: 12px; white-space: nowrap; }
.t11-stats { display: flex; margin-left: auto; }
.t11-stat { display: flex; align-items: center; gap: 7px; height: 56px; padding: 0 8px; border: 1px solid var(--o-filet); background: #fff; }
.t11-stat + .t11-stat { border-left: 0; }
.t11-sic { width: 20px; height: 20px; display: inline-flex; color: #5C636A; flex: none; }
.t11-sic svg { width: 20px; height: 20px; }
.t11-st { display: flex; flex-direction: column; line-height: 1.15; font-size: 13.5px; color: var(--o-texte-2); white-space: nowrap; }
.t11-st b { font-weight: 600; color: var(--o-lien); }
#t11-st-pts { background: #FFFDF5; }
#t11-st-pts .t11-sic { color: #4A7892; }
#t11-st-pts .t11-st { font-size: 16px; }
#t11-st-pts .t11-st b { font-size: 18px; }
.t11-feuille { position: absolute; left: 16px; top: 96px; width: 1030px; bottom: 0; background: #fff; border: 1px solid var(--o-filet);
  border-bottom: 0; padding: 18px 30px 0; color: var(--o-texte); }
.t11-radio { display: flex; align-items: center; gap: 10px; font-size: 18px; }
.t11-radio i { width: 18px; height: 18px; border-radius: 50%; border: 1px solid #ADB5BD; display: inline-block; margin-left: 10px; }
.t11-radio i:first-child { margin-left: 0; }
.t11-radio i.on { border: 6px solid var(--muk-prim); }
.t11-photo { position: absolute; right: 30px; top: 18px; width: 104px; height: 104px; border: 1px solid var(--o-filet); background: #F8F9FA;
  display: flex; align-items: center; justify-content: center; }
.t11-photo svg { width: 64px; height: 64px; }
.t11-nom { margin-top: 10px; width: 760px; font-size: 34px; border-bottom: 1px solid var(--o-filet); padding-bottom: 4px; }
.t11-soc { margin-top: 10px; width: 760px; font-size: 18px; border-bottom: 1px solid var(--o-filet); padding-bottom: 6px; }
.t11-ph { color: #8A939B; }
.t11-cols { margin-top: 18px; display: grid; grid-template-columns: 1fr 1fr; gap: 34px; }
.t11-fc { display: grid; grid-template-columns: 150px 1fr; align-items: center; min-height: 36px; font-size: 17px; }
.t11-fc .l { font-weight: 600; color: var(--o-texte); white-space: nowrap; }
.t11-fc .v { border-bottom: 1px solid #EEF0F2; padding: 4px 2px; min-height: 30px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t11-aide { color: var(--o-lien); font-size: 12px; margin-left: 3px; font-weight: 700; }
.t11-adr .t11-fc { align-items: start; }
.t11-sel { border-bottom: 1px solid var(--o-filet); padding: 4px 0; }
.t11-adr .v { border: 0; display: flex; flex-direction: column; gap: 2px; padding: 0; }
.t11-u { border-bottom: 1px solid #EEF0F2; padding: 4px 2px; min-height: 30px; }
.t11-trio { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
#t11-badge { background: #fff; }
.t11-badge { display: inline-flex; align-items: center; height: 26px; padding: 0 11px; border-radius: 999px; background: #C82333; color: #fff;
  font-size: 15px; font-weight: 700; }
#t11-badge .v { border-bottom: 0; }
.t11-ong { margin: 20px -30px 0; padding: 0 30px; }
.t11-ong .onglet { font-size: 17px; padding: 10px 14px; }
.t11-ajout { margin-top: 14px; height: 40px; font-size: 17px; }
.t11-chatter { position: absolute; right: 0; top: 80px; bottom: 0; width: 482px; background: #fff; border-left: 1px solid var(--o-filet); padding: 16px 18px; }
.t11-chatter .ch-bts .bt { height: 40px; font-size: 16px; padding: 0 11px; display: inline-flex; align-items: center; gap: 6px; }
.t11-chatter .ch-bts .bt .ico { width: 16px; height: 16px; display: inline-flex; }
.t11-sep { display: flex; align-items: center; gap: 14px; margin-top: 22px; font-size: 15px; color: var(--o-texte-3); }
.t11-sep::before, .t11-sep::after { content: ''; flex: 1; border-top: 1px solid #E5E7EB; }
.t11-msg { display: flex; gap: 12px; margin-top: 12px; font-size: 17px; color: var(--o-texte-2); }
.t11-bot { width: 40px; height: 40px; flex: none; display: block; }
.t11-bot svg { width: 40px; height: 40px; display: block; }
.t11-auteur b { color: var(--o-texte); margin-right: 8px; }
.t11-auteur small { font-size: 14px; color: var(--o-texte-3); }
.t11-suivi { margin-top: 6px; display: flex; align-items: center; gap: 6px; white-space: nowrap; }
.t11-old { color: var(--o-texte-3); }
.t11-new { color: #0B6E87; }
.t11-fle { color: var(--o-texte-3); }
.t11-suivi i { color: var(--o-texte-3); }
/* l'assistant Ajuster des points */
.m-ch .v .entree.t11-ligne { margin-top: 0; height: 46px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 4px; font-size: 19px; }
.m-ch .v .entree.t11-ligne .ph, .m-ch .v .entree.t11-ligne .val { left: 4px; }
.entree.t11-m2o::after { content: '▾'; position: absolute; right: 8px; top: 50%; transform: translateY(-50%); color: var(--muk-prim); font-size: 15px; }
/* l'historique de la cliente */
.t11-lh { position: relative; z-index: 2; }
.t11-cadre { position: absolute; left: 0; right: 0; top: 134px; bottom: 0; overflow: hidden; }
#t11-hist .fil .parent i { font-style: normal; margin: 0 10px; color: var(--o-texte-3); }
/* la caisse */
#t11-pos { z-index: 2; }
#t11-pos .pos-cherche { visibility: hidden; }
#t11-pos .pos-mode .ico { color: #495057; }
#t11-cli-bt { color: var(--o-texte); }
#t11-cli-bt.t11-choisi { color: var(--muk-prim); font-weight: 600; }
.pos-rv .v.t11-off { background: #A7BCC9; color: #fff; }
.t11-pmsg { position: absolute; left: 0; right: 0; top: 380px; text-align: center; font-size: 22px; color: var(--o-texte); }
.t11-pz { position: absolute; left: 60px; right: 60px; top: 300px; }
.t11-pstat { height: 72px; border: 1px solid #1E7B34; background: #D4EDDA; border-radius: 6px; display: flex; justify-content: space-between;
  align-items: center; padding: 0 26px; font-size: 30px; color: #155D27; }
.t11-pstat span:last-child { font-weight: 700; }
.t11-pl { margin-top: 10px; height: 72px; font-size: 26px; color: var(--o-texte); grid-template-columns: 1fr auto 40px; }
.t11-pdlg { position: absolute; left: 230px; top: 50px; width: 1260px; height: 610px; z-index: 31; background: #fff; border-radius: 8px;
  overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,.45); color: var(--o-texte); }
.t11-pdlg-h { height: 84px; display: flex; align-items: center; gap: 16px; padding: 0 24px; border-bottom: 1px solid var(--o-filet); }
.t11-pdlg-h .bt { height: 50px; font-size: 20px; }
.entree.t11-pq { margin: 0 0 0 auto; width: 520px; height: 50px; font-size: 20px; }
.t11-pdlg-b { padding: 10px 24px; }
.t11-pr { display: grid; grid-template-columns: 300px 340px 1fr 56px; align-items: center; column-gap: 16px; min-height: 76px; margin-top: 8px;
  padding: 0 18px; border: 1px solid var(--o-filet); border-radius: 8px; font-size: 18px; color: var(--o-texte); }
.t11-pr b { font-size: 19px; }
.t11-pr-t { min-height: 44px; margin-top: 0; border: 0; font-weight: 600; font-size: 18px; }
.t11-pr-a { color: var(--o-texte-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t11-pr-c { display: flex; flex-direction: column; gap: 2px; font-size: 16px; color: var(--o-texte-2); }
.t11-pr-c span { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.t11-pr-c .ico { width: 14px; height: 14px; display: inline-flex; color: #6C757D; }
.t11-pr-c .ico svg { width: 14px; height: 14px; }
.t11-pr-m { width: 46px; height: 46px; border: 1px solid var(--o-filet); border-radius: 6px; display: flex; align-items: center; justify-content: center;
  font-size: 22px; color: #343A40; }
.t11-plus { display: flex; justify-content: center; margin-top: 16px; }
.t11-plus .bt { height: 50px; font-size: 19px; }
.t11-pdlg-p { position: absolute; left: 0; right: 0; bottom: 0; height: 84px; display: flex; align-items: center; padding: 0 24px;
  border-top: 1px solid var(--o-filet); background: #fff; }
.t11-pdlg-p .bt { height: 50px; font-size: 20px; }
""".replace('@NOM@', CAISSIER).replace('@ROLE@', demo.POSTES['caisse'][1])

TUTORIEL = {
    'slug': 't11-fidelite',
    'profil': 't11_fidelite',
    'numero': 11,
    'titre': 'Fidélité AITE : un seul capital de points, des VIP qui se révèlent seuls',
    'fonction': 'Fidélité & statuts VIP',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Fidélité & statuts clients',
        'question': 'Qui sont *vraiment* vos meilleurs clients ?',
        'douleurs': [('echange', 'Bar, hôtel, spa : chacun ses clients'),
                     ('etoile', 'Le VIP donné à la main… et à vie'),
                     ('message', '« Je suis VIP, non ? » — sans preuve'),
                     ('billet', 'La nuit offerte, sans aucune trace'),
                     ('cle', 'Un logiciel de fidélité en plus')],
        'voix': "Qui sont vraiment vos meilleurs clients ? Le bar, l'hôtel et le spa ont chacun les leurs, et le "
                "statut VIP se donne à la main, pour toujours.",
    },
    'revelation': {
        'promesse': "Bar, séjours, spa, coiffure, pressing, espaces VIP : un seul capital de points, et un statut "
                    "Standard, VIP ou VVIP recalculé une fois par jour.",
        'voix': "Avec Aïte haousse, le bar, l'hôtel et les prestations nourrissent un seul capital de points, et les "
                "VIP se révèlent tout seuls.",
    },
    'temps': ['Cumuler', 'Reconnaître', 'Récompenser'],
    'app': 't11-pos',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't11-livre'},
    'bulles': {
        'b-nom': 'Le geste clé : un ticket sans client ne rapporte aucun point.',
        'b-pts': 'Un point par tranche de %s, soit %d%spoints pour %s.' % (fcfa(1000), points(TICKET), NBSP,
                                                                       fcfa(TICKET)),
        'b-seuils': 'VIP : %s et 10%svisites sur 12%smois. VVIP : %s, 25%svisites et 3%sfamilles de services.'
                    % (fcfa(500000), NBSP, NBSP, fcfa(2000000), NBSP, NBSP),
        'b-trace': 'Chaque changement de statut est noté et daté, sans aucune saisie.',
        'b-motif': 'Réservé au responsable. Sans motif, ou si le solde devient négatif, rien ne passe.',
    },
    'reactions': {
        'r-liste': 'Ma liste pour les invitations et les attentions est prête.',
        'r-pole': 'Je vois enfin où mes clients fidèles dépensent.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Au bar : « à quel nom ? »',
         'texte': 'Le caissier choisit la cliente sur le ticket, encaisse et valide. Rien de plus.',
         'voix': "Au bar, Hervé pose la question qui compte : à quel nom ? Il tape Ngono, choisit Estelle sur le "
                 "ticket, encaisse en espèces et valide. Pour les points, il n'a rien d'autre à faire.",
         'gestes': [*personnage('t11-pc', CAISSIER[0]), clic('#t11-cli-bt', d=0.6), ouvrir('t11-pdlg'), saisir('t11-pq', 'Ngono'),
                    cacher('#t11-pr-all', d=0.2), montrer('#t11-pr-f', d=0.3, y=6, avec=True),
                    clic('#t11-pr-est', fx=0.2, d=0.5), fermer('t11-pdlg'), texte('#t11-cli-n', CLIENTE),
                    classe('#t11-cli-bt', ajouter=['t11-choisi']), zoom('#t11-cli-bt', s=1.35, fx=2.3, d=0.6),
                    bulle('b-nom', '#t11-cli-bt', cote='droite', d=2.2), pause(1.1), dezoom(d=0.5),
                    clic('#t11-esp', d=0.55), cacher('#t11-pmsg', d=0.15), montrer('#t11-pstat', d=0.3, y=8),
                    montrer('#t11-pl', d=0.3, y=8, avec=True), classe('#t11-valider', retirer=['t11-off']),
                    clic('#t11-valider', d=0.55)]},
        {'temps': 0, 'titre': 'Les points tombent seuls',
         'texte': 'Mouvements de points : la cliente, l\'origine, le ticket, et 12 points.',
         'voix': "Dans le grand livre des points, la vente est déjà là : la cliente, le bar, le ticket, et douze "
                 "points, un par tranche de mille francs. Son séjour facturé ce matin en a rapporté cent douze.",
         'gestes': [*personnage(None, NOM[0], retirer=['t11-pc']), cacher('#t11-pos', d=0.5), pause(0.3), classe('#t11-l0', ajouter=['survol']),
                    zoom('#t11-l0', s=1.25, fx=0.6, d=0.8), bulle('b-pts', '#t11-l5', cote='bas', d=3.0),
                    pause(2.8), dezoom(d=0.6), anneau('#t11-l2', d=1.6), pause(0.6)]},
        {'temps': 0, 'titre': 'Regroupé par origine',
         'texte': 'Séjours, bar, coiffure, pressing, spa, espaces VIP : un seul capital.',
         'voix': "Regroupé par origine, le grand livre montre d'où viennent les points : séjours, bar, coiffure, "
                 "pressinng, spa, espaces VIP. Un seul capital, pour tous.",
         'gestes': [clic('#t11-livre-rech .deroule', d=0.6), montrer('#t11-panneau', d=0.25, y=-6),
                    clic('#t11-g-origine', d=0.5), cacher('#t11-panneau', d=0.15), vue('t11-origine'),
                    anneau('#t11-o-grps', d=2.2), pause(0.3), anneau('#t11-o-tot', d=1.4),
                    reaction('r-pole', d=2.8), pause(1.6)]},
        {'temps': 1, 'titre': 'Les VIP se révèlent seuls',
         'texte': 'Le statut se recalcule une fois par jour, sur 12 mois glissants.',
         'voix': "Une fois par jour, le statut de chaque client se recalcule sur douze mois : dépenses, visites, "
                 "familles de services. Les VIP et les double VIP rejoignent seuls leur liste.",
         'gestes': [clic('#t11-m-fid', d=0.6), montrer('#t11-dd', d=0.2, y=-6), clic('#t11-dd-vip', d=0.45),
                    cacher('#t11-dd', d=0.15), vue('t11-vip-f'), pause(0.5), clic('#t11-vipf-fx', d=0.5),
                    vue('t11-vip'), anneau('#t11-k-estelle', d=1.4),
                    bulle('b-seuils', '#t11-vip .t11-kg', cote='bas', d=3.2, avec=True), pause(2.0),
                    reaction('r-liste', d=2.8), pause(1.6)]},
        {'temps': 1, 'titre': "La fiche d'Estelle",
         'texte': 'Badge VVIP, date du statut, solde de points, et l\'historique des changements.',
         'voix': "Sur la fiche d'Estelle, le badge double VIP, la date du statut et son solde de points. L'historique note "
                 "chaque changement de statut, sans que personne n'ait rien saisi.",
         'gestes': [clic('#t11-k-estelle', d=0.6), vue('t11-fiche'), pause(0.3),
                    zoom('#t11-badge', s=1.7, d=0.8), pause(1.8), dezoom(d=0.6), curseur('#t11-st-pts', fx=0.3, d=0.5),
                    anneau('#t11-st-pts', d=1.3), curseur('.t11-chatter .ch-bts', fx=0.9, d=0.4),
                    anneau('#t11-ch-m1', d=1.3), anneau('#t11-ch-m2', d=1.3),
                    bulle('b-trace', '#t11-ch-m2', cote='bas', d=2.6, avec=True), pause(0.5)]},
        {'temps': 2, 'titre': 'Une nuit offerte, avec son motif',
         'texte': 'Ajuster des points : la cliente, −1 000 points, et le motif obligatoire.',
         'voix': "Pour remercier Estelle, la directrice lui offre une nuit et la décompte de ses points : depuis le "
                 "menu Fidélité, Ajuster des points, la cliente, moins mille points, et le motif, sans lequel rien ne "
                 "passe.",
         'gestes': [clic('#t11-m-fid', d=0.6), montrer('#t11-dd', d=0.2, y=-6), clic('#t11-dd-adj', d=0.45),
                    cacher('#t11-dd', d=0.15), ouvrir('t11-as'), clic('#t11-as-cli', d=0.4),
                    choisir('t11-as-cli', CLIENTE), saisir('t11-as-pts', '-1000'),
                    saisir('t11-as-mot', 'Utilisation : nuit offerte'),
                    bulle('b-motif', '#t11-as-mot', cote='bas', d=2.4), pause(1.9), clic('#t11-appl', d=0.5),
                    fermer('t11-as'), clic('#t11-st-pts', fx=0.4, d=0.4), vue('t11-hist')]},
        {'temps': 2, 'titre': "Tout l'historique, un seul solde",
         'texte': 'Points : chaque mouvement de la cliente, le retrait en rouge, le solde en pied de liste.',
         'voix': "Un clic sur Points : tout l'historique d'Estelle, séjours, bar, spa, coiffure, espaces VIP. Le "
                 "retrait s'affiche en rouge, et le solde descend d'autant.",
         'gestes': [curseur('#t11-h0', fx=0.45, d=0.5),
                    classe('#t11-h0', ajouter=['survol'], avec=True), zoom('#t11-h0', s=1.25, fx=0.6, d=0.7),
                    pause(1.8), dezoom(d=0.6), defiler('#t11-hist-defil', -(HAUT_LISTE - VISIBLE), d=1.6),
                    anneau('#t11-h-tot', d=2.0), pause(1.2)]},
    ],
    'resultats': {
        'titre': 'Vos meilleurs clients, enfin reconnus',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'point', 'icone': 'pieces',
             'texte': 'par tranche de 1 000 FCFA, calculé tout seul — barème réglable sans code dans les Paramètres'},
            {'valeur': '6', 'compter': 6, 'unite': 'services', 'icone': 'echange',
             'texte': 'bar et boutique, séjours, spa, coiffure, pressing, espaces VIP : un seul capital'},
            {'valeur': '3', 'compter': 3, 'unite': 'statuts', 'icone': 'etoile',
             'texte': 'Standard, VIP, VVIP, recalculés une fois par jour sur 12 mois glissants'},
        ],
        'voix': "Un point par tranche de mille francs, six services pour un seul capital, trois statuts recalculés "
                "chaque jour : vos meilleurs clients, enfin reconnus.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': "L'analyse des ventes",
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 5, 'apres': 5.0},
}


def _insecables(texte):
    """Typographie française à l'écran : espace insécable avant « : ; ? ! » et
    à l'intérieur des guillemets, pour qu'aucun signe ne commence une ligne."""
    for signe in (':', ';', '?', '!', '»'):
        texte = texte.replace(' ' + signe, NBSP + signe)
    return texte.replace('« ', '«' + NBSP)


for _cle in ('bulles', 'reactions'):
    TUTORIEL[_cle] = {k: _insecables(v) for k, v in TUTORIEL[_cle].items()}
for _etape in TUTORIEL['etapes']:
    _etape['titre'], _etape['texte'] = _insecables(_etape['titre']), _insecables(_etape['texte'])
TUTORIEL['revelation']['promesse'] = _insecables(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['douleurs'] = [(i, _insecables(t)) for i, t in TUTORIEL['accroche']['douleurs']]
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = _insecables(_carte['texte'])
