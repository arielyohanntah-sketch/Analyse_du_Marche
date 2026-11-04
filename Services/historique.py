"""Chargement et analyse de l'historique des prix (20 876 lignes).

Deux structures sont construites en une seule lecture :
- par_source : source -> liste des relevés (pour les moyennes) ;
- par_cle    : (source, produit_id) -> liste des relevés (pour la recherche).

La recherche indexée est O(1) en moyenne, contre O(n) pour un parcours
complet de la liste. C'est le point central de la partie "complexité".
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from time import perf_counter

from Models.Historique import ResultatHistorique, StatsSource
from Models.Journal import Journal
from Services.comparaison_service import ORDRE_SOURCES
from Services.normalisation_service import normaliser_source, parser_prix


@dataclass(frozen=True)
class Releve:
    date: str          # AAAA-MM-JJ
    source: str
    produit_id: str
    prix: int


class Historique:
    def __init__(self, chemin: str | Path):
        self.chemin = Path(chemin)
        self.releves: list[Releve] = []
        self.par_source: dict[str, list[Releve]] = defaultdict(list)
        self.par_cle: dict[tuple[str, str], list[Releve]] = defaultdict(list)
        self.temps_chargement: float = 0.0

    def charger(self, journal: Journal | None = None) -> ResultatHistorique:
        """Lit le CSV une seule fois et construit les index."""
        debut = perf_counter()
        ignores = 0

        with self.chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
            lecteur = csv.DictReader(fichier)
            colonnes = set(lecteur.fieldnames or [])
            attendues = {"date", "source", "produit_id", "prix_fcfa"}
            if not attendues.issubset(colonnes):
                raise ValueError(
                    f"Historique invalide : colonnes manquantes "
                    f"{attendues - colonnes}"
                )

            for ligne in lecteur:
                date = (ligne.get("date") or "").strip()
                source = normaliser_source((ligne.get("source") or "").strip())
                produit_id = (ligne.get("produit_id") or "").strip()
                prix = parser_prix(ligne.get("prix_fcfa"))

                if len(date) != 10 or not produit_id or prix is None:
                    ignores += 1
                    continue

                releve = Releve(date, source, produit_id, prix)
                self.releves.append(releve)
                self.par_source[source].append(releve)
                self.par_cle[(source, produit_id)].append(releve)

        self.temps_chargement = perf_counter() - debut

        if journal is not None:
            journal.ajouter(
                "HISTORIQUE", "-", "-",
                f"{len(self.releves)} relevés lus, {ignores} ligne(s) ignorée(s)",
                f"index construit en {self.temps_chargement * 1000:.1f} ms",
            )

        return self.analyser()

    def analyser(self) -> ResultatHistorique:
        """Calcule, pour chaque enseigne, la moyenne annuelle et le Black Friday."""
        if not self.releves:
            return ResultatHistorique(temps_chargement=self.temps_chargement)

        sources = [s for s in ORDRE_SOURCES if s in self.par_source]
        sources += [s for s in self.par_source if s not in sources]

        stats: list[StatsSource] = []
        for source in sources:
            releves = self.par_source[source]
            moyenne_annuelle = mean(r.prix for r in releves)
            black_friday = [
                r for r in releves
                if "2025-11-24" <= r.date <= "2025-11-30"
            ]
            moyenne_bf = mean(r.prix for r in black_friday) if black_friday else 0.0
            variation = (
                (moyenne_bf - moyenne_annuelle) / moyenne_annuelle * 100
                if moyenne_annuelle else 0.0
            )

            releve_min = min(releves, key=lambda r: (r.prix, r.date))

            # Moyenne par mois, puis mois le moins cher.
            par_mois: dict[str, list[int]] = defaultdict(list)
            for releve in releves:
                par_mois[releve.date[:7]].append(releve.prix)
            moyennes_mois = {
                mois: mean(prix) for mois, prix in par_mois.items()
            }
            meilleur_mois = min(
                moyennes_mois, key=lambda mois: (moyennes_mois[mois], mois)
            )

            stats.append(StatsSource(
                source=source,
                moyenne_annuelle=round(moyenne_annuelle, 1),
                moyenne_black_friday=round(moyenne_bf, 1),
                variation_pct=round(variation, 2),
                nb_releves=len(releves),
                nb_releves_bf=len(black_friday),
                prix_min=releve_min.prix,
                date_prix_min=releve_min.date,
                meilleur_mois=meilleur_mois,
                moyenne_meilleur_mois=round(moyennes_mois[meilleur_mois], 1),
            ))

        return ResultatHistorique(
            stats=stats,
            debut=min(r.date for r in self.releves),
            fin=max(r.date for r in self.releves),
            nb_lignes=len(self.releves),
            temps_chargement=self.temps_chargement,
        )

    # --- Deux façons de chercher : c'est le support du benchmark ---------
    def rechercher_naif(self, source: str, produit_id: str) -> list[Releve]:
        """Parcours complet : O(n) par requête."""
        return [
            r for r in self.releves
            if r.source == source and r.produit_id == produit_id
        ]

    def rechercher_index(self, source: str, produit_id: str) -> list[Releve]:
        """Dictionnaire : O(1) en moyenne par requête."""
        return self.par_cle.get((source, produit_id), [])
