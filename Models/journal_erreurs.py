# Rôle : Enregistre les erreurs et anomalies des fichiers (doublons, ruptures, prix invalides).
# Emplacement MVC : MODÈLE (Gestion des anomalies)


class JournalErreurs:
    """Consigne les anomalies repérées dans les fichiers des boutiques."""

    def __init__(self):
        self.anomalies = []

    def ajouter(self, boutique, reference, anomalie, description, solution):
        """Ajoute une anomalie dans le journal."""
        self.anomalies.append({
            "boutique": boutique,
            "reference": reference,
            "anomalie": anomalie,
            "description": description,
            "solution": solution
        })

    def sauvegarder_fichier(self, chemin_fichier):
        """Écrit le journal dans un fichier texte."""
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("          JOURNAL DES ANOMALIES TROUVÉES DANS LES DONNÉES\n")
            f.write("=" * 80 + "\n\n")
            for a in self.anomalies:
                f.write(f"[{a['boutique']}] Réf: {a['reference']} | Problème: {a['anomalie']}\n")
                f.write(f"   Détail : {a['description']}\n")
                f.write(f"   Action : {a['solution']}\n\n")

    def recuperer_liste(self):
        """Renvoie la liste brute des anomalies."""
        return self.anomalies
