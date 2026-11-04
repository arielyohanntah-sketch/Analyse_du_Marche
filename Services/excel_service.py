"""Collecte du classeur Excel de Comptoir Ivoire."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from Models.Journal import Journal
from Models.Offre import Offre
from Services.normalisation_service import (
    parser_entier,
    parser_note,
    sans_accents,
)


def _trouver_entete(lignes: list[tuple], journal: Journal) -> int:
    """Trouve la ligne d'en-tête (celle qui contient 'Code' et 'Article').

    Le fichier a un titre en ligne 1 et une ligne vide en ligne 2 : on ne
    code donc pas "ligne 3" en dur, on la cherche. C'est plus robuste.
    """
    for index, ligne in enumerate(lignes[:15]):
        textes = [sans_accents(str(cellule)).lower() for cellule in ligne if cellule]
        if any("code" in t for t in textes) and any("article" in t for t in textes):
            journal.ajouter(
                "COLLECTE", "Comptoir Ivoire", "-",
                f"en-tête détecté à la ligne {index + 1}",
                "lecture à partir de la ligne suivante",
            )
            return index
    raise ValueError("Comptoir Ivoire : ligne d'en-tête introuvable.")


def _colonne(entetes: list[str], mot_cle: str) -> int | None:
    """Retourne l'indice d'une colonne dont l'en-tête contient mot_cle."""
    for index, entete in enumerate(entetes):
        if mot_cle in entete:
            return index
    return None


def lire_comptoir(chemin: str | Path, journal: Journal) -> list[Offre]:
    """Lit comptoir_ivoire.xlsx.

    Le client paie le prix catalogue diminué de la remise, et vient chercher
    l'article : pas de frais de livraison.
    """
    chemin = Path(chemin)
    classeur = load_workbook(chemin, data_only=True, read_only=True)
    feuille = classeur.active
    titre_feuille = feuille.title
    lignes = list(feuille.iter_rows(values_only=True))
    classeur.close()

    index_entete = _trouver_entete(lignes, journal)
    entetes = [
        sans_accents(str(cellule)).lower().strip() if cellule is not None else ""
        for cellule in lignes[index_entete]
    ]

    i_code = _colonne(entetes, "code")
    i_article = _colonne(entetes, "article")
    i_prix = _colonne(entetes, "prix")
    i_remise = _colonne(entetes, "remise")
    i_quantite = _colonne(entetes, "quantit")

    if None in (i_code, i_article, i_prix, i_remise, i_quantite):
        raise ValueError(
            "Comptoir Ivoire : colonnes Code/Article/Prix/Remise/Quantité "
            "introuvables."
        )

    offres: list[Offre] = []
    for ligne in lignes[index_entete + 1:]:
        code = ligne[i_code] if i_code < len(ligne) else None
        article = ligne[i_article] if i_article < len(ligne) else None
        if code is None or article is None:
            continue

        code = str(code).strip()
        article = str(article).strip()
        if not code or not article:
            continue

        prix = ligne[i_prix] if i_prix < len(ligne) else None
        remise = parser_note(ligne[i_remise] if i_remise < len(ligne) else 0) or 0.0
        quantite = parser_entier(ligne[i_quantite] if i_quantite < len(ligne) else 0)

        offres.append(Offre(
            source="Comptoir Ivoire",
            reference=code,
            designation_brute=article,
            prix_source=prix,
            frais_livraison=0,
            remise_pct=remise,
            ancien_prix_source=None,
            stock=quantite,
            disponible_source=(quantite is not None and quantite > 0),
            note=None,
            nb_avis=None,
        ))

    journal.ajouter(
        "COLLECTE", "Comptoir Ivoire", "-",
        f"{len(offres)} articles lus dans la feuille '{titre_feuille}'",
        "fichier Excel chargé",
    )
    return offres
