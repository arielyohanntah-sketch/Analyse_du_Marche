"""Contrôleur principal : orchestre les services et les vues.

C'est le "C" du MVC. Il ne contient ni calcul métier (services) ni mise en
forme (vues) : il appelle les bons modules dans le bon ordre.
"""

from __future__ import annotations

from pathlib import Path

from Models.Analyse import ResultatAnalyse, ResultatBenchmark
from Models.Journal import Journal
from Services.benchmark_service import benchmark_historique
from Services.comparaison_service import comparer, exporter_comparatif_csv
from Services.csv_service import lire_catalogue, lire_marche_lagune
from Services.excel_service import lire_comptoir
from Services.historique import Historique
from Services.json_service import lire_baobab
from Services.matching_service import rapprocher_offres
from Services.normalisation_service import dedupliquer, normaliser_offre
from Services.panier_service import analyser_panier
from Views.Interface import Interface


class AnalyseController:
    def __init__(self, racine: str | Path | None = None):
        self.racine = Path(racine) if racine else Path(__file__).resolve().parent.parent
        self.data = self.racine / "data"
        self.reports = self.racine / "reports"
        self.vue = Interface()
        self.resultat: ResultatAnalyse | None = None

    # ------------------------------------------------------------------
    # Pipeline complet
    # ------------------------------------------------------------------
    def _verifier_fichiers(self) -> None:
        attendus = [
            "catalogue_reference.csv",
            "marche_lagune.csv",
            "baobab_shop.json",
            "comptoir_ivoire.xlsx",
            "historique_prix.csv",
        ]
        manquants = [nom for nom in attendus if not (self.data / nom).exists()]
        if manquants:
            raise FileNotFoundError(
                "Fichiers de données manquants dans data/ : "
                + ", ".join(manquants)
            )

    def executer(self) -> ResultatAnalyse:
        """Lance collecte → normalisation → rapprochement → comparaison."""
        self._verifier_fichiers()
        journal = Journal()

        # 1) Collecte
        produits = lire_catalogue(self.data / "catalogue_reference.csv", journal)
        offres = []
        offres += lire_marche_lagune(self.data / "marche_lagune.csv", journal)
        offres += lire_baobab(self.data / "baobab_shop.json", journal)
        offres += lire_comptoir(self.data / "comptoir_ivoire.xlsx", journal)

        # 2) Dédoublonnage puis normalisation
        # On dédoublonne avant de normaliser pour ne pas journaliser deux fois
        # les mêmes problèmes sur les lignes en double.
        offres = dedupliquer(offres, journal)
        for offre in offres:
            normaliser_offre(offre, journal)

        # 3) Rapprochement avec le catalogue
        rapprocher_offres(offres, produits, journal)

        # 4) Comparaison et synthèse
        comparaisons, synthese = comparer(offres, produits)

        # 5) Panier
        panier = analyser_panier(offres, produits)

        # 6) Historique
        historique_objet = Historique(self.data / "historique_prix.csv")
        historique = historique_objet.charger(journal)

        # 7) Complexité : recherche naïve contre recherche indexée
        benchmark = ResultatBenchmark(
            historique=[benchmark_historique(historique_objet, 500)],
            nb_requetes=500,
        )

        resultat = ResultatAnalyse(
            produits=produits,
            offres=offres,
            comparaisons=comparaisons,
            synthese=synthese,
            panier=panier,
            historique=historique,
            journal=journal,
            benchmark=benchmark,
        )

        # 8) Exports demandés par l'énoncé
        self.exporter(resultat)
        self.resultat = resultat
        return resultat

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------
    def exporter(self, resultat: ResultatAnalyse | None = None) -> None:
        """Écrit le journal de nettoyage et le comparatif CSV."""
        resultat = resultat or self.resultat
        if resultat is None:
            raise RuntimeError("Aucune analyse à exporter : lancez executer().")

        self.reports.mkdir(parents=True, exist_ok=True)
        resultat.journal.exporter_csv(self.reports / "journal_nettoyage.csv")
        exporter_comparatif_csv(
            resultat.comparaisons, self.reports / "comparatif.csv"
        )
