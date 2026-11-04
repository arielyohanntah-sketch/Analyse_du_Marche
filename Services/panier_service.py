"""Calcul du panier de rentrée et de la meilleure combinaison d'achats."""

from __future__ import annotations

from collections import defaultdict

from Models.Offre import Offre
from Models.Panier import LignePanier, ResultatPanier, TotalBoutique
from Models.Produit import Produit
from Services.comparaison_service import ORDRE_SOURCES, _rang_source

# Panier imposé par le sujet : (produit_id, quantité)
PANIER_RENTREE: list[tuple[str, int]] = [
    ("P04", 1),   # Tecno Spark 20
    ("P12", 1),   # Lenovo IdeaPad 3
    ("P14", 2),   # 2 clés USB SanDisk
    ("P15", 1),   # disque dur Seagate
    ("P28", 1),   # micro-ondes Samsung
]


def analyser_panier(offres: list[Offre],
                    produits: list[Produit]) -> ResultatPanier:
    """Calcule le coût du panier dans chaque boutique et la meilleure combinaison.

    Ici, chaque article est indépendant : acheter chaque article au prix le
    plus bas est donc optimal. Le coût de la combinaison est la somme des
    minima, et non le minimum des sommes.
    """
    catalogue = {produit.produit_id: produit for produit in produits}

    # produit_id -> source -> offre disponible
    offres_par_produit: dict[str, dict[str, Offre]] = defaultdict(dict)
    for offre in offres:
        if offre.produit_id and offre.prix_effectif is not None:
            existante = offres_par_produit[offre.produit_id].get(offre.source)
            if existante is None or offre.prix_effectif < existante.prix_effectif:
                offres_par_produit[offre.produit_id][offre.source] = offre

    lignes_optimales: list[LignePanier] = []
    total_optimal: int | None = 0

    for produit_id, quantite in PANIER_RENTREE:
        produit = catalogue.get(produit_id)
        nom = produit.nom if produit else produit_id
        offres_produit = offres_par_produit.get(produit_id, {})

        if not offres_produit:
            lignes_optimales.append(LignePanier(produit_id, nom, quantite))
            total_optimal = None
            continue

        # Meilleur prix pour cet article (égalité : ordre des sources)
        source_min = min(
            offres_produit,
            key=lambda source: (offres_produit[source].prix_effectif,
                                _rang_source(source)),
        )
        prix_unitaire = offres_produit[source_min].prix_effectif
        lignes_optimales.append(LignePanier(
            produit_id=produit_id,
            nom=nom,
            quantite=quantite,
            prix_unitaire=prix_unitaire,
            source=source_min,
            total=prix_unitaire * quantite,
        ))

        if total_optimal is not None:
            total_optimal += prix_unitaire * quantite

    # Coût si l'on achète tout dans une seule boutique
    totaux: list[TotalBoutique] = []
    for source in ORDRE_SOURCES:
        total = 0
        manquants: list[str] = []
        for produit_id, quantite in PANIER_RENTREE:
            produit = catalogue.get(produit_id)
            nom = produit.nom if produit else produit_id
            offre = offres_par_produit.get(produit_id, {}).get(source)
            if offre is None or offre.prix_effectif is None:
                manquants.append(nom)
            else:
                total += offre.prix_effectif * quantite

        complet = not manquants
        totaux.append(TotalBoutique(
            source=source,
            total=total if complet else None,
            complet=complet,
            manquants=manquants,
        ))

    # Meilleure boutique "tout en un" parmi celles qui ont tout le panier
    completes = [t for t in totaux if t.complet]
    if completes:
        meilleure = min(completes, key=lambda t: (t.total, _rang_source(t.source)))
        source_unique = meilleure.source
        total_unique = meilleure.total
    else:
        source_unique = None
        total_unique = None

    economie = None
    if total_optimal is not None and total_unique is not None:
        economie = total_unique - total_optimal

    return ResultatPanier(
        lignes=lignes_optimales,
        totaux=totaux,
        total_optimal=total_optimal,
        source_unique_moins_chere=source_unique,
        total_source_unique=total_unique,
        economie=economie,
    )
