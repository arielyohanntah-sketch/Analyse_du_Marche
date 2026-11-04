"""Collecte des fichiers CSV : catalogue de référence et Marché Lagune."""

from __future__ import annotations

import csv
from pathlib import Path

from Models.Journal import Journal
from Models.Offre import Offre
from Models.Produit import Produit
from Services.normalisation_service import parser_entier, parser_note


def lire_catalogue(chemin: str | Path, journal: Journal) -> list[Produit]:
    """Lit catalogue_reference.csv et retourne la liste des 30 produits."""
    chemin = Path(chemin)
    produits: list[Produit] = []

    with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier)
        colonnes = set(lecteur.fieldnames or [])
        attendues = {"produit_id", "nom", "categorie", "marque"}
        if not attendues.issubset(colonnes):
            raise ValueError(
                f"Catalogue invalide : colonnes manquantes {attendues - colonnes}"
            )

        for numero, ligne in enumerate(lecteur, start=2):
            produit_id = (ligne.get("produit_id") or "").strip()
            nom = (ligne.get("nom") or "").strip()
            if not produit_id or not nom:
                journal.ajouter(
                    "COLLECTE", "Catalogue", f"ligne {numero}",
                    "identifiant ou nom manquant",
                    "ligne ignorée",
                    "ERREUR",
                )
                continue
            produits.append(Produit(
                produit_id=produit_id,
                nom=nom,
                categorie=(ligne.get("categorie") or "").strip(),
                marque=(ligne.get("marque") or "").strip(),
            ))

    journal.ajouter(
        "COLLECTE", "Catalogue", "-",
        f"{len(produits)} produits de référence lus",
        "catalogue chargé",
    )
    return produits


def lire_marche_lagune(chemin: str | Path, journal: Journal) -> list[Offre]:
    """Lit marche_lagune.csv (séparateur ';', encodage UTF-8 avec BOM).

    Le prix affiché inclut déjà la livraison : frais_livraison = 0.
    """
    chemin = Path(chemin)
    offres: list[Offre] = []

    with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=";")
        colonnes = set(lecteur.fieldnames or [])
        attendues = {
            "reference", "designation", "prix", "ancien_prix",
            "disponibilite", "note_clients", "nb_avis",
        }
        if not attendues.issubset(colonnes):
            raise ValueError(
                f"Marché Lagune invalide : colonnes manquantes {attendues - colonnes}"
            )

        for numero, ligne in enumerate(lecteur, start=2):
            reference = (ligne.get("reference") or "").strip()
            designation = (ligne.get("designation") or "").strip()
            if not reference or not designation:
                journal.ajouter(
                    "COLLECTE", "Marché Lagune", f"ligne {numero}",
                    "référence ou désignation manquante",
                    "ligne ignorée",
                    "ERREUR",
                )
                continue

            disponibilite = (ligne.get("disponibilite") or "").strip().lower()
            offres.append(Offre(
                source="Marché Lagune",
                reference=reference,
                designation_brute=ligne.get("designation") or "",
                prix_source=ligne.get("prix"),
                frais_livraison=0,
                remise_pct=0.0,
                ancien_prix_source=ligne.get("ancien_prix"),
                stock=None,
                disponible_source=disponibilite != "rupture",
                note=parser_note(ligne.get("note_clients")),
                nb_avis=parser_entier(ligne.get("nb_avis")),
            ))

    journal.ajouter(
        "COLLECTE", "Marché Lagune", "-",
        f"{len(offres)} lignes lues",
        "fichier CSV chargé",
    )
    return offres
