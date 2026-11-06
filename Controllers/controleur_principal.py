# Rôle : Chef d'orchestre, pilote le menu interactif et relie le modèle à la vue.
# Emplacement MVC : CONTRÔLEUR

import time
import os
from models.journal_erreurs import JournalErreurs
from models.chargement_fichiers import (
    charger_catalogue_reference,
    charger_donnees_boutiques,
    charger_historique_prix
)
from models.analyse_comparaison import (
    comparer_prix,
    rechercher_produit,
    exporter_tableau_csv,
    faire_synthese,
    calculer_panier_rentree,
    analyser_black_friday
)
from views.affichage_console import AffichageConsole


class ControleurPrincipal:
    """Contrôleur qui gère le cycle de vie de l'application console interactive."""

    def __init__(self, chemins):
        self.chemins = chemins
        self.vue = AffichageConsole()
        self.journal = JournalErreurs()

    def demarrer(self):
        """Charge les données et lance la boucle du menu interactif."""
        dossier_data = os.path.dirname(self.chemins.get("catalogue_ref", ""))

        print("\n[INFO] Chargement et analyse des catalogues en cours...")

        # 1. Chargement du catalogue de référence
        catalogue_ref = charger_catalogue_reference(self.chemins["catalogue_ref"])

        # 2. Chargement et nettoyage des boutiques
        donnees = charger_donnees_boutiques(
            chemin_ml=self.chemins["marche_lagune"],
            chemin_bb=self.chemins["baobab_shop"],
            chemin_ci=self.chemins["comptoir_ivoire"],
            catalogue_ref=catalogue_ref,
            journal=self.journal
        )

        # Sauvegarde automatique des fichiers d'export
        chemin_journal = os.path.join(dossier_data, "journal_anomalies.txt")
        self.journal.sauvegarder_fichier(chemin_journal)

        rapport = comparer_prix(donnees)
        chemin_csv = os.path.join(dossier_data, "comparatif.csv")
        exporter_tableau_csv(rapport, chemin_csv)

        synthese = faire_synthese(rapport)
        panier = calculer_panier_rentree(donnees)

        # 3. Mesure de la complexité sur l'historique
        t_debut = time.perf_counter()
        nb_lignes, stats_hist = charger_historique_prix(self.chemins["historique_prix"])
        temps_ms = (time.perf_counter() - t_debut) * 1000
        resultats_bf = analyser_black_friday(stats_hist)

        print("[OK] Données prêtes ! Lancement du menu.")

        # 4. Boucle interactive du menu console
        while True:
            self.vue.afficher_menu_principal()
            choix = self.vue.demander_choix()

            if choix == "1":
                self.vue.afficher_tableau_comparatif(rapport)
                self.vue.pause()

            elif choix == "2":
                terme = self.vue.demander_recherche()
                if terme:
                    resultats = rechercher_produit(terme, donnees)
                    self.vue.afficher_resultats_recherche(resultats)
                self.vue.pause()

            elif choix == "3":
                self.vue.afficher_synthese(synthese)
                self.vue.pause()

            elif choix == "4":
                self.vue.afficher_panier_rentree(panier)
                self.vue.pause()

            elif choix == "5":
                self.vue.afficher_black_friday(resultats_bf)
                self.vue.pause()

            elif choix == "6":
                self.vue.afficher_journal_anomalies(self.journal.recuperer_liste())
                self.vue.pause()

            elif choix == "7":
                self.vue.afficher_complexite(nb_lignes, temps_ms)
                self.vue.pause()

            elif choix == "0":
                print("\nMerci d'avoir utilisé le Comparateur de Marché. Au revoir !\n")
                break

            else:
                print("Choix invalide. Veuillez entrer un chiffre entre 0 et 7.")
