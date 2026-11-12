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
| Actions directes | **Fait** (avec un compte rendu facultatif, publié dans l'historique de l'opportunité), **Reporter** (à demain, lundi prochain, dans une semaine ou à une date), **Réassigner** (responsables), clic sur l'opportunité pour l'ouvrir. |
| Par commercial | Pour chaque commercial : retards, activités du jour, à venir, réalisées, opportunités sans activité. Un clic filtre le tableau sur lui. |
| Opportunités sans activité planifiée | Les opportunités ouvertes (ni gagnées ni perdues) qui n'ont aucune prochaine étape, avec le bouton **Planifier**. |
| Filtres | Commercial, équipe commerciale, type d'activité. |

**Qui voit quoi.** Les droits d'Odoo s'appliquent : un commercial
« Mes documents uniquement » voit ses propres activités (et celles qu'on
lui a assignées) ; un responsable voit toute l'équipe et peut réassigner.
À l'ouverture, un commercial voit ses activités, un responsable celles de
tout le monde.

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
sa langue pour les dates.

**Réglages** : CRM → Configuration → Paramètres → bloc **Suivi des
activités** :

| Réglage | Par défaut | Rôle |
|---|---|---|
| Récapitulatif du matin | Activé | Active ou coupe l'envoi pour tout le monde |
| Heure d'envoi | 7:00 | Heure locale (fuseau de la personne qui fait le réglage) |
| Activités à venir (jours) | 3 | Jours à venir inclus en plus des retards et du jour ; 0 = seulement retards et jour |

Le bouton **M'envoyer mon récapitulatif maintenant** permet de voir
l'e-mail tout de suite.

**Se désabonner** : chaque utilisateur, depuis son avatar → **Mes
préférences** → case « Récapitulatif CRM du matin ».

**Prérequis : un serveur d'envoi d'e-mails.** Sur une installation
hébergée (VPS), Odoo n'envoie des e-mails que si un serveur de courrier
sortant est configuré : Paramètres → Technique → Serveurs de courrier
sortant (mode développeur). Les récapitulatifs sont mis en file d'attente
puis envoyés par la tâche planifiée « Mail : gestionnaire de file
d'attente des e-mails », en général dans les minutes qui suivent.

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

## Tests automatisés

32 tests : indicateurs, droits par profil, filtres, actions, contenu et
destinataires du récapitulatif, fuseau horaire, réglages, et un parcours
complet dans un navigateur. À lancer sur un **serveur de test** (mêmes
précautions que pour le module WhatsApp, voir son README) :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d aite_cad_test -i aite_crm_activity --test-tags aite_crm_activity --workers 0 --max-cron-threads 0 --db-filter '^aite_cad_test$' --http-port 8079 --stop-after-init
```

Résultat attendu : `0 failed, 0 error(s) of 32 tests`. Le parcours dans le
navigateur demande Chrome ou Chromium sur le serveur de test ; sans lui,
ce test est ignoré. Supprimer ensuite la base de test (`dropdb
aite_cad_test`).

## Contenu technique

| Fichier | Rôle |
|---|---|
| `models/crm_activity_dashboard.py` | Données (`get_dashboard_data`) et actions (`action_mark_done`, `action_reschedule`, `action_reassign`) du tableau de bord, avec les droits de l'utilisateur |
| `models/crm_activity_digest.py` | Récapitulatif : destinataires, contenu par utilisateur (droits, fuseau, langue), envoi par la tâche planifiée |
| `models/res_config_settings.py` | Réglages : activation et heure (tâche planifiée), fenêtre des activités à venir |
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
