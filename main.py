"""Point d'entrée du projet.

Exemples :
    python main.py              # analyse complète + rapports
    python main.py --menu       # menu interactif
    python main.py --no-benchmark
"""

from __future__ import annotations

import argparse
import sys

from Controllers.Analyse_Controller import AnalyseController


def configurer_console() -> None:
    """Force l'UTF-8 pour afficher correctement les accents sous Windows."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def main() -> int:
    configurer_console()

    parseur = argparse.ArgumentParser(
        description="Analyse comparative de marché — trois boutiques, un catalogue."
    )
    parseur.add_argument(
        "--menu", action="store_true",
        help="afficher le menu interactif après l'analyse",
    )
    parseur.add_argument(
        "--no-benchmark", action="store_true",
        help="ne pas mesurer les temps de recherche",
    )
    arguments = parseur.parse_args()

    controleur = AnalyseController()
    try:
        if arguments.menu:
            controleur.menu()
        else:
            resultat = controleur.executer(avec_benchmark=not arguments.no_benchmark)
            controleur.vue.afficher_resultat(resultat)
    except FileNotFoundError as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1
    except Exception as erreur:  # message clair pour l'utilisateur
        print(f"Erreur inattendue : {erreur}", file=sys.stderr)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
