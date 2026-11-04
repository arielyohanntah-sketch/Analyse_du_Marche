"""Modèle représentant un produit du catalogue de référence.

Un Produit est un objet immuable (frozen=True) : une fois créé, on ne le
modifie plus. C'est le "socle commun" auquel on rattache les offres des
trois boutiques.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Produit:
    produit_id: str      # Exemple : "P04"
    nom: str             # Exemple : "Tecno Spark 20 128 Go"
    categorie: str       # Smartphone, Informatique, Électroménager
    marque: str          # Exemple : "Tecno"
