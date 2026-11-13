# AITE — Chat du site web

**Odoo 19 (Enterprise & Community) · module `aite_website_livechat` · version 19.0.1.0.0**

Une bulle de chat sur **toutes les pages du site**, toujours affichée, même
quand personne n'est connecté à Odoo. Le visiteur écrit ; vous recevez son
message dans **Discuss** et en **notification push** sur votre navigateur et
sur votre téléphone (application mobile Odoo). Vous répondez quand vous
pouvez : s'il est encore sur le site, il voit la réponse en direct, sinon il
la reçoit par e-mail.

Le module s'appuie sur le **chat en direct d'Odoo** (Live Chat, modules
`im_livechat` et `website_livechat`) : pas de nouvelle fenêtre de chat, les
conversations, statistiques et réglages habituels du Live Chat restent les
mêmes.

## Ce que fait le module

- **Toujours joignable.** Sans ce module, Odoo cache la bulle dès qu'aucun
  opérateur n'est « en ligne » (Odoo ouvert dans un navigateur). Avec
  « Toujours joignable », la bulle reste affichée et la conversation est
  confiée à un opérateur du canal, connecté ou non, choisi comme le fait
  Odoo : l'opérateur qui a déjà parlé à ce visiteur, puis la langue, puis
  le moins occupé. Quand un opérateur est en ligne, rien ne change : c'est
  lui qui est choisi.
- **Les messages arrivent chez l'opérateur** comme toute conversation du
  Live Chat : dans Discuss (rubrique du canal, « Chat du site »), avec une
  notification push à chaque message du visiteur (voir plus bas).
- **Message d'absence.** Au premier message du visiteur, si l'opérateur
  n'est pas en ligne, une réponse automatique part aussitôt : « Merci pour
  votre message ! Nous ne sommes pas en ligne pour le moment : nous vous
  répondons ici dès que possible. Pour être sûr de recevoir notre réponse,
  indiquez-nous votre adresse e-mail ou votre numéro de téléphone. »
  - une seule fois par conversation, jamais quand l'opérateur est en ligne ;
  - si le visiteur a déjà donné son e-mail ou son téléphone (dans ce premier
    message, ou par son compte), la dernière phrase n'est pas envoyée ;
  - signée de l'opérateur, comme le message d'accueil ;
  - elle ne déclenche aucune notification et ne compte pas comme une
    réponse : ni dans les statistiques et rapports du Live Chat (délai de
    première réponse, nombre de messages), ni comme un message non lu de
    l'opérateur ; dans sa liste de messages, la conversation montre la
    question du visiteur.
- **Coordonnées du visiteur.** L'adresse e-mail et le numéro de téléphone
  que le visiteur écrit dans le chat sont repérés et affichés à l'opérateur
  dans Discuss, panneau **Informations** (icône ℹ) de la conversation,
  rubrique « Contact du visiteur ». À défaut, l'e-mail de son compte s'il
  est connecté. Le visiteur, lui, ne peut pas lire ces champs. Pour
  l'e-mail :
  - la **première** adresse que le visiteur donne est retenue ; une adresse
    citée ensuite au fil d'une phrase (« mon comptable, compta@…, attend
    aussi le devis ») ne la remplace pas ;
  - un message court qui ne contient guère que la nouvelle adresse
    (« Pardon, plutôt jean@exemple.cm » : cinq mots au plus en dehors de
    l'adresse) corrige une faute de frappe ;
  - les adresses de l'entreprise (société, utilisateurs internes, domaine
    des alias e-mail et des sites) ne sont jamais retenues ;
  - seuls les 10 000 premiers caractères d'un message sont examinés.
