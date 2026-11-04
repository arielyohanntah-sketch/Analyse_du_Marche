"""Normalisation des noms, des prix et des disponibilités.

C'est le coeur du nettoyage. On transforme des écritures différentes
("SAMSUNG GALAXY A15 (128GB)", "Galaxy A15 128GB - Samsung",
"Samsun Galaxy A15 128Go") vers une même forme canonique :
    "samsung galaxy a15 128gb"

On ne supprime pas les accents du nom affiché : on les supprime seulement
dans la version normalisée utilisée pour comparer les produits.
"""

from __future__ import annotations

import difflib
import re
import unicodedata

from Models.Journal import Journal
from Models.Offre import Offre


# ---------------------------------------------------------------------------
# 1. Dictionnaires de normalisation
# ---------------------------------------------------------------------------

# Expressions remplacées avant le découpage en mots.
# L'ordre compte : les expressions longues passent avant les mots seuls.
EXPRESSIONS: list[tuple[str, str]] = [
    (r"\bair\s+conditioner\b", "climatiseur"),
    (r"\bair\s+conditioning\b", "climatiseur"),
    (r"\bsteam\s+iron\b", "fer"),
    (r"\bcle\s+usb\b", "usb"),
    (r"\bdisque\s+dur\b", "disque dur"),
    (r"\bdd\b", "disque dur"),
    (r"\bfer\s+a\s+repasser\b", "fer"),
    (r"\bmicrowave\b", "micro ondes"),
    (r"\bmicrowaves\b", "micro ondes"),
    (r"\bsans\s+fil\b", ""),
    (r"\bpc\s+portable\b", ""),
    (r"\bordinateur\s+portable\b", ""),
    (r"\bmoniteur\b", "ecran"),
    (r"\bmonitor\b", "ecran"),
    (r"\btelevision\b", "tv"),
]

# Mots seuls remplacés par un mot canonique.
SYNONYMES: dict[str, str] = {
    "frigo": "refrigerateur",
    "fridge": "refrigerateur",
    "refrigerator": "refrigerateur",
    "clim": "climatiseur",
    "blender": "mixeur",
    "kettle": "bouilloire",
    "iron": "fer",
    "mouse": "souris",
    "printer": "imprimante",
    "router": "routeur",
    "ventilo": "ventilateur",
    "fan": "ventilateur",
}

# Mots trop généraux ou simples descriptions : ils ne doivent pas peser
# dans le rapprochement des produits.
MOTS_IGNORES: set[str] = {
    "de", "du", "des", "le", "la", "les", "un", "une", "et", "a", "au",
    "aux", "en", "sur", "pour", "avec", "the", "with", "and", "for",
    "pc", "portable", "ordinateur", "laptop", "smartphone", "telephone",
    "core", "series", "ssd", "ultra", "expansion", "steam", "wireless",
    "crystal", "uhd", "4k", "pouces", "externe", "electrique", "electric",
    "pied", "fil", "sans", "plus", "max", "new", "original", "pack",
}

# Marques connues et leurs formes canoniques.
# Pour TP-Link, les deux mots "tp" et "link" doivent être présents.
MARQUES: dict[str, list[str]] = {
    "Samsung": ["samsung"],
    "Tecno": ["tecno"],
    "Infinix": ["infinix"],
    "Itel": ["itel"],
    "Apple": ["apple"],
    "Xiaomi": ["xiaomi"],
    "HP": ["hp"],
    "Lenovo": ["lenovo"],
    "Dell": ["dell"],
    "SanDisk": ["sandisk"],
    "Seagate": ["seagate"],
    "Logitech": ["logitech"],
    "TP-Link": ["tp", "link"],
    "Hisense": ["hisense"],
    "Nasco": ["nasco"],
    "LG": ["lg"],
    "Binatone": ["binatone"],
    "Moulinex": ["moulinex"],
    "Philips": ["philips"],
}


# ---------------------------------------------------------------------------
# 2. Texte : accents, casse, espaces, unités
# ---------------------------------------------------------------------------

def sans_accents(texte: str) -> str:
    """Enlève les accents : 'Écran' -> 'Ecran'."""
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def nettoyer_designation(texte: str) -> str:
    """Nettoie le nom pour l'affichage (sans le dénaturer)."""
    texte = str(texte)
    texte = texte.replace("\u00a0", " ").replace("\u202f", " ")
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()


