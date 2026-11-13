# Restaurant — périmètre fonctionnel

**Source :** onze messages vocaux WhatsApp d'un client, transmis à AITE le 12/11/2026 (transcription en annexe A), une précision d'AITE sur l'établissement, du 13/11/2026, et ses réponses du même jour à six des sept questions posées (annexe A bis ; parties 1 et 2).
**Date :** 12/11/2026 ; mises à jour le 13/11/2026 (profil de l'établissement, puis réponses d'AITE) · **Rédaction :** AITE Consulting · **Statut :** document de travail, à valider par le dirigeant d'AITE ; l'extrait destiné au client reste à tirer.

**Comment lire ce document.** Il est écrit pour le dirigeant d'AITE et ne se transmet pas tel quel au client. L'extrait à lui remettre se compose de :

- la partie 2, sans sa rubrique « Le profil de l'établissement », interne : le client la confirme par ses réponses (Q3, Q6, Q64 à Q83) ;
- le tableau de synthèse de la partie 1, colonnes « Réf. », « Exigence », « Priorité », « À l'ouverture » et « État » ;
- dans chaque fiche de la partie 3, les rubriques « Le client dit », « Règle de gestion », « Critères d'acceptation » et « Questions » ;
- la partie 4, colonnes « Sujet », « Pourquoi cela compte » et « Question », avec la liste « hors périmètre » (4.6) ;
- la partie 7, avec son bloc de validation ;
- l'annexe A : ce sont ses propres messages, qu'il peut ainsi corriger.

Restent internes : les rubriques « Couverture » et « Bonne pratique », placées en fin de fiche et marquées *Interne* ; la colonne « Ce que l'on sait » de la partie 4 et les montages de caisse (4.7) ; les efforts ; les parties 5 et 6 ; les annexes A bis, B et C.

Sept conventions :

- **(M1) à (M11)** : ce que le client a dit, cité par le numéro du message.
- **(P)** : la précision donnée par AITE le 13/11/2026 sur l'établissement (annexe A bis). Ce n'est pas une parole du client : nous n'en tirons que des déductions et des propositions, jamais une demande ; dans l'extrait, (P) se lit « d'après ce qu'AITE sait de votre établissement, à confirmer ». Les points qui en naissent : PROF-01 à PROF-08 (partie 4.7), repris en partie 6.
- **(R)** : les réponses d'AITE du 13/11/2026 à Q3, Q64, Q65 et à trois questions complémentaires (annexe A bis). Comme (P), pas des paroles du client, à faire confirmer (partie 7.3), et lues de même dans l'extrait. « Option » : une fonction qui peut s'activer, éteinte par défaut.
- « **Déduction :** » : ce qu'AITE comprend ou tire d'un message sans que le client l'ait dit en toutes lettres. Quand une phrase a deux lectures, la déduction renvoie à une question.
- « **Proposition :** » : une idée d'AITE, que le client n'a pas demandée. Celles qui demandent un travail portent un identifiant (REST-05-P1), repris dans les lots de la partie 6. Un critère d'acceptation qui dépend d'une proposition, du tableau des droits ou d'une réponse du client commence par une parenthèse qui le dit.
- « **à vérifier** » : un comportement lu dans le code d'Odoo 18 mais pas essayé à l'écran. Rien n'a été essayé à l'écran de caisse. Une installation à froid et des essais côté serveur ont été joués le 12/11/2026 sur une base jetable, puis rejoués pendant la correction de ce document, et complétés le 13/11/2026 pour le profil de l'établissement, puis pour les réponses d'AITE : les points confirmés ainsi portent la mention « exécuté côté serveur » (détail en annexe C). Chaque point « à vérifier » doit être essayé à l'écran avant d'être promis au client.
- Les renvois **[n]** mènent aux sources (annexe B). Un renvoi suivi du signe ° (par exemple [21°]) désigne une page qui n'a pas pu être ouverte : seul un extrait renvoyé par le moteur de recherche a été lu. Les renvois **C…** (Odoo 18) et **H…** (AITE HOUSE) mènent aux preuves dans le code (annexe C).

---

## 1. En bref

Le client ouvre un restaurant avec service à table ; il veut tenir sa salle, son stock et ses rapports.

