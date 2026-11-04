"""Vue console : tout l'affichage texte de l'application.

Cette classe ne calcule rien. Elle reçoit des objets déjà calculés par le
contrôleur et les met en forme. C'est le "V" du MVC.
"""

from __future__ import annotations

from Models.Analyse import ResultatAnalyse
from Models.Historique import ResultatHistorique
from Models.Journal import Journal
from Models.Panier import ResultatPanier
from Models.Produit import Produit
from Models.Offre import Offre

NOMS_COURTS = {
    "Marché Lagune": "Marché",
    "Baobab Shop": "Baobab",
    "Comptoir Ivoire": "Comptoir",
}
LARGEUR = 78


def fcfa(montant: int | float | None) -> str:
    if montant is None:
        return "-"
    return f"{montant:,.0f}".replace(",", " ") + " FCFA"


def pourcent(valeur: float | None) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:.1f}".replace(".", ",") + " %"


def duree(secondes: float | None) -> str:
    if secondes is None:
        return "-"
    if secondes < 0.001:
        return f"{secondes * 1_000_000:.0f} µs"
    if secondes < 1:
        return f"{secondes * 1000:.2f} ms"
    return f"{secondes:.2f} s"


class Interface:
    # ------------------------------------------------------------------
    # Outils d'affichage
    # ------------------------------------------------------------------
    def titre(self, texte: str) -> None:
        print()
        print("=" * LARGEUR)
        print(texte.center(LARGEUR))
        print("=" * LARGEUR)

    def sous_titre(self, texte: str) -> None:
        print()
        print("-" * LARGEUR)
        print(texte)
        print("-" * LARGEUR)

    def tableau(self, entetes: list[str], lignes: list[list[str]]) -> None:
        largeurs = [len(entete) for entete in entetes]
        for ligne in lignes:
            for index, cellule in enumerate(ligne):
                largeurs[index] = max(largeurs[index], len(str(cellule)))

        separateur = "+" + "+".join("-" * (largeur + 2) for largeur in largeurs) + "+"
        print(separateur)
        print("| " + " | ".join(
            entete.ljust(largeur)
            for entete, largeur in zip(entetes, largeurs)
        ) + " |")
        print(separateur)
        for ligne in lignes:
            print("| " + " | ".join(
                str(cellule).ljust(largeur)
                for cellule, largeur in zip(ligne, largeurs)
            ) + " |")
        print(separateur)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------
    def afficher_entete(self, resultat: ResultatAnalyse) -> None:
        self.titre("ANALYSE COMPARATIVE DE MARCHÉ")
        print("Trois boutiques, un même catalogue, des prix différents.")
        print(f"Produits de référence : {len(resultat.produits)}")
        print(f"Offres collectées     : {len(resultat.offres)}")
        print(f"Produits comparés     : {resultat.synthese.nb_produits_compares}")
        print()
        print("Sources : Marché Lagune (CSV) · Baobab Shop (JSON) · "
              "Comptoir Ivoire (Excel)")

    def afficher_collecte(self, offres: list[Offre]) -> None:
        self.sous_titre("1. COLLECTE ET RAPPROCHEMENT")
        lignes = []
        for source in ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]:
            offres_source = [o for o in offres if o.source == source]
            disponibles = sum(1 for o in offres_source if o.disponible)
            reconnues = sum(1 for o in offres_source if o.produit_id)
            lignes.append([
                source,
                str(len(offres_source)),
                str(disponibles),
                str(reconnues),
            ])
        self.tableau(
            ["Boutique", "Offres", "Disponibles", "Rapprochées"],
            lignes,
        )
        print("Une offre est 'disponible' si elle a un prix exploitable et "
              "n'est pas en rupture.")

    def afficher_journal(self, journal: Journal, details: bool = False) -> None:
        self.sous_titre("2. JOURNAL DE NETTOYAGE")
        compteur = journal.compter()
        print(f"INFO : {compteur['INFO']}  |  "
              f"AVERTISSEMENTS : {compteur['AVERTISSEMENT']}  |  "
              f"ERREURS : {compteur['ERREUR']}")

        a_afficher = [
            ligne for ligne in journal.lignes
            if details or ligne.gravite in ("AVERTISSEMENT", "ERREUR")
        ]
        if not a_afficher:
            print("Aucun avertissement : les données étaient propres.")
            return

        niveaux = {"INFO": "INFO", "AVERTISSEMENT": "ATT", "ERREUR": "ERR"}
        lignes = []
        for ligne in a_afficher:
            lignes.append([
                niveaux.get(ligne.gravite, ligne.gravite),
                ligne.source[:16],
                ligne.reference[:10],
                (ligne.probleme[:45] + "...") if len(ligne.probleme) > 48
                else ligne.probleme,
            ])
        self.tableau(["Niv.", "Source", "Réf.", "Problème"], lignes)
        print("Le journal complet est exporté dans reports/journal_nettoyage.csv")

    def afficher_comparatif(self, resultat: ResultatAnalyse) -> None:
        self.sous_titre("3. COMPARATIF DES PRIX")
        lignes = []
        for ligne in resultat.comparaisons:
            meilleure = " + ".join(
                NOMS_COURTS.get(source, source) for source in ligne.sources_min
            )
            nom = ligne.produit.nom
            if len(nom) > 32:
                nom = nom[:29] + "..."
            lignes.append([
                ligne.produit.produit_id,
                nom,
                meilleure,
                fcfa(ligne.prix_min),
                fcfa(ligne.prix_max),
                fcfa(ligne.ecart_fcfa),
                pourcent(ligne.ecart_pct),
                "OUI" if ligne.ecart_pct >= 10 else "-",
            ])
        self.tableau(
            ["ID", "Produit", "Meilleure", "Prix min", "Prix max",
             "Écart FCFA", "Écart %", "Alerte"],
            lignes,
        )
        print("Écart = prix max − prix min : c'est la marge réalisée en "
              "évitant la boutique la plus chère.")
        print("Alerte = écart supérieur ou égal à 10 % : à surveiller.")

    def afficher_synthese(self, resultat: ResultatAnalyse) -> None:
        synthese = resultat.synthese
        self.sous_titre("4. SYNTHÈSE ET DÉCISION")

        print("Nombre de fois où chaque boutique est la moins chère "
              "(égalités comprises) :")
        for source in sorted(
            synthese.victoires, key=lambda s: synthese.victoires[s], reverse=True
        ):
            print(f"  {source:<18} : {synthese.victoires[source]:>2} produit(s)")
        print(f"  Dont {synthese.nb_egalites} égalité(s) entre boutiques.")

        print()
        print("Écart moyen de chaque boutique par rapport au prix le plus bas :")
        for source in sorted(
            synthese.surcout_moyen_pct, key=lambda s: synthese.surcout_moyen_pct[s]
        ):
            print(f"  {source:<18} : {pourcent(synthese.surcout_moyen_pct[source])}")

        print()
        print("Top 3 des marges potentielles en FCFA (où il y a le plus à gagner) :")
        for ligne in synthese.top_gains_fcfa:
            print(f"  {ligne.produit.produit_id} {ligne.produit.nom[:38]:<38} "
                  f"→ {fcfa(ligne.ecart_fcfa)} d'écart")

        print()
        print("Top 3 des écarts relatifs (les plus gros pourcentages) :")
        for ligne in synthese.top_ecarts_pct:
            print(f"  {ligne.produit.produit_id} {ligne.produit.nom[:38]:<38} "
                  f"→ {pourcent(ligne.ecart_pct)}")

        if synthese.produits_non_compares:
            print()
            print("Produits non comparés (moins de deux boutiques disponibles) :")
            for non_compare in synthese.produits_non_compares:
                print(f"  {non_compare.produit.produit_id} "
                      f"{non_compare.produit.nom[:42]:<42} : {non_compare.raison}")

    def afficher_panier(self, panier: ResultatPanier) -> None:
        self.sous_titre("5. PANIER DE RENTRÉE")
        lignes = []
        for total in panier.totaux:
            if total.complet:
                lignes.append([
                    total.source,
                    fcfa(total.total),
                    "complet",
                ])
            else:
                manque = ", ".join(total.manquants)
                lignes.append([
                    total.source,
                    "INCOMPLET",
                    manque[:45],
                ])
        self.tableau(["Boutique", "Coût du panier", "Détail"], lignes)

        print()
        print("Meilleure combinaison : acheter chaque article là où il est "
              "le moins cher.")
        lignes = []
        for ligne in panier.lignes:
            lignes.append([
                ligne.produit_id,
                ligne.nom[:30],
                str(ligne.quantite),
                NOMS_COURTS.get(ligne.source or "", ligne.source or "-"),
                fcfa(ligne.prix_unitaire),
                fcfa(ligne.total),
            ])
        self.tableau(
            ["ID", "Produit", "Qté", "Boutique", "Prix unit.", "Total"],
            lignes,
        )
        print(f"Total de la combinaison : {fcfa(panier.total_optimal)}")
        print(f"Meilleure boutique unique : {panier.source_unique_moins_chere} "
              f"({fcfa(panier.total_source_unique)})")
        print(f"Économie réalisée : {fcfa(panier.economie)}")

    def afficher_historique(self, historique: ResultatHistorique) -> None:
        self.sous_titre("6. HISTORIQUE : QUAND FALLAIT-IL ACHETER ?")
        print(f"Période : {historique.debut} → {historique.fin} "
              f"({historique.nb_lignes} relevés)")
        lignes = []
        for stats in historique.stats:
            lignes.append([
                stats.source,
                fcfa(stats.moyenne_annuelle),
                fcfa(stats.moyenne_black_friday),
                pourcent(stats.variation_pct),
                stats.meilleur_mois,
                fcfa(stats.moyenne_meilleur_mois),
            ])
        self.tableau(
            ["Boutique", "Moyenne annuelle", "Black Friday", "Variation",
             "Meilleur mois", "Prix moyen"],
            lignes,
        )
        print("Variation négative = le Black Friday était moins cher que "
              "la moyenne de l'année.")
        for stats in historique.stats:
            if stats.variation_pct < 0:
                print(f"  {stats.source} : Black Friday plus intéressant "
                      f"de {pourcent(abs(stats.variation_pct))}.")
            else:
                print(f"  {stats.source} : Black Friday plus cher "
                      f"de {pourcent(stats.variation_pct)} ; "
                      f"le meilleur mois était {stats.meilleur_mois}.")

    def afficher_benchmark(self, resultat: ResultatAnalyse) -> None:
        if resultat.benchmark is None:
            return
        self.sous_titre("7. COMPLEXITÉ : TEMPS MESURÉS")
        for titre, mesures in [
            ("Recherche dans l'historique", resultat.benchmark.historique),
            ("Recherche dans un catalogue", resultat.benchmark.correspondance),
        ]:
            if not mesures:
                continue
            print()
            print(titre + " :")
            lignes = []
            for mesure in mesures:
                acceleration = (
                    mesure.temps_naif / mesure.temps_index
                    if mesure.temps_index > 0 else 0
                )
                lignes.append([
                    mesure.libelle,
                    mesure.complexite_naive,
                    duree(mesure.temps_naif),
                    mesure.complexite_index,
                    duree(mesure.temps_index),
                    f"×{acceleration:.0f}",
                ])
            self.tableau(
                ["Opération", "Complexité naïve", "Temps naïf",
                 "Complexité index", "Temps index", "Gain"],
                lignes,
            )
        print("Le benchmark est refait à chaque exécution sur cette machine.")

    def afficher_temps(self, resultat: ResultatAnalyse) -> None:
        numero = "8" if resultat.benchmark is not None else "7"
        self.sous_titre(f"{numero}. TEMPS D'EXÉCUTION PAR ÉTAPE")
        lignes = [
            [etape, duree(temps)]
            for etape, temps in resultat.temps.items()
        ]
        self.tableau(["Étape", "Temps"], lignes)

    def afficher_resultat(self, resultat: ResultatAnalyse) -> None:
        self.afficher_entete(resultat)
        self.afficher_collecte(resultat.offres)
        self.afficher_journal(resultat.journal)
        self.afficher_comparatif(resultat)
        self.afficher_synthese(resultat)
        self.afficher_panier(resultat.panier)
        self.afficher_historique(resultat.historique)
        self.afficher_benchmark(resultat)
        self.afficher_temps(resultat)
        print()
        print("Rapports générés :")
        print("  reports/comparatif.csv")
        print("  reports/journal_nettoyage.csv")
        print("  reports/rapport.html")

    # ------------------------------------------------------------------
    # Menu interactif
    # ------------------------------------------------------------------
    def menu_principal(self) -> str:
        print()
        print("=" * LARGEUR)
        print("MENU".center(LARGEUR))
        print("=" * LARGEUR)
        print("1. Afficher tout le rapport")
        print("2. Comparatif des prix")
        print("3. Synthèse et décision")
        print("4. Panier de rentrée")
        print("5. Historique des prix")
        print("6. Journal de nettoyage complet")
        print("7. Benchmark de complexité")
        print("8. Régénérer le rapport HTML")
        print("9. Quitter")
        return input("Votre choix : ").strip()
