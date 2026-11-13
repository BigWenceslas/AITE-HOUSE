# AITE — Suivi des activités CRM

**Odoo 19 (Enterprise & Community) · module `aite_crm_activity` · version 19.0.2.0.0**

Trois outils pour que plus aucune opportunité ne reste sans suite :

1. un **tableau de bord** qui suit et gère les tâches et activités
   (appels, e-mails, rendez-vous, à faire…) planifiées sur les
   opportunités ;
2. un **récapitulatif envoyé chaque matin** par e-mail à chaque
   utilisateur, avec la liste de ses activités en cours ;
3. un **rapport d'analyse** (tableau croisé, graphique, liste) des
   activités ouvertes et réalisées.

## Le tableau de bord

**CRM → Suivi des activités**

En haut, les **filtres** : commercial (ou « Non assigné »), équipe
commerciale, type d'activité et **période** (7 derniers jours, ce mois,
mois dernier, ce trimestre ou dates au choix). Ils sont conservés quand on
revient d'une opportunité par le fil d'Ariane.

| Zone | Contenu |
|---|---|
| Alertes | Un bandeau signale les retards **critiques** et les opportunités **dormantes** ; son bouton affiche la liste concernée. |
| Indicateurs | Activités **en retard** (dont critiques, nombre d'opportunités et **montant en jeu**), **du jour**, **à venir**, **réalisées** sur la période (avec la **comparaison avec la période précédente** de même durée et le taux d'activités faites **à temps**), **opportunités sans activité** (avec leur montant). Un clic filtre la liste. |
| Onglet **À traiter** | La liste des activités, triée par échéance (badge « élevé » ou « critique » selon le retard), avec les actions **Fait** (compte rendu facultatif publié dans l'historique), **Reporter** (demain, lundi prochain, dans une semaine ou une date) et **Réassigner** (avec confirmation). Puis les **opportunités sans activité planifiée**, avec la date de la dernière action, le badge « dormante » et le bouton **Planifier**. |
| Onglet **Équipe** | Le tableau **par commercial** (retards, jour, à venir, réalisées, sans activité, avec une ligne « Total équipe » et une barre de charge) : un clic sur un chiffre affiche les activités correspondantes. Puis le **plan de charge** : activités en retard et à faire jour par jour, par commercial. |
| Onglet **Tendances** | Les 12 dernières semaines : activités faites à temps, faites en retard et créées ; classements par type d'activité et par commercial ; lien vers le rapport d'analyse. |
| Aperçu d'une opportunité | Un clic sur une opportunité ouvre un panneau latéral : client et coordonnées, étape, montant, activités à faire (avec les mêmes actions) et dernières activités réalisées avec leur compte rendu ; « Ouvrir la fiche » pour aller plus loin. |

Une activité sur une opportunité **perdue** ne compte plus dans les
activités à faire (Odoo la laisse ouverte) ; si elle avait été faite, elle
reste comptée dans les réalisées.

**Qui voit quoi.** Les droits d'Odoo s'appliquent (Paramètres →
Utilisateurs → droits « Ventes ») :

- **Utilisateur : mes documents seulement** : le tableau s'ouvre sur ses
  propres activités ; il voit aussi celles qu'on lui a assignées sur
  l'opportunité d'un collègue (sans le détail de l'opportunité). Il ne
  peut pas réassigner (refusé aussi par le serveur).
- **Utilisateur : tous les documents** et **Administrateur** : le tableau
  s'ouvre sur les activités de tout le monde, et ils peuvent réassigner.

Le tableau de bord et le rapport sont réservés aux utilisateurs du CRM.

**Lien direct** : `/odoo/activites-en-retard` ouvre le tableau de bord sur
les activités en retard (c'est le lien du récapitulatif du matin quand on
a des retards).

## Le rapport d'analyse

**CRM → Analyse → Suivi des activités (analyse)** (lien direct
`/odoo/analyse-activites`) : une ligne par activité sur une piste ou
opportunité, ouverte ou réalisée, à analyser en tableau croisé, graphique
ou liste (export Excel possible). Mesures : nombre, en retard, jours de
retard, taux d'activités faites à temps. Filtres prêts : en retard,
aujourd'hui, à venir, réalisées, mes activités, retard critique, réalisées
ce mois-ci… Les mêmes règles de visibilité que le CRM s'appliquent : sur
une activité qui lui est assignée sur l'opportunité d'un collègue, un
commercial « mes documents » ne voit que le nom de l'opportunité (client,
étape, commercial et issue restent vides, export compris). L'export
demande le droit « Export : autorisé » (Paramètres → Utilisateurs).

## Le récapitulatif du matin

Chaque jour, à l'heure choisie, chaque utilisateur qui a des activités en
cours sur des opportunités reçoit un e-mail :

- ses activités **en retard** (avec le nombre de jours de retard), **du
  jour** et **à venir** sur les prochains jours ;
- pour chacune : l'échéance, le type, le résumé, l'opportunité (lien
  direct), le client, l'étape et le montant ;
- un badge « élevé » ou « critique » selon le retard, et le **montant en
  jeu** des opportunités en retard ;
- un bouton vers son tableau de bord (directement sur ses retards s'il en
  a).

Un utilisateur sans activité en cours ne reçoit rien. La date « du jour »
suit le fuseau horaire de chaque utilisateur, et l'e-mail est rédigé dans
sa langue pour les dates. Une personne sans droits sur le CRM à qui on a
confié une activité sur une opportunité (un comptable, par exemple) la
reçoit aussi, sans lien vers le tableau de bord.

**Réglages** : CRM → Configuration → Paramètres → bloc **Suivi des
activités** :

| Réglage | Par défaut | Rôle |
|---|---|---|
| Récapitulatif du matin | Activé | Active ou coupe l'envoi pour tout le monde |
| Heure d'envoi | 7:00 | Une seule heure pour tout le monde, dans le fuseau ci-dessous |
| Fuseau horaire | Africa/Douala | L'envoi garde la même heure locale toute l'année |
| Activités à venir (jours) | 3 | Jours à venir inclus en plus des retards et du jour ; 0 = seulement retards et jour |

Dans le même bloc, **Tableau de bord et seuils de retard** :

| Réglage | Par défaut | Rôle |
|---|---|---|
| Tableau de bord : activités à venir (jours) | 7 | Fenêtre « À venir » et largeur du plan de charge (14 jours au plus) |
| Retard élevé à partir de (jours) | 3 | Badge « élevé » |
| Retard critique à partir de (jours) | 7 | Badge « critique » et alerte ; doit être supérieur au retard élevé |
| Opportunité dormante après (jours) | 14 | Opportunité sans activité ni action depuis ce nombre de jours |

Le bouton **M'envoyer mon récapitulatif maintenant** envoie l'e-mail tout
de suite : il permet de le voir et de vérifier que l'envoi des e-mails
fonctionne (en cas d'échec, le message affiche la raison).

**Se désabonner** : chaque utilisateur, depuis son avatar → **Mes
préférences** → case « Récapitulatif CRM du matin ».

**Prérequis : un moyen d'envoyer des e-mails.** Configurez un serveur
sortant dans Paramètres → Technique → E-mail → **Serveurs de messagerie
sortants** (mode développeur), ou à défaut les paramètres `smtp_server`,
`smtp_port`, `smtp_user`, `smtp_password` et `smtp_ssl` du fichier
`odoo.conf`. Sans l'un ni l'autre, Odoo essaie un serveur local
(`localhost:25`), souvent absent sur un VPS. Les récapitulatifs sont mis
en file d'attente puis envoyés par l'action planifiée « E-mail :
Gestionnaire de la file d'attente des e-mails » (Paramètres → Technique →
Automatisation → Actions planifiées), que le module déclenche aussitôt :
ils partent dans les minutes qui suivent l'heure d'envoi.

## Installation sur le VPS

Même procédure que pour le module WhatsApp (voir son README pour le
détail des cas) :

1. Envoyer `aite_crm_activity.zip` sur le VPS, puis le décompresser dans
   le dossier des modules personnalisés déclaré dans `addons_path` :

   ```bash
   sudo unzip -o /tmp/aite_crm_activity.zip -d /opt/odoo/custom-addons/
   ```

   ```bash
   sudo chown -R odoo:odoo /opt/odoo/custom-addons
   ```

2. Redémarrer Odoo :

   ```bash
   sudo systemctl restart odoo
   ```

3. Dans Odoo, mode développeur activé : **Apps → Mettre à jour la liste
   des Apps**, retirer le filtre « Apps », chercher « Suivi des
   activités » → **Activer**.

Le récapitulatif est actif dès l'installation, à 7 h (heure de Douala) :
le régler ou le couper dans les Paramètres du CRM.

## Mise à jour d'une installation existante (19.0.1 → 19.0.2)

Faire d'abord une **sauvegarde** de la base : gestionnaire des bases
(`https://votre-site/web/database/manager` → *Backup*), ou
`sudo -u odoo pg_dump -Fc NOM_DE_LA_BASE -f /tmp/sauvegarde.dump`. La
mise à jour se fait **service arrêté**.

```bash
sudo systemctl stop odoo
```

Retirer l'ancien dossier, puis déposer le nouveau (étape 1 de
l'installation : `unzip`, `chown`) :

```bash
sudo rm -rf /opt/odoo/custom-addons/aite_crm_activity
```

```bash
sudo unzip -o /tmp/aite_crm_activity.zip -d /opt/odoo/custom-addons/
```

```bash
sudo chown -R odoo:odoo /opt/odoo/custom-addons
```

Mettre le module à niveau, puis redémarrer :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d NOM_DE_LA_BASE -u aite_crm_activity --stop-after-init
```

```bash
sudo systemctl start odoo
```

(`odoo` est la commande des installations `.deb` ; depuis les sources :
`python3 odoo-bin` dans le dossier d'Odoo.) Les réglages du récapitulatif
(heure, fuseau, fenêtre « à venir », désabonnements) et l'heure de
l'action planifiée sont conservés ; les nouveaux seuils prennent leurs
valeurs par défaut (7 jours à venir, retard élevé à 3 jours, critique à
7 jours, opportunité dormante à 14 jours), modifiables dans les
Paramètres du CRM. Recharger ensuite la page dans le navigateur
(Ctrl+Maj+R) pour obtenir le nouveau tableau de bord.

## Tests automatisés

146 tests : indicateurs, droits par profil, filtres, actions, période et
comparaison, opportunités perdues, gravité des retards et montants en
jeu, plan de charge, tendances, aperçu d'une opportunité, rapport
d'analyse (nombres, droits, export), contenu et destinataires du
récapitulatif, fuseaux horaires, échec d'envoi, réglages, et trois
parcours dans un navigateur (tableau de bord complet, lien « activités
en retard », aperçu plein écran sur tablette). À lancer sur un **serveur de test** (mêmes précautions que
pour le module WhatsApp, voir son README) ; les résultats ne dépendent ni
des données déjà présentes (démonstration comprise) ni des Paramètres
déjà enregistrés.

Les parcours dans le navigateur demandent Chromium et le module Python
`websocket-client` :

```bash
sudo apt install chromium python3-websocket
```

Puis :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d aite_cad_test -i aite_crm_activity --test-tags aite_crm_activity --workers 0 --max-cron-threads 0 --db-filter '^aite_cad_test$' --http-port 8079 --stop-after-init
```

Résultat attendu : `0 failed, 0 error(s) of 146 tests`. Ce total compte
aussi les tests **ignorés** : si le log contient « skipped » pour
`test_dashboard_tour`, `test_overdue_link_tour` ou `test_panel_modal_tour`,
ou « Chrome executable not found » ou « websocket-client module is not
installed », les parcours dans le navigateur n'ont pas tourné. Le parcours
de l'aperçu provoque exprès une action refusée : l'avertissement « Cette
activité n'existe plus » dans le log est attendu.

Supprimer ensuite la base de test et ses fichiers :

```bash
sudo -u odoo dropdb aite_cad_test
```

```bash
sudo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/aite_cad_test
```

## Note technique — dates et fuseaux horaires

- « Aujourd'hui », les périodes et les reports rapides du tableau de bord
  suivent le fuseau horaire de l'utilisateur (ses préférences Odoo), pas
  l'horloge du navigateur.
- Le récapitulatif calcule « aujourd'hui » dans le fuseau de chaque
  destinataire ; l'heure d'envoi suit le fuseau choisi dans les Paramètres.
- La date « réalisée » d'une activité est enregistrée par Odoo en date
  UTC : une activité marquée faite entre minuit et 1 h à Douala compte pour
  la veille.
- Le rapport d'analyse calcule le retard dans le fuseau de la personne
  assignée.

## Contenu technique

| Fichier | Rôle |
|---|---|
| `models/crm_activity_params.py` | Réglages partagés (fenêtres, seuils, gravité du retard) et règle des opportunités perdues |
| `models/crm_activity_dashboard.py` | Données (`get_dashboard_data`, `get_trend_data`, `get_lead_preview`) et actions (`action_mark_done`, `action_reschedule`, `action_reassign`) du tableau de bord, avec les droits de l'utilisateur |
| `models/crm_activity_report.py`, `report/` | Rapport d'analyse (vue SQL) et ses vues |
| `security/` | Droits et règles d'accès du rapport (mêmes règles que le CRM) |
| `models/crm_activity_digest.py` | Récapitulatif : destinataires, contenu par utilisateur (droits, fuseau, langue), envoi par la tâche planifiée |
| `models/res_config_settings.py` | Réglages : récapitulatif (activation, heure, fuseau), fenêtres et seuils du tableau de bord |
| `models/ir_cron.py` | Garde l'heure d'envoi locale d'un jour à l'autre, changements d'heure compris |
| `models/res_users.py` | Préférence « Récapitulatif CRM du matin », modifiable par chacun |
| `static/src/dashboard/` | Le tableau de bord (OWL), ses onglets, le graphique et le panneau d'aperçu |
| `views/dashboard_views.xml` | Actions (dont le lien direct « activités en retard ») et menu |
| `views/digest_templates.xml` | L'e-mail du récapitulatif |
| `data/ir_cron_data.xml` | Tâche planifiée quotidienne |
| `tests/` | Tests automatisés (étiquette `aite_crm_activity`) et parcours navigateur |

Reconstruire le zip, depuis la racine du dépôt :

```bash
cd addons && rm -f ../dist/aite_crm_activity.zip && zip -r ../dist/aite_crm_activity.zip aite_crm_activity -x '*/__pycache__/*'
```

---
© AITE Consulting SARL — LGPL-3.
