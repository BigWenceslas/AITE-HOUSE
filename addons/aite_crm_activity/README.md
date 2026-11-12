# AITE — Suivi des activités CRM

**Odoo 19 (Enterprise & Community) · module `aite_crm_activity` · version 19.0.1.0.0**

Deux outils pour que plus aucune opportunité ne reste sans suite :

1. un **tableau de bord** qui suit et gère les tâches et activités
   (appels, e-mails, rendez-vous, à faire…) planifiées sur les
   opportunités ;
2. un **récapitulatif envoyé chaque matin** par e-mail à chaque
   utilisateur, avec la liste de ses activités en cours.

## Le tableau de bord

**CRM → Suivi des activités**

| Zone | Contenu |
|---|---|
| Indicateurs | Activités **en retard**, **du jour**, **à venir** (7 jours), **réalisées** (7 derniers jours), **opportunités sans activité** planifiée. Un clic filtre la liste. |
| Activités | La liste à traiter, triée par échéance, avec l'opportunité, le client, l'étape, le montant et la personne assignée. Onglets : En cours, En retard, Aujourd'hui, À venir, Réalisées. |
| Actions directes | **Fait** (avec un compte rendu facultatif, publié dans l'historique de l'opportunité), **Reporter** (menu : à demain, lundi prochain, dans une semaine ou à une date), **Réassigner** (choix de la personne puis confirmation ; elle est prévenue par Odoo), clic sur l'opportunité pour l'ouvrir. |
| Par commercial | Pour chaque commercial : retards, activités du jour, à venir, réalisées, opportunités sans activité. Un clic filtre le tableau sur lui, un second clic retire le filtre. La ligne « Non assigné » regroupe ce qui n'est assigné à personne. |
| Opportunités sans activité planifiée | Les opportunités ouvertes (ni gagnées ni perdues) qui n'ont plus aucune activité à faire, y compris celles dont la dernière activité vient d'être marquée comme faite, avec le bouton **Planifier**. |
| Filtres | Commercial (ou « Non assigné »), équipe commerciale, type d'activité. Ils sont conservés quand on revient d'une opportunité par le fil d'Ariane. |

**Qui voit quoi.** Les droits d'Odoo s'appliquent (Paramètres →
Utilisateurs → droits « Ventes ») :

- **Utilisateur : mes documents seulement** : le tableau s'ouvre sur ses
  propres activités ; il voit aussi celles qu'on lui a assignées sur
  l'opportunité d'un collègue (sans le détail de l'opportunité). Il ne
  peut pas réassigner.
- **Utilisateur : tous les documents** et **Administrateur** : le tableau
  s'ouvre sur les activités de tout le monde, et ils peuvent réassigner.

Le tableau de bord est réservé aux utilisateurs du CRM.

## Le récapitulatif du matin

Chaque jour, à l'heure choisie, chaque utilisateur qui a des activités en
cours sur des opportunités reçoit un e-mail :

- ses activités **en retard** (avec le nombre de jours de retard), **du
  jour** et **à venir** sur les prochains jours ;
- pour chacune : l'échéance, le type, le résumé, l'opportunité (lien
  direct), le client, l'étape et le montant ;
- un bouton vers son tableau de bord.

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

Pour une **mise à jour** du module, procéder comme pour le module WhatsApp
(service arrêté, puis `-u aite_crm_activity`).

## Tests automatisés

47 tests : indicateurs, droits par profil, filtres, actions, contenu et
destinataires du récapitulatif, fuseaux horaires, échec d'envoi,
réglages, et un parcours complet dans un navigateur. À lancer sur un
**serveur de test** (mêmes précautions que pour le module WhatsApp, voir
son README).

Le parcours dans le navigateur demande Chromium et le module Python
`websocket-client` :

```bash
sudo apt install chromium python3-websocket
```

Puis :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d aite_cad_test -i aite_crm_activity --test-tags aite_crm_activity --workers 0 --max-cron-threads 0 --db-filter '^aite_cad_test$' --http-port 8079 --stop-after-init
```

Résultat attendu : `0 failed, 0 error(s) of 47 tests`. Ce total compte
aussi un test **ignoré** : si le log contient « skipped » pour
`test_dashboard_tour`, ou « Chrome executable not found » ou
« websocket-client module is not installed », le parcours dans le
navigateur n'a pas tourné.

Supprimer ensuite la base de test et ses fichiers :

```bash
sudo -u odoo dropdb aite_cad_test
```

```bash
sudo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/aite_cad_test
```

## Contenu technique

| Fichier | Rôle |
|---|---|
| `models/crm_activity_dashboard.py` | Données (`get_dashboard_data`) et actions (`action_mark_done`, `action_reschedule`, `action_reassign`) du tableau de bord, avec les droits de l'utilisateur |
| `models/crm_activity_digest.py` | Récapitulatif : destinataires, contenu par utilisateur (droits, fuseau, langue), envoi par la tâche planifiée |
| `models/res_config_settings.py` | Réglages : activation, heure et fuseau horaire (tâche planifiée), fenêtre des activités à venir |
| `models/ir_cron.py` | Garde l'heure d'envoi locale d'un jour à l'autre, changements d'heure compris |
| `models/res_users.py` | Préférence « Récapitulatif CRM du matin », modifiable par chacun |
| `static/src/dashboard/` | Le tableau de bord (OWL) |
| `views/digest_templates.xml` | L'e-mail du récapitulatif |
| `data/ir_cron_data.xml` | Tâche planifiée quotidienne |
| `tests/` | Tests automatisés (étiquette `aite_crm_activity`) et parcours navigateur |

Reconstruire le zip, depuis la racine du dépôt :

```bash
cd addons && rm -f ../dist/aite_crm_activity.zip && zip -r ../dist/aite_crm_activity.zip aite_crm_activity -x '*/__pycache__/*'
```

---
© AITE Consulting SARL — LGPL-3.
