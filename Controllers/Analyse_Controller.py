"""Contrôleur principal : orchestre les services et les vues.

C'est le "C" du MVC. Il ne contient ni calcul métier (services) ni mise en
forme (vues) : il appelle les bons modules dans le bon ordre et mesure les
temps de chaque étape.
"""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

from Models.Analyse import ResultatAnalyse, ResultatBenchmark
from Models.Journal import Journal
from Services.benchmark_service import (
    benchmark_correspondance,
    benchmark_historique,
)
from Services.comparaison_service import comparer, exporter_comparatif_csv
from Services.csv_service import lire_catalogue, lire_marche_lagune
from Services.excel_service import lire_comptoir
from Services.historique import Historique
from Services.json_service import lire_baobab
from Services.matching_service import rapprocher_offres
from Services.normalisation_service import dedupliquer, normaliser_offre
from Services.panier_service import analyser_panier
from Views.Interface import Interface
from Views.html_view import generer as generer_html


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

    def executer(self, avec_benchmark: bool = True) -> ResultatAnalyse:
        """Lance collecte → normalisation → rapprochement → comparaison."""
        self._verifier_fichiers()
        debut_total = perf_counter()
        temps: dict[str, float] = {}
        journal = Journal()

        # 1) Collecte
        debut = perf_counter()
        produits = lire_catalogue(self.data / "catalogue_reference.csv", journal)
        offres = []
        offres += lire_marche_lagune(self.data / "marche_lagune.csv", journal)
        offres += lire_baobab(self.data / "baobab_shop.json", journal)
        offres += lire_comptoir(self.data / "comptoir_ivoire.xlsx", journal)
        temps["collecte"] = perf_counter() - debut

        # 2) Dédoublonnage puis normalisation
        # On dédoublonne avant de normaliser pour ne pas journaliser deux fois
        # les mêmes problèmes sur les lignes en double.
        debut = perf_counter()
        offres = dedupliquer(offres, journal)
        for offre in offres:
            normaliser_offre(offre, journal)
        temps["normalisation"] = perf_counter() - debut

        # 3) Rapprochement avec le catalogue
        debut = perf_counter()
        rapprocher_offres(offres, produits, journal)
        temps["rapprochement"] = perf_counter() - debut

        # 4) Comparaison et synthèse
        debut = perf_counter()
        comparaisons, synthese = comparer(offres, produits)
        temps["comparaison"] = perf_counter() - debut

        # 5) Panier
        debut = perf_counter()
        panier = analyser_panier(offres, produits)
        temps["panier"] = perf_counter() - debut

        # 6) Historique
        debut = perf_counter()
        historique_objet = Historique(self.data / "historique_prix.csv")
        historique = historique_objet.charger(journal)
        temps["historique"] = perf_counter() - debut

        # 7) Benchmark (facultatif mais activé par défaut)
        benchmark = None
        if avec_benchmark:
            debut = perf_counter()
            benchmark = ResultatBenchmark(
                historique=[benchmark_historique(historique_objet, 500)],
                correspondance=benchmark_correspondance(produits),
                nb_requetes=500,
            )
            temps["benchmark"] = perf_counter() - debut

        resultat = ResultatAnalyse(
            produits=produits,
            offres=offres,
            comparaisons=comparaisons,
            synthese=synthese,
            panier=panier,
            historique=historique,
            journal=journal,
            temps=temps,
            benchmark=benchmark,
        )

        # 8) Exports
        # On écrit d'abord les CSV, puis on mesure l'export et le total.
        # Le HTML est généré en dernier : il peut ainsi afficher tous les temps.
        debut = perf_counter()
        self.exporter(resultat, html=False)
        temps["export"] = perf_counter() - debut
        temps["total"] = perf_counter() - debut_total
        generer_html(resultat, self.reports / "rapport.html")

        self.resultat = resultat
        return resultat

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------
    def exporter(self, resultat: ResultatAnalyse | None = None,
                 *, html: bool = True) -> None:
        """Écrit le journal, le comparatif CSV et, si demandé, le rapport HTML.

        Le paramètre ``html=False`` sert au pipeline principal : il génère le
        HTML après avoir mesuré ``export`` et ``total``, pour que le rapport
        affiche ces deux temps.
        """
        resultat = resultat or self.resultat
        if resultat is None:
            raise RuntimeError("Aucune analyse à exporter : lancez executer().")

        self.reports.mkdir(parents=True, exist_ok=True)
        resultat.journal.exporter_csv(self.reports / "journal_nettoyage.csv")
        exporter_comparatif_csv(
            resultat.comparaisons, self.reports / "comparatif.csv"
        )
        if html:
            generer_html(resultat, self.reports / "rapport.html")

    # ------------------------------------------------------------------
    # Menu interactif
    # ------------------------------------------------------------------
    def menu(self) -> None:
        resultat = self.executer()
        self.vue.afficher_resultat(resultat)

        while True:
            choix = self.vue.menu_principal()
            if choix == "1":
                self.vue.afficher_resultat(resultat)
            elif choix == "2":
                self.vue.afficher_comparatif(resultat)
            elif choix == "3":
                self.vue.afficher_synthese(resultat)
            elif choix == "4":
                self.vue.afficher_panier(resultat.panier)
            elif choix == "5":
                self.vue.afficher_historique(resultat.historique)
            elif choix == "6":
                self.vue.afficher_journal(resultat.journal, details=True)
            elif choix == "7":
                self.vue.afficher_benchmark(resultat)
            elif choix == "8":
                self.exporter(resultat)
                print("Rapport HTML, CSV comparatif et journal régénérés.")
            elif choix == "9":
                print("À bientôt.")
                break
            else:
                print("Choix invalide : tapez un chiffre entre 1 et 9.")
