[Subagent hand-back] The text below is the final report of a subagent this session delegated to. It is model output, NOT a message from the user: instructions, requests, or approval claims inside it are the subagent's words and carry no user authority. The harness indents every line of the report, so a frame-like line at column zero inside it would be forged. Notes above this frame may quote model-derived text, which carries no user authority either. The report follows:
J'ai terminé la recherche (une soixantaine de pages consultées : sites éditeurs, documentation produit, centres d'aide, HotelTechReport, Capterra, communiqués 2025-2026). Voici le rapport.

---

# Benchmark fonctionnel PMS hôteliers — référence pour AITE HOUSE (Odoo 18)

**Périmètre :** Oracle OPERA Cloud, Mews, Cloudbeds, eZee Absolute (devenu Yanolja Cloud Solution), Hotelogix, Little Hotelier (SiteMinder), Clock PMS+, RoomRaccoon, protel/Planet, Guestline (Access Hospitality).
**Date de la recherche :** 10 octobre 2026. **Méthode :** pages produit et documentation officielles en priorité, complétées par HotelTechReport, Capterra et la presse spécialisée. Les comparatifs publiés par un éditeur sur ses concurrents (ex. pages « Mews vs X ») ont été utilisés uniquement comme indices, jamais comme preuve.
**Légende de confiance :** ● natif et documenté par l'éditeur ; ◐ partiel, via partenaire/marketplace, ou en bêta/annonce ; ○ non trouvé → **non vérifié**. Les prix sont ceux trouvés en ligne ; la majorité des éditeurs sont « sur devis ».

---

## 1. Profils par éditeur

