# Rôle : Point de départ du programme, il initialise les chemins et lance le contrôleur.
# Emplacement MVC : RACINE DU PROJET (Point d'entrée)

import os
import sys

# Désactive la génération des dossiers __pycache__
sys.dont_write_bytecode = True

from controllers.controleur_principal import ControleurPrincipal


def main():
    # Affichage propre des accents sous Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    # Chemins absolus vers les fichiers de données
    repertoire_projet = os.path.dirname(os.path.abspath(__file__))
    dossier_data = os.path.join(repertoire_projet, "data")

    chemins_fichiers = {
        "catalogue_ref": os.path.join(dossier_data, "catalogue_reference.csv"),
        "marche_lagune": os.path.join(dossier_data, "marche_lagune.csv"),
        "baobab_shop": os.path.join(dossier_data, "baobab_shop.json"),
        "comptoir_ivoire": os.path.join(dossier_data, "comptoir_ivoire.xlsx"),
        "historique_prix": os.path.join(dossier_data, "historique_prix.csv"),
    }

    print("===================================================================================")
    print("      LANCEMENT DU COMPARATEUR DE MARCHÉ (DA PYTHON - SÉANCE 3 - PROJET L2)        ")
    print("===================================================================================")

    # Création et exécution du contrôleur
    app = ControleurPrincipal(chemins_fichiers)
    app.demarrer()


if __name__ == "__main__":
    main()