- **Le profil de l'établissement** (P, R) : un restaurant seul, sans chambres, avec pizzas, café, petits déjeuners, bar et cuisine. Aucune exigence nouvelle, mais huit points à trancher (PROF-01 à PROF-08, partie 4.7).
- **Ce que le profil et les réponses changent.** *Réglé (R), à confirmer :* l'hôtel sort ; on vend cinq modules d'AITE HOUSE sur seize, installés sans erreur sans le socle hôtelier (exécuté côté serveur), fidélité exclue sauf décision d'AITE ; une seule caisse, ouverte sur chaque poste, et des ventes à table. *En options, fermées par défaut :* emporter, comptoir, livraison, sans suivi des courses (PROF-04) ; tiroir du bar, par une seconde caisse (PARAM-11) ; bar qui encaisse les tables. *Mais Odoo les ouvre d'office* (le « + » offert à tous, C93 ; un poste au bar encaisse toute table, C12) : d'où PROF-04-P1 (S) au lot 1, consigne jusqu'à REST-03. *À régler :* tailles, formules, imprimantes, doses (PROF-01, 03, 05, 07), PARAM-10 ; *à corriger :* AH-11, AH-12. *À développer si le client le demande :* supplément selon la taille, chiffre par formule, moitié-moitié, moments de la journée (PROF-01 à 03, PROF-06) ; type de vente, livraison suivie (PROF-04-P2, PROF-04-P3) ; options du bar ensemble (PROF-08-P1). *À demander :* Q72, Q77 à Q79.
- **Déjà dans Odoo 18, à activer ou à régler** (12 exigences sur 26, 5 autres en partie) : plan de salle, table ouverte par son numéro, correction du nombre de personnes, écran de commande par familles, droits du manager, réunion et division des tables, saisie du stock, rapports par période et par famille, tableau de bord standard du restaurant (prix moyen par personne), fiches techniques.
- **À développer par AITE** (9 exigences, plus le complément des 5 précédentes et les options proposées) : qui a ouvert, qui a saisi et qui a encaissé ; quatre niveaux d'accès ; nombre de personnes obligatoire ; verrou après envoi, code du supérieur, trace des annulations et leur rapport ; alerte de couleur ; refus de vente à stock nul.
- **À trancher avec lui** (83 questions, partie 7, dont 13 nées du profil et 7 des réponses) : 17 conditionnent le démarrage (date d'ouverture, taille, matériel, cuisine, tableau des droits, sens de plusieurs phrases, ventes sans table, caisses, comptage du soir, date des options), dont 3 répondues par AITE (Q3, Q64, Q65) ; pour les 66 autres, un choix par défaut est proposé.
- **Alertes pour AITE** (partie 5) : aucun essai à l'écran n'a été fait ; nos ardoises peuvent s'ouvrir sur une table non encaissée (exécuté côté serveur) ; nos analyses perdent le nom du vendeur dès que les employés s'identifient par code ; le compte Odoo qui ouvre la caisse décide de ce qui fonctionne en salle.

### Tableau de synthèse

- **Priorité** : classement d'AITE d'après les mots du client. « Il faut », « il faudrait », « doit », « je veux », ou une demande sans réserve = Indispensable ; « si possible », « ce serait bien » = Souhaité ; « pour le futur » = Plus tard. Ce classement dit l'importance, pas l'échéance : il est à confirmer avec lui (Q1).
- **À l'ouverture** : « oui » = la fonction existe dans Odoo 18 et sera là dès l'installation ; « à confirmer » = elle demande un développement, dont la date dépend de la réponse à Q1 ; « non » = le client la repousse lui-même (M8).
- **État** (pour le client) : Existe déjà ; Existe en partie ; À développer ; À décider avec vous.
- **Couverture** (interne) : **Activer** = la fonction existe, il suffit de l'installer ou de la cocher ; **Régler** = elle existe et demande un paramétrage ou une saisie ; **Développer** = AITE doit l'écrire ; **À trancher** = dépend d'une réponse du client. L'effort S, M ou L est une estimation tirée de la lecture du code, pas un chiffrage. La feuille de route n'emploie que M et L et ne donne aucune équivalence en jours : cette équivalence est à fixer par AITE avant tout devis.

| Réf. | Exigence | Source | Priorité | À l'ouverture | État | Couverture (interne) |
|---|---|---|---|---|---|---|
| REST-01 | Chaque utilisateur s'identifie par son code personnel. | M1, M2 | Indispensable | oui ; code obligatoire et unique : à confirmer | Existe en partie | Activer ; code obligatoire et unique : Développer (S) |
| REST-02 | Chaque opération garde le nom de son auteur : qui a ouvert la table, qui a saisi, qui a encaissé. | M1, M2 | Indispensable | à confirmer | À développer | Développer (M) ; code demandé avant d'ouvrir une table, avant d'encaisser et après chaque envoi (REST-02-P1) : Développer (S) ; délai d'inactivité (REST-02-P2) : À trancher |
| REST-03 | Quatre niveaux d'accès : serveur, caissière, chef de salle ou superviseur, manager. | M10 | Indispensable | à confirmer | À développer ; tableau à décider avec vous | Développer (L) ; tableau des droits (REST-03-P1) : À trancher |
| REST-04 | Le manager voit tout ; il peut ajouter des produits et changer des prix. | M10 | Indispensable | oui | Existe déjà | Régler ; prix interdit au superviseur : couvert par REST-03 |
| REST-05 | Le numéro de la table est demandé à l'ouverture. | M2 | Indispensable | oui | Existe déjà ; façon de faire à décider avec vous | Activer, lecture à confirmer ; numéro inconnu refusé (REST-05-P1) : Développer (S), À trancher |
| REST-06 | Le nombre de personnes est demandé à l'ouverture. | M2 | Indispensable | à confirmer | À développer | Développer (S) |
| REST-07 | Le nombre de personnes se corrige en cours de repas. | M9 | Indispensable | oui | Existe déjà | Activer ; zéro refusé (REST-07-P1) : Développer, avec REST-06 |
| REST-08 | Le nom du client ou de la société s'écrit sur la table, à l'ouverture ou après. | M2 | Souhaité | oui pour un client enregistré ; nom libre : à confirmer | Existe en partie ; à décider avec vous | Activer (client enregistré, après l'ouverture) ; nom libre, y compris à l'ouverture : Développer (S) ; À trancher |
| REST-09 | L'écran de commande est rangé par familles, sous-familles et sous-sous-familles. | M5 | Indispensable | oui | Existe déjà ; premier écran à décider avec vous | Régler ; premier écran réduit aux deux familles (REST-09-P1) : À trancher, effort à estimer |
| REST-10 | Une commande envoyée ne se retire plus. | M3 | Indispensable | à confirmer | À développer | Développer (M), à concevoir avec REST-11 et REST-12 |
| REST-11 | L'annulation passe par le code d'un supérieur. | M3, M10 | Indispensable | à confirmer | À développer | Développer (M) |
| REST-12 | Chaque annulation est expliquée et laisse une trace. | M10, M7, M1 | Indispensable pour la trace et le rapport ; journal non modifiable et motif obligatoire : propositions d'AITE | à confirmer | À développer ; à décider avec vous | Développer (M) ; journal non modifiable (REST-12-P1) et motif obligatoire (REST-12-P2) : À trancher |
| REST-13 | On peut réunir des tables. | M4 | Souhaité | oui | Existe déjà | Activer (à vérifier : droits du compte de la caisse) |
| REST-14 | On peut diviser une table. | M4 | Souhaité | oui, si la division se fait par produits | Existe déjà si la division se fait par produits ; à décider avec vous | Activer si la division se fait par produits ; parts égales (REST-14-P1) : Développer, effort à estimer ; À trancher |
| REST-15 | On peut déplacer un produit vers une autre table, existante ou nouvelle. | M4 | Souhaité | oui, en deux gestes (à vérifier) | Existe en partie ; à décider avec vous | Activer en deux gestes (à vérifier) ; geste unique (REST-15-P1) : Développer (M) ; trace des déplacements (REST-15-P2) : Développer (S) ; À trancher |
| REST-16 | Le plan de salle est visible. | M11 | Indispensable | oui | Existe déjà | Régler ; informations sur la table (REST-16-P1) : effort à estimer |
| REST-17 | La table est verte à l'ouverture, orange après un délai. | M11 | Indispensable | à confirmer | À développer ; délai à décider avec vous | Développer (M) ; délai : À trancher |
| REST-18 | Le stock que l'on a s'enregistre, même pour les petites quantités. | M6 | Indispensable | oui | Existe déjà | Activer ; écran d'entrée rapide (REST-18-P1) : Développer (S), À trancher |
| REST-19 | La vente est refusée quand le stock est épuisé. | M6 | Indispensable | à confirmer | À développer ; produits concernés à décider avec vous | Développer (L pour l'ensemble, en quatre volets 19a à 19d) ; produits concernés : À trancher |
| REST-20 | Les fiches techniques se remplissent peu à peu. | M8 | Plus tard pour le contenu ; fonction disponible à l'ouverture ou non : à trancher | contenu : non ; fonction : à confirmer | Existe déjà ; à décider avec vous | Activer ; écran simplifié (REST-20-P1) : Développer (M) |
| REST-21 | La rentabilité de chaque plat se calcule. | M8 | Plus tard | non | Existe en partie | Régler ; compléments : Développer (M) |
| REST-22 | Un rapport donne les annulations. | M7, M10 | Indispensable | à confirmer | À développer | Développer (S), après REST-12 |
| REST-23 | Un rapport donne les ventes de ce que l'on choisit : une famille, une sous-famille ou un produit. | M7 | Indispensable | oui | Existe déjà | Régler ; sous-totaux par niveau de famille (REST-23-P1) : Développer (S) |
| REST-24 | La période des rapports se choisit librement. | M7 | Indispensable | oui | Existe déjà | Activer |
| REST-25 | Un rapport compte les personnes, les tables et les ventes. | M9 | Indispensable | oui, en version standard (à contrôler à l'écran) | Existe en partie | Activer (à contrôler à l'écran) ; comptage exact (REST-25-P1) : Développer (S à M) |
| REST-26 | Un rapport donne le prix moyen par personne. | M9 | Souhaité | oui, en version standard (à contrôler à l'écran) | Existe déjà | Activer (à contrôler à l'écran) ; selon la règle de comptage (REST-26-P1) : Développer (S) |

Décompte : 19 exigences indispensables, 5 souhaitées, 2 plus tard. D'après la colonne « État » : douze existent déjà (REST-04, 05, 07, 09, 13, 14, 16, 18, 20, 23, 24, 26), cinq existent en partie (REST-01, 08, 15, 21, 25), neuf sont à développer (REST-02, 03, 06, 10, 11, 12, 17, 19, 22). D'après le premier mot de la colonne « Couverture » : douze à activer, cinq à régler, neuf à développer. Trois des douze « existent déjà » sous réserve d'une lecture à confirmer avec le client : REST-05, REST-09 et REST-14 ; deux autres, REST-25 et REST-26, sous réserve d'un contrôle à l'écran.

---

## 2. Ce que le client a dit

Les dix besoins, reformulés avec les mots du métier. Chacun renvoie aux messages d'où il vient (annexe A). Les passages peu audibles sont signalés.

1. **Savoir qui a fait quoi (M1).** La caisse ne fonctionne qu'après la saisie du code de l'utilisateur, et chaque opération garde le code de son auteur. Son exemple : Valérie, caissière, a ouvert le système et ouvert ou saisi une table (mot peu audible) ; lui-même vient encaisser avec son propre code ; on doit savoir que c'est elle qui a ouvert ou saisi, et lui qui a encaissé.
2. **Ouvrir une table avec son numéro et son nombre de personnes (M2, M9).** Après la saisie du code, la caisse demande le numéro de la table et le nombre de personnes. Si possible, on écrit aussi le nom du client ou d'une société, à l'ouverture ou plus tard. Si des personnes rejoignent la table en cours de repas, on corrige leur nombre.
3. **Une commande envoyée ne se retire plus (M3, M10).** Seul le code d'un supérieur permet d'annuler. Ce supérieur décide, et s'en explique dans son rapport.
4. **Bouger les tables et les produits (M4).** Réunir des tables, diviser une table en deux (il dit l'avoir déjà précisé : nous n'avons pas cette précision), déplacer un produit vers une autre table déjà ouverte, retirer un produit et créer une nouvelle table avec. « Si c'est possible, ce sera bien. »
5. **Un écran de commande rangé par familles (M5).** D'abord Nourriture et Boisson ; puis les sous-familles (Boisson : alcoolisé, non alcoolisé) ; puis les sous-sous-familles (alcoolisé : bière, vin, whisky…).
6. **Tenir le stock et refuser la vente quand il n'y en a plus (M6).** On enregistre les quantités qu'on a, même petites. Quand un produit est épuisé, la caisse ne le prend plus.
7. **Tous les rapports (M7, M9).** Les annulations ; les ventes de ce que l'on choisit (les boissons, les salades, le poulet) ; sur la période que l'on veut : jour, semaine, mois, année. À la fermeture (des tables, ou de la caisse : à confirmer), le système compte les personnes : un rapport donne un prix moyen par personne ou, à défaut, le nombre de personnes, le nombre de tables et la quantité vendue, pour faire le calcul soi-même.
8. **Les fiches techniques, plus tard (M8 ; début du message peu audible).** Elles ne seront pas prêtes pour l'ouverture ; si la fonction est là, on les remplira peu à peu pour calculer la rentabilité.
9. **Quatre niveaux d'accès (M10).** Le serveur ; la caissière ; le chef de salle ou les superviseurs, qui décident d'annuler ou non ; le manager, qui voit tout et peut, par exemple, ajouter des produits et changer des prix.
10. **Un plan de salle en couleurs (M11).** Une table ouverte est, par exemple, verte ; avant la durée normale d'un repas (à une heure, ou à une heure trente), elle passe à l'orange, pour qu'on pense à demander au serveur si le client veut l'addition, qu'il appelle « la facture ». Il arrive qu'une addition soit oubliée et, semble-t-il, que le client parte (mots peu audibles).

### Ce que le client n'a pas dit : le profil de l'établissement (interne)

Précision écrite par AITE le 13/11/2026, hors des messages (P), puis réponses d'AITE du même jour (R) ; textes et lectures en annexe A bis. À faire confirmer par le client (Q3, Q6, Q64, Q65).

- **Ce qui reste inconnu.** Le nom, la date d'ouverture (Q1), le nombre de tables (Q2), l'édition d'Odoo (Q4), le matériel (Q5), qui livrerait (Q72), le comptage du soir (Q77), les tailles de pizza et les formules (Q66, Q69), les horaires (Q73).

---

## 3. Exigences détaillées

Chaque fiche suit le même plan. D'abord ce qui peut être remis au client : ce qu'il a dit, la règle de gestion, les critères d'acceptation (ils deviendront des cas du cahier de recette) et les questions, numérotées comme en partie 7. Ensuite, marquées *Interne* : la couverture (ce qui existe, ce qui manque, l'effort) et la bonne pratique retenue.

**Vocabulaire.** Les mots du client à gauche, ceux de ce document à droite.

| Le client dit | Ce document écrit | Remarque |
|---|---|---|
| le nombre de personnes | personnes | Ce sont les couverts servis ; Odoo écrit « Convives ». |
| la facture | addition | La note d'une table. Dans les questions, nous gardons ses mots (« la facture de la table ») et disons « facture officielle » pour le document établi au nom d'une société. |
| catégorie, sous-catégorie | famille, sous-famille | Odoo écrit « catégorie ». |
| prix moyen | prix moyen par personne | C'est la dépense moyenne par personne. |
| profitabilité | rentabilité | |
| mot de passe, code | code | |
| ajouter les tables ensemble | réunir des tables | |
| un code du grade supérieur | le code d'un supérieur | « Supérieur » désigne le chef de salle, un superviseur ou le manager. |

Sept mots ont un seul sens dans tout le document. **Commande** : ce qui part en préparation, à la cuisine ou au bar (Odoo appelle aussi « commande » l'addition entière ; ce sens n'apparaît que dans les rubriques internes). **Achat** : ce qui est commandé à un fournisseur, avec son bon de commande. **Serveur** : toujours l'employé de salle. **Poste** : l'écran ou la tablette de caisse ; **système central** : l'ordinateur qui garde les données. **Table ouverte** : une table dont le nombre de personnes a été validé, avec ou sans produit ; elle reste occupée au retour sur le plan. **Envoyé** : se dit d'un produit validé par le bouton « Commander », qu'un bon soit imprimé ou non, et quelle que soit sa famille. Ces deux dernières définitions sont celles que nous retenons ; Odoo, aujourd'hui, ne les applique pas (voir REST-06 et REST-10). Les noms de modules et de champs, entre accents graves, ne figurent que dans la rubrique « Couverture ».

Trois mots s'ajoutent avec le profil (P). **Vente sans table** : au comptoir, à emporter ou en livraison. **Formule** : plusieurs produits vendus ensemble à prix fixe (« Combo » dans Odoo). **Poste de préparation** : la cuisine, le bar, le four ; à ne pas confondre avec le poste de caisse.

### 3.1 Identification et traçabilité

#### REST-01 — Chaque utilisateur s'identifie par son code personnel

- **Source :** M1, M2 · **Priorité :** Indispensable · **À l'ouverture :** oui pour la connexion par code ; à confirmer pour le code obligatoire et unique.
- **Le client dit :** « il faut le mot de passe de l'utilisateur pour que ça permette de fonctionner » (M1) ; « après que quelqu'un ait entré son code » (M2).
- **Règle de gestion.** La caisse ne s'utilise qu'après la saisie du code de l'utilisateur : sans code valide, aucune table ne s'ouvre et aucune vente ne se saisit (M1). **Déduction :** chaque employé a son propre code et aucun code n'est partagé ; sans cela, on ne saurait pas qui a fait quoi (REST-02).
- **Critères d'acceptation.**
  1. Étant donné une caisse qui vient d'être ouverte, quand personne n'a saisi de code, alors aucune table ne peut être ouverte.
  2. Étant donné un employé autorisé, quand il saisit son code, alors son nom s'affiche en haut de l'écran et il peut travailler.
  3. Étant donné un employé sans code, ou dont le code est déjà celui d'un collègue, quand sa fiche est enregistrée, alors l'enregistrement est refusé et le message dit quoi corriger.
- **Questions :** Q15, Q18.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* la connexion des employés à la caisse, par le module `pos_hr`, qui s'installe seul dès que l'application Employés (`hr`) est présente. Réglage « Se connecter avec Employés » (Point de Vente → Configuration → Paramètres, bloc « Interface du PdV »). Le code est le « Code PIN » de la fiche employé, onglet « Paramètres », visible du seul groupe Employés / Responsable (C63) ; un badge est possible (« ID du badge »). Le bouton « Bloquer » ramène à l'écran de code (C1, C3, C4). *Il manque :* un employé sans code entre sans rien taper, et deux employés peuvent avoir le même code (C2). *AITE développe :* le code obligatoire et unique pour tout employé autorisé sur la caisse ; le contrôle d'unicité compare les codes en `sudo()`, puisque celui qui enregistre une fiche ne voit pas les codes des autres. **Effort : S.** À savoir : (1) le code est comparé sur le poste de caisse et non par le système central (C3) : c'est un contrôle suffisant pour identifier, pas une sécurité forte ; (2) la caisse elle-même s'ouvre avec un compte Odoo (identifiant et mot de passe), les codes ne servent qu'ensuite (C74) : la personne qui ouvre la caisse a donc besoin d'un compte — voir « Le compte de la caisse », partie 5.1 (à vérifier à l'écran).
- *Interne —* **Bonne pratique.** Un code personnel par employé, jamais un code d'équipe : avec un code partagé, ni les ventes ni les gestes ne se rattachent plus à une personne [19°]. Odoo n'accepte que des chiffres dans ce code [2].

#### REST-02 — Chaque opération garde le nom de son auteur

- **Source :** M1, M2 · **Priorité :** Indispensable · **À l'ouverture :** à confirmer.
- **Le client dit :** « Que les transactions gardent le code de l'utilisateur. […] Elle a ouvert le système, elle a [attrapé / tapé] une table. Moi, je viens faire le paiement avec mon code. Il faudrait qu'on sache que c'est elle qui a [attrapé / tapé] et c'est moi qui ai fait la transaction » (M1) ; « Au moment d'ouvrir la table, après que quelqu'un ait entré son code » (M2).
- **Règle de gestion.** Chaque opération garde le code de son auteur (M1). Pour chaque table, on sait qui l'a ouverte ou saisie (mot peu audible) et qui l'a encaissée (M1). Le client décrit lui-même le code entré avant d'ouvrir une table (M2) et au moment d'encaisser (M1).
  **Déduction, à confirmer (Q14) :** si le mot est « ouvert », on garde le nom de celui qui a ouvert la table ; si le mot est « tapé », on garde aussi le nom de celui qui a saisi chaque produit. Faute de réponse, nous gardons les trois noms : qui a ouvert, qui a saisi, qui a encaissé. Ces noms ne changent plus ensuite ; on les lit sur l'addition enregistrée et dans les rapports.
  **Déduction, à confirmer (Q15) :** « elle a ouvert le système » peut aussi désigner l'ouverture de la caisse en début de service ; on garde alors le nom de la personne qui a ouvert la caisse.
  **Déduction :** la caisse demande le code avant d'ouvrir une table et avant d'encaisser. **Proposition (REST-02-P1) :** elle le redemande aussi après chaque envoi de commande. **Proposition (REST-02-P2) :** elle le redemande après un moment sans activité.
- **Critères d'acceptation.**
  1. Étant donné une table ouverte par Valérie, quand le restaurateur l'encaisse avec son propre code, alors l'addition enregistrée indique « Ouverte par : Valérie » et « Encaissée par : » suivi de son nom.
  2. Étant donné un employé identifié et une autre personne qui vient encaisser une table, quand elle demande le paiement, alors la caisse lui demande son code avant d'encaisser.
  3. (Selon la réponse à Q14.) Étant donné une table où deux employés ont saisi des produits, quand on consulte l'addition, alors on lit pour chaque saisie le produit, la quantité ajoutée, le nom de l'employé et l'heure.
  4. (Proposition.) Étant donné une période, quand le manager ouvre le rapport des ventes, alors il peut regrouper les ventes par « ouverte par » et par « encaissée par ».
  5. (Si REST-02-P1 est retenue.) Étant donné un serveur qui vient d'envoyer une commande, quand quelqu'un touche de nouveau l'écran, alors le code est demandé.
- **Questions :** Q14, Q15, Q16, Q17.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* il garde un seul nom par addition, le « Caissier » (`employee_id`) (C6), et le compte Odoo qui a ouvert la session de caisse (« Ouvert par »), qui n'est pas un employé à code (C74). *Il manque :* ce nom unique est réécrit à chaque produit ajouté, puis à la validation du paiement, au nom de l'employé alors connecté (C7). Dans l'exemple de M1 : si le restaurateur s'identifie avant d'encaisser, seul son nom reste et Valérie disparaît ; s'il ne le fait pas, l'encaissement est enregistré au nom de Valérie. Or la caisse ne se verrouille qu'à la main : la veille d'écran et le retour au plan de salle laissent l'employé connecté (C4). Les lignes d'une addition n'ont aucun auteur (C9), et deux saisies du même produit fusionnent en une seule ligne, quel que soit l'employé et que la première soit déjà envoyée ou non ; le transfert fusionne aussi les lignes (C64) : une ligne n'a donc pas un auteur unique. L'historique des changements de caissier repose sur un seul champ de la session (C5) : avec une même caisse ouverte sur plusieurs postes, les connexions de tous les postes s'y mélangent ; il ne peut pas servir de preuve. *AITE développe :* « ouverte par » (figé à l'ouverture), « encaissée par » (figé au paiement), leur affichage sur l'addition et dans les rapports ; et, pour l'auteur des saisies, un choix à trancher par AITE : (a) un journal des saisies (produit, quantité ajoutée, employé, heure), lu sur l'addition, sans toucher aux lignes — recommandé ; (b) interdire la fusion des lignes entre employés différents, ce qui allonge les additions et touche les bons de cuisine, la division et le transfert. Y ajouter le poste, ou la caisse d'ouverture (C97, C98). **Effort : M** avec le journal (a) ; à réévaluer avec (b). Code demandé avant d'ouvrir une table et avant d'encaisser, puis REST-02-P1 et REST-02-P2 : **Effort : S** pour l'ensemble.
- *Interne —* **Bonne pratique.** Les caisses de restaurant gardent plusieurs noms par addition : le serveur de la table, l'auteur et l'approbateur de chaque annulation [21°][44°]. Elles savent redemander le code après chaque vente ou après un délai d'inactivité réglable [19°][20°].

### 3.2 Profils et droits

#### REST-03 — Quatre niveaux d'accès

- **Source :** M10 · **Priorité :** Indispensable · **À l'ouverture :** à confirmer.
- **Le client dit :** « Les accès doivent être échelonnés de façon suivante. On a le serveur, on a la caissière, on a le chef de salle ou les superviseurs qui sont au-dessus, qui peuvent prendre la décision d'annuler ou de ne pas annuler […]. Et puis il y a un accès de manager » (M10).
- **Règle de gestion.** Chaque employé a un niveau : serveur, caissière, chef de salle ou superviseur, manager (M10). Le client a dit deux choses sur ces niveaux : les chefs de salle et les superviseurs décident d'annuler ou non ; le manager voit tout (M10). **Déduction :** le niveau fixe les gestes permis. Tout le reste est à écrire avec lui.
  **Proposition (REST-03-P1) :** le tableau ci-dessous, à remplir avec le client (Q8). Au départ, ce tableau est fixe : AITE le règle d'après ses réponses.

  | Geste | Serveur | Caissière | Chef de salle, superviseur | Manager |
  |---|---|---|---|---|
  | Ouvrir la caisse en début de service | à trancher | oui, d'après l'exemple de M1 (à confirmer) | oui | oui |
  | Ouvrir une table, saisir, envoyer | oui | oui | oui | oui |
  | Retirer un produit pas encore envoyé | oui | oui | oui | oui |
  | Encaisser | à trancher | oui | oui | oui |
  | Ouvrir une vente sans table (option) | à trancher | oui | oui | oui |
  | Modifier la table d'un collègue | à trancher | oui | oui | oui |
  | Réunir, diviser, déplacer | à trancher | oui | oui | oui |
  | Annuler un produit envoyé ou une table | non : code d'un supérieur | à trancher | oui (M10) ; explication : à trancher | oui ; explication : à trancher |
  | Remise, produit offert | non | à trancher | à trancher | oui |
  | Changer un prix en caisse | non | non | non | oui |
  | Rembourser une addition payée | non | non | à trancher | oui |
  | Forcer la vente d'un produit épuisé | non | non | à trancher | oui |
  | Sortir des espèces | non | à trancher | oui | oui |
  | Fermer la caisse | non | à trancher | oui | oui |
  | Saisir le stock, faire l'inventaire | non | non | à trancher | oui |
  | Produits, prix, plan de salle | non | non | non | oui |
  | Motifs d'annulation, délai de l'alerte, niveau des employés | non | non | non | oui |
  | Rapports | non | à trancher | annulations | tous |

  **Proposition (REST-03-P2), en option :** le manager modifie lui-même ce tableau à l'écran.
- **Critères d'acceptation.**
  1. (Selon le tableau validé.) Étant donné un employé de niveau serveur, quand il tente d'annuler un produit envoyé, alors la caisse demande le code d'un supérieur.
  2. (Selon le tableau validé.) Étant donné chacun des quatre niveaux, quand on joue un à un les gestes du tableau, alors chaque geste est permis ou refusé comme le tableau le prévoit.
  3. Étant donné le manager qui change le niveau d'un employé, quand la caisse est rouverte, alors le nouveau niveau s'applique.
  4. (Si REST-03-P2 est retenue.) Étant donné le manager qui retire au serveur le droit d'encaisser, quand la caisse est rouverte, alors le paiement n'est plus proposé au serveur.
- **Questions :** Q8, Q15, Q16, Q19, Q20, Q21, Q22, Q80.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* deux rôles en caisse, « Droits de base » et « Droits avancés » (deux listes d'employés dans les paramètres de la caisse), plus le profil « Administrateur » du Point de Vente pour l'espace de gestion (C10, C14). Une troisième marque existe pour un seul geste : seul l'employé lié à un compte Administrateur du Point de Vente peut fermer la caisse quand l'écart de comptage dépasse le maximum autorisé (C72). Sans développement, on obtient donc : manager = Administrateur ; superviseur = Droits avancés ; serveur et caissière = Droits de base, sans différence entre eux. *Il manque :* un serveur qui commande sans encaisser (le bouton de paiement n'est lié à aucun rôle) ; l'annulation réservée (elle est ouverte à tous) ; le dosage geste par geste : les droits avancés donnent en bloc le changement de prix (si « Contrôle des prix » est coché), la création de produits, le plan de salle et la fermeture (C11, C12). Les entrées et sorties d'espèces, elles, sont ouvertes à tout employé identifié dès que le compte de la caisse a le droit Facturation ; les réserver demande un développement, compris dans REST-03 (C57 ; lu dans le code et dans le test standard, non essayé à l'écran). Les gestes nés du profil (taille, supplément, formule, addition sans table, « à emporter », liste de prix) ne testent aucun rôle (C90) : à écrire au tableau des droits si besoin (Q8, Q74). Les employés se règlent par caisse, pas par poste (C97) : réserver l'encaissement des tables à certains barmen (Q80) relève de ce développement. Ces droits sont contrôlés par l'écran de la caisse, pas par le système central (C13). Les lecteurs de rapports ont besoin d'un compte Odoo personnel : la documentation précise qu'un employé aux droits avancés qui n'a pas de compte n'accède pas à l'espace de gestion [2] ; le prix par utilisateur de l'édition Enterprise n'a pas été vérifié. *AITE développe :* les quatre niveaux par employé et le tableau des droits, appliqué dans la caisse et vérifié par le système central pour les gestes sensibles. **Effort : L.** REST-03-P2 (tableau modifiable à l'écran) : effort à estimer, en plus.
- *Interne —* **Bonne pratique.** Des droits définis geste par geste pour chaque rôle ; quand le droit manque, la caisse demande le code d'un supérieur sans changer d'utilisateur [21°][22°].

#### REST-04 — Le manager voit tout ; il peut ajouter des produits et changer des prix

- **Source :** M10 · **Priorité :** Indispensable · **À l'ouverture :** oui.
- **Le client dit :** « il y a un accès de manager, un super [admin], qui peut voir tous les autres trucs, peut-être ajouter des produits, changer des prix et autres » (M10).
- **Règle de gestion.** Le manager voit tout (M10). Le client cite en exemple l'ajout de produits et le changement des prix (« peut-être […] et autres »). **Déduction, à confirmer (Q23) :** le manager accède à tous les écrans et à tous les rapports ; il crée et modifie les produits et leurs prix. **Proposition (REST-04-P1) :** aucun autre niveau ne change un prix en caisse.
- **Critères d'acceptation.**
  1. (Si REST-04-P1 est retenue.) Étant donné « Contrôle des prix » coché, quand une caissière sélectionne une ligne, alors la touche Prix est grisée, ne répond pas, et le prix de la ligne ne peut pas être changé.
  2. Étant donné le manager, quand il crée un produit avec son prix et sa famille, alors le produit est proposé à l'écran de commande après rechargement de la caisse.
  3. (Selon le tableau validé.) Étant donné un serveur, quand il s'identifie, alors la caisse ne lui propose aucun lien vers la configuration ni vers les rapports.
- **Questions :** Q16, Q23.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le profil « Administrateur » du Point de Vente (fiche utilisateur) donne les produits, les prix, les familles, les moyens de paiement, le plan de salle et les rapports (C14). Le réglage « Contrôle des prix » (« Limiter les modifications de prix aux managers », bloc « Tarif » des paramètres) interdit aux droits de base de changer le prix d'une ligne : la touche Prix est désactivée (C15). **Régler**, pour les serveurs et les caissières. Pour le superviseur, le réglage ne suffit pas : s'il reçoit les « Droits avancés », il garde le changement de prix ; REST-04-P1 n'est tenue pour lui qu'avec REST-03. *Il manque aussi,* pour que le manager fasse ce qu'on lui prête : son compte doit recevoir en plus Employés / Responsable (codes, création des employés) et Fabrication / Administrateur, pour le coût d'une fiche technique (lot 3) et, pour ce profil, pour créer les fiches des doses et des pizzas ; le profil Administrateur du Point de Vente ne les donne pas, ni l'écriture des règles d'une liste de prix (C63, C91 ; exécuté côté serveur). Variante (REST-04-P2) : AITE lui fournit un écran « Équipe de salle » qui écrit pour lui (effort à estimer). Deux réserves : les remises restent ouvertes à tous les employés tant que les deux réglages de remise ne sont pas désactivés (C71 ; partie 4.2) ; et si le serveur n'a aucun lien vers la gestion, son poste reste connecté à Odoo sous le compte de la caisse : le lien est masqué, pas l'adresse (C62 ; partie 5.1).
- *Interne —* **Bonne pratique.** La documentation d'Odoo indique que, sans réglage, tout employé peut modifier un prix à la main et accorder une remise [2] : « Contrôle des prix » est donc à cocher avant l'ouverture.

### 3.3 Ouverture et vie d'une table

#### REST-05 — Le numéro de la table est demandé à l'ouverture

- **Source :** M2 · **Priorité :** Indispensable · **À l'ouverture :** oui.
- **Le client dit :** « après que quelqu'un ait entré son code, il faudrait que le système demande le numéro de la table et le nombre de personnes sur la table pour ouvrir la table » (M2).
- **Règle de gestion.** Après la saisie du code, la caisse fait donner le numéro de la table, puis le nombre de personnes (REST-06), avant tout produit (M2). **Déduction, à confirmer (Q24) :** toucher la table sur le plan de salle vaut réponse à « le système demande le numéro » ; le numéro peut aussi être tapé au clavier. **Déduction :** toute commande de salle est rattachée à une table numérotée. **Déduction (R) :** en temps normal, toute vente a une table ; la vente sans table (à emporter, comptoir, livraison) est une option, éteinte par défaut (PROF-04). **Proposition (REST-05-P1) :** refuser un numéro inconnu, avec un message clair ; à ne retenir que si le client n'ouvre jamais de table hors du plan (M4, Q25). Elle ne gêne pas la vente sans table, qui s'ouvre par un autre bouton.
- **Critères d'acceptation.**
  1. Étant donné un employé qui vient de saisir son code, quand il ouvre une table, alors la caisse lui fait donner le numéro (en touchant la table sur le plan, ou au clavier), puis le nombre de personnes, avant tout produit.
  2. Étant donné le plan de salle, quand le serveur touche la table 12, alors l'écran de commande s'ouvre au nom de la table 12.
  3. Étant donné le sélecteur de table, quand il tape 12 et valide, alors la table 12 s'ouvre.
  4. (Si REST-05-P1 est retenue.) Étant donné un numéro qui n'existe pas, quand il valide, alors la caisse affiche « La table 99 n'existe pas » et n'ouvre rien.
  5. (Option de vente sans table ouverte, PROF-04.) Étant donné un employé identifié, quand il ouvre une vente au comptoir, alors l'addition s'ouvre sans numéro de table ni nombre de personnes.
- **Questions :** Q24, Q25, Q64.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le service à table, par le module `pos_restaurant` : réglages « Est un bar/restaurant » puis « Plan des salles & des tables » (paramètres du Point de Vente, bloc « Mode restaurant »). La caisse s'ouvre sur le plan ; le bouton « Table » ouvre le « Sélecteur de table » (« Saisir un numéro de table », bouton « Aller à/au ») (C16). **Activer**, sous réserve de la lecture ci-dessus. *À savoir :* un numéro qui ne correspond à aucune table n'est pas refusé ; il ouvre une addition à ce nom, sans table (C17). C'est peut-être ce que le client appelle « créer une nouvelle table » (REST-15) : REST-05-P1 supprimerait ce comportement, et lui seul. La vente sans table existe par ailleurs : le bouton « + » ouvre une addition sans table, qui peut recevoir un nom ; aucun réglage ne le masque (C82, C93 ; lu dans le code). **Effort de REST-05-P1 : S** ; PROF-04-P1, qui le ferme : S de plus.
- *Interne —* **Bonne pratique.** Aucune source vérifiée ne porte sur le numéro de table ; rien n'est donc retenu ici.

#### REST-06 — Le nombre de personnes est demandé à l'ouverture

- **Source :** M2 · **Priorité :** Indispensable · **À l'ouverture :** à confirmer.
- **Le client dit :** « il faudrait que le système demande le numéro de la table et le nombre de personnes sur la table pour ouvrir la table » (M2).
- **Règle de gestion.** À l'ouverture d'une table, la caisse demande le nombre de personnes (M2). **Déduction :** aucun produit ne peut être saisi tant que ce nombre n'est pas donné ; une fois le nombre validé, la table est ouverte : elle apparaît occupée sur le plan, même sans produit, et le délai de l'alerte (REST-17) part de ce moment. **Proposition (REST-06-P1) :** le nombre vaut au moins 1. **Proposition (REST-06-P2) :** la question est posée aussi quand une table libre reçoit des produits déplacés (REST-15) ; une addition née d'une division ne compte aucune personne de plus, les personnes restent sur la table d'origine ; une vente sans table (option, PROF-04) ne demande pas de nombre de personnes, en porte 0 et n'entre pas dans le compte des tables (Q76).
- **Critères d'acceptation.**
  1. Étant donné une table libre, quand le serveur l'ouvre, alors la caisse demande le nombre de personnes avant tout produit.
  2. Étant donné cette question, quand il valide sans nombre, alors la table ne s'ouvre pas.
  3. (Si REST-06-P1 est retenue.) Étant donné cette question, quand il valide zéro, alors la table ne s'ouvre pas.
  4. Étant donné le nombre 4 saisi, quand on consulte l'addition, alors elle indique 4 personnes.
  5. Étant donné une table ouverte pour 4 personnes sans aucun produit, quand on revient au plan, alors elle apparaît occupée.
  6. (Si REST-06-P2 est retenue.) Étant donné la table 9 libre, quand on y déplace deux produits, alors la caisse demande le nombre de personnes de la table 9.
- **Questions :** Q25, Q29, Q64, Q76.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le nombre de personnes existe sur l'addition (« Convives », `customer_count`). *Il manque :* il n'est pas demandé ; il vaut 1 d'office et la table s'ouvre directement sur l'écran de commande (C18). L'écran pose aussi 1 personne sur une addition sans table, et la remet à chaque chargement ; le serveur accepte 0 (C82, C93) : à changer par REST-06-P2. Pour Odoo, une table n'est occupée que si son addition porte un produit ou a été réservée par le bouton « Réservez la table » : une table ouverte sans produit redevient libre au retour au plan, et son addition, nombre de personnes compris, est jetée (C66 ; à vérifier à l'écran). Quatre chemins ouvrent une addition sans passer par la question : le déplacement vers une table libre, la division (addition « 5B », sans table), le numéro inconnu et le bouton « + » (C32, C33, C17, C82) ; le dernier laisse servir sans table, sans nombre de personnes ni alerte (REST-17, PROF-04). *AITE développe :* la question obligatoire à l'ouverture ; la table réservée dès la validation du nombre ; les cas de REST-06-P2. **Effort : S.**
- *Interne —* **Bonne pratique.** Rendre le nombre de convives obligatoire pour toute nouvelle addition : ce serait une option chez Oracle (attribution incertaine), et Toast demande la taille de la tablée dès que le serveur choisit une table [42°][27°].

#### REST-07 — Le nombre de personnes se corrige en cours de repas

- **Source :** M9 · **Priorité :** Indispensable (« il faut que le système permette qu'on ajoute le nombre de personnes »), bien que le message commence par « si possible » ; sans effet pratique, la fonction existe · **À l'ouverture :** oui.
- **Le client dit :** « Si possible, le système doit donner l'option de pouvoir ajouter le nombre de personnes. […] Après, deux personnes viennent s'ajouter sur eux. Il faut que le système permette qu'on ajoute le nombre de personnes » (M9).
- **Règle de gestion.** Tant que la table est ouverte, on peut ajouter des personnes (M9). **Déduction :** on peut aussi en retirer ; le nombre retenu pour les rapports est celui de l'encaissement de la table. **Proposition (REST-07-P1) :** la caisse refuse zéro personne sur une table qui porte des produits.
- **Critères d'acceptation.**
  1. Étant donné une table ouverte pour 5 personnes, quand deux personnes arrivent et que le serveur saisit 7, alors l'addition indique 7 personnes.
  2. Étant donné cette table encaissée, quand on lit le rapport du jour, alors elle compte pour 7 personnes.
  3. (Si REST-07-P1 est retenue.) Étant donné une table qui porte des produits, quand le serveur saisit zéro personne, alors la caisse refuse.
- **Questions :** Q29.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le bouton « Convives » de l'écran de commande ouvre le clavier « Des convives ? », à tout moment avant le paiement (C18). **Activer.** *Il manque :* le clavier accepte zéro personne sur une table qui porte des produits (C68), ce qui fausse le prix moyen par personne ; le tableau de bord standard écarte ces additions (C55). REST-07-P1 : petit développement, à faire avec REST-06.
- *Interne —* **Bonne pratique.** Une touche « nombre de convives » reste utilisable pendant tout le repas, et la taille de la tablée se corrige depuis le détail de l'addition [42°][27°].

#### REST-08 — Le nom du client ou de la société sur la table

- **Source :** M2 · **Priorité :** Souhaité (« ce serait bien ») · **À l'ouverture :** oui pour un client enregistré ; à confirmer pour un nom libre.
- **Le client dit :** « s'il y aura possibilité d'écrire le nom du client sur la table ou d'écrire le nom d'une société, pendant qu'on ouvre la table, ce serait bien. Ou alors même après » (M2).
- **Règle de gestion.** On peut écrire sur une table le nom d'une personne ou d'une société, pendant qu'on l'ouvre ou plus tard (M2). **Déduction :** ce nom est facultatif. **Proposition (R), option de vente sans table (PROF-04) :** le même nom sert à retrouver l'addition (Q71). **Proposition (REST-08-P1) :** il se lit sur le plan de salle et s'imprime sur l'addition ; pour une vente sans table, aussi sur le bon, avec, en livraison, l'adresse et le téléphone.
- **Critères d'acceptation.**
  1. Étant donné la fenêtre d'ouverture d'une table, quand le serveur y écrit « Société X » en plus du nombre de personnes, alors la table s'ouvre à ce nom ; s'il laisse le nom vide, la table s'ouvre quand même.
  2. Étant donné un nom saisi en cours de repas, quand on rouvre la table, alors le nom est conservé.
  3. (Si REST-08-P1 est retenue.) Étant donné une table au nom de « Société X », quand on regarde le plan de salle et l'addition imprimée, alors ce nom y figure.
  4. Étant donné une table sans nom, quand elle est encaissée, alors rien n'est réclamé.
- **Questions :** Q27, Q71.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le bouton « Client » de l'écran de commande rattache la table à un client enregistré, personne ou société, une fois la table ouverte et à tout moment avant le paiement ; un client peut être créé depuis la caisse (C20). *Il manque :* un simple nom écrit sans créer de fiche, et la saisie du nom pendant l'ouverture même. Le champ existe (« Modifier le nom de la commande ») mais le bouton n'apparaît que pour une addition sans table, et le plan de salle n'affiche que le numéro (C21). *AITE développe :* le nom libre sur une table, saisi dans la fenêtre du nombre de personnes (REST-06) ou plus tard, visible sur le plan et sur l'addition. **Effort : S.** Sur une addition sans table, le nom libre existe déjà ; ni ce nom ni le client ne s'impriment sur le bon ou le ticket (C78, C82, C95 ; lu dans le code). Dans AITE HOUSE, un client enregistré ouvre droit à l'ardoise (partie 5).
- *Interne —* **Bonne pratique.** En service à table, le nom d'addition reste facultatif ; il apparaît dans la liste des additions ouvertes et s'imprime sur le ticket [26°].

### 3.4 Prise de commande

#### REST-09 — L'écran de commande est rangé par familles, sous-familles et sous-sous-familles

- **Source :** M5 · **Priorité :** Indispensable (« l'interface qui va venir doit venir telle que… ») · **À l'ouverture :** oui.
- **Le client dit :** « après l'ouverture de la table, l'interface qui va venir doit venir telle qu'il y a nourriture, il y a boisson. […] quand je clique boisson, je peux être capable de voir alcoolisé, non alcoolisé. Quand je [clique] alcoolisé, je dois voir peut-être bière, vin, whisky » (M5).
- **Règle de gestion.** Après l'ouverture de la table, l'écran propose Nourriture et Boisson. Toucher une famille montre ses sous-familles (Boisson : Alcoolisé, Non alcoolisé) ; toucher une sous-famille montre les suivantes (Alcoolisé : Bière, Vin, Whisky…) (M5). **Déduction :** les produits viennent au dernier niveau. **Déduction, à confirmer (Q31) :** le client décrit un premier écran à deux entrées ; il ne dit pas s'il accepte que des produits s'affichent déjà en dessous. **Déduction, à confirmer (Q32) :** la fin du message, peu audible, demande de pouvoir revenir d'un niveau en arrière. **Déduction (P), à confirmer (Q70) :** le client n'a cité ni pizza, ni petit déjeuner, ni café ; leur place dans cet arbre est à fixer avec lui.
- **Critères d'acceptation.**
  1. Étant donné une table qui vient d'être ouverte, quand l'écran de commande s'affiche, alors il montre Nourriture et Boisson (avec ou sans produits en dessous, selon la réponse à Q31).
  2. Étant donné l'écran de commande d'une table, quand le serveur touche Boisson, alors il voit Alcoolisé et Non alcoolisé.
  3. Étant donné Alcoolisé affiché, quand il touche Bière, alors seules les bières sont proposées.
  4. (Si la réponse à Q32 le confirme.) Étant donné une sous-famille affichée, quand il retouche la famille active, alors il remonte d'un niveau.
  5. Étant donné un produit que le manager range dans « Vin », quand la caisse est rechargée, alors il apparaît sous Boisson, Alcoolisé, Vin.
- **Questions :** Q31, Q32, Q48, Q70.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* les catégories du Point de Vente ont plusieurs niveaux, sans limite de profondeur (Point de Vente → Configuration → « Catégories de produits du PdV », champ « Catégorie parente »). L'écran de commande montre les catégories de premier niveau ; toucher une catégorie affiche ses sous-catégories, et retoucher la catégorie active remonte d'un niveau. Chaque catégorie a une couleur, une image et un rang ; « Limiter les catégories » choisit celles d'une caisse (C22, C23). **Régler :** le travail est la saisie de la carte (familles, produits, prix), à planifier avant l'ouverture ; chaque produit doit avoir une catégorie de caisse, sans quoi le bouton « Commander » ne répond pas (C67). *Écart avec M5, à trancher :* au premier écran, tous les produits s'affichent déjà sous Nourriture et Boisson, et l'écran montre 100 produits au plus (C22). REST-09-P1, si le client veut un premier écran réduit aux deux familles : développement, effort à estimer. *À vérifier à l'écran :* le nombre de touches pour commander une bière, puis une pizza à taille et suppléments ou une formule, qui ouvrent une fenêtre de choix (C77, C80).
- *Interne —* **Bonne pratique.** Trois niveaux au plus : chaque niveau ajoute une touche à chaque produit commandé, et les produits les plus vendus se placent en tête [49°][50°]. L'arbre demandé par le client fait exactement trois niveaux.

### 3.5 Envoi et annulation

#### REST-10 — Une commande envoyée ne se retire plus

- **Source :** M3 · **Priorité :** Indispensable · **À l'ouverture :** à confirmer.
- **Le client dit :** « une fois que les commandes sont rentrées et qu'on a envoyées, elles ne peuvent plus être enlevées » (M3).
- **Règle de gestion.** Dès qu'un produit est envoyé, personne ne peut plus le retirer sans le code d'un supérieur (M3, REST-11). **Déduction :** tant qu'un produit n'est pas envoyé, le serveur le corrige librement ; le client ne parle que des commandes « envoyées ». **Déduction :** baisser la quantité d'un produit envoyé, c'est en retirer une partie, et annuler la table entière, c'est retirer tout ce qui a été envoyé : la même règle s'applique, pour tous les produits, quelle que soit leur famille. **Déduction :** un déplacement (division, transfert, réunion de tables) ne retire rien, le produit passe d'une addition à une autre : le verrou ne s'y oppose pas. **Proposition (REST-10-P1) :** la règle vaut aussi pour le remboursement d'une addition payée, pour toute modification après l'impression de l'addition et pour les tables encore ouvertes au moment de fermer la caisse (Q37).
- **Critères d'acceptation.**
  1. Étant donné un produit saisi mais pas envoyé, quand le serveur le retire, alors il disparaît sans code.
  2. Étant donné un produit envoyé, quand le serveur tente de le retirer ou d'en baisser la quantité, alors la caisse refuse et demande le code d'un supérieur.
  3. Étant donné trois bières envoyées et une quatrième seulement saisie, quand le serveur retire la quatrième, alors c'est permis et les trois autres restent.
  4. Étant donné un produit d'une famille sans poste de préparation, quand il a été envoyé, alors il est verrouillé comme les autres.
  5. Étant donné un produit envoyé depuis un poste, quand un serveur tente de le retirer depuis un autre poste, ou après avoir rechargé la page, alors la caisse refuse de la même façon.
  6. Étant donné une table qui porte des produits envoyés, quand un serveur tente de l'annuler en entier, depuis l'écran de commande ou depuis la liste des additions, alors la caisse demande le code d'un supérieur.
  7. Étant donné un produit envoyé, quand un serveur cherche à le ramener à zéro par une remise, alors aucune remise ne lui est proposée (les remises sont désactivées à l'ouverture, partie 4.2).
  8. Étant donné des produits envoyés, quand on divise l'addition ou qu'on déplace ces produits vers une autre table, alors le verrou ne s'y oppose pas.
  9. (Si REST-10-P1 est retenue.) Étant donné des tables encore ouvertes, quand on ferme la caisse, alors elles ne peuvent être annulées qu'avec le code d'un supérieur, et chaque annulation laisse sa trace.
- **Questions :** Q6, Q34, Q37.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* l'envoi. Le bouton « Commander » envoie ce qui a changé depuis le dernier envoi, et l'addition retient les quantités envoyées (`last_order_preparation_change`) ; le réglage « Imprimantes de préparation » imprime les bons par poste (C24). Pour ce profil : une imprimante par poste de préparation (PROF-05) ; chaque produit d'une formule part vers le sien (C80 ; lu dans le code). *Il manque :* le verrou. Tout employé peut diminuer ou supprimer un produit déjà envoyé ; la cuisine reçoit seulement un bon d'annulation. Un point d'accroche existe dans le code, mais il ne fait pas ce que REST-10 demande : il compare à une quantité gardée en mémoire du poste, qui repart de zéro au rechargement de la page et que les autres postes ne connaissent pas ; sous cette quantité, il ne refuse pas, il crée une ligne négative de compensation, sans code ; et il ne couvre que le pavé numérique (C25). Restent ouverts : « Annuler la commande », la corbeille de la liste des commandes, « Annuler les commandes » à la fermeture, la division et le transfert (qui suppriment ou diminuent des lignes envoyées), la remise de 100 % (touche % active par défaut), et le système central, qui accepte toute suppression de ligne venant du compte de la caisse (C60, C13). Deux limites de l'envoi lui-même : quand des imprimantes de préparation sont réglées avec leurs familles, seuls les produits de ces familles comptent comme « à envoyer » ; et sans bon imprimé, l'envoi n'est enregistré sur le système central qu'au retour au plan de salle, donc invisible des autres postes d'ici là (C67 ; lu dans le code, non essayé à l'écran). *AITE développe :* le verrou des produits envoyés, fondé sur les quantités envoyées enregistrées sur l'addition et non sur la mémoire du poste ; il couvre tous les chemins de retrait listés ci-dessus et tous les produits ; l'envoi est enregistré sur le système central dès le geste « Commander », bon imprimé ou non. **Effort : M**, à concevoir avec REST-11 et REST-12, et avec REST-13, 14 et 15 pour distinguer le retrait du déplacement. REST-10-P1 : compris dans cet effort pour la fermeture avec des tables ouvertes ; pour le remboursement, le tableau des droits de REST-03 dit déjà qui rembourse, et le code d'un supérieur avec explication reste à estimer, comme la modification après impression.
- *Interne —* **Bonne pratique.** Deux gestes distincts : retirer un produit pas encore envoyé (libre, c'est une erreur de saisie) et annuler un produit envoyé (droit réservé) ; la cuisine ou le bar est prévenu de l'annulation [21°][25°].

#### REST-11 — L'annulation passe par le code d'un supérieur

- **Source :** M3, M10 · **Priorité :** Indispensable · **À l'ouverture :** à confirmer.
- **Le client dit :** « Il faudrait juste un code du grade supérieur, c'est-à-dire un truc hiérarchique, [pour] pouvoir annuler » (M3) ; « le chef de salle ou les superviseurs qui sont au-dessus, qui peuvent prendre la décision d'annuler ou de ne pas annuler » (M10).
- **Règle de gestion.** Pour annuler un produit envoyé, il faut le code d'un supérieur (M3). Les chefs de salle et les superviseurs décident d'annuler ou non (M10). **Déduction :** le manager, au-dessus d'eux, le peut aussi. **Déduction, à confirmer (Q21) :** la caissière, citée après le serveur, n'annule pas ce qu'un serveur a envoyé. **Proposition (REST-11-P1) :** le supérieur tape son code sur le poste du serveur, qui reste identifié ; l'annulation est enregistrée au nom du supérieur, avec le nom du serveur qui l'a demandée.
- **Critères d'acceptation.**
  1. Étant donné un produit envoyé, quand un superviseur tape son code, alors le produit est annulé et la cuisine ou le bar reçoit un bon d'annulation.
  2. (Si REST-11-P1 est retenue.) Étant donné cette annulation, quand elle est faite, alors le serveur reste identifié sur le poste.
  3. (Selon le tableau validé.) Étant donné la demande de code, quand le code tapé est celui d'un serveur ou d'une caissière, alors l'annulation est refusée.
  4. Étant donné une annulation faite, quand on consulte sa trace (REST-12), alors elle indique le serveur qui a demandé et le supérieur qui a autorisé.
- **Questions :** Q18, Q21, Q37.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* rien de tel. Aucun geste de la caisse ne demande le code d'une autre personne ; le supérieur doit prendre la caisse à son nom (« Changer de caissier »), agir, puis la rendre (C26). « Annuler la commande » et « Remboursement » sont ouverts à tout employé (C12, C28, C29). *AITE développe :* la fenêtre « Code du supérieur », qui autorise le geste sans changer d'utilisateur ; le code est vérifié et l'annulation enregistrée par le système central, et non par le seul poste (C3, C13). **Effort : M.** *Repli, si la date d'ouverture est proche :* le verrou de REST-10 appliqué par niveau, le supérieur passant par « Changer de caissier », déjà dans Odoo (C26), en attendant la fenêtre. À noter : un utilisateur d'Odoo rapporte sur le forum qu'on ne peut pas retirer la suppression aux serveurs par les droits d'accès [60°], et des extensions payantes de la boutique Odoo proposent une validation par le code d'un responsable [62°] (pages non ouvertes).
- *Interne —* **Bonne pratique.** Quand l'employé n'a pas le droit d'annuler, la caisse demande le code ou la carte d'un responsable [21°]. Pour les supérieurs, un badge vaut mieux qu'un code, qu'un employé peut retenir en le voyant taper [45°].

#### REST-12 — Chaque annulation est expliquée et laisse une trace

- **Source :** M10, M7, M1 · **Priorité :** Indispensable pour la trace et le rapport (M1, M7) ; le journal non modifiable et le motif obligatoire sont des propositions d'AITE, à trancher · **À l'ouverture :** à confirmer.
- **Le client dit :** les superviseurs « peuvent prendre la décision d'annuler ou de ne pas annuler parce qu'ils vont expliquer dans leur rapport » (M10) ; « Les rapports d'annulation » (M7) ; « Que les transactions gardent le code de l'utilisateur » (M1).
- **Règle de gestion.** Le supérieur qui annule en répond : il s'en explique dans son rapport (M10). Le client veut un rapport des annulations (M7) et que chaque opération garde le code de son auteur (M1). **Déduction, à confirmer (Q9) :** « leur rapport » peut être un compte rendu que le supérieur fait lui-même en fin de service, hors de la caisse, ou une liste que la caisse sort à son nom. **Déduction :** la trace distingue l'annulation (le produit quitte toutes les additions) du déplacement (il passe d'une addition à une autre) ; divisions, transferts et réunions de tables n'y figurent pas comme des annulations. **Proposition (REST-12-P1) :** chaque annulation laisse dans la caisse une ligne que personne ne peut modifier ni effacer : date et heure, table, produit, quantité, montant, serveur, supérieur, explication. **Proposition (REST-12-P2) :** l'explication est saisie au moment de l'annulation, par un motif obligatoire choisi dans une liste que le manager peut modifier (erreur de saisie, client parti, plat refusé, produit manquant, autre), avec un commentaire libre ; c'est le moyen de ne pas reconstituer le rapport de mémoire en fin de service.
- **Critères d'acceptation.**
  1. Étant donné une annulation faite, quand le manager consulte les annulations, alors il lit la date, l'heure, la table, le produit, la quantité, le montant, le serveur et le supérieur.
  2. Étant donné une division, un transfert ou une réunion de tables, quand on consulte les annulations, alors aucune ligne n'y a été ajoutée.
  3. (Si REST-12-P1 est retenue.) Étant donné une ligne du journal, quand un utilisateur, quel que soit son niveau, tente de la modifier ou de la supprimer, alors c'est refusé.
  4. (Si REST-12-P2 est retenue.) Étant donné un superviseur qui annule, quand il ne choisit pas de motif, alors l'annulation ne se fait pas ; quand il en choisit un, le motif figure sur la ligne.
  5. (Si REST-12-P2 est retenue.) Étant donné le manager, quand il ajoute un motif à la liste, alors ce motif est proposé à l'annulation suivante.
- **Questions :** Q9, Q35, Q36.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le réglage « Suivi des modifications de commandes », désactivé par défaut. Quand une quantité baisse ou qu'une ligne est supprimée, il écrit une note dans l'historique de l'addition, marque la ligne et l'addition comme « modifiées » et récapitule les additions modifiées dans l'historique de la session à la fermeture (C27, C73). C'est insuffisant : pas de motif, auteur incertain, pas de total, note visible des seuls administrateurs ; et il ne distingue pas un retrait d'un déplacement : une baisse de quantité comme en produit une division y est notée « Quantité commandée : 3.0→2 » (exécuté côté serveur). Une table annulée en entier reste consultable à l'état « Annulé », sans motif ni auteur, si son addition avait déjà été enregistrée sur le système central ; sinon elle disparaît sans trace (C28, C73). *Réglage proposé dès l'ouverture :* cocher ce suivi, comme filet en attendant le journal d'AITE, en sachant que divisions et transferts y apparaissent aussi. *AITE développe :* la trace des annulations, en journal non modifiable (REST-12-P1), et la liste des motifs (REST-12-P2). **Effort : M.**
- *Interne —* **Bonne pratique.** Un motif obligatoire à chaque annulation, choisi dans une liste paramétrable, et l'accord d'un responsable [21°][34°][44°].

### 3.6 Gestion des tables

#### REST-13 — Réunir des tables

- **Source :** M4 · **Priorité :** Souhaité (« si c'est possible, ce sera bien ») · **À l'ouverture :** oui.
- **Le client dit :** « la fonctionnalité d'ajouter les tables ensemble, diviser les tables en deux, que j'ai déjà précisé » (M4).
- **Règle de gestion.** On peut réunir des tables (M4). **Déduction, à confirmer (Q10) :** deux tables occupées ne font plus qu'une addition, qui porte les produits des deux ; le client dit avoir « déjà précisé » ce point, et nous n'avons pas cette précision. **Propositions :** ce qui a déjà été envoyé ne repart pas en cuisine ; les personnes des deux tables s'additionnent (Q29).
- **Critères d'acceptation.**
  1. Étant donné les tables 4 et 5 occupées, quand on les réunit, alors une seule addition porte tous leurs produits.
  2. (Proposition.) Étant donné des produits déjà envoyés sur ces tables, quand on les réunit, alors aucun bon n'est renvoyé en cuisine pour ces produits.
  3. Étant donné une réunion de tables, quand on lit le rapport des annulations, alors aucune annulation n'y apparaît.
  4. (Selon la réponse à Q29.) Étant donné une table de 3 personnes et une table de 4, quand on les réunit, alors l'addition compte 7 personnes.
- **Questions :** Q10, Q19, Q29.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* depuis l'écran de commande, Actions → « Transférer / Fusionner », puis on touche la table occupée (C32) ; ou bien, sur le plan, on glisse une table sur une autre, et l'addition s'appelle alors « 4 & 5 » (C31). **Activer.** Limites lues dans le code, *à vérifier* : réunir en glissant écrit sur la fiche des tables, ce qui exige que le compte de la caisse soit Administrateur du Point de Vente (écriture refusée à un compte « Utilisateur » : exécuté côté serveur) ; sinon, passer par « Transférer / Fusionner », qui n'écrit pas sur les tables (C61 ; à essayer) ; le message affiché pendant le glisser (« Link Table ») n'est pas traduit (C31) ; les personnes des deux tables ne sont pas additionnées (C19) ; l'addition absorbée reste dans les listes à l'état « Annulé » et doit être écartée du rapport des annulations (C32).
- *Interne —* **Bonne pratique.** La documentation d'Odoo décrit la fusion par Actions puis « Transférer / Fusionner » [1] ; le glisser d'une table sur une autre se lit dans le code (C31), pas dans la documentation. Chez Square, glisser une table sur une table occupée propose la fusion [36°]. Un défaut corrigé en version 19 faisait renvoyer en cuisine, après une fusion, des produits déjà envoyés [18] : le cas est à jouer en recette sur la version livrée.

#### REST-14 — Diviser une table

- **Source :** M4 · **Priorité :** Souhaité · **À l'ouverture :** oui, si la division se fait par produits.
- **Le client dit :** « diviser les tables en deux, que j'ai déjà précisé » (M4).
- **Règle de gestion.** On peut diviser une table en deux (M4). **Déduction, à confirmer (Q10) :** diviser, c'est sortir une partie des produits vers une seconde addition, encaissée à part. Deux autres lectures sont possibles : couper le total en deux parts égales (REST-14-P1), ou séparer deux tables qu'on avait réunies. Le client dit l'avoir « déjà précisé » ; nous n'avons pas cette précision.
- **Critères d'acceptation.**
  1. (Si la division se fait par produits.) Étant donné la table 5 avec six produits, quand le serveur en choisit deux et divise, alors une addition « 5B » porte ces deux produits et la table 5 garde les quatre autres.
  2. Étant donné des produits déjà envoyés, quand on divise, alors aucun bon n'est renvoyé en cuisine et aucune ligne n'apparaît dans le rapport des annulations.
  3. Étant donné l'addition « 5B » encaissée, quand on revient à la table 5, alors elle est toujours ouverte avec ses quatre produits.
  4. (Si REST-14-P1 est retenue.) Étant donné une addition de 30 000 FCFA, quand on la divise en deux parts égales, alors deux paiements de 15 000 FCFA la soldent.
- **Questions :** Q10, Q29.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le réglage « Autoriser le partage d'addition », coché d'office à la création d'une caisse de restaurant, mais pas quand on passe une caisse existante en mode restaurant (C33, C59). Actions → « Fractionner » : on touche les produits à sortir, puis « Diviser la commande » ; ils partent dans une nouvelle addition nommée d'après la table, « 5B », « 5C »… (C33). **Activer**, si la division se fait par produits. Limites : il faut au moins deux unités sur la table ; pas de division du total en parts égales (REST-14-P1 : développement, effort à estimer) ; la division fait passer une personne de l'addition d'origine à la nouvelle (le total est conservé, sauf pour une table d'une seule personne, qui tombe à zéro), et la nouvelle addition n'est rattachée à aucune table (C19, C33). *À vérifier :* la documentation dit que la seconde addition doit être payée avant de revenir à la première [1] ; ce point n'a pas été contrôlé dans le code.
- *Interne —* **Bonne pratique.** La division se fait produit par produit [37°].

#### REST-15 — Déplacer un produit vers une autre table, existante ou nouvelle

- **Source :** M4 · **Priorité :** Souhaité · **À l'ouverture :** oui, en deux gestes (à vérifier).
- **Le client dit :** « prendre un produit d'une table [et l'ajouter] sur une autre table existante, retirer un produit et créer une nouvelle table avec » (M4).
- **Règle de gestion.** Un produit d'une table peut être déplacé vers une autre table déjà ouverte, ou retiré pour créer une nouvelle table (M4). **Déduction :** déplacé vers une table occupée, il s'ajoute à son addition ; le message cite deux fois ce déplacement, et nous y lisons un seul geste (Q30). **Déduction, à confirmer (Q26) :** « créer une nouvelle table » peut désigner une table libre du plan, une addition à part sur la même table (« 5B », déjà possible en un geste par la division), ou une table qui n'est pas sur le plan. **Proposition (REST-15-P1) :** un seul geste, « Déplacer vers la table… ». **Proposition (REST-15-P2) :** garder la trace de chaque déplacement (produit, table de départ, table d'arrivée, auteur, heure) et demander le code d'un supérieur pour modifier la table d'un collègue.
- **Critères d'acceptation.**
  1. Étant donné les tables 3 et 7 occupées, quand le serveur déplace une bière de la 3 vers la 7, alors la bière figure sur l'addition de la 7 et plus sur celle de la 3.
  2. (Selon la réponse à Q26.) Étant donné la table 9 libre, quand il y déplace deux produits de la table 3, alors la table 9 devient occupée avec ces deux produits.
  3. Étant donné des produits déjà envoyés, quand on les déplace, alors aucun bon n'est renvoyé en cuisine et aucune ligne n'apparaît dans le rapport des annulations.
  4. (Si REST-15-P2 est retenue.) Étant donné un déplacement, quand le manager consulte la trace, alors il y lit le produit, les deux tables, l'auteur et l'heure.
- **Questions :** Q19, Q25, Q26, Q28, Q30.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* pas de geste direct, mais deux gestes à la suite. D'abord « Fractionner », qui sort les produits dans une addition « 5B » ; puis, sur cette addition, « Transférer / Fusionner », et l'on touche la table voulue : libre, l'addition s'y installe ; occupée, les produits s'ajoutent à la sienne (C33, C32). **Activer**, mais cet enchaînement est déduit du code : *à vérifier* à l'écran avant de le promettre. Chaque déplacement en deux gestes vers une table occupée laisse une addition « 5B » à l'état « Annulé », à écarter du rapport des annulations (C32). Pour une table hors plan : le sélecteur de table ouvre une addition au nom d'un numéro inconnu (C17). REST-15-P1 : un bouton « Déplacer vers la table… » sur l'écran de division (C34). **Effort : M. À trancher.** REST-15-P2 : aujourd'hui un déplacement ne laisse aucune trace et n'est lié à aucun niveau (C32). **Effort : S.**
- *Interne —* **Bonne pratique.** Déplacer un produit vers une nouvelle addition ou vers une addition existante fait partie des gestes courants d'une caisse de restaurant [36°][28°]. Ces déplacements doivent laisser une trace : ils servent à une fraude connue, qui consiste à encaisser en espèces puis à déplacer les produits de l'addition vers d'autres tables [47°].

### 3.7 Plan de salle et alertes

#### REST-16 — Le plan de salle est visible

- **Source :** M11 · **Priorité :** Indispensable · **À l'ouverture :** oui.
- **Le client dit :** « Le plan de salle doit être visible dans le système et les tables doivent avoir des couleurs » (M11).
- **Règle de gestion.** Le plan de salle est visible dans la caisse (M11). **Déduction :** chaque table y est à sa place, avec son numéro, et l'on distingue d'un coup d'œil les tables libres des tables ouvertes. **Proposition :** la caisse s'ouvre sur ce plan. **Proposition (REST-16-P1) :** chaque table ouverte affiche, en plus de son numéro, la durée et le nombre de personnes et, au choix, le montant, le nom du serveur ou le nom du client (Q40).
- **Critères d'acceptation.**
  1. Étant donné une salle dessinée, quand un serveur s'identifie, alors le plan s'affiche avec toutes les tables et leurs numéros.
  2. Étant donné une table ouverte pour 4 personnes sans aucun produit, quand on revient au plan, alors elle se distingue des tables libres.
  3. (Selon le tableau validé.) Étant donné un serveur, quand il cherche à modifier le plan, alors ce geste ne lui est pas proposé.
  4. (Si REST-16-P1 est retenue.) Étant donné une table ouverte pour 4 personnes depuis 40 minutes, quand on regarde le plan, alors on lit sur la table « 4 pers. » et « 40 min ».
- **Questions :** Q2, Q40.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* les salles et les tables (numéro, forme, places, couleur), le plan comme écran d'accueil de la caisse de restaurant, son dessin depuis la caisse (« Modifier le plan », réservé aux droits avancés) ou depuis Configuration → « Plans de salle », et une vue en grille (« Changer de vue de salle ») (C35, C11). **Régler :** dessiner les salles du client. Réserves : « Modifier le plan » depuis la caisse écrit sur les tables et exige, comme la réunion par glisser, que le compte de la caisse soit Administrateur du Point de Vente (C61 ; à vérifier) ; une table ouverte sans produit n'apparaît occupée qu'avec le développement de REST-06 (C66) ; après 5 minutes sans toucher l'écran, un écran de veille remplace le plan (C65 ; voir REST-17). *Il manque,* sans que le client l'ait demandé : la table n'affiche que son numéro et une pastille (nombre de produits pas encore envoyés) ; ni montant, ni nombre de personnes, ni durée, ni nom du serveur (C36). REST-16-P1 : effort à estimer ; la durée est déjà comptée dans REST-17.
- *Interne —* **Bonne pratique.** Le plan de salle montre l'état des tables en temps réel [1] ; chez d'autres éditeurs, chaque table occupée affiche en plus le nombre de personnes, le serveur, le total et le temps écoulé [23°].

#### REST-17 — La table est verte à l'ouverture, orange après un délai

- **Source :** M11 · **Priorité :** Indispensable (« les tables doivent avoir des couleurs ») · **À l'ouverture :** à confirmer.
- **Le client dit :** « quand une table est ouverte, par exemple, elle est verte ; quand une table a dépassé une heure de temps, elle passe à l'orange. […] Il faudrait qu'on se rappelle avant le temps qu'un client devait mettre normalement. Si un client met une heure de temps ou deux heures de temps, il faut… à une heure ou une heure trente que ça signale déjà à l'orange par exemple » (M11).
- **Règle de gestion.** Les tables ont des couleurs. Une table ouverte est, par exemple, verte ; passé un délai, elle passe, par exemple, à l'orange : c'est le signal pour demander au serveur si le client veut l'addition. L'alerte doit venir avant la durée normale d'un repas : le client cite une heure, ou une heure trente, pour un repas d'une à deux heures (M11). Le délai et les couleurs sont à fixer avec lui (Q11, Q38). **Déduction (P), à confirmer (Q38) :** un café, un petit déjeuner et un dîner n'occupent pas une table le même temps ; faute de réponse, un seul délai (PROF-06). **Déduction :** le délai se compte depuis l'ouverture de la table (REST-06) ; il reste compté depuis la première ouverture quand la table est transférée, divisée ou réunie. **Propositions :** le délai se règle par caisse, avec une phrase qui dit ce qui va se passer ; la durée écoulée s'écrit sur la table, pour ne pas dépendre de la seule couleur ; la couleur des tables n'est plus un choix de dessin, elle est réservée à l'alerte ; sur un poste laissé seul, le plan et ses couleurs restent affichés. **Proposition (REST-17-P1) :** un second palier, rouge, quand la durée normale du repas est dépassée. **Proposition (REST-17-P2) :** le serveur peut remettre l'alerte à zéro quand il a vérifié que le client reste.
- **Critères d'acceptation.**
  1. Étant donné un délai réglé à 60 minutes, quand une table est ouverte depuis 59 minutes, alors elle est verte ; à 60 minutes révolues, et au plus tard à 61 minutes, elle est orange, sans que personne n'ait touché l'écran.
  2. Étant donné un poste laissé 10 minutes sans y toucher, quand on le regarde, alors le plan et ses couleurs sont toujours affichés.
  3. Étant donné une table orange, quand elle est encaissée, alors elle redevient libre.
  4. Étant donné le manager qui porte le délai à 90 minutes, quand la caisse est rouverte, alors le nouveau délai s'applique.
  5. Étant donné une table ouverte depuis 50 minutes, quand on la transfère, la divise ou la réunit, alors la durée reste comptée depuis la première ouverture.
  6. (Proposition.) Étant donné une table ouverte depuis 40 minutes, quand on regarde le plan, alors « 40 min » se lit sur la table.
- **Questions :** Q11, Q38, Q39, Q41.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* une table occupée prend sa couleur, verte par défaut ; une table libre est grisée. « Verte à l'ouverture » est donc acquis si l'on laisse les tables en vert (C36) et si la table est tenue pour occupée dès son ouverture (REST-06). *Il manque :* toute notion de durée sur le plan de salle ; la donnée de départ existe (l'heure de création de l'addition), mais une addition née d'une division est une addition neuve (C37, C33). Et après 5 minutes sans toucher l'écran, la caisse remplace tout écran, sauf celui du paiement, par un écran de veille (heure et logo) : sur un poste laissé seul, le plan coloré n'est plus visible (C65). *AITE développe :* le délai réglable, la couleur recalculée chaque minute, la durée affichée, l'heure de première ouverture conservée et, sur les caisses de restaurant, l'écran de veille désactivé ou remplacé par le plan de salle. **Effort : M**, ces points compris. REST-17-P1 et REST-17-P2 : effort à estimer. Une addition sans table n'est pas sur le plan : ni couleur ni alerte, seulement un onglet sans durée (C87 ; PROF-07) ; option ouverte, y mettre la durée (PROF-04). À noter : sur la boutique Odoo, des extensions affichent la durée sur la table, mais aucune fiche repérée ne décrit un seuil de couleur réglable [63°] (pages non ouvertes).
- *Interne —* **Bonne pratique.** Afficher le temps écoulé depuis l'ouverture de l'addition et changer de couleur à deux seuils réglables, comme Square (jaune, puis rouge) et Lightspeed (bande rouge sous la durée) [35°][41°]. Resy, outil de réservation, règle la durée d'une table par service [79°] ; en faire le seuil de l'alerte est une déduction.

### 3.8 Stock

#### REST-18 — Le stock que l'on a s'enregistre, même pour les petites quantités

- **Source :** M6 · **Priorité :** Indispensable (classement d'AITE : « on va pouvoir entrer… », dit sans réserve) · **À l'ouverture :** oui.
- **Le client dit :** « au niveau des entrées, on va pouvoir entrer les quantités des stocks qu'on a. Quand on a des trucs de petite quantité, on met quand même le stock qu'on a. On enregistre quand même le stock qu'on a » (M6).
- **Règle de gestion.** On saisit dans le système la quantité que l'on a de chaque produit, y compris ceux dont on a peu (M6). **Déduction :** il s'agit du stock de départ, puis de chaque arrivée. **Déduction, à confirmer (Q42) :** les « trucs de petite quantité » peuvent être les produits dont on a peu d'unités, les petits achats faits sans bon de commande, ou les ingrédients utilisés à petite dose (M8 emploie « petites quantités » en ce sens). **Proposition :** chaque saisie garde sa date et son auteur. **Proposition (REST-18-P1) :** un écran d'entrée rapide (produit, quantité, unité) pour les petits achats.
- **Critères d'acceptation.**
  1. Étant donné un produit suivi dont le stock est nul, quand on enregistre que l'on en a 24 bouteilles, alors le stock vaut 24.
  2. (Proposition.) Étant donné cette saisie, quand on consulte les mouvements de stock, alors elle est datée et porte le nom de celui qui l'a faite.
  3. (Selon la réponse à Q42 ; si REST-18-P1 est retenue.) Étant donné un petit achat de 3 unités sans bon de commande, quand il est saisi, alors le stock augmente de 3.
  4. Étant donné les saisies de la semaine, quand le manager consulte les mouvements de stock, alors il retrouve chacune d'elles.
- **Questions :** Q7, Q42, Q43.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* l'application Inventaire, installée avec le Point de Vente : les réceptions, l'« Inventaire physique » et le bouton « Mettre la quantité à jour » de la fiche produit. Le produit doit avoir la case « Suivre l'inventaire » cochée (C38). **Activer.** *AITE HOUSE fait déjà :* le tableau de bord du stock (ruptures, couverture, quantité à commander). *Il manque :* ce tableau de bord ne compte comme « entrées » que les réceptions d'un fournisseur ; une quantité saisie par simple correction d'inventaire y est classée comme un écart (H12). REST-18-P1 : **Effort : S.**
- *Interne —* **Bonne pratique.** Enregistrer chaque entrée à la réception, après avoir rapproché la livraison du bon de commande et de la facture, et compté ou pesé [51°]. Dans Odoo, les quantités se saisissent et se corrigent dans l'inventaire physique [7].

#### REST-19 — La vente est refusée quand le stock est épuisé

- **Source :** M6 · **Priorité :** Indispensable · **À l'ouverture :** à confirmer.
- **Le client dit :** « pendant qu'on vend, si ça finit, que le système ne prenne même pas » (M6).
- **Règle de gestion.** Quand un produit est épuisé, la caisse refuse de le prendre (M6). **Déduction :** elle le dit clairement au serveur ; seuls les produits dont le stock est saisi sont concernés (Q12) : un produit non suivi, par exemple un plat sans fiche technique, n'est pas bloqué. **Proposition (P), à confirmer (Q12) :** une pizza, un café, un petit déjeuner sont faits d'ingrédients ; sans stock saisi ni fiche technique, la caisse ne les refuse pas : le refus à zéro commence par les produits vendus à l'unité, comme les boissons en bouteille. Le besoin se découpe en quatre volets :
  - **19a — Refus à zéro (M6).** Un produit suivi dont le stock enregistré est nul ne peut plus être ajouté à une table ; dès qu'une entrée de stock est saisie, il redevient vendable sans fermer la caisse.
  - **19b — Proposition : décompte dès l'envoi.** Ce qui reste se calcule en retirant du stock les quantités envoyées sur les tables encore ouvertes, sur tous les postes (Q46). Si deux serveurs ont saisi la dernière unité sans l'avoir envoyée, c'est le second envoi qui est refusé. Une quantité envoyée puis annulée redevient disponible, sauf si l'explication dit que le produit est perdu (Q36).
  - **19c — Proposition : quantité restante affichée** sur le bouton du produit.
  - **19d — Proposition : passage en force.** Un supérieur peut forcer la vente avec son code quand le stock enregistré est faux ; ce passage en force laisse une trace (Q44).
- **Critères d'acceptation.**
  1. (19a.) Étant donné un produit suivi dont le stock enregistré est nul, quand un serveur tente de l'ajouter à une table, alors la caisse refuse avec le message « Produit épuisé ».
  2. (19a.) Étant donné un produit épuisé, quand une entrée de stock est enregistrée, alors il redevient vendable en moins d'une minute (seuil proposé), sans recharger la caisse.
  3. (19a.) Étant donné un plat non suivi en stock, quand le serveur l'ajoute, alors la vente passe.
  4. (19b, si retenu.) Étant donné un produit suivi dont il reste 2 unités, quand ces 2 unités ont été envoyées sur une table pas encore encaissée, alors un nouvel ajout sur un autre poste est refusé, au plus tard une minute après l'envoi (seuil proposé).
  5. (19b, si retenu.) Étant donné une seule unité restante, saisie sur deux tables mais pas encore envoyée, quand la seconde table envoie, alors l'envoi de ce produit est refusé.
  6. (19b, si retenu ; selon la réponse à Q36.) Étant donné un produit envoyé puis annulé avec l'explication « erreur de saisie », quand on regarde ce qui reste, alors la quantité est redevenue disponible.
  7. (19c, si retenu.) Étant donné un produit suivi dont il reste 5 unités, quand on regarde son bouton, alors on y lit 5.
  8. (19d, si retenu.) Étant donné un produit épuisé à l'écran mais présent au bar, quand un supérieur tape son code, alors la vente passe et le passage en force est enregistré.
- **Questions :** Q12, Q43, Q44, Q45, Q46, Q59.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* rien pour ce besoin. La caisse ne consulte pas le stock quand on ajoute un produit ; le stock ne baisse qu'au paiement (ou à la fermeture de la caisse), donc pas pour les tables encore ouvertes ; il peut devenir négatif (C39, C40). Le stock ne se lit qu'à la demande, dans la fiche d'information du produit (C41). *AITE développe,* en quatre volets : 19a, le refus à zéro d'après le stock enregistré, pour les boissons vendues à l'unité d'abord (**Effort : M**) ; 19b, le décompte dès l'envoi, partagé entre les postes (**M**) ; 19c, la quantité restante sur le bouton (**S**) ; 19d, le passage en force tracé, avec la fenêtre de REST-11 (**S**). L'ensemble avait été estimé **L** ; la répartition par volet est une estimation à confirmer. Conditions de 19a : le stock de départ saisi avant le premier jour (sans lui, la caisse refuse toutes les ventes des produits suivis) et, pour les boissons servies au verre, le nombre de doses par bouteille (Q45). Pour ce profil : le stock d'une pizza ou d'un café à fiche technique se lit sur ses ingrédients (C79, C86). Des modules libres font une partie de ce travail ([13], licence différente de la nôtre ; partie 5.6). À noter : sur le forum d'Odoo, un utilisateur constate qu'Odoo laisse vendre sans limite [61°] (page non ouverte).
- *Interne —* **Bonne pratique.** Trois états par article : disponible, quantité restante affichée sur le bouton, épuisé (bouton grisé). Le compteur baisse quand la commande part en cuisine, et l'article passe seul à « épuisé » à zéro [30°][39°]. Ne bloquer que les articles dont le stock est réellement tenu : un stock enregistré faux refuse une vente alors que la bouteille est sur l'étagère [40°].

### 3.9 Fiches techniques et rentabilité

#### REST-20 — Les fiches techniques se remplissent peu à peu

- **Source :** M8 (début du message peu audible) · **Priorité :** Plus tard pour le contenu (« pour le futur, on pourra remplir progressivement ») ; fonction disponible à l'ouverture ou plus tard : à trancher (Q13) · **À l'ouverture :** contenu : non ; fonction : à confirmer.
- **Le client dit :** « [Aussi, c'est vrai que les fiches techniques, je ne crois pas] que ce sera prêt avant l'ouverture pour qu'on remplisse les petites quantités pour pouvoir calculer la profitabilité. Mais si la fonction [est là], pour le futur, on pourra remplir progressivement » (M8).
- **Règle de gestion.** Les fiches techniques ne seront pas prêtes pour l'ouverture ; si la fonction est là, on les remplira peu à peu (M8). **Déduction, à confirmer (Q13) :** le début du message est peu audible ; nous comprenons qu'il s'agit des fiches techniques, c'est-à-dire des recettes avec la quantité de chaque ingrédient par portion. Le client distingue le contenu, qui viendra plus tard, et la fonction, qu'il peut attendre, vide, dès l'ouverture. **Déduction :** la fiche est facultative ; un plat sans fiche se vend normalement ; les fiches se créent une à une. **Proposition (REST-20-P1) :** un écran « Fiche technique » dans les mots de la cuisine (grammage, coût de la portion).
- **Critères d'acceptation.**
  1. Étant donné un plat sans fiche technique, quand il est vendu, alors la vente passe et aucun ingrédient ne sort du stock.
  2. Étant donné un plat dont la fiche prévoit 200 g de poulet, quand trois plats sont vendus et encaissés, alors le stock de poulet baisse de 600 g.
  3. Étant donné une fiche créée aujourd'hui, quand on relit les ventes d'hier, alors les quantités, les montants et les sorties de stock d'hier n'ont pas changé.
- **Questions :** Q13, Q63.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* l'application Fabrication (`mrp`) fournit les « Nomenclatures » ; avec le « Type de nomenclature » « Kit », la vente d'un plat en caisse fait sortir ses ingrédients du stock : l'éclatement est fait par `mrp`, et `pos_mrp`, installé seul avec Fabrication, ajuste le coût (C42). Condition : le plat est un produit de type « Biens » ; les lignes d'un autre type ne créent aucun mouvement de stock. Rien n'oblige à avoir une fiche pour vendre. **Activer.** Exécuté côté serveur le 12/11/2026 (trois plats payés : le poulet et le riz passent de 10 à 7) ; à rejouer depuis l'écran de caisse. Pour ce profil (exécuté côté serveur, essais S1 et S6 ; écran non vu) : une seule fiche par pizza, à lignes limitées à une taille ou à un supplément (C79 ; la documentation ne décrit ce réglage que pour des variantes [66]) ; même mécanisme pour le café et l'alcool à la dose (C86 ; PROF-07). *Il manque :* un écran pensé pour une cuisine ; celui d'Odoo est un écran d'atelier. REST-20-P1, le moment venu : **Effort : M.** À dire au client : les ingrédients ne sortent du stock qu'à partir du jour où la fiche existe. Si le client veut la fonction dès l'ouverture, l'installation de Fabrication, sans fiche, passe au lot 1.
- *Interne —* **Bonne pratique.** Commencer par les cinq à dix plats les plus vendus [56°] ; ne laisser une fiche déduire le stock que lorsqu'elle est complète [31°]. Dans Odoo, le stock d'un kit se compte au niveau de ses composants [6].

#### REST-21 — La rentabilité de chaque plat se calcule

- **Source :** M8 (début du message peu audible) · **Priorité :** Plus tard · **À l'ouverture :** non.
- **Le client dit :** « pour qu'on remplisse les petites quantités pour pouvoir calculer la profitabilité » (M8).
- **Règle de gestion.** Les fiches techniques servent à calculer la rentabilité (M8). **Déduction :** pour chaque plat qui a une fiche, le système calcule ce que le plat coûte et ce qu'il rapporte. **Propositions :** il donne le coût de la portion, la marge (prix de vente hors taxes moins coût) et la part du coût dans le prix, par plat et par famille, sur la période choisie ; un plat dont le coût n'est pas connu est signalé comme tel, et non compté comme rentable à 100 % ; quand une fiche est créée après coup, le manager peut demander le recalcul des marges d'une période, et ce recalcul garde sa date et son auteur.
- **Critères d'acceptation.**
  1. Étant donné un plat vendu 5 000 FCFA hors taxes dont la fiche coûte 1 600 FCFA, quand on lit le rapport, alors la marge est de 3 400 FCFA et le coût représente 32 % du prix.
  2. (Proposition.) Étant donné un plat vendu sans coût connu, quand on lit le rapport, alors il figure dans une rubrique « coût inconnu ».
  3. Étant donné une période, quand le manager regroupe par famille, alors il lit la marge de chaque famille.
  4. (Proposition.) Étant donné une fiche créée aujourd'hui, quand le manager demande le recalcul des marges du mois, alors les marges des ventes de ce plat sont recalculées, la date et l'auteur du recalcul sont conservés, et les montants vendus ne changent pas.
- **Questions :** Q52, Q63.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le coût de chaque vente est écrit au paiement ; la marge figure dans l'« Analyse des ventes » ; le bouton « Calculer le prix depuis la nomenclature », réservé au groupe Fabrication / Administrateur, reporte sur le plat la somme des coûts de ses ingrédients (module `mrp_account`) ; le réglage « Afficher les marges & les coûts » les montre en caisse aux droits avancés (C43, C63). *AITE HOUSE fait déjà :* la marge et le coût des ventes par produit, par famille et par caisse (module `aite_pos_analytics`). *Il manque :* (1) un plat sans coût y apparaît avec 100 % de marge, et remplir sa fiche plus tard ne corrige pas les ventes passées (exécuté côté serveur) ; (2) le coût d'Odoo et celui d'AITE écrivent la même colonne : AITE photographie le coût unitaire à la création de la ligne et en tire le coût total et la marge, puis Odoo réécrit le coût total au paiement par sa propre méthode, ingrédients compris, sans que la marge soit recalculée. Pour un plat à fiche technique suivi en stock et valorisé au coût moyen, l'essai côté serveur donne un coût des ventes de 3 000 pour 15 000 de ventes, mais une marge de 15 000 et un taux de 100 %, dans la monnaie de la base d'essai (H13, C69). (3) Pour une pizza à tailles et suppléments, le coût calculé ignore les lignes liées à un choix : marge surestimée (C79 ; exécuté côté serveur). *AITE développe :* une seule source de coût pour les lignes de caisse (le coût d'Odoo, écrit au paiement, ou la photographie d'AITE) ; le report automatique du coût de la fiche sur le plat ; la liste des plats vendus sans coût ; le recalcul des marges d'une période ; le coût par taille et par supplément des produits à choix (à estimer, avec PROF-01). **Effort : M**, sans ce dernier point.
- *Interne —* **Bonne pratique.** La part du coût se calcule sur le prix hors taxes : coût matière du plat divisé par prix de vente hors taxes [55°]. Pour la viande, le poisson et les légumes, le coût réel tient compte du rendement (poids utilisable sur poids acheté) [53°].

### 3.10 Rapports

#### REST-22 — Le rapport des annulations

- **Source :** M7, M10 · **Priorité :** Indispensable (« les rapports d'annulation ») · **À l'ouverture :** à confirmer.
- **Le client dit :** « Les rapports, on doit avoir tous les rapports. Les rapports d'annulation » (M7) ; « ils vont expliquer dans leur rapport » (M10).
- **Règle de gestion.** Sur la période choisie, un rapport liste les annulations (M7). **Déduction :** il ne compte que les annulations ; les divisions, les transferts et les réunions de tables n'y figurent pas. **Propositions :** il donne les totaux par serveur, par supérieur, par motif et par produit, en quantité et en montant ; le chef de salle peut le lire (Q22).
- **Critères d'acceptation.**
  1. Étant donné trois annulations dans la journée, quand le manager ouvre le rapport du jour, alors il lit trois lignes et leur total.
  2. (Proposition.) Étant donné ce rapport, quand il regroupe par supérieur ou par motif, alors il lit un sous-total par supérieur ou par motif.
  3. Étant donné deux tables réunies, une table divisée et un produit déplacé dans la journée, quand il lit le rapport, alors aucun de ces gestes n'y figure.
  4. (Selon le tableau validé.) Étant donné un chef de salle, quand il ouvre le rapport des annulations, alors il le lit sans avoir accès à la configuration de la caisse.
- **Questions :** Q9, Q22, Q49.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* les tables annulées en entier se retrouvent par le filtre « Annulé » des commandes. *Il manque :* un produit retiré d'une table restée ouverte ne laisse, au mieux, qu'une note dans l'historique ; le rapport « Détails des ventes » n'a aucune rubrique d'annulations (C47, C27). *AITE HOUSE* n'a aucun rapport d'annulation : ses analyses ne retiennent que les additions réglées (H2). *AITE développe :* le rapport, à partir de la trace de REST-12 ; il écarte les additions passées à l'état « Annulé » par une réunion de tables ou par un déplacement (C32). **Effort : S,** une fois REST-12 fait. Pour que le chef de salle le lise : un compte Odoo personnel et un profil de lecture des rapports qui ne donne pas l'administration de la caisse (H10 ; partie 5.2).
- *Interne —* **Bonne pratique.** Un rapport lisible sous trois angles : par serveur, par approbateur, par motif [24°][43°]. La lecture par approbateur sert à contrôler aussi celui qui autorise.

#### REST-23 — Les ventes de ce que l'on choisit : une famille, une sous-famille ou un produit

- **Source :** M7 · **Priorité :** Indispensable (« je veux le rapport des boissons ») · **À l'ouverture :** oui.
- **Le client dit :** « Je veux le rapport des boissons, est-ce que je peux filtrer justement les boissons ? Je veux le rapport des salades […] ? Je veux le rapport des poulets, est-ce que je peux filtrer juste le poulet ? […] on choisit ce qu'on veut » (M7).
- **Règle de gestion.** Sur la période choisie, on obtient les ventes de ce que l'on choisit (M7). **Déduction :** on choisit une famille, une sous-famille ou un produit, et l'on obtient les quantités et les montants. **Déduction, à confirmer (Q48) :** « le poulet » peut être une famille de la carte, un produit, ou tous les plats au poulet répartis dans plusieurs familles. **Propositions :** une famille comprend ses sous-familles (« Boissons » additionne bières, vins et sodas) ; chaque produit appartient à une seule famille ; les rapports suivent les familles de l'écran de commande, pour n'avoir qu'un seul arbre à tenir.
- **Critères d'acceptation.**
  1. Étant donné des ventes de bières, de vins et de sodas, quand le manager choisit « Boissons », alors le total comprend les trois sous-familles.
  2. Étant donné le choix « Salades », quand il lit le rapport, alors seules les salades y figurent, avec quantités et montants.
  3. Étant donné le choix d'un seul produit, quand il lit le rapport, alors seules les ventes de ce produit y figurent.
  4. (Proposition.) Étant donné un produit vendu, quand on additionne toutes les familles, alors il n'est compté qu'une fois.
- **Questions :** Q48, Q52, Q69.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* l'« Analyse des ventes » (Point de Vente → Analyse → Commandes) se filtre et se regroupe par « Catégorie de produits » et par « Catégorie du point de vente » (C44). Filtrer sur la catégorie de produits « Boissons » ramène déjà les produits de toutes ses sous-familles, parce que cette catégorie se cherche sur son nom complet (« Boissons / Alcoolisé / Bière ») (C70 ; mécanisme exécuté côté serveur sur la recherche de produits ; le filtre de l'analyse reste à contrôler à l'écran). *AITE HOUSE fait déjà :* l'« Analyse AITE », onglet « Par catégorie » (chiffre d'affaires, marge, quantités par famille), d'après la catégorie de produits, avec le même champ de recherche (H3). **Régler :** ranger chaque produit dans une seule famille, de la même façon dans les deux classements d'Odoo (celui de l'écran et celui des rapports) ; enregistrer des filtres favoris « Boissons », « Salades », « Poulet » ; éviter qu'un nom de famille en contienne un autre, le filtre se faisant sur le texte. *Il manque :* un sous-total par niveau quand on regroupe (le regroupement ne montre que les familles finales) ; l'équivalent pour la catégorie de caisse (le filtre du tableau de bord standard n'inclut pas les sous-catégories, C55) ; et, dans Odoo, un produit rangé dans plusieurs catégories de caisse n'est compté que dans la première (C45). REST-23-P1, les sous-totaux par niveau de famille : **Effort : S.** *Limites nées du profil :* ni taille ni supplément dans l'analyse (C79) ; une formule y compterait une unité et aucun chiffre sur sa famille (C81 ; à vérifier en caisse : prix des lignes écrits à la main dans l'essai) ; ni « à emporter » ni « sans table » (C83).
- *Interne —* **Bonne pratique.** Le rapport de base d'un restaurant est celui des ventes par article, regroupées par famille puis sous-famille [32°]. Square, lui, sépare le rangement de l'écran et la famille des rapports, pour pouvoir réorganiser l'écran sans fausser l'historique [38°] : ce choix n'est pas retenu ici, pour ne pas faire tenir deux arbres au client.

#### REST-24 — La période se choisit librement

- **Source :** M7 · **Priorité :** Indispensable · **À l'ouverture :** oui.
- **Le client dit :** « tous les rapports possibles, que ce soit journalier, hebdomadaire, mensuel, annuel. Donc le filtre permet qu'on prenne la période qu'on veut » (M7).
- **Règle de gestion.** Tout rapport se calcule sur la période que l'on veut : un jour, une semaine, un mois, une année (M7). **Déduction :** ou d'une date à une autre.
- **Critères d'acceptation.**
  1. Étant donné un rapport, quand le manager choisit « Cette semaine », alors il lit les chiffres du lundi à aujourd'hui.
  2. Étant donné un rapport, quand il choisit du 01/12/2026 au 15/12/2026, alors seules les ventes de ces quinze jours sont comptées.
  3. Étant donné une période sans vente, quand il ouvre le rapport, alors l'écran dit qu'il n'y a rien sur cette période.
- **Questions :** Q53, Q54.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* les filtres par mois, trimestre et année, les regroupements par jour, semaine, mois et année, le rapport « Détails des ventes » d'une date à une autre (C46), et le filtre « du… au… » du tableau de bord standard du restaurant (C55). L'heure de la journée manque au menu de regroupement des vues ; le tableau de bord standard l'a, sans « matin, midi, soir » à régler (C85 ; écran non vu ; Q53). *AITE HOUSE fait déjà :* « Aujourd'hui », « Cette semaine », « Ce mois », « Ce trimestre », « Cette année » et une période personnalisée (H4). **Activer.** Les rapports à développer (REST-22, REST-25-P1) reprennent les mêmes choix.
- *Interne —* **Bonne pratique.** Les rapports de vente de référence se calculent sur une période choisie par l'utilisateur [32°] ; ceux d'Odoo se filtrent et se regroupent à la demande [5].

#### REST-25 — Le nombre de personnes, le nombre de tables et les ventes

- **Source :** M9 · **Priorité :** Indispensable (classement d'AITE : « mon souci c'est que le système puisse compter le nombre de personnes ») · **À l'ouverture :** oui, en version standard (à contrôler à l'écran).
- **Le client dit :** « Pendant qu'on ferme, mon souci c'est que le système puisse compter le nombre de personnes. Que ça puisse donner un rapport. […] Même si ça ne donne pas, ça compte le nombre de personnes, et le nombre de tables, et la quantité vendue, ça permet qu'on peut faire le calcul nous-mêmes et savoir ce qui se passe » (M9).
- **Règle de gestion.** Le système compte les personnes, et un rapport donne le nombre de personnes, le nombre de tables et la quantité vendue, pour que le client puisse faire le calcul lui-même (M9). **Déduction, à confirmer (Q51) :** « pendant qu'on ferme » désigne l'encaissement de chaque table ; l'autre lecture est la fermeture de la caisse en fin de journée. Faute de réponse, les personnes sont comptées à l'encaissement de chaque table et leur total figure aussi sur le rapport de fin de journée. **Déduction, à confirmer (Q50) :** « la quantité vendue » désigne le montant des ventes, puisqu'il veut en tirer un prix moyen ; l'autre lecture est le nombre d'articles. Faute de réponse, le rapport donne les deux, sur la même page et pour la même période. **Propositions (REST-25-P1) :** une table divisée en plusieurs additions compte pour une seule table ; quand deux tables sont réunies, leurs personnes s'additionnent ; une addition déplacée vers une table libre compte pour une table de plus ; les additions encore ouvertes ou annulées ne sont pas comptées. **Proposition, si la vente sans table est ouverte (R, Q76) :** ces ventes se comptent à part, par type, hors des tables et des personnes (PROF-04-P2).
- **Critères d'acceptation.**
  1. Étant donné trois tables encaissées de 2, 4 et 7 personnes pour 130 000 FCFA, quand le manager ouvre le rapport du jour, alors il lit sur la même page 3 tables, 13 personnes et 130 000 FCFA.
  2. Étant donné une période, quand il lit le rapport, alors il lit aussi les quantités vendues de chaque produit.
  3. (Si REST-25-P1 est retenue.) Étant donné une table de 6 personnes divisée en deux additions, quand il lit le rapport, alors elle compte pour 1 table et 6 personnes.
  4. (Si REST-25-P1 est retenue.) Étant donné une table encore ouverte et une table annulée, quand il lit le rapport, alors ni l'une ni l'autre n'est comptée.
  5. (Selon la réponse à Q51.) Étant donné la caisse fermée le soir, quand on lit le rapport de fermeture, alors il indique le nombre de tables et de personnes de la journée.
  6. (Si PROF-04-P2 est retenue ; selon Q76.) Étant donné deux tables de 4 et 2 personnes et trois ventes au comptoir, quand il lit le rapport, alors il lit 2 tables, 6 personnes et, à part, 3 ventes sans table.
- **Questions :** Q29, Q49, Q50, Q51, Q76.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* la table et le nombre de personnes sont enregistrés sur chaque addition (C48). Dès que le service à table et la connexion par code sont installés, Odoo installe d'office le tableau de bord « PdV - Restaurant » (module `spreadsheet_dashboard_pos_restaurant`), réservé au profil Administrateur du Point de Vente. Il donne, sur une période « du… au… » et avec un filtre par serveur : le nombre d'additions, le chiffre d'affaires, le « Revenu moyen par convive » toutes taxes et hors taxes, le chiffre d'affaires et le nombre d'additions par table, le nombre d'additions par heure et par jour (colonne « # Tables »), les quantités vendues par produit et par catégorie de caisse (C55 ; présence constatée par installation, écran non vu). La vue croisée des commandes (Point de Vente → Commandes) accepte « Convives » comme mesure, par jour, semaine ou mois (C56). Le repli que le client accepte en M9 est donc couvert sans développement : **Activer**, à contrôler à l'écran. *Limites lues dans le fichier du tableau de bord :* le calcul des convives n'écarte ni les additions ouvertes ni les annulées (dont celles que créent les réunions de tables) ; le total des personnes n'est pas affiché ; « # Tables » compte des additions, si bien qu'une table divisée compte pour deux ; pas de total par famille parente ; le classement par responsable suit le compte Odoo, pas l'employé. S'y ajoutent les deux défauts de comptage décrits en REST-13 et REST-14 (C19). Odoo range aussi sans table divisions, remboursements et numéros inconnus (C17, C33, C93). Une vente sans table y compte pour une personne (C82) ; à 0, elle en sort : 3 000 par personne au lieu de 3 444 ; une division n'y change rien (C19) ; un remboursement, compté pour une personne, le fait tomber à 1 714 (C83, C93 ; calcul refait côté serveur, S15 ; tableau de bord non ouvert). *AITE HOUSE* compte des additions, pas des tables ni des personnes (H2, H15). *AITE développe* (REST-25-P1) : le total de personnes affiché, l'exclusion des additions ouvertes et annulées, la règle de comptage après division, réunion ou déplacement (la table d'origine est mémorisée), les remboursements exclus, les ventes sans table comptées à part (avec PROF-04-P2), la reprise dans les analyses d'AITE. **Effort : S à M**, estimé avant le profil, à confirmer avec les ventes sans table. Ces compléments passent par un tableau de bord livré par AITE : la modification d'un tableau de bord à l'écran serait réservée à l'édition Enterprise (non vérifié, code Enterprise absent).
- *Interne —* **Bonne pratique.** Publier ensemble le nombre de personnes servies et le nombre d'additions : ce sont deux bases différentes, qui donnent deux moyennes différentes [57°][58°].

#### REST-26 — Le prix moyen par personne

- **Source :** M9 · **Priorité :** Souhaité (« même si ça ne donne pas […] on peut faire le calcul nous-mêmes ») · **À l'ouverture :** oui, en version standard (à contrôler à l'écran).
- **Le client dit :** « La quantité vendue divisée par le nombre de personnes, qu'on ait un prix moyen » (M9).
- **Règle de gestion.** Un rapport donne un prix moyen : la quantité vendue divisée par le nombre de personnes (M9). **Déduction, à confirmer (Q50) :** c'est le montant des ventes divisé par le nombre de personnes servies, sur la période choisie. **Propositions (REST-26-P1) :** donner aussi le prix moyen par table ; écrire sur le rapport si les montants sont toutes taxes comprises ou hors taxes ; calculer ce prix moyen avec la règle de comptage de REST-25-P1, donc sur les tables seules (Q76).
- **Critères d'acceptation.**
  1. Étant donné 130 000 FCFA de ventes pour 13 personnes servies, quand le manager lit le rapport, alors le prix moyen par personne est de 10 000 FCFA.
  2. Étant donné une période sans table servie, quand il lit le rapport, alors aucune moyenne n'est affichée.
  3. (Si REST-26-P1 est retenue.) Étant donné le rapport, quand on le lit, alors il indique si les montants sont toutes taxes comprises ou hors taxes, et donne aussi le prix moyen par table.
- **Questions :** Q50, Q52, Q53, Q76.
- *Interne —* **Couverture.** *Odoo 18 fait déjà :* le « Revenu moyen par convive », toutes taxes et hors taxes, du tableau de bord standard « PdV - Restaurant » : total des additions divisé par la somme des convives (C55) ; et le montant par convive affiché pendant la saisie d'une table (C18). **Activer**, à contrôler à l'écran, avec les limites de comptage dites en REST-25. *AITE HOUSE* calcule un « panier moyen » par addition, pas par personne (H15). REST-26-P1 : **Effort : S**, seulement si la règle de comptage d'AITE est retenue.
- *Interne —* **Bonne pratique.** Dépense moyenne par personne = chiffre d'affaires divisé par le nombre de personnes servies ; l'usage français la calcule toutes taxes et boissons comprises [57°][59°]. Elle se distingue de la moyenne par addition [58°]. Une vente à emporter sans personne au dénominateur gonfle la moyenne ; comptée pour une personne par défaut, comme chez Toast et dans Odoo, elle la fausse : à la baisse pour un café, à la hausse pour plusieurs pizzas [75°][76°].

---

## 4. Ce que le client n'a pas demandé et qu'il faut trancher

Ces points ne sont pas dits dans les messages, ou n'y sont dits qu'à moitié ; chacun conditionne une demande du client. Ils sont à décider avec lui avant l'ouverture. La colonne « Ce que l'on sait » est interne ; les trois autres peuvent lui être remises.

### 4.1 La cuisine, le matériel, l'hébergement

| Sujet | Ce que l'on sait (interne) | Pourquoi cela compte | Question |
|---|---|---|---|
| Où arrive une commande envoyée | Odoo imprime un bon par poste de préparation (cuisine, bar), selon les familles de produits [1]. L'écran de préparation en cuisine n'existe que dans l'édition Enterprise [4] (C49). | Le client parle de commandes « envoyées » sans dire où. Sans imprimante ni écran, la cuisine ne reçoit rien, et une annulation ne la prévient pas. | Q6 |
| Les remarques pour la cuisine, les formules, l'ordre des plats | Odoo porte une remarque sur chaque produit (« Note cuisine », C76) et sait vendre des formules (PROF-03). Envoi en plusieurs temps : pas de « suite » en 18.0 Community ; un double-clic met de côté une ligne non envoyée, sans rien écrire sur le bon (C89 ; lu dans le code). | Ces usages changent la saisie de la carte et ce qui s'imprime sur les bons. | Q33, Q69 |
| L'édition d'Odoo et l'hébergement | On ne sait pas quelle édition aura ce client. Tout ce document vaut pour l'édition Community ; Enterprise ajoute l'écran de préparation et la réservation de tables (C49) ; son code n'a pas pu être lu. L'hébergement en ligne d'Odoo (Odoo Online) n'accepte pas les applications non standard [64] : il est exclu par les modules d'AITE. | L'édition et l'hébergement décident du matériel de cuisine, du coût, et de qui sauvegarde les données. Ils sont à connaître avant tout chiffrage. | Q4 |
| Le matériel | En édition Community, les bons de cuisine passent par une imprimante Epson reliée au réseau ou par un boîtier Odoo (C50) ; non testé. Dès qu'une imprimante Epson est déclarée, Odoo ouvre la caisse par une adresse prévue pour le HTTP ; sur un hébergement en HTTPS, il faudra sans doute un certificat sur l'imprimante ou le boîtier : à essayer sur l'hébergement réel (C75). | Les imprimantes et les tablettes doivent être choisies, puis essayées avec la caisse avant l'ouverture, pas le jour même. | Q2, Q5 |
| Les coupures d'internet et de courant | La caisse d'Odoo continue de vendre pendant une coupure passagère [3]. Mais un stock partagé entre plusieurs postes et un code de supérieur vérifié par le système central supposent la connexion. La mise à jour des tables entre postes passe par un canal temps réel, qui doit traverser l'hébergement (C75). | Il faut une règle pour le jour où le réseau tombe en plein service : vendre sans contrôle, ou attendre. Sans onduleur, une coupure de courant arrête la caisse, les imprimantes et le Wi-Fi. | Q59, Q60 |

### 4.2 L'argent

| Sujet | Ce que l'on sait (interne) | Pourquoi cela compte | Question |
|---|---|---|---|
| Remises et produits offerts | Aujourd'hui, tout employé peut accorder une remise [2] (C15). Réglage immédiat : décocher « Remises appliquées à la ligne » (coché par défaut : c'est lui qui rend active la touche %) et ne pas activer « Remises globales » ; plus aucun employé ne remise alors en caisse (C71 ; non essayé à l'écran). Le développement ne sert qu'à autoriser de nouveau les remises, avec l'accord d'un supérieur et une explication, comme le font les éditeurs de caisses [44°]. Square distingue le produit annulé (saisi par erreur, pas encore préparé) du produit offert (déjà préparé ou servi) [34°]. | Sans règle, la remise à 100 % devient le moyen de contourner le verrou des annulations. | Q20, Q36 |
| Après l'encaissement | Tout employé peut rembourser une addition déjà payée (C29). Chez Toast, une addition payée ne s'annule plus : elle se rembourse, et c'est un autre droit [21°]. | Même risque que pour les annulations, après le paiement. | Q37 |
| Annuler une table entière ; fermer la caisse avec des tables ouvertes | « Annuler la commande » est ouvert à tout employé (C28). À la fermeture, si des tables sont encore ouvertes, un bouton les annule toutes d'un coup (C30). Toast, lui, interdit de clore la journée tant que chaque addition ouverte n'a pas été réglée, annulée avec accord ou transférée [29°]. | Ce bouton contourne tout le dispositif d'annulation, précisément pour les additions oubliées dont parle M11. | Q37 |
| L'addition imprimée avant le paiement | Le réglage existe (« Impression du reçu avant le paiement », C52). Une fraude classique consiste à présenter l'addition, encaisser en espèces, puis annuler ou déplacer des lignes [48°]. | Il faut décider si toute modification après impression passe par un supérieur, et si l'alerte orange s'arrête une fois l'addition imprimée. | Q37, Q39, Q58 |
| Les moyens de paiement, dont le Mobile Money | Dans AITE HOUSE, le Mobile Money se saisit aujourd'hui comme un moyen de paiement manuel, sans liaison avec l'opérateur ; la liaison est prévue plus tard dans la feuille de route (H20). AITE HOUSE sait aussi tenir un compte client à régler plus tard (l'ardoise) : voir la partie 5 avant de le proposer au restaurant. | Le client veut pouvoir écrire le nom d'une société sur une table (M2) : il faut savoir si cette société paie sur place, reçoit une facture officielle ou a un compte. | Q27, Q56 |
| Les pourboires | Odoo a un réglage pour les pourboires (C52). | S'ils passent par la caisse, ils ne doivent pas se mêler au chiffre d'affaires dans les rapports. | Q57 |
| La fermeture de la caisse et les espèces | Avec la connexion par code, fermer la caisse est réservé aux droits avancés ; entrer ou sortir des espèces est ouvert à tout employé identifié (C11, C57). Une extension libre d'Odoo permet une fermeture « à l'aveugle », où la caissière compte sans voir le montant attendu [12]. | La fermeture et les espèces font partie du tableau des droits ; le comptage des espèces est le premier contrôle du soir. | Q8 |
| Les taxes et la facture officielle d'une société | Le régime de taxe du client n'est pas connu. La dépense moyenne se calcule en général toutes taxes comprises, la rentabilité hors taxes [57°][55°]. La feuille de route prévoit de suivre la taxation en temps réel de la DGI (H20). Aucune obligation camerounaise sur la conservation des annulations de caisse n'a été trouvée pendant cette étude : à vérifier auprès d'un fiscaliste. | La base des montants s'écrit une fois pour tous les rapports, sinon deux rapports donneront deux chiffres pour la même journée. Il faut aussi savoir ce que doit porter la facture remise à une société. | Q52, Q55 |

### 4.3 Le contrôle

| Sujet | Ce que l'on sait (interne) | Pourquoi cela compte | Question |
|---|---|---|---|
| Les retraits avant l'envoi | Ils restent libres (REST-10). Chez Toast non plus, aucun droit ne les couvre, et l'éditeur le reconnaît comme une demande d'évolution [33°]. | Une boisson saisie, servie au bar sans être envoyée, puis retirée, échappe au contrôle. On peut au moins compter ces retraits par serveur. | Q34 |
| La table d'un collègue | Toast en fait deux droits distincts : voir les additions des autres, et les modifier [22°]. | L'exemple de M1 (Valérie ouvre, le restaurateur encaisse) suppose que quelqu'un d'autre accède à la table. Il faut dire qui. | Q19 |
| Qui contrôle celui qui autorise | Les éditeurs publient un rapport des annulations par approbateur [24°]. | Celui qui autorise peut se tromper, ou être complice. Il faut savoir qui lit ce rapport, et si le manager laisse lui aussi une explication. | Q22, Q35 |
| Où se lisent les rapports | Un employé identifié par son seul code n'accède pas à l'espace de gestion : il lui faut un compte personnel [2] ; aucun rapport ne s'affiche dans la caisse. | Le chef de salle ne lira le rapport des annulations que s'il a un compte et un appareil pour le lire ; le nombre de comptes pèse sur le coût. | Q22 |
| La solidité des codes | Le code est vérifié sur le poste de caisse (C3). Un badge est recommandé pour les supérieurs, parce qu'un code tapé devant un employé se retient [45°]. | Tout le contrôle des annulations repose sur le secret du code du supérieur. | Q18 |

### 4.4 Le stock et les rapports

| Sujet | Ce que l'on sait (interne) | Pourquoi cela compte | Question |
|---|---|---|---|
| Le stock de départ et les inventaires réguliers | Le client parle de saisir « le stock qu'on a » (M6) ; il ne dit rien du rythme des inventaires ni des écarts. Les manuels de gestion demandent un inventaire à rythme fixe : très souvent pour les produits chers ou périssables, chaque mois au minimum pour le reste [54°][52°]. | Sans stock de départ saisi avant le premier jour, la caisse refuse toutes les ventes des produits suivis. Sans inventaires, le stock de la caisse s'écarte du stock réel et le refus devient faux. | Q7, Q43 |
| Les unités d'achat et de vente | On achète au casier ou au carton, on vend à la bouteille, au verre ou à la dose. Le coût d'un verre se calcule à partir de la bouteille [55°]. Essayé côté serveur : PROF-07. | Sans cette correspondance, ni le stock ni le refus de vente ne sont justes pour le vin et le whisky servis au verre. | Q45 |
| Le moment où le stock baisse | Les caisses de restaurant décomptent à l'envoi en cuisine [30°] ; Odoo décompte au paiement (C40). | Tant qu'une table est ouverte, ses consommations ne sont pas déduites : deux serveurs peuvent vendre la même dernière bouteille. | Q46 |
| La casse, les pertes, les repas du personnel, le plat préparé puis annulé | Les méthodes de contrôle du coût matière demandent de saisir les pertes connues pour isoler l'écart inexpliqué [46°]. Un plat déjà préparé puis annulé a consommé de la marchandise [34°]. | Sans cette saisie, le stock de la caisse dépasse le stock réel et la rentabilité (REST-21) est faussée. L'explication d'une annulation doit donc dire si le produit est perdu. | Q36, Q47 |
| Les familles des rapports et celles de l'écran | Dans Odoo, la famille de l'écran de commande et la famille des rapports sont deux classements distincts ; nos analyses suivent le second (C45, H3). | Si les deux classements divergent, « Boissons » à l'écran et « Boissons » dans le rapport ne recouvrent pas les mêmes produits. | Q48 |
| La journée qui finit après minuit | Dans nos analyses, une addition est datée de l'heure de son encaissement (C37, H2). | Une table ouverte à 23 h 30 et payée à 0 h 20 tombe sur le lendemain. Il faut fixer l'heure de fin de journée. | Q54 |

### 4.5 Le démarrage

| Sujet | Ce que l'on sait (interne) | Pourquoi cela compte | Question |
|---|---|---|---|
| La saisie avant l'ouverture | La carte (produits, familles, prix), le plan de salle, les employés avec leurs codes et leurs niveaux, le stock de départ : rien de cela n'existe encore dans le système. | C'est le plus gros du travail de réglage ; il dépend du client autant que d'AITE. | Q7 |
| La formation et le premier jour | Rien n'est encore prévu. | Quatre niveaux d'employés découvrent la caisse en même temps ; un service d'essai avant l'ouverture montre ce qui manque. | Q62 |
| Hôtel, bar, ventes sans table | (R) : un restaurant seul, sans les modules hôteliers d'AITE HOUSE (H21) ; vente sans table et caisse du bar en option (PROF-04, PROF-08). | Ce qu'il faut installer, l'écran d'ouverture et le nombre de caisses en dépendent. | Q3, Q25, Q64, Q65, Q78 |
| Le logiciel que le client connaît | Son vocabulaire (« code du grade supérieur », et peut-être « taper une table », mot peu audible) laisse penser qu'il a déjà travaillé avec une caisse de restaurant. | Reprendre ses habitudes d'écran réduit la formation des équipes. | Q14, Q61 |

### 4.6 Ce qui n'est pas dans ce périmètre

**Proposition**, à valider par le dirigeant d'AITE puis par le client. Sauf demande nouvelle, cette étude ne couvre pas :

- la réservation de tables ;
- la commande passée par le client lui-même, par QR code (la fonction s'installe avec le service à table, mais reste désactivée) ;
- l'écran de préparation en cuisine : la cuisine et le bar reçoivent des bons imprimés ;
- la liaison automatique avec les opérateurs de Mobile Money : le paiement est saisi à la main ;
- l'hébergement et la note de chambre : l'établissement est un restaurant seul (R, Q3) ; en l'état, la fidélité, liée au module hôtelier ;
- la liaison avec une plateforme de livraison ; la livraison est une option, qui livre reste à dire (PROF-04, Q72) ;
- la pizza moitié-moitié en caisse, la carte et les prix qui changent seuls selon l'heure : absents d'Odoo 18 Community (édition Enterprise non lue, Q4) ; ils n'entrent dans le périmètre que si le client les demande (Q68, Q74), au lot 2 (PROF-02, PROF-06) ;
- la comptabilité et les déclarations fiscales.

### 4.7 Ce que le profil de l'établissement ajoute

Ces huit points viennent de la précision d'AITE (P), pas des messages ; PROF-04 et PROF-08 suivent ses réponses (R). Aucun n'est une exigence, chacun est à trancher avec le client. Rien n'a été essayé à l'écran de caisse.

| Sujet | Ce que l'on sait (interne) | Pourquoi cela compte | Question |
|---|---|---|---|
| **PROF-01** — Tailles et suppléments (pizzas, café) | Avec des attributs sans création de variante (« Jamais »), une seule fiche par pizza : une fenêtre fait choisir la taille et cocher les suppléments, chacun à prix fixe [65] (C77 ; lu dans le code). Limites : pas de quantité par supplément ; même prix sur toutes les tailles, quand Toast le fait suivre la taille [69°]. La fiche technique suit ces choix (C79 ; exécuté côté serveur) ; le coût calculé et les rapports, non (REST-21, REST-23). | Si les pizzas ont plusieurs tailles, la carte se saisit autrement : une seule touche par pizza, la taille se choisit ensuite ; en contrepartie, les rapports ne séparent pas les tailles. | Q66, Q67 |
| **PROF-02** — Pizza moitié-moitié | Rien dans Odoo 18 Community (C77 ; code Enterprise absent). Sans développement : une remarque pour la cuisine, au prix de la pizza saisie. Rezku la saisit sur une seule ligne [71°] ; trois règles de prix se rencontrent : un pourcentage par moitié, la moyenne, la plus chère [70°] (attribution incertaine). | Sans règle écrite, deux serveurs facturent la même pizza à deux prix. | Q68 |
| **PROF-03** — Formules (petit déjeuner, menu) | Un produit de type « Combo » : un produit et un seul par choix, supplément possible, prix fixe [67] (C80 ; lu dans le code). Limites : ni choix facultatif, ni heures de validité. Seuls les produits choisis sortent du stock (C81 ; exécuté côté serveur). Effet sur les rapports, à vérifier en caisse : REST-23. | Une formule change la saisie de la carte, les bons et les ventes par famille (REST-23). | Q69 |
| **PROF-04** — Vente au comptoir, à emporter, livraison | (R) : pas de vente sans table en temps normal ; les trois formes en option. *Sans développement :* le « + » ouvre une addition sans table, à nom libre (« 12:30 Nom », triée par heure) ; aucun réglage ne le retire (C82, C93), seul PROF-04-P1. *À emporter :* « Manger sur place / À emporter », décoché par défaut, se coche même session ouverte et ne change la taxe qu'avec une position fiscale à créer (C94 ; exécuté côté serveur). *Livraison par le restaurant :* adresse et téléphone lus en caisse, imprimés par la seule « Note générale » ; frais vendus comme un produit ; paiement au retour, avant la fermeture (C95 ; exécuté côté serveur). Par plateforme : Enterprise et abonnement [68]. Les éditeurs font choisir et publient le type de vente [73°][74°][85°] et font rendre compte au livreur [86°]. | La caisse permet d'office de vendre sans table ; la fermer demande un petit développement. Ouverte, elle touche l'ouverture (REST-05, REST-06), le nom (REST-08), l'alerte (REST-17), la taxe et les rapports (REST-25, REST-26). | Q64, Q71, Q72, Q76, Q78, Q81, Q82 |
| **PROF-05** — Postes de préparation (cuisine, bar, four) | (P) cite « bar et cuisine » : deux postes de préparation, ou l'offre. Une imprimante par poste, avec ses familles ; une famille peut sortir sur deux imprimantes (C84 ; lu dans le code, aucun bon imprimé). Un produit sans famille cochée n'est jamais envoyé (C67) ; les titres des bons risquent de sortir en anglais (C78). NCR décrit, pour un four à convoyeur, un poste de montage et un poste d'enfournement [72°]. | Le nombre d'imprimantes et le rangement de la carte en familles en dépendent. | Q2, Q6 |
| **PROF-06** — Moments de la journée (matin, midi, soir) | La caisse ne cache rien et ne change aucun prix selon l'heure : les heures « Disponible entre » d'une famille ne servent qu'à la commande par QR code, et une seconde liste de prix se choisit à la main, par tout employé (C85, C90 ; lu dans le code). Rapports par heure : REST-24. Toast déclare des périodes nommées et une carte par plage horaire [77°][78°]. | Si l'établissement ouvre du matin au soir (Q73), un total de journée ne suffit pas, et un seul délai d'alerte sonne trop tôt le soir ou trop tard le matin (REST-17). | Q11, Q38, Q53, Q73, Q74 |
| **PROF-07** — Bar : verre, dose, addition ouverte | La caisse vend dans l'unité du produit : un produit par format (bouteille, verre, dose), chacun avec une fiche technique qui puise dans le même stock, tenu dans la petite unité pour éviter les arrondis (C86 ; exécuté côté serveur). Option comptoir ouverte, une addition de bar sans table est absente du plan, donc sans alerte ; elle bloque la fermeture (C87, C30). Square vend un même stock à la bouteille et au verre [80°]. | Sans doses réglées, ni le stock ni le refus de vente ne sont justes au bar. Une addition de bar oubliée est le cas de M11, sans la couleur. | Q45, Q75 |
| **PROF-08** — Une ou plusieurs caisses | (R) : caisse unique par défaut ; en option, le bar a son tiroir, son fond et sa fermeture (option 1), ou encaisse aussi les tables (option 2). Les éditeurs donnent un tiroir à une personne pour le service et clôturent tiroir par tiroir [82°][83°] ; ils transfèrent l'addition du bar sur la table [84°][81°]. | Le nombre de tiroirs, la fermeture du soir, le chiffre par caisse et le client qui passe du bar à la table en dépendent. | Q65, Q77 à Q80, Q83 |

*Interne —* **Montages de caisse (PROF-08)**, essayés côté serveur (S9 à S12).

| Montage | Fond et fermeture | Tables entre postes | Proposition |
|---|---|---|---|
| A. Une seule caisse, ouverte sur chaque poste | Un (C96) | Partagées, transférables (C87 ; lu dans le code) | **Par défaut** ; un poste au bar y encaisse toute table (C12) : option 2 ouverte de fait, fermée par consigne puis REST-03 |
| B. Deux caisses, une salle | Deux | Non chargées, sauf par « PdV sécurisé », masqué pour la restauration, dans « Commandes » ; total faux, paiement hors des fermetures (C98) | À écarter |
| C. Deux caisses, chacune sa salle | Deux, contrôlés à part (C99) | Aucune | **Option 1** (PARAM-11) ; avec l'option 2, PROF-08-P1 |

*Interne —* À proscrire : deux modes espèces sur une caisse (pas deux tiroirs) ; une caisse sans espèces ne rend pas la monnaie (C96, C99). En A, la fermeture dit qui a encaissé, pas sur quel poste (C97 ; exécuté côté serveur) ; le bar prend le tiroir et l'imprimante de tickets de la caisse : sa propre imprimante demande le montage C (lu dans le code, à vérifier sur place).

---

## 5. Effets sur AITE HOUSE

Cette partie est pour AITE. Elle repose sur la lecture du code des seize modules et d'Odoo 18 Community. Rien n'a été essayé à l'écran de caisse. Une installation à froid (`point_of_sale`, `pos_restaurant`, `hr`, `mrp`, `aite_pos_analytics` et `aite_pos_credit`, sans données de démonstration) et des essais côté serveur ont été joués le 12/11/2026 sur une base jetable, puis rejoués pendant la correction (annexe C) ; la suite AITE complète n'a pas été installée avec ces modules. Le 13/11/2026, la pile « restaurant seul » (5.1) a été installée à froid et ses tests joués (essais V1 à V9). Un risque qui ne porte pas la mention « exécuté côté serveur » est une déduction, à confirmer par un test. Les montants cités pour les essais sont dans la monnaie de la base d'essai.

### 5.1 Ce que l'activation du service à table change

- **Trois nouvelles dépendances standard.** Aucun module d'AITE HOUSE ne dépend aujourd'hui de `pos_restaurant`, de `hr` ni de `mrp` ; la feuille de route ne les liste pas (H20), et le scénario de la présentation dit en toutes lettres qu'AITE HOUSE n'installe pas `pos_restaurant` (H1).
- **Des modules entraînés.** Liste constatée par installation le 12/11/2026 (C51) : avec `pos_restaurant`, `pos_self_order` (commande par QR, désactivée par défaut), `pos_self_order_epson_printer` et `pos_online_payment_self_order` ; avec `hr`, `pos_hr`, `pos_hr_restaurant`, `hr_skills`, `hr_org_chart` (et `web_hierarchy`) et `mail_bot_hr` ; avec `mrp`, `pos_mrp`, `mrp_account` et `sale_mrp` ; et deux tableaux de bord, `spreadsheet_dashboard_pos_hr` et `spreadsheet_dashboard_pos_restaurant` (C55). `purchase_mrp` s'y ajoute avec les Achats (constaté le 13/11/2026, essai V1) ; `hr_maintenance` ne viendrait qu'avec `aite_housekeeping`, module hôtelier.
- **Le compte de la caisse.** Avec la connexion par code, tous les employés travaillent sous un seul compte Odoo, celui qui a ouvert la caisse (C74). Ce compte décide de ce qui fonctionne. S'il n'est qu'« Utilisateur » du Point de Vente, l'écriture d'une table est refusée (exécuté côté serveur) : réunir deux tables en les glissant et « Modifier le plan » échouent, quel que soit le niveau de l'employé (C61) ; la création de produit en caisse et le bouton des espèces dépendent aussi des droits de ce compte (C62, C57). S'il est « Administrateur », chaque poste reste connecté à Odoo avec ces droits : le lien vers la gestion est masqué aux employés, pas l'adresse (C62). **À décider par AITE :** un compte dédié à la caisse, Administrateur du Point de Vente et sans autre application, ou un compte « Utilisateur » et des gestes limités à « Transférer / Fusionner ». Le manager et les lecteurs de rapports ont chacun leur propre compte ; celui du manager reçoit aussi Employés / Responsable (C63).
- **Des réglages par caisse.** « Est un bar/restaurant » et « Se connecter avec Employés » se cochent caisse par caisse : les caisses sans service à table que le client aurait déjà (Q4) ne changent pas d'elles-mêmes. Mais le code de ces modules est chargé dans toutes les caisses.
- **Un restaurant seul (R) : cinq modules sur seize.** `aite_pos_analytics`, `aite_pos_credit`, `aite_stock_dashboard`, `aite_purchase_dashboard` et `aite_direction_dashboard` s'installent sans le socle hôtelier ; les onze autres, le socle et les dix modules qui en dépendent directement, sortent du périmètre de ce client (H21, qui complète H17).
- **Installation à froid et tests (exécuté côté serveur, essais V1 à V3).** Base vierge, Community, en français, sans données de démonstration, avec le service à table, la connexion par code, le stock, les achats, la fabrication et les cinq modules : 90 modules installés, journal sans erreur ni avertissement, aucun modèle hôtelier ; `aite_pos_credit` entraîne l'application Ventes. Les 264 tests Odoo des cinq modules passent ; 4 s'ignorent faute d'hôtel, dont celui de la journée après minuit (H26). Avec les données de démonstration d'Odoo : 1 échec et 6 erreurs, dus à ces données ; rien n'a été corrigé.
- **Constats.** (1) Le pays se choisit à la création de la base : créée en ligne de commande, sans pays, elle naît en dollars, avec le plan comptable générique ; créée comme par l'écran de création, avec le pays Cameroun, elle naît en FCFA, avec le plan comptable camerounais (essai V9 ; exécuté côté serveur, écran non vu). Aucun des cinq modules ne pose le FCFA (H22). (2) Deux fiches d'applications portent le nom du client pilote (H23). (3) Le cockpit Direction tient sans hôtel : le bloc Hébergement n'est calculé que si le module hôtelier existe ; ses lignes « Annulations » et « Remises élevées » ne sont jamais alimentées (H24 ; essai V4, écran non vu). (4) « Top bières » et « Consignes d'emballages » sont des cartes du bar-cave pilote (H25). (5) Le scénario standard « Restaurant » d'Odoo charge, même sans démonstration, salles, produits en anglais et additions d'exemple, que nos analyses comptent ; il laisse une session ouverte, qui interdit de cocher « Se connecter avec Employés » : à ne pas lancer chez le client (C92, essai V5). (6) `dev/setup_env.sh`, `dev/run_tests.sh` et `docs/INSTALLATION.md` supposent l'hôtel ; l'audit des menus ne voit que 4 des 15 entrées d'AITE (H28, essai V7).
- **Deux éditions.** L'édition du client est inconnue : les développements doivent fonctionner sur Community et sur Enterprise, comme le socle. **Proposition :** un module `aite_restaurant` (dépendant de `pos_restaurant` et de `pos_hr`) pour la caisse, et un module passerelle auto-installé pour les analyses, sur le modèle d'`aite_hotel_gantt`, afin de ne pas imposer `pos_hr` à `aite_pos_analytics`.

### 5.2 Module par module

| Module | Ce qui tient | Ce qui change ou casse | Preuve |
|---|---|---|---|
| `aite_pos_credit` (ardoises) | Le bouton « Mettre sur ardoise » n'entre en collision avec aucun écran de `pos_restaurant` ni de `pos_hr`, à la lecture. | **L'ardoise se crée sans regarder l'état de la commande.** Or le service à table enregistre sur le système central les commandes encore ouvertes, lignes de paiement comprises. Exécuté côté serveur : sur une commande à l'état « Nouveau », l'enregistrement d'un paiement « Ardoise client » non validé crée l'ardoise (2 000, ouverte), et elle reste ouverte après l'annulation de la commande. Le bouton n'a aucune condition de niveau : un serveur pourrait mettre une table sur ardoise. Enfin une caisse créée par le scénario standard « Restaurant » ou « Bar », ou la première caisse créée, reçoit d'office « Ardoise client », qu'Odoo prend pour son mode « Compte client » ; une caisse créée ensuite à la main ne le reçoit pas (exécuté côté serveur). Revu le 13/11/2026 : même résultat pour la caisse du scénario standard (essai V5). Caisse du bar (option 1) : à ajouter à la main, ou d'office (AH-13 ; H31). | H5, C53, H7, H8, C58, H31 |
| `aite_hotel_pos_link` (note de chambre), `aite_loyalty` (fidélité) | Note de chambre : **sans objet (R)**. Fidélité, prévue aussi pour le restaurant et la boutique : **indisponible en l'état**, elle exige le socle hôtelier et `aite_slot_booking` (H17, H21) ; la rendre installable seule serait un développement, non estimé. Ailleurs : folio et points ne sont touchés que sur une commande réglée. | Ailleurs : les relectures de commandes du service à table ne sont pas couvertes par le test de l'écart n° 78 ; fidélité à tester après une division. | H6, H9 |
| `aite_pos_analytics` (analyses des ventes) | La vue ne lit que des colonnes de base et ignore les tables ouvertes : rien ne devrait casser. | **La dimension « Caissier » lit l'utilisateur Odoo de la caisse**, le même pour tous les employés identifiés par code : toutes les ventes tomberaient sous un seul nom, et le cas de recette D12 (« Suivre les ventes par vendeur ») ne passerait plus. Confirmé côté serveur par le chemin de la caisse (essai V8). Les heures de pointe montrent l'heure d'encaissement, pas d'arrivée. Le « nombre de commandes » compte des additions. La répartition des paiements ne filtre pas l'état de la commande. Un plat sans coût affiche 100 % de marge, et le coût total d'une ligne est réécrit par Odoo au paiement sans que la marge d'AITE soit recalculée (exécuté côté serveur ; REST-21). La vue est écrite d'un bloc, sans point d'extension. Deux modes espèces : tiroir du bar sans contrôle d'écart (H30). | H2, C8, H16, C37, H15, H14, H13, C69, H30 |
| `aite_stock_dashboard` (stock) | Ruptures, couverture, quantité à commander pour les produits suivis. | Un plat non suivi en stock mais vendu en caisse sortirait en « Rupture ». Avec des fiches techniques, ce sont les ingrédients qui sortent : le chiffre d'affaires estimé et le coulage perdent leur sens. | H11 |
| `aite_purchase_dashboard` (achats) | Aucun lien avec la caisse : rien ne change. | Carte « Consignes d'emballages » héritée du bar-cave pilote (AH-11). | H21, H25 |
| `aite_direction_dashboard`, `aite_exec_dashboard` | Ils relisent les moteurs ci-dessus. | Ils héritent de leurs écarts (pastille Stock, « tickets », panier moyen). Aucun n'affiche les personnes ni les tables. | H15 |
| `aite_demo_data` | — | Une seule caisse de démonstration, limitée à la boutique ; ni salle, ni table, ni employé, ni fiche technique ; familles à deux niveaux. Exige le socle hôtelier ; aucune pizza parmi ses 74 produits de restaurant (essai V6). | H18, H27 |
| Droits AITE | — | « Manager — Analyses POS » implique l'administrateur du Point de Vente : le donner à un superviseur pour qu'il lise les rapports en fait un « manager » en caisse. Il faut un profil de lecture des rapports qui ne donne pas l'administration de la caisse. Sans hôtel, Stock, Achats et Direction n'ont pas de groupe propre. | H10, C10, H29 |
| Étude comparative | — | Elle présente le plan de salle comme « couvert » et la synthèse parle de « POS hors-ligne avec plan de salle », alors que rien n'a été essayé à l'écran avec nos modules. À corriger, ou à couvrir par la campagne de tests ci-dessous, avant tout engagement. | H19 |

### 5.3 Risques d'intégration, par ordre de gravité

1. **Ardoise ouverte sur une table non encaissée** (financier). Confirmé par exécution côté serveur le 12/11/2026 ; reste à rejouer à l'écran : sur une table, choisir « Ardoise client », revenir au plan sans valider, puis annuler la table. Le risque est actif par défaut, puisqu'une caisse de restaurant créée par le scénario standard reçoit ce mode de paiement (C58). Correction attendue : un contrôle d'état avant de créer l'ardoise, comme le font déjà la note de chambre et la fidélité, et l'annulation de l'ardoise quand la commande est annulée (H5, H6).
2. **Perte du nom du vendeur dans les analyses** dès l'activation de la connexion par code. C'est le cœur de la demande M1 : REST-02 et l'adaptation d'`aite_pos_analytics` vont ensemble (H2, C7).
3. **Droits contournés.** Avec la connexion par code, les employés n'ont pas de compte Odoo : nos groupes (POS Crédit, Analyses POS) ne filtrent plus rien dans la caisse (H7, H10). Les contrôles ajoutés dans la caisse auront la même nature que ceux d'Odoo, faits par l'écran, sauf à les doubler d'une vérification et d'un journal sur le système central (C13). Et le poste reste connecté sous le compte de la caisse (partie 5.1).
4. **Tableau de bord du stock faussé** par les plats non suivis et par les fiches techniques (H11).
5. **Rentabilité trompeuse** tant que les fiches techniques ne sont pas remplies, et tant que deux calculs de coût écrivent la même colonne (H13, C69).
6. **Chiffres qui changent de sens sans erreur visible** : heure d'encaissement, additions comptées comme des tables, paiements d'une table ouverte (C37, H15, H14) ; pour ce profil, une formule sans chiffre sur sa famille et, option ouverte, une vente sans table comptée pour une personne (C81, C83).
7. **Performance** (hypothèse à mesurer) : les totaux de la session de caisse se recalculent à chaque enregistrement d'une commande de table, sur une session partagée par plusieurs postes (H14).
8. **Limites connues d'Odoo 18 sur les tables partagées.** Trois tickets publics : en mode restaurant, des commandes restaurées depuis le poste sont écrasées par celles du système central après un rafraîchissement [16] ; avec deux caisses distinctes sur la même salle, l'une ne voit pas la table ouverte par l'autre [17] (récit d'un seul utilisateur ; une réponse d'un tiers, le 30/10/2026, indique que le défaut n'existe plus sur la branche de développement ; pas de réponse d'Odoo) ; un défaut de réimpression en cuisine après fusion a été corrigé en version 19 [18]. Aucun n'a été reproduit ici. **Proposition, compatible avec les réponses (R), à confirmer (Q2, Q65) :** une seule caisse, ouverte sur chaque poste (montage A, PROF-08) ; deux caisses sur une même salle : montage B, à écarter (C88, C98).
9. **Impression et temps réel derrière l'hébergement.** Les bons de cuisine sur imprimante Epson et la mise à jour des tables entre postes dépendent du protocole et du proxy de l'hébergement (C75) : à essayer sur l'hébergement réel. La feuille de route note par ailleurs un diagnostic d'impression en attente (H20).
10. **Anglais résiduel.** « Link Table » n'est pas traduit (REST-13) ; « Bloquer », « Convives », « Fractionner », « Aller à/au », « Cash entrant/sortant » sont peu parlants (C54). Notre règle « pas d'anglais résiduel » demandera des corrections de traduction. S'y ajoutent les titres des bons de préparation (C78).
11. **Restaurant seul : réglages et héritages à reprendre** (constats 1, 2 et 4 de la partie 5.1 ; H22, H23, H25).

### 5.4 Tests à prévoir

Sur une base séparée (jamais `aite_dev`), d'abord avec les cinq modules sans hôtel (R), puis avec la suite AITE complète, puisque AH-01 à AH-05 touchent des modules que le client pilote utilise ; avec `pos_restaurant`, `hr`, `pos_hr`, `mrp`, `pos_mrp` ; installation à froid, puis mise à niveau d'une base existante si le client a déjà Odoo (Q4) ; sur Community, puis sur Enterprise s'il l'a. Les essais côté serveur des 12 et 13/11/2026 sont tous à rejouer à l'écran.

1. Installation sans erreur et liste des modules installés d'office : fait côté serveur pour les cinq modules (essai V1) ; à refaire avec la suite complète, et sur Enterprise.
2. Ouverture d'une caisse de restaurant et, s'il en existe déjà une, d'une caisse sans service à table ; écran de paiement avec le bouton d'ardoise ; aucune erreur. Tous les gestes de la salle rejoués sous un compte de caisse « Utilisateur », puis « Administrateur ».
3. Ardoise : aucune ardoise avant validation du paiement ; même test après annulation de la table, division, transfert et réunion.
4. (Avec la suite complète seulement : sans objet pour ce client, R.) Note de chambre et fidélité sur une table : une seule ligne de folio, un seul mouvement de points, y compris après division.
5. (Même condition.) Relecture des commandes par un employé sans profil hôtel : ouverture de la caisse avec des tables en cours, changement de table, annulation.
6. Analyses : même chiffre d'affaires dans l'analyse AITE, le cockpit Direction, le rapport de session et le tableau de bord standard « PdV - Restaurant » ; personnes et tables après une division, une réunion et une annulation ; onglet Paiements avec une table ouverte portant un paiement ; table ouverte à 23 h 30 et payée après minuit ; trois employés sur le même poste.
7. Stock : plat non suivi vendu (pas de « Rupture ») ; plat à fiche technique (sorties d'ingrédients).
8. Marge d'un plat avant, puis après la saisie de sa fiche technique ; plat à fiche technique suivi en stock, valorisé au coût standard puis au coût moyen : coût et marge cohérents.
9. Temps d'enregistrement d'une commande sur une session de plusieurs centaines de commandes, avec deux ou trois postes.
10. (Même condition.) Demande de maintenance créée par une équipière après l'installation de `hr`, si le client a aussi le module gouvernante.
11. Sur la base de développement, `dev/run_tests.sh` toujours vert une fois ces modules installés. Sur la base « restaurant seul », où ce script ne s'applique pas (H28) : les 264 tests Odoo des cinq modules, verts sans données de démonstration (essai V3). À reprendre : les 7 anomalies vues avec ces données, et le test de la journée après minuit, ignoré sans hôtel (H26). Les tests actuels créent les commandes sans passer par la caisse : prévoir des tests qui empruntent le chemin de la caisse.
12. Les points « à vérifier » de la partie 3, à l'écran ; les trois cas tirés des tickets publics (rafraîchir la page en plein service, deux postes sur la même table, réunion de tables puis bon de cuisine) ; deux postes derrière l'hébergement de production, canal temps réel et impression des bons compris.
13. Pour le profil, à l'écran : les points PROF-01 à PROF-08, listés en fin d'annexe C, et les montages A et C (PROF-08).

Les critères d'acceptation de la partie 3 deviendront un nouveau domaine du cahier de recette (le domaine R, après les dix-sept domaines A à Q).

### 5.5 Lien avec la feuille de route

La demande est **hors feuille de route** : aucune des fonctionnalités F01 à F26 ne porte sur le service à table, le plan de salle, les annulations de caisse, les personnes servies, les niveaux d'accès en salle ou les fiches techniques. Elle demande une ligne nouvelle, « Restaurant », et un arbitrage avec la fin de la vague 1 (F05, F07, F08, F09), qui reste le travail en cours. Recoupements (H20) :

| Fonctionnalité | Recoupement |
|---|---|
| F25, portail QR en chambre | S'appuie sur `pos_self_order`, qui dépend de `pos_restaurant` et s'installe avec lui. Les heures de disponibilité d'une famille n'agissent que là (C85). |
| F10, Mobile Money | Même besoin au restaurant ; aujourd'hui saisi comme un moyen de paiement manuel. |
| F05, clôture du jour | Reprend le chiffre d'affaires de caisse et les encaissements par mode ; la question de la journée après minuit s'y pose aussi (H26). |
| F09, routage de la note de chambre | Sans objet pour ce client (R) ; concerné pour un restaurant d'hôtel. |
| F16, minibar | Même mécanique que REST-19 : consommation, stock, recharge. |
| F15, accises et licences par point de vente | La séparation alcoolisé / non alcoolisé de REST-09 peut y servir. |
| F17, mode dégradé hors connexion | Même question que pour la caisse de restaurant. |
| F19, HACCP ; F21, planning des équipes | La cuisine et les employés entrent dans le système avec ce projet. |

### 5.6 Développer plutôt qu'assembler

- **OCA (modules libres revus par les pairs).** La branche 18.0 du dépôt des modules de caisse ne contient aucun module propre au restaurant [8]. Le module de droits par geste (dont « supprimer une ligne ») n'est pas porté en 18.0 : sa migration a été fermée sans fusion [9]. Même chose pour le stock disponible en caisse [10]. Le blocage du stock négatif existe en 18.0, mais il agit sur le mouvement de stock, donc après la prise de commande [11].
- **Cybrosys (code ouvert).** Trois modules en 18.0 touchent nos besoins : blocage des produits épuisés en caisse [13], droits par employé sur les boutons de la caisse [14], écran de cuisine pour Community [15]. Les deux premiers sont sous licence AGPL-3, différente de la LGPL-3 d'AITE HOUSE.
- **Boutique Odoo (payant).** Validation par le code d'un responsable [62°], minuteurs de table [63°] : fiches vues dans les seuls résultats de recherche, non ouvertes.
- **Recommandation.** Développer les contrôles dans AITE HOUSE plutôt qu'empiler des modules de plusieurs éditeurs : aucun ne donne les quatre niveaux, ni un rapport d'annulations commun avec le reste. Ces modules servent de modèles de conception. Aucun n'a été installé ni audité ; la compatibilité des licences est à faire valider (point non sourcé).

---

## 6. Lots proposés

Sans prix ni dates : ils dépendent des réponses de la partie 7, à commencer par la date d'ouverture (Q1). Les efforts sont des estimations ; l'équivalence en jours reste à fixer par AITE (partie 1). Chaque poste a un identifiant, repris dans le tableau 6.5.

### 6.1 Ouvrir sans développement

Si rien n'est développé à temps, le restaurant peut ouvrir avec ce qu'Odoo 18 fait déjà, une fois réglé :

- **Ce qui est là.** REST-04, 05, 07, 09, 13, 14, 16, 18 et 24 ; REST-01 (connexion par code, sans le contrôle du code obligatoire et unique) ; REST-08 (client enregistré) ; REST-15 (en deux gestes, à vérifier) ; REST-23 (filtres par famille) ; REST-25 et REST-26 (tableau de bord standard, à contrôler à l'écran).
- **Réglages de protection.** « Contrôle des prix » coché ; « Remises appliquées à la ligne » décoché et « Remises globales » non activé ; « Suivi des modifications de commandes » coché.
- **Ce qui manque alors.** On ne sait pas de façon fiable qui a ouvert et qui a encaissé (REST-02) ; le serveur et la caissière ont les mêmes droits (REST-03) ; le nombre de personnes n'est pas demandé (REST-06) ; une commande envoyée se retire sans code (REST-10, 11, 12, 22) ; aucune alerte de couleur (REST-17) ; la vente n'est pas refusée à stock nul (REST-19) ; le tableau de bord standard compte chaque vente sans table et chaque remboursement comme une personne, chaque division comme une addition (REST-25) ; tout employé peut vendre sans table (PROF-04).

### 6.2 Lot 1 — À l'ouverture

- **Exigences.** Les dix-neuf que nous classons indispensables d'après les mots du client, à confirmer avec lui (Q1) : REST-01, 02, 03, 04, 05, 06, 07, 09, 10, 11, 12, 16, 17, 18, 19, 22, 23, 24 et 25. S'y ajoutent, parce qu'elles existent déjà : REST-13, REST-14 (si la division se fait par produits), REST-26, REST-08 par le bouton « Client », et REST-15 en deux gestes si l'essai à l'écran le confirme. REST-20 rejoint ce lot, sans aucune fiche, si le client veut la fonction dès l'ouverture (Q13).
- **Réglages et saisies (PARAM-01 à PARAM-08, PARAM-10).** Installation du service à table, de la connexion par code et de l'inventaire ; compte de la caisse, compte du manager avec ses droits (Employés / Responsable compris), comptes des lecteurs de rapports. Réglages : « Est un bar/restaurant », « Plan des salles & des tables », « Se connecter avec Employés », « Contrôle des prix », les deux remises désactivées, « Autoriser le partage d'addition » (à cocher si la caisse existait déjà), « Imprimantes de préparation », « Suivi des modifications de commandes », « Suivre l'inventaire ». Dessin du plan de salle. Saisie de la carte en trois niveaux, chaque produit ayant sa catégorie de caisse (sinon « Commander » ne répond pas) et le même rangement dans les deux classements. Saisie des employés, des codes, des niveaux et du stock de départ. Essai du matériel sur place. Filtres favoris des rapports et contrôle à l'écran du tableau de bord standard. Base créée avec le pays Cameroun ; devise et plan comptable contrôlés avant toute écriture (PARAM-10). **Nés du profil, selon les réponses :** les réglages de PROF-01, PROF-03, PROF-05 et PROF-08 (tableau 6.5), dont les options « Variantes » et « Unités de mesure » des paramètres et l'unité centilitre, à créer ; la vente à la dose (PROF-07) et la fiche technique par taille (PROF-01) demandent l'application Fabrication : dès ce lot si le client le veut (Q13), sinon au lot 3 (PARAM-09) ; « Manger sur place / À emporter » reste décoché (PROF-04).
- **Développements.** Code obligatoire et unique (REST-01, S) ; ouverte par, encaissée par, journal des saisies (REST-02, M) ; code demandé avant d'ouvrir une table, avant d'encaisser et après chaque envoi (REST-02-P1, S) ; quatre niveaux et tableau des droits, remboursement et espèces compris (REST-03, L) ; nombre de personnes obligatoire, table réservée dès la validation, zéro refusé, 0 personne sur une vente sans table (REST-06, REST-07-P1, S) ; verrou après envoi sur tous les chemins de retrait, annulation d'une table et fermeture avec des tables ouvertes comprises (REST-10, M) ; code du supérieur (REST-11, M) ; trace des annulations et motifs (REST-12, M) et leur rapport (REST-22, S) ; couleur de la table selon la durée, plan toujours affiché (REST-17, M) ; refus de vente à stock nul, volet 19a (M), puis 19b à 19d selon les réponses ; comptage exact des personnes et des tables, remboursements exclus, ventes sans table à part (REST-25-P1, S à M) ; sous-totaux par niveau de famille (REST-23-P1, S) ; case qui tient la vente sans table fermée (PROF-04-P1, S). REST-10, 11, 12 et 22 se conçoivent ensemble, et avec REST-13, 14 et 15, pour distinguer le retrait du déplacement.
- **Corrections dans AITE HOUSE, avant toute mise en service.** Ardoise créée seulement sur une commande réglée, et annulée quand la commande l'est (AH-01) ; décision de proposer ou non l'ardoise au restaurant, bouton d'ardoise selon le niveau (AH-02) ; nom de l'employé dans les analyses (AH-03) ; profil de lecture des rapports, pour que le chef de salle lise le rapport des annulations (AH-05) ; étude comparative corrigée (AH-10) ; fiches d'applications et cartes héritées du client pilote (AH-11) ; installation « restaurant seul » (AH-12) ; campagne de tests de la partie 5.4 (TEST-01) ; formation et service d'essai (FORM-01).
- **Dépend de.** Les questions encore ouvertes de la partie 7.1 (Q1, Q2, Q4 à Q13, Q77, Q78) et la confirmation de Q3, Q64 et Q65 ; puis, avec un choix par défaut si le client ne répond pas : Q14, Q15, Q16, Q17, Q18, Q19, Q21, Q22, Q23, Q24, Q29, Q35, Q37, Q38, Q43, Q45, Q46, Q48, Q50, Q51, Q59, Q66, Q67, Q69, Q70, Q76, Q79, Q80, Q83 ; et l'essai à l'écran des points « à vérifier ».
- **Si la date d'ouverture est proche.** Les développements les plus lourds sont REST-03 et REST-19, puis le bloc REST-10 à REST-12. **Proposition de repli, à décider avec le client :** pour REST-19, s'en tenir au volet 19a sur les boissons revendues à l'unité, dont le stock est simple à tenir ; pour REST-03, commencer par les gestes que le client a nommés (annuler, produits, prix) et par l'encaissement, puis compléter le tableau ; pour REST-11, le verrou par niveau et « Changer de caissier » par le supérieur, en attendant la fenêtre « Code du supérieur » ; pour REST-25 et REST-26, le tableau de bord standard et la vue croisée des commandes avec la mesure « Convives », en attendant le comptage exact, en sachant qu'ils comptent les ventes sans table et les remboursements comme des personnes (Q76).

### 6.3 Lot 2 — Dans les semaines qui suivent

- **Exigences.** REST-08 (nom libre sur la table, à l'ouverture ou après) ; selon les réponses du client : REST-09-P1 (premier écran réduit aux deux familles), REST-14-P1 (division en parts égales), REST-15-P1 (déplacement en un seul geste).
- **Développements, selon les réponses du client.** Délai d'inactivité (REST-02-P2) ; tableau des droits modifiable à l'écran (REST-03-P2) ; écran « Équipe de salle » pour le manager (REST-04-P2) ; numéro de table inconnu refusé (REST-05-P1) ; verrou étendu au remboursement et à la modification après impression (REST-10-P1) ; trace des déplacements (REST-15-P2) ; informations sur la table (REST-16-P1) ; palier rouge et remise à zéro de l'alerte (REST-17-P1, REST-17-P2) ; écran d'entrée de stock rapide (REST-18-P1) ; volets 19b à 19d s'ils n'ont pas été livrés au lot 1 ; prix moyen par table (REST-26-P1) ; remises et produits offerts autorisés par un supérieur, avec explication (COMP-01) ; retraits avant envoi comptés par serveur (COMP-02) ; saisie de la casse et des pertes (COMP-03). Nés du profil, si le client les demande : les développements de PROF-01 à PROF-03, de PROF-06 et de PROF-07. Options (R), si et le jour où le client les ouvre (Q78) : PROF-04, PROF-04-P2, PROF-04-P3, PARAM-11, AH-13, PROF-08-P1 (tableau 6.5).
- **Dans AITE HOUSE.** Tableau de bord du stock sans les plats non suivis (AH-06) ; personnes et tables dans le cockpit Direction (AH-07) ; jeu de démonstration « restaurant » (AH-08) ; traductions (AH-09) ; cas de recette du domaine R (TEST-02).
- **Dépend de.** Le lot 1 en service ; Q20, Q25, Q26, Q27, Q28, Q31, Q34, Q39, Q40, Q42, Q44, Q47, Q53, Q68, Q71 à Q75, Q81, Q82.

### 6.4 Lot 3 — Plus tard

- **Exigences.** REST-20 (fiches techniques) et REST-21 (rentabilité).
- **Réglages (PARAM-09).** Installation de l'application Fabrication, si elle n'a pas été faite au lot 1 ; droit Fabrication / Administrateur pour le manager ; choix de la méthode de valorisation des familles ; premières fiches sur les plats les plus vendus ; formats et doses du bar, s'ils ne l'ont pas été au lot 1 (PROF-07).
- **Développements.** Écran « Fiche technique » (REST-20-P1, M) ; source unique de coût, report du coût, plats sans coût, recalcul des marges (REST-21 et AH-04, M).
- **Propositions à discuter le moment venu.** Comparer chaque mois ce que les fiches prévoient de consommer et ce que les inventaires constatent [46°].
- **Dépend de.** Un stock tenu (REST-18) et des inventaires réguliers (Q43) ; le choix des unités (Q45) ; les réponses sur les fiches (Q13, Q63).

### 6.5 Postes à chiffrer

Un poste par ligne. « à estimer » : aucun effort n'a encore été évalué. « Qui » : AITE, sauf mention du client. PROF-01 à PROF-08 viennent du profil (P), PROF-04-P1 à P3 et PROF-08-P1 des réponses (R) ; PROF-04-P1 est classé S par analogie avec REST-05-P1.

| Poste | Contenu | Lot | Effort | Dépend de | Qui |
|---|---|---|---|---|---|
| REST-01 | Code obligatoire et unique | 1 | S | Q18 | AITE |
| REST-02 | Ouverte par, encaissée par, journal des saisies | 1 | M | Q14 | AITE |
| REST-02-P1 | Code demandé avant d'ouvrir une table, avant d'encaisser, après chaque envoi | 1 | S, avec P2 | Q17 | AITE |
| REST-02-P2 | Code redemandé après un moment sans activité | 2 | compris dans P1 | Q17 | AITE |
| REST-03 | Quatre niveaux ; tableau des droits fixe (REST-03-P1) | 1 | L | Q8 | AITE, tableau rempli avec le client |
| REST-03-P2 | Tableau des droits modifiable à l'écran | 2 | à estimer | décision d'AITE | AITE |
| REST-04-P2 | Écran « Équipe de salle » pour le manager (codes, employés) | 2 | à estimer | décision d'AITE | AITE |
| REST-05-P1 | Numéro de table inconnu refusé | 2 | S | Q25, Q64 | AITE |
| REST-06, REST-07-P1 | Nombre de personnes obligatoire ; table réservée dès la validation ; zéro refusé ; tables nées d'un déplacement ; 0 personne sans table | 1 | S | Q29, Q76 | AITE |
| REST-08 | Nom libre sur la table, à l'ouverture ou après, lu sur le plan et l'addition | 2 | S | Q27, Q71 | AITE |
| REST-09-P1 | Premier écran réduit aux deux familles | 2 | à estimer | Q31 | AITE |
| REST-10 | Verrou après envoi, sur tous les chemins de retrait | 1 | M | Q6, Q37 | AITE |
| REST-10-P1 | Verrou étendu au remboursement et à la modification après impression | 2 | à estimer | Q37 | AITE |
| REST-11 | Fenêtre « Code du supérieur » | 1 | M | Q21 | AITE |
| REST-12 | Trace des annulations ; journal non modifiable (P1) ; motifs (P2) | 1 | M | Q9, Q35 | AITE |
| REST-14-P1 | Division du total en parts égales | 2 | à estimer | Q10 | AITE |
| REST-15-P1 | Déplacement en un seul geste | 2 | M | Q28 | AITE |
| REST-15-P2 | Trace des déplacements ; code pour la table d'un collègue | 2 | S | Q19 | AITE |
| REST-16-P1 | Informations sur la table du plan | 2 | à estimer | Q40 | AITE |
| REST-17 | Alerte de couleur, durée affichée, plan toujours visible | 1 | M | Q11, Q38 | AITE |
| REST-17-P1, REST-17-P2 | Palier rouge ; remise à zéro de l'alerte | 2 | à estimer | Q39 | AITE |
| REST-18-P1 | Écran d'entrée de stock rapide | 2 | S | Q42 | AITE |
| REST-19a | Refus de vente à stock nul | 1 | M | Q12, Q45 | AITE |
| REST-19b | Décompte dès l'envoi, entre les postes | 1 ou 2 | M | Q46 | AITE |
| REST-19c | Quantité restante sur le bouton | 1 ou 2 | S | Q12 | AITE |
| REST-19d | Passage en force par un supérieur, tracé | 1 ou 2 | S | Q44 | AITE |
| REST-20-P1 | Écran « Fiche technique » | 3 | M | Q63 | AITE |
| REST-21, AH-04 | Source unique de coût, report du coût, plats sans coût, recalcul des marges ; coût par taille et par supplément (à estimer) | 3 | M | Q52, Q63 | AITE |
| REST-22 | Rapport des annulations | 1 | S | Q22 | AITE |
| REST-23-P1 | Sous-totaux par niveau de famille | 1 | S | Q48 | AITE |
| REST-25-P1 | Comptage exact des personnes et des tables ; remboursements exclus ; ventes sans table comptées à part | 1 | S à M, à confirmer | Q29, Q50, Q51, Q76 | AITE |
| REST-26-P1 | Prix moyen par table ; mention toutes taxes ou hors taxes | 2 | S | Q52, Q53, Q76 | AITE |
| COMP-01 | Remises et produits offerts autorisés par un supérieur | 2 | à estimer | Q20 | AITE |
| COMP-02 | Retraits avant envoi comptés par serveur | 2 | à estimer | Q34 | AITE |
| COMP-03 | Saisie de la casse, des pertes et des repas du personnel | 2 | à estimer | Q47 | AITE |
| PROF-01 | Tailles et suppléments (réglage) ; fiche technique par taille (réglage, avec PARAM-09) ; supplément au prix selon la taille (développement) | 1 ; 1 ou 3 ; 2 | à estimer | Q13, Q66, Q67 | AITE, carte du client |
| PROF-02 | Pizza moitié-moitié : remarque pour la cuisine, puis mécanisme et règle de prix (développement) | 2 | à estimer | Q68 | AITE |
| PROF-03 | Formules (réglage) ; chiffre par formule dans les rapports (développement) | 1 ; 2 | à estimer | Q69 | AITE |
| PROF-04 | Option de vente sans table, le jour venu : « à emporter », produit « Frais de livraison », favoris | 2 | à estimer | Q64, Q72, Q78, Q81, Q82 | AITE |
| PROF-04-P1 | Case « Autoriser la vente sans table » par caisse, décochée par défaut | 1 | S | Q8, Q64, Q78 | AITE |
| PROF-04-P2 | Type de vente posé à l'ouverture et compté à part ; taxe gardée au choix du client ; nom et client imprimés | 2 | à estimer | Q71, Q76, Q81 | AITE |
| PROF-04-P3 | Livraison suivie : heure promise, livreur, statut, courses non réglées, alerte à la fermeture | 2 | à estimer | Q72, Q82 | AITE |
| PROF-05 | Une imprimante par poste de préparation, familles rattachées | 1 | à estimer, avec PARAM-02 | Q2, Q6 | AITE |
| PROF-06 | Délai d'alerte, rapports, carte ou prix selon le moment de la journée (développement) | 2 | à estimer | Q11, Q38, Q53, Q73, Q74 | AITE |
| PROF-07 | Bar : formats, doses, unités (réglage) ; alerte de durée sur une addition sans table laissée ouverte (développement, si le client la demande) | 1 ou 3 ; 2 | à estimer, avec PARAM-09 | Q45, Q75 | AITE, doses du client |
| PROF-08 | Une seule caisse, ouverte sur chaque poste (montage A) ; familles « bar » | 1 | à estimer, avec PARAM-01 | Q65, Q77, Q83 | AITE, choix du client |
| PROF-08-P1 | Encaisser une table depuis la caisse du bar (options 1 et 2) | 2 | à estimer (défauts du montage B) | Q78 à Q80 | AITE |
| AH-01 | Ardoise créée sur une commande réglée seulement ; annulée avec elle | 1 | à estimer | — | AITE |
| AH-02 | Ardoise proposée ou non au restaurant ; bouton selon le niveau | 1 | à estimer | Q56 | AITE |
| AH-03 | Nom de l'employé dans les analyses (module passerelle) | 1 | à estimer | — | AITE |
| AH-05 | Profil de lecture des rapports | 1 | à estimer | Q22 | AITE |
| AH-06 | Tableau de bord du stock sans les plats non suivis | 2 | à estimer | — | AITE |
| AH-07 | Personnes et tables dans le cockpit Direction | 2 | à estimer | — | AITE |
| AH-08 | Jeu de démonstration « restaurant » | 2 | à estimer | — | AITE |
| AH-09 | Traductions | 2 | à estimer | — | AITE |
| AH-10 | Étude comparative corrigée | 1 | à estimer | — | AITE |
| AH-11 | Fiches d'applications et cartes héritées du client pilote | 1 | à estimer | — | AITE |
| AH-12 | Installation et environnement « restaurant seul » | 1 | à estimer | — | AITE |
| AH-13 | « Ardoise client » sur toute nouvelle caisse | 2 | à estimer | Q78 | AITE |
| PARAM-01 | Installation ; compte de la caisse, compte du manager, comptes des lecteurs | 1 | à estimer | Q4 | AITE |
| PARAM-02 | Réglages de la caisse | 1 | à estimer | Q6 | AITE |
| PARAM-03 | Dessin du plan de salle | 1 | à estimer | Q2 | AITE, avec le client |
| PARAM-04 | Saisie de la carte : familles, produits, prix | 1 | à estimer | Q7, Q48, Q66, Q69, Q70 | le client fournit, AITE saisit |
| PARAM-05 | Employés, codes, niveaux | 1 | à estimer | Q7, Q8 | le client fournit, AITE saisit |
| PARAM-06 | Stock de départ | 1 | à estimer | Q7, Q43 | le client compte, AITE saisit ou forme |
| PARAM-07 | Matériel : imprimantes, tablettes, réseau, essai sur place | 1 | à estimer | Q5, Q60 | le client achète, AITE essaie |
| PARAM-08 | Filtres favoris des rapports ; tableau de bord standard contrôlé à l'écran | 1 | à estimer | Q49 | AITE |
| PARAM-09 | Fabrication, méthode de valorisation, premières fiches | 3 | à estimer | Q63 | AITE, avec le client |
| PARAM-10 | Base créée avec le pays Cameroun ; devise et plan comptable contrôlés | 1 | à estimer | Q4, Q55 | AITE |
| PARAM-11 | Caisse du bar (option 1), un soir, principale fermée ; le chiffre par caisse change alors de sens | 2 | à estimer | Q77, Q78 | AITE, avec le client |
| TEST-01 | Campagne de tests de la partie 5.4 | 1 | à estimer | — | AITE |
| TEST-02 | Cas de recette du domaine R | 2 | à estimer | — | AITE |
| FORM-01 | Formation par niveau d'accès ; service d'essai | 1 | à estimer | Q62 | AITE, avec le client |

---

## 7. Questions au client

Dix-sept questions conditionnent le démarrage (Q1 à Q13, Q64, Q65, Q77 et Q78) : elles sont à poser de vive voix ou par message vocal, une à la fois ; Q3, Q64 et Q65 portent déjà une réponse (R), à confirmer. Pour les 66 autres, notre choix par défaut est indiqué : le client n'a à répondre que s'il veut autre chose. Les numéros sont ceux cités dans les parties 1 à 6. Q64 à Q76 viennent de ce que nous savons de l'établissement sans le tenir des messages ; « D'après nos informations (P) » le signale, à corriger si c'est inexact. Q77 à Q83 découlent de ces réponses.

*Note pour AITE : joindre à l'envoi le tableau des droits de la fiche REST-03, auquel renvoie la question Q8, le tableau de synthèse réduit à ses colonnes « Réf. », « Exigence », « Priorité », « À l'ouverture » et « État », et la liste « hors périmètre » (4.6).*

### 7.1 À décider avant de commencer

Sans ces réponses, ni devis ni calendrier. La dernière colonne donne l'hypothèse sur laquelle AITE travaille en attendant.

| N° | Question | Hypothèse de travail, en attendant |
|---|---|---|
| **Q1** | À quelle date ouvrez-vous ? Parmi vos demandes, lesquelles doivent absolument fonctionner ce jour-là ? | Aucune : sans date, nous ne pouvons pas proposer de calendrier. |
| **Q2** | Combien aurez-vous de salles, de tables, de postes de caisse, de tablettes, de postes de préparation (cuisine, bar, four à pizza) et d'employés à chacun des quatre niveaux ? | Aucune : sans ces nombres, pas de devis. D'après nos informations (P) : « bar et cuisine », sans nombre ; une caisse principale, unique ; le bar qui encaisse, en option (R, Q65). |
| **Q3** | Votre établissement est-il bien un restaurant seul, sans chambres d'hôtel ? | D'après nos informations (R), à confirmer : un restaurant seul, sans chambres. |
| **Q4** | Utilisez-vous déjà le logiciel Odoo pour une autre activité, et voulez-vous le système installé sur un ordinateur chez vous ou en ligne, chez un hébergeur ? | Vous n'utilisez pas encore Odoo ; nous choisissons l'hébergement avec vous. |
| **Q5** | Quel matériel avez-vous déjà acheté (imprimantes, tablettes, tiroir-caisse : marque et modèle) ? | Aucun matériel n'est encore acheté. |
| **Q6** | Où doit arriver une commande envoyée : un bon imprimé en cuisine, un autre au bar, un autre au four à pizza, ou un écran ? | Un bon en cuisine, pizzas comprises, et un autre au bar. D'après nos informations (P) : « bar et cuisine », lus comme deux postes de préparation. |
| **Q7** | Qui nous fournira la carte (produits, familles, prix), le plan de la salle, la liste des employés et le stock de départ, et pour quelle date ? | Aucune : sans ces données, la caisse reste vide. |
| **Q8** | Pouvons-nous remplir avec vous le tableau des droits joint : qui encaisse, qui annule, qui rembourse, qui pourrait ouvrir une vente sans table, si vous en faites, qui ouvre et qui ferme la caisse ? Une séance d'une heure suffit. | Chaque case « à trancher » du tableau vaut « non ». |
| **Q9** | Vous dites que les chefs de salle « vont expliquer dans leur rapport ». De quel rapport parlez-vous : un compte rendu qu'ils vous font en fin de service, ou une liste que la caisse sort à leur nom, avec l'explication écrite dans la caisse au moment de l'annulation ? | L'explication est choisie dans la caisse au moment de l'annulation, et la caisse sort la liste. |
| **Q10** | Vous dites avoir déjà précisé comment réunir et diviser les tables : nous ne trouvons pas cette précision dans les messages reçus. Diviser en deux, est-ce (a) sortir certains produits sur une seconde facture, (b) couper le total en deux parts égales, ou (c) séparer deux tables qu'on avait réunies ? | (a) : on sort certains produits sur une seconde facture. |
| **Q11** | Combien de temps dure normalement un repas chez vous, et la table doit-elle passer à l'orange à une heure ou à une heure trente ? | La table passe à l'orange à une heure. |
| **Q12** | Quels produits la caisse doit-elle refuser quand il n'y en a plus : les boissons en bouteille seulement, ou aussi les plats et les pizzas ? | Les boissons vendues à l'unité seulement ; ni les pizzas ni le café, faits d'ingrédients. |
| **Q13** | Message 8 : parlez-vous bien des fiches techniques, c'est-à-dire des recettes avec la quantité de chaque ingrédient ? Voulez-vous que la fonction soit déjà là le jour de l'ouverture, vide, pour la remplir peu à peu, ou peut-elle arriver plus tard ? | Il s'agit bien des recettes ; la fonction arrive après l'ouverture. |
| **Q64** | Vendez-vous aussi sans table : au comptoir ou au bar, à emporter, en livraison ? | D'après nos informations (R), à confirmer : tout se vend à table ; la vente à emporter, au comptoir et en livraison est prévue, sans être activée (Q72, Q78). |
| **Q65** | Le bar encaisse-t-il lui-même, avec son propre tiroir-caisse, ou tout s'encaisse-t-il au même endroit ? | D'après nos informations (R), à confirmer : une seule caisse, la principale ; prévus, sans être activés : un tiroir-caisse au bar, avec sa monnaie de départ et sa fermeture ; le bar qui encaisse aussi les tables (Q77 à Q80). |
| **Q77** | En temps normal, le bar encaisse-t-il, ou tout se paie-t-il à la caisse principale ? Le soir, comptez-vous l'argent une seule fois ? Le bar a-t-il son propre tiroir-caisse, avec sa monnaie de départ ? | Tout se paie à la caisse principale : un comptage, un tiroir-caisse ; si le bar encaisse un jour, son argent y est porté avant le comptage. |
| **Q78** | Tiroir-caisse propre au bar, vente à emporter, au comptoir, en livraison : si vous les voulez, dès l'ouverture ou plus tard ? | Plus tard ; le tiroir du bar s'ajoute un soir, caisse fermée, la vente sans table à tout moment. |

### 7.2 Nos choix par défaut, à corriger si besoin

Pour chaque ligne, la dernière colonne dit ce que nous ferons sans réponse de votre part. Les lignes qui commencent par « Message » portent sur un passage peu audible, ou que nous lisons de deux façons.

#### A. Les codes et les niveaux d'accès

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q14** | Message 1 : quand vous dites que Valérie « a tapé une table » (mot peu audible), voulez-vous dire qu'elle a ouvert la table, ou qu'elle y a saisi la commande ? | Nous gardons les trois noms : qui a ouvert la table, qui a saisi chaque produit, qui a encaissé. |
| **Q15** | Message 1, « elle a ouvert le système » : qui ouvre la caisse en début de service ? | La caissière ou un supérieur, chacun avec un compte personnel ; les serveurs n'ouvrent pas la caisse. |
| **Q16** | Vous-même, quel niveau d'accès aurez-vous ? | Celui du manager. |
| **Q17** | Vous dites qu'on entre son code avant d'ouvrir une table et pour encaisser. Faut-il le redemander aussi après chaque envoi de commande, et après un moment sans activité ? | Le code est demandé avant d'ouvrir une table, avant d'encaisser et après chaque envoi ; pas de délai d'inactivité au départ. |
| **Q18** | Un code à quatre chiffres par personne vous convient-il, ou voulez-vous en plus un badge pour les chefs de salle et le manager, pour que leur code ne soit pas vu par les serveurs ? | Un code à quatre chiffres pour tous ; pas de badge au départ. |
| **Q19** | Un serveur peut-il compléter ou encaisser la table d'un collègue, et peut-il réunir, diviser ou déplacer seul ? | Un serveur ne modifie que ses propres tables, où il peut réunir, diviser et déplacer ; la caissière et les supérieurs accèdent à toutes les tables. |
| **Q20** | Qui peut accorder une remise ou offrir un produit, et jusqu'à quel montant ? | À l'ouverture, aucune remise n'est possible en caisse ; ensuite, remises et produits offerts sont réservés aux supérieurs, avec une explication. |
| **Q21** | La caissière peut-elle annuler ce qu'un serveur a envoyé, ou seulement le chef de salle, les superviseurs et le manager ? | Seulement le chef de salle, les superviseurs et le manager. |
| **Q22** | Qui, en dehors du manager, doit consulter les rapports, et depuis quel appareil ? | Le chef de salle lit le rapport des annulations, depuis un ordinateur ou une tablette, avec un compte personnel ; la caissière ne lit que la fermeture de caisse. |
| **Q23** | Message 10 : le manager a-t-il accès à tout, sans exception, et à quoi pensez-vous par « et autres » ? | Le manager a accès à tout. |

#### B. Les tables

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q24** | Pour ouvrir une table, préférez-vous toucher la table sur le plan de salle, ou que la caisse vous demande son numéro au clavier ? | On touche la table sur le plan ; le numéro au clavier reste possible. |
| **Q25** | Vous arrive-t-il d'ouvrir une table qui n'est pas sur le plan, ou la caisse doit-elle refuser un numéro qui n'existe pas ? | La caisse ne refuse pas : un numéro inconnu ouvre une facture à ce nom. |
| **Q26** | Quand vous retirez un produit pour « créer une nouvelle table », est-ce une table du plan encore libre, ou une facture à part pour des clients assis à la même table ? | Les deux sont possibles. |
| **Q27** | Pour le nom du client ou de la société, un simple nom écrit sur la table suffit-il, ou voulez-vous des clients enregistrés, pour une facture officielle au nom de la société (différente de la facture de la table) ou pour un compte à régler plus tard ? | Un simple nom, facultatif ; un client n'est enregistré que s'il lui faut une facture officielle ou un compte. |
| **Q28** | Pour déplacer un produit vers une autre table, deux gestes à la suite (sortir le produit, puis choisir la table) vous conviennent-ils, ou faut-il un seul geste ? | Deux gestes au départ. |
| **Q29** | Quand on réunit deux tables, additionne-t-on leurs personnes ? Quand on divise une table, ou qu'un produit part ouvrir une nouvelle table, combien de personnes y compte-t-on ? | Réunion : on additionne. Division : toutes les personnes restent comptées sur la table d'origine. Nouvelle table : la caisse demande son nombre de personnes. |
| **Q30** | Message 4 : nous comprenons quatre gestes — réunir des tables, diviser une table, déplacer un produit vers une table déjà ouverte, retirer un produit pour créer une nouvelle table. Y en a-t-il un cinquième ? | Ces quatre gestes. |
| **Q79** | Un client qui commence au bar puis s'installe à une table : paie-t-il au bar avant, ou ce qu'il a bu s'ajoute-t-il à l'addition de sa table ? | Ce qu'il a bu s'ajoute à sa table ; avec un tiroir au bar, il paie au bar avant. |
| **Q80** | Le barman peut-il encaisser l'addition d'une table de la salle ? Tous les barmen, ou seulement un responsable ? | Non en temps normal ; si vous l'ouvrez, tout employé qui encaisse (Q8). |

#### C. La prise de commande

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q31** | Juste après l'ouverture de la table, voulez-vous voir seulement les deux touches Nourriture et Boisson, ou acceptez-vous que des produits s'affichent déjà en dessous ? | L'écran standard : les deux touches en haut, des produits en dessous. |
| **Q32** | Fin du message 5, « quand je rentre avant » : voulez-vous dire qu'on doit pouvoir revenir d'un niveau en arrière ? | Oui : on revient d'un niveau en retouchant la famille. |
| **Q33** | Avez-vous des remarques pour la cuisine (cuisson, sans piment), et des entrées envoyées avant les plats ? | Les remarques seulement : une remarque libre sur chaque produit ; pas d'envoi en plusieurs temps au départ. Les formules font l'objet de Q69. |
| **Q34** | Avant l'envoi, le serveur corrige librement ses erreurs de saisie : voulez-vous quand même que ces retraits soient comptés par serveur ? | Non. |

#### D. Les annulations

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q35** | Voulez-vous qu'une explication soit choisie dans une liste à chaque annulation, y compris quand c'est le manager qui annule ? Liste proposée : erreur de saisie, client parti, plat refusé, produit manquant, autre. | Oui, pour tous, avec cette liste. |
| **Q36** | Un plat déjà préparé puis annulé est-il compté comme une perte ou remis en stock, et voulez-vous distinguer « annulé » et « offert » ? | L'explication dit si le produit est perdu ; un produit perdu sort du stock ; pas de produit « offert » au départ. |
| **Q37** | Le code d'un supérieur et l'explication valent-ils aussi pour : (a) l'annulation d'une table entière ; (b) la baisse d'une quantité déjà envoyée ; (c) le remboursement d'une facture déjà payée ; (d) toute modification après l'impression de la facture de la table ; (e) les tables encore ouvertes au moment de fermer la caisse ? Répondez par oui ou par non pour chacune. | Oui pour les cinq : (a), (b) et (e) dès l'ouverture ; (c) et (d) ensuite. |

#### E. Le plan de salle

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q38** | Un seul délai pour tout le restaurant, le matin, le midi et le soir, compté depuis l'ouverture de la table, avec le vert puis l'orange : cela vous convient-il ? | Oui. |
| **Q39** | Voulez-vous en plus : (a) un second signal, rouge, quand la durée normale du repas est dépassée ; (b) que l'alerte s'arrête quand la facture de la table a été imprimée ; (c) que le serveur puisse la remettre à zéro quand il a vérifié que le client reste ? | Non pour les trois au départ : pas de rouge ; l'alerte dure jusqu'à l'encaissement ; pas de remise à zéro. |
| **Q40** | Que voulez-vous lire sur chaque table du plan : la durée, le nombre de personnes, le montant, le nom du serveur, le nom du client ? | Le numéro, la durée et le nombre de personnes. |
| **Q41** | Message 11 : dites-vous qu'il arrive que le client parte sans que sa facture lui ait été présentée ? | Nous le comprenons ainsi. |

#### F. Le stock

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q42** | Quand vous parlez de « trucs de petite quantité », s'agit-il des produits dont vous avez peu d'unités, des petits achats faits sans bon de commande, ou des ingrédients utilisés à petite dose (épices, huile) ? | Tout produit que vous voulez suivre a son stock saisi, même s'il y en a peu. |
| **Q43** | Qui saisira le stock, et à quel rythme ferez-vous l'inventaire ? | Le stock de départ est saisi avant l'ouverture ; ensuite, un inventaire complet chaque mois. |
| **Q44** | Si la caisse dit « épuisé » alors que le produit est bien là, qui a le droit de forcer la vente ? | Un supérieur, avec son code ; le passage en force est enregistré. |
| **Q45** | Quelles boissons vendez-vous au verre ou à la dose (vin, whisky), et combien de verres ou de doses comptez-vous par bouteille ? | Au départ, seules les boissons vendues à l'unité sont refusées quand le stock est épuisé. |
| **Q46** | Le stock doit-il baisser dès l'envoi de la commande, pour que deux serveurs ne vendent pas la même dernière bouteille, ou seulement au paiement ? | Dès l'envoi. |
| **Q47** | Comment voulez-vous noter la casse, les pertes et les repas du personnel ? | Comme des sorties de stock avec une explication, saisies par un supérieur ; les repas du personnel ne passent pas par la caisse. |

#### G. Les rapports

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q48** | Les familles des rapports sont-elles celles de l'écran de commande ? « Le poulet » est-il une famille de votre carte, ou voulez-vous retrouver tous les plats au poulet, où qu'ils soient rangés ? | Les familles de l'écran de commande ; chaque produit dans une seule famille ; le rapport se filtre sur une famille, une sous-famille ou un produit. |
| **Q49** | Vous demandez « tous les rapports ». Voici la liste de départ : annulations ; ventes par famille et par produit ; ventes par serveur et par caissière ; personnes et tables servies ; prix moyen par personne ; fermeture de caisse. Lesquels manquent ? | Cette liste. |
| **Q50** | Quand vous dites « la quantité vendue divisée par le nombre de personnes », parlez-vous du montant des ventes en FCFA, ou du nombre d'articles vendus ? | Le rapport donne les deux ; le prix moyen se calcule sur le montant. |
| **Q51** | « Pendant qu'on ferme » : parlez-vous de la fermeture de chaque table, ou de la fermeture de la caisse le soir ? | Les personnes sont comptées à l'encaissement de chaque table, et leur total figure sur le rapport de fin de journée. |
| **Q52** | Vos prix à la carte sont-ils toutes taxes comprises, et les montants des rapports se lisent-ils après les remises ? | Oui aux deux. |
| **Q53** | Le prix moyen se calcule-t-il par personne seulement ou aussi par table, et faut-il séparer le matin, le midi et le soir ? | Par personne et par table ; sans séparer les moments de la journée au départ. |
| **Q54** | Une table ouverte à 23 h 30 et payée à 0 h 20 compte-t-elle pour la veille ? | Oui : la journée va de l'ouverture à la fermeture de la caisse. |
| **Q55** | Votre comptable vous impose-t-il des règles sur les tickets, leur numérotation, la conservation des annulations ou la facture officielle remise à une société ? | Aucune règle particulière. |

#### H. Le paiement, les pannes, le démarrage

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q56** | Quels moyens de paiement acceptez-vous : espèces, Mobile Money (MTN, Orange), carte, compte client ? | Les espèces, et le Mobile Money saisi à la main, sans liaison avec l'opérateur. |
| **Q57** | Les pourboires passent-ils par la caisse ? | Non. |
| **Q58** | La facture de la table est-elle imprimée et présentée avant le paiement ? | Oui. |
| **Q59** | En cas de coupure d'internet en plein service, la caisse doit-elle continuer à vendre sans contrôle de stock et sans annulation possible, ou s'arrêter ? | Elle continue à vendre. |
| **Q60** | Avez-vous un onduleur pour la caisse, les imprimantes et le Wi-Fi, et le Wi-Fi couvre-t-il toute la salle et la terrasse ? | Nous le vérifierons sur place avant l'ouverture. |
| **Q61** | Avec quel logiciel de caisse avez-vous déjà travaillé, s'il y en a un dont vous voulez retrouver les habitudes ? | Aucun. |
| **Q62** | Combien de personnes faut-il former, et pouvons-nous faire un service d'essai avant l'ouverture ? | Une séance par niveau d'accès et un service d'essai. |

#### I. Les fiches techniques

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q63** | Par quels plats voulez-vous commencer les fiches techniques, et qui les saisira ? | À voir ensemble après l'ouverture. |

#### J. Le profil de l'établissement

| N° | Question | Sauf avis contraire, nous retenons |
|---|---|---|
| **Q66** | Vos pizzas se vendent-elles en plusieurs tailles, et avec des suppléments payants ? | Nous suivons votre carte ; taille et suppléments se choisissent à la commande, sur une seule touche par pizza. |
| **Q67** | Un même supplément coûte-t-il plus cher sur une grande pizza que sur une petite ? | Non : un prix par supplément. |
| **Q68** | Vendez-vous des pizzas moitié-moitié et, si oui, à quel prix ? | Pas de moitié-moitié en caisse au départ : le serveur saisit l'une des deux pizzas et écrit la demande en remarque pour la cuisine. |
| **Q69** | Vendez-vous des formules à prix fixe, par exemple un petit déjeuner ou un menu du midi ? | Pas de formule au départ. |
| **Q70** | Où rangez-vous les pizzas, le petit déjeuner et le café : sous Nourriture et Boisson, ou comme des familles à part ? | Pizzas et Petit déjeuner sous Nourriture ; Café sous Boisson, Non alcoolisé. |
| **Q71** | Si un jour vous vendez à emporter, faut-il noter le nom du client et l'heure de retrait ? | Le nom et l'heure en tête du nom de la vente (« 12:30 Nom »), sans alerte. |
| **Q72** | Si un jour vous livrez : qui livrerait, vos employés, des coursiers ou une application ? | Vos employés, sans suivi des courses ; une application de livraison reste hors périmètre. |
| **Q73** | Quels jours et à quelles heures êtes-vous ouvert, et jusqu'à quelle heure servez-vous le petit déjeuner ? | Aucun horaire n'est réglé dans la caisse. |
| **Q74** | La carte ou les prix doivent-ils changer selon l'heure, par exemple un petit déjeuner vendu le matin seulement ? | Non : toute la carte se vend à toute heure, au même prix. |
| **Q75** | Au bar, un client peut-il consommer sans table et payer en partant, sur une facture laissée ouverte à son nom ? | Non en temps normal, si « comptoir » vaut pour le bar : places du bar sur le plan ; facture sans table avec l'option comptoir. |
| **Q76** | Une vente au comptoir ou à emporter compte-t-elle dans le nombre de personnes et dans le prix moyen par personne ? | Non : une vente sans table compte 0 personne et se compte à part. |
| **Q81** | Si vous vendez à emporter : le prix est-il le même sur place et à emporter ? Votre comptable applique-t-il une taxe différente à l'emporter ? | Même prix, même taxe. |
| **Q82** | Si vous livrez : la livraison est-elle payante, à quel prix ? Le client paie-t-il en commandant ou au livreur ? Faut-il suivre l'heure promise, le livreur et les impayés ? | Prix unique ; le livreur rapporte l'argent avant la fermeture ; heure et livreur notés sur la commande. |
| **Q83** | Voulez-vous connaître à part ce que le bar a vendu ? Le bar a-t-il son propre stock ? | Le chiffre du bar se lit par ses familles ; un seul stock. |

### 7.3 Validation

Le client valide quatre choses : le tableau de synthèse (ce qui existe, ce qui est à développer, ce qui est prévu pour l'ouverture) ; ses réponses aux questions ci-dessus, les choix par défaut valant pour les questions restées sans réponse ; les réponses données pour son établissement (R : Q3, Q64, Q65) ; la liste de ce qui n'est pas dans le périmètre.

| Nom | Fonction | Date | Signature |
|---|---|---|---|
| | | …/…/…… | |

---
## 8. Annexes

### Annexe A — Transcription des onze messages

Reprise telle quelle de la transcription consolidée, avec sa note de méthode.

**Messages vocaux du client — transcription consolidée**

Source : 11 messages vocaux WhatsApp reçus le 12/11/2026 (15 fichiers envoyés, dont 4 doublons),
2 min 54 s au total. Transcription locale par Whisper large-v3, recoupée avec Whisper turbo.
Ordre : celui de l'horodatage des fichiers. Entre crochets : mot incertain ou rétabli (les deux
modèles divergent, ou la phrase transcrite n'a pas de sens telle quelle).

**M1** (26 s) — Voilà, ce que je voulais, c'est que, bon, en tout début, déjà, l'interface doit être telle que, quand c'est ouvert, il faut le mot de passe de l'utilisateur pour que ça permette de fonctionner. Que les transactions gardent le code de l'utilisateur. C'est-à-dire, j'ai une caissière qui s'appelle Valérie. Elle a ouvert le système, elle a [attrapé / tapé] une table. Moi, je viens faire le paiement avec mon code. Il faudrait qu'on sache que c'est elle qui a [attrapé / tapé] et c'est moi qui ai fait la transaction.

**M2** (27 s) — Au moment d'ouvrir la table, après que quelqu'un ait entré son code, il faudrait que le système demande le numéro de la table et le nombre de personnes sur la table pour ouvrir la table. En plus de ça, s'il y aura possibilité d'écrire le nom du client sur la table ou d'écrire le nom d'une société, pendant qu'on ouvre la table, ce serait bien. Ou alors même après, qu'on puisse rentrer le nom de la société sur la table ou le nom de la personne.

**M3** (19 s) — Les commandes seront de façon, une fois que les commandes sont rentrées et qu'on a envoyées, elles ne peuvent plus être enlevées. Il faudrait juste un code du grade supérieur, c'est-à-dire un truc hiérarchique, [pour] pouvoir annuler.

**M4** (20 s) — Il y a aussi la fonctionnalité d'ajouter les tables ensemble, diviser les tables en deux, que j'ai déjà précisé, prendre un produit [et l'ajouter] sur une autre table, ou prendre un produit d'une table [et l'ajouter] sur une autre table existante, retirer un produit et créer une nouvelle table avec. Quand tout ça est possible, ça facilite un peu l'opération. Si c'est possible, ce sera bien.

**M5** (26 s) — Aussi, après l'ouverture de la table, l'interface qui va venir doit venir telle qu'il y a nourriture, il y a boisson. Et quand on entre, c'est structuré tel que ça permet de… On voit directement les sous-catégories, les sous-sous-catégories. C'est-à-dire, si je vois boisson, quand je clique boisson, je peux être capable de voir alcoolisé, non alcoolisé. Quand je [clique] alcoolisé, je dois voir peut-être bière, vin, whisky, machin. [Et quand je rentre avant, un peu ça.]

**M6** (18 s) — Maintenant, au niveau des entrées, on va pouvoir entrer les quantités des stocks qu'on a. Quand on a des trucs de petite quantité, on met quand même le stock qu'on a. On enregistre quand même le stock qu'on a. C'est-à-dire que pendant qu'on vend, si ça finit, que le système ne prenne même pas.

**M7** (36 s) — Les rapports, on doit avoir tous les rapports. Les rapports d'annulation, les rapports de… Je veux que tous les rapports soient vraiment possibles. Je veux le rapport des boissons, est-ce que je peux filtrer justement les boissons ? Je veux le rapport des salades, est-ce que je peux filtrer justement les salades ? Je veux le rapport des poulets, est-ce que je peux filtrer juste le poulet ? Donc vraiment tous les rapports possibles, que ce soit journalier, hebdomadaire, mensuel, annuel. Donc le filtre permet qu'on prenne la période qu'on veut et on choisit ce qu'on veut et que ça puisse nous donner.

**M8** (14 s) — [Aussi, c'est vrai que les fiches techniques, je ne crois pas] que ce sera prêt avant l'ouverture pour qu'on remplisse les petites quantités pour pouvoir calculer la profitabilité. Mais si la fonction [est là], pour le futur, on pourra remplir progressivement.

**M9** (43 s) — Si possible, le système doit donner l'option de pouvoir ajouter le nombre de personnes. C'est-à-dire que les gens sont [à 6, 5 / assis], ils sont en train de manger. Après, deux personnes viennent s'ajouter sur eux. Il faut que le système permette qu'on ajoute le nombre de personnes. Pendant qu'on ferme, mon souci c'est que le système puisse compter le nombre de personnes. Que ça puisse donner un rapport. La quantité vendue divisée par le nombre de personnes, qu'on ait un prix moyen. Donc il y a des rapports comme ça. Même si ça ne donne pas, ça compte le nombre de personnes, et le nombre de tables, et la quantité vendue, ça permet qu'on peut faire le calcul nous-mêmes et savoir ce qui se passe.

**M10** (27 s) — Les accès doivent être échelonnés de façon suivante. On a le serveur, on a la caissière, on a le chef de salle ou les superviseurs qui sont au-dessus, qui peuvent prendre la décision d'annuler ou de ne pas annuler parce qu'ils vont expliquer dans leur rapport. Et puis il y a un accès de manager, un super [admin], qui peut voir tous les autres trucs, peut-être ajouter des produits, changer des prix et autres.

**M11** (39 s) — Le plan de salle doit être visible dans le système et les tables doivent avoir des couleurs. C'est-à-dire, quand une table est ouverte, par exemple, elle est verte ; quand une table a dépassé une heure de temps, elle passe à l'orange. C'est-à-dire qu'on essaie [d'attirer l'attention] pour qu'on n'oublie pas. Il y a des factures que souvent on oublie, le client [est parti], on ne sait pas. Il faudrait qu'on se rappelle avant le temps qu'un client devait mettre normalement. Si un client met une heure de temps ou deux heures de temps, il faut… à une heure ou une heure trente que ça signale déjà à l'orange par exemple, que là on sache qu'on doit envoyer, demander au serveur de regarder s'il veut la facture ou pas.

### Annexe A bis — Précision et réponses d'AITE (13/11/2026)

Le 13/11/2026, AITE — pas le client, et hors des messages vocaux — a écrit, mot pour mot :

> Le client c'est un restaurant
>
> Pizza café petit déjeuner bar et cuisine

**Lecture retenue (P).** Un restaurant seul, sans hôtel, qui sert des pizzas, du café et des petits déjeuners, et qui a un bar et une cuisine. C'est une lecture : « bar et cuisine » peut désigner deux postes de préparation, ou simplement l'offre ; « sans hôtel » n'est pas écrit. Rien d'autre n'est connu (liste en partie 2).

**Réponses d'AITE du 13/11/2026 (R)**, mot pour mot, orthographe d'origine comprise ; chaque ligne reprend une question, puis la réponse.

Premier message (Q3, Q64, Q65, abrégées : Q64 sans « ou au bar », Q65 sans « tiroir-caisse ») :

> A-t-il bien un restaurant seul, sans chambres oui juste restaurant
>
> Vend-il aussi sans table : comptoir, à emporter, livraison ? normalement non mais prevois l'option
>
> Le bar encaisse-t-il lui-même, ou tout s’encaisse-t-il au même endroit le bar peut encaisser mais il y'a une caisse principal

Second message :

> * quelles ventes sans table sont visées : comptoir, à emporter, livraison ; a emporter comptoir et livraison
> * si le bar a son propre tiroir, son propre fond de caisse et sa propre fermeture ; exacte mais ca reste une option
> * si le bar encaisse seulement ses ventes ou aussi les tables ; le bar peut encaisse les vente des table mais ca reste une option le client a une caisse unique
> * si une addition commencée au bar suit le client à table.

La quatrième question est restée sans réponse (Q79).

**Lecture retenue (R), à faire confirmer par le client (Q3, Q64, Q65) :** restaurant seul ; ventes à table en temps normal, vente sans table (à emporter, comptoir, livraison) en option ; caisse unique, avec deux options : (1) tiroir, fond et fermeture du bar ; (2) le bar encaisse aussi les tables. Réponses d'AITE, peut-être pas dictées par le client ; « prevois l'option » et « ca reste une option » : consignes pour l'étude (activable, pas par défaut).

**Ce qu'elles ne disent pas :** qui livre (Q72), si la livraison est payante (Q82), quand ouvrir les options (Q78), si le bar encaisse en temps normal (Q77), ce que « caisse unique » désigne : un poste (Q2) ou un tiroir-caisse (Q77).

### Annexe B — Sources

**Avertissement.** La recherche sur le web a fonctionné (une centaine de requêtes, en français et en anglais), mais **l'ouverture des pages a échoué pour presque tous les sites** : la session de travail n'autorisait pas ces adresses. Seuls `github.com` et `raw.githubusercontent.com` ont pu être ouverts. Conséquences :

- Le premier groupe ([1] à [7], [64]) et le troisième ([8] à [18]) ont été **lus en entier**. La documentation d'Odoo 18 l'a été dans sa source (les fichiers du dépôt `odoo/documentation`, branche 18.0), pas sur le site publié ; les captures d'écran n'ont pas été vues. Du deuxième groupe ([65] à [68]), seuls les passages employés ont été comparés au fichier source.
- Les cinq derniers groupes ([19] à [63], [69] à [86]) ne sont que des **extraits renvoyés par le moteur de recherche** : le passage utilisé figurait dans le résultat, la page n'a pas été ouverte. Les libellés exacts, les chiffres et les prix sont à revérifier en ouvrant les pages. Quand le moteur n'a pas rattaché un passage à une adresse précise, la source porte la mention « attribution incertaine ».
- Ces sources sont en majorité des éditeurs de caisses (Toast, Square, Lightspeed, Oracle, Lavu) : elles décrivent leurs produits, avec un biais commercial. Elles servent de repères de conception, pas de normes.
- **Non trouvé malgré la recherche :** un taux d'annulations de référence ; une obligation camerounaise sur la conservation des annulations de caisse ; la documentation des caisses françaises Zelty et L'Addition ; un nombre de touches cible pour un écran de commande.
- Aucun module tiers cité n'a été installé ni audité. Le code de l'édition Enterprise d'Odoo n'était pas disponible.
- **Pendant la correction du 12/11/2026 :** [1], [2] et [64] ont été rouverts dans leur source, et [17] sur GitHub. Une nouvelle tentative sur `support.toasttab.com` et `squareup.com` a échoué (hôtes hors de la liste réseau autorisée de la session) : aucune des 45 sources [19] à [63] n'a pu être contrôlée. Dans le texte, leurs renvois portent le signe ° ([21°]). Pour les contrôler, ces hôtes, ainsi que `docs.oracle.com`, doivent être autorisés dans les réglages réseau de la session.
- **Mise à jour du 13/11/2026 (profil de l'établissement).** 84 requêtes de plus, toutes génériques ; quatre essais d'ouverture hors GitHub, quatre échecs. Quatre pages de la documentation d'Odoo 18 ouvertes dans leur source ([65] à [68]). Treize sources nouvelles ([69] à [81]) ne sont que des extraits du moteur de recherche. **Non trouvé :** une règle admise pour compter les personnes d'une vente à emporter ; une caisse qui règle l'alerte de durée par service ; une source de métier francophone sur la pizza. **Non cherché :** les usages propres au Cameroun (livraison à moto, paiement mobile à la livraison).
- **Mise à jour du 13/11/2026 (réponses d'AITE).** 31 requêtes génériques ; deux ouvertures hors GitHub, échouées. Cinq sources nouvelles ([82] à [86]), extraits du moteur, nord-américaines. **Décompte : 86 sources, dont 23 pages ouvertes ([1] à [18], [64] à [68]) et 63 non ouvertes ([19] à [63], [69] à [86]).**

**Documentation officielle d'Odoo 18, lue en entier dans sa source (dépôt `odoo/documentation`, branche 18.0), non comparée à la page publiée**

- **[1]** Odoo 18, « Restaurant features » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale/restaurant.rst>
- **[2]** Odoo 18, « Multi-employee management » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale/employee_login.rst>
- **[3]** Odoo 18, « Point of Sale » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale.rst>
- **[4]** Odoo 18, « Preparation display » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale/preparation.rst>
- **[5]** Odoo 18, « Reporting » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale/reporting.rst>
- **[6]** Odoo 18, « Kits » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/inventory_and_mrp/manufacturing/advanced_configuration/kit_shipping.rst>
- **[7]** Odoo 18, « Inventory adjustments » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.rst>
- **[64]** Odoo 18, « Hosting », rubrique « Change hosting solution » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/administration/hosting.rst> — « Odoo Online is not compatible with non-standard apps » ; ajoutée et ouverte pendant la correction

**Documentation officielle d'Odoo 18, pages ouvertes le 13/11/2026 dans leur source (branche 18.0) ; passages employés comparés au fichier**

- **[65]** Odoo 18, « Product variants » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/sales/products_prices/products/variants.rst>
- **[66]** Odoo 18, « Managing BoMs for product variants » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/inventory_and_mrp/manufacturing/advanced_configuration/product_variants.rst>
- **[67]** Odoo 18, « Product combos » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale/combos.rst>
- **[68]** Odoo 18, « Online food delivery » — <https://raw.githubusercontent.com/odoo/documentation/18.0/content/applications/sales/point_of_sale/online_food_delivery.rst>

**Modules libres et tickets publics, pages ouvertes sur GitHub (aucun module installé ni audité)**

- **[8]** OCA/pos, branche 18.0, liste des modules disponibles — <https://github.com/OCA/pos/tree/18.0>
- **[9]** OCA/pos, demande de fusion n° 1480, « [18.0][MIG] pos_access_right » — <https://github.com/OCA/pos/pull/1480> — fermée sans fusion
- **[10]** OCA/pos, demande de fusion n° 1457, « [18.0] [MIG] pos_stock_available_online » — <https://github.com/OCA/pos/pull/1457> — fermée sans fusion
- **[11]** OCA, « Stock Disallow Negative » (stock_no_negative, 18.0) — <https://raw.githubusercontent.com/OCA/stock-logistics-workflow/18.0/stock_no_negative/README.rst> — licence AGPL-3
- **[12]** OCA/pos, « POS - Blind Session Closing » (18.0) — <https://raw.githubusercontent.com/OCA/pos/18.0/pos_blind_session_closing/README.rst> — licence AGPL-3
- **[13]** Cybrosys, « Display Stock in POS | Restrict Out-of-Stock Products in POS » (pos_restrict_product_stock, 18.0), manifeste — <https://raw.githubusercontent.com/CybroOdoo/CybroAddons/18.0/pos_restrict_product_stock/__manifest__.py> — licence AGPL-3
- **[14]** Cybrosys, « POS Access Right » (pos_access_right_hr, 18.0), manifeste — <https://raw.githubusercontent.com/CybroOdoo/CybroAddons/18.0/pos_access_right_hr/__manifest__.py> — licence AGPL-3
- **[15]** Cybrosys, « POS Kitchen Screen » (pos_kitchen_screen_odoo, 18.0), manifeste — <https://raw.githubusercontent.com/CybroOdoo/CybroAddons/18.0/pos_kitchen_screen_odoo/__manifest__.py> — licence LGPL-3
- **[16]** odoo/odoo, ticket n° 189836, « [18.0] POS - indexedDB and server data (sync_from_ui) are in conflict » — <https://github.com/odoo/odoo/issues/189836> — ouvert
- **[17]** odoo/odoo, ticket n° 298891, « POS: trusted_config_ids never resolves in devices_synchronisation.js, breaking cross-register order sync (shared restaurant tables) » — <https://github.com/odoo/odoo/issues/298891> — ouvert le 28/10/2026 ; une seule réponse, d'un tiers, le 30/10/2026 (selon lui, le défaut n'est plus présent sur la branche de développement) ; pas de réponse d'Odoo
- **[18]** odoo/odoo, ticket n° 266373, « [19.0] POS Restaurant - Transfer / Merge incorrectly marks already sent items as new for kitchen printing » — <https://github.com/odoo/odoo/issues/266373> — corrigé le 15/07/2026 en version 19

**Éditeurs de caisses de restaurant : extraits renvoyés par le moteur de recherche, pages non ouvertes**

- **[19]** Square, « Require passcodes at point of sale » — <https://squareup.com/help/us/en/article/8357-require-passcodes-at-point-of-sale>
- **[20]** Eats365, « Configure POS to sign out automatically » — <https://eats365pos.helpjuice.com/device-management/configure-pos-to-sign-out-automatically>
- **[21]** Toast, « Void Items, Payments, and Checks » — <https://support.toasttab.com/en/article/Voiding-Items-Payments-and-Checks?lang=en_US>
- **[22]** Toast, « Permissions Reference Guide » — <https://support.toasttab.com/en/article/Access-Permissions-Reference?lang=en_US>
- **[23]** Toast, « Manage Tables With Toast POS » — <https://support.toasttab.com/en/article/New-POS-Managing-Tables>
- **[24]** Toast, « View and Manage Voided Items in Toast Web » — <https://support.toasttab.com/en/article/Managing-Voided-Items-and>
- **[25]** Toast, « Configure Order Changes and Voids to Auto Print to Kitchen » — <https://support.toasttab.com/en/article/How-do-I-configure-order-changes-or-voids-to-auto-print-in-the-kitchen-1492627886122>
- **[26]** Toast, « Start a Tab » — <https://support.toasttab.com/en/article/Starting-a-Tab-1492811100378>
- **[27]** Toast, « Enable seat numbers and party sizes for POS orders » — <https://support.toasttab.com/en/article/Seat-Numbers-Enabling-and-Configuring-1493086465089>
- **[28]** Toast, « Transfer Items, Checks, and Payments » — <https://support.toasttab.com/en/article/Transferring-Items-Checks-and-Payments>
- **[29]** Toast, « Close Out Day, Z Report, and Auto-Capture Overview » — <https://support.toasttab.com/en/article/Close-Out-Day-Z-Report-Auto-Capture>
- **[30]** Toast, « Menu item inventory overview » — <https://doc.toasttab.com/doc/platformguide/adminMenuItemInventoryOverview.html>
- **[31]** Toast, « Toast Inventory: Stock Depletion » — <https://support.toasttab.com/en/article/Toast-InventoryStock-Depletion>
- **[32]** Toast, « Product Mix (PMIX) Report Overview » — <https://support.toasttab.com/en/article/Product-Mix-PMIX-Report-Overview>
- **[33]** Toast, centre d'aide, « Can I prevent employees from removing items from tickets » — <https://intercom.help/toast-central/en/articles/9310971-can-i-prevent-employees-from-removing-items-from-tickets>
- **[34]** Square, « Comp, void and reassign checks with Square for Restaurants » — <https://squareup.com/help/us/en/article/8166-comp-void-and-reassign-checks-with-square-for-restaurants>
- **[35]** Square, « Customize table management settings » — <https://squareup.com/help/us/en/article/8146-customize-table-management-settings>
- **[36]** Square, « Check management with Square for Restaurants » — <https://squareup.com/help/us/en/article/6429-check-management-with-square-for-restaurants>
- **[37]** Square, « Split a payment and check with Square for Restaurants » — <https://squareup.com/help/us/en/article/8165-split-a-payment-and-check-with-square-for-restaurants>
- **[38]** Square, « Create a menu group and edit layout » — <https://squareup.com/help/us/en/article/7804-organize-your-menu-with-square-for-restaurants>
- **[39]** Square, « Manage item availability » — <https://squareup.com/help/us/en/article/6425-managing-items-with-square-for-restaurants>
- **[40]** Square Developer, « Monitor Sold-out Item Variations or Modifiers » — <https://developer.squareup.com/docs/inventory-api/monitor-sold-out-status-on-item-variation>
- **[41]** Lightspeed K-Series, centre d'aide, écran des tables et plan de salle — <https://k-series-support.lightspeedhq.com/hc/articles/360050328494> — titre de l'article non restitué par le moteur
- **[42]** Oracle Simphony, « Adding the Guest Count to a Check » — <https://docs.oracle.com/en/industries/food-beverage/simphony/19.6/sipou/t_checks_add_guest_count.htm> — attribution incertaine : le passage sur les deux options obligatoires vient d'une page Oracle que le moteur n'a pas rattachée à une adresse précise
- **[43]** Oracle Back Office, guide des rapports, « Voided Menu Items » — <https://docs.oracle.com/en/industries/food-beverage/back-office/20.1/rarrg/c_voided_menu_items.htm>
- **[44]** Lavu, « How to Handle Restaurant POS Void and Comp Tracking » — <https://lavu.com/how-to-handle-restaurant-pos-void-and-comp-tracking/>
- **[45]** Restaurant365, « 10 Ways to Reduce Employee Fraud » — <https://www.restaurant365.com/blog/10-ways-to-reduce-employee-fraud/>
- **[46]** Restaurant365, « Theoretical vs Actual Variance Report » — <https://docs.restaurant365.com/docs/theoretical-vs-actual-report>
- **[47]** Avero, « Fraud Fridays: The Transfer Web » — <https://averoinc.com/fraud-fridays-the-transfer-web/> — Avero vend un outil de détection des fraudes
- **[48]** Avero, centre d'aide, guide de détection des fraudes — <https://averoinc.zendesk.com/hc/en-us/articles/360056166454> — titre de l'article non restitué par le moteur
- **[49]** Microsale, « Menu Fundamentals » — <https://microsale.zendesk.com/hc/en-us/articles/4412765487255-Menu-Fundamentals>
- **[50]** SumUp, « How to configure your product catalogue for maximum checkout efficiency » — <https://www.sumup.com/en-gb/running-business/management/product-catalogue-for-maximum-checkout-efficiency/>

**Gestion de restaurant (manuels, presse professionnelle, cabinets) : extraits renvoyés par le moteur de recherche, pages non ouvertes**

- **[51]** BCcampus, Basic Kitchen and Food Service Management, « Basic Inventory Procedures » — <https://opentextbc.ca/basickitchenandfoodservicemanagement/chapter/basic-inventory-procedures/>
- **[52]** BCcampus, Basic Kitchen and Food Service Management, « Monthly Food Costs » — <https://opentextbc.ca/basickitchenandfoodservicemanagement/chapter/monthly-food-costs/>
- **[53]** BCcampus, Basic Kitchen and Food Service Management, « Yield Testing » — <https://opentextbc.ca/basickitchenandfoodservicemanagement/chapter/yield-testing/>
- **[54]** DineOpen, « Restaurant inventory management best practices 2025 » — <https://www.dineopen.com/blog/restaurant-inventory-management-best-practices-2025>
- **[55]** Keobiz, « Votre nouvelle carte est prête : à quel prix vendre ce plat signature pour garantir votre marge ? » — <https://www.keobiz.fr/fiches-pratiques/ouvrir-restaurant-hotel/food-cost-beverage-cost-marges/> — repères d'un cabinet comptable français
- **[56]** BevSpot, « How to calculate plate costs: your kitchen's step-by-step guide » — <https://bevspot.com/blog/how-to-calculate-plate-costs-your-kitchens-step-by-step-guide/>
- **[57]** L'Hôtellerie Restauration, SOS experts, « Le ticket moyen » — <https://www.lhotellerie-restauration.fr/sos-experts/1-1-le-ticket-moyen>
- **[58]** Black Box Intelligence, « Restaurant Glossary — Average check » — <https://blackboxintelligence.com/resources/restaurant-glossary/average-check>
- **[59]** Mews, « Ratio restauration : lesquels faut-il suivre ? » — <https://www.mews.com/fr/blog/ratio-restauration>

**Forum et boutique d'applications d'Odoo : extraits renvoyés par le moteur de recherche, pages non ouvertes**

- **[60]** Forum Odoo, « Limit waiters ability to delete products and close tables in Odoo POS restaurant » — <https://www.odoo.com/forum/help-1/limit-waiters-ability-to-delete-products-and-close-tables-in-odoo-pos-restaurant-239870> — testé par son auteur en 17.0 et 17.2
- **[61]** Forum Odoo, « Point of Sale (POS) module to control available product quantities » — <https://www.odoo.com/forum/help-1/point-of-sale-pos-module-to-control-available-product-quantities-for-example-meals-prepared-daily-by-the-kitchen-277105>
- **[62]** Boutique Odoo, « pos hr manager validation mac5 » (18.0) — <https://apps.odoo.com/apps/modules/18.0/pos_hr_manager_validation_mac5/> — version, prix et licence à revérifier sur la fiche
- **[63]** Boutique Odoo, « cst pos table time counter » (18.0) — <https://apps.odoo.com/apps/modules/18.0/cst_pos_table_time_counter> — version, prix et licence à revérifier sur la fiche

**Pizzeria, vente à emporter, café et bar : extraits renvoyés par le moteur de recherche le 13/11/2026, pages non ouvertes**

- **[69]** Toast, guide de la plateforme, « Size price » — <https://doc.toasttab.com/doc/platformguide/adminSizePrice.html> — attribution incertaine
- **[70]** NCR Voyix Aloha POS, « Pricing pizzas with basic pizza » — <https://docs.ncrvoyix.com/restaurant/aloha-pos/implementing/basic_pizza/pricing_pizzas_with_basic_pizza> — attribution incertaine : la règle « la plus chère » vient d'une page de Rezku que le moteur n'a pas précisée
- **[71]** Rezku, « Pizza (Pizza Products) » et « Pizza Ordering » — <https://support.rezku.com/portal/en/kb/articles/pizza-pizza-products>
- **[72]** NCR Voyix Aloha Kitchen, « Configuring specific kitchen environments » — <https://docs.ncrvoyix.com/restaurant/aloha-kitchen/implementing/configuring_specific_kitchen_environments>
- **[73]** Toast, « Configure Custom Dining Options » — <https://support.toasttab.com/en/article/Dining-Options-1492794310377> — attribution incertaine
- **[74]** Toast, « Sales Summary Report Overview » — <https://support.toasttab.com/en/article/Sales-Summary-Report>
- **[75]** Oracle Back Office, guide des rapports, « Service Metrics » — <https://docs.oracle.com/en/industries/food-beverage/back-office/20.1/rarrg/c_common_calc_service.htm> — attribution incertaine
- **[76]** Toast, « Total Guest Counts » — <https://support.toasttab.com/en/article/How-is-Guest-Count-Calculated>
- **[77]** Toast, « Set Up Restaurant Hours and Services » — <https://support.toasttab.com/en/article/Setup-Restaurant-Hours-and-Services>
- **[78]** Toast, « Set Menu Availability » — <https://support.toasttab.com/en/article/Settings-Menu-Availability>
- **[79]** Resy, « Customize Turn Times » — <https://helpdesk.resy.com/en_us/turn-times-B1K2bIGXc> — outil de réservation, pas une caisse
- **[80]** Square, « Convert stock » — <https://squareup.com/help/us/en/article/7237-stock-conversion-sell-by>
- **[81]** Lightspeed K-Series, « Creating and managing bar tabs » — <https://k-series-support.lightspeedhq.com/hc/en-us/articles/4408089985179-Creating-and-managing-bar-tabs>

**Tiroir, caisse et vente sans table : extraits du moteur de recherche, 13/11/2026, pages non ouvertes**

- **[82]** Toast (fr-CA), « Obtenez de l'aide avec le tiroir-caisse et la révision de shift » — <https://support.toasttab.com/fr-CA/article/Cash-Drawer-and-Shift-Review-Troubleshooting> — attribution incertaine
- **[83]** NCR Voyix Aloha POS, « Drawer Checkout » — <https://docs.ncrvoyix.com/restaurant/aloha-pos/implementing/drawer_checkout/implementing_drawer_checkout>
- **[84]** Oracle Simphony, « Check Transfers » — <https://docs.oracle.com/en/industries/food-beverage/simphony/sipou/c_checks_transfers.htm>
- **[85]** Restaurant365, « Daily Operations Report » — <https://docs.restaurant365.com/docs/daily-operations-report>
- **[86]** Shift4, centre d'aide, règlement du livreur — <https://shift4.zendesk.com/hc/en-us/articles/360038555733> — titre non restitué par le moteur ; attribution incertaine

### Annexe C — Preuves dans le code

**Odoo 18.** Lecture du code de l'édition Community, branche 18.0, commit `5c4488a4` (écrit le 30/10/2026, intégré le 11/11/2026), dans `/home/user/odoo18/addons` ; les chemins ci-dessous sont relatifs à ce dossier et les numéros de ligne valent pour ce commit. Les libellés français viennent des fichiers `i18n/fr.po` des modules. **Rien n'a été essayé à l'écran** : aucune caisse n'a été ouverte dans un navigateur. Une installation à froid et des essais côté serveur ont été joués le 12/11/2026 (tableau plus bas). Les renvois C55 à C76 ont été ajoutés pendant la correction, d'après les constats de la relecture technique, relus un à un dans le code. C77 à C92, ajoutés le 13/11/2026 pour le profil, et C93 à C99, pour les réponses d'AITE, disent chacun leur niveau : « lu dans le code » ou « exécuté côté serveur ».

| Réf. | Point | Fichier:ligne |
|---|---|---|
| C1 | Connexion des employés : l'écran de code s'affiche tant que personne n'est identifié | `pos_hr/static/src/overrides/models/pos_store.js:6-14` ; `pos_hr/static/src/overrides/screens/login_screen/login_screen.xml:8-23` |
| C2 | Le code n'est demandé que s'il existe ; plusieurs employés peuvent avoir le même | `pos_hr/static/src/app/select_cashier_mixin.js:35-58, 105-129` |
| C3 | Code et badge sur la fiche employé ; transmis au poste sous forme hachée (SHA-1) et comparés sur le poste | `hr/models/hr_employee.py:145-147` ; `pos_hr/models/hr_employee.py:51-61` ; `pos_hr/static/src/app/select_cashier_mixin.js:43` |
| C4 | Verrouillage à la main seulement (bouton « Bloquer ») ; veille après 5 min et retour au plan après 3 min sans déconnexion | `pos_hr/static/src/overrides/components/navbar/navbar.xml:13-21` ; `point_of_sale/static/src/app/store/pos_store.js:182-200` ; `pos_restaurant/static/src/overrides/models/pos_store.js:15-36` |
| C5 | Changement de caissier ; l'employé courant est écrit sur la session et suivi dans son historique | `pos_hr/static/src/overrides/components/cashier_name/cashier_name.js:8-12` ; `pos_hr/static/src/overrides/models/pos_store.js:56-66` ; `pos_hr/models/pos_session.py:9-14` |
| C6 | Un seul employé par commande (« Caissier ») ; le paiement recopie ce champ | `pos_hr/models/pos_order.py:9` ; `pos_hr/models/pos_payment.py:7` |
| C7 | Ce champ est posé à la création, réécrit à chaque ajout de ligne, puis à la validation du paiement | `pos_hr/static/src/overrides/models/pos_store.js:47-55, 78-91` ; `pos_hr/static/src/overrides/components/payment_screen/payment_screen.js:5-11` |
| C8 | L'utilisateur porté par la commande est celui de la caisse, le même pour tous les employés | `point_of_sale/static/src/app/store/pos_store.js:1172` ; `point_of_sale/models/pos_order.py:324-328` |
| C9 | Aucun champ d'auteur sur la ligne de commande | `point_of_sale/models/pos_order.py:1457-1515` |
| C10 | Deux rôles en caisse (caissier, manager) ; listes « Droits de base » et « Droits avancés » ; l'employé lié à un administrateur du Point de Vente est manager d'office | `pos_hr/models/hr_employee.py:27-44` ; `pos_hr/models/pos_config.py:10-21` ; `pos_hr/views/res_config_settings_views.xml:9-16` |
| C11 | Réservé au rôle manager : prix (si « Contrôle des prix »), création d'article, plan de salle, fermeture ; les espèces ne le sont pas (C57) | `point_of_sale/static/src/app/store/pos_store.js:1107-1109` ; `pos_hr/static/src/overrides/models/pos_store.js:140-144` ; `pos_hr_restaurant/static/src/overrides/components/navbar/navbar.js:5-14` ; `pos_hr/static/src/overrides/components/navbar/navbar.xml:5-12` |
| C12 | Bouton de paiement et menu Actions (« Annuler la commande », « Remboursement ») sans condition de rôle | `pos_restaurant/static/src/overrides/components/product_screen/actionpad_widget/actionpad_widget.xml:36-42` ; `point_of_sale/static/src/app/screens/product_screen/control_buttons/control_buttons.xml:29-44` |
| C13 | Les rôles sont testés dans l'écran de la caisse ; côté serveur, l'utilisateur de la caisse peut créer, modifier et supprimer commandes et lignes | `pos_hr/models/hr_employee.py:27-44` ; `point_of_sale/security/ir.model.access.csv:4-5` |
| C14 | Profils « Utilisateur » et « Administrateur » du Point de Vente et leurs droits | `point_of_sale/security/point_of_sale_security.xml:8-17` ; `point_of_sale/security/ir.model.access.csv:34-42, 55-60` |
| C15 | « Contrôle des prix » réservé au rôle manager : la touche Prix est désactivée pour les autres, et le message d'interdiction n'est atteint que par un autre chemin ; remises par ligne et remise globale ouvertes à tous | `point_of_sale/models/pos_config.py:125-126, 189` ; `point_of_sale/static/src/app/screens/product_screen/product_screen.js:164-168` ; `pos_hr/static/src/overrides/screens/product_screen/order_summary/order_summary.js:7-17` ; `pos_discount/static/src/overrides/components/control_buttons/control_buttons.xml:5-10` |
| C16 | La caisse de restaurant s'ouvre sur le plan ; une table s'ouvre en la touchant ou par son numéro | `pos_restaurant/static/src/overrides/models/pos_store.js:28-36, 221-249` ; `pos_restaurant/static/src/app/floor_screen/floor_screen.js:588-609` ; `pos_restaurant/static/src/overrides/components/navbar/navbar.xml:25-29` |
| C17 | Numéro de table entier ; un numéro inconnu crée une commande sans table | `pos_restaurant/models/pos_restaurant.py:95` ; `pos_restaurant/static/src/overrides/components/navbar/navbar.js:36-70` |
| C18 | Nombre de personnes : champ « Convives », 1 par défaut, bouton de modification, montant par convive | `pos_restaurant/models/pos_order.py:9` ; `pos_restaurant/static/src/overrides/models/pos_order.js:5-25` ; `pos_restaurant/static/src/app/control_buttons/control_buttons.xml:14-17` ; `pos_restaurant/static/src/app/control_buttons/control_buttons.js:26-47` |
| C19 | La division fait passer 1 personne de la commande d'origine à la nouvelle, créée avec 1 personne et sans table ; la fusion ne reprend pas les personnes de la table absorbée | `pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.js:104-109, 168` ; `pos_restaurant/static/src/overrides/models/pos_order.js:5-16` ; `pos_restaurant/static/src/overrides/models/pos_store.js:291-353` |
| C20 | Client de la commande (bouton « Client ») ; une société est un contact ; création depuis la caisse | `point_of_sale/models/pos_order.py:342` ; `point_of_sale/models/res_partner.py:32-37` ; `point_of_sale/static/src/app/store/pos_store.js:1988-1999` |
| C21 | Nom libre de commande : le champ existe, le bouton est réservé aux commandes sans table ; le plan n'affiche que le numéro | `point_of_sale/models/pos_order.py:364` ; `pos_restaurant/static/src/app/control_buttons/control_buttons.xml:32-34` ; `pos_restaurant/static/src/app/floor_screen/floor_screen.xml:148` |
| C22 | Catégories de caisse à plusieurs niveaux sans limite ; affichage des sous-catégories ; 100 articles au plus à l'écran | `point_of_sale/models/pos_category.py:17-27` ; `point_of_sale/static/src/app/screens/product_screen/product_screen.js:114-152, 379-420, 450-457` |
| C23 | « Limiter les catégories » ; couleur, image et rang d'une catégorie | `point_of_sale/models/pos_config.py:120-121, 779-804` ; `point_of_sale/models/pos_category.py:28-40` |
| C24 | Envoi : bouton « Commander », quantités envoyées mémorisées, bons par imprimante de préparation | `pos_restaurant/static/src/overrides/components/product_screen/actionpad_widget/actionpad_widget.xml:15-35` ; `point_of_sale/static/src/app/store/pos_store.js:1738-1761, 1883-1913` ; `point_of_sale/models/pos_order.py:322` |
| C25 | Point d'accroche laissé ouvert : toute ligne, même envoyée, se diminue ou se supprime. Activé, il compare à une quantité gardée en mémoire du poste et, sous cette quantité, crée une ligne négative au lieu de refuser ; il ne couvre que le pavé numérique | `point_of_sale/static/src/app/store/pos_store.js:1620-1622` ; `point_of_sale/static/src/app/screens/product_screen/order_summary/order_summary.js:62-69, 106-129, 159-196, 216-275` ; `point_of_sale/static/src/app/models/pos_order_line.js:28` ; `point_of_sale/static/src/app/models/pos_order.js:355` |
| C26 | La vérification du code n'est appelée que pour se connecter ou changer de caissier | `pos_hr/static/src/app/select_cashier_mixin.js:35-58` ; `pos_hr/static/src/overrides/screens/login_screen/login_screen.js:35-37` ; `pos_hr/static/src/overrides/components/cashier_name/cashier_name.js:32-34` |
| C27 | « Suivi des modifications de commandes » : une note dans l'historique de la commande, sans motif | `point_of_sale/models/pos_config.py:211` ; `point_of_sale/models/pos_order.py:1586-1590, 1853-1859` ; `pos_hr/models/pos_order.py:20-23` ; `point_of_sale/views/pos_order_view.xml:207` |
| C28 | « Annuler la commande » : la commande passe à l'état « Annulé » et reste en base ; l'effacement n'est appelé que par la commande en libre-service | `point_of_sale/static/src/app/store/pos_store.js:474-550` ; `point_of_sale/models/pos_order.py:1100-1107, 1387-1400` ; `pos_self_order/controllers/orders.py:100` |
| C29 | Remboursement ouvert à tout employé depuis la liste des commandes | `point_of_sale/static/src/app/screens/ticket_screen/ticket_screen.js:224-310` ; `point_of_sale/models/pos_order.py:1293-1317` |
| C30 | Fermeture refusée tant qu'une commande est ouverte ; un bouton les annule toutes puis ferme | `point_of_sale/models/pos_session.py:393-394` ; `point_of_sale/static/src/app/navbar/closing_popup/closing_popup.js:292-311` |
| C31 | Réunir des tables en glissant l'une sur l'autre ; message « Link Table » sans traduction française | `pos_restaurant/static/src/app/floor_screen/floor_screen.js:131-235` ; `pos_restaurant/models/pos_restaurant.py:105` ; `pos_restaurant/i18n/fr.po:655-661` |
| C32 | « Transférer / Fusionner » : table libre, la commande s'y installe ; table occupée, les lignes s'ajoutent et la commande d'origine est annulée ; ni trace ni contrôle de rôle | `pos_restaurant/static/src/app/control_buttons/control_buttons.xml:29-31` ; `pos_restaurant/static/src/overrides/models/pos_store.js:291-353` ; `point_of_sale/static/src/app/store/pos_store.js:512-550` |
| C33 | « Fractionner » : nouvelle commande sans table, nommée par suffixe (B, C…) ; partage d'addition activé d'office à la création d'une caisse de restaurant (C59) | `pos_restaurant/static/src/app/control_buttons/control_buttons.xml:23-28` ; `pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.js:30-54, 71-82, 101-174` ; `pos_restaurant/models/pos_config.py:33-35` |
| C34 | Points d'accroche prévus : avant et après une division, avant la suppression d'une commande | `pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.js:84-86` ; `point_of_sale/static/src/app/store/pos_store.js:557-559` |
| C35 | Salles et tables : modèles, dessin du plan depuis la caisse, vue en grille | `pos_restaurant/models/pos_restaurant.py:8-22, 88-106` ; `pos_restaurant/static/src/app/floor_screen/floor_screen.js:699-786` ; `pos_restaurant/views/pos_restaurant_views.xml:112-116` |
| C36 | Table libre grisée, table occupée à sa couleur (vert par défaut) ; la table n'affiche que son numéro et une pastille | `pos_restaurant/static/src/app/floor_screen/floor_screen.xml:122-126, 148-160` ; `pos_restaurant/models/pos_restaurant.py:104` |
| C37 | Aucune durée sur le plan ; l'heure de la commande est posée à sa création puis réécrite au paiement | `point_of_sale/static/src/app/models/pos_order.js:30` ; `point_of_sale/static/src/app/screens/payment_screen/payment_screen.js:296` ; `pos_restaurant/static/src/app/models/restaurant_table.js:76-80` |
| C38 | Entrées de stock standard : inventaire physique, mise à jour de la quantité, case « Suivre l'inventaire » | `point_of_sale/__manifest__.py:10` ; `stock/models/stock_quant.py:98, 436` ; `stock/views/product_views.xml:234-235` ; `stock/models/product.py:714-716` |
| C39 | La caisse ne consulte pas le stock à la saisie ; la sortie de stock est validée après coup, une erreur de validation est ignorée | `point_of_sale/static/src/app/store/pos_store.js:1439-1446` ; `point_of_sale/models/stock_picking.py:41-55, 102-105` |
| C40 | Le stock baisse au paiement (« En temps réel ») ou à la fermeture de la session, jamais pour une table ouverte | `point_of_sale/models/pos_order.py:190-201, 1225-1249` ; `point_of_sale/models/res_company.py:11-15` ; `point_of_sale/models/pos_session.py:345-349` |
| C41 | Stock visible à la demande seulement, dans la fiche d'information du produit (rouge sous 5, orange jusqu'à 10) | `point_of_sale/static/src/app/components/product_info_banner/product_info_banner.js:20-72` ; `point_of_sale/models/product.py:223-237` |
| C42 | Nomenclature de type « Kit » ; à la confirmation du mouvement de stock, `mrp` éclate le plat en mouvements d'ingrédients ; `pos_mrp` ne sert qu'au calcul du coût ; seuls les produits de type « Biens » créent un mouvement | `mrp/models/mrp_bom.py:28-31` ; `mrp/models/stock_move.py:550-554` ; `point_of_sale/models/stock_picking.py:34` ; `pos_mrp/models/pos_order.py:9-34` |
| C43 | Coût figé sur la ligne à la validation ; marge ; « Calculer le prix depuis la nomenclature » ; marges visibles en caisse du seul rôle manager | `point_of_sale/models/pos_order.py:1763-1802` ; `mrp_account/models/product.py:82-120` ; `mrp_account/views/product_views.xml:14-18` ; `point_of_sale/static/src/app/screens/product_screen/product_info_popup/product_info_popup.js:19-24` |
| C44 | « Analyse des ventes » : dimensions et mesures ; ni table ni nombre de personnes ; l'employé est ajouté par pos_hr | `point_of_sale/report/pos_order_report.py:14-41` ; `point_of_sale/views/pos_order_report_view.xml:58-68` ; `pos_hr/report/pos_order_report.py:10-13` |
| C45 | Famille de l'analyse : la première catégorie de caisse de l'article, sans total par catégorie parente | `point_of_sale/report/pos_order_report.py:56-64, 94` ; `point_of_sale/models/product.py:17` |
| C46 | Filtres et regroupements par période ; « Détails des ventes » d'une date à une autre | `point_of_sale/views/pos_order_report_view.xml:57, 70` ; `point_of_sale/wizard/pos_details.py:30-47` ; `point_of_sale/models/report_sale_details.py:351-379` |
| C47 | Commandes annulées retrouvables par filtre ; « Détails des ventes » ne compte que les commandes payées | `point_of_sale/views/pos_order_view.xml:419` ; `point_of_sale/views/pos_order_report_view.xml:55, 88` ; `point_of_sale/models/report_sale_details.py:38` |
| C48 | Table et nombre de personnes enregistrés sur la commande et affichés sur sa fiche | `pos_restaurant/models/pos_order.py:8-9` ; `pos_restaurant/views/pos_order_views.xml:9-12` |
| C49 | Réglages qui renvoient à l'édition Enterprise : « Écran de préparation », « Réservation de table » | `point_of_sale/views/res_config_settings_views.xml:396-398` ; `pos_restaurant/views/res_config_settings_views.xml:38-45` |
| C50 | Imprimantes de préparation en Community : boîtier IoT ou Epson ePOS | `point_of_sale/models/pos_printer.py:13-16` ; `pos_epson_printer/models/pos_printer.py:32` |
| C51 | Modules installés d'office, liste constatée par installation (essai A) : pos_self_order et ses deux compléments avec pos_restaurant ; pos_hr, pos_hr_restaurant, hr_skills, hr_org_chart et mail_bot_hr avec hr ; pos_mrp, mrp_account et sale_mrp avec mrp ; deux tableaux de bord. Non installés ici : hr_maintenance, purchase_mrp | `pos_self_order/__manifest__.py:7-8` ; `pos_self_order_epson_printer/__manifest__.py:12, 14` ; `pos_online_payment_self_order/__manifest__.py:10, 15` ; `pos_hr/__manifest__.py:14, 27` ; `pos_hr_restaurant/__manifest__.py:13-14` ; `hr_skills/__manifest__.py:17, 40` ; `hr_org_chart/__manifest__.py:16-17` ; `mail_bot_hr/__manifest__.py:9, 11` ; `pos_mrp/__manifest__.py:14, 24` ; `mrp_account/__manifest__.py:21, 36` ; `sale_mrp/__manifest__.py:16, 24` ; `spreadsheet_dashboard_pos_hr/__manifest__.py:9, 14` ; `hr_maintenance/__manifest__.py:10, 19` ; `purchase_mrp/__manifest__.py:26, 28` |
| C52 | Réglages existants : « Impression du reçu avant le paiement », « Pourboires » | `pos_restaurant/views/res_config_settings_views.xml:32-34` ; `pos_restaurant/models/pos_config.py:14, 16` ; `point_of_sale/views/res_config_settings_views.xml:92` |
| C53 | Une commande encore ouverte est enregistrée sur le serveur avec ses lignes et ses paiements, à chaque retour au plan de salle | `point_of_sale/models/pos_order.py:111-126` ; `pos_restaurant/static/src/overrides/models/pos_store.js:253` |
| C54 | Libellés français tirés des fichiers de traduction ; « Link Table » sans traduction ; « Cash In/Out » traduit « Cash entrant/sortant » | `pos_restaurant/i18n/fr.po:655-661` ; `point_of_sale/i18n/fr.po:4121, 1478-1479` |
| C55 | Tableau de bord standard « PdV - Restaurant » : installé d'office avec pos_hr et pos_restaurant, réservé à l'administrateur du Point de Vente. Mesures : chiffre d'affaires, nombre de commandes, somme des convives, revenu par convive, commandes et chiffre d'affaires par table, quantités par produit et par catégorie de caisse. Filtres : période « du… au… », catégorie de caisse sans ses sous-catégories, produit, serveur. Le calcul des convives écarte les commandes à 0 convive mais ne filtre pas leur état | `spreadsheet_dashboard_pos_restaurant/__manifest__.py:8, 13` ; `spreadsheet_dashboard_pos_restaurant/data/dashboards.xml:4-13` ; `spreadsheet_dashboard_pos_restaurant/data/files/pos_restaurant_dashboard.json` (tableaux croisés « PoS Orders », « PoS Orders by Table », « Point of Sale Analysis by Product » ; filtres globaux) ; `spreadsheet_dashboard_pos_restaurant/i18n/fr.po:102-103, 181-182` |
| C56 | Vue croisée des commandes ; « Convives » est un champ enregistré, que la vue peut additionner | `point_of_sale/views/pos_order_view.xml:240-250, 257` ; `pos_restaurant/models/pos_order.py:9` |
| C57 | Espèces : le bouton est rendu par la barre de navigation, qui teste le contrôle des espèces de la caisse et le droit Facturation du compte de la session, sans condition de rôle ; la surcharge de pos_hr vise un accesseur qu'aucun gabarit n'utilise ; le test standard de pos_hr dit « Cash in/out should be accessible for all users » | `point_of_sale/static/src/app/navbar/navbar.xml:51` ; `point_of_sale/static/src/app/navbar/navbar.js:56-58` ; `point_of_sale/models/pos_session.py:163` ; `point_of_sale/static/src/app/pos_app.js:107-109` ; `pos_hr/static/src/overrides/models/Chrome.js:5-8` ; `pos_hr/static/tests/tours/pos_hr_tour.js:79-81` |
| C58 | Moyens de paiement d'une nouvelle caisse : le scénario standard reprend comme « Compte client » tout mode sans journal de la société ; le choix par défaut d'une caisse créée à la main écarte les modes « client obligatoire » | `point_of_sale/models/pos_config.py:51-67, 1027-1036` ; `pos_restaurant/models/pos_config.py:85, 112-121` |
| C59 | « Autoriser le partage d'addition » n'est coché d'office qu'à la création d'une caisse de restaurant, pas quand on modifie une caisse existante | `pos_restaurant/models/pos_config.py:30-54` |
| C60 | Autres chemins de retrait d'un produit envoyé : « Annuler la commande », corbeille de la liste des commandes, « Annuler les commandes » à la fermeture, division, touche % | `point_of_sale/static/src/app/screens/product_screen/control_buttons/control_buttons.xml:42-44` ; `point_of_sale/static/src/app/screens/ticket_screen/ticket_screen.js:429-441` ; `point_of_sale/static/src/app/navbar/closing_popup/closing_popup.js:292-311` ; `pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.js:131-143, 163-165` ; `point_of_sale/static/src/app/screens/product_screen/product_screen.js:163` |
| C61 | L'écriture d'une table ou d'une salle est réservée à l'administrateur du Point de Vente ; la réunion par glisser, le paiement d'une table réunie et le dessin du plan écrivent sur les tables | `pos_restaurant/security/ir.model.access.csv:2-5` ; `pos_restaurant/static/src/app/floor_screen/floor_screen.js:147-150, 213-217, 230-232` ; `pos_restaurant/static/src/overrides/components/payment_screen/payment_screen.js:17-26` ; `point_of_sale/static/src/app/models/data_service.js:334` |
| C62 | Le lien vers l'espace de gestion n'est proposé qu'à l'employé lié au compte de la caisse ; la création d'article dépend des droits de ce compte | `pos_hr/static/src/overrides/components/navbar/navbar.js:5-8` ; `point_of_sale/static/src/app/store/pos_store.js:167, 2021-2023` ; `pos_hr/static/src/overrides/models/pos_store.js:140-144` |
| C63 | Code PIN, badge et onglet « Paramètres » de la fiche employé réservés au groupe Employés / Responsable, comme la création d'un employé ; l'administrateur du Point de Vente n'implique que Point de Vente / Utilisateur et Inventaire / Utilisateur ; « Calculer le prix depuis la nomenclature » réservé à Fabrication / Administrateur | `hr/models/hr_employee.py:145-147` ; `hr/views/hr_employee_views.xml:190, 209-213` ; `hr/security/ir.model.access.csv:4-6` ; `point_of_sale/security/point_of_sale_security.xml:12-16` ; `mrp_account/views/product_views.xml:10-18` |
| C64 | Deux saisies du même produit fusionnent en une ligne, sans égard pour l'employé ni pour l'envoi ; le transfert fusionne aussi | `point_of_sale/static/src/app/models/pos_order_line.js:324-360` ; `pos_restaurant/static/src/overrides/models/pos_store.js:308-313` |
| C65 | Après 5 minutes sans activité, un écran de veille (heure et logo) remplace tout écran sauf celui du paiement | `point_of_sale/static/src/app/store/pos_store.js:185-200` ; `point_of_sale/static/src/app/pos_app.js:22` ; `point_of_sale/static/src/app/screens/saver_screen/saver_screen.xml` |
| C66 | Une table n'est occupée que si sa commande porte un produit, a été réservée (« Réservez la table ») ou est déjà enregistrée sur le serveur ; sinon la commande est jetée au retour au plan | `point_of_sale/static/src/app/models/pos_order.js:314-316` ; `pos_restaurant/static/src/overrides/models/pos_store.js:167-175, 253-258` ; `pos_restaurant/static/src/app/product_screen/order_summary/order_summary.js:5-28` ; `pos_restaurant/static/src/app/product_screen/order_summary/order_summary.xml:6` ; `pos_restaurant/i18n/fr.po:275-276` |
| C67 | « Envoyé » : avec des imprimantes de préparation réglées par familles, seuls les produits de ces familles comptent ; l'envoi n'est enregistré aussitôt sur le serveur que si un bon est imprimé ; « Commander » est inactif si aucun produit modifié n'a de catégorie de caisse | `point_of_sale/static/src/app/models/utils/order_change.js:42-60` ; `point_of_sale/static/src/app/store/pos_store.js:1101-1106, 1738-1761` ; `pos_restaurant/static/src/overrides/components/product_screen/actionpad_widget/actionpad_widget.js:32-38, 63-65` ; `pos_restaurant/static/src/overrides/models/pos_store.js:74-93` |
| C68 | Le clavier « Des convives ? » accepte 0 sur une commande qui porte des lignes | `pos_restaurant/static/src/app/control_buttons/control_buttons.js:36-44` |
| C69 | Le coût total d'une ligne est écrit par Odoo au paiement (ou à la fermeture de la session), ingrédients d'un kit compris | `point_of_sale/models/pos_order.py:464-476, 1487, 1767-1788` ; `pos_mrp/models/pos_order.py:9-18` |
| C70 | Une catégorie de produits se cherche sur son nom complet (« Boissons / Alcoolisé / Bière ») : filtrer sur « Boissons » ramène les sous-familles | `product/models/product_category.py:14, 30-35` ; `point_of_sale/views/pos_order_report_view.xml:60` |
| C71 | Remises : « Remises appliquées à la ligne » est coché par défaut et active la touche % ; le bouton de remise globale n'apparaît que si « Remises globales » est activé | `point_of_sale/models/pos_config.py:189` ; `point_of_sale/static/src/app/screens/product_screen/product_screen.js:163` ; `pos_discount/static/src/overrides/components/control_buttons/control_buttons.xml:5-10` ; `point_of_sale/i18n/fr.po:3328-3329, 4064-4065` |
| C72 | Marque « admin » de l'employé lié à un administrateur du Point de Vente : lui seul ferme la caisse quand l'écart dépasse le maximum autorisé | `pos_hr/models/hr_employee.py:33-40` ; `pos_hr/static/src/overrides/components/closing_popup/closing_popup.js:13-22` ; `point_of_sale/static/src/app/navbar/closing_popup/closing_popup.js:166-174` |
| C73 | « Suivi des modifications de commandes » : ligne et commande marquées « modifiées », récapitulatif dans l'historique de la session à la fermeture ; une commande jamais enregistrée sur le serveur est retirée sans trace | `point_of_sale/models/pos_order.py:388-389, 533-536, 1515` ; `point_of_sale/models/pos_session.py:476-482` ; `point_of_sale/static/src/app/store/pos_store.js:512-545` |
| C74 | La caisse s'ouvre avec un compte Odoo ; la session garde ce compte (« Ouvert par ») | `point_of_sale/controllers/main.py:16` ; `point_of_sale/models/pos_session.py:35-41` |
| C75 | Avec une imprimante Epson, la caisse s'ouvre par l'adresse `/pos/web`, que le commentaire du code dit servie en HTTP sur l'hébergement d'Odoo, sauf paramètre système contraire ; la synchronisation entre postes passe par le canal temps réel (websocket) | `point_of_sale/models/pos_config.py:693-703, 215-227` ; `point_of_sale/controllers/main.py:22-23` ; `point_of_sale/static/src/app/store/devices_synchronisation.js:26-27` |
| C76 | Remarque par produit (« Note cuisine ») ; menus composés | `point_of_sale/static/src/app/screens/product_screen/control_buttons/control_buttons.xml:7-11` ; `point_of_sale/static/src/app/screens/product_screen/control_buttons/control_buttons.js:125-130` ; `point_of_sale/i18n/fr.po:3877-3878` ; `point_of_sale/models/product_combo.py:6-8` |
| C77 | Article à attributs en caisse (lu dans le code) : fenêtre de choix ; cases à cocher seulement avec « Création de variante » = « Jamais » ; supplément de prix fixe, sans quantité ; aucun « moitié-moitié » | `point_of_sale/static/src/app/store/pos_store.js:646-693, 791-843` ; `point_of_sale/static/src/app/store/product_configurator_popup/product_configurator_popup.js:13-58, 147-172` ; `product/models/product_attribute.py:14-20, 28-50` |
| C78 | Bon de préparation (lu dans le code, jamais imprimé) : une ligne par choix, puis la « Note cuisine » ; en tête, « Sur place » ou « À emporter », la table ou le numéro ; ni nom libre ni client ; titres « New », « Cancelled », « Note » en chaînes fixes ; ticket : table et convives seulement | `point_of_sale/static/src/app/store/order_change_receipt_template.xml:8-26, 32-51` ; `point_of_sale/static/src/app/store/pos_store.js:1797-1804, 1846-1869` ; `pos_restaurant/static/src/overrides/components/receipt_header_patch.js:8-19` |
| C79 | Attributs sans variante et kit à lignes limitées à une valeur (exécuté côté serveur, essai S1) : la vente sort les ingrédients des choix faits ; le coût calculé ignore ces lignes ; aucun champ d'attribut dans l'« Analyse des ventes » | `point_of_sale/models/stock_picking.py:77-104` ; `mrp/models/stock_move.py:566-590` ; `mrp/models/mrp_bom.py:584-622, 730-744` ; `point_of_sale/report/pos_order_report.py:14-41` |
| C80 | Formules (lu dans le code) : article « Combo », un article par choix, « Prix supplémentaire » ; prix réparti sur les articles choisis ; chaque ligne imprimée selon sa propre catégorie ; aucune heure de validité | `product/models/product_combo.py:22-30, 53-73` ; `point_of_sale/static/src/app/store/combo_configurator_popup/combo_configurator_popup.js:24-56, 82-92` ; `point_of_sale/static/src/app/models/utils/compute_combo_items.js:11-45` ; `point_of_sale/static/src/app/store/pos_store.js:1915-1932` |
| C81 | Formule vendue (exécuté côté serveur, essai S2 ; prix des lignes écrits à la main d'après le code, C80) : seuls les articles choisis sortent du stock ; famille de la formule : 1 unité, 0 de chiffre | `point_of_sale/models/pos_order.py:133-188` ; `point_of_sale/models/stock_picking.py:34` ; `point_of_sale/report/pos_order_report.py:56-96` |
| C82 | Commande sans table (lu dans le code) : bouton « + », nom libre ; « Manger sur place / À emporter », sa position fiscale et son champ sur la commande, bascule par Actions ; 1 convive posé par l'écran ; rien pour la livraison | `point_of_sale/static/src/app/components/order_tabs/order_tabs.xml:4-16` ; `pos_restaurant/static/src/app/control_buttons/control_buttons.xml:32-48` ; `pos_restaurant/models/pos_config.py:18-23` ; `pos_restaurant/static/src/overrides/models/pos_order.js:5-10` ; `pos_restaurant/models/pos_order.py:8-10` |
| C83 | Ventes sans table dans les rapports (calcul refait côté serveur avec le filtre du tableau de bord, essai S3 ; tableau de bord non ouvert) : toute commande d'au moins 1 convive est retenue ; l'« Analyse des ventes » n'a ni table, ni convives, ni « à emporter » | `spreadsheet_dashboard_pos_restaurant/data/files/pos_restaurant_dashboard.json` (tableau croisé « PoS Orders ») ; `point_of_sale/report/pos_order_report.py:14-41` |
| C84 | Imprimantes de préparation (lu dans le code ; réglage accepté côté serveur, essai S4 ; aucun bon imprimé) : chacune a ses catégories ; une catégorie peut aller sur deux imprimantes | `point_of_sale/models/pos_printer.py:12-17` ; `point_of_sale/static/src/app/store/pos_store.js:335-348, 1771-1844` |
| C85 | Moments de la journée (lu dans le code ; essai S5) : seule la commande en libre-service lit les heures « Disponible entre » ; règle de prix à dates-heures absolues ; regroupement par heure absent du menu des vues | `pos_self_order/models/pos_category.py:12-29` ; `pos_self_order/static/src/app/self_order_service.js:156-180` ; `product/models/product_pricelist_item.py:29-36` ; `web/static/src/search/utils/dates.js:48-54` |
| C86 | Vente à la dose (exécuté côté serveur, essai S6) : la caisse vend dans l'unité de l'article ; quantités arrondies à la précision décimale des unités, 2 d'origine | `point_of_sale/static/src/app/models/product_product.js:122-126` ; `mrp/models/mrp_bom.py:637-639` ; `stock/models/stock_quant.py:82-87` |
| C87 | Une ou plusieurs caisses (lu dans le code) : la commande sans table est partagée entre les postes d'une même caisse, mais absente du plan ; une caisse ne charge que les commandes ouvertes de sa session (au chargement ; voir C98) | `pos_restaurant/static/src/overrides/models/pos_store.js:160-188, 253-266` ; `point_of_sale/static/src/app/store/devices_synchronisation.js:193-202` ; `point_of_sale/models/pos_order.py:62-64` |
| C88 | Deux caisses sur la même salle (exécuté côté serveur, essai S7) : une seule commande ouverte par table ; elle passe dans la session de la caisse qui enregistre en dernier | `pos_restaurant/models/pos_order.py:12-22` ; `point_of_sale/models/pos_order.py:105-108` |
| C89 | Envoi en plusieurs temps (lu dans le code) : aucun champ de « service » ; un double-clic met de côté une ligne pas encore envoyée | `point_of_sale/models/pos_order.py:1465` ; `pos_restaurant/static/src/overrides/models/pos_order_line.js:22-34` ; `point_of_sale/static/src/app/models/utils/order_change.js:84-101` |
| C90 | Gestes du profil sans test de rôle (lu dans le code) : attributs, formule, commande sans table, « à emporter », « Liste de prix » | `point_of_sale/static/src/app/screens/product_screen/control_buttons/control_buttons.xml:24-28` ; `point_of_sale/static/src/app/screens/product_screen/control_buttons/control_buttons.js:81-111` ; `pos_restaurant/static/src/app/control_buttons/control_buttons.js:70-98` |
| C91 | Droits de gestion (exécuté côté serveur, essais S8 et V9) : Point de Vente / Administrateur écrit attributs, choix de combo, catégories et imprimantes ; nomenclatures : Fabrication / Administrateur ; règles de prix : Inventaire, Fabrication, Ventes ou Achats / Administrateur, ou « Création de produits » ; un utilisateur créé à l'écran recevrait ces droits par défaut (écran non vu) | `point_of_sale/security/ir.model.access.csv:20-26, 51-54` ; `pos_mrp/security/ir.model.access.csv:2-3` ; `stock/security/ir.model.access.csv:28` ; `mrp/security/ir.model.access.csv:44` ; `product/security/ir.model.access.csv:24` |
| C92 | Scénario standard « Restaurant » (exécuté côté serveur, essai V5) : il charge, même sans données de démonstration, salles, tables, articles, sessions et commandes d'exemple | `pos_restaurant/models/pos_config.py:107-135` ; `pos_restaurant/data/restaurant_session_floor.xml:22-178, 496-650` |
| C93 | Vente sans table (lu dans le code ; exécuté côté serveur, S14, S15) : « + » toujours accessible ; divisions et remboursements sans table aussi ; 1 personne posée par l'écran, à chaque chargement (lu dans le code) ; 0 accepté par le serveur, écarté du tableau de bord | `point_of_sale/static/src/app/components/order_tabs/order_tabs.xml:4-6` ; `pos_restaurant/static/src/overrides/models/pos_order.js:8` ; `point_of_sale/static/src/app/models/related_models.js:1162-1165` ; `spreadsheet_dashboard_pos_restaurant/data/files/pos_restaurant_dashboard.json:1697` |
| C94 | « Manger sur place / À emporter » (lu dans le code ; exécuté côté serveur, S14) : position fiscale remise au choix d'un client ; bouton des positions fiscales et « Taxes flexibles » masqués ; pas de position « à emporter » au plan camerounais | `pos_restaurant/views/res_config_settings_views.xml:21-31, 53-55` ; `pos_restaurant/static/src/app/control_buttons/control_buttons.xml:47` ; `point_of_sale/static/src/app/models/pos_order.js:946-952` ; `l10n_cm/data/template/account.fiscal.position-cm.csv:1-6` |
| C95 | Livraison (exécuté côté serveur, S14 ; impression lue dans le code) : adresse et téléphone chargés ; seule la « Note générale » s'imprime ; ni heure, ni livreur, ni statut ; commande ouverte : fermeture refusée, ou « Annuler les commandes », qui l'annule sans l'effacer (lu dans le code) | `point_of_sale/models/res_partner.py:32-37` ; `point_of_sale/models/pos_order.py:321-391, 1100-1103` ; `point_of_sale/static/src/app/navbar/closing_popup/closing_popup.js:292-311` ; `point_of_sale/static/src/app/store/pos_store.js:545` |
| C96 | Caisse unique (exécuté côté serveur, S9) : un journal d'espèces, celui du premier mode ; avec deux modes, rendu, mouvements et comptage sur le premier, écart fictif au rapport | `point_of_sale/models/pos_session.py:278-301` ; `point_of_sale/models/pos_config.py:442-450` ; `point_of_sale/models/report_sale_details.py:158-206` |
| C97 | Qui a encaissé (exécuté côté serveur, S9) : fermeture par employé, poste absent ; imprimante de tickets, tiroir et employés réglés par caisse (lu dans le code) | `pos_hr/models/pos_session.py:71-91` ; `point_of_sale/static/src/app/hardware_proxy/hardware_proxy_service.js:161-170` ; `pos_epson_printer/models/pos_config.py:10-16` ; `pos_hr/models/pos_config.py:37-44` |
| C98 | Deux caisses, une salle (exécuté côté serveur, S10 ; synchronisation lue dans le code ; complète C88) : « PdV sécurisé » masqué pour la restauration, accepté écrit par la technique ; rien de l'autre caisse au chargement ni en synchronisation ; l'écran « Commandes » trouve l'addition ; total faux après fusion ; paiement commencé ailleurs hors des fermetures | `point_of_sale/views/res_config_settings_views.xml:117` ; `point_of_sale/static/src/app/store/devices_synchronisation.js:193-202` ; `point_of_sale/static/src/app/store/pos_store.js:1413-1438` |
| C99 | Caisse du bar ajoutée (exécuté côté serveur, S11, S12) : modes hors espèces sans « client obligatoire » (ici « Carte »), ni les espèces de la principale, ni « Ardoise client » ; une salle d'office ; même stock ; principale ouverte, ses modes, salles et familles bloqués ; sans espèces, pas de rendu ; archivage, pas suppression | `point_of_sale/models/pos_config.py:51-67, 627-631` ; `pos_restaurant/models/pos_config.py:25-28, 54-69` ; `point_of_sale/models/pos_order.py:232-235` |

**AITE HOUSE.** Dépôt au commit `6b35539` (11/11/2026) ; chemins relatifs à la racine du dépôt. H21 à H29, ajoutés le 13/11/2026 pour le profil de l'établissement, sont lus dans le code au commit `9e9630d`, qui n'y ajoute que le présent document et une ligne à la feuille de route ; H30 et H31 au commit `413ecc7`.

| Réf. | Point | Fichier:ligne |
|---|---|---|
| H1 | « Pas de plan de salle ni de tables : AITE HOUSE n'installe pas pos_restaurant » | `docs/videos/scenarios/c3_bar_restaurant.py:9` |
| H2 | Analyse AITE : une ligne par ligne de commande, un seul auteur (l'utilisateur Odoo), date de la commande, commandes réglées seulement | `addons/aite_pos_analytics/models/pos_analytics_report.py:113-118, 142` |
| H3 | Famille des analyses AITE : la catégorie de produits ; onglet « Par catégorie » ; champ de recherche sur la catégorie | `addons/aite_pos_analytics/models/pos_analytics_report.py:78, 120` ; `addons/aite_pos_analytics/models/pos_dashboard.py:316` ; `addons/aite_pos_analytics/views/pos_analytics_report_views.xml:64` |
| H4 | Périodes du tableau de bord AITE, dont la période personnalisée | `addons/aite_pos_analytics/static/src/js/services/utils.js:282` ; `addons/aite_pos_analytics/static/src/js/components/filter_bar.js:92` |
| H5 | Ardoise créée à la création, à la modification et à l'enregistrement d'une commande, sans contrôle de son état ; une seule ardoise par commande | `addons/aite_pos_credit/models/pos_order.py:81-116` |
| H6 | Note de chambre et fidélité : rien n'est fait tant que la commande n'est pas réglée | `addons/aite_hotel_pos_link/models/pos_order.py:160` ; `addons/aite_loyalty/models/hooks.py:38` |
| H7 | Bouton « Mettre sur ardoise » affiché sans condition de rôle | `addons/aite_pos_credit/static/src/js/pos/payment_screen_button.xml:13` |
| H8 | Mode « Ardoise client » créé sans journal et rattaché aux caisses existantes à l'installation ; Odoo le reprend ensuite comme « Compte client » d'une nouvelle caisse (C58) | `addons/aite_pos_credit/hooks.py:63-72, 87-92` |
| H9 | Champ de folio réservé au profil Réception (écart n° 78) ; le test ne couvre qu'un chemin de relecture | `addons/aite_hotel_pos_link/models/pos_order.py:45` ; `addons/aite_hotel_pos_link/tests/test_room_charge.py:403` |
| H10 | « Manager — Analyses POS » implique l'administrateur du Point de Vente | `addons/aite_pos_analytics/security/pos_analytics_security.xml:23-29` |
| H11 | Tableau de bord du stock : tout article sorti est retenu, donc « Rupture » à stock nul ; chiffre d'affaires estimé sur les sorties | `addons/aite_stock_dashboard/models/stock_dashboard.py:83, 281-298, 742` |
| H12 | Seules les réceptions d'un fournisseur comptent comme entrées ; l'ajustement d'inventaire est classé à part | `addons/aite_stock_dashboard/models/stock_dashboard.py:559-562, 685-687` |
| H13 | Coût unitaire photographié à la création de la ligne ; coût total et marge calculés par AITE dans des champs du même nom que ceux d'Odoo ; le coût total est réécrit par Odoo au paiement (C69), la marge n'est pas recalculée ; rattrapage documenté par le shell seulement | `addons/aite_pos_analytics/models/pos_order_line.py:27-57, 59-69` ; `addons/aite_pos_analytics/models/pos_analytics_report.py:126-128` ; `addons/aite_pos_analytics/README.md:44` |
| H14 | Répartition des paiements sans filtre sur l'état de la commande ; totaux de session dépendant de toutes les lignes de la session | `addons/aite_pos_analytics/models/pos_dashboard.py:690` ; `addons/aite_pos_analytics/models/pos_session.py:98` |
| H15 | Panier moyen = chiffre d'affaires / nombre de commandes ; « tickets » du tableau exécutif | `addons/aite_pos_analytics/models/pos_dashboard.py:245-253` ; `addons/aite_exec_dashboard/models/exec_dashboard.py:267` |
| H16 | Cas de recette D06 (remise tracée) et D12 (ventes par vendeur) | `recette/cas_de_test.py:241, 272` |
| H17 | Modules qui exigent le socle hôtelier | `addons/aite_loyalty/__manifest__.py:38-39` ; `addons/aite_exec_dashboard/__manifest__.py:39` ; `addons/aite_hotel_pos_link/__manifest__.py:34` |
| H18 | Jeu de démonstration : une seule caisse, « Caisse Boutique (démo) » ; catégories à deux niveaux | `addons/aite_demo_data/models/demo_generator.py:557, 587` ; `addons/aite_demo_data/data/01_product_categories.xml:4, 97` |
| H19 | Étude comparative : plan de salle « Couvert » ; « POS hors-ligne avec plan de salle » | `docs/etude_comparative/build_etude.py:150, 418` |
| H20 | Feuille de route : dépendances standard ; F05, F09, F10, F15, F16, F17, F19, F21, F25 ; ticket d'impression du client pilote | `ROADMAP.md:43, 64, 68, 74, 79, 80, 81, 88, 90, 94, 165` |
| H21 | Cinq modules sans le socle hôtelier ; les onze autres : le socle et les dix modules qui en dépendent directement (ligne `depends` des manifestes) ; aucun ne dépend de pos_restaurant, pos_hr, mrp ni pos_mrp ; `aite_pos_credit` dépend de `sale` | `addons/aite_pos_analytics/__manifest__.py:30-35` ; `addons/aite_pos_credit/__manifest__.py:45-51` ; `addons/aite_stock_dashboard/__manifest__.py:54` ; `addons/aite_purchase_dashboard/__manifest__.py:55` ; `addons/aite_direction_dashboard/__manifest__.py:17-22, 34` ; par exemple `addons/aite_city_tax/__manifest__.py:31`, `addons/aite_demo_data/__manifest__.py:77` |
| H22 | Dans le dépôt, FCFA posé par la graine hôtelière (avec le pays) et par le jeu de démonstration (devise seule) ; aucun ne pose de plan comptable ; « Écart (FCFA) » écrit en dur | `dev/seeds/seed_laverandah.py:4-8` ; `addons/aite_demo_data/models/demo_generator.py:202-253` ; `addons/aite_pos_analytics/static/src/xml/views.xml:922` |
| H23 | Fiches d'applications : nom du client pilote ; « Compatible Odoo 18 Enterprise » | `addons/aite_pos_analytics/__manifest__.py:3, 22` ; `addons/aite_direction_dashboard/__manifest__.py:5, 12` ; `addons/aite_pos_credit/__manifest__.py:37` |
| H24 | Cockpit Direction : bloc Hébergement calculé seulement si le modèle `aite.hotel.dashboard` existe ; « Annulations / retours » et « Remises élevées » toujours à zéro | `addons/aite_direction_dashboard/models/direction_dashboard.py:426-437, 546-583, 768-769` ; `addons/aite_direction_dashboard/static/src/xml/direction_dashboard.xml:273-306` |
| H25 | Cartes du client pilote : « Top bières », « Consignes d'emballages » | `addons/aite_pos_analytics/models/pos_dashboard.py:512-519` ; `addons/aite_purchase_dashboard/static/src/xml/dashboard.xml:302-327` |
| H26 | Tests ignorés sans la suite hôtelière, dont la journée après minuit ; tests qui ne supportent pas les données de démonstration du Point de Vente | `addons/aite_direction_dashboard/tests/test_consistency.py:176-194, 232-234` ; `addons/aite_pos_credit/tests/test_ecarts_caisse.py:87-91` ; `addons/aite_pos_credit/tests/test_migration.py:36-40` |
| H27 | `aite_demo_data` : dépend du socle hôtelier ; 74 produits de restaurant, aucune pizza | `addons/aite_demo_data/__manifest__.py:74-88` ; `addons/aite_demo_data/data/02_products_restaurant.xml:4-734` |
| H28 | Outils et documentation qui supposent l'hôtel ; l'audit des menus ne regarde que les actions de type fenêtre | `dev/setup_env.sh:30-33, 126-130` ; `dev/run_tests.sh:41-46` ; `docs/INSTALLATION.md:1, 101-102` ; `dev/audit_menus.py:24, 27, 50` |
| H29 | Sans hôtel, quatre groupes AITE (Analyses POS, POS Crédit) ; aucun pour Stock, Achats et Direction | `addons/aite_pos_analytics/security/pos_analytics_security.xml:16-48` ; `addons/aite_pos_credit/security/pos_credit_security.xml:11-30` |
| H30 | `aite_pos_analytics` (exécuté côté serveur, S13) : point de vente = caisse de la commande ; écart par session, sur le premier mode espèces | `addons/aite_pos_analytics/models/pos_analytics_report.py:22-25` ; `addons/aite_pos_analytics/models/pos_session.py:144-195` |
| H31 | « Ardoise client » rattachée aux caisses présentes à l'installation (lu dans le code ; aucune en S13) ; reçue par la première caisse et le scénario standard, pas par une seconde faite à la main (exécuté côté serveur, S13) ; « caisse d'origine » = caisse de la commande | `addons/aite_pos_credit/hooks.py:86-97` ; `addons/aite_pos_credit/models/pos_credit.py:66-68` |

**Essais côté serveur du 12/11/2026.** Base jetable `aite_relecture_tech` : Odoo 18 Community au commit ci-dessus, avec `point_of_sale`, `pos_restaurant`, `hr`, `mrp`, `aite_pos_analytics` et `aite_pos_credit`, sans données de démonstration (81 modules installés). Essais joués dans `odoo-bin shell` et annulés à la fin (rollback), d'abord pendant la relecture technique, puis rejoués à l'identique pendant la correction, avec les mêmes résultats. Aucun n'est passé par l'écran de caisse. Les montants sont dans la monnaie de la base d'essai. Les scripts et leurs sorties sont des fichiers de travail de la session, hors dépôt ; la base jetable est à supprimer une fois les essais à l'écran faits.

| Essai | Ce qui a été joué | Résultat |
|---|---|---|
| A | Liste des modules installés | Celle de la partie 5.1 |
| B | Écriture d'une table par un compte « Utilisateur » du Point de Vente | Refusée (erreur d'accès) |
| B2 | Fiche employé vue par un Administrateur du Point de Vente sans droit Employés | Ni code ni badge visibles ; création d'un employé refusée |
| C | Tableaux de bord présents | « PdV - Restaurant », réservé au groupe Point de Vente / Administrateur |
| D | Recherche des produits dont la catégorie contient « Boissons essai » (le même mécanisme sert au filtre des analyses) | Elle retrouve le produit rangé trois niveaux plus bas |
| E0, E, I | Moyens de paiement d'une nouvelle caisse, `aite_pos_credit` installé | Caisse du scénario standard « Restaurant » : Carte, Ardoise client, Espèces ; caisse créée ensuite à la main : Carte, Espèces |
| F | Plat à nomenclature « Kit », trois plats payés | Poulet et riz : 10 → 7. Plat sans coût : coût 0, marge 100 %. Après « Calculer le prix depuis la nomenclature » : coût du plat 1 000, vente passée inchangée |
| G | Commande à l'état « Nouveau » ; paiement « Ardoise client » enregistré sans validation (mode rattaché à la main à la caisse d'essai) ; puis annulation | Ardoise créée, 2 000, ouverte ; toujours ouverte après l'annulation de la commande |
| H | « Suivi des modifications de commandes » coché ; quantité d'une ligne baissée de 3 à 2 | Ligne et commande marquées « modifiées » ; note « Quantité commandée : 3.0→2 » |
| J | Plat à fiche technique suivi en stock, catégorie au coût moyen ; trois plats payés 15 000 | Coût des ventes 3 000 ; marge 15 000 ; taux 100 % ; mêmes chiffres dans la vue d'analyse AITE |
| K | Champs « Table » et « Convives » de la commande | Enregistrés ; « Convives » s'additionne |

**Essais côté serveur du 13/11/2026 (profil de l'établissement).** Bases jetables, même commit, supprimées ensuite ; aucun essai n'est passé par l'écran de caisse : les commandes ont été créées côté serveur. `aite_profil_odoo` (service à table, connexion par code, fabrication ; 70 modules, en anglais et en dollars) : S1 à S8. `aite_profil_resto` (pile « restaurant seul », en français, sans démonstration ; 90 modules) : V1, V3 à V8. `aite_profil_test` (même pile, avec démonstration ; 92 modules) : V2. `aite_profil_relecture` (même pile, pays Cameroun, pendant la relecture technique ; 92 modules) : V9.

S1 : pizza à attributs « Jamais » et kit à lignes limitées à une valeur, trois ventes payées (C79 ; grande : mozzarella 0,10 + 0,05 ; coût calculé 1,8, sans ces lignes). S2 : formule à trois choix, payée ; lignes écrites à la main d'après le code de l'écran, formule à 0 et prix répartis (C81). S3 : deux ventes à table (4 et 2 convives) et trois sans table (1 convive écrit à la main ; vide par défaut côté serveur), mesures recalculées avec le filtre du tableau de bord : 88 pour 9 convives (9,78) ; tables seules, 70 pour 6 (11,67) ; « À emporter », 2 commandes sur 5 (C83). S5 : heures « Disponible entre » d'une catégorie ; règle de prix datée (2,0, puis 1,5 dans la fenêtre) ; groupes 8, 13 et 21 au fuseau de Douala (C85). S6 : whisky, 3 doses de 4 cl et 1 bouteille de 70 cl, 2,10 L → 1,28 L ; café à 7 g : 0,01 kg sorti d'un stock en kilos, 7 g d'un stock en grammes (C86). S4, S7 et S8 : lignes C84, C88, C89 et C91. V1 : installation à froid de la pile « restaurant seul », base créée en ligne de commande, sans pays : 90 modules, journal sans erreur ni avertissement, aucun modèle hôtelier, société en USD. V2, V3 : tests des cinq modules ; avec les données de démonstration, 1 échec et 6 erreurs sur 264 ; sans, aucun, et 4 ignorés. V4 à V7 : lignes H24, C92, H27 et H28. V8 : vente de table par l'entrée qu'utilise l'écran, rangée dans les analyses AITE sous le compte de la caisse, pas sous l'employé. V9 : même pile, base créée par la fonction qu'appelle l'écran de création (`odoo/service/db.py:84-86`), pays Cameroun : société en XAF, plan comptable « cm », 92 modules, journal sans erreur ni avertissement ; création d'une règle de prix refusée à un compte qui n'a que Point de Vente / Administrateur (journal relu pendant la correction).

**Essais côté serveur du 13/11/2026 (réponses d'AITE).** Bases jetables créées sans pays, donc en dollars, puis supprimées ; commandes écrites comme l'écran les envoie, sous le compte admin. `aite_rep_caisses` : S9 (deux modes espèces), S10 (deux caisses, une salle, avec et sans « PdV sécurisé »), S11 (sans espèces), S12 (caisse du bar ajoutée, principale ouverte), S13 (modules AITE). `aite_rep_sanstable` : S14 (cinq commandes, de la table à la livraison), S15 (personnes et prix moyen ; division refaite à la relecture comme l'écran la fait).

**Lectures qui se contredisaient.**

- *Commande ouverte annulée : effacée ou conservée ?* Une lecture la disait effacée de la base. Relecture faite : la caisse appelle l'annulation (`point_of_sale/static/src/app/store/pos_store.js:545`, `point_of_sale/models/pos_order.py:1100-1107`), qui passe la commande à l'état « Annulé » et la conserve ; l'effacement (`point_of_sale/models/pos_order.py:1387-1400`) n'est appelé que par la commande en libre-service (`pos_self_order/controllers/orders.py:100`). Tranché : la commande est conservée.
- *Entrées et sorties d'espèces : droits de base ou droits avancés ?* La documentation les range dans les droits de base [2] ; une première lecture du code les disait réservées au rôle manager (`pos_hr/static/src/overrides/models/Chrome.js:5-8`). Relecture faite : cette surcharge vise un accesseur qu'aucun gabarit n'utilise ; le bouton est rendu par la barre de navigation, sans condition de rôle, et le test standard de pos_hr le confirme (C57). Tranché par le code : droits de base, comme la documentation ; non essayé à l'écran.
- *Nombre de niveaux de droits des employés.* La consigne de travail en évoquait trois ; le code de la version 18.0 a deux rôles, caissier et manager (`pos_hr/models/pos_config.py:10-15`), plus une marque « admin » pour l'employé lié à un compte Administrateur, utilisée pour un seul geste : fermer la caisse malgré un écart supérieur au maximum autorisé (C72). Les versions suivantes d'Odoo n'ont pas été vérifiées.
- *Division d'une addition.* La documentation dit que la seconde addition doit être payée avant de revenir à la première [1] ; ce point n'a pas été contrôlé dans le code. À vérifier à l'écran.
- *Réunir des tables en glissant.* La première version attribuait ce geste à la documentation ; relue, elle ne décrit que Actions puis « Transférer / Fusionner » [1]. Le glisser se lit dans le code seulement (C31).
- *Rapports par personne et par table.* Une première lecture les disait absents d'Odoo. Relecture faite : le tableau de bord standard « PdV - Restaurant » et la vue croisée des commandes en donnent une partie (C55, C56) ; écran non vu.
- *« Ardoise client » sur une nouvelle caisse.* Une première lecture limitait ce mode aux caisses existantes à l'installation. L'essai montre qu'une caisse créée par le scénario standard le reçoit (C58, essais E0 et I).
- *`purchase_mrp`.* Le 12/11/2026, il était donné comme non installé, à tester (C51, essai A, sans les Achats). Le 13/11/2026, il s'installe avec la pile « restaurant seul », qui comprend les Achats (essai V1).

**Exécutés côté serveur, à rejouer à l'écran :** sortie de stock des ingrédients d'un plat à fiche technique (REST-20) ; ardoise créée sur une table non encaissée (partie 5.3) ; liste des modules installés d'office (partie 5.1) ; marge à 100 % d'un plat sans coût et coût total réécrit au paiement (REST-21) ; recherche par famille parente (REST-23) ; écriture d'une table refusée à un compte « Utilisateur » (REST-13, REST-16) ; note du suivi des modifications après une baisse de quantité (REST-12). Du 13/11/2026 : les essais S1 à S15, V5, V8 et V9 ci-dessus.

**Lus dans le code et jamais exécutés, à essayer avant de les promettre :** déplacer un produit par division puis transfert (REST-15) ; additions « annulées » créées par une réunion de tables ou un déplacement (REST-13, REST-22) ; nombre de personnes après une division ou une réunion (REST-25) ; table ouverte sans produit libérée au retour au plan (REST-06) ; écran de veille après 5 minutes (REST-17) ; bouton « Commander » inactif sans catégorie de caisse et envoi non enregistré sans bon imprimé (REST-10) ; espèces ouvertes à tout employé (REST-03) ; touche Prix désactivée (REST-04) ; remises désactivées par les deux réglages (partie 4.2) ; tableau de bord « PdV - Restaurant » et mesure « Convives » de la vue croisée (REST-25, REST-26) ; impression Epson et canal temps réel derrière l'hébergement (partie 4.1). Pour le profil : fenêtres de choix d'une pizza et d'une formule, prix et rapports d'une formule (PROF-01, PROF-03) ; bouton « + », nom libre, personne posée d'office, bascule « à emporter » (PROF-04, REST-25) ; bons par poste de préparation et leurs titres (PROF-05) ; liste de prix choisie à la main (PROF-06) ; double-clic de mise de côté (partie 4.1) ; addition de bar transférée, caisse sur plusieurs postes (PROF-07, PROF-08).