def normaliser_texte(texte: str | None) -> str:
    """Transforme un nom en forme canonique utilisée pour le rapprochement.

    Étapes : minuscules -> suppression des accents -> ponctuation remplacée
    par des espaces -> unités unifiées -> synonymes -> mots ignorés.
    """
    if texte is None:
        return ""

    t = sans_accents(str(texte)).lower()
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("–", "-").replace("—", "-").replace("−", "-")
    t = re.sub(r"[\u00a0\u202f\u2007\u2009\u2060]", " ", t)

    # 1,5 -> 1.5 (virgule décimale)
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)

    # 24" -> 24 pouces (le mot "pouces" sera ensuite ignoré)
    t = re.sub(r'(\d+(?:\.\d+)?)\s*"', r"\1 pouces ", t)

    # Expressions (avant de remplacer la ponctuation)
    for motif, remplacement in EXPRESSIONS:
        t = re.sub(motif, remplacement, t)

    # Ponctuation -> espace. On garde le point des nombres décimaux.
    t = re.sub(r"[^a-z0-9.]+", " ", t)

    # Unités collées : "128 gb" -> "128gb", "1,5 l" -> "1.5l"
    t = re.sub(r"\b(\d+(?:\.\d+)?)\s*(go|gb)\b", r"\1gb", t)
    t = re.sub(r"\b(\d+(?:\.\d+)?)\s*(to|tb)\b", r"\1tb", t)
    t = re.sub(r"\b(\d+(?:\.\d+)?)\s*(cv|hp)\b", r"\1hp", t)
    t = re.sub(r"\b(\d+(?:\.\d+)?)\s*l\b", r"\1l", t)

    t = re.sub(r"\s+", " ", t).strip()

    mots: list[str] = []
    for mot in t.split():
        mot = SYNONYMES.get(mot, mot)
        if mot and mot not in MOTS_IGNORES:
            mots.append(mot)
    return " ".join(mots)


def tokeniser(texte_normalise: str) -> set[str]:
    """Retourne l'ensemble des mots d'un texte déjà normalisé."""
    return set(texte_normalise.split())


def normaliser_source(nom: str | None) -> str:
    """Ramène les noms d'enseignes à une forme unique.

    Utile pour l'historique, où une source pourrait être écrite avec une
    casse ou un accent différent.
    """
    texte = normaliser_texte(nom)
    if "lagune" in texte:
        return "Marché Lagune"
    if "baobab" in texte:
        return "Baobab Shop"
    if "comptoir" in texte:
        return "Comptoir Ivoire"
    return nettoyer_designation(nom or "")


# ---------------------------------------------------------------------------
# 3. Marques : détection exacte et correction des fautes de frappe
# ---------------------------------------------------------------------------

def identifier_marque(texte_normalise: str) -> tuple[str | None, bool]:
    """Retourne (marque canonique, orthographe_exacte).

    Exemple : "samsun galaxy a15" -> ("Samsung", False)
              "samsung galaxy a15" -> ("Samsung", True)
    """
    mots = tokeniser(texte_normalise)

    # 1) Recherche exacte
    for marque, variantes in MARQUES.items():
        if all(v in mots for v in variantes):
            return marque, True

    # 2) Recherche approximative pour les fautes de frappe.
    # On ne compare que des mots alphabétiques d'au moins 4 lettres,
    # pour éviter de confondre "hp" ou "lg" avec autre chose.
    for mot in mots:
        if not mot.isalpha() or len(mot) < 4:
            continue
        for marque, variantes in MARQUES.items():
            for variante in variantes:
                if len(variante) < 4:
                    continue
                ratio = difflib.SequenceMatcher(None, mot, variante).ratio()
                if ratio >= 0.85:
                    return marque, False

    return None, False


# ---------------------------------------------------------------------------
# 4. Prix, notes et quantités
# ---------------------------------------------------------------------------

def parser_prix(valeur: str | int | float | None) -> int | None:
    """Convertit un prix en entier FCFA, ou None s'il n'est pas exploitable.

    Gère : "102 900 FCFA", "279 300", 109400, "Prix sur demande", "".
    """
    if valeur is None or isinstance(valeur, bool):
        return None
    if isinstance(valeur, (int, float)):
        return int(round(valeur)) if valeur > 0 else None

    texte = str(valeur).strip()
    if not texte:
        return None

    texte_minuscule = sans_accents(texte).lower()
    if "demande" in texte_minuscule or "devis" in texte_minuscule:
        return None
    if "-" in texte_minuscule:
        return None

    # On garde uniquement les chiffres et les séparateurs.
    nettoye = re.sub(r"[^\d,.]", "", texte)
    if not nettoye:
        return None

    if "," in nettoye and "." in nettoye:
        # Le dernier séparateur rencontré est le séparateur décimal.
        if nettoye.rfind(",") > nettoye.rfind("."):
            nettoye = nettoye.replace(".", "").replace(",", ".")
        else:
            nettoye = nettoye.replace(",", "")
    elif "," in nettoye:
        partie_decimale = nettoye.split(",")[-1]
        if len(partie_decimale) in (1, 2):
            nettoye = nettoye.replace(",", ".")
        else:
            nettoye = nettoye.replace(",", "")
    elif "." in nettoye:
        partie_decimale = nettoye.split(".")[-1]
        # "102.900" ou "1.500" : séparateur de milliers
        if len(partie_decimale) == 3:
            nettoye = nettoye.replace(".", "")

    try:
        nombre = float(nettoye)
    except ValueError:
        return None

    if nombre <= 0:
        return None
    return int(nombre + 0.5)


