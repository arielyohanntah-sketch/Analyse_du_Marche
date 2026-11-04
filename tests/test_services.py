"""Tests unitaires des briques principales.

Lancement depuis la racine du projet :
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from Models.Journal import Journal
from Models.Offre import Offre
from Models.Produit import Produit
from Services.comparaison_service import comparer
from Services.historique import Historique
from Services.matching_service import rapprocher_offres
from Services.normalisation_service import (
    dedupliquer,
    identifier_marque,
    normaliser_offre,
    normaliser_texte,
    parser_prix,
)
from Services.panier_service import analyser_panier


def offre_test(source: str, produit_id: str, prix: int,
               disponible: bool = True) -> Offre:
    offre = Offre(
        source=source,
        reference=f"{source}-{produit_id}",
        designation_brute="produit test",
        prix_source=prix,
        disponible_source=disponible,
    )
    offre.prix = prix
    offre.disponible = disponible
    offre.produit_id = produit_id
    return offre


class TestNormalisation(unittest.TestCase):
    def test_parser_prix(self):
        self.assertEqual(parser_prix("102 900 FCFA"), 102900)
        self.assertEqual(parser_prix("279 300"), 279300)
        self.assertEqual(parser_prix("88 700 FCFA"), 88700)
        self.assertEqual(parser_prix(109400), 109400)
        self.assertIsNone(parser_prix("Prix sur demande"))
        self.assertIsNone(parser_prix(""))
        self.assertIsNone(parser_prix(None))

    def test_normaliser_texte(self):
        self.assertEqual(
            normaliser_texte("SAMSUNG GALAXY A15 (128GB)"),
            "samsung galaxy a15 128gb",
        )
        self.assertEqual(
            normaliser_texte("Clé USB SanDisk 64Go"),
            "usb sandisk 64gb",
        )
        self.assertEqual(
            normaliser_texte("DD externe Seagate 1To"),
            "disque dur seagate 1tb",
        )
        self.assertEqual(
            normaliser_texte("LG Air Conditioner 1HP"),
            "lg climatiseur 1hp",
        )

    def test_identifier_marque_avec_faute(self):
        marque, exacte = identifier_marque("samsun galaxy a15 128gb")
        self.assertEqual(marque, "Samsung")
        self.assertFalse(exacte)

    def test_prix_livraison_et_remise(self):
        journal = Journal()

        baobab = Offre(
            source="Baobab Shop", reference="B1", designation_brute="Test",
            prix_source=10000, frais_livraison=1500,
        )
        normaliser_offre(baobab, journal)
        self.assertEqual(baobab.prix, 11500)

        comptoir = Offre(
            source="Comptoir Ivoire", reference="C1", designation_brute="Test",
            prix_source=10000, remise_pct=10,
        )
        normaliser_offre(comptoir, journal)
        self.assertEqual(comptoir.prix, 9000)

    def test_prix_incoherent_ecarte(self):
        journal = Journal()
        offre = Offre(
            source="Marché Lagune", reference="M1",
            designation_brute="TECNO SPARK 20",
            prix_source="779 000 FCFA",
            ancien_prix_source="88 700 FCFA",
        )
        normaliser_offre(offre, journal)
        self.assertFalse(offre.disponible)
        self.assertIsNone(offre.prix)
        self.assertTrue(any("incohérent" in ligne.probleme
                            for ligne in journal.lignes))

    def test_dedoublonnage(self):
        journal = Journal()
        offres = [
            Offre("Marché Lagune", "ML-1", "A", "100 FCFA"),
            Offre("Marché Lagune", "ML-1", "A", "100 FCFA"),
        ]
        resultat = dedupliquer(offres, journal)
        self.assertEqual(len(resultat), 1)
        self.assertTrue(any("double" in ligne.probleme
                            for ligne in journal.lignes))


class TestMatchingEtComparaison(unittest.TestCase):
    def test_rapprochement(self):
        produits = [
            Produit("P04", "Tecno Spark 20 128 Go", "Smartphone", "Tecno"),
            Produit("P12", "Lenovo IdeaPad 3 Core i3 8 Go 256 Go",
                    "Informatique", "Lenovo"),
        ]
        offres = [
            Offre("Marché Lagune", "M1", "TECNO SPARK 20 - 128GB", "75 000 FCFA"),
            Offre("Baobab Shop", "B1", "Lenovo IdeaPad 3 (i3, 8GB, 256GB SSD)",
                  298200),
        ]
        journal = Journal()
        for offre in offres:
            normaliser_offre(offre, journal)
        rapprocher_offres(offres, produits, journal)
        self.assertEqual(offres[0].produit_id, "P04")
        self.assertEqual(offres[1].produit_id, "P12")

    def test_comparaison_et_produit_non_compare(self):
        produits = [
            Produit("P1", "Produit 1", "Test", "Marque"),
            Produit("P2", "Produit 2", "Test", "Marque"),
        ]
        offres = [
            offre_test("Marché Lagune", "P1", 100),
            offre_test("Baobab Shop", "P1", 150),
            offre_test("Comptoir Ivoire", "P1", 120),
            offre_test("Marché Lagune", "P2", 50),
        ]
        comparaisons, synthese = comparer(offres, produits)
        self.assertEqual(len(comparaisons), 1)
        ligne = comparaisons[0]
        self.assertEqual(ligne.meilleure_source, "Marché Lagune")
        self.assertEqual(ligne.prix_min, 100)
        self.assertEqual(ligne.prix_max, 150)
        self.assertEqual(ligne.ecart_fcfa, 50)
        self.assertEqual(ligne.ecart_pct, 50.0)
        self.assertEqual(synthese.nb_produits_compares, 1)
        self.assertEqual(len(synthese.produits_non_compares), 1)

    def test_panier(self):
        produits = [
            Produit(pid, pid, "Test", "Marque")
            for pid in ["P04", "P12", "P14", "P15", "P28"]
        ]
        prix = {
            "P04": (100, 90, 95),
            "P12": (200, 210, 180),
            "P14": (10, 12, 11),
            "P15": (50, 55, 52),
            "P28": (70, 65, 75),
        }
        sources = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]
        offres = []
        for produit_id, valeurs in prix.items():
            for source, valeur in zip(sources, valeurs):
                offres.append(offre_test(source, produit_id, valeur))

        panier = analyser_panier(offres, produits)
        # 90 + 180 + 2×10 + 50 + 65 = 405
        self.assertEqual(panier.total_optimal, 405)
        self.assertEqual(panier.source_unique_moins_chere, "Comptoir Ivoire")
        self.assertEqual(panier.total_source_unique, 424)
        self.assertEqual(panier.economie, 19)


class TestHistorique(unittest.TestCase):
    def test_moyenne_black_friday(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "historique.csv"
            with chemin.open("w", encoding="utf-8", newline="") as fichier:
                writer = csv.writer(fichier)
                writer.writerow(["date", "source", "produit_id", "prix_fcfa"])
                writer.writerow(["2025-11-25", "Baobab Shop", "P01", "100"])
                writer.writerow(["2025-11-26", "Baobab Shop", "P01", "80"])
                writer.writerow(["2026-01-01", "Baobab Shop", "P01", "120"])

            historique = Historique(chemin)
            resultat = historique.charger()
            stats = resultat.stats[0]
            self.assertEqual(resultat.nb_lignes, 3)
            self.assertAlmostEqual(stats.moyenne_annuelle, 100.0)
            self.assertAlmostEqual(stats.moyenne_black_friday, 90.0)
            self.assertAlmostEqual(stats.variation_pct, -10.0)
            self.assertEqual(
                len(historique.rechercher_naif("Baobab Shop", "P01")),
                len(historique.rechercher_index("Baobab Shop", "P01")),
            )


if __name__ == "__main__":
    unittest.main()
