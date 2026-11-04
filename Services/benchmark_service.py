"""Mesure du temps de recherche dans l'historique des prix.

L'énoncé demande de chercher des prix dans un historique de plus de
20 000 lignes et de mesurer le temps. On compare deux approches pour la
même opération :
- parcours complet de la liste : O(q × n) ;
- index en mémoire (dict) : O(q), avec O(n) de construction.

Les mesures sont refaites à chaque exécution, sur la machine de l'étudiant.
"""

from __future__ import annotations

import random
from time import perf_counter

from Models.Analyse import MesureBenchmark
from Services.historique import Historique


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
