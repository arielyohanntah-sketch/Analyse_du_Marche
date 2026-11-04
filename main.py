"""Point d'entrée du projet.

Lancement :
    python main.py
"""

from __future__ import annotations

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

    controleur = AnalyseController()
    try:
        resultat = controleur.executer()
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
