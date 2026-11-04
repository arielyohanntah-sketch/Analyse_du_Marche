"""Modèle représentant une offre (un article vendu par une boutique).

Le même objet sert à deux moments :
1. à la collecte : il contient les valeurs brutes lues dans le fichier ;
2. après normalisation : il contient le prix réellement payé, le nom nettoyé
   et, après rapprochement, l'identifiant du produit du catalogue.

Séparer "brut" et "nettoyé" permet de garder une trace de ce qui a été corrigé
et de l'expliquer dans le journal de nettoyage.
"""

from dataclasses import dataclass


@dataclass
class Offre:
    # --- Informations issues de la collecte (valeurs brutes) ---
    source: str
    reference: str
    designation_brute: str
    prix_source: str | int | float | None
    frais_livraison: int = 0
    remise_pct: float = 0.0
    ancien_prix_source: str | int | float | None = None
    stock: int | None = None
    disponible_source: bool = True
    note: float | None = None
    nb_avis: int | None = None

    # --- Informations calculées pendant la normalisation ---
    designation: str = ""              # nom propre, pour l'affichage
    designation_normalisee: str = ""   # nom canonique, pour le rapprochement
    prix_brut: int | None = None       # prix affiché, avant remise/livraison
    prix: int | None = None            # prix réellement payé (livraison incluse)
    disponible: bool = True            # disponible ET prix exploitable
    produit_id: str | None = None      # rempli par le service de rapprochement
    score_matching: float = 0.0
    methode_matching: str = ""

    @property
    def prix_effectif(self) -> int | None:
        """Prix utilisable dans la comparaison, ou None si l'offre est écartée.

        Une rupture de stock ou un prix absent ne doit jamais être retenu
        comme "le moins cher".
        """
        if not self.disponible:
            return None
        return self.prix
