# -*- coding: utf-8 -*-
"""Étude comparative AITE HOUSE vs marché — générateur HTML → PDF."""
import base64
import os

LOGO = ""
for p in ("/home/claude/logo_aite.jpg", "/mnt/user-data/uploads/logo_final_1_0.jpg"):
    if os.path.exists(p):
        LOGO = ('<img src="data:image/jpeg;base64,%s" style="height:13mm"/>'
                % base64.b64encode(open(p, "rb").read()).decode())
        break

CSS = """
@page { size: A4; margin: 15mm 14mm 17mm;
  @bottom-center { content: "AITE Consulting — Étude comparative AITE HOUSE · octobre 2026 — page " counter(page) " / " counter(pages);
    font-family: 'DejaVu Sans'; font-size: 7pt; color: #8A949C; } }
@page cover { margin: 0; @bottom-center { content: none; } }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 9.2pt; color: #37414A;
  line-height: 1.42; }
h1 { font-size: 19pt; color: #0A4C5C; margin: 0 0 1mm; }
h2 { font-size: 13pt; color: #0F6478; margin: 6mm 0 2.5mm; border-bottom: .5mm solid #DFE8EC;
  padding-bottom: 1.2mm; page-break-after: avoid; }
h3 { font-size: 10pt; color: #0A4C5C; margin: 4mm 0 1.5mm; page-break-after: avoid; }
p { margin-bottom: 2.2mm; text-align: justify; }
b { color: #0A4C5C; }
ul { margin: 0 0 2.5mm 5mm; } li { margin-bottom: 1.1mm; }
table { width: 100%; border-collapse: collapse; font-size: 7.6pt; margin: 2mm 0 3mm; }
th { background: #0A4C5C; color: #fff; text-align: left; padding: 1.4mm 1.8mm; font-size: 7pt;
  text-transform: uppercase; letter-spacing: .3pt; }
td { border-bottom: .25mm solid #E6ECEF; padding: 1.3mm 1.8mm; vertical-align: top; }
tr { page-break-inside: avoid; }
tr:nth-child(even) td { background: #F7FAFB; }
td.c, th.c { text-align: center; }
tr.grp td { background: #E8F1F4; color: #0A4C5C; font-weight: 800; font-size: 7.4pt; }
.pill { display: inline-block; border-radius: 2mm; padding: .2mm 1.6mm; font-size: 6.8pt;
  font-weight: 700; white-space: nowrap; }
.p-r { background: #F6E0DE; color: #C0392B; } .p-a { background: #F8ECD8; color: #B0761C; }
.p-g { background: #DFF0E6; color: #2E7D4F; } .p-v { background: #EFE2F2; color: #7A2E86; }
.p-b { background: #E3EEF3; color: #0F6478; } .p-n { background: #EEF1F3; color: #7C8790; }
.ok { color: #2E7D4F; font-weight: 800; } .mid { color: #B0761C; font-weight: 800; }
.no { color: #C0392B; font-weight: 800; }
.box { page-break-inside: avoid; border: .35mm solid #DFE8EC; border-left: 1.4mm solid #0F6478; border-radius: 2mm;
  padding: 2.8mm 4mm; margin: 2.5mm 0; background: #F7FAFB; }
.box.v { border-left-color: #7A2E86; } .box.o { border-left-color: #E6A23C; }
.box.r { border-left-color: #C0392B; }
.krow { display: flex; gap: 3mm; margin: 3mm 0; }
.k { flex: 1; border: .35mm solid #E3E9EC; border-left: 1.3mm solid #0F6478; border-radius: 1.6mm;
  padding: 2mm 2.6mm; }
.k.r { border-left-color: #C0392B; } .k.a { border-left-color: #E6A23C; }
.k.g { border-left-color: #38A169; } .k.v { border-left-color: #7A2E86; }
.klbl { font-size: 6pt; font-weight: 700; color: #7C8790; letter-spacing: .3pt; }
.kval { font-size: 13pt; font-weight: 800; margin-top: .5mm; }
.ksub { font-size: 6.4pt; color: #7C8790; }
.hd { display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1mm solid #0F6478; padding-bottom: 3mm; margin-bottom: 4mm; }
.sub { font-size: 10pt; color: #5A6670; } .meta { font-size: 7.8pt; color: #8A949C; margin-top: 1mm; }
.cols { display: flex; gap: 5mm; } .cols > div { flex: 1; }
.pb { page-break-before: always; }
.small { font-size: 7.4pt; color: #5A6670; }
.src { font-size: 6.9pt; color: #6A7680; line-height: 1.4; }
.src a { color: #0F6478; text-decoration: none; }
/* couverture */
.cover { page: cover; width: 210mm; height: 297mm; background: linear-gradient(170deg,#083D4E 0%,#0C5468 55%,#0F6478 100%);
  color: #fff; position: relative; overflow: hidden; }
.cov-peach { position: absolute; right: -55mm; top: -75mm; width: 150mm; height: 150mm;
  border-radius: 50%; background: #F4CDAA; opacity: .9; }
.cov-ring { position: absolute; left: -30mm; bottom: -30mm; width: 120mm; height: 120mm;
  border-radius: 50%; border: 3mm solid rgba(255,255,255,.18); }
.cov-in { position: absolute; left: 18mm; top: 60mm; width: 160mm; }
.cov-kick { font-size: 11pt; letter-spacing: 2.5pt; color: #F4CDAA; font-weight: 800; }
.cov-h1 { font-size: 30pt; font-weight: 800; line-height: 1.1; margin: 4mm 0; }
.cov-sub { font-size: 12pt; color: #D7E6EA; line-height: 1.5; }
.cov-badge { display: inline-block; background: #7A2E86; border: 1mm solid #fff; padding: 2.5mm 7mm;
  font-size: 15pt; font-weight: 800; letter-spacing: 1pt; margin-top: 10mm; }
.cov-foot { position: absolute; left: 18mm; bottom: 16mm; width: 174mm; display: flex;
  justify-content: space-between; align-items: flex-end; font-size: 8.5pt; color: #D7E6EA; }
.cov-foot .logo { background: #fff; border-radius: 2mm; padding: 2mm 3mm; }
"""

# ─────────────────────────── données ───────────────────────────
OK, MID, NO = ('<span class="ok">●</span>', '<span class="mid">◐</span>',
               '<span class="no">○</span>')
STD = '<span class="pill p-b">Standard</span>'
DIF = '<span class="pill p-v">Différenciant</span>'
RAR = '<span class="pill p-a">Rare</span>'
LOC = '<span class="pill p-g">Local</span>'

