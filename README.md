# Site de la crèche Les Bisounours

Site de la crèche associative Les Bisounours (Rosporden), hébergé gratuitement sur GitHub Pages.
Les contenus se modifient sans toucher au code, grâce à l'interface Pages CMS.

---

## 1. Mettre le site en ligne (une seule fois, environ 20 minutes)

### Créer le compte GitHub
1. Aller sur [github.com](https://github.com) et créer un compte gratuit, **idéalement avec l'adresse e-mail de la crèche** pour que le site reste à l'association quand le bureau change.
2. Choisir un nom de compte court, par exemple `creche-bisounours`. Il apparaîtra dans l'adresse du site.

### Déposer les fichiers
1. En haut à droite, cliquer sur **+** › **New repository**.
2. Nom : `site-creche`. Laisser **Public**. Cliquer sur **Create repository**.
3. Sur la page qui s'affiche, cliquer sur le lien **uploading an existing file**.
4. Décompresser le fichier zip du site sur l'ordinateur, puis **glisser tout le contenu du dossier** dans la fenêtre du navigateur.
   - ⚠️ Le dossier contient des éléments cachés indispensables (`.github` et `.pages.yml`). Sur Mac, appuyer sur **Cmd + Maj + point** dans le Finder pour les afficher avant de tout sélectionner. Sur Windows : menu **Affichage** › cocher **Éléments masqués**.
5. Cliquer sur **Commit changes**.
6. Vérifier que la liste des fichiers du dépôt contient bien **`.github`** et **`.pages.yml`**. Si l'un des deux manque (certains navigateurs ignorent les éléments cachés) : **Add file** › **Create new file**, taper le nom exact (`.pages.yml`, ou `.github/workflows/publier.yml`), coller le contenu du fichier correspondant ouvert avec un éditeur de texte, puis **Commit changes**.

### Activer la publication
1. Dans le dépôt, onglet **Settings** › menu de gauche **Pages**.
2. Dans **Source**, choisir **GitHub Actions**.
3. Onglet **Actions** › cliquer sur **Publier le site** › bouton **Run workflow**.
4. Attendre environ une minute que la pastille devienne verte ✅.
5. Le site est en ligne à l'adresse : `https://NOM-DU-COMPTE.github.io/site-creche/`

---

## 2. Brancher l'interface d'édition Pages CMS (une seule fois)

1. Aller sur [pagescms.org](https://pagescms.org) et cliquer sur **Sign in** (se connecter avec le compte GitHub de la crèche).
2. Autoriser l'application et lui donner accès au dépôt `site-creche`.
3. Ouvrir le dépôt : les rubriques **Actualités, Menus, Infos pratiques, Page d'accueil, Chiffres clés, Inscriptions, Équipe, Recrutement** apparaissent.
4. Pour donner l'accès à d'autres personnes (directrice, membre du bureau…) : dans Pages CMS, ouvrir les **réglages du dépôt** › **Collaborators**, et inviter leur adresse e-mail. **Elles n'ont pas besoin de compte GitHub.**

---

## 3. Modifier le site au quotidien

Tout se fait dans [pagescms.org](https://pagescms.org) :

| Je veux… | Rubrique | Comment |
|---|---|---|
| Mettre les menus de la semaine | **Menus** | Changer la période, cliquer sur le fichier PDF pour envoyer le nouveau, puis **Save** |
| Publier une actualité | **Actualités** › **Add an entry** | Titre, date, texte, photo facultative, puis **Save** |
| Retirer une actualité sans la supprimer | **Actualités** | Décocher « Publiée sur le site » |
| Changer les horaires, le téléphone, les liens de l'espace parents | **Infos pratiques** | Modifier puis **Save** |
| Ajouter une personne dans l'équipe | **Équipe** | Bouton **Add** sous « Membres de l'équipe » |
| Publier une offre d'emploi | **Recrutement** | Bouton **Add** sous « Offres d'emploi » ; supprimer l'offre une fois pourvue |
| Mettre à jour les chiffres après l'AG | **Chiffres clés** | Le montant alimente le compteur animé de « Notre projet » |
| Mettre le dossier d'inscription | **Inscriptions** | Envoyer le PDF dans « Dossier de pré-inscription » |

Après chaque **Save**, le site se met à jour tout seul en **une à deux minutes**.

**Bonnes pratiques**
- **Aucune photo d'enfant reconnaissable** sur le site public : elles vont dans l'album privé (voir ci-dessous).
- Photo d'une salariée : uniquement avec son **accord écrit**.
- Toujours remplir la **description de la photo** (utile aux personnes malvoyantes).
- Si le site ne se met pas à jour : sur GitHub, onglet **Actions**, une pastille rouge ❌ indique une erreur. Cliquer dessus : le message explique quel fichier pose problème.

---

## 4. L'espace parents (portail familles)

Les documents des familles et les photos ne sont **jamais** déposés sur le site : ils sont dans le Drive de la crèche, dans un portail privé (voir le dossier `portail-familles` et son guide).
Une fois le portail installé, copier ses trois liens (formulaire, album photos, documents communs) dans Pages CMS › **Infos pratiques**. La page « Espace parents » du site affiche alors ses boutons.

## 5. Plus tard : un nom de domaine (facultatif, environ 10 € par an)

Pour avoir une adresse du type `www.creche-bisounours.fr` :
1. Acheter le nom chez un registraire (OVH, Gandi, Porkbun…).
2. GitHub › **Settings** › **Pages** › **Custom domain** : saisir le nom et suivre les indications.
3. Chez le registraire, ajouter les enregistrements DNS indiqués par GitHub.

---

## Pour les personnes qui touchent au code

```
contenu/      ← textes et données modifiables (édités par Pages CMS)
gabarits/     ← mise en page des pages (HTML + Jinja2)
static/       ← styles, scripts, logos, images et PDF envoyés
build.py      ← assemble contenu + gabarits dans _site/
.pages.yml    ← configuration de l'interface d'édition
.github/workflows/publier.yml ← publication automatique
```

Tester sur un ordinateur :
```
pip install -r requirements.txt
python build.py
```
puis ouvrir `_site/index.html`.
