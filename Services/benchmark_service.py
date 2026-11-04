"""Mesures de temps : recherche historique et recherche dans un catalogue.

On mesure deux approches pour la même opération :
- parcours complet (boucle) : O(q × n) ;
- index en mémoire (dict) : O(q), avec O(n) de construction.

Les mesures sont refaites à chaque exécution, sur la machine de l'étudiant.
"""

from __future__ import annotations

import random
from time import perf_counter

from Models.Analyse import MesureBenchmark
from Models.Produit import Produit
from Services.historique import Historique
from Services.normalisation_service import normaliser_texte


def benchmark_historique(historique: Historique,
                         nb_requetes: int = 500) -> MesureBenchmark:
    """Compare la recherche naïve et la recherche indexée dans l'historique."""
    cles = list(historique.par_cle.keys())
    if not cles:
        return MesureBenchmark(
            "Recherche dans l'historique", 0, 0.0, 0.0,
            "O(q × n)", "O(q)",
        )

    generateur = random.Random(42)
    # On tire nb_requetes clés (avec répétition possible) pour avoir un
    # nombre de requêtes constant, même s'il y a peu de couples source/produit.
    cles = generateur.choices(cles, k=nb_requetes)

    debut = perf_counter()
    for source, produit_id in cles:
        historique.rechercher_naif(source, produit_id)
    temps_naif = perf_counter() - debut

    debut = perf_counter()
    for source, produit_id in cles:
        historique.rechercher_index(source, produit_id)
    temps_index = perf_counter() - debut

    return MesureBenchmark(
        libelle="Recherche dans l'historique",
        taille=len(historique.releves),
        temps_naif=temps_naif,
        temps_index=temps_index,
        complexite_naive="O(q × n)",
        complexite_index="O(q)",
    )


def _catalogue_synthetique(produits: list[Produit], taille: int) -> list[Produit]:
    """Répète les produits réels avec un numéro unique pour créer N produits."""
    resultat: list[Produit] = []
    for index in range(taille):
        modele = produits[index % len(produits)]
        resultat.append(Produit(
            produit_id=f"X{index:06d}",
            nom=f"{modele.nom} serie {index}",
            categorie=modele.categorie,
            marque=modele.marque,
        ))
    return resultat


def benchmark_correspondance(produits: list[Produit],
                             tailles: tuple[int, ...] = (1000, 5000, 20000),
                             nb_requetes: int = 100) -> list[MesureBenchmark]:
    """Compare la recherche par nom : boucle O(q×n) contre dict O(q).

    Ce benchmark illustre le principe de l'index inversé utilisé dans le
    rapprochement réel : au lieu de parcourir tout le catalogue, on va
    directement aux candidats.
    """
    mesures: list[MesureBenchmark] = []

    for taille in tailles:
        catalogue = _catalogue_synthetique(produits, taille)
        # On normalise une seule fois les noms : la comparaison porte bien
        # sur la structure de recherche, pas sur le coût de normalisation.
        noms = [(normaliser_texte(p.nom), p) for p in catalogue]
        generateur = random.Random(42)
        positions = generateur.sample(
            range(taille), min(nb_requetes, taille)
        )
        requetes = [noms[i][0] for i in positions]

        # Version naïve : pour chaque requête, on parcourt le catalogue.
        debut = perf_counter()
        for nom_cherche in requetes:
            trouve = None
            for nom, produit in noms:
                if nom == nom_cherche:
                    trouve = produit
                    break
            _ = trouve
        temps_naif = perf_counter() - debut

        # Version indexée : on construit un dictionnaire une fois.
        debut = perf_counter()
        index = {nom: p for nom, p in noms}
        for nom_cherche in requetes:
            _ = index.get(nom_cherche)
        temps_index = perf_counter() - debut

        mesures.append(MesureBenchmark(
            libelle=f"Recherche par nom ({taille} produits)",
            taille=taille,
            temps_naif=temps_naif,
            temps_index=temps_index,
            complexite_naive="O(q × n)",
            complexite_index="O(q) après O(n)",
        ))

    return mesures
