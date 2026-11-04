"""Comparaison des prix et construction de la synthèse."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from Models.Analyse import (
    LigneComparaison,
    ProduitNonCompare,
    Synthese,
)
from Models.Offre import Offre
from Models.Produit import Produit

ORDRE_SOURCES = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]
SEUIL_ALERTE_PCT = 10.0


def _rang_source(source: str) -> int:
    try:
        return ORDRE_SOURCES.index(source)
    except ValueError:
        return len(ORDRE_SOURCES)


def comparer(offres: list[Offre],
             produits: list[Produit]) -> tuple[list[LigneComparaison], Synthese]:
    """Compare les offres disponibles et produit le rapport + la synthèse.

    Règle : un produit n'est comparé que s'il est disponible dans au moins
    deux boutiques avec un prix exploitable.
    """
    # 1) Regrouper en O(n) : produit_id -> {source -> offre}
    par_produit: dict[str, dict[str, Offre]] = defaultdict(dict)
    for offre in offres:
        if not offre.produit_id or offre.prix_effectif is None:
            continue
        existante = par_produit[offre.produit_id].get(offre.source)
        # Si une même boutique propose deux fois le même produit, on garde
        # l'offre la moins chère.
        if existante is None or offre.prix_effectif < existante.prix_effectif:
            par_produit[offre.produit_id][offre.source] = offre

    comparaisons: list[LigneComparaison] = []
    non_compares: list[ProduitNonCompare] = []

    # 2) Parcours du catalogue (30 produits) : O(m)
    for produit in produits:
        offres_produit = par_produit.get(produit.produit_id, {})

        if len(offres_produit) < 2:
            sources = sorted(offres_produit, key=_rang_source)
            if not sources:
                raison = ("aucune offre disponible : rupture, prix absent "
                          "ou produit non vendu")
            else:
                raison = "une seule boutique disponible : rien à comparer"
            non_compares.append(ProduitNonCompare(produit, raison, sources))
            continue

        prix_par_source = {
            source: offre.prix_effectif
            for source, offre in offres_produit.items()
        }
        prix_par_source = dict(
            sorted(prix_par_source.items(), key=lambda item: _rang_source(item[0]))
        )

        prix_min = min(prix_par_source.values())
        prix_max = max(prix_par_source.values())
        sources_min = [
            source for source, prix in prix_par_source.items()
            if prix == prix_min
        ]
        ecart_fcfa = prix_max - prix_min
        ecart_pct = round(ecart_fcfa / prix_min * 100, 1) if prix_min else 0.0

        comparaisons.append(LigneComparaison(
            produit=produit,
            prix_par_source=prix_par_source,
            sources_min=sources_min,
            meilleure_source=sources_min[0],
            prix_min=prix_min,
            prix_max=prix_max,
            ecart_fcfa=ecart_fcfa,
            ecart_pct=ecart_pct,
            surcouts={
                source: prix - prix_min
                for source, prix in prix_par_source.items()
            },
            nombre_sources=len(prix_par_source),
        ))

    # 3) Synthèse
    victoires = {source: 0 for source in ORDRE_SOURCES}
    nb_egalites = 0
    for ligne in comparaisons:
        for source in ligne.sources_min:
            victoires[source] = victoires.get(source, 0) + 1
        if len(ligne.sources_min) > 1:
            nb_egalites += 1

    surcout_moyen: dict[str, float] = {}
    for source in ORDRE_SOURCES:
        ecarts = [
            (ligne.prix_par_source[source] - ligne.prix_min) / ligne.prix_min * 100
            for ligne in comparaisons
            if source in ligne.prix_par_source
        ]
        surcout_moyen[source] = round(sum(ecarts) / len(ecarts), 2) if ecarts else 0.0

    top_gains = sorted(
        comparaisons, key=lambda ligne: ligne.ecart_fcfa, reverse=True
    )[:3]
    top_ecarts = sorted(
        comparaisons, key=lambda ligne: ligne.ecart_pct, reverse=True
    )[:3]

    # Le tableau principal est trié par écart décroissant : les plus gros
    # écarts, donc les décisions les plus intéressantes, apparaissent en haut.
    comparaisons.sort(key=lambda ligne: ligne.ecart_pct, reverse=True)

    synthese = Synthese(
        nb_produits_compares=len(comparaisons),
        victoires=victoires,
        nb_egalites=nb_egalites,
        surcout_moyen_pct=surcout_moyen,
        top_gains_fcfa=top_gains,
        top_ecarts_pct=top_ecarts,
        produits_non_compares=non_compares,
    )
    return comparaisons, synthese


def exporter_comparatif_csv(comparaisons: list[LigneComparaison],
                            chemin: str | Path) -> None:
    """Exporte le tableau comparatif dans un CSV lisible par Excel."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    with chemin.open("w", encoding="utf-8-sig", newline="") as fichier:
        writer = csv.writer(fichier, delimiter=";")
        entetes = [
            "produit_id", "produit", "categorie", "marque",
            "meilleure_boutique", "prix_min", "prix_max",
            "ecart_fcfa", "ecart_pct", "alerte", "nb_boutiques",
        ]
        entetes += [f"prix_{source}" for source in ORDRE_SOURCES]
        writer.writerow(entetes)

        for ligne in comparaisons:
            writer.writerow([
                ligne.produit.produit_id,
                ligne.produit.nom,
                ligne.produit.categorie,
                ligne.produit.marque,
                " / ".join(ligne.sources_min),
                ligne.prix_min,
                ligne.prix_max,
                ligne.ecart_fcfa,
                ligne.ecart_pct,
                "OUI" if ligne.ecart_pct >= SEUIL_ALERTE_PCT else "NON",
                ligne.nombre_sources,
                *[ligne.prix_par_source.get(source, "") for source in ORDRE_SOURCES],
            ])