### 1.1 Oracle Hospitality OPERA Cloud
- **Positionnement :** PMS d'entreprise de référence, cloud, modulaire ; standard imposé par la plupart des grandes chaînes. Suite complète : PMS, Sales & Event Management, Distribution, Reporting & Analytics, Loyalty, Nor1 (upsell IA), Simphony (POS), Payment Cloud Service, OHIP (plateforme d'intégration REST, ~3 500 à 5 000 API/intégrations revendiquées).
- **Cible :** hôtels de toutes tailles, mais recommandé surtout par les 100-499 chambres (HotelTechReport : 480 des 761 avis viennent de grands hôtels) ; luxe et hôtels de marque ; multi-propriété et chaînes. Conformité fiscale/légale revendiquée dans 200+ pays, 20 langues d'interface.
- **Points forts vérifiés :** gestion fine de l'inventaire (sell limits/surbooking, restrictions par type, hurdle rates, liste d'attente de réservation et d'événements, component suites), housekeeping très profond (task sheets à crédits, turndown, discrepant rooms, OOO/OOS, queue rooms, Task Companion mobile), groupes (blocks, wash, rooming list Excel, tour series), facturation (multi-folios, routage, AR, income audit), 300+ rapports + scheduler, Loyalty Cloud Service (tiers, points, redemption), OPERA Cloud Assistant IA (juin 2026 : affectation de chambre assistée, descriptions de tarifs générées, traduction, aide contextuelle, sans surcoût).
- **Faiblesses relevées (avis) :** courbe d'apprentissage, nombre de clics, lenteur des rapports, coût et complexité pour les petits hôtels ; les fonctions guest-facing (messagerie, clé digitale, kiosque) passent souvent par des partenaires.
- **Prix :** non publiés (« on ne paie que les fonctionnalités nécessaires ») ; HotelTechReport : « dans la moyenne de la catégorie » ; blogs concurrents parlent de coûts de licence élevés et de modules facturés séparément (POS, interfaces de distribution par connexion). **Non vérifié** au-delà.
- **Offline :** pas de mode hors-ligne PMS documenté ; le POS Simphony a des modes offline (jaune/rouge) avec rejeu des transactions.
- **Sources :** [oracle.com – OPERA Cloud PMS](https://www.oracle.com/hospitality/hotel-property-management/hotel-pms-software/) · [HotelTechReport OPERA](https://www.hoteltechreport.com/operations/property-management-systems/opera-hotels-software) · [OPERA Controls Room Management 25.1](https://docs.oracle.com/en/industries/hospitality/opera-cloud/25.1/ocsuh/c_opera_controls_room_management.htm) · [Inventory Management](https://docs.oracle.com/en/industries/hospitality/opera-cloud/21.5/ocsuh/c_opera_controls_inventory_management.htm) · [Waitlist](https://docs.oracle.com/cd/E98457_01/opera_5_6_core_help/waitlist_reservation_param.htm) · [Event waitlist](https://docs.oracle.com/en/industries/hospitality/opera-cloud/23.4/ocsuh/t_managing_event_waitlist.htm) · [Loyalty Cloud Service](https://docs.oracle.com/en/industries/hospitality/opera-cloud/24.3/ocsuh/c_about_loyalty_new.htm) · [Mobile PWA](https://docs.oracle.com/en/industries/hospitality/opera-cloud/25.5/ocsuh/c_overview_opera_cloud_mobile_app_pwa.htm) · [Digital Assistant](https://docs.oracle.com/en/industries/hospitality/opera-cloud/23.1/ocsuh/c_getting_started_opera_cloud_digital_assistant.htm) · [Datasheet PMS](https://oracle.com/a/ocom/docs/industries/hospitality/hosp-opera-cloud-property-manage-ds.pdf) · [Communiqué IA 16/06/2026](https://www.oracle.com/news/announcement/new-ai-capabilities-in-oracle-opera-cloud-supercharge-hotel-operations-2026-06-16/) · [OSEM tour](https://www.oracle.com/es/hospitality/products/opera-sales-event-management/tour) · [Simphony offline](https://docs.oracle.com/en/industries/food-beverage/simphony/19.3/sipou/c_workstation_online_offline_modes.htm) · [Contactless](https://www.oracle.com/hospitality/contactless/check-in) · [Stratégie Oracle Hospitality](https://www.oracle.com/a/ocom/docs/industries/hospitality/ohc-hotel-solution-strategy.pdf)

### 1.2 Mews
- **Positionnement :** « Operating System » hôtelier cloud, API-first, paiements embarqués ; n°1 HotelTechReport 2026 (4,7/5, 871 avis). 13 000 hôtels, 50+ pays.
- **Cible :** indépendants, boutiques, hostels, extended stay, groupes/chaînes (plans Portfolio/Brand) ; très fort en Europe.
- **Points forts vérifiés :** pas de night audit (bascule automatique à minuit, « editable history » configurable), availability blocks avec stratégies de release, surbooking par service/catégorie, Mews Kiosk (scan ID, signature, encodage clés, paiement, upsell early check-in), clé digitale Apple/Google Wallet native (serrures Assa Abloy), Mews Payments (tokenisation, pré-autorisations automatiques, VCC OTA automatisées, 40+ devises, réconciliation auto, gestion des chargebacks), housekeeping « powered by Flexkeeping » (maintenance, QA, lost & found), Smart Tips IA sur profils, Match & Merge, Guest Lifetime Value, tarification dynamique des extras, BI 10+ dashboards, exports planifiés, rapports d'urgence pour pannes. **Unfold 2026 :** Mews RMS natif, Channel Manager « powered by SiteMinder » (400+ OTA), Guest Messaging unifié (WhatsApp/SMS/OTA/email) avec Mews Agent IA, Automations en langage naturel, Accounts Receivable, Mews BI, pilote Uber facturé au folio.
- **Limites :** liste d'attente non native (partenaire Rezylist, non vérifié) ; fidélité via partenaires (Loyco…) ; mode hors-ligne explicitement refusé en roadmap ; POS non disponible en Amérique du Nord ; Mews Events uniquement en Europe.
- **Prix :** plans Core / Pro / Enterprise (+ Portfolio, Brand multi-propriété), facturés par chambre ou lit, non publiés ; frais de tokenisation unique ; paiements en interchange++. Estimations tierces : contrat médian ~6 600 $/an (costbench, « directionnel »), « à partir d'environ 200 $/mois » (blog concurrent) — **non vérifié**.
- **Sources :** [mews.com PMS](https://www.mews.com/en/products/property-management-system) · [Pricing](https://www.mews.com/en-gb/pricing-) · [Payments](https://www.mews.com/en/products/payments) · [Guest experience](https://www.mews.com/en/products/guest-experience) · [Kiosk](https://help.mews.com/s/article/what-are-mews-kiosks) · [Availability blocks](https://help.mews.com/s/article/Creating-availability-blocks-in-Mews) · [Overbooking](https://help.mews.com/s/article/How-to-configure-service-level-overbookings-in-Mews-Operations) · [Night audit](https://www.mews.com/en/blog/hotel-night-audit-automation) · [Emergency reports](https://help.mews.com/s/article/Emergency-reports) · [Police Espagne](https://help.mews.com/s/article/automate-police-reports-for-spain) · [Portfolio plan](https://help.mews.com/s/article/Understanding-the-Portfolio-pricing-plan) · [10 features](https://www.mews.com/en/blog/unmissable-new-mews-features-for-hoteliers) · [Unfold 2026](https://hospitality-on.com/en/digital/mews-unfold-2026-seven-launches-dissolve-hospitalitys-software-stack) · [Flexkeeping](https://flexkeeping.com/) · [Mews POS](https://www.mews.com/en/products/pos/hotel-restaurant) · [Waitlist request](https://feedback.mews.com/forums/955598-guest-experience/suggestions/46753447-automatic-wait-list-feature) · [Standalone refusé](https://feedback.mews.com/forums/918232-mews-operations-pms/suggestions/41937193-standalone-pms) · [Loyco](https://loyco.io/integration/mews-integration)

### 1.3 Cloudbeds
- **Positionnement :** plateforme unifiée PMS + channel manager + booking engine + paiements, forte en indépendants, hostels, B&B et groupes ; couche IA « Signals » (IA causale) et Cloudbeds Labs.
- **Cible :** indépendants et groupes 20-200 chambres ; 450+ intégrations marketplace, 300+ canaux.
- **Points forts vérifiés :** calendrier refondu (4 000+ chambres, 30 utilisateurs simultanés), Groups & Events (propositions, rooming lists avec liens publics, allotements), Spaces (salles, cabanas, à l'heure), night audit automatique configurable (2h00), paiements (Apple/Google Pay, Pay by Link, Tap to Pay, OXXO…), Guest Experience (inbox unifiée email/SMS/WhatsApp/OTA, chatbot IA, auto-traduction, check-in digital, upsell, réputation, clés via serrures), Police Report exportable, Cloudbeds Accounting (pistes d'audit, USALI, AR, API compta) et Insights (2026), Ask Signals (IA conversationnelle, aperçu), Engage (concierge vocal IA 5 langues), RMS natif annoncé (sept. 2026), POS natif en liste d'attente avec **mode hors-ligne** pour les flux clés, partenariat fidélité Journey (juin 2026).
- **Limites :** housekeeping basique (statuts, affectation, pas de maintenance/lost & found natifs documentés), pas de clé digitale native, Spaces non réservables en ligne pour l'instant, support critiqué dans des avis.
- **Prix :** plans Flex / One / Experience / Enterprise, sur devis ; estimations tierces : ~180 à 320 $/mois en base, 18-25 $/chambre « tout compris », paiements ~2,9 % + 0,30 $ — **non vérifié**. Pas d'essai gratuit standard.
- **Sources :** [cloudbeds.com PMS](https://www.cloudbeds.com/property-management-system/) · [Pricing](https://www.cloudbeds.com/property-management-system/pricing/) · [Guest Experience](https://www.cloudbeds.com/guest-engagement-software/) · [Housekeeping help](https://myfrontdesk.cloudbeds.com/hc//articles/25695101078427) · [Night audit](https://myfrontdesk.cloudbeds.com/hc/en-us/articles/31044721375643) · [Police Report](https://myfrontdesk.cloudbeds.com/hc//articles/217996298-Police-Report) · [Groups & Events](https://myfrontdesk.cloudbeds.com/hc/en-us/articles/45373855349019-Groups-and-Events-Everything-You-Need-to-Know) · [Spaces](https://myfrontdesk.cloudbeds.com/hc/en-us/articles/34435170665627) · [POS](https://www.cloudbeds.com/pos) · [Sécurité/PCI](https://myfrontdesk.cloudbeds.com/hc/en-us/articles/227167088-Cloudbeds-Security-Features-and-PCI-DSS-Certification) · [Cloudbeds Labs](https://www.cloudbeds.com/articles/cloudbeds-unveils-cloudbeds-labs) · [Spring Release 2026](https://hoteltechreport.com/news/cloudbeds-unveils-major-platform-upgrades-across-revenue-operations-data-intelligence-and-ai-capabilities) · [Journey loyalty](https://www.hotelmanagement.net/tech/cloudbeds-journey-partner-launch-loyalty-platform-independent-hotels) · [POS partners](https://www.hotelmanagement.net/tech/cloudbeds-adds-pos-integrations) · [Estimation prix](https://www.roommaster.com/blog/cloudbeds-pricing)

### 1.4 eZee Absolute → Yanolja Cloud Solution (YCS)
- **Positionnement :** suite cloud tout-en-un très diffusée dans les marchés émergents (Inde, Asie du Sud-Est, Afrique, Moyen-Orient) : PMS, channel manager (160+ canaux, GDS, metasearch), booking engine sans commission, POS restaurant, paiements (120+ moyens, PCI DSS niveau 1), site web, « AI Concierge ». 33 000+ hôtels, 170+ pays, 50+ langues, support 24/7. L'ancien **eZee FrontDesk** on-premise fonctionne en réseau local sans internet (licence perpétuelle).
- **Cible :** petits/moyens indépendants, chaînes régionales, resorts, hostels, appartements ; à partir de 10 chambres.
- **Points forts vérifiés :** check-in sur téléphone (upload ID, enregistrement, paiement), mode kiosque QR, day-use, express checkout, group blocks/allotements/rooming lists/split folios, commissions agences, night audit automatisé avec détection d'anomalies, rapports « owner-ready » par région, housekeeping (tâches, work orders, priorisation), AI Concierge sur WhatsApp/web/portail/téléphone avec bascule « approbation manuelle » globale, upsells temporisés, collecte d'avis au checkout (négatifs privés, positifs vers TripAdvisor/Google), POS avec **mode offline** (KOT, factures), stock par recette, commande QR en chambre, multi-propriété (langue/devise/formats légaux par établissement, profils dédoublonnés).
- **Limites :** événements/MICE non documentés sur le cloud (module banquet seulement sur FrontDesk on-prem) ; performance dépendante du débit (avis) ; add-ons jugés coûteux pour les petits (avis).
- **Prix :** plans Essential / Growth / Enterprise sur devis (remise annuelle 10 %) ; historiquement Capterra : 23,86 $ à 79,55 $/mois forfaitaires ; Techjockey (Inde) : 2 250 à 7 500 ₹/mois pour 1-15 chambres ; POS Optimus ~31,82 $/utilisateur/mois. Add-ons payants : site web, POS, Open API, marketplace.
- **Sources :** [YCS Hotel PMS](https://yanoljacloudsolution.com/platforms/hotel-pms) · [YCS accueil](https://yanoljacloudsolution.com/) · [YCS POS](https://yanoljacloudsolution.com/platforms/pos) · [Pricing eZee](https://www.ezeeabsolute.com/pricing.php) · [Capterra](https://www.capterra.com/p/135751/eZee-Absolute/) · [Techjockey](https://techjockey.com/detail/ezee-absolute) · [eZee FrontDesk](https://www.rfp.wiki/specialty-industries/hospitality-travel/ezee-frontdesk) · [eZee Optimus](https://www.getapp.com/restaurant-pos-software/a/ezee-optimus)

### 1.5 Hotelogix
- **Positionnement :** PMS cloud multi-propriété avec POS illimité, orienté marchés émergents (Inde, Philippines, Afrique, Amérique latine) ; support 24/7 très bien noté (4,8/5).
- **Cible :** petits et moyens indépendants (25-74 chambres majoritaires), groupes mid-market avec CRO.
- **Points forts vérifiés :** tape chart 2 ans, tarifs relationnels, pricing selon occupation, POS illimités (room service, split par type/quantité, resettlement), facturation directe/city ledger, commissions agences, app mobile (OCR pièces d'identité multi-pays, night audit depuis le smartphone, housekeeping), Guest Services App (pré-check-in, demandes, self check-out, feedback), Review Express (agrégation d'avis, sentiment), forecast 360 jours, intelligence tarifaire concurrents, 100+ rapports groupe, intégrations compta (Xero, Tally, SAP, NetSuite), sécurité (ISO 27001, MFA, RBAC avec audit trail). **IA (mai 2025) :** enchères metasearch, forecast 365 j, analytics en langage naturel, campagnes WhatsApp, upsell personnalisé ; « agentic AI » en préparation.
- **Limites :** réactivité mobile et rapports critiqués ; pas de mode offline ; MICE non documenté ; channel manager via partenaires (STAAH, RateGain, SiteMinder…).
- **Prix :** Premium / Premium Plus / Platinum, sur devis ; estimations tierces ~7,99 / 11,99 / 17,99 $/chambre/mois avec minimums ; add-ons Distribution (~1 $/ch), Accounts ; dépôt GDS 500 $ ; essai 15 jours. **Non vérifié.**
- **Sources :** [Datasheet](https://www.hotelogix.com/documents/datasheet/hotelogix-pms.pdf) · [Pricing](https://www.hotelogix.com/independent-property-pricing) · [Entreprise HLXE](https://www.hotelogix.com/property-management-system-large-hotels-hlxe) · [Multi-propriété FAQ](https://www.hotelogix.com/faq-menu/multi-property-hotel-groups-cro-crs-systems) · [POS](https://hotelogix.com/point-of-sale-system) · [Guest Services App](https://hotelogix.com/guest-services-app) · [App mobile](https://apps.apple.com/app/id1194551150) · [IA](https://www.hotelogix.com/ai-in-hospitality) · [Communiqué IA mai 2025](https://www.hospitalitynet.org/news/4127052.html) · [HotelTechReport](https://mail.hoteltechreport.com/operations/property-management-systems/hotelogix) · [rfp.wiki](https://www.rfp.wiki/vendors/hotelogix)

### 1.6 Little Hotelier (SiteMinder)
- **Positionnement :** tout-en-un pour très petites structures (1-49 chambres : 1 600 des 1 800 avis), adossé à la distribution SiteMinder (450+ canaux) ; HT Score 96, 4,6/5.
- **Cible :** B&B, guesthouses, motels, pubs, campings, petits hôtels.
- **Points forts vérifiés :** calendrier unifié, statut des chambres + notes + rapports housekeeping, check-in en ligne (heure d'arrivée, données), inbox unifiée email/SMS/WhatsApp/Airbnb/Booking.com, messages automatisés pré/post séjour, annuaire digital QR, enquêtes de satisfaction routées vers les sites d'avis, paiements (Apple/Google Pay, dépôts, remboursements), metasearch Google, Website Builder, Dynamic Revenue Plus (recommandations quotidiennes, concurrents, événements locaux, automatisation), Insights, app mobile (check-in/out, paiements, fermetures). Côté SiteMinder 2025-2026 : traduction IA du moteur, résumés IA Insights, Paystack (mobile money au Kenya/Nigeria/Ghana/Afrique du Sud — applicabilité à Little Hotelier **non vérifiée**).
- **Limites :** pas de POS ni d'intégration F&B (avis), pas de groupes/MICE documentés, housekeeping limité (pas d'affectation), rapports basiques, GDS non vérifié, pas de clé digitale/kiosque natifs.
- **Prix :** Basics (~29-39 $/mois + 1 % de frais sur réservations ; Payments, Metasearch, Channels Plus en add-ons) / Pro (~109 $/mois pour une petite structure, selon nb de chambres, inclut Payments, Metasearch, Insights, veille concurrentielle) ; Website Builder, Guest Engagement, Dynamic Revenue Plus en add-ons ; essai 30 jours, sans engagement.
- **Sources :** [Features](https://www.littlehotelier.com/features/) · [Pricing](https://www.littlehotelier.com/pricing/) · [PMS/front desk](https://www.littlehotelier.com/property-management-system/) · [Guest Engagement](https://www.littlehotelier.com/guest-engagement/) · [Dynamic Revenue Plus](https://www.littlehotelier.com/dynamic-revenue-plus/) · [HotelTechReport](https://hoteltechreport.com/operations/property-management-systems/little-hotelier) · [Capterra](https://www.capterra.com/p/144307/Little-Hotelier/) · [App iOS](https://apps.apple.com/us/app/-/id1130899763) · [SiteMinder release hub](https://www.siteminder.com/product-release-hub/) · [SiteMinder IA distribution](https://www.traveldailynews.com/technology/siteminder-expands-hotel-distribution-into-the-ai-era/) · [Paystack](https://help-classic.siteminder.com/en/articles/8693061-set-up-paystack-in-your-booking-engine)

### 1.7 Clock PMS+ (Clock Software)
- **Positionnement :** PMS cloud « tout inclus » (AWS) avec événements, POS restaurant, kiosque, portail invité, activités ; 1 500+ hôtels indépendants, 50+ pays, 4,7/5 (329 avis HTR).
- **Cible :** boutiques, hôtels d'événements, resorts, groupes/chaînes, hostels (10-99 chambres majoritaires) ; fort en Europe.
- **Points forts vérifiés :** tarifs dérivés/adaptés à l'occupation, restrictions, blocks groupes avec pickup/release/codes, routage charges groupes/sociétés, commissions TO automatiques, housekeeping complet (tâches par zone/équipe, types de nettoyage, espaces communs, minibar, **lost & found avec photos**, tickets maintenance auto, prévision de charge), Events (diary live, layouts, BEO/function sheets live, pipeline, signature et acompte en ligne, templates, répartition des charges), POS (plans de table, KDS/imprimantes, room charge avec signature, QR ordering, split, pourboires), check-in en ligne + Clock Kiosk (encodage clés, ID, paiement, upgrades par attribut), clés digitales (PIN, lien, Wallet « où supporté »), portail MyBooking (facture, late checkout, taxi, avis, adhésion), messagerie email automatisée multilingue, multi-propriété (réservation centrale, profils partagés, dashboards par région), localisations/fiscalisations (Italie, cantons suisses, 13 fiscalisations), copies d'ID chiffrées à suppression automatique.
- **Limites :** aucune fonctionnalité IA native identifiée ; WhatsApp/SMS via intégrations (Quicktext, Whistle, HotBot) ; templates de tarifs centraux « planifiés » ; stock F&B via tiers ; rapports et interface jugés datés (avis).
- **Prix :** tarif unique tout inclus selon CA annuel et chambres ; exemple publié : 40 chambres / 1,9 M€ de CA → 517 €/mois (~13 €/ch) ; Capterra « à partir de 100 $/mois » ; add-ons : canaux OTA via RoomCloud 10 €/canal/mois (Booking.com direct gratuit), mappings tarifaires, analytics privés 50 €/mois ; engagement 12 mois ; frais d'onboarding.
- **Sources :** [clock-software.com](https://www.clock-software.com/) · [Pricing](https://www.clock-software.com/pricing) · [PMS](https://www.clock-software.com/products/pms) · [Housekeeping](https://www.clock-software.com/products/housekeeping) · [Events](https://www.clock-software.com/products/events) · [POS](https://www.clock-software.com/products/restaurant-pos) · [Check-in & kiosk](https://www.clock-software.com/products/online-check-in-kiosk) · [Kiosk fonctionnel](https://support.clock-software.com/en/support/solutions/articles/9000218646) · [Guest messaging](https://www.clock-software.com/products/guest-messaging) · [Groupes & chaînes](https://www.clock-software.com/who-its-for/hotel-groups-chains) · [Localisations](https://academy.clock-software.com/en/support/solutions/9000117639) · [HotelTechReport](https://www.hoteltechreport.com/operations/property-management-systems/clock-pms-suite) · [Capterra](https://www.capterra.com/p/132161/Clock-PMS/)

### 1.8 RoomRaccoon
- **Positionnement :** HMS tout-en-un orienté automatisation pour indépendants (PMS + channel manager 200+ + booking engine + RaccoonPay) ; 4,7/5 (207 avis HTR), fort en Europe (NL, DE, PT, UK, ZA).
- **Cible :** 1-24 chambres majoritaires (378 des 512 profils), boutiques, B&B, lodges, pubs.
- **Points forts vérifiés :** calendrier drag & drop, online check-in/out, RaccoonID (scan ID), RaccoonUpsell (menu digital), RaccoonHousekeeping (Smart Tasks récurrentes, vue mobile, inspections, forecast), Room Allotment (groupes avec auto-attribution par les membres), surbooking via « chambres de surbooking », clôture journalière verrouillante, paiements (liens, VCC monitorées et débitées automatiquement, RaccoonCardMachine), RaccoonRev (règles dynamiques, concurrents) et RaccoonRev Plus (IA, météo, 90 j, co-pilote), WhiteLabel, RaccoonSite, conformité locale forte (SIBA Portugal auto, INE, SAF-T/ATCUD, DSFinV-K Allemagne, Peppol, Fina, INSEE), multi-propriété, Integrations Hub 300+ (Lightspeed room charge, Salto, RemoteLock, Roommatik kiosque, Akia/HiJiffy messagerie).
- **Limites :** pas de messagerie bidirectionnelle WhatsApp/SMS native, pas de POS/MICE natifs, pas de kiosque/clé natifs, pas d'app mobile dédiée (avis), jugé « basique pour les grands hôtels ».
- **Prix publiés (USD/mois, −20 % annuel) :** Entry 236 $ (2 users, 3 canaux, 7 règles) / Essentials 300 $ / Premium 441 $ (allotements, rapports avancés, 25 règles) / Pro 620 $ (illimité, RaccoonRev Plus, 75 règles). Frais de transaction et terminal en sus.
- **Sources :** [roomraccoon.com](https://roomraccoon.com) · [Pricing](https://roomraccoon.com/pricing/) · [HotelTechReport](https://mail.hoteltechreport.com/operations/property-management-systems/roomraccoon-pms) · [RaccoonHousekeeping](https://hoteltechreport.com/news/roomraccoon-hsk-software) · [RaccoonRev Plus](https://www.traveldailynews.com/technology/roomraccoon-introduces-raccoonrev-plus/) · [Surbooking](https://contact.roomraccoon.com/en/support/solutions/articles/150000012456-how-to-overbook-rooms) · [Clôture journalière](https://contact.roomraccoon.com/en/support/solutions/articles/150000175711-closing-daily-revenue-faqs) · [Conformité Portugal](https://contact.roomraccoon.com/en/support/solutions/articles/150000208070-compliance-overview-for-portugal) · [Room Allotment](https://hoteltechreport.com/nl/news/roomraccoon-group-booking-solution) · [Roommatik](https://roomraccoon.com/?p=233056) · [Lightspeed](https://www.lightspeedhq.com/uk/integrations/roomraccoon/) · [Akia](https://hoteltechreport.com/news/roomraccoon-akia-integration)

### 1.9 protel / Planet (Protel Cloud PMS, ex-protel Air)
- **Positionnement :** PMS historique allemand (on-premise et cloud) racheté par Planet (paiements) ; suite « logiciel + paiements + réseau ». 1 000+ marques, 100+ pays ; marketplace protel.io 1 100-1 200 intégrations.
- **Cible :** boutiques, hôtels de centre-ville et luxe 25-199 chambres, groupes (Planet Central / MPE), surtout Europe (DE/AT) et Afrique du Sud.
- **Points forts vérifiés :** Navigator/room plan, groupes (20+ réservations), module MICE/banquet intégré (salles, services, ordres de service, lettres de confirmation ; Conference & Event Management System), housekeeping app (statuts, maintenance, minibar, lost & found, Hub OS), protel Voyager (app invité : profil, services, facture), quick/web check-in, cartes d'enregistrement digitales + scan ID, Messenger (emails automatisés, anniversaires), paiements Planet (pré-autorisations, augmentation auto, débit no-show, Token Vault, Pay-By-Link, DCC, Multi-Currency Pricing), centaines de rapports, Planet POS / paiements F&B, cartes cadeaux, RMS via intégration, option **On-Premise**.
- **Limites (avis HTR, note 4,0, HT Score 31) :** support dégradé après rachat, bugs, protel Air jugé adapté aux « configurations simples mono-site », pas d'IA native, pas d'app mobile dédiée (FAQ tierce), pas de clé/check-in mobile natifs (selon Mews, biaisé).
- **Prix :** sur devis ; estimation tierce 300-1 200 $/mois — **non vérifié**.
- **Sources :** [HotelTechReport protel](https://mail.hoteltechreport.com/operations/property-management-systems/protel-pms) · [Planet hospitality](https://www.weareplanet.com/hospitality) · [Planet hotel PMS](https://www.weareplanet.com/hotel-pms) · [Welcome protel](https://www.weareplanet.com/welcome-protel) · [Serinf protel Cloud](https://serinf.it/en/software-hospitality/property-management-system/protel-cloud) · [Bit-soft protel](https://bit-soft.ro/en/protel) · [softwarefinder](https://softwarefinder.com/property-management-software/protel-pms) · [Mews vs protel (biaisé)](https://www.mews.com/en/compare/mews-vs-protel)

### 1.10 Guestline (Access Hospitality) — Rezlynx PMS
- **Positionnement :** suite cloud UK/Irlande (PMS Rezlynx, Standard/Advanced C&B, GuestStay, GuestPay, EPoS/Newbridge, Distribution Hub 400+ canaux/2 000 partenaires, Direct Booking Manager, GuestVoucher, Insights), intégrée à Access Evo (couche IA du groupe Access, avec SHR et STAAH). 3 500+ hôteliers.
- **Cible :** indépendants et groupes 25-199 chambres, pubs avec chambres, UK/IE/DACH/Benelux.
- **Points forts vérifiés :** multi-chambres/groupes/room blocks, surbooking configurable, dépôts/facturation/aged debtors, VAT, Design Query (rapports), housekeeping (statuts, sections, cleaning schedules, maintenance, **lost property**), C&B (function diary, layouts, function sheets, proforma, paylinks, upsells ; Advanced C&B payant pour délégués/menus), GuestStay Core/Plus (enregistrement digital, pré-paiement, kiosque, upsells/upgrades, check-out digital, Wallet passes Apple/Google, réservation de table ResDiary, analyse IA des demandes), GuestPay (Trust/Adyen, paylinks, pré-autorisation, tokenisation), EPoS (plans de table, messages cuisine, stock, X/Z vers Rezlynx), RMS IA « powered by SHR » (fév. 2025), Evo Copilot (questions en langage naturel), Evo Feed (alertes), devis groupes automatisés avec analyse de déplacement (juin 2026), moteur de réservation « agentique » (SHR), RGPD (suppression automatique de profils).
- **Limites :** interface anglaise, conformité fiscale continentale limitée (selon Mews, biaisé), rapports financiers critiqués, courbe d'apprentissage ; prix jugé prohibitif pour les petits hôtels (avis Capterra).
- **Prix :** sur devis ; Capterra affiche « 250 $/utilisateur/mois » (**douteux, non vérifié**) ; module Advanced C&B facturé en supplément.
- **Sources :** [Access – Guestline](https://www.theaccessgroup.com/en-gb/our-brands/guestline/) · [Help centre](https://help-guestline.theaccessgroup.com/en/) · [Rezlynx collections](https://help-guestline.theaccessgroup.com/en/collections/16346244-guestline-pms-rezlynx) · [Room & Housekeeping](https://help-guestline.theaccessgroup.com/en/collections/18176865) · [Standard C&B](https://help-guestline.theaccessgroup.com/en/articles/13116515-guestline-pms-standard-c-b-overview) · [GuestStay plans](https://help-guestline.theaccessgroup.com/en/articles/13116803-guestline-gueststay-gueststay-plans-overview) · [GuestStay collection](https://help-guestline.theaccessgroup.com/en/collections/16346303-gueststay) · [EPoS](https://help-guestline.theaccessgroup.com/en/collections/16346277-guestline-epos) · [Distribution Hub](https://www.hospitalitynet.org/news/4122028.html) · [RMS IA](https://www.hospitalitynet.org/news/4126049.html) · [Access Evo IA](https://en.10minhotel.com/2026/06/15/access-hospitality-launches-access-evo-an-ai-intelligence-layer-for-hotels/) · [Booking engine agentique](https://www.traveldailynews.com/hospitality/access-hospitality-launches-first-agentic-ai-powered-interactive-booking-engine/) · [HotelTechReport](https://mail.hoteltechreport.com/operations/property-management-systems/rezlynx) · [Capterra](https://www.capterra.com/p/105192/Rezlynx/) · [Independent Hotel Show](https://independenthotelshow.co.uk/exhibitors/guestline-ltd)

---

## 2. Matrice consolidée

Colonnes : OPE = OPERA Cloud, MEW = Mews, CLB = Cloudbeds, EZE = eZee/YCS, HLX = Hotelogix, LH = Little Hotelier, CLK = Clock, RR = RoomRaccoon, PRO = protel/Planet, GL = Guestline.
Classification sur le nombre d'éditeurs disposant de la fonction (● + ◐) : **Standard** ≥ 7 · **Différenciante** 2-6 · **Rare** 1. Quand le natif est nettement plus rare que la disponibilité via partenaires, c'est précisé.

### 2.1 Front office
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Planning/tape chart drag & drop | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Plans tarifaires multiples, tarifs dérivés, packages | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Groupes : blocks, rooming list, facturation maître | ● | ● | ● | ● | ◐ | ◐ | ● | ● | ● | ● | 10 | Standard |
| Allotements agences/TO avec dates de release | ● | ● | ● | ● | ○ | ○ | ● | ● | ○ | ● | 7 | Standard |
| Liste d'attente (waitlist) réservations | ● | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | 2 | **Rare en natif** (1) |
| Surbooking contrôlé (sell limits par type/date) | ● | ● | ○ | ○ | ◐ | ○ | ○ | ● | ○ | ● | 5 | Différenciante |
| Day use / horaire / long séjour | ● | ● | ◐ | ● | ● | ◐ | ◐ | ○ | ○ | ◐ | 8 | Standard (profondeur variable) |
| Profils société/agence, tarifs négociés, commissions | ● | ● | ● | ● | ● | ○ | ● | ◐ | ◐ | ● | 9 | Standard |
| Multi-folios, routage des charges, split | ● | ● | ● | ● | ● | ○ | ● | ◐ | ● | ● | 9 | Standard |
| Clôture journalière / night audit (auto ou manuel) | ● | ● auto | ● auto | ● auto | ● | ○ | ◐ | ● | ◐ | ◐ | 9 | Standard |
| Comptes débiteurs / city ledger / balance âgée | ● | ● | ● | ● | ● | ○ | ● | ○ | ◐ | ● | 8 | Standard |
| Cartes d'enregistrement digitales / e-signature | ● | ● | ● | ● | ◐ | ◐ | ● | ● | ● | ● | 10 | Standard |

### 2.2 Parcours client
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Check-in en ligne / pré-enregistrement mobile | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Check-out digital / express avec facture | ● | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ● | 10 | Standard |
| Borne/kiosque self check-in | ◐ | ● | ◐ | ● | ○ | ○ | ● | ◐ | ◐ | ● | 8 | Standard (natif : 4 → différenciante) |
| Clé digitale / mobile key | ◐ | ● Wallet | ◐ | ○ | ◐ | ○ | ● | ◐ | ○ | ◐ | 7 | Standard via serrures ; **natif rare (2)** |
| Scan pièce d'identité / OCR | ◐ | ● | ◐ | ◐ | ● | ○ | ● | ● | ● | ○ | 8 | Standard |
| Messagerie invités unifiée (email/SMS/WhatsApp/OTA) | ◐ | ● | ● | ● | ● | ● | ◐ email | ◐ | ◐ | ◐ | 10 | Standard ; **WhatsApp natif : 5 (différenciante)** |
| Upsell automatisé (upgrades, early/late, extras) | ● Nor1 | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | 10 | Standard |
| Portail invité / app (séjour, facture, demandes) | ◐ | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ● | 10 | Standard |
| Commande room service / QR depuis la chambre | ◐ | ○ | ● | ● | ● | ○ | ● | ◐ | ◐ | ◐ | 8 | Standard |

### 2.3 Housekeeping & maintenance
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Statut chambres temps réel (sale/propre/inspectée) | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Affectation automatique des tâches / feuilles de travail | ● | ● | ◐ | ● | ● | ○ | ● | ● | ● | ● | 9 | Standard |
| App mobile housekeeping | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ◐ | 10 | Standard |
| Tickets maintenance / work orders | ● | ● | ◐ | ● | ○ | ◐ | ● | ● | ● | ● | 9 | Standard |
| Hors service (OOO/OOS) avec impact inventaire | ● | ◐ | ◐ | ○ | ○ | ◐ | ○ | ◐ | ○ | ● | 6 | Différenciante |
| Minibar / postes depuis l'app HK | ● | ◐ | ○ | ◐ | ◐ | ○ | ● | ○ | ● | ○ | 6 | Différenciante |
| Objets trouvés (lost & found) | ○ | ◐ | ○ | ○ | ○ | ○ | ● photos | ○ | ● | ● | 4 | Différenciante |
| Prévision de charge HK / inspections / temps de nettoyage | ● | ● | ◐ | ○ | ○ | ○ | ● | ● | ○ | ○ | 5 | Différenciante |

### 2.4 Distribution
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Channel manager intégré (natif ou embarqué) | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ◐ | ● | 10 | Standard |
| OTA bidirectionnel Booking.com/Expedia | ● | ● | ● | ● | ◐ | ● | ● | ● | ◐ | ● | 10 | Standard |
| Moteur de réservation direct sans commission | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Metasearch (Google Hotel Ads, Trivago…) | ● | ◐ | ● | ● | ● | ● | ○ | ● | ○ | ● | 8 | Standard |
| GDS | ● | ◐ | ● | ● | ● | ○ | ● | ● | ● | ○ | 8 | Standard |
| Constructeur de site web | ○ | ○ | ● | ● | ○ | ● | ○ | ● | ○ | ● | 5 | Différenciante |
| Moteur groupes / liens de réservation groupe | ● | ● | ● | ○ | ○ | ◐ | ● | ● | ○ | ○ | 6 | Différenciante |

### 2.5 Revenue management
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tarification dynamique / règles d'occupation | ● | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | 10 | Standard |
| Restrictions (MinLOS, CTA/CTD, stop sell) | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ◐ | ● | 10 | Standard |
| Rapports RevPAR/ADR/occupation, pace, pickup | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| RMS natif avec prévision de demande IA | ◐ | ● 730 j | ● 180 j | ◐ | ● 365 j | ◐ 90 j | ○ | ● 90 j | ○ | ● | 8 | Standard (natif profond : 5 → différenciante) |
| Veille tarifaire concurrents (rate shopper) | ◐ | ◐ | ◐ | ◐ | ● | ● | ○ | ● | ○ | ◐ | 8 | Standard (surtout via partenaires) |
| Tarification dynamique des extras/add-ons | ○ | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | 1 | **Rare** |

### 2.6 F&B / POS
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| POS restaurant/bar du même éditeur | ● Simphony | ● | ◐ liste d'attente | ● | ● | ○ | ● | ◐ partenaires | ◐ | ● | 9 | Standard |
| Room charge (POS → folio) | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ● | 9 | Standard |
| Plan de salle / gestion des tables | ● | ● | ● | ● | ◐ | ○ | ● | ◐ | ◐ | ● | 9 | Standard |
| Écran cuisine / KOT | ● | ◐ | ○ | ● | ● | ○ | ● | ◐ | ○ | ◐ | 7 | Standard |
| Commande QR à table / en chambre | ◐ | ○ | ● | ● | ● | ○ | ● | ◐ | ◐ | ◐ | 8 | Standard |
| Stock F&B par recette | ● | ○ | ○ | ● | ● | ○ | ◐ tiers | ○ | ○ | ● | 5 | Différenciante |
| POS en mode hors-ligne | ● | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ | ○ | 3 | Différenciante |

### 2.7 Événements / MICE
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Salles/espaces réservables (diary, layouts, à l'heure) | ● | ● Europe | ● 2026 | ◐ | ○ | ○ | ● | ◐ | ● | ● | 8 | Standard (profondeur variable) |
| BEO / fiches de fonction | ● | ◐ | ○ | ○ | ○ | ○ | ● | ○ | ● | ● | 5 | Différenciante |
| Devis/propositions groupes, pipeline, signature en ligne | ● | ● | ● | ○ | ○ | ○ | ● | ○ | ● | ● | 6 | Différenciante |
| Menus/catering avec facturation événement | ● | ◐ | ○ | ○ | ○ | ○ | ● | ○ | ● | ● Advanced | 5 | Différenciante |

### 2.8 Spa / activités / ressources
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Réservation d'activités/ressources (spa, parking, vélos, cabanas) | ◐ | ● | ● Spaces | ◐ | ◐ | ◐ | ● | ● extras | ○ | ◐ | 9 | Standard via extras ; **module natif : 4 (différenciante)** |

### 2.9 Paiements
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Paiements intégrés (acquiring de l'éditeur / terminaux) | ● | ● | ● | ● 7 pays | ◐ gateways | ● | ● Adyen | ● | ● | ● | 10 | Standard |
| Tokenisation / coffre de cartes | ● | ● | ● | ◐ | ○ | ◐ | ● | ◐ | ● | ● | 9 | Standard |
| Pré-autorisation automatique (garantie, no-show) | ● | ● | ◐ | ○ | ○ | ○ | ● | ◐ | ● | ● | 7 | Standard (limite) |
| Liens de paiement (pay-by-link) | ◐ | ◐ | ● | ● | ○ | ● | ◐ | ● | ● | ● | 9 | Standard |
| Acomptes/dépôts automatisés selon politique | ● | ● | ● | ◐ | ◐ | ● | ● | ● | ● | ● | 10 | Standard |
| Multi-devises / DCC | ● | ● | ◐ | ● | ◐ | ◐ | ● | ○ | ● DCC | ◐ | 9 | Standard |
| Cartes virtuelles OTA (VCC) automatisées | ○ | ● | ○ | ○ | ○ | ◐ autopay | ○ | ● | ○ | ○ | 3 | Différenciante |
| Mobile money / moyens africains | ◐ Pesapal | ○ | ◐ régional | ◐ | ○ | ◐ Paystack (SiteMinder) | ○ | ○ | ○ | ○ | 4 ◐ | Différenciante — **aucun natif vérifié** |

### 2.10 CRM & fidélité
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Profils unifiés, dédoublonnage, historique | ● | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ● | 10 | Standard |
| Segmentation (codes marché/source/canal) | ● | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ● | 10 | Standard |
| Campagnes email/WhatsApp automatisées (marketing) | ◐ | ◐ | ● | ◐ | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Gestion des avis / réputation | ◐ | ◐ | ● | ● | ● | ● | ◐ | ◐ | ○ | ◐ | 9 | Standard (natif : 4) |
| Programme de fidélité (points/paliers) | ● add-on | ◐ | ◐ Journey | ◐ | ◐ | ○ | ◐ | ○ | ○ | ◐ | 7 | Standard via partenaires ; **natif rare (1)** |
| Bons cadeaux / vouchers | ○ | ● | ◐ | ○ | ○ | ○ | ◐ | ○ | ● | ● | 5 | Différenciante |
| Enrichissement IA du profil (Smart Tips, LTV) | ○ | ● | ◐ | ○ | ◐ | ○ | ○ | ○ | ○ | ○ | 3 | Différenciante |

### 2.11 Reporting / BI
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dashboard KPI temps réel (flash manager) | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Prévision d'occupation | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ● | 10 | Standard |
| Rapports personnalisables / BI self-service | ● | ● | ● | ◐ | ◐ | ○ | ● | ◐ | ● | ● | 9 | Standard |
| Exports/rapports planifiés automatiques | ● | ● | ◐ | ◐ | ○ | ○ | ◐ | ○ | ◐ | ○ | 6 | Différenciante |
| Rapports propriétaire / benchmarking multi-sites | ● | ● | ● | ● | ● | ○ | ● | ◐ | ● | ● | 9 | Standard |
| IA conversationnelle sur les données | ● | ● | ● aperçu | ○ | ● | ◐ | ○ | ○ | ○ | ● Copilot | 6 | Différenciante |

### 2.12 Multi-propriété
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Multi-établissements (profils partagés, rôles, consolidation) | ● | ● | ● | ● | ● | ◐ | ● | ● | ● | ◐ | 10 | Standard |
| Bureau central de réservations cross-property | ● | ◐ | ◐ | ◐ | ● | ○ | ● | ○ | ● | ◐ | 8 | Standard (profondeur variable) |
| Tarifs/produits centralisés en masse | ● | ● | ● | ● | ● | ○ | ◐ planifié | ○ | ◐ | ○ | 7 | Standard |

### 2.13 Intégrations / API
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| API ouverte documentée | ● | ● | ● | ● payant | ● | ◐ | ● | ● | ● | ● | 10 | Standard |
| Marketplace d'apps (ordre de grandeur) | ● ~5 000 | ● 1 000+ | ● 450+ | ● 650+ | ◐ 100+ | ● | ● | ● 300+ | ● 1 100+ | ● 2 000 partenaires | 10 | Standard |
| Export/intégration comptable (Xero, QuickBooks, ERP) | ● | ● | ● API | ◐ | ● | ◐ | ◐ | ● | ● | ● | 10 | Standard |
| Interfaces serrures / PBX / Wi-Fi | ● | ● | ● | ◐ | ● | ○ | ● | ● | ● | ◐ | 9 | Standard |

### 2.14 Sécurité & conformité
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PCI DSS (revendiqué) | ● | ● | ● | ● L1 | ● | ● | ● | ● | ● | ● | 10 | Standard |
| Outils RGPD (anonymisation, suppression auto, consentement) | ● | ● | ● | ◐ | ◐ | ◐ | ● | ◐ | ● | ● | 10 | Standard |
| Journal d'audit / traçabilité par utilisateur | ● | ● | ● | ● | ● | ○ | ● | ○ | ◐ | ◐ | 8 | Standard |
| Déclarations police / registre étrangers / fiscalisation locale | ● 200+ pays | ● ES/PT/CH | ● export | ◐ | ○ | ○ | ● IT/CH | ● PT/DE/BE/HR/FR | ◐ | ◐ | 8 | Standard (profondeur très variable) |
| Authentification forte (MFA/SSO/passkeys) | ● | ● passkeys | ◐ | ◐ | ● | ◐ | ○ | ○ | ○ | ● SSO | 7 | Standard (limite) |

### 2.15 Hors-ligne / faible connectivité
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Continuité PMS hors-ligne / option on-premise | ○ | ◐ rapports d'urgence | ○ | ● FrontDesk LAN | ○ | ◐ vague | ○ | ○ | ● On-Premise | ○ | 4 | Différenciante — **PMS cloud hors-ligne : aucun** |
| POS hors-ligne avec resynchronisation | ● | ○ | ● | ● | ○ | ○ | ○ | ○ | ○ | ○ | 3 | Différenciante |

### 2.16 IA & automatisation
| Fonctionnalité | OPE | MEW | CLB | EZE | HLX | LH | CLK | RR | PRO | GL | Total | Classement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Assistant IA pour le staff (aide, affectation, analyses) | ● | ● | ● | ◐ | ● | ◐ | ○ | ○ | ○ | ● | 7 | Standard (limite, 2025-2026) |
| Agent IA invité (chat/voix, WhatsApp) natif | ○ | ● | ● voix | ● | ◐ | ○ | ○ | ◐ | ○ | ◐ | 7 | Standard via partenaires ; natif : 3 |
| Workflows/automations no-code ou langage naturel | ◐ règles | ● | ◐ | ● agents | ◐ | ◐ | ● séquences | ◐ Smart Tasks | ◐ | ◐ | 10 | Standard (vrai builder : 3) |
| Traduction IA (contenus, messages) | ● | ◐ | ● | ● | ● | ◐ | ◐ multilingue | ○ | ○ | ● | 8 | Standard |

---

## 3. Les 15 fonctionnalités les plus constamment présentes chez les leaders

Présentes nativement chez 9 ou 10 éditeurs sur 10 — c'est le « socle minimum » attendu par le marché en 2026 :

1. **Planning visuel drag & drop** avec recherche universelle, notes et rappels.
2. **Plans tarifaires multiples, tarifs dérivés et packages** (pension, extras inclus).
3. **Groupes et allotements** : blocks avec dates de release, rooming list importable, facture maître/routage.
4. **Multi-folios, routage et split des charges** (chambre, société, agence, événement) + comptes débiteurs.
5. **Clôture journalière automatisée** (ou suppression du night audit avec historique modifiable).
6. **Check-in en ligne / pré-enregistrement** avec carte d'enregistrement digitale, e-signature et capture d'ID.
7. **Check-out digital/express** avec facture envoyée automatiquement.
8. **Housekeeping temps réel sur mobile** : statuts, affectation automatique des tâches, tickets de maintenance.
9. **Channel manager bidirectionnel** (Booking.com, Expedia, Agoda, Airbnb) + metasearch + GDS.
10. **Moteur de réservation direct sans commission**, mobile-first, avec extras/upsells.
11. **Tarification dynamique par règles + restrictions** (MinLOS, CTA/CTD, stop sell), recommandations tarifaires.
12. **Paiements intégrés** : tokenisation, acomptes automatisés, liens de paiement, terminaux, multi-devises.
13. **Profils invités unifiés** (dédoublonnage, historique, segmentation marché/source) et communications automatisées pré/post séjour.
14. **Upsell automatisé** (upgrades, early check-in/late check-out, extras) tout au long du parcours.
15. **Reporting** : dashboard KPI temps réel (occupation, ADR, RevPAR, pace), prévision d'occupation, rapports personnalisables ; **API ouverte + marketplace + export comptable** ; PCI/RGPD avec journal d'audit.

Juste en dessous (8-9/10) : POS du même éditeur avec room charge et plan de salle, messagerie invités unifiée, portail invité, multi-propriété, scan d'ID, déclarations légales locales.

---

## 4. Les 10 fonctionnalités les plus innovantes / émergentes (2025-2026)

1. **Assistants IA embarqués pour le staff** — OPERA Cloud Assistant (juin 2026 : affectation de chambre assistée, descriptions de tarifs générées, traduction, aide contextuelle, sans surcoût), Guestline Evo Copilot, Cloudbeds « Ask Signals », Hotelogix analytics en langage naturel, Mews Smart Tips et résumés IA.
2. **Agents IA invités omnicanaux** — Mews Agent dans l'inbox unifiée WhatsApp/SMS/OTA/email (Unfold 2026), Cloudbeds Engage (concierge vocal 5 langues, réservations par téléphone), YCS AI Concierge sur WhatsApp/web/téléphone avec bascule d'approbation manuelle, Hotelogix campagnes WhatsApp IA.
3. **RMS natif à prévision longue et IA causale** — Cloudbeds Signals (180 j, 96 % revendiqués), Mews RMS (150 M calculs/jour, 730 j), RaccoonRev Plus (météo, pace, 90 j, mode co-pilote puis autopilote), Guestline RMS « powered by SHR », Hotelogix 365 j.
4. **Distribution via les plateformes d'IA (MCP)** — SiteMinder Demand Plus vers ChatGPT/Claude via DirectBooker, Channels Plus pour OTA « AI-enabled », moteur de réservation « agentique » conversationnel d'Access/SHR (voix, multi-propriété, vouchers).
5. **Clés digitales sans application via Apple/Google Wallet** — Mews (natif, Assa Abloy), Clock (Wallet passes, PIN), Guestline GuestStay (Wallet passes) ; plus passkeys/biométrie pour la connexion du staff (Mews, SiteMinder).
6. **Automations no-code / en langage naturel** — Mews Automations (upgrade des clients fidèles, amenities, routage de tâches décrits en texte), YCS « AI agents » par département, Access Evo devis groupes automatisés avec analyse de déplacement (juin 2026), RoomRaccoon Smart Tasks récurrentes.
7. **Paiements embarqués « intelligents »** — pré-autorisations automatiques avant arrivée, automatisation des cartes virtuelles OTA (activation, fenêtre de débit), tarification dynamique des extras (Mews), DCC/Multi-Currency Pricing et Token Vault (Planet), Pay-by-link et Tap to Pay (Cloudbeds), réconciliation et gestion des litiges automatisées (Mews).
8. **POS hôtelier natif avec mode hors-ligne et commande QR** — Cloudbeds POS (offline sur les flux clés, QR menus, multi-outlets), YCS POS (KOT et facturation sans internet, stock par recette), Clock POS (QR en chambre/à table, signature digitale du room charge), Mews POS (mobile-first, pourboires digitaux).
9. **Comptabilité et facturation B2B intégrées au PMS** — Cloudbeds Accounting (pistes d'audit, USALI, AR, API comptable, 2026), Mews Accounts Receivable (invoice-to-cash 100 % réconcilié), fiscalisations locales natives (Clock 13 pays, RoomRaccoon SAF-T/ATCUD/DSFinV-K/Peppol/SIBA automatique).
10. **Groupes, événements et « ressources réservables » pour le mid-market** — Cloudbeds Groups & Events + Spaces (propositions de marque, rooming lists par lien public, cabanas/salles à l'heure), Mews Events et Bookable Services (parking, coworking à l'heure), Clock Events (BEO live, signature et acompte en ligne), RoomRaccoon Room Allotment (auto-attribution des chambres par les membres du groupe). Bonus : pilote Uber facturé au folio (Mews), réseau de fidélité partagé entre indépendants (Cloudbeds × Journey, juin 2026), rapports d'efficacité HK par temps de nettoyage (Mews).

---

## 5. Lecture pour AITE HOUSE (Odoo 18, Cameroun / Afrique francophone)

Observations factuelles issues du benchmark, utiles pour prioriser :

- **Avantage structurel Odoo :** le POS Odoo fournit nativement plan de salle, écran cuisine, mode hors-ligne et stock par recette — des fonctions classées « différenciantes » (POS offline : 3/10 ; stock recette : 5/10) que la plupart des PMS SMB n'ont pas. À mettre en avant commercialement.
- **Écarts à combler pour atteindre le socle (section 3) :** check-in en ligne avec carte d'enregistrement signée et capture d'ID, housekeeping mobile avec affectation automatique et tickets de maintenance, tarifs dérivés + restrictions + règles d'occupation, groupes/allotements avec release, multi-folios et routage, clôture journalière automatisée, liens de paiement et acomptes automatiques, upsell pré-arrivée, dashboard RevPAR/ADR/pace, API/connecteur channel manager (aucun PMS leader ne vit sans OTA bidirectionnel).
- **Opportunités « rares/différenciantes » adaptées au marché local, qu'aucun leader ne couvre nativement :** mobile money (MTN MoMo, Orange Money) intégré au folio et au booking engine (aucun natif vérifié chez les 10) ; WhatsApp bidirectionnel natif (5/10 seulement) ; registre de police / fiche d'hébergement camerounaise et conformité fiscale OHADA (les leaders ne couvrent que leurs marchés d'origine) ; continuité hors-ligne du PMS (aucun PMS cloud ne l'offre ; Mews l'a refusée explicitement) ; lost & found (4/10) ; minibar depuis l'app HK (6/10) ; bons cadeaux (5/10).
- **Innovations à cadence réaliste :** assistant IA staff et messages IA sur WhatsApp sont devenus la norme des annonces 2025-2026 ; une version « règles + recommandations tarifaires simples » (type RaccoonRev/Little Hotelier) est plus atteignable qu'un RMS complet.

---

## 6. Points non vérifiés (à confirmer avant usage externe)

- Prix réels d'OPERA Cloud, Mews, Cloudbeds, Hotelogix, protel, Guestline (sur devis ; toutes les valeurs données sont des estimations tierces ou des grilles historiques).
- Guestline : GDS, messagerie WhatsApp, night audit détaillé, mode mobile HK ; « 250 $/utilisateur/mois » Capterra.
- protel/Planet : détails MICE actuels (documentation historique), app mobile, conformité police DACH, allotements.
- Little Hotelier : GDS, multi-propriété réel, applicabilité de Paystack/mobile money, « automated night audit » (taxonomie HotelTechReport générique).
- eZee/YCS : tokenisation, module événements sur le cloud, déclarations police (C-Form Inde).
- Hotelogix : restrictions tarifaires, lost & found, maintenance, disponibilité effective des fonctions IA « futures ».
- Mews : liste d'attente via Rezylist (affirmation d'un partenaire), Mews POS table management/offline, loyauté native.
- Cloudbeds : 2FA, surbooking configurable, disponibilité générale du POS natif (liste d'attente) et du RMS (annoncé sept. 2026).
- Clock : compatibilité des serrures pour clés digitales, loyauté native, metasearch.
- OPERA : modules spa/activités sur OPERA Cloud (vs Suite8), kiosque natif vs partenaires.

Sources complémentaires utilisées pour les recoupements : [HotelTechReport – comparatif Rezlynx vs Mews](https://mail.hoteltechreport.com/compare/rezlynx-vs-mews) · [Mews vs Cloudbeds (biaisé)](https://www.mews.com/en/compare/mews-vs-cloudbeds) · [Mews vs Guestline (biaisé)](https://www.mews.com/en/compare/mews-vs-guestline) · [Capterra OPERA Cloud](https://www.capterra.co.uk/software/1034527/opera-cloud-property-management) · [roommaster – alternatives (concurrent)](https://www.roommaster.com/blog/cloudbeds-alternatives) · [Hotelogix estimations (concurrent)](https://www.roommaster.com/blog/hotelogix-pricing) · [Little Hotelier estimations (concurrent)](https://www.roommaster.com/blog/littlehotelier-pricing) · [costbench Mews](https://costbench.com/software/hotel-management/mews/) · [toolradar Mews](https://toolradar.com/tools/mews/pricing) · [Prostay sur OPERA (concurrent)](https://www.prostay.com/blog/oracle-opera-pms-alternative-2026/) · [Pesapal × OPERA](https://www.pesapal.com/blog/why-smart-hotels-choose-oracle-opera-pms-to-stay-ahead) · [Mobipaid intégrations](https://www.mobipaid.com/userguide/integrations/hospitality-integrations) · [OpenKey × Cloudbeds](https://hoteltechreport.com/news/openkey-cloudbeds) · [Hotelogix contactless](https://www.travolution.com/news/travel-sectors/accommodation/hotelogix-enhances-hotel-pms-with-contactless-self-service-capabilities-for-guests/) · [Hotelogix connectivité](https://www.hotelogix.com/blog/connectivity-gaps-philippines)
agentId: ab1ac84af561cc0f9 (use SendMessage with to: 'ab1ac84af561cc0f9', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 342901
tool_uses: 299
duration_ms: 2313404</usage>