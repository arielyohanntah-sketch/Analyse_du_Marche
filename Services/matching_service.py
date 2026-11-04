"""Rapprochement des offres avec le catalogue de référence.

Principe :
1. chaque nom est normalisé (voir normalisation_service) ;
2. on construit une signature : mots, marque, capacités (128gb, 1.5l, 1hp...)
   et modèles (a15, g9, i5, m185...) ;
3. un index inversé "mot -> produits candidats" évite de comparer chaque
   offre avec les 30 produits ;
4. des règles éliminent les faux candidats (marque différente, capacité
   différente, modèle différent) ;
5. un score de similarité choisit le meilleur candidat.

Complexité : O(n + m) pour construire l'index, puis O(n × k) pour le
rapprochement, où k est le nombre moyen de candidats (petit). La version
naïve serait O(n × m).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from Models.Journal import Journal
from Models.Offre import Offre
from Models.Produit import Produit
from Services.normalisation_service import (
    MARQUES,
    identifier_marque,
    normaliser_texte,
    tokeniser,
)

SEUIL_MATCH = 0.60
CAPACITE_RE = re.compile(r"^\d+(?:\.\d+)?(?:gb|tb|hp|l)$")
MODELE_RE = re.compile(r"^(?=.*[a-z])(?=.*\d).+$")


@dataclass
class Signature:
    tokens: set[str]
    marque: str | None
    marque_exacte: bool
    capacites: set[str]
    modeles: set[str]


def construire_signature(texte_normalise: str,
                         marque_connue: str | None = None) -> Signature:
    """Construit la signature d'un nom déjà normalisé."""
    tokens = tokeniser(texte_normalise)
    marque_detectee, exacte = identifier_marque(texte_normalise)
    marque = marque_connue or marque_detectee

    # On ajoute la forme canonique de la marque : cela permet de reconnaître
    # "Samsun" comme "Samsung" sans dépendre de l'orthographe exacte.
    if marque:
        for variante in MARQUES.get(marque, []):
            tokens.add(variante)

    capacites = {t for t in tokens if CAPACITE_RE.match(t)}
    modeles = {
        t for t in tokens
        if MODELE_RE.match(t) and t not in capacites
    }
    return Signature(tokens, marque, exacte, capacites, modeles)


def _incompatible(reference: Signature, offre: Signature) -> bool:
    """Vrai si une règle métier interdit le rapprochement."""
    # 1) Deux marques différentes ne peuvent pas être le même produit.
    if (reference.marque and offre.marque
            and reference.marque != offre.marque):
        return True

    # 2) Deux capacités différentes (128gb vs 256gb, 1hp vs 1.5hp...).
    if (reference.capacites and offre.capacites
            and not (reference.capacites & offre.capacites)):
        return True

    # 3) Deux modèles différents (a15 vs a25, i3 vs i5...).
    if (reference.modeles and offre.modeles
            and not (reference.modeles & offre.modeles)):
        return True

    return False


def _score(reference: Signature, offre: Signature) -> float:
    """Score entre 0 et 1 : recouvrement des mots + bonus de marque."""
    communs = reference.tokens & offre.tokens
    if not communs:
        return 0.0

    rappel = len(communs) / len(reference.tokens)
    precision = len(communs) / len(offre.tokens)
    f1 = 2 * rappel * precision / (rappel + precision)
    bonus_marque = 1.0 if (reference.marque and
                           reference.marque == offre.marque) else 0.0
    return min(1.0, 0.7 * f1 + 0.2 * rappel + 0.1 * bonus_marque)


class IndexCatalogue:
    """Index inversé mot -> indices des produits candidats."""

    def __init__(self, produits: list[Produit]):
        self.produits = produits
        self.signatures = [
            construire_signature(normaliser_texte(p.nom), p.marque)
            for p in produits
        ]
        self.index: dict[str, set[int]] = defaultdict(set)
        for position, signature in enumerate(self.signatures):
            for token in signature.tokens:
                self.index[token].add(position)

    def candidats(self, signature: Signature) -> set[int]:
        indices: set[int] = set()
        for token in signature.tokens:
            indices.update(self.index.get(token, set()))
        if not indices:
            # Aucun mot connu : on retombe sur une comparaison complète.
            return set(range(len(self.produits)))
        return indices


def rapprocher_offres(offres: list[Offre], produits: list[Produit],
                      journal: Journal) -> IndexCatalogue:
    """Associe chaque offre à un produit_id du catalogue.

    Les objets Offre sont modifiés sur place. L'index est retourné pour
    pouvoir être réutilisé (et mesuré dans le benchmark).
    """
    index = IndexCatalogue(produits)
    nb_reconnus = 0

    for offre in offres:
        signature_offre = construire_signature(offre.designation_normalisee)

        meilleur: Produit | None = None
        meilleur_score = 0.0
        second_score = 0.0
        meilleure_signature: Signature | None = None

        for position in index.candidats(signature_offre):
            produit = produits[position]
            signature_reference = index.signatures[position]

            if _incompatible(signature_reference, signature_offre):
                continue

            score = _score(signature_reference, signature_offre)
            if score > meilleur_score:
                second_score = meilleur_score
                meilleur_score = score
                meilleur = produit
                meilleure_signature = signature_reference
            elif score > second_score:
                second_score = score

        if meilleur is None or meilleur_score < SEUIL_MATCH:
            journal.ajouter(
                "RAPPROCHEMENT", offre.source, offre.reference,
                "aucun produit du catalogue ne correspond",
                "offre ignorée dans la comparaison",
                "AVERTISSEMENT",
            )
            continue

        offre.produit_id = meilleur.produit_id
        offre.score_matching = round(meilleur_score, 3)
        offre.methode_matching = (
            "exacte"
            if meilleure_signature is not None
            and meilleure_signature.tokens == signature_offre.tokens
            else "approximative"
        )
        nb_reconnus += 1

        if meilleur_score < 0.80:
            journal.ajouter(
                "RAPPROCHEMENT", offre.source, offre.reference,
                f"nom éloigné du catalogue (score {meilleur_score:.2f})",
                f"associé à {meilleur.produit_id} — {meilleur.nom}",
                "AVERTISSEMENT",
            )

        # Deux candidats très proches : on le signale pour vérification.
        if second_score >= meilleur_score - 0.05:
            journal.ajouter(
                "RAPPROCHEMENT", offre.source, offre.reference,
                f"correspondance ambiguë (meilleur {meilleur_score:.2f}, "
                f"second {second_score:.2f})",
                f"{meilleur.produit_id} retenu",
                "AVERTISSEMENT",
            )

    journal.ajouter(
        "RAPPROCHEMENT", "-", "-",
        f"{nb_reconnus}/{len(offres)} offres associées à un produit",
        "index inversé et score de similarité",
    )
    return index
