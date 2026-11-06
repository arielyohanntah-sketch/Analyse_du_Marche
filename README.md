# 📊 Analyse Comparative de Marché (Comparateur de Prix Multi-Boutiques)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-MVC-green.svg)](#architecture-mvc)
[![Licence](https://img.shields.io/badge/Niveau-Licence%202%20Informatique-orange.svg)](#)

Projet universitaire d'analyse comparative de marché et de décision d'achat développé dans le cadre du cours de **Python (L2 Computer Science - Séance 3)**.

Le programme collecte, nettoie et compare les catalogues de prix de trois enseignes ivoiriennes fictives d'électronique et d'électroménager :
* **Marché Lagune** (Site e-commerce, export CSV avec séparateur `;`)
* **Baobab Shop** (Application mobile, export JSON d'API avec frais de livraison)
* **Comptoir Ivoire** (Boutique physique à Adjamé, classeur Excel `.xlsx` avec remises)

---

## 🎯 Objectifs du Projet

1. **Collecter et harmoniser** des sources de formats hétérogènes (CSV, JSON, Excel) vers un catalogue de référence de 30 produits (`P01` à `P30`).
2. **Gérer les anomalies réelles** : suppression des doublons, détection des prix aberrants, filtrage des ruptures de stock et journalisation dans `journal_anomalies.txt`.
3. **Comparer les prix en stock** : calcul du prix le plus bas, de l'enseigne gagnante et de l'écart en FCFA et en pourcentage :
   $$\text{Écart (\%)} = \frac{\text{Prix haut} - \text{Prix bas}}{\text{Prix bas}} \times 100$$
4. **Optimiser un panier d'achat** (panier de rentrée scolaire composé de 5 articles).
5. **Analyser l'historique des prix** sur plus de 20 000 relevés journaliers pour vérifier la réalité des promotions du Black Friday.
6. **Optimiser la complexité algorithmique** ($\mathcal{O}(N)$ en temps et $\mathcal{O}(K)$ en mémoire via streaming).

---

## 🏗️ Architecture MVC

Le projet respecte rigoureusement le modèle architectural **Modèle - Vue - Contrôleur (MVC)** avec des noms de fichiers clairs et explicites en français :

```text
ANALYSE_DU_MARCHE/
│
├── models/                             # COUCHE MODÈLE (Logique & Données)
│   ├── journal_erreurs.py              # Journalise les anomalies (doublons, ruptures, prix invalides)
│   ├── nettoyage_donnees.py            # Normalise les noms/prix et rapproche vers P01-P30
│   ├── chargement_fichiers.py          # Lecture streaming des fichiers CSV, JSON, Excel
│   └── analyse_comparaison.py          # Comparatif, panier optimal, Black Friday, export CSV
│
├── views/                              # COUCHE VUE (Interface Utilisateur)
│   └── affichage_console.py            # Formate et affiche les tableaux dans le terminal
│
├── controllers/                        # COUCHE CONTRÔLEUR (Orchestration)
│   └── controleur_principal.py         # Relie le Modèle à la Vue et pilote le flux
│
├── data/                               # Sources de données & exports
│   ├── catalogue_reference.csv         # 30 produits officiels (P01 à P30)
│   ├── marche_lagune.csv               # Données Marché Lagune (CSV)
│   ├── baobab_shop.json                # Données Baobab Shop (JSON)
│   ├── comptoir_ivoire.xlsx            # Données Comptoir Ivoire (Excel)
│   ├── historique_prix.csv             # 20 876 relevés de prix journaliers
│   ├── comparatif.csv                  # [GÉNÉRÉ] Tableau comparatif complet
│   └── journal_anomalies.txt           # [GÉNÉRÉ] Journal des 17 anomalies détectées
│
├── main.py                             # Point d'entrée principal
└── README.md                           # Documentation du dépôt GitHub
```

---

## ⚡ Prérequis & Installation

### 1. Cloner le projet
```bash
git clone https://github.com/votre-compte/analyse-comparative-marche.git
cd analyse-comparative-marche
```

### 2. Installer la seule dépendance requise (`openpyxl`)
Le projet utilise quasi-exclusivement la bibliothèque standard de Python (`csv`, `json`, `os`, `sys`, `time`, `re`).  
La seule dépendance externe est `openpyxl` pour la lecture du classeur Excel :

```bash
pip install openpyxl
```

---

## 🚀 Exécution

Pour lancer le comparateur, exécutez simplement :

```bash
python main.py
```

---

## 📈 Résultats Principaux de l'Analyse

### 1. Synthèse globale des enseignes
* **Baobab Shop** est la moins chère sur **9 produits sur 23** (39,1 % des cas).
* **Comptoir Ivoire** est la moins chère sur **8 produits sur 23** (34,8 % des cas) et affiche le plus faible écart moyen par rapport au prix le plus bas (**+2,81 %**).
* **Marché Lagune** est la moins chère sur **6 produits** (26,1 % des cas).

### 2. Le Panier de rentrée
Composition du panier :
* 1× Tecno Spark 20 (P04)
* 1× Lenovo IdeaPad 3 (P12)
* 2× Clés USB SanDisk 64 Go (P14)
* 1× Disque dur externe Seagate 1 To (P15)
* 1× Micro-ondes Samsung 23 L (P28)

| Option d'achat | Coût total (FCFA) | Économie réalisée |
| :--- | :--- | :--- |
| Tout acheter chez Marché Lagune | 1 205 400 F | Prix pénalisé par le prix aberrant du P04 |
| Tout acheter chez Baobab Shop | 491 500 F | - |
| Tout acheter chez Comptoir Ivoire | 484 075 F | - |
| **Panier Optimisé Multi-Boutiques** | **477 575 F** | **727 825 F d'économie maximale (-60,4 %)** |

### 3. Étude Historique & Black Friday (20 876 relevés)
* **Marché Lagune** : -11,16 % pendant le Black Friday $\rightarrow$ **Vraie réduction**.
* **Baobab Shop** : -11,59 % pendant le Black Friday $\rightarrow$ **Vraie réduction**.
* **Comptoir Ivoire** : +3,72 % pendant le Black Friday $\rightarrow$ **Pas de réduction réelle**.

---

## 🧠 Étude de Complexité Algorithmique (Big-O)

* **Complexité Temporelle $\mathcal{O}(N)$ :**  
  L'utilisation de **tables de hachage (dictionnaires Python)** permet d'insérer et d'indexer chaque produit en temps moyen constant $\mathcal{O}(1)$. Les 20 876 lignes de l'historique sont traitées en **~40 millisecondes**, évitant tout parcours imbriqué quadratique lent en $\mathcal{O}(N^2)$.
* **Complexité Spatiale $\mathcal{O}(K)$ :**  
  Les fichiers volumineux sont lus en **flux continu (streaming)** ligne par ligne via `csv.DictReader` sans jamais charger l'intégralité du fichier en mémoire vive avec `read()`, garantissant une empreinte RAM minimale.


