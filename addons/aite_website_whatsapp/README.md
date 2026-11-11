# AITE — Bouton WhatsApp du site web

**Odoo 19 (Enterprise & Community) · module `aite_website_whatsapp` · version 19.0.1.0.0**

Un bouton vert WhatsApp, fixé en bas de l'écran, sur **toutes les pages du
site** : un clic ouvre directement une discussion avec votre numéro —
dans l'application WhatsApp sur mobile, dans WhatsApp Web sur ordinateur —
avec votre message d'accueil déjà saisi.

## Ce que fait le module

- Le bouton est ajouté à la **mise en page commune du site** : il figure
  sur toutes les pages — accueil, pages créées dans l'éditeur, boutique,
  blog, espace client, page de connexion — y compris les pages créées
  plus tard. Aucune page à modifier une à une.
- Sur **ordinateur**, un court texte d'accroche (« Une question ?
  Écrivez-nous ») s'affiche à côté de l'icône ; sur **mobile**, seule
  l'icône reste, pour ne pas masquer le contenu.
- Le lien est un simple lien `https://wa.me/…`, sans script : il marche
  dès l'affichage de la page, sur tous les navigateurs.
- Le bouton est masqué dans l'éditeur du site et en mode traduction, pour
  ne pas gêner la mise en page, et à l'impression.

## Installation

Le module ne contient **aucun code Python** : il s'installe sur tous les
hébergements Odoo 19.

### Odoo Online (hébergé par Odoo, adresse en `…odoo.com`)

1. Récupérer le fichier **`aite_website_whatsapp.zip`** (dossier `dist/`
   du dépôt).
2. Activer le **mode développeur** : Paramètres → tout en bas →
   « Activer le mode développeur ».
3. **Applications → Importer un module** → choisir le zip →
   **Importer**.

   Si le menu « Importer un module » n'apparaît pas : Applications →
   rechercher `base_import_module` (retirer le filtre « Applications ») →
   l'installer, puis recommencer.

### Odoo.sh ou serveur hébergé

1. Copier le dossier `aite_website_whatsapp/` dans le dépôt des modules
   (Odoo.sh : dans la branche, puis *push*) ou dans un répertoire de
   l'`addons_path` (serveur : puis redémarrer le service).
2. Mode développeur → **Applications → Mettre à jour la liste des
   applications** → rechercher « WhatsApp » → **Activer**.

## Réglage

**Site web → Configuration → Paramètres → bloc « WhatsApp »** (juste sous
le bloc « Général ») :

| Réglage | Exemple | Rôle |
|---|---|---|
| Bouton WhatsApp | ☑ | Affiche ou masque le bouton sur tout le site |
| Numéro | `+237 6 73 37 33 67` | Numéro WhatsApp **avec l'indicatif pays**. Espaces, tirets, points, parenthèses, `+` ou `00` sont acceptés. |
| Message | `Bonjour, je souhaite avoir des informations.` | Texte déjà saisi dans la discussion ; le visiteur peut le modifier. Vide : discussion vierge. |
| Accroche | `Une question ? Écrivez-nous` | Texte à côté du bouton, sur ordinateur. Vide : icône seule. |
| Placer le bouton en bas à gauche | ☐ | Par défaut le bouton est en bas à droite |

Enregistrer, puis cliquer le lien **Tester** qui apparaît sous les
réglages : il doit ouvrir une discussion avec le bon numéro.

Chaque site web a ses propres réglages (choisir le site en haut de
l'écran Paramètres).

## Bon à savoir

- **Délai d'affichage pour les visiteurs.** Odoo garde en cache les pages
  statiques servies aux visiteurs non connectés jusqu'à **une heure**.
  Après un changement de réglage, vous le voyez immédiatement (connecté) ;
  un visiteur anonyme peut voir l'ancienne version de ces pages pendant
  une heure au plus.
- **Chat en direct d'Odoo.** Sa bulle occupe aussi le coin inférieur
  droit : cocher « Placer le bouton en bas à gauche ».
- **Site en plusieurs langues.** Le message et l'accroche sont
  traduisibles. Ils sont enregistrés dans la langue de l'utilisateur qui
  fait le réglage ; pour saisir la version anglaise, passer ses
  préférences en anglais puis revenir sur l'écran Paramètres. Une langue
  non renseignée reprend le texte saisi en premier.
- **Numéro sans indicatif** (ex. `673373367`) : WhatsApp ne trouvera pas
  le contact. Toujours commencer par l'indicatif (`237` pour le Cameroun).

## Désinstallation

Applications → « Bouton WhatsApp » → **Désinstaller**. Le bouton
disparaît et les réglages sont supprimés.

## Contenu technique

| Fichier | Rôle |
|---|---|
| `data/website_fields.xml` | Champs de réglage `x_aite_wa_*` sur le modèle `website`, dont le lien `wa.me` calculé à partir du numéro |
| `data/res_config_settings_fields.xml` | Les mêmes champs dans l'écran Paramètres, liés au site sélectionné |
| `views/res_config_settings_views.xml` | Le bloc « WhatsApp » des paramètres du site |
| `views/website_templates.xml` | Le bouton, ajouté à `website.layout` après `#wrapwrap` |
| `static/src/scss/whatsapp_button.scss` | Style du bouton (bundle `web.assets_frontend`) |

Les champs sont déclarés en données (`ir.model.fields`, préfixe `x_`)
plutôt qu'en Python : c'est ce qui rend le module importable sur Odoo
Online. Ils sont supprimés avec le module.

Reconstruire le zip à importer, depuis la racine du dépôt :

```bash
cd addons && zip -r ../dist/aite_website_whatsapp.zip aite_website_whatsapp -x '*/__pycache__/*'
```

---
© AITE Consulting SARL — LGPL-3.
