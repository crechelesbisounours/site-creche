"""
Génère le site de la crèche Les Bisounours.

Lit les contenus modifiables (dossier `contenu/`), les place dans les gabarits
(dossier `gabarits/`) et écrit le site prêt à publier dans `_site/`.
GitHub lance ce script automatiquement à chaque modification.

Pour tester sur un ordinateur :  pip install jinja2 pyyaml markdown
                                 python build.py
puis ouvrir _site/index.html dans un navigateur.
"""
import datetime as dt
import pathlib
import re
import shutil
import sys
import time
import unicodedata

import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader, ChainableUndefined, select_autoescape
from markupsafe import Markup

RACINE = pathlib.Path(__file__).resolve().parent
CONTENU = RACINE / "contenu"
GABARITS = RACINE / "gabarits"
STATIQUE = RACINE / "static"
SORTIE = RACINE / "_site"

# Pages du site : gabarit -> identifiant utilisé pour surligner le menu
PAGES = {
    "index.html": "accueil",
    "projet.html": "projet",
    "equipe.html": "equipe",
    "actualites.html": "actualites",
    "inscriptions.html": "inscriptions",
    "recrutement.html": "recrutement",
    "contact.html": "contact",
    "espace-parents.html": "parents",
    "mentions-legales.html": "mentions",
    "404.html": "erreur",
}
NAVIGATION = [
    {"id": "projet", "label": "Notre projet", "url": "projet.html"},
    {"id": "equipe", "label": "L'équipe", "url": "equipe.html"},
    {"id": "actualites", "label": "Actualités", "url": "actualites.html"},
    {"id": "inscriptions", "label": "Inscriptions", "url": "inscriptions.html"},
    {"id": "recrutement", "label": "Recrutement", "url": "recrutement.html"},
]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


class ErreurContenu(Exception):
    pass


# ---------- Filtres utilisés dans les gabarits ----------

def chemin(valeur):
    """Chemin d'un fichier envoyé par l'interface d'édition, rendu relatif."""
    if not valeur:
        return ""
    valeur = str(valeur).strip()
    if re.match(r"^[a-z]+://", valeur):
        return valeur
    return valeur.lstrip("/")


def vers_date(valeur):
    if isinstance(valeur, dt.datetime):
        return valeur.date()
    if isinstance(valeur, dt.date):
        return valeur
    if isinstance(valeur, str) and valeur.strip():
        return dt.date.fromisoformat(valeur.strip()[:10])
    return None


def date_fr(valeur):
    d = vers_date(valeur)
    return f"{d.day} {MOIS[d.month - 1]} {d.year}" if d else ""


def euros(valeur):
    try:
        n = int(round(float(valeur)))
    except (TypeError, ValueError):
        return str(valeur)
    return f"{n:,}".replace(",", " ") + " €"


def tel(valeur):
    chiffres = re.sub(r"\D", "", str(valeur or ""))
    if chiffres.startswith("0") and len(chiffres) == 10:
        return "+33" + chiffres[1:]
    return chiffres


def markdown_html(texte):
    return Markup(md.markdown(str(texte or ""), extensions=["nl2br", "sane_lists"]))


# ---------- Lecture des contenus ----------

def lire_yaml(nom, obligatoires=()):
    fichier = CONTENU / nom
    try:
        donnees = yaml.safe_load(fichier.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise ErreurContenu(f"Le fichier contenu/{nom} est introuvable.")
    except yaml.YAMLError as e:
        raise ErreurContenu(f"Le fichier contenu/{nom} contient une erreur de mise en forme : {e}")
    for cle in obligatoires:
        if cle not in donnees:
            raise ErreurContenu(f"Il manque « {cle} » dans contenu/{nom}.")
    for cle, val in list(donnees.items()):
        if val is None:
            donnees[cle] = ""
    return donnees


def slug(texte):
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texte.lower()).strip("-") or "actualite"


