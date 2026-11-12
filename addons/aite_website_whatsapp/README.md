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
- Le bouton est masqué pendant l'édition d'une page, pour ne pas gêner la
  mise en page, et à l'impression. Connecté ou non, vous le voyez comme
  vos visiteurs.

## Installation sur un serveur (VPS)

Les commandes ci-dessous se lancent **sur le VPS**, en SSH. Les chemins et
le nom du service varient selon l'installation : les deux premières
commandes servent à les retrouver.

**1. Repérer le fichier de configuration et le dossier des modules**

```bash
systemctl list-units --type=service | grep -i odoo
```

```bash
grep -E '^\s*addons_path' /etc/odoo/odoo.conf
```

La première commande donne le nom du service (souvent `odoo`, `odoo19` ou
`odoo-server`). Si `/etc/odoo/odoo.conf` n'existe pas, le chemin du
fichier de configuration figure après `-c` dans
`systemctl cat <nom du service>`. Dans `addons_path`, choisissez le
dossier de **vos** modules (pas celui d'Odoo ni d'Enterprise) — par
exemple `/opt/odoo/custom-addons`.

**2. Déposer le module**

Depuis votre ordinateur, envoyer le zip sur le VPS :

```bash
scp aite_website_whatsapp.zip utilisateur@adresse-du-vps:/tmp/
```

Puis, sur le VPS (adapter le dossier de l'étape 1) :

```bash
sudo unzip -o /tmp/aite_website_whatsapp.zip -d /opt/odoo/custom-addons/
```

```bash
sudo chown -R odoo:odoo /opt/odoo/custom-addons/aite_website_whatsapp
```

(`odoo` est l'utilisateur système qui fait tourner le service : la
ligne `User=` de `systemctl cat <nom du service>` le confirme.)

**3. Redémarrer Odoo**

```bash
sudo systemctl restart odoo
```

**4. Installer le module** dans Odoo : activer le **mode développeur**
(Paramètres → tout en bas → « Activer le mode développeur »), puis
**Applications → Mettre à jour la liste des applications**, rechercher
« WhatsApp » (retirer le filtre « Applications ») → **Activer**.

**Facultatif — numéros saisis au format local.** Pour que `699 00 00 00`
soit complété automatiquement en `+237 699 00 00 00`, Odoo s'appuie sur
la bibliothèque Python `phonenumbers`. Sans elle, le module fonctionne
aussi, mais le numéro doit être saisi avec l'indicatif. Pour l'installer :
`sudo apt install python3-phonenumbers` (Odoo installé en paquet `.deb`),
ou `pip install phonenumbers` dans l'environnement Python d'Odoo
(installation depuis les sources), puis redémarrer le service.

## Réglage

**Site web → Configuration → Paramètres → bloc « WhatsApp »** (juste sous
le bloc « Général ») :

| Réglage | Exemple | Rôle |
|---|---|---|
| Bouton WhatsApp | ☑ | Affiche ou masque le bouton sur tout le site |
| Numéro | `+237 6 99 00 00 00` | Numéro WhatsApp avec l'indicatif pays. Espaces, tirets, points, `+` ou `00` sont acceptés ; un numéro local reçoit l'indicatif du pays de la société (voir ci-dessus). |
| Message | `Bonjour, je souhaite avoir des informations.` | Texte déjà saisi dans la discussion ; le visiteur peut le modifier. Vide : discussion vierge. |
| Accroche | `Une question ? Écrivez-nous` | Texte à côté du bouton, sur ordinateur. Vide : icône seule. |
| Position | En bas à droite | Ou en bas à gauche |

Enregistrer, puis cliquer le lien **Tester** qui apparaît sous les
réglages : il doit ouvrir une discussion avec le bon numéro. Le bouton
apparaît aussitôt sur le site, pour tous les visiteurs.

Chaque site web a ses propres réglages (choisir le site en haut de
l'écran Paramètres).

## Bon à savoir

- **Chat en direct d'Odoo.** Sa bulle occupe aussi le coin inférieur
  droit : choisir la position « En bas à gauche ».
- **Site en plusieurs langues.** Le message et l'accroche sont
  traduisibles. Ils s'enregistrent dans la langue de l'utilisateur qui
  fait le réglage ; pour saisir la version anglaise, passer ses
  préférences en anglais puis revenir sur l'écran Paramètres. Une langue
  non renseignée reprend le texte saisi en premier.
- **Numéro refusé** : « n'est pas valide » signale un numéro trop court ou
  trop long (moins de 7 ou plus de 15 chiffres, indicatif compris).

## Mise à jour depuis la version précédente (19.0.1)

- **Installée depuis le dossier des modules** : remplacer le dossier
  (étape 2), redémarrer (étape 3), puis Applications → « Bouton
  WhatsApp » → **Mettre à niveau**. Les réglages déjà saisis sont repris.
- **Installée par « Applications → Importer un module »** : la
  **désinstaller** d'abord (Applications → « Bouton WhatsApp » →
  Désinstaller), puis suivre l'installation ci-dessus et ressaisir les
  réglages. Une version importée n'est jamais chargée comme module
  Python : la nouvelle ne s'activerait pas par-dessus.

## Tests automatisés

18 tests (lien, numéro, contrôles, écran Paramètres, affichage page par
page). À lancer sur une **base de test**, jamais sur la base de
production, et sur un autre port que le service en cours
(`--http-port`) :

```bash
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d base_de_test -i aite_website_whatsapp --test-enable --test-tags aite_whatsapp --http-port 8079 --stop-after-init
```

(`odoo` est la commande des installations `.deb` ; depuis les sources :
`python3 odoo-bin` dans le dossier d'Odoo.) Résultat attendu en fin de
journal : `0 failed, 0 error(s)`. Sans `phonenumbers`, un test est
ignoré (numéro local).

## Désinstallation

Applications → « Bouton WhatsApp » → **Désinstaller**. Le bouton
disparaît et les réglages sont supprimés.

## Contenu technique

| Fichier | Rôle |
|---|---|
| `models/website.py` | Réglages par site (`aite_whatsapp_*`), lien `wa.me` calculé dans la langue du visiteur, contrôle du numéro |
| `models/res_config_settings.py` | Les mêmes réglages dans l'écran Paramètres, liés au site sélectionné |
| `views/res_config_settings_views.xml` | Le bloc « WhatsApp » des paramètres du site |
| `views/website_templates.xml` | Le bouton, ajouté à `website.layout` après `#wrapwrap` |
| `static/src/scss/whatsapp_button.scss` | Style du bouton (bundle `web.assets_frontend`) |
| `migrations/19.0.2.0.0/` | Reprise des réglages de la version 19.0.1 |
| `tests/` | Tests automatisés (étiquette `aite_whatsapp`) |

Reconstruire le zip, depuis la racine du dépôt :

```bash
cd addons && zip -r ../dist/aite_website_whatsapp.zip aite_website_whatsapp -x '*/__pycache__/*'
```

---
© AITE Consulting SARL — LGPL-3.
