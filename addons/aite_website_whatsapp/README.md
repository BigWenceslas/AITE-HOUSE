# AITE — Bouton WhatsApp du site web

**Odoo 19 (Enterprise & Community) · module `aite_website_whatsapp` · version 19.0.2.0.0**

Un bouton vert WhatsApp, fixé en bas de l'écran, sur **toutes les pages du
site** : un clic ouvre directement une discussion avec votre numéro —
dans l'application WhatsApp sur mobile, dans WhatsApp Web sur ordinateur —
avec votre message d'accueil déjà saisi.

## Ce que fait le module

- Le bouton est ajouté à la **mise en page commune du site** : il figure
  sur toutes les pages — accueil, pages créées dans l'éditeur, boutique,
  blog, espace client, page de connexion, page 404 — y compris les pages
  créées plus tard. Aucune page à modifier une à une.
- Sur **ordinateur**, un court texte d'accroche (« Une question ?
  Écrivez-nous ») s'affiche à côté de l'icône ; sur **mobile**, seule
  l'icône reste, pour ne pas masquer le contenu.
- Le lien est un simple lien `https://wa.me/…`, sans script : il marche
  dès l'affichage de la page, sur tous les navigateurs.
- Connecté ou non, vous le voyez comme vos visiteurs. Il s'efface pendant
  l'édition d'une page, tant qu'une fenêtre modale est ouverte, et à
  l'impression. La bannière des cookies, les popups et le menu mobile
  passent au-dessus de lui. Il s'adapte aux mises en page du thème
  (pleine largeur, encadrée, carte postale) et à l'en-tête en barre
  latérale.

## Installation sur le VPS

Les commandes se lancent **sur le VPS**, en SSH, avec un compte qui a
`sudo`. Elles supposent une installation par le paquet officiel `.deb`
(fichier `/etc/odoo/odoo.conf`, service et utilisateur `odoo`) ; les
adapter si votre installation diffère — l'étape 1 permet de le vérifier.

**1. Repérer le service, sa configuration et le dossier des modules**

```bash
systemctl list-units --type=service | grep -i odoo
```

```bash
sudo grep -E '^\s*addons_path' /etc/odoo/odoo.conf
```

La première commande donne le nom du service (souvent `odoo`). Si le
fichier `/etc/odoo/odoo.conf` n'existe pas, son chemin figure après `-c`
ou `--config` dans `systemctl cat odoo`, de même que l'utilisateur du
service (ligne `User=`).

- **La ligne `addons_path` s'affiche** et contient un dossier pour vos
  propres modules (ni celui d'Odoo ni celui d'Enterprise, par exemple
  `/opt/odoo/custom-addons`) : c'est là que va le module.
- **La ligne s'affiche mais ne contient que le dossier d'Odoo** (par
  exemple `/usr/lib/python3/dist-packages/odoo/addons`) : faire l'étape 2
  avec `/opt/odoo/custom-addons`, puis ajouter
  `,/opt/odoo/custom-addons` **à la fin de cette même ligne**
  (`sudo nano /etc/odoo/odoo.conf`).
- **Rien ne s'affiche** — cas normal d'une installation `.deb` : il faut
  créer ce dossier. Faire l'étape 2 avec `/opt/odoo/custom-addons`, puis
  ajouter dans `/etc/odoo/odoo.conf`, sous `[options]`
  (`sudo nano /etc/odoo/odoo.conf`), la ligne :

  ```
  addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
  ```

  Le premier chemin est celui des modules d'Odoo (et d'Enterprise) dans le
  paquet `.deb` ; il doit rester en tête.

Le fichier ne doit contenir qu'**une seule** ligne `addons_path` active :
une deuxième empêcherait le service de démarrer.

**2. Déposer le module**

Depuis votre ordinateur, envoyer le zip sur le VPS :

```bash
scp aite_website_whatsapp.zip utilisateur@adresse-du-vps:/tmp/
```