# (Fonctionnalité, AITE HOUSE aujourd'hui, Marché leaders, Afrique/local, Odoo apporte, Commentaire)
GRILLE = [
    ("HÉBERGEMENT & FRONT OFFICE", None),
    ("Planning visuel des chambres, check-in / check-out", OK, STD, "", "aite_hotel_management",
     "Couvert."),
    ("Folio, extras, proforma, acompte, facture unique de séjour", OK, STD, "", "hotel_mgmt + account",
     "Couvert — argument fort (facture unique hôtel+bar+prestations)."),
    ("Main courante / photo du jour", OK, DIF, "", "aite_hotel_management", "Couvert."),
    ("Plans tarifaires multiples, saisons, tarifs dérivés, packages", MID, STD, "",
     "Listes de prix Odoo", "Tarif par type de chambre ; pas de saisons ni packages pension."),
    ("Restrictions (séjour minimum, stop-sell, fermé à l'arrivée)", NO, STD, "", "—", "Absent."),
    ("Tarifs négociés sociétés / agences, commissions", MID, STD, "", "Listes de prix + CRM",
     "Possible par liste de prix ; pas de profil agence ni commissions."),
    ("Groupes : blocks, rooming list, facture maître", NO, STD, "", "—", "Absent."),
    ("Allotements tour-opérateurs avec dates de release", NO, STD, "", "—", "Absent."),
    ("Multi-folios et routage des charges (chambre / société / événement)", MID, STD, "",
     "Note de chambre", "Un folio par séjour ; pas de routage ni de split."),
    ("Chambre hors service (OOO) liée à un ordre de travail", MID, DIF, "", "Maintenance (CE)",
     "Statut hors service existe ; pas de lien avec la maintenance."),
    ("Clôture journalière / night audit hôtel", NO, STD, "", "Clôture POS seulement",
     "Nuitées postées à la main ; pas de rapport du jour automatique."),
    ("Comptes débiteurs / balance âgée (city ledger)", OK, STD, "", "aite_pos_credit",
     "Couvert — crédit clients natif, rare chez les PMS SMB."),
    ("Fiche d'enregistrement client digitale, e-signature, scan de pièce", NO, STD, LOC,
     "Sign (EE) / Documents (EE)", "Absent — obligation loi 2016/006 art. 28 au Cameroun."),
    ("Taxe de séjour automatique par nuitée (barème étoiles) + état mensuel", NO, "", LOC,
     "Taxes Odoo", "Aucun PMS international ne la gère nativement : différenciateur direct."),
    ("PARCOURS CLIENT", None),
    ("Réservation en ligne avec acompte (site web)", OK, STD, "", "aite_website_booking",
     "Couvert."),
    ("Pré-check-in en ligne (lien J-2, données saisies par le client)", NO, STD, "", "Portail Odoo",
     "Absent."),
    ("Check-out express, facture envoyée automatiquement", NO, STD, "", "Mail/SMS/WhatsApp",
     "Absent."),
    ("Messagerie client unifiée (email / SMS / WhatsApp)", MID, STD, DIF, "SMS (CE) · WhatsApp (EE)",
     "Email et SMS possibles ; WhatsApp non branché. WhatsApp natif : 5 leaders sur 10."),
    ("Upsell automatisé (surclassement, petit-déjeuner, late check-out)", NO, STD, "", "—",
     "Absent."),
    ("Portail invité / QR en chambre (facture, demandes, room service)", MID, STD, "",
     "pos_self_order (CE) + portail", "Briques présentes, non assemblées pour l'hôtel."),
    ("Kiosque self check-in · clé digitale", NO, DIF, "", "Frontdesk (EE, inspiration)",
     "Absent — long terme."),
    ("HOUSEKEEPING & MAINTENANCE", None),
    ("Statut chambres temps réel (sale / propre / inspectée)", NO, STD, "", "—",
     "Absent — présent chez 10 leaders sur 10 et au cœur d'EISI."),
    ("Affectation des tâches aux femmes de chambre, feuilles de travail, mobile", NO, STD, "", "—",
     "Absent."),
    ("Ordres de travail / tickets de maintenance (GMAO)", NO, STD, "", "Maintenance (CE)",
     "Absent — l'app Odoo Maintenance couvre 80 % du besoin."),
    ("Inspections de chambres, checklists, photos", NO, DIF, "", "Quality (EE) / Surveys (CE)",
     "Absent."),
    ("Minibar (consommation, recharge, poste sur folio)", NO, DIF, "", "POS / Inventaire",
     "Absent."),
    ("Objets trouvés (lost & found)", NO, DIF, "", "servia_lost_found (CE, gratuit)",
     "Absent — 4 leaders sur 10 ; module EISI."),
    ("Communication interdépartementale, demandes clients tracées", MID, DIF, "", "Discuss / Helpdesk (EE)",
     "Discuss existe ; pas de flux réception ↔ étages ↔ maintenance."),
    ("BAR, RESTAURANT & ESPACES", None),
    ("Caisse tactile multi-points de vente, hors-ligne", OK, DIF, "", "POS Odoo",
     "Couvert — POS hors-ligne : 3 leaders sur 10 seulement."),
    ("Note de chambre (POS → folio)", OK, STD, "", "aite_hotel_pos_link", "Couvert."),
    ("Plan de salle, commande par table, addition partagée", OK, STD, "", "pos_restaurant (CE)",
     "Couvert."),
    ("Écran cuisine / bons de préparation", MID, STD, "", "Imprimantes (CE) · Preparation Display (EE)",
     "Impression CE ; écran cuisine = Enterprise."),
    ("Commande QR à table / en chambre", MID, STD, "", "pos_self_order (CE)",
     "Disponible, non relié à la chambre."),
    ("Stock F&B par recette / fiches techniques", MID, DIF, "", "Nomenclatures (kits)",
     "Possible via kits ; non packagé."),
    ("Espaces & prestations au créneau (salles, piscine, billard)", OK, DIF, "", "aite_slot_booking",
     "Couvert — module natif : 4 leaders sur 10."),
    ("Banquets / séminaires : devis, BEO, menus, facturation événement", MID, DIF, "", "Ventes / CRM",
     "Devis possible ; pas de BEO ni de fiche de fonction."),
    ("DISTRIBUTION & REVENUE", None),
    ("Channel manager bidirectionnel (Booking.com, Expedia, Airbnb)", NO, STD, "",
     "Connecteurs Channex / WuBook / Beds24", "Absent — aucun PMS leader ne vit sans OTA."),
    ("Metasearch (Google Hotel Ads) · GDS", NO, STD, "", "—", "Absent — via channel manager."),
    ("Tarification dynamique par règles d'occupation, recommandations", NO, STD, "", "—", "Absent."),
    ("Rapports RevPAR / ADR / taux d'occupation / pace / pickup", MID, STD, "", "aite_exec_dashboard",
     "Taux d'occupation et nuitées ; ADR/RevPAR/pace à ajouter."),
    ("Prévision d'occupation", NO, STD, "", "—", "Absent."),
    ("PAIEMENTS", None),
    ("Mobile Money intégré (MTN MoMo, Orange Money) : web, lien, folio, POS", MID, RAR, LOC,
     "Smobilpay/Maviance (CE) · CinetPay · Orange Money (EE)",
     "Saisi comme mode de paiement manuel ; aucune passerelle. Aucun PMS ne le fait nativement au Cameroun."),
    ("Liens de paiement, acomptes automatisés selon politique", MID, STD, "", "Fournisseurs de paiement Odoo",
     "Acompte web ; pas de lien de paiement MoMo."),
    ("Pré-autorisation carte, tokenisation", NO, STD, "", "—", "Absent — marché carte faible au Cameroun."),
    ("CRM, FIDÉLITÉ & RÉPUTATION", None),
    ("Fiche client unique, historique séjours / bar / crédit", OK, STD, "", "res.partner",
     "Couvert."),
    ("Programme de fidélité points / paliers VIP-VVIP", OK, RAR, "", "aite_loyalty",
     "Couvert — natif chez 1 leader sur 10 : avantage à mettre en avant."),
    ("Campagnes email / SMS ciblées", OK, STD, "", "Mass mailing / SMS (CE)", "Couvert."),
    ("Gestion des avis / e-réputation (Google, Booking)", NO, STD, "", "—", "Absent."),
    ("Bons cadeaux / vouchers", NO, DIF, "", "Cartes cadeaux POS (CE)", "Brique POS disponible."),
    ("Enquêtes de satisfaction post-séjour", MID, STD, "", "Surveys (CE)", "Brique disponible, non automatisée."),
    ("PILOTAGE, CONFORMITÉ & EXPLOITATION", None),
    ("Cockpit Direction consolidé, actions à traiter", OK, STD, "", "aite_direction_dashboard",
     "Couvert — indicateurs cash à risque / crédits−dettes uniques."),
    ("Analyses ventes : heures de pointe, marges, CMV, écarts de caisse", OK, DIF, "", "aite_pos_analytics",
     "Couvert."),
    ("Stock : ruptures, coulage, inventaires, dépôts · Achats : échéancier, OTIF, prix", OK, DIF, "",
     "aite_stock/purchase_dashboard", "Couvert."),
    ("Statistiques réglementaires (MINTOUL : arrivées, nuitées, nationalités)", NO, "", LOC, "—",
     "Absent — loi 2016/006 art. 16 (amende 50 K–500 K F)."),
    ("Registre de police / export journalier des clients hébergés", NO, DIF, LOC, "—",
     "Absent — modèle HORA (Côte d'Ivoire) à anticiper."),
    ("Facture conforme DGI (NIU, TVA 19,25 %), SYSCOHADA, FEC", OK, STD, LOC, "l10n_cm (CE)",
     "Couvert ; DSF en chantier ; taxation temps réel 2026 à préparer."),
    ("Consommations & énergie (eau, électricité, carburant groupe) par chambre occupée", NO, RAR, LOC,
     "—", "Absent — module EISI ; très pertinent face aux coupures."),
    ("Qualité & audits (checklists, hygiène cuisine, standards)", NO, DIF, "", "Quality (EE) · Surveys (CE)",
     "Absent — module EISI (Audits 2025)."),
    ("Planning des équipes (shifts) par poste", MID, DIF, "", "Planning (EE) · Présences (CE)",
     "Présences et congés couverts ; pas de planning de shifts."),
    ("RH : congés, présences, recrutement, paie CNPS/IRPP", OK, DIF, LOC, "HR Odoo + AIT SI RH",
     "Couvert — aucun PMS ne le propose."),
    ("Journal d'audit, droits par poste, 2FA", OK, STD, "", "Odoo (chatter, groupes, auth_totp)",
     "Couvert."),
    ("Mode dégradé réception (hors connexion)", NO, RAR, LOC, "—",
     "Absent — aucun PMS cloud ne l'offre ; attente forte localement."),
    ("Assistant IA (questions en langage naturel sur les chiffres), agent WhatsApp", NO, DIF, "", "—",
     "Absent — norme des annonces 2025-2026."),
]

