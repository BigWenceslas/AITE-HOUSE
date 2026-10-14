# -*- coding: utf-8 -*-
"""Chapitre 3 — Ardoises clients et recouvrement.

Source : fiche de recette n° 3 « Ardoises clients et recouvrement » (caisse :
tableau de bord Recouvrement, liste des ardoises, filtre « Ouvertes », fiche,
assistant de remboursement, ardoise réglée, refus d'accès aux réservations).

Libellés relevés dans : aite_pos_credit/static/src/xml (tableau de bord
« POS Crédit — Recouvrement », capture de référence française),
views/pos_credit_views.xml (liste, fiche, boutons « Enregistrer un
remboursement » / « Annuler », statusbar Ouverte / Réglée, onglets),
models/pos_credit.py (Origine « Point de vente », sévérités Récente / En
retard / Critique), wizard/pos_credit_repay_wizard*.py|xml (« Enregistrer un
remboursement », moyens de paiement, bouton « Encaisser »). Menus du profil
Caisse relevés sur une base de recette (load_menus). Le refus reprend le
message d'Odoo 18 et les groupes qui lisent aite.hotel.reservation
(aite_hotel_management/security/ir.model.access.csv).
"""

import demo
from ecrans import (assistant, bouton, cell_puce, champ, cp_fiche, deux_colonnes, e, entree, erreur_acces, fenetre,
                    graphe_barres, graphe_courbe, graphes, groupe, kpi, lien, m_champ, m_champs, num, onglets, statusbar,
                    table, tdb_entete, tdb_filtres, tdb_section, titre_fiche, toast, vue_fiche, vue_liste, vue_tdb)
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, etat, fermer, montrer, notifier, ouvrir,
                    pause, saisir, survol, texte, vue)

NOM, ROLE = demo.POSTES['caisse']
MENUS = ['Recouvrement', 'Ardoises', 'Remboursements']

# ------------------------------------------------------------ Recouvrement --
RECOUVREMENT = vue_tdb('c3-dash', (
    tdb_entete('POS Crédit — Recouvrement', 'Ardoises & remboursements · suivi des dettes clients')
    + tdb_filtres([('Période', ["Aujourd'hui", 'Cette semaine', 'Ce mois', 'Tout'], 2),
                   ('Origine', ['Toutes', 'Point de vente', 'Ventes'], 0)])
    + tdb_section('Encours & recouvrement', [
        kpi('c3-k-enc', 'Encours total (dû)', '150 000 FCFA', '5 clients débiteurs', 'rouge'),
        kpi('c3-k-rec', 'Recouvré (période)', '37 000 FCFA', '4 remboursements', 'vert', ('12,4 % vs N-1', 'haut')),
        kpi('c3-k-new', 'Nouvelles ardoises (période)', '18 500 FCFA', '1 ardoise ouverte', 'ambre'),
        kpi('c3-k-taux', 'Taux de recouvrement', '19,8 %', 'recouvré / (encours + recouvré)', 'violet')])
    + tdb_section('Indicateurs de risque', [
        kpi('c3-k-moy', 'Ardoise moyenne', '30 000 FCFA', '5 débiteurs actifs'),
        kpi('c3-k-anc', 'Plus ancienne dette', '104 j', 'Sylvie Mbarga'),
        kpi('c3-k-ret', 'En retard (+30 j)', '101 500 FCFA', "67,7 % de l'encours"),
        kpi('c3-k-reg', 'Ardoises réglées (période)', '2', 'délai moyen 18 j')])
    + graphes(graphe_barres('c3-g-age', "Balance âgée (aging) de l'encours",
                            [(32, '#3B6D11'), (48, '#854F0B'), (30, '#A32D2D'), (20, '#5C1A1A')],
                            etiquettes=['0–30 j', '30–60 j', '60–90 j', '+90 j']),
              graphe_courbe('c3-g-evo', 'Nouvelles ardoises vs Recouvré (6 mois)', [20, 26, 38, 44, 35, 30], '#A32D2D',
                            etiquettes=['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']))
), initiale=True)