Puis, sur le VPS (remplacer `/opt/odoo/custom-addons` par le dossier de
l'étape 1) :

```bash
sudo mkdir -p /opt/odoo/custom-addons
```

```bash
sudo unzip -o /tmp/aite_website_whatsapp.zip -d /opt/odoo/custom-addons/
```

```bash
sudo chown -R odoo:odoo /opt/odoo/custom-addons
```

Le zip doit être **décompressé** : Odoo ne lit pas les fichiers `.zip`.
On doit obtenir `/opt/odoo/custom-addons/aite_website_whatsapp/__manifest__.py`.

**3. Redémarrer Odoo**

```bash
sudo systemctl restart odoo
```

**4. Installer le module** dans Odoo : Paramètres → tout en bas →
**Activer le mode développeur**, puis **Apps → Mettre à jour la liste des
Apps**, retirer le filtre « Apps » de la recherche, chercher « WhatsApp »
→ **Activer**.

**Facultatif — numéros saisis au format local.** Pour que `699 00 00 00`
soit complété automatiquement en `+237 699 00 00 00`, Odoo s'appuie sur
la bibliothèque Python `phonenumbers` et sur le **pays de la société** du
site (Paramètres → Sociétés → Pays). Sans l'une ou l'autre, le module
fonctionne aussi, mais un numéro local est refusé : il faut le saisir
avec l'indicatif. Pour l'installer : `sudo apt install python3-phonenumbers`
(installation `.deb`), ou `pip install phonenumbers` dans l'environnement
Python d'Odoo (installation depuis les sources), puis redémarrer le
service.

## Réglage

**Site Web → Configuration → Paramètres → bloc « WhatsApp »** (juste sous
le bloc « Général ») :

| Réglage | Exemple | Rôle |
|---|---|---|
| Bouton WhatsApp | ☑ | Affiche ou masque le bouton sur tout le site |
| Numéro | `+237 6 99 00 00 00` | Numéro WhatsApp avec l'indicatif pays. Espaces, tirets, points, parenthèses, `+` ou `00` sont acceptés. Format local : voir ci-dessus. |
| Message | `Bonjour, je souhaite avoir des informations.` | Texte déjà saisi dans la discussion ; le visiteur peut le modifier. Vide : discussion vierge. |
| Accroche | `Une question ? Écrivez-nous` | Texte à côté du bouton, sur ordinateur. Vide : icône seule. |
| Position | En bas à droite | Ou en bas à gauche |

Cocher la case, remplir le numéro et enregistrer. Le lien **Tester** qui
apparaît sous les réglages doit ouvrir une discussion avec le bon numéro.
Le bouton apparaît aussitôt sur le site, pour tous les visiteurs.

Chaque site web a ses propres réglages (choisir le site en haut de
l'écran Paramètres).

## Bon à savoir

- **Chat en direct d'Odoo.** Sa bulle occupe aussi le coin inférieur
  droit : choisir la position « En bas à gauche ».
- **Site en plusieurs langues.** Le message et l'accroche sont
  traduisibles. Ils s'enregistrent dans la langue de l'utilisateur qui
  fait le réglage ; pour saisir la version anglaise, passer ses
  préférences en anglais puis revenir sur l'écran Paramètres. Une langue
  non renseignée affiche le texte anglais (tant qu'aucune version anglaise
  n'a été saisie : le premier texte enregistré). Vider le message ou
  l'accroche l'efface dans toutes les langues.
- **Numéro refusé** (« n'est pas reconnu ») : numéro local alors que la
  bibliothèque `phonenumbers` est absente, que la société du site n'a pas
  de pays ou que le numéro n'est pas valide pour ce pays ; ou numéro de
  moins de 7 ou de plus de 15 chiffres, indicatif compris. Le saisir au
  format `+237 …`.

## Mise à jour d'une installation existante

Faire d'abord une **sauvegarde** de la base : gestionnaire des bases
(`https://votre-site/web/database/manager` → *Backup*), ou
`sudo -u odoo pg_dump -Fc NOM_DE_LA_BASE -f /tmp/sauvegarde.dump`. La
mise à jour se fait **service arrêté** : un redémarrage sur le nouveau
code avant la mise à niveau du module provoquerait des erreurs sur tout
le site.

```bash
sudo systemctl stop odoo
```

Retirer l'ancien dossier (pour ne garder aucun fichier de l'ancienne
version) :

```bash
sudo rm -rf /opt/odoo/custom-addons/aite_website_whatsapp
```

Déposer le nouveau, comme à l'étape 2 de l'installation (`scp`, `unzip`,
`chown`), puis mettre le module à niveau :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d NOM_DE_LA_BASE -u aite_website_whatsapp --stop-after-init
```

```bash
sudo systemctl start odoo
```

(`odoo` est la commande des installations `.deb` ; depuis les sources :
`python3 odoo-bin` dans le dossier d'Odoo.) Les réglages déjà saisis dans
la version 19.0.1 sont repris ; un numéro qu'elle acceptait sans « + »
(`237 6 99 …`) le reçoit. Si un numéro n'est plus reconnu, le journal de
la mise à jour le signale (« n'est pas reconnu ; le bouton reste
masqué ») : le ressaisir au format `+237 …` dans les Paramètres.

Si le service a déjà été redémarré sur le nouveau code et que le site
affiche « column … does not exist », le remède est le même : arrêter le
service, lancer la commande `-u` ci-dessus, redémarrer.

**Cas particulier — version 19.0.1 installée par « Apps → Importer un
module ».** Ne **pas** déposer le nouveau dossier tant qu'elle est
installée : Odoo chargerait le nouveau code sans pouvoir mettre le module
à niveau, et le site afficherait des erreurs. Ordre à suivre : Apps → retirer le filtre
« Apps » de la recherche → chercher « Bouton WhatsApp » → ⋮ →
**Désinstaller**, puis l'installation complète
ci-dessus, puis ressaisir les réglages. Si le dossier a déjà été déposé :
le retirer, redémarrer, désinstaller, puis le déposer à nouveau.

## Tests automatisés

24 tests : lien, numéro, contrôles, écran Paramètres, affichage page par
page. Ils créent une base de test, avec l'identifiant `admin` / mot de
passe `admin`.

**À lancer de préférence sur un serveur de test, pas sur le VPS de
production.** Sur le serveur de production, une base de plus suffit à
dérégler le site : sans filtre de base dans la configuration, Odoo ne
sait plus quelle base servir et renvoie les visiteurs vers l'écran de
choix de la base. Si vous devez malgré tout les lancer sur ce VPS :
vérifier d'abord que `/etc/odoo/odoo.conf` contient
`db_name = NOM_DE_LA_BASE` (sinon l'ajouter et redémarrer le service),
puis supprimer la base de test juste après.

Lancement, sur une base qui **n'existe pas encore** (Odoo la crée) :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d aite_wa_test -i aite_website_whatsapp --test-tags aite_whatsapp --workers 0 --max-cron-threads 0 --db-filter '^aite_wa_test$' --http-port 8079 --stop-after-init
```

`--workers 0`, `--db-filter` et `--http-port` neutralisent les réglages de
production (processus multiples, filtre de base, port déjà occupé par le
service), qui feraient échouer les tests d'affichage. Résultat attendu en
fin de journal (ou dans le fichier `logfile` de la configuration) :
`0 failed, 0 error(s) of 24 tests`. Sans `phonenumbers`, un de ces tests
est ignoré (numéro local). Si la ligne annonce **0 tests**, la base
existait déjà avec le module : relancer avec une nouvelle base.

Supprimer ensuite la base de test :

```bash
sudo -u odoo dropdb aite_wa_test
```

```bash
sudo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/aite_wa_test
```

## Désinstallation

Apps → retirer le filtre « Apps » de la recherche → chercher « Bouton
WhatsApp » → ⋮ → **Désinstaller**. Le bouton disparaît
et les réglages sont supprimés.

## Contenu technique

| Fichier | Rôle |
|---|---|
| `models/website.py` | Réglages par site (`aite_whatsapp_*`), lien `wa.me` calculé dans la langue du visiteur, contrôle du numéro |
| `models/res_config_settings.py` | Les mêmes réglages dans l'écran Paramètres, appliqués au site sélectionné en une seule écriture |
| `views/res_config_settings_views.xml` | Le bloc « WhatsApp » des paramètres du site |
| `views/website_templates.xml` | Le bouton, ajouté à la fin de `#wrapwrap` dans `website.layout` |
| `static/src/scss/whatsapp_button.scss` | Style du bouton (bundle `web.assets_frontend`) |
| `migrations/19.0.2.0.0/` | Reprise des réglages de la version 19.0.1 |
| `tests/` | Tests automatisés (étiquette `aite_whatsapp`) |

Reconstruire le zip, depuis la racine du dépôt :

```bash
cd addons && rm -f ../dist/aite_website_whatsapp.zip && zip -r ../dist/aite_website_whatsapp.zip aite_website_whatsapp -x '*/__pycache__/*'
```

---
© AITE Consulting SARL — LGPL-3.