def lire_actualites():
    actus = []
    for f in sorted((CONTENU / "actualites").glob("*.md")):
        brut = f.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", brut, re.S)
        if not m:
            raise ErreurContenu(f"L'actualité {f.name} n'a pas d'en-tête (titre, date).")
        meta = yaml.safe_load(m.group(1)) or {}
        corps = m.group(2).strip()
        titre = str(meta.get("titre") or meta.get("title") or "").strip()
        if not titre:
            raise ErreurContenu(f"L'actualité {f.name} n'a pas de titre.")
        try:
            date = vers_date(meta.get("date")) or dt.date.today()
        except ValueError:
            raise ErreurContenu(f"La date de l'actualité {f.name} n'est pas valide.")
        if meta.get("publiee") is False:
            continue
        texte_brut = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", corps)
        texte_brut = re.sub(r"[#*_>`]", "", texte_brut).replace("\n", " ").strip()
        resume = texte_brut if len(texte_brut) <= 170 else texte_brut[:170].rsplit(" ", 1)[0] + "…"
        actus.append({
            "titre": titre,
            "date": date,
            "image": meta.get("image") or "",
            "image_description": meta.get("image_description") or "",
            "html": markdown_html(corps),
            "resume": resume,
            "slug": slug(f.stem),
        })
    actus.sort(key=lambda a: a["date"], reverse=True)
    return actus


def verifier_fichiers(donnees):
    """Signale les images ou PDF référencés mais absents (sans bloquer)."""
    alertes = []

    def parcourir(v):
        if isinstance(v, dict):
            for x in v.values():
                parcourir(x)
        elif isinstance(v, list):
            for x in v:
                parcourir(x)
        elif isinstance(v, str) and re.match(r"^/?(images|documents)/", v):
            if not (STATIQUE / v.lstrip("/")).exists():
                alertes.append(v)
    parcourir(donnees)
    return alertes


# ---------- Génération ----------

def construire():
    debut = time.time()
    donnees = {
        "infos": lire_yaml("infos.yml", ["telephone", "email"]),
        "accueil": lire_yaml("accueil.yml", ["titre"]),
        "chiffres": lire_yaml("chiffres.yml", ["chiffres"]),
        "menus": lire_yaml("menus.yml"),
        "inscriptions": lire_yaml("inscriptions.yml"),
        "equipe": lire_yaml("equipe.yml", ["membres"]),
        "recrutement": lire_yaml("recrutement.yml"),
    }
    donnees["recrutement"]["offres"] = donnees["recrutement"].get("offres") or []
    donnees["equipe"]["membres"] = donnees["equipe"].get("membres") or []
    donnees["infos"]["horaires_details"] = donnees["infos"].get("horaires_details") or []
    actualites = lire_actualites()

    env = Environment(
        loader=FileSystemLoader(GABARITS),
        autoescape=select_autoescape(["html"]),
        undefined=ChainableUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(chemin=chemin, date_fr=date_fr, euros=euros, tel=tel, markdown=markdown_html)

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    shutil.copytree(STATIQUE, SORTIE, ignore=shutil.ignore_patterns(".gitkeep", ".DS_Store"))
    (SORTIE / ".nojekyll").write_text("")

    version = dt.datetime.now().strftime("%Y%m%d%H%M")
    for gabarit, page in PAGES.items():
        html = env.get_template(gabarit).render(
            page=page, navigation=NAVIGATION, actualites=actualites, version=version, **donnees)
        (SORTIE / gabarit).write_text(html, encoding="utf-8")

    for f in verifier_fichiers(donnees) + [a["image"] for a in actualites
                                           if a["image"] and not (STATIQUE / chemin(a["image"])).exists()]:
        print(f"  Attention : le fichier « {f} » est indiqué mais introuvable.")
    print(f"Site généré dans _site/ ({len(PAGES)} pages, {len(actualites)} actualité(s)) en {time.time() - debut:.1f} s.")


if __name__ == "__main__":
    try:
        construire()
    except ErreurContenu as e:
        print(f"\nERREUR dans le contenu : {e}\n", file=sys.stderr)
        sys.exit(1)
