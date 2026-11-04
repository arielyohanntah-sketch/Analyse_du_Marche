"""Modèles produits par l'analyse comparative et par les benchmarks."""

from dataclasses import dataclass, field

from Models.Produit import Produit
from Models.Offre import Offre
from Models.Panier import ResultatPanier
from Models.Historique import ResultatHistorique
from Models.Journal import Journal


@dataclass
class LigneComparaison:
    produit: Produit
    prix_par_source: dict[str, int]       # boutique -> prix payé
    sources_min: list[str]                # une ou plusieurs boutiques à égalité
    meilleure_source: str                 # choix affiché (première de sources_min)
    prix_min: int
    prix_max: int
    ecart_fcfa: int                       # prix_max - prix_min
    ecart_pct: float                      # (prix_max - prix_min) / prix_min * 100
    surcouts: dict[str, int]              # boutique -> prix - prix_min
    nombre_sources: int


@dataclass
class ProduitNonCompare:
    produit: Produit
    raison: str
    sources_disponibles: list[str] = field(default_factory=list)


@dataclass
class Synthese:
    nb_produits_compares: int
    victoires: dict[str, int]          # égalités comprises
    nb_egalites: int
    surcout_moyen_pct: dict[str, float]
    top_gains_fcfa: list[LigneComparaison]
    top_ecarts_pct: list[LigneComparaison]
    produits_non_compares: list[ProduitNonCompare]


@dataclass
class MesureBenchmark:
    libelle: str
    taille: int
    temps_naif: float
    temps_index: float
    complexite_naive: str
    complexite_index: str


@dataclass
class ResultatBenchmark:
    historique: list[MesureBenchmark] = field(default_factory=list)
    correspondance: list[MesureBenchmark] = field(default_factory=list)
    nb_requetes: int = 0


@dataclass
class ResultatAnalyse:
    produits: list[Produit]
    offres: list[Offre]
    comparaisons: list[LigneComparaison]
    synthese: Synthese
    panier: ResultatPanier
    historique: ResultatHistorique
    journal: Journal
    temps: dict[str, float] = field(default_factory=dict)
    benchmark: ResultatBenchmark | None = None
