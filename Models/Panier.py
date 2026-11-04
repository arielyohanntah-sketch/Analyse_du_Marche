"""Modèles liés au panier de rentrée et à son optimisation."""

from dataclasses import dataclass, field


@dataclass
class LignePanier:
    produit_id: str
    nom: str
    quantite: int
    prix_unitaire: int | None = None
    source: str | None = None
    total: int | None = None


@dataclass
class TotalBoutique:
    source: str
    total: int | None            # None si le panier est incomplet
    complet: bool
    manquants: list[str] = field(default_factory=list)


@dataclass
class ResultatPanier:
    lignes: list[LignePanier]                 # achat article par article
    totaux: list[TotalBoutique]               # coût si tout est acheté dans une boutique
    total_optimal: int | None                 # somme des meilleurs prix
    source_unique_moins_chere: str | None     # meilleure boutique "tout en un"
    total_source_unique: int | None
    economie: int | None                      # économie du panier éclaté