- **Réponse par e-mail.** Si l'opérateur répond alors que le visiteur a
  quitté le site (ou fermé la fenêtre du chat), la réponse lui est aussi
  envoyée par e-mail. Le visiteur peut répondre à cet e-mail (il arrive à
  l'adresse de la société) ou revenir écrire dans le chat du site. Règles :
  - uniquement vers l'adresse que le visiteur a écrite lui-même (voir
    ci-dessus) ou celle de son compte ;
  - uniquement le texte écrit par les opérateurs dans **cette**
    conversation (ni le visiteur, ni le message d'absence, ni le chatbot),
    sans mise en forme ;
  - **au plus un e-mail toutes les 10 minutes** par conversation : le
    premier part 2 minutes après la réponse, et tout ce que l'opérateur
    écrit d'ici là y est ajouté ; les réponses suivantes sont regroupées
    dans l'e-mail suivant, 10 minutes après le précédent ;
  - si le visiteur revient écrire avant l'envoi, l'e-mail est annulé (il a
    vu la réponse dans le chat).
- **Une question n'est jamais close sans réponse.** Odoo termine une
  conversation quand le visiteur ferme la fenêtre du chat, et son nettoyage
  quotidien termine toute conversation restée un jour sans activité ;
  l'opérateur ne peut alors plus y écrire. Pour un canal « Toujours
  joignable » :
  - si le visiteur ferme le chat avant toute réponse, la conversation reste
    ouverte pour l'opérateur, avec l'avis « Le visiteur a quitté la
    conversation. Il a fermé le chat avant votre réponse : elle lui sera
    envoyée par e-mail » (ou « … sans laisser d'adresse e-mail : il ne la
    verra pas ») ; la réponse part par e-mail ;
  - le nettoyage quotidien laisse ouvertes, jusqu'à 7 jours après leur
    dernier message, les conversations qui attendent la réponse d'un
    opérateur et celles dont la réponse n'a pas encore été vue par le
    visiteur (il peut revenir la lire sur le site, dans le même
    navigateur) ;
  - les autres conversations suivent la règle d'Odoo.
- **Installation.** Si le site n'a pas encore de chat, le module crée le
  canal **« Chat du site »** (texte de la bulle « Une question ? Écrivez-nous »,
  affiché à côté d'elle seulement si la règle du canal est « Afficher avec
  notification » ; message d'accueil « Bonjour 👋 Comment pouvons-nous vous aider ? », opérateur :
  l'administrateur — s'il est archivé, le premier responsable du Live Chat
  ou, à défaut, le premier administrateur actif —, affiché sur toutes les
  pages, toujours joignable,
  réponse par e-mail activée) et le rattache au site. Un canal existant
  n'est jamais modifié : ses cases « Toujours joignable » et « Réponse par
  e-mail » restent décochées, à cocher dans les Paramètres. Seule
  exception : le canal de démonstration « YourWebsite.com » qu'Odoo crée
  sans opérateur et qui n'a jamais servi est laissé tel quel, mais le site
  passe sur « Chat du site ».
- **Avec le bouton WhatsApp** (module `aite_website_whatsapp`) : quand les
  deux sont à droite, le bouton WhatsApp se place juste au-dessus de la
  bulle du chat, centré sur elle, sur ordinateur, téléphone et tablette. La
  hauteur des bulles est mesurée dans la page : le bouton WhatsApp remonte
  au-dessus des conversations réduites, de la marge plus grande des
  téléphones et du décalage en fin de page. Les deux modules restent
  indépendants.

## Recevoir les messages : Discuss, navigateur, téléphone

Chaque message d'un visiteur arrive chez l'opérateur de la conversation :

1. **Discuss** (Odoo dans le navigateur) : la conversation apparaît dans la
   rubrique du canal (« Chat du site »), avec un compteur de messages non
   lus. Rien à régler.
2. **Notification push du navigateur** (Chrome, Edge, Firefox, Safari, sur
   ordinateur ou Android) : même Odoo fermé, tant que le navigateur tourne.
   - le site doit être en **HTTPS** (obligatoire pour les notifications
     push) ;
   - ouvrir Odoo, cliquer sur l'icône des messages (bulle en haut à droite)
     → **Activer les notifications**, puis accepter la demande du
     navigateur ; à refaire sur chaque navigateur et chaque appareil.
3. **Application mobile Odoo** (Android et iOS), **Enterprise seulement** :
   - installer l'application « Odoo » (Play Store / App Store), se
     connecter avec l'adresse du site (`https://…`) et accepter les
     notifications ;
   - les notifications passent par le service de notifications d'Odoo
     S.A. : la base doit être **enregistrée avec un abonnement Enterprise
     valide** (Paramètres → tout en bas : numéro d'abonnement), et le
     serveur doit pouvoir joindre Internet ;
   - si les notifications n'arrivent pas, chercher « push » dans la barre
     de recherche de **Paramètres → Paramètres généraux** et vérifier que
     les notifications mobiles sont activées.

Le module n'a pas de code de notification propre : il fait de l'opérateur
un membre de la conversation, et Odoo envoie lui-même les notifications à
chaque membre sauf l'auteur du message (voie testée par les tests
automatisés). La notification de l'application mobile n'a pas pu être
essayée pendant le développement (version Community, pas de téléphone) :
elle suit cette même voie standard d'Odoo Enterprise.

**« Ne pas déranger »** : un opérateur qui choisit ce statut (menu de son
avatar) ne reçoit **aucune** notification push, ni navigateur ni mobile —
c'est la règle d'Odoo. Il voit toujours les conversations dans Discuss. Le
statut « Absent » n'empêche pas les notifications. Pour le message
d'absence, un opérateur en « Ne pas déranger » ou « Absent » compte comme
pas en ligne.

## Le serveur (VPS) : messages en temps réel

Le chat en temps réel passe par une connexion permanente (« websocket »,
adresse `/websocket`). Sans elle, les messages arrivent quand même, mais
seulement au rechargement de la page : le visiteur ne voit pas la réponse
s'afficher, l'opérateur ne voit pas les nouveaux messages tant qu'il ne
recharge pas Discuss. Les notifications push, elles, partent quand même, et
le message d'absence s'affiche aussitôt chez le visiteur.

Le site en HTTPS (obligatoire pour les notifications push) passe par un
proxy, en général **nginx**. Or nginx ne transmet pas une connexion
websocket sans réglage : Odoo la refuse (erreur **400**) et le chat n'est
plus en temps réel. Le bloc `location /websocket` ci-dessous est donc
nécessaire **dans tous les cas**. Seul le port vers lequel il envoie
change :

- **Odoo lancé avec `workers = 0`** (un seul processus : réglage par défaut
  du paquet `.deb`, quand `/etc/odoo/odoo.conf` n'a pas de ligne
  `workers`) : le websocket passe par le port habituel, **8069** ;
- **Odoo lancé avec `workers` supérieur à 0** (cas habituel en
  production) : le websocket est servi par un port à part, **8072**
  (`gevent_port`).

Pour savoir lequel s'applique :

```bash
sudo grep -E '^\s*workers' /etc/odoo/odoo.conf
```

(rien ou `workers = 0` : port 8069 ; un nombre supérieur à 0 : port 8072.)

1. Dans `/etc/odoo/odoo.conf`, section `[options]` (`sudo nano
   /etc/odoo/odoo.conf`), vérifier ou ajouter :

   ```
   proxy_mode = True
   ```

   et, seulement avec `workers` supérieur à 0 :

   ```
   gevent_port = 8072
   ```

2. Dans le fichier du site nginx (souvent `/etc/nginx/sites-available/odoo`
   ou `/etc/nginx/conf.d/odoo.conf`), en **haut du fichier**, hors des blocs
   `server`, ajouter s'ils n'y sont pas déjà :

   ```nginx
   upstream odoo {
       server 127.0.0.1:8069;
   }
   upstream odoochat {
       server 127.0.0.1:8072;
   }
   map $http_upgrade $connection_upgrade {
       default upgrade;
       ''      close;
   }
   ```

   Avec `workers = 0`, remplacer `8072` par **`8069`** dans le bloc
   `upstream odoochat` (le websocket passe alors par le port habituel).

   puis, **dans** le bloc `server { … }` du site en HTTPS, **avant** le bloc
   `location / { … }` :

   ```nginx
   location /websocket {
       proxy_pass http://odoochat;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection $connection_upgrade;
       proxy_set_header X-Forwarded-Host $http_host;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_read_timeout 720s;
   }
   ```

   Si votre `location /` envoie déjà vers `http://127.0.0.1:8069`, le
   laisser tel quel.

3. Vérifier et recharger :

   ```bash
   sudo nginx -t
   ```

   ```bash
   sudo systemctl reload nginx
   ```

   ```bash
   sudo systemctl restart odoo
   ```

4. **Tester.** Le plus simple, dans le navigateur : ouvrir le site, touche
   F12 → onglet **Réseau** → filtre **WS** → recharger la page : la ligne
   `websocket` doit afficher le statut **101**. Ou, depuis n'importe quel
   ordinateur (remplacer l'adresse) :

   ```bash
   curl -s -o /dev/null --max-time 5 -w "%{http_code}\n" --http1.1 -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Origin: https://votre-site.cm" https://votre-site.cm/websocket
   ```

   La commande rend la main au bout de 5 secondes. La réponse attendue est
   **101** (connexion acceptée). Un **400** ou **404** : la requête arrive
   à Odoo sans les en-têtes du websocket (revoir le bloc `location
   /websocket` et `proxy_http_version 1.1`) ; un **502** : rien n'écoute
   sur le port du bloc `upstream odoochat` (8072 avec `workers` supérieur
   à 0, 8069 sinon ; vérifier `workers` et `gevent_port`, puis le journal
   d'Odoo).

**Les e-mails** (réponse par e-mail) partent par le serveur d'e-mails
sortants d'Odoo (Paramètres → Paramètres généraux → **Utiliser les
serveurs de messagerie personnalisés** → Serveurs de messagerie sortants)
et par les tâches planifiées, actives par défaut
(`max_cron_threads` ne doit pas valoir 0). L'adresse d'expéditeur est
l'e-mail de la société du site (Paramètres → Sociétés) : à renseigner.

## Installation sur le VPS

Les commandes se lancent **sur le VPS**, en SSH, avec un compte qui a
`sudo`. Elles supposent une installation par le paquet officiel `.deb`
(fichier `/etc/odoo/odoo.conf`, service et utilisateur `odoo`) ; les
adapter si votre installation diffère. Si le module `aite_website_whatsapp`
est déjà installé, le dossier des modules est le même : passer directement
à l'étape 2.

**1. Repérer le service, sa configuration et le dossier des modules**

```bash
systemctl list-units --type=service | grep -i odoo
```

```bash
sudo grep -E '^\s*addons_path' /etc/odoo/odoo.conf
```

La première commande donne le nom du service (souvent `odoo`). Si le
fichier `/etc/odoo/odoo.conf` n'existe pas, son chemin figure après `-c`
ou `--config` dans `systemctl cat odoo`.

- **La ligne `addons_path` s'affiche** et contient un dossier pour vos
  propres modules (ni celui d'Odoo ni celui d'Enterprise, par exemple
  `/opt/odoo/custom-addons`) : c'est là que va le module.
- **La ligne s'affiche mais ne contient que le dossier d'Odoo** : faire
  l'étape 2 avec `/opt/odoo/custom-addons`, puis ajouter
  `,/opt/odoo/custom-addons` **à la fin de cette même ligne**
  (`sudo nano /etc/odoo/odoo.conf`).
- **Rien ne s'affiche** — cas normal d'une installation `.deb` : faire
  l'étape 2 avec `/opt/odoo/custom-addons`, puis ajouter dans
  `/etc/odoo/odoo.conf`, sous `[options]`, la ligne :

  ```
  addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
  ```

  Le premier chemin est celui des modules d'Odoo (et d'Enterprise) dans le
  paquet `.deb` ; il doit rester en tête.

Le fichier ne doit contenir qu'**une seule** ligne `addons_path` active.

**2. Déposer le module**

Depuis votre ordinateur, envoyer le zip sur le VPS :

```bash
scp aite_website_livechat.zip utilisateur@adresse-du-vps:/tmp/
```

Puis, sur le VPS (remplacer `/opt/odoo/custom-addons` par le dossier de
l'étape 1) :

```bash
sudo mkdir -p /opt/odoo/custom-addons
```

```bash
sudo unzip -o /tmp/aite_website_livechat.zip -d /opt/odoo/custom-addons/
```

```bash
sudo chown -R odoo:odoo /opt/odoo/custom-addons
```

Le zip doit être **décompressé** : on doit obtenir
`/opt/odoo/custom-addons/aite_website_livechat/__manifest__.py`.

**3. Redémarrer Odoo**

```bash
sudo systemctl restart odoo
```

**4. Installer le module** dans Odoo : Paramètres → tout en bas →
**Activer le mode développeur**, puis **Apps → Mettre à jour la liste des
Apps**, retirer le filtre « Apps » de la recherche, chercher « Chat du
site » → **Activer**. Les modules Live Chat et **Live Chat sur le site
web** s'installent avec lui s'ils ne l'étaient pas.

**5. Vérifier** : ouvrir le site dans une fenêtre de navigation privée
(sans être connecté) : la bulle du chat doit apparaître en bas à droite,
même si personne n'est connecté à Odoo. Écrire un message : le message
d'absence s'affiche, et la conversation arrive dans Discuss de
l'administrateur. Si la bulle n'apparaît pas, le canal n'a pas
d'opérateur : c'est le cas quand l'utilisateur « Administrator » d'origine
est archivé et qu'aucun autre responsable du Live Chat ou administrateur
actif n'a été trouvé (le journal d'Odoo l'indique). Ajouter un opérateur
(voir **Réglage** ci-dessous : Opérateurs du chat → onglet Agents).

## Réglage

**Site Web → Configuration → Paramètres → bloc « Général » → « Live
Chat »**, sous le choix du canal (réservé aux responsables du Live Chat) :

| Réglage | Par défaut | Rôle |
|---|---|---|
| Toujours joignable | ☑ | La bulle reste affichée quand aucun opérateur n'est en ligne |
| Message d'absence | (texte ci-dessus) | Réponse automatique au premier message, si l'opérateur n'est pas en ligne. Vide : pas de message d'absence |
| Réponse par e-mail | ☑ | Les réponses envoyées au visiteur parti, s'il a donné son adresse |
| Opérateurs du chat | — | Ouvre le canal : **Agents** (qui reçoit les conversations), textes de la bulle, couleurs, règles d'affichage |

**Ajouter un opérateur** : bouton **Opérateurs du chat** → onglet
**Agents** → **Ajouter une ligne**. Seuls les utilisateurs qui ont un droit
« Live Chat » (Paramètres → Utilisateurs → l'utilisateur → Live Chat :
Utilisateur ou Administrateur) peuvent être choisis. Avec plusieurs
opérateurs hors ligne, chaque nouvelle conversation va au moins occupé.

Les mêmes réglages existent pour chaque canal dans **Live Chat → Canaux →
le canal → onglet Options → « Quand personne n'est en ligne »** (sites
multiples, chat intégré à un autre site).

**Le modèle de l'e-mail** (sujet, texte) se modifie dans Paramètres →
Technique → E-mail → **Modèles d'e-mail** → « Chat du site : réponse au
visiteur par e-mail » (mode développeur).

## Bon à savoir

- **Message d'absence en plusieurs langues** : il est traduisible, comme
  les textes de la bulle. Il s'enregistre dans la langue de l'utilisateur
  qui fait le réglage ; pour saisir la version anglaise, passer ses
  préférences en anglais puis revenir sur l'écran Paramètres. Le visiteur
  le reçoit dans la langue du site qu'il consulte.
- **Chatbot** : si une règle du canal lance un chatbot qui « transfère à
  un opérateur », le transfert se fait aussi quand personne n'est en ligne,
  et le message d'absence part au moment du transfert.
- **Repérage du téléphone** : indicatif. Une suite de 8 à 15 chiffres (un
  numéro de commande, par exemple) peut être prise pour un numéro ; elle
  n'est qu'affichée à l'opérateur, jamais utilisée.
- **Conversation reprise sur le site** : dans le même navigateur, tant que
  le visiteur n'a pas fermé la fenêtre du chat (croix) et que la
  conversation est ouverte (voir plus haut : jusqu'à 7 jours tant que la
  réponse n'a pas été vue). Sinon, ou depuis un autre appareil, il ouvre
  une nouvelle conversation, confiée au même opérateur s'il revient dans
  la semaine depuis le même navigateur.
- **Adresse des réponses par e-mail** : celle affichée dans « Contact du
  visiteur » ; elle ne se modifie pas à la main. En cas de doute (adresse
  qui semble être celle d'un tiers), répondre plutôt par un e-mail écrit
  soi-même.
- **La bulle est déplaçable** par le visiteur (glisser-déposer) : déplacée
  ailleurs, elle peut alors passer sur d'autres éléments de la page, comme
  avec le chat d'Odoo sans ce module.

## Mise à jour d'une installation existante

Faire d'abord une **sauvegarde** de la base : gestionnaire des bases
(`https://votre-site/web/database/manager` → *Backup*), ou
`sudo -u odoo pg_dump -Fc NOM_DE_LA_BASE -f /tmp/sauvegarde.dump`. La mise
à jour se fait **service arrêté** :

```bash
sudo systemctl stop odoo
```

```bash
sudo rm -rf /opt/odoo/custom-addons/aite_website_livechat
```

Déposer le nouveau dossier, comme à l'étape 2 de l'installation (`scp`,
`unzip`, `chown`), puis mettre le module à niveau :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d NOM_DE_LA_BASE -u aite_website_livechat --stop-after-init
```

```bash
sudo systemctl start odoo
```

(`odoo` est la commande des installations `.deb` ; depuis les sources :
`python3 odoo-bin` dans le dossier d'Odoo.) Les réglages et le modèle
d'e-mail déjà personnalisés sont conservés.

## Tests automatisés

63 tests : disponibilité et choix de l'opérateur, chatbot, notification de
l'opérateur, message d'absence (statistiques, rapports, messages non lus),
repérage des coordonnées (adresses de tiers ou de l'entreprise, message
démesuré), réponse par e-mail (cadence, contenu, adresse), conversation
gardée ouverte (visiteur qui ferme le chat, nettoyage quotidien),
installation et réinstallation, écran Paramètres, droits d'accès, et sept
parcours dans un vrai navigateur (visiteur public, avec et sans connexion
en temps réel ; liste des messages de l'opératrice ; bulle et bouton
WhatsApp sur ordinateur, sur petit écran et sur téléphone Android, avec
une conversation réduite, si le module WhatsApp est présent). Ils créent
une base de test, avec l'identifiant `admin` / mot de passe `admin`.

**À lancer de préférence sur un serveur de test, pas sur le VPS de
production** (une base de plus peut dérégler un serveur sans filtre de
base). Si vous devez les lancer sur ce VPS : vérifier d'abord que
`/etc/odoo/odoo.conf` contient `db_name = NOM_DE_LA_BASE`, puis supprimer
la base de test juste après.

Lancement, sur une base qui **n'existe pas encore** :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d aite_lc_test -i aite_website_livechat,aite_website_whatsapp --test-tags aite_website_livechat --workers 0 --max-cron-threads 0 --db-filter '^aite_lc_test$' --http-port 8079 --stop-after-init
```

(Sans le module WhatsApp sur le serveur, retirer `,aite_website_whatsapp` :
les quatre tests de chevauchement sont alors ignorés.) Résultat attendu en
fin de journal : `0 failed, 0 error(s) of 63 tests`. Les parcours dans le
navigateur demandent Chrome ou Chromium sur le serveur.

Supprimer ensuite la base de test :

```bash
sudo -u odoo dropdb aite_lc_test
```

```bash
sudo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/aite_lc_test
```

## Désinstallation

Apps → retirer le filtre « Apps » → chercher « Chat du site » → ⋮ →
**Désinstaller**. Le site continue de fonctionner : le canal « Chat du
site » et les conversations restent, mais le chat redevient celui d'Odoo
(bulle affichée seulement quand un opérateur est en ligne, ni message
d'absence ni réponse par e-mail). Le bouton WhatsApp reprend sa place.

**Réinstallation** : les réglages propres au module sont effacés à la
désinstallation. En réinstallant, le canal « Chat du site » que le module
avait créé retrouve « Toujours joignable » et « Réponse par e-mail » ; un
message d'absence personnalisé est remplacé par le texte par défaut (à
ressaisir dans les Paramètres). Les autres canaux restent décochés.

## Contenu technique

| Fichier | Rôle |
|---|---|
| `models/im_livechat_channel.py` | Réglages du canal (`aite_*`), disponibilité « toujours joignable », choix d'un opérateur hors ligne (`_get_operator`) |
| `models/discuss_channel.py` | Message d'absence, repérage des coordonnées, réponse par e-mail et sa cadence, conversation gardée ouverte quand le visiteur ferme le chat, données du panneau « Informations » et aperçu de la liste des messages |
| `models/discuss_channel_member.py` | Nettoyage quotidien (conversations en attente gardées 7 jours), messages non lus de l'opérateur |
| `models/im_livechat_report_channel.py` | Rapport des sessions du Live Chat sans le message d'absence |
| `models/website.py` | Création du canal « Chat du site » à l'installation (et à la réinstallation) |
| `models/res_config_settings.py` | Réglages dans l'écran Paramètres du site |
| `controllers/webclient.py` | Affichage de la bulle côté visiteur (`init_livechat`) |
| `data/mail_template_data.xml` | Modèle de l'e-mail au visiteur |
| `views/` | Écran Paramètres et onglet Options du canal |
| `static/src/scss/livechat_button.scss`, `static/src/frontend/` | Bulle du chat et bouton WhatsApp sans chevauchement (hauteur des bulles mesurée dans la page) |
| `static/src/embed/common/` | Fenêtre du chat du visiteur : message d'absence affiché sans attendre le websocket |
| `static/src/core/web/` | « Contact du visiteur » dans le panneau Informations de Discuss ; aperçu de la liste des messages |
| `static/tests/tours/`, `tests/` | Tests automatisés (étiquette `aite_website_livechat`) |

Reconstruire le zip, depuis la racine du dépôt :

```bash
cd addons && rm -f ../dist/aite_website_livechat.zip && zip -qr ../dist/aite_website_livechat.zip aite_website_livechat -x '*/__pycache__/*'
```

---
© AITE Consulting SARL — LGPL-3.