# ---------------------------------------------------------------- Ardoises --
COLS = [('Référence', '150px'), ('Client', '220px'), ('Origine', '170px'), ("Date d'ouv…", '150px'),
        ('Montant initial', '170px', 'd'), ('Déjà rembour…', '160px', 'd'), ('Reste dû', '160px', 'd'),
        ('Âge (j)', '90px', 'd'), ('Sévérité', '130px'), ('État', '1fr')]
LIGNES = []
for i, (ref, cli, date, mt, remb, reste, age, sev, genre) in enumerate(demo.ARDOISES):
    LIGNES.append({'id': 'c3-l%d' % i, 'classe': {'orange': 'retard', 'rouge': 'critique'}.get(genre, ''),
                   'cellules': [ref, cli, cell_puce('Point de vente', 'info'), date, num(mt), num(remb), num(reste),
                                age, cell_puce(sev, genre), cell_puce('Ouverte', 'clair')]})
ARDOISES = vue_liste('c3-liste', 'Ardoises', COLS, LIGNES, facettes=[('c3-fac', 'Ouvertes')], pager='1-5 / 5',
                     total=['', '', '', '', '187 000 FCFA', '37 000 FCFA', '150 000 FCFA', '', '', ''])

# ------------------------------------------------------------------- Fiche --
REMB = table([('Date', '160px'), ('Moyen de paiement', '260px'), ('Réf. transaction', '1fr'), ('Montant', '170px', 'd'),
              ('Encaissé par', '220px'), ('État', '140px')],
             [('c3-r1', ['30/09/2026', 'Espèces', '', '20 000 FCFA', NOM, ('<span><span class="puce vert">Validé</span></span>',)])],
             identifiant='c3-remb')
NOUVEAU_REMB = ('<div class="t-ligne masque" id="c3-r2" style="grid-template-columns:160px 260px 1fr 170px 220px 140px">'
                '<span>14/10/2026</span><span>Orange Money</span><span class="ell">OM261014.1530.A55120</span>'
                '<span class="d">44 500 FCFA</span><span>%s</span><span><span class="puce vert">Validé</span></span></div>'
                % e(NOM))
FEUILLE = (
    titre_fiche('ARD/0024')
    + deux_colonnes(
        groupe('', [champ('Client', 'Armand Mvogo', gras=True), champ("Date d'ouverture", '18/08/2026', gras=True),
                    champ('Origine', '<span class="puce gris">Point de vente</span>', html=True),
                    champ('Commande POS d\'origine', 'Bar — Commande 00412'), champ("Caisse d'origine", 'Bar de la terrasse')]),
        groupe('', [champ('Montant initial', '64 500 FCFA', gras=True), champ('Déjà remboursé', '20 000 FCFA', 'c3-deja'),
                    champ('Reste dû', '44 500 FCFA', 'c3-reste'), champ('Âge (jours)', '57'),
                    champ('Sévérité', 'En retard', 'c3-sev')]))
    + onglets(['Remboursements', 'Note']) + REMB.replace('<div class="t-ajout">', NOUVEAU_REMB + '<div class="t-ajout">'))
FICHE = vue_fiche('c3-fiche', cp_fiche('Ardoises', 'ARD/0024', '4 / 5', stats=[('c3-st', 'billet', 'Remboursements', '1')]),
                  [bouton('c3-b-remb', 'Enregistrer un remboursement', 'primaire'), bouton('c3-b-ann', 'Annuler')],
                  statusbar('c3-sb', ['Ouverte', 'Réglée'], 0), FEUILLE,
                  boutons_apres=[[bouton('c3-b-rouv', 'Rouvrir')]])

