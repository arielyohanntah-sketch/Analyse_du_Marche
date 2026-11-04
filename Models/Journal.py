"""Journal de nettoyage : la mémoire de toutes les corrections faites.

Le professeur demande de "repérer les problèmes, les traiter et les lister
dans un journal". Chaque anomalie devient une LigneJournal avec :
- l'étape du traitement,
- la source et la référence concernées,
- le problème constaté,
- l'action appliquée,
- un niveau de gravité.
"""

from dataclasses import dataclass, field
import csv
from pathlib import Path


@dataclass
class LigneJournal:
    etape: str
    source: str
    reference: str
    probleme: str
    action: str
    gravite: str = "INFO"   # INFO, AVERTISSEMENT ou ERREUR


@dataclass
class Journal:
    lignes: list[LigneJournal] = field(default_factory=list)

    def ajouter(self, etape: str, source: str, reference: str,
                probleme: str, action: str, gravite: str = "INFO") -> None:
        self.lignes.append(
            LigneJournal(etape, source, reference, probleme, action, gravite)
        )

    def compter(self) -> dict[str, int]:
        compteur = {"INFO": 0, "AVERTISSEMENT": 0, "ERREUR": 0}
        for ligne in self.lignes:
            compteur[ligne.gravite] = compteur.get(ligne.gravite, 0) + 1
        return compteur

    def exporter_csv(self, chemin: str | Path) -> None:
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with chemin.open("w", encoding="utf-8-sig", newline="") as fichier:
            writer = csv.writer(fichier, delimiter=";")
            writer.writerow(
                ["etape", "source", "reference", "probleme", "action", "gravite"]
            )
            for ligne in self.lignes:
                writer.writerow([
                    ligne.etape, ligne.source, ligne.reference,
                    ligne.probleme, ligne.action, ligne.gravite,
                ])