# Priorisation : (id, fonctionnalité, origine, valeur, diff, effort, édition, vague, module proposé)
PRIO = [
    ("F01", "Housekeeping : statut chambres (sale/propre/inspectée/HS), affectation des femmes de chambre, vue mobile",
     "Socle marché · EISI", 5, 2, "M", "CE", 1, "aite_housekeeping"),
    ("F02", "Maintenance : ordres de travail liés aux chambres et équipements, préventif, chambre HS retirée de l'inventaire",
     "Socle marché · EISI", 5, 2, "S", "CE (app Maintenance)", 1, "aite_hotel_maintenance"),
    ("F03", "Fiche d'enregistrement client + registre de police + photo de la pièce + export journalier",
     "Réglementaire CM", 5, 5, "M", "CE (Sign en option)", 1, "aite_guest_registry"),
    ("F04", "Taxe de séjour automatique par nuitée selon la catégorie (barèmes CM, CI, SN, GN) + état mensuel de reversement",
     "Réglementaire CM/CI/SN/GN", 5, 5, "S", "CE", 1, "aite_city_tax"),
    ("F05", "Clôture journalière hôtel (night audit) : nuitées postées automatiquement, rapport du jour, contrôles",
     "Socle marché", 4, 2, "M", "CE", 1, "aite_hotel_management"),
    ("F06", "Indicateurs RevPAR / ADR / TO / pace / pickup dans le cockpit et le tableau de bord exécutif",
     "Socle marché", 4, 2, "S", "CE", 1, "aite_exec_dashboard"),
    ("F07", "Plans tarifaires par saison, packages (pension), restrictions (séjour mini, stop-sell), tarifs sociétés/agences",
     "Socle marché", 4, 2, "M", "CE", 1, "aite_hotel_management"),
    ("F08", "Groupes et allotements : blocks, rooming list importable, facture maître, dates de release",
     "Socle marché", 4, 2, "M", "CE", 1, "aite_hotel_management"),
    ("F09", "Multi-folios et routage des charges (chambre / société / événement), split de facture",
     "Socle marché", 3, 2, "M", "CE", 1, "aite_hotel_management"),
    ("F10", "Mobile Money intégré : MTN MoMo et Orange Money (Smobilpay) — acompte web, lien de paiement, folio, POS, réconciliation",
     "Différenciateur local", 5, 5, "M", "CE", 2, "aite_momo_payments"),
    ("F11", "WhatsApp : confirmation, pré-arrivée, facture, relance d'ardoise, demande d'avis (API Meta via Odoo EE ou connecteur CE)",
     "Différenciateur · tendance", 5, 4, "M", "EE natif / CE connecteur", 2, "aite_guest_messaging"),
    ("F12", "Pré-check-in en ligne (lien J-2 : fiche remplie, pièce téléversée) + check-out express avec facture envoyée",
     "Socle marché", 4, 3, "M", "CE", 2, "aite_online_checkin"),
    ("F13", "Channel manager / OTA via connecteur (Channex, WuBook ou Beds24) : Booking.com, Expedia, Airbnb, Google",
     "Socle marché", 5, 2, "L", "CE", 2, "aite_channel_connector"),
    ("F14", "Statistiques MINTOUL mensuelles : arrivées, nuitées, nationalités, résidents/non-résidents, TO, durée moyenne",
     "Réglementaire CM", 4, 5, "S", "CE", 2, "aite_guest_registry"),
    ("F15", "Conformité DGI : numérotation, FEC, préparation taxation en temps réel ; accises et licences par point de vente",
     "Réglementaire CM", 4, 4, "M", "CE", 2, "l10n_cm + aite_compliance"),
    ("F16", "Objets trouvés + minibar depuis l'app housekeeping (poste direct sur le folio)",
     "EISI", 3, 3, "S", "CE", 2, "aite_housekeeping"),
    ("F17", "Mode dégradé réception : planning et arrivées du jour en cache, saisie différée, resynchronisation",
     "Différenciateur local", 4, 5, "L", "CE", 2, "aite_offline_desk"),
    ("F18", "Consommations & énergie : relevés eau / électricité / carburant du groupe, coût par chambre occupée, alertes d'anomalie",
     "EISI · local", 4, 5, "M", "CE", 3, "aite_utilities"),
    ("F19", "Qualité & audits : checklists d'inspection de chambres, hygiène cuisine (HACCP simplifié), audits de standards avec photos",
     "EISI", 3, 4, "M", "CE (Quality EE en option)", 3, "aite_quality_audits"),
    ("F20", "Incidents & voix du client : réclamations et demandes multi-canaux liées à la réservation, délais de résolution, top 10",
     "EISI · socle", 4, 3, "M", "CE (Helpdesk EE en option)", 3, "aite_guest_requests"),
    ("F21", "Planning des équipes (shifts) par poste : réception, étages, bar — échanges, Gantt",
     "EISI · socle", 3, 2, "S", "EE (Planning) / M en CE", 3, "Planning Odoo"),
    ("F22", "Upsell automatisé pré-arrivée : surclassement, petit-déjeuner, late check-out, transfert aéroport",
     "Socle marché", 4, 3, "M", "CE", 3, "aite_online_checkin"),
    ("F23", "Tarification dynamique simple : règles d'occupation, recommandations tarifaires, veille concurrents manuelle",
     "Tendance 2026", 3, 3, "M", "CE", 3, "aite_revenue"),
    ("F24", "Assistant IA du gérant (questions en langage naturel sur le cockpit) et agent WhatsApp réservations/FAQ",
     "Tendance 2026", 4, 4, "L", "CE + API IA", 3, "aite_assistant"),
    ("F25", "Portail de séjour par QR en chambre : facture en cours, demandes, room service (self-order), avis ; bons cadeaux",
     "Socle marché", 3, 3, "M", "CE", 3, "aite_guest_portal"),
    ("F26", "Gestion des avis / e-réputation (Google, Booking) et enquêtes post-séjour automatisées",
     "Socle marché", 3, 2, "S", "CE (Surveys)", 3, "aite_guest_messaging"),
]

AFRIQUE = [
    ("Cloudbeds (USA)", "Indépendants 20-50 ch. ; Douala ≈ 280 KFCFA/mois", "◐ via passerelle", "◐ taxe paramétrable", "◐ UI FR", "Sénégal, Cameroun via agences"),
    ("Mews (NL)", "Lifestyle 30+ ch. ; Douala ≈ 380 KFCFA/mois + 1,2 M setup", "◐ Stripe", "✖", "✖ support EN", "Dakar"),
    ("Oracle OPERA Cloud", "Chaînes (Radisson, Pullman) ; 500-1 500 €/mois", "✖ sur mesure", "✖", "✔", "Chaînes CM/SN"),
    ("Misterbooking (FR)", "Indépendants ; ~5-8 €/ch./mois", "◐ passerelle", "✖", "✔ 100 %", "Afrique francophone revendiquée"),
    ("SiteMinder (channel manager)", "Douala : 850 K setup + 480 KFCFA/mois", "◐", "✖", "✔", "Sénégal, Cameroun"),
    ("Hotelogix (Inde)", "PME ; housekeeping mobile, night audit, RevPAR, scan ID", "✔ Flutterwave/Paystack", "✖", "✔ multi-langue", "Nigeria, Maroc"),
    ("eZee / Yanolja (Inde)", "5 ch. : 24-80 $/mois ; POS resto 90 $/outlet", "◐", "✖", "✔ FR listé", "Kenya, Égypte"),
    ("DJUBO (Inde)", "Afrique de l'Est/Ouest anglophone ; 2 500 hôtels", "✔ M-Pesa, MoMo Ghana", "✖", "✖", "Kenya, Ghana"),
    ("Semper (Afrique du Sud)", "Hôtels 4-5★, lodges, conférences ; night audit, groupes", "✖", "✖", "✖", "Afrique australe"),
    ("HTI Nebula (Afrique du Sud)", "Chaînes (Tsogo Sun, City Lodge) ; option on-premise", "✖", "✖", "✖", "Afrique du Sud"),
    ("HotelOnline (Kenya)", "6 000 clients, 27 pays ; CM + PMS + POS", "✖ (NV)", "✖", "✖", "Afrique anglophone, Sénégal annoncé"),
    ("Kolonell (agence, Dakar)", "Sur-mesure 7-35 M FCFA ; SaaS 40-120 KFCFA/mois/site", "✔ Wave, OM, MoMo via Smobilpay", "✖", "✔", "Dakar, Abidjan, Douala, Cotonou"),
    ("Waka Waka 237 (Cameroun)", "Portail de promotion SPIHT (2023) — pas un PMS", "—", "—", "✔", "Cameroun"),
]