ASSISTANT = assistant('c3-as', 'Enregistrer un remboursement', m_champs(
    [m_champ('Ardoise', e('ARD/0024')), m_champ('Client', e('Armand Mvogo')),
     m_champ('Reste dû actuel', e('44 500 FCFA'))],
    [m_champ('Montant à encaisser', entree('c3-mt', '', '44 500 FCFA')), m_champ('Moyen de paiement', entree('c3-moy', '', 'Espèces')),
     m_champ('Réf. transaction', entree('c3-ref', '')), m_champ('Date', e('14/10/2026'))]),
    [('c3-ok', 'Encaisser', 'primaire', None), ('c3-non', 'Annuler', 'gris', None)], haut=150)

REFUS = erreur_acces('c3-refus', 'Réservation hôtelière', 'aite.hotel.reservation',
                     ['Gestion Hôtelière/Gouvernante', 'Gestion Hôtelière/Responsable', 'Gestion Hôtelière/Réception'])

ECRAN = fenetre('app-c3', 'POS Crédit', MENUS, [RECOUVREMENT, ARDOISES, FICHE], actif='Recouvrement', societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#185FA5', calques=ASSISTANT + REFUS)

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
    'vues_initiales': {'odoo': 'c3-dash'},
    'etapes': [
        {'titre': 'Le tableau de bord Recouvrement', 'texte': "L'encours, ce qui rentre, et l'âge de la dette.",
         'voix': "Le tableau de bord Recouvrement donne l'encours total, ce qui a été recouvré ce mois, et surtout "
                 "l'âge de la dette : plus une ardoise vieillit, plus le risque d'impayé grandit.",
         'gestes': [compter('#c3-k-enc-v', 0, 150000, d=1.1, apres=' FCFA'),
                    animer('#c3-g-age', {'scaleY': 0}, {'scaleY': 1}, d=1.0, avec=True),
                    animer('#c3-g-evo', {'scaleX': 1}, {'scaleX': 0}, d=1.4, avec=True),
                    anneau('#c3-k-ret', d=1.6, decale=0.4), anneau('#c3-g-age', d=1.8)]},
        {'titre': 'Les ardoises ouvertes', 'texte': 'Client, reste dû, âge et sévérité, en couleur.',
         'voix': "La liste des ardoises, filtrée sur les ouvertes, montre le reste dû et l'âge de chacune. Les "
                 "couleurs suivent la sévérité : récente, en retard, critique.",
         'gestes': [clic('#app-c3 .o-haut .menu:nth-child(4)', d=0.6), vue('c3-liste'), pause(0.4),
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
        {'titre': "L'ardoise est réglée", 'texte': 'Reste dû à zéro, remboursement tracé, écriture comptable passée.',
         'voix': "Le reste dû tombe à zéro et l'ardoise passe Réglée. Le remboursement est tracé avec son moyen de "
                 "paiement, la personne qui l'a encaissé et sa référence.",
         'gestes': [texte('#c3-reste', '0 FCFA'), texte('#c3-deja', '64 500 FCFA'), texte('#c3-sev', 'Réglée'),
                    classe('#c3-sb-0', retirer=['actif']), classe('#c3-sb-1', ajouter=['actif']),
                    cacher('#c3-fiche-ga', d=0.2), montrer('#c3-fiche-gb', d=0.3, y=0), texte('#c3-st-v', '2'),
                    montrer('#c3-r2', d=0.4), anneau('#c3-sb', d=1.2), anneau('#c3-r2', d=1.6)]},
        {'titre': "Hors de son périmètre", 'texte': 'La caisse n\'ouvre pas les réservations de l\'hôtel.',
         'voix': "La caisse n'a pas de droits sur l'hôtel. Si Hervé tente d'ouvrir une réservation, Odoo refuse "
                 "et nomme les profils autorisés.",
         'gestes': [ouvrir('c3-refus'), pause(0.6), anneau('#c3-refus .refus', d=2.0), clic('#c3-refus-ok'),
                    fermer('c3-refus')]},
    ],
}
