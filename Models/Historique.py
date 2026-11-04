"""Modèles de la partie historique des prix."""

from dataclasses import dataclass, field


@dataclass
class StatsSource:
    source: str
    moyenne_annuelle: float
    moyenne_black_friday: float
    variation_pct: float          # négatif = moins cher pendant le Black Friday
    nb_releves: int
    nb_releves_bf: int
    prix_min: int
    date_prix_min: str
    meilleur_mois: str            # "2025-11", "2026-03", ...
    moyenne_meilleur_mois: float


@dataclass
class ResultatHistorique:
    stats: list[StatsSource] = field(default_factory=list)
    debut: str = ""
    fin: str = ""
    nb_lignes: int = 0
    temps_chargement: float = 0.0