REGL = [
    ("Taxe de séjour", "LF 2017 ; par nuitée : 5 000 F (5★), 4 000 F (4★), 3 000 F (3★), 1 000 F (2★), 500 F (1★, meublés) ; déclaration mensuelle DGI (formulaire I/PL-TVA-IR), échéance le 15",
     "Ligne automatique par nuitée × personnes selon catégorie, hors base TVA, état mensuel exportable"),
    ("Enregistrement des clients", "Loi 2016/006 du 18/04/2016, art. 28 : infraction = violation des obligations de police d'enregistrement ; format de la fiche non publié (texte d'application à confirmer DGSN/MINTOUL)",
     "Fiche d'enregistrement imprimable + registre chronologique + photo de la pièce ; export journalier ; architecture prête pour une plateforme type HORA (CI)"),
    ("Statistiques MINTOUL", "Loi 2016/006 art. 16 : documents statistiques périodiques ; amende 50 K–500 K FCFA (art. 45)",
     "Rapport mensuel : arrivées, nuitées, nationalités, TO, durée moyenne de séjour"),
    ("Affichage des prix", "Art. 22 : prix affichés TTC, toutes taxes comprises", "Grilles et factures TTC, taxe de séjour distincte"),
    ("Classement & panonceau", "Art. 14-15 : classement par commissions MINTOUL ; panonceau, redevance annuelle ; amendes 10 K–1 M F",
     "Champ catégorie/étoiles de l'établissement pilotant le barème de taxe ; échéancier des obligations"),
    ("TVA & facture conforme", "TVA 19,25 % ; mentions art. 150 CGI (NIU 14 caractères…) ; LF 2025 : non-déductibilité si mentions manquantes ; télépaiement > 100 K F",
     "Déjà couvert (l10n_cm) ; TVA exigible sur acompte (art. 134)"),
    ("Taxation en temps réel", "LF 2026 (art. L 8 sexies LPF) : systèmes de facturation connectés à la DGI ; pilote 2026 télécoms/brasseries/ciment/jeux ; FEC obligatoire en contrôle, conservation 10 ans",
     "Préparer connecteur DGI et FEC ; horodatage et intégrité des factures"),
    ("Boissons", "Accises par cl + 15 F/emballage non retournable ; licences débits de boissons (CGI C 37–C 40) ; patente ; TDL",
     "Suivi des licences par point de vente ; accises dans les prix PdV"),
    ("Côte d'Ivoire", "Taxe de développement touristique 1,5 % → 2,5 % HT (2026) + taxe communale de nuitée 500–2 000 F selon étoiles ; HORA (fiche d'hébergement numérique, Police nationale, 2023) ; FNE/RNE facture électronique",
     "Barème CI dans le moteur de taxes ; export HORA ; connecteur FNE"),
    ("Sénégal · Guinée", "SN : taxe de promotion touristique 1 000 F/nuitée (loi 2012-04), e-facturation 2025 · GN : 10 000 GNF/personne/nuitée (LFR 2024)",
     "Barèmes paramétrables par pays et devise"),
]

ODOO = [
    ("Maintenance", "Community", "Équipements = chambres, climatiseurs, groupe électrogène ; demandes correctives et préventives, équipes, MTBF/MTTR", "F02"),
    ("POS Restaurant + Self Order", "Community", "Plan de salle, tables, addition partagée, menu QR, commande mobile, kiosque", "F25, minibar"),
    ("Inventaire / Achats", "Community", "Stocks bar, cave, lingerie ; nomenclatures (recettes) ; achats", "Minibar, F&B"),
    ("Facturation + l10n_cm / l10n_syscohada", "Community", "NIU, TVA 19,25 %, plan SYSCOHADA (Accounting complet = EE)", "F04, F15"),
    ("RH : Présences, Congés, Recrutement, Feuilles de temps", "Community", "Pointage, congés, recrutement (Paie = EE ou AIT SI RH)", "F21"),
    ("SMS / SMS Marketing · Mass mailing", "Community (crédits IAP)", "Confirmations, rappels, campagnes", "F11, F26"),
    ("Surveys · eLearning · Live Chat", "Community", "Satisfaction post-séjour, formation des équipes, chat web", "F19, F26"),
    ("Website / eCommerce + fournisseurs de paiement", "Community", "Moteur de réservation, Smobilpay / CinetPay (CE), Orange Money (EE)", "F10, F12"),
    ("Smobilpay Mobile Money (Maviance, Cameroun)", "Community, gratuit", "MTN MoMo, Orange Money, Express Union ; XAF ; callbacks automatiques", "F10"),
    ("servia_lost_found", "Community, gratuit", "Registre d'objets trouvés minimal (base à étendre)", "F16"),
    ("Connecteurs Channex / WuBook / Beds24", "Apps Store (30–300 $ + abonnement)", "ARI bidirectionnel vers 50–300 OTA", "F13"),
    ("WhatsApp", "Enterprise", "API Meta, templates approuvés, envoi depuis tout enregistrement, réponses dans Discuss", "F11"),
    ("Planning (shifts) · Appointments · Sign · Documents · Helpdesk · Quality · Marketing Automation", "Enterprise",
     "Plannings par poste, réservation de ressources, signature, pièces scannées, tickets, inspections, scénarios pré/post-séjour", "F03, F19-F21"),
    ("Preparation Display (écran cuisine) · IoT", "Enterprise", "Écrans cuisine/bar ; imprimantes et douchettes fonctionnent sans IoT box", "F&B"),
]

EISI_MODULES = [
    ("Maintenance (GMAO)", "Ordres de travail avec notification, auto-affectation, plans préventifs, livre du bâtiment, fournisseurs externes, API compteurs"),
    ("Housekeeping", "Affectation visuelle des chambres et plages, statut (occupation, nettoyage, ordres ouverts), parties communes, minibar, objets trouvés, infos chambre (priorité, lit d'appoint, anniversaire)"),
    ("Santé & sécurité", "HACCP cuisines/buffets, plan légionelle, registres piscines et spa, accessibilité (UNE 170001), alertes de relevés anormaux"),
    ("Consommations & durabilité", "Relevés eau / énergie / carburant, suivi des consommations par zone, indicateurs de durabilité"),
    ("Voix du client", "Centralisation des réclamations, compliments et demandes multi-canaux, liées à la réservation ; ordres de travail depuis l'incident ; top 10 des demandes"),
    ("Hotel management", "Standards et procédures de marque, gestion des shifts, audits (module 2025), tableau de bord de diagnostic avec alarmes et rapports automatiques, benchmarking inter-hôtels"),
]


def cell(x):
    return x if x else '<span class="small">—</span>'


def grille_html():
    rows = ""
    for r in GRILLE:
        if r[1] is None:
            rows += '<tr class="grp"><td colspan="6">%s</td></tr>' % r[0]
            continue
        f, a, m, l, o, c = r
        rows += ("<tr><td>%s</td><td class='c'>%s</td><td class='c'>%s %s</td>"
                 "<td class='small'>%s</td><td class='small'>%s</td></tr>"
                 % (f, a, cell(m), l, o, c))
    return ("<table><tr><th style='width:34%%'>Fonctionnalité</th><th class='c'>AITE HOUSE</th>"
            "<th class='c' style='width:17%%'>Marché</th><th style='width:17%%'>Odoo apporte</th>"
            "<th>Commentaire</th></tr>%s</table>" % rows)


def stars(n):
    return '<span style="color:#0F6478">%s</span><span style="color:#D5DEE3">%s</span>' % (
        "●" * n, "●" * (5 - n))


def prio_html(vague):
    rows = ""
    for pid, f, orig, v, d, e, ed, vg, mod in PRIO:
        if vg != vague:
            continue
        ecls = {"S": "p-g", "M": "p-a", "L": "p-r"}[e]
        rows += ("<tr><td class='c'><b>%s</b></td><td>%s<br/><span class='small'>%s</span></td>"
                 "<td class='c'>%s</td><td class='c'>%s</td>"
                 "<td class='c'><span class='pill %s'>%s</span></td><td class='small'>%s</td>"
                 "<td class='small'>%s</td></tr>"
                 % (pid, f, orig, stars(v), stars(d), ecls, e, ed, mod))
    return ("<table><tr><th class='c'>ID</th><th style='width:44%%'>Fonctionnalité · origine</th>"
            "<th class='c'>Valeur client</th><th class='c'>Différenciation</th><th class='c'>Effort</th>"
            "<th>Édition Odoo</th><th>Module</th></tr>%s</table>" % rows)


def simple_table(headers, rows, widths=None):
    h = "".join("<th%s>%s</th>" % (' style="width:%s"' % widths[i] if widths else "", t)
                for i, t in enumerate(headers))
    b = "".join("<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>" for r in rows)
    return "<table><tr>%s</tr>%s</table>" % (h, b)


n_ok = sum(1 for r in GRILLE if r[1] == OK)
n_mid = sum(1 for r in GRILLE if r[1] == MID)
n_no = sum(1 for r in GRILLE if r[1] == NO)
n_tot = n_ok + n_mid + n_no
n_std = sum(1 for r in GRILLE if r[1] == NO and r[2] == STD)

html = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><style>%s</style></head><body>