def parser_note(valeur: str | int | float | None) -> float | None:
    """Convertit une note client en float, en acceptant la virgule."""
    if valeur is None or isinstance(valeur, bool):
        return None
    if isinstance(valeur, (int, float)):
        return float(valeur)
    texte = str(valeur).strip().replace(",", ".")
    try:
        return float(texte)
    except ValueError:
        return None


def parser_entier(valeur: str | int | float | None) -> int | None:
    """Convertit une quantité en entier, ou None."""
    if valeur is None or isinstance(valeur, bool):
        return None
    if isinstance(valeur, (int, float)):
        return int(valeur)
    texte = re.sub(r"[^\d-]", "", str(valeur))
    if texte in ("", "-"):
        return None
    try:
        return int(texte)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 5. Normalisation d'une offre et dédoublonnage
# ---------------------------------------------------------------------------

def normaliser_offre(offre: Offre, journal: Journal) -> Offre:
    """Nettoie une offre brute et calcule son prix réellement payé."""
    brut = offre.designation_brute
    offre.designation = nettoyer_designation(brut)

    if offre.designation != str(brut):
        journal.ajouter(
            "NORMALISATION", offre.source, offre.reference,
            "espaces superflus dans le nom",
            "nom nettoyé pour l'affichage",
        )

    offre.designation_normalisee = normaliser_texte(offre.designation)

    # Faute de frappe sur la marque (ex. "Samsun")
    marque, exacte = identifier_marque(offre.designation_normalisee)
    if marque and not exacte:
        journal.ajouter(
            "NORMALISATION", offre.source, offre.reference,
            "marque probablement mal orthographiée",
            f"interprétée comme {marque}",
            "AVERTISSEMENT",
        )

    # Prix affiché
    offre.prix_brut = parser_prix(offre.prix_source)

    # Prix écrit sous forme de texte sans devise (ex. "279 300" dans Excel)
    if offre.prix_brut is not None and isinstance(offre.prix_source, str):
        texte = offre.prix_source.lower()
        if "fcfa" not in texte and any(c.isdigit() for c in texte):
            journal.ajouter(
                "NORMALISATION", offre.source, offre.reference,
                "prix écrit sous forme de texte",
                f"converti en {offre.prix_brut} FCFA",
            )

    # Détection d'un prix incohérent avec l'ancien prix.
    ancien_prix = parser_prix(offre.ancien_prix_source)
    if offre.prix_brut is not None and ancien_prix:
        ratio = offre.prix_brut / ancien_prix
        if ratio > 1.5 or ratio < 0.3:
            journal.ajouter(
                "NETTOYAGE", offre.source, offre.reference,
                f"prix {offre.prix_brut} FCFA incohérent avec l'ancien prix "
                f"{ancien_prix} FCFA (ratio {ratio:.2f})",
                "offre écartée de la comparaison",
                "AVERTISSEMENT",
            )
            offre.prix = None
            offre.disponible = False
            return offre

    # Prix absent ou illisible
    if offre.prix_brut is None:
        journal.ajouter(
            "NETTOYAGE", offre.source, offre.reference,
            "prix absent ou illisible",
            "offre non comparable",
            "AVERTISSEMENT",
        )
        offre.prix = None
        offre.disponible = False
        return offre

    # Prix réellement payé :
    # - remise éventuelle (Comptoir Ivoire)
    # - frais de livraison éventuels (Baobab Shop)
    prix = offre.prix_brut * (1 - offre.remise_pct / 100) + offre.frais_livraison
    offre.prix = int(prix + 0.5)

    if not offre.disponible_source:
        journal.ajouter(
            "NETTOYAGE", offre.source, offre.reference,
            "article en rupture de stock",
            "offre exclue de la comparaison",
        )
        offre.disponible = False
    else:
        offre.disponible = True

    return offre


def dedupliquer(offres: list[Offre], journal: Journal) -> list[Offre]:
    """Supprime les doublons (même source + même référence).

    On garde la première occurrence et on signale les suivantes.
    Complexité : O(n) grâce au dictionnaire.
    """
    vues: set[tuple[str, str]] = set()
    resultat: list[Offre] = []

    for offre in offres:
        cle = (offre.source, offre.reference.strip())
        if cle in vues:
            journal.ajouter(
                "NETTOYAGE", offre.source, offre.reference,
                "ligne en double",
                "doublon ignoré",
                "AVERTISSEMENT",
            )
            continue
        vues.add(cle)
        resultat.append(offre)

    return resultat
