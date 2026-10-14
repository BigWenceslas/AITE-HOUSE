# Écarts relevés en écrivant la vidéo

En rejouant l'application écran par écran, quelques points ne concordent pas
avec la recette ou avec les règles du projet (`CLAUDE.md`, « Règles
d'intuitivité »). Ils sont **signalés ici, pas corrigés** : la vidéo montre
ce que le code affiche, ou contourne le geste sans le rejouer. Chaque point
est à trancher par l'équipe avant une correction dans `addons/`.

| # | Où | Constat | Règle ou source contredite | Dans la vidéo |
|---|---|---|---|---|
| 1 | `aite_housekeeping/views/menus.xml` — menu « Répartir les chambres du jour » | Le menu porte `groups="aite_hotel_management.group_hotel_user"` (Réception) : le profil **Gouvernante** ne le voit pas. | Cas P02 du cahier de recette et `tests/vague1/scenario_housekeeping.py` : c'est la gouvernante qui répartit les chambres. | Geste non montré au chapitre 2. |
| 2 | `aite_exec_dashboard` — sous-titre de « Chiffre d'affaires total » (`'Période ' + state.dateFrom + ' → ' + state.dateTo`) | Dates affichées au format ISO : « Période 2026-10-01 → 2026-10-15 ». | Règle 6 : dates au format `%d/%m/%Y`. | Rejoué tel quel (chapitre 6). |
| 3 | `aite_slot_booking` — titre « Planning du <jour> » (`state.day`) | « Planning du 2026-10-15 ». | Règle 6. | Rejoué tel quel (chapitre 6). |
| 4 | `aite_city_tax` (`city_tax_report.py`) et `aite_guest_registry` (`guest_stats.py`) — champ `month` | Les lignes des pivots « Taxe de séjour — état mensuel » et « Statistiques d'hébergement » s'intitulent « 2026-10 » (`to_char(…, 'YYYY-MM')`). | Règle 6 (un mois lisible : « octobre 2026 » ou « 10/2026 »). | Rejoué tel quel (chapitre 7). |
| 5 | `aite_pos_analytics/static/src/js/services/utils.js` — `fmtPct` | Pourcentages au point décimal et sans espace : « 56.0% », « Taux: 56.0% ». | Règle 6 (format français : « 56,0 % »), comme les autres tableaux de bord AITE. | Rejoué tel quel (chapitre 6). |
| 6 | `aite_purchase_dashboard` — carte « En retard de paiement » (`negMoney`) | Quand rien n'est en retard, la carte affiche « −0 FCFA » (capture de recette `r4-direction-04`). | Lisibilité (règle 4 : une phrase d'état lisible). | La vidéo montre un montant en retard non nul : le défaut n'apparaît pas. |
| 7 | `aite_city_tax/models/hotel_hotel.py` (`city_tax_help`) et `city_tax_rate.py` (libellé du barème) | La devise est écrite par son code ISO : « 3 000 XAF par personne et par nuit », « Cameroun — 3 ★ : 3 000 XAF ». | Règle 6 : montants en FCFA (le symbole de la devise, `currency_id.symbol`, donnerait « FCFA »). | Rejoué tel quel (chapitre 7). |
| 8 | `docs/captures_uat/` (recette UAT) | Les captures de la recette navigateur sont en anglais (« Access Error », « Close », « Point of Sale », « My Company ») : la base de recette n'était pas en français. | Règle 6 (« pas d'anglais résiduel ») — vaut pour la base livrée, pas pour le code. | La vidéo rejoue l'interface en français, comme sur la base `fr_FR` du client. |

Points vérifiés et **conformes** au passage : la ligne « Taxe de séjour —
4 nuitée(s) × personne (3 ★, Cameroun) » ajoutée seule au folio (cas N02),
le bandeau « Registre des clients : N fiche(s) à compléter » après le
check-in (O01), la sévérité « Réglée » d'une ardoise soldée, les refus
d'accès de la gouvernante (folios), de la caisse (réservations) et du
magasin (ardoises), et les chiffres repris à l'identique d'un tableau de
bord à l'autre (restauration = analyse des ventes, encours des ardoises,
valeur du stock).