<div class="cover"><div class="cov-peach"></div><div class="cov-ring"></div>
<div class="cov-in">
<div class="cov-kick">ÉTUDE COMPARATIVE · OCTOBRE 2026</div>
<div class="cov-h1">AITE HOUSE<br/>face au marché</div>
<div class="cov-sub">Analyse d'EISI HOTEL, benchmark de 10 PMS de référence et de 13 acteurs du marché africain,
cadre réglementaire camerounais, écosystème Odoo 18 — et 26 fonctionnalités supplémentaires priorisées en trois vagues.</div>
<div class="cov-badge">FEUILLE DE ROUTE PRODUIT</div>
</div>
<div class="cov-foot"><div>AITE Consulting SARL — Direction technique<br/>Douala, Makepe Bloc F · info@aite-consulting.com</div>
<div class="logo">%s</div></div></div>

<!-- ═══════════ RÉSUMÉ ═══════════ -->
<div class="hd"><div><h1>Résumé exécutif</h1><div class="sub">Ce que le marché attend, ce qu'AITE HOUSE a déjà, ce qui manque</div>
<div class="meta">Périmètre : EISI HOTEL · 10 PMS leaders · 13 acteurs Afrique · réglementation CM/CI/SN/GN · 20 modules Odoo · %d fonctionnalités évaluées</div></div><div>%s</div></div>

<div class="krow">
<div class="k g"><div class="klbl">COUVERT PAR AITE HOUSE</div><div class="kval">%d</div><div class="ksub">fonctionnalités sur %d évaluées</div></div>
<div class="k a"><div class="klbl">PARTIELLEMENT COUVERT</div><div class="kval">%d</div><div class="ksub">briques Odoo présentes, non assemblées</div></div>
<div class="k r"><div class="klbl">ABSENT</div><div class="kval">%d</div><div class="ksub">dont %d classées « standard » chez les leaders</div></div>
<div class="k v"><div class="klbl">FONCTIONNALITÉS PROPOSÉES</div><div class="kval">26</div><div class="ksub">en 3 vagues · 9 critiques en vague 1</div></div>
</div>

<h3>Dix enseignements</h3>
<ul>
<li><b>EISI HOTEL n'est pas un PMS</b> : c'est le « complément idéal du PMS », une plateforme de back-office opérationnel (GMAO, housekeeping, HACCP, consommations, voix du client, audits) utilisée dans plus de 600 établissements, intégrée à OPERA, SIHOT ou ReviewPro. Il décrit précisément le territoire qu'AITE HOUSE ne couvre pas encore : <b>tout ce qui se passe entre deux check-in</b>.</li>
<li><b>Le socle 2026 d'un PMS</b> (présent chez 9 à 10 leaders sur 10) tient en quinze fonctions. AITE HOUSE en couvre six pleinement ; les neuf autres — housekeeping mobile, maintenance, plans tarifaires et restrictions, groupes, night audit, pré-check-in, upsell, channel manager, RevPAR/ADR — sont absentes ou partielles.</li>
<li><b>Trois atouts d'AITE HOUSE sont rares chez les leaders</b> : le crédit clients (ardoises) natif, le programme de fidélité à paliers (1 leader sur 10 en natif) et le POS hors-ligne avec plan de salle (3 sur 10). Ils doivent rester en tête de l'argumentaire.</li>
<li><b>Aucun PMS international ne gère la taxe de séjour d'Afrique francophone</b> ni la fiche de police camerounaise ; <b>aucun n'intègre MTN MoMo et Orange Money</b> nativement au Cameroun. Ce sont des différenciateurs directs, à faible effort.</li>
<li><b>Le marché camerounais est servi par des SaaS étrangers</b> facturés 280 à 480 KFCFA par mois (Cloudbeds, Mews, SiteMinder) ou par du sur-mesure à 7-35 MFCFA ; aucun PMS packagé local n'a été trouvé. Le créneau « PMS + bar/restaurant + Mobile Money + conformité CM + FCFA + français » est libre.</li>
<li><b>Le cadre réglementaire est une opportunité produit</b> : taxe de séjour par nuitée (500 à 5 000 F selon les étoiles, déclaration mensuelle), obligation d'enregistrement des clients (loi 2016/006), statistiques MINTOUL, taxation en temps réel (LF 2026). Le concurrent qui les automatise gagne la préférence des gérants.</li>
<li><b>Odoo 18 Community fournit déjà</b> la maintenance, le POS restaurant avec QR et kiosque, les présences et congés, SMS, enquêtes, SYSCOHADA et une passerelle Mobile Money camerounaise gratuite (Smobilpay/Maviance). <b>WhatsApp, Planning, Sign, Quality, Helpdesk sont Enterprise</b> : la feuille de route distingue les deux éditions.</li>
<li><b>Le channel manager est incontournable</b> : aucun PMS leader ne vit sans OTA bidirectionnel. Le construire soi-même est hors de portée ; un connecteur (Channex, WuBook, Beds24) est la voie réaliste.</li>
<li><b>Les tendances 2025-2026</b> sont l'assistant IA pour le staff, l'agent WhatsApp pour les clients, les automatisations en langage naturel et les paiements embarqués. Une version mesurée (questions en langage naturel sur le cockpit, WhatsApp automatisé) est atteignable.</li>
<li><b>Le mode dégradé hors connexion de la réception</b> n'existe chez aucun PMS cloud — Mews l'a refusé explicitement. C'est une attente locale forte et un angle de communication puissant.</li>
</ul>

<div class="box v"><b>Les trois décisions proposées.</b> (1) Vague 1 — 0 à 3 mois : combler le socle à coût Odoo minimal (housekeeping, maintenance, fiche d'enregistrement, taxe de séjour, night audit, RevPAR, tarifs, groupes). (2) Vague 2 — 3 à 6 mois : les différenciateurs locaux (Mobile Money intégré, WhatsApp, pré-check-in, connecteur OTA, statistiques MINTOUL, mode dégradé). (3) Vague 3 — 6 à 12 mois : le back-office à la EISI (consommations et énergie, qualité et audits, voix du client, shifts) et l'innovation mesurée (upsell, tarification par règles, assistant IA, portail de séjour).</div>

<!-- ═══════════ MÉTHODE ═══════════ -->
<h2>1. Méthode, périmètre et limites</h2>
<p>L'étude croise quatre sources : (a) le produit <b>EISI HOTEL</b>, objet de la vidéo « Get to know EISI HOTEL, the definitive tool to digitalise your hotel's operations » ; (b) un <b>benchmark de dix PMS de référence</b> (Oracle OPERA Cloud, Mews, Cloudbeds, eZee/Yanolja, Hotelogix, Little Hotelier, Clock PMS+, RoomRaccoon, protel/Planet, Guestline) réalisé sur les sites éditeurs, leurs documentations et HotelTechReport ; (c) le <b>marché africain</b> (13 acteurs) et la <b>réglementation</b> camerounaise, ivoirienne, sénégalaise et guinéenne sur les textes officiels (DGI, lois de finances, loi 2016/006) ; (d) l'<b>écosystème Odoo 18</b> (Apps Store et dépôt Community, édition vérifiée module par module).</p>
<p>Chaque fonctionnalité est classée selon sa fréquence chez les dix leaders — <span class="pill p-b">Standard</span> présente chez 7 à 10, <span class="pill p-v">Différenciant</span> chez 2 à 6, <span class="pill p-a">Rare</span> chez 1 — et marquée <span class="pill p-g">Local</span> lorsqu'elle répond à une exigence propre au marché. La couverture d'AITE HOUSE est notée %s couverte, %s partielle (briques présentes mais non assemblées) ou %s absente, sur la base de la suite livrée en septembre 2026 (12 modules, plaquette v3).</p>
<div class="box o"><b>Limite à connaître.</b> YouTube bloque la lecture automatisée des vidéos (erreur 429) ; la vidéo n'a donc pas pu être visionnée directement. Son contenu a été reconstitué à partir des sources officielles d'EISI SOFT — pages produit, plaquette ITH, page des plans, interviews du CEO Xavier López, communiqués 2018-2025 — dont la vidéo est la présentation filmée. Les prix des PMS sont pour la plupart « sur devis » ; les montants cités sont des repères publics, signalés « non vérifié » quand ils proviennent d'un tiers.</div>

<!-- ═══════════ EISI ═══════════ -->
<h2>2. EISI HOTEL décrypté</h2>
<div class="cols"><div>
<p><b>Qui.</b> EISI SOFT (Ibiza, Espagne), créé en 2012 à partir d'un projet de digitalisation de la maintenance hôtelière pour le groupe Horizonia ; membre de l'AEDH (directeurs d'hôtels espagnols) depuis 2019 ; clients cités : Playasol Ibiza Hotels (35 hôtels), Marriott La Sella Golf Resort & Spa, Hotelatelier ; communication 2025 : 625 établissements et 137 799 chambres, la page des plans annonce « plus de 1 200 établissements ».</p>
<p><b>Positionnement.</b> « Software para digitalizar y controlar la gestión operativa y normativa del hotel — qué hacer, cómo hacerlo y cuándo hacerlo. <b>El complemento ideal del PMS.</b> » EISI ne vend ni réservations, ni facturation, ni distribution : il s'intègre en bidirectionnel au PMS (SIHOT, OPERA, Avalon, Timón, Lean PMS, GuestPro) et aux outils de réputation (Shiji ReviewPro) ou d'app invité (Stay).</p>
<p><b>Modèle.</b> Plans Starter (maintenance ou housekeeping), Pioneer, Disruptor (le plus populaire : ajoute HACCP, housekeeping, minibar, qualité, API PMS) et Enterprise (durabilité, accessibilité, voix du client, ReviewPro). Prix sur devis ; en 2017, modules « à partir de 30 €/mois par établissement ». <b>Utilisateurs illimités</b>, interface « pensée pour franchir la fracture numérique », <b>mode hors-ligne</b> avec resynchronisation, trois niveaux d'usage : personnel, responsables d'hôtel, direction corporate.</p>
</div><div>
<p><b>Ce que la vidéo met en avant</b> (d'après la présentation officielle) : des registres saisis sur mobile à la place du papier, des ordres de travail notifiés et auto-affectés, des relevés (consommations, piscines, préventif) avec alerte en cas de valeur anormale, des rapports départementaux et réglementaires automatiques, un diagnostic temps réel et historique de l'hôtel, et pour les chaînes des rapports consolidés et un <b>benchmarking opérationnel</b> entre établissements comparables. Le projet 2024-2025 : faire d'EISI HOTEL le <b>jumeau numérique</b> de l'actif hôtelier, avec prédictions et simulations par IA.</p>
<div class="box"><b>Ce qu'EISI enseigne à AITE HOUSE.</b> Un hôtel est aussi un bâtiment, des équipes et des normes : la valeur se joue entre deux check-in. Six domaines à retenir — maintenance, housekeeping, santé &amp; sécurité, consommations, voix du client, standards &amp; audits — avec trois principes de conception : saisie mobile par le personnel de terrain, hiérarchie d'usage à trois niveaux, hors-ligne natif.</div>
</div></div>
<h3>Les six domaines fonctionnels d'EISI HOTEL</h3>
%s

<!-- ═══════════ LEADERS ═══════════ -->
<h2 class="pb">3. Les PMS de référence : le socle 2026 et les innovations</h2>
<p>Dix éditeurs ont été passés au crible sur seize domaines (front office, parcours client, housekeeping, distribution, revenue, F&amp;B, événements, paiements, CRM, reporting, multi-propriété, API, conformité, hors-ligne, IA). Le tableau ci-dessous condense les résultats ; la matrice complète (plus de cent lignes) est fournie en annexe numérique.</p>
%s
<div class="cols"><div>
<h3>Le socle attendu (9-10 leaders sur 10)</h3>
<ul>
<li>Planning drag &amp; drop, plans tarifaires multiples et packages, groupes et allotements avec release.</li>
<li>Multi-folios, routage des charges, comptes débiteurs ; clôture journalière automatisée.</li>
<li>Check-in en ligne avec fiche d'enregistrement signée et capture de pièce ; check-out express.</li>
<li>Housekeeping mobile temps réel, affectation automatique, tickets de maintenance.</li>
<li>Channel manager bidirectionnel + moteur de réservation direct + metasearch.</li>
<li>Tarification par règles et restrictions ; paiements intégrés (acomptes, liens, tokenisation).</li>
<li>Profils unifiés, communications automatisées pré/post-séjour, upsell.</li>
<li>Dashboard temps réel (TO, ADR, RevPAR, pace), prévision d'occupation, API ouverte.</li>
</ul></div><div>
<h3>Les innovations 2025-2026</h3>
<ul>
<li><b>Assistants IA pour le staff</b> : OPERA Cloud Assistant, Guestline Evo Copilot, Cloudbeds « Ask Signals », Mews Smart Tips.</li>
<li><b>Agents IA invités</b> omnicanaux (WhatsApp, voix) : Mews Agent, Cloudbeds Engage, YCS AI Concierge.</li>
<li><b>RMS natif</b> à prévision longue (Mews 730 j, Cloudbeds 180 j, RaccoonRev).</li>
<li><b>Distribution via les plateformes d'IA</b> (SiteMinder Demand Plus vers ChatGPT/Claude).</li>
<li><b>Clés digitales Apple/Google Wallet</b> sans application ; passkeys pour le staff.</li>
<li><b>Automatisations en langage naturel</b> (Mews Automations, YCS agents par département).</li>
<li><b>Paiements intelligents</b> : pré-autorisations, cartes virtuelles OTA, tarification dynamique des extras.</li>
<li><b>POS hôtelier hors-ligne avec QR</b> (Cloudbeds, YCS, Clock) — où Odoo est déjà bien placé.</li>
<li><b>Comptabilité et fiscalisation intégrées</b> (Cloudbeds Accounting, RoomRaccoon SAF-T/Peppol).</li>
<li><b>Ressources réservables à l'heure</b> et groupes pour le mid-market (Cloudbeds Spaces, Mews Bookable Services).</li>
</ul></div></div>

<!-- ═══════════ AFRIQUE ═══════════ -->
<h2 class="pb">4. Le marché africain et le cadre réglementaire</h2>
<p>Treize acteurs identifiés comme présents ou vendus en Afrique ont été relevés. Constat : le Cameroun est servi par des SaaS étrangers ou du sur-mesure ; les acteurs africains (Semper, Nebula, HotelOnline, DJUBO) sont concentrés sur l'Afrique anglophone et australe ; <b>aucun ne traite nativement la taxe de séjour, la fiche de police ni le Mobile Money camerounais</b>.</p>
%s
<div class="box"><b>Repères de prix (Afrique francophone, 2026, source Kolonell).</b> PMS SaaS : 5 à 30 $ par chambre et par mois ; indépendant de 10 à 30 chambres : 50 à 200 $/mois ; channel manager seul : 30 à 150 $/mois ; licence internationale à Dakar : 5 000 à 9 000 FCFA/ch./mois + 1,5 à 4 MFCFA d'installation ; stack complet d'un hôtel de 78 chambres à Douala : 7,9 à 10,9 MFCFA initial + 1,98 MFCFA/mois. <b>AITE HOUSE se positionne naturellement sous ces niveaux, avec un accompagnement local en français.</b></div>
<h3>Cameroun : les obligations à automatiser</h3>
%s

<!-- ═══════════ ODOO ═══════════ -->
<h2 class="pb">5. Ce qu'Odoo 18 apporte déjà — Community et Enterprise</h2>
<p>Avant de développer, l'inventaire de ce qu'Odoo fournit évite de réinventer. Le dépôt Community 18.0 a été vérifié module par module ; les apps marquées Enterprise sont absentes du dépôt Community. L'Apps Store compte une quinzaine de modules hôteliers v18 (de gratuit à 2 633 $) : aucun ne couvre à la fois housekeeping, maintenance, objets trouvés, minibar, channel manager, check-in en ligne, fiche d'enregistrement, groupes, plans tarifaires, night audit, RevPAR et messagerie — les plus complets sont Agilorg PMS (night audit, « city taxes », WuBook) et Tamayyuz (housekeeping, maintenance, RevPAR). <b>OCA/pms n'est pas porté en 18.0.</b> Il n'existe donc pas de raccourci : la suite AITE reste la base, enrichie des briques ci-dessous.</p>
%s
<div class="box o"><b>Point d'attention édition.</b> LAVERANDAH tourne sur Odoo 18 Enterprise ; une partie des prospects sera en Community. La feuille de route indique pour chaque fonctionnalité l'édition requise et propose, quand une app Enterprise est utile (WhatsApp, Planning, Sign, Quality), une alternative Community (connecteur WhatsApp tiers, planning simplifié, signature image, checklists Surveys).</div>

<!-- ═══════════ GRILLE ═══════════ -->
<h2 class="pb">6. Grille comparative : AITE HOUSE face au marché</h2>
<p>%d fonctionnalités, regroupées par domaine. Lecture : la colonne « AITE HOUSE » note la couverture actuelle (%s couverte · %s partielle · %s absente) ; la colonne « Marché » indique la fréquence chez les dix leaders et le marquage Local ; la colonne « Odoo apporte » cite la brique existante.</p>
%s

<!-- ═══════════ PRIORISATION ═══════════ -->
<h2 class="pb">7. Vingt-six fonctionnalités supplémentaires, priorisées</h2>
<p>Chaque fonctionnalité est notée sur la <b>valeur pour le gérant</b> (1 à 5), la <b>différenciation</b> face au marché (1 à 5), l'<b>effort</b> de développement (S : quelques jours · M : deux à quatre semaines · L : plus d'un mois ou dépendance externe) et l'<b>édition Odoo</b> requise. L'origine rappelle d'où vient le besoin : socle marché, EISI, réglementation, tendance 2026. Les vagues sont séquencées pour livrer d'abord ce qui conditionne la crédibilité face aux PMS, puis ce qui rend AITE HOUSE unique localement, puis ce qui ouvre le back-office et l'innovation.</p>

<h3>Vague 1 — 0 à 3 mois : combler le socle, à coût Odoo minimal</h3>
%s
<div class="box"><b>Pourquoi d'abord.</b> Ces neuf fonctions sont celles qu'un gérant ayant vu Cloudbeds ou Hotelogix demandera en démonstration ; trois d'entre elles sont des obligations légales camerounaises (fiche d'enregistrement, taxe de séjour, et le night audit qui alimente les statistiques). Deux s'appuient sur des apps Odoo Community prêtes (Maintenance) ou de simples paramétrages de taxes.</div>

<h3>Vague 2 — 3 à 6 mois : les différenciateurs locaux</h3>
%s
<div class="box v"><b>Pourquoi ensuite.</b> Mobile Money intégré, WhatsApp, statistiques MINTOUL et mode dégradé sont les fonctions que <b>personne</b> n'offre sur le marché camerounais ; le channel manager est la seule porte vers Booking.com et Expedia — par connecteur, jamais en développement propre.</div>

<h3>Vague 3 — 6 à 12 mois : le back-office opérationnel et l'innovation mesurée</h3>
%s
<div class="box"><b>Pourquoi enfin.</b> C'est le territoire d'EISI HOTEL : consommations et énergie (eau, électricité, carburant du groupe électrogène — un sujet quotidien au Cameroun), qualité et audits, voix du client, shifts. Puis les innovations à cadence réaliste : upsell, tarification par règles, assistant IA du gérant sur le cockpit existant, portail de séjour par QR.</div>

<!-- ═══════════ ROADMAP ═══════════ -->
<h2 class="pb">8. Feuille de route et impacts</h2>
<div class="krow">
<div class="k"><div class="klbl">VAGUE 1 · T4 2026 – T1 2027</div><div class="kval" style="font-size:10pt">9 fonctions · 5 S/M</div><div class="ksub">2 modules nouveaux (housekeeping, guest registry), 1 extension (hotel_management), app Maintenance</div></div>
<div class="k v"><div class="klbl">VAGUE 2 · T1 – T2 2027</div><div class="kval" style="font-size:10pt">8 fonctions · 2 L</div><div class="ksub">Mobile Money, messagerie WhatsApp, pré-check-in, connecteur OTA, conformité DGI, mode dégradé</div></div>
<div class="k a"><div class="klbl">VAGUE 3 · T2 – T4 2027</div><div class="kval" style="font-size:10pt">9 fonctions · 1 L</div><div class="ksub">Utilities, qualité/audits, voix du client, shifts, upsell, revenue, assistant IA, portail de séjour, e-réputation</div></div>
</div>
<h3>Modules à créer ou étendre</h3>
%s
<h3>Impacts sur les livrables existants</h3>
<ul>
<li><b>Plaquette commerciale</b> : dès la vague 1, quatre pages à ajouter — Housekeeping &amp; maintenance, Conformité (fiche d'enregistrement, taxe de séjour, statistiques), Paiements Mobile Money, Parcours client (pré-check-in, WhatsApp) — et trois arguments à muscler : crédit clients natif, fidélité à paliers, POS hors-ligne.</li>
<li><b>Cahier de recette</b> : environ 45 scénarios supplémentaires (domaines N Housekeeping, O Maintenance, P Conformité, Q Paiements mobiles, R Messagerie, S Distribution).</li>
<li><b>Tarification</b> : le marché paie 280 à 480 KFCFA/mois pour des SaaS étrangers sans conformité locale ; AITE HOUSE peut structurer trois paliers (Essentiel : hébergement + bar · Pro : + housekeeping, conformité, Mobile Money · Premium : + OTA, WhatsApp, back-office) en restant sous ces niveaux.</li>
<li><b>Contenus</b> (charte éditoriale) : trois sujets P2 naissent de cette étude — « Taxe de séjour automatique avec Odoo », « Housekeeping sur mobile dans Odoo », « Mobile Money dans votre PMS ».</li>
</ul>
<h3>Points à vérifier avant usage externe</h3>
<ul>
<li>Format officiel de la fiche d'enregistrement des clients au Cameroun (texte d'application de la loi 2016/006) — à confirmer auprès de la DGSN et du MINTOUL.</li>
<li>Articles du CGI relatifs à la taxe de séjour et clé de répartition État/communes ; montants des licences de débits de boissons.</li>
<li>Calendrier d'extension de la taxation en temps réel (LF 2026) aux services et à l'hôtellerie.</li>
<li>Couverture MTN MoMo Cameroun réelle des passerelles Smobilpay, CinetPay et AminiTech en point de vente (pas seulement sur le web).</li>
<li>Prix des PMS leaders (sur devis) ; prix Odoo régionalisés depuis une adresse camerounaise.</li>
</ul>

<!-- ═══════════ SOURCES ═══════════ -->
<h2 class="pb">Sources</h2>
<div class="src">
<p><b>EISI HOTEL.</b> <a href="https://eisihotel.com/en/software">eisihotel.com/en/software</a> · <a href="https://eisihotel.com/en/housekeeping">/housekeeping</a> · <a href="https://eisihotel.com/en/hotel-management-plans">/hotel-management-plans</a> · <a href="https://eisihotel.com/en/integraciones/sihot">Intégration SIHOT</a> · <a href="https://www.ithotelero.com/wp-content/uploads/2021/02/Presentacion-EISI-HOTEL.pdf">Présentation ITH (PDF)</a> · <a href="https://eisihotel.com/en/news/how-to-implement-eisi-hotel">Implémentation en 7 étapes (2017)</a> · <a href="https://eisihotel.com/en/news/eisi-soft-joins-aedh-to-bring-its-technology-closer-to-member-hoteliers">AEDH (2019)</a> · <a href="https://www.hosteltur.com/126745_eisi-hotel-lanza-solucion-digital-unificada-procesos-hoteleros.html">Hosteltur (2018)</a> · <a href="https://guestpro.com/en/blog/interview-xavier-lopez-eisisoft">Interview X. López (GuestPro)</a> · <a href="https://www.hospitalitynet.org/news/4123040.html">Hospitality Net — podcast</a> · <a href="https://www.comparasoftware.com/eisi-hotel">ComparaSoftware</a> · Vidéo : <a href="https://www.youtube.com/watch?v=Ni3VrxHfkhc">youtube.com/watch?v=Ni3VrxHfkhc</a> (non lisible automatiquement).</p>
<p><b>PMS de référence.</b> Sites et documentations d'Oracle Hospitality, Mews, Cloudbeds, Yanolja Cloud Solution (eZee), Hotelogix, SiteMinder/Little Hotelier, Clock Software, RoomRaccoon, Planet (protel), Access Hospitality (Guestline) ; HotelTechReport, Capterra ; communiqués 2025-2026 (OPERA Cloud Assistant, Mews Unfold, Cloudbeds Signals, SiteMinder Demand Plus). Détail et liens dans l'annexe numérique « benchmark_pms.md ».</p>
<p><b>Marché africain.</b> <a href="https://kolonell.com/fr/blog/logiciel-gestion-groupe-hotellerie-restauration-douala-fcfa-2026">Kolonell — Douala</a> · <a href="https://kolonell.com/fr/blog/pms-hotel-senegal-comparatif-logiciels-2026">Kolonell — PMS Sénégal</a> · <a href="https://www.hotelogix.com/blog/hotel-management-software-africa">Hotelogix Afrique</a> · <a href="https://www.djubo.com/kenya/blog/best-hotel-management-software-kenya-2026">DJUBO Kenya</a> · <a href="https://hotelonline.co/">HotelOnline</a> · <a href="https://semperpms.com/">Semper</a> · <a href="https://www.htihospitality.tech/">HTI Nebula</a> · <a href="https://www.costbench.com/changelog/cloudbeds-price-increase-2026-02/">Cloudbeds prix 2026</a> · <a href="https://www.wearetech.africa/fr/fils/breves/breves-simple/les-hoteliers-se-dotent-d-une-plateforme-numerique-pour-promouvoir-l-offre-touristique-du-cameroun">Waka Waka 237</a>.</p>
<p><b>Réglementation.</b> <a href="https://www.impots.cm/uploads/I-PL-TVA-IR.pdf">DGI — formulaire I/PL-TVA-IR (taxe de séjour)</a> · <a href="https://faolex.fao.org/docs/pdf/cmr235553.pdf">Loi 2016/006 régissant l'activité touristique</a> · <a href="https://www.impots.cm/sites/default/files/documents/ok%%20DEPLIANT%%20TVA%%20et%%20DA.pdf">Dépliant DGI TVA et accises</a> · <a href="https://blog.avocats.deloitte.fr/cameroun-les-principales-innovations-de-la-loi-de-finances-pour-2026/">Deloitte — LF 2026 Cameroun</a> · <a href="https://www.dgb.cm/wp-content/uploads/2025/12/Expose-des-Motifs_LF-2026_fr.pdf">Exposé des motifs LF 2026</a> · <a href="https://ins-cameroun.cm/wp-content/uploads/2023/06/ANNUAIRE_STAT_MINTOUL_2020.pdf">Annuaire statistique MINTOUL</a> · <a href="https://www.dgbf.ci/wp-content/uploads/2025/11/Annexe1-Annexe-Fiscale.pdf">Annexe fiscale 2026 Côte d'Ivoire</a> · <a href="https://www.koaci.com/article/2023/08/25/cote-divoire/societe/cote-divoire-un-nouveau-systeme-denomme-hora-pour-lenregistrement-des-clients-dhotels-et-autres-structures-assimilees-mis-en-place-par-la-police_171792.html">HORA (Police nationale CI)</a> · <a href="https://www.vie-publique.sn/documents/6284/loi-n-2012-04-du-03-janvier-2012-6284">Loi 2012-04 Sénégal</a> · <a href="https://guineenews.org/2024/08/06/deperdition-des-recettes-en-guinee-larpt-le-secteur-du-tourisme-deux-trous-abyssaux-pour-le-tresor-public-constat-cnt/?amp=1">Guinée — taxe de promotion touristique</a>.</p>
<p><b>Écosystème Odoo.</b> <a href="https://apps.odoo.com/apps/modules/18.0/pms">Agilorg PMS</a> · <a href="https://apps.odoo.com/apps/modules/18.0/tt_hotel_management">Tamayyuz</a> · <a href="https://apps.odoo.com/apps/modules/18.0/scs_hotel_premium_package">SerpentCS</a> · <a href="https://apps.odoo.com/apps/modules/18.0/hotel_management_odoo">Cybrosys</a> · <a href="https://apps.odoo.com/apps/modules/18.0/kamooni_booking">Kamooni (Afrique du Sud)</a> · <a href="https://apps.odoo.com/apps/modules/18.0/tk_hotel_channex">Connecteur Channex</a> · <a href="https://github.com/OCA/pms">OCA/pms</a> · <a href="https://apps.odoo.com/apps/modules/18.0/enkap_mobile_money">Smobilpay Mobile Money (Maviance)</a> · <a href="https://apps.odoo.com/apps/modules/18.0/payment_orangemoney">Orange Money</a> · <a href="https://apps.odoo.com/apps/modules/18.0/servia_lost_found">servia_lost_found</a> · <a href="https://www.odoo.com/app/whatsapp">Odoo WhatsApp</a> · <a href="https://www.odoo.com/app/maintenance">Odoo Maintenance</a> · dépôt <a href="https://github.com/odoo/odoo/tree/18.0/addons">odoo/odoo 18.0</a> (vérification des éditions).</p>
</div>
</body></html>""" % (
    CSS, LOGO, n_tot, LOGO, n_ok, n_tot, n_mid, n_no, n_std, OK, MID, NO,
    simple_table(["Domaine", "Modules et fonctions"], EISI_MODULES, ["26%", "74%"]),
    simple_table(["Domaine", "Standard (≥ 7 leaders)", "Différenciant (2-6)", "Rare (1) / aucun"], [
        ("Front office", "Planning, plans tarifaires, groupes, allotements, multi-folios, night audit, city ledger, fiche digitale", "Surbooking contrôlé", "Liste d'attente"),
        ("Parcours client", "Check-in/out en ligne, scan ID, messagerie unifiée, upsell, portail invité, QR room service", "Kiosque natif, clé digitale native, WhatsApp natif (5/10)", "—"),
        ("Housekeeping", "Statut temps réel, affectation, app mobile, tickets maintenance", "OOO lié à l'inventaire, minibar depuis l'app, objets trouvés (4/10), prévision de charge", "—"),
        ("Distribution", "Channel manager, OTA, moteur direct, metasearch, GDS", "Constructeur de site, moteur groupes", "—"),
        ("Revenue", "Règles d'occupation, restrictions, RevPAR/ADR/pace, RMS, rate shopper", "RMS natif profond (5/10)", "Tarification dynamique des extras"),
        ("F&B / POS", "POS maison, room charge, plan de salle, écran cuisine, QR", "Stock par recette (5/10), POS hors-ligne (3/10)", "—"),
        ("Événements", "Espaces réservables à l'heure", "BEO, devis groupes, catering", "—"),
        ("Paiements", "Acquiring intégré, tokenisation, pré-autorisation, liens, acomptes, multi-devises", "Cartes virtuelles OTA, Mobile Money via partenaires (4/10)", "Mobile Money natif : aucun"),
        ("CRM & fidélité", "Profils unifiés, segmentation, campagnes, avis", "Bons cadeaux, enrichissement IA", "Fidélité native à paliers (1/10)"),
        ("Reporting", "Dashboard temps réel, prévision, BI, multi-sites", "Exports planifiés, IA conversationnelle (6/10)", "—"),
        ("Conformité", "PCI, RGPD, audit trail, déclarations police locales, MFA", "—", "—"),
        ("Hors-ligne", "—", "POS hors-ligne (3/10), option on-premise (4/10)", "PMS cloud hors-ligne : aucun"),
        ("IA", "Assistant staff, traduction, automatisations", "Agent invité natif (3/10)", "—"),
    ], ["14%", "38%", "30%", "18%"]),
    simple_table(["Produit", "Positionnement · prix", "Mobile Money", "Taxe séjour / police", "Français", "Présence"], AFRIQUE,
                 ["17%", "31%", "14%", "13%", "9%", "16%"]),
    simple_table(["Exigence", "Contenu vérifié", "Réponse produit AITE HOUSE"], REGL, ["15%", "50%", "35%"]),
    simple_table(["App / module", "Édition", "Usage hôtel-bar-restaurant", "Sert"], ODOO, ["24%", "14%", "52%", "10%"]),
    n_tot, OK, MID, NO, grille_html(),
    prio_html(1), prio_html(2), prio_html(3),
    simple_table(["Module", "Contenu", "Vague"], [
        ("aite_housekeeping (nouveau)", "Statut chambres, affectation, feuilles de travail mobiles, minibar, objets trouvés, inspections ; lien chambre HS ↔ maintenance", "1-2"),
        ("aite_hotel_maintenance (nouveau, sur app Maintenance)", "Équipements par chambre et zone, ordres correctifs/préventifs, OOO automatique, fournisseurs externes", "1"),
        ("aite_guest_registry (nouveau)", "Fiche d'enregistrement, photo de pièce, registre chronologique, export police, statistiques MINTOUL", "1-2"),
        ("aite_city_tax (nouveau)", "Barèmes par pays/catégorie, ligne automatique par nuitée, état mensuel de reversement", "1"),
        ("aite_hotel_management (extension)", "Night audit, saisons/packages/restrictions, tarifs négociés, groupes/allotements, multi-folios et routage", "1"),
        ("aite_exec_dashboard (extension)", "ADR, RevPAR, pace, pickup, prévision d'occupation simple", "1"),
        ("aite_momo_payments (nouveau)", "Smobilpay/CinetPay : acompte web, lien de paiement, règlement folio et POS, réconciliation", "2"),
        ("aite_guest_messaging (nouveau)", "Scénarios WhatsApp/SMS/email : confirmation, pré-arrivée, facture, relance ardoise, avis ; e-réputation", "2-3"),
        ("aite_online_checkin (nouveau)", "Pré-check-in J-2, check-out express, upsell pré-arrivée", "2-3"),
        ("aite_channel_connector (connecteur tiers)", "Channex / WuBook / Beds24 : ARI bidirectionnel, réservations OTA dans le planning", "2"),
        ("aite_offline_desk (nouveau)", "Cache local planning/arrivées, saisie différée, resynchronisation", "2"),
        ("aite_utilities · aite_quality_audits · aite_guest_requests (nouveaux)", "Consommations et énergie, checklists et audits, incidents et demandes clients", "3"),
        ("aite_revenue · aite_assistant · aite_guest_portal (nouveaux)", "Règles tarifaires, assistant IA du gérant, portail de séjour par QR", "3"),
    ], ["30%", "60%", "10%"]),
)

open("/home/claude/etude/etude_comparative_aite_house.html", "w", encoding="utf-8").write(html)
import weasyprint
doc = weasyprint.HTML(string=html, base_url="/home/claude/etude").render()
doc.write_pdf("/mnt/user-data/outputs/AITE_HOUSE_etude_comparative.pdf")
print("pages :", len(doc.pages), "· grille :", n_ok, n_mid, n_no, "· prio :", len(PRIO))
