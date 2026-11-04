"""Collecte du fichier JSON de Baobab Shop."""

from __future__ import annotations

import json
from pathlib import Path

from Models.Journal import Journal
from Models.Offre import Offre


def lire_baobab(chemin: str | Path, journal: Journal) -> list[Offre]:
    """Lit baobab_shop.json et transforme chaque article en Offre.

    Chez Baobab, le client paie amount + delivery_fee.
    """
    chemin = Path(chemin)
    with chemin.open("r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    items = donnees.get("items")
    if not isinstance(items, list):
        raise ValueError("Baobab Shop invalide : la clé 'items' est absente.")

    offres: list[Offre] = []
    for index, item in enumerate(items, start=1):
        titre = (item.get("title") or "").strip()
        sku = (item.get("sku") or f"ligne {index}").strip()
        if not titre:
            journal.ajouter(
                "COLLECTE", "Baobab Shop", sku,
                "titre manquant",
                "article ignoré",
                "ERREUR",
            )
            continue

        pricing = item.get("pricing") or {}
        rating = item.get("rating") or {}
        stock = item.get("stock")
        stock = int(stock) if isinstance(stock, (int, float)) else None

        offres.append(Offre(
            source="Baobab Shop",
            reference=sku,
            designation_brute=titre,
            prix_source=pricing.get("amount"),
            frais_livraison=int(pricing.get("delivery_fee") or 0),
            remise_pct=0.0,
            ancien_prix_source=None,
            stock=stock,
            disponible_source=(stock is not None and stock > 0),
            note=rating.get("average"),
            nb_avis=rating.get("count"),
        ))

    journal.ajouter(
        "COLLECTE", "Baobab Shop", "-",
        f"{len(offres)} articles lus",
        "fichier JSON chargé",
    )
    return offres
