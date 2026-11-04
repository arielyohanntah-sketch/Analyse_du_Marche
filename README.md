# Analyse comparative de marché

**Trois boutiques en ligne vendent les mêmes produits, mais avec des catalogues
écrits différemment et des prix différents. Pour chaque produit, où faut-il
acheter, et quel écart de prix existe-t-il ?**

Ce projet répond à cette question avec une chaîne complète :

```text
Collecter → Normaliser → Indexer / Rapprocher → Comparer → Décider
```

Il est écrit en **Python**, en architecture **MVC**, avec les données fictives
fournies dans `data/` (CSV, JSON et Excel).

---

## 1. Le problème expliqué simplement

Le client veut acheter de l'électronique et de l'électroménager à Abidjan.
Trois enseignes vendent des produits proches :

| Enseigne | Format du fichier | Particularité |
|---|---|---|
| **Marché Lagune** | CSV avec `;` | prix en texte (`102 900 FCFA`), livraison incluse |
| **Baobab Shop** | JSON d'API | prix = `amount` + `delivery_fee` |
| **Comptoir Ivoire** | Excel | prix catalogue − remise, retrait en boutique |

Les noms ne sont pas écrits pareil :

- `SAMSUNG GALAXY A15 (128GB)`
- `Galaxy A15 128GB - Samsung`
- `Samsun Galaxy A15 128Go`

Le programme doit reconnaître qu'il s'agit du **même produit**, comparer les
prix réellement payés, puis dire :

> Pour l'ordinateur HP 250 G9, la meilleure boutique est Baobab Shop à
> 354 200 FCFA. L'écart avec la plus chère est de 52 800 FCFA (14,9 %).

---

## 2. Ce que le programme produit

Le programme répond aux huit points de l'énoncé :

1. **Chargement** : lecture des trois formats (CSV, JSON, Excel) dans une même
   structure `Offre`.
2. **Nettoyage** : normalisation des noms, des prix, des unités et des
   disponibilités. Chaque problème est écrit dans un **journal**.
3. **Rapprochement** : chaque offre reçoit un `produit_id` du catalogue
   commun (`P01` à `P30`).
4. **Comparatif** : pour chaque produit disponible dans au moins deux
   boutiques, prix minimum, prix maximum, écart en FCFA et en %, meilleure
   boutique. Export dans `reports/comparatif.csv`.
5. **Synthèse** : nombre de victoires par enseigne, écart moyen par rapport
   au prix le plus bas, top 3 des plus gros écarts.
6. **Panier** : coût du panier de rentrée dans chaque boutique, puis
   meilleure combinaison article par article.
7. **Historique** : comparaison de la semaine du Black Friday (24–30 novembre
   2025) avec la moyenne annuelle, et meilleur mois par enseigne.
8. **Complexité** : temps mesurés pour la recherche naïve et la recherche
   indexée dans l'historique.

Les résultats sont affichés dans la console et exportés dans :

- `reports/comparatif.csv` ;
- `reports/journal_nettoyage.csv`.

---

## 3. Résultats obtenus sur les données de l'exercice

### Comparatif

- **30** produits de référence, **76** offres collectées.
- **23** produits sont comparables (au moins deux boutiques disponibles).
- **7** produits ne le sont pas : rupture, prix absent, ou une seule
  boutique les vend.

### Victoires (égalités comprises)

| Boutique | Produits où elle est la moins chère |
|---|---:|
| Comptoir Ivoire | 10 |
| Baobab Shop | 9 |
| Marché Lagune | 6 |

Il y a **2 égalités** (souris Logitech M185 et fer Philips).

### Écart moyen par rapport au prix le plus bas

| Boutique | Surcoût moyen |
|---|---:|
| Comptoir Ivoire | 2,8 % |
| Marché Lagune | 3,8 % |
| Baobab Shop | 4,7 % |

### Top 3 des marges en FCFA

| Produit | Meilleure boutique | Prix min | Prix max | Écart |
|---|---|---:|---:|---:|
| P11 — HP 250 G9 | Baobab Shop | 354 200 | 407 000 | **52 800 FCFA** |
| P09 — iPhone 13 | Baobab Shop | 417 200 | 443 700 | **26 500 FCFA** |
| P24 — Climatiseur LG 1 CV | Baobab Shop | 253 300 | 279 300 | **26 000 FCFA** |

### Top 3 des écarts relatifs (à surveiller)

| Produit | Écart |
|---|---:|
| P29 — Bouilloire 1,7 L | **26,1 %** |
| P14 — Clé USB SanDisk 64 Go | **19,7 %** |
| P21 — Congélateur Nasco 200 L | **16,0 %** |

### Panier de rentrée

| Boutique | Coût si tout est acheté sur place |
|---|---:|
| Marché Lagune | incomplet (Tecno Spark 20 écarté) |
| Baobab Shop | 491 500 FCFA |
| Comptoir Ivoire | **484 075 FCFA** |

**Meilleure combinaison** : 477 575 FCFA
(1 Tecno chez Baobab, 1 Lenovo chez Comptoir, 2 clés USB et 1 disque dur
chez Marché, 1 micro-ondes chez Baobab).

**Économie** : 6 500 FCFA par rapport à la meilleure boutique unique.

### Historique

| Boutique | Moyenne annuelle | Black Friday | Variation |
|---|---:|---:|---:|
| Marché Lagune | 161 978 | 143 894 | **−11,2 %** |
| Baobab Shop | 140 913 | 124 579 | **−11,6 %** |
| Comptoir Ivoire | 154 843 | 160 604 | **+3,7 %** |

Le Black Friday était intéressant chez Marché Lagune et Baobab Shop, mais
pas chez Comptoir Ivoire. Le mois le moins cher est **septembre 2026** pour
les trois enseignes.

### Complexité (exemple de mesure)

| Opération | Version naïve | Version indexée | Gain |
|---|---:|---:|---:|
| 500 recherches dans 20 876 lignes | ≈ 230 ms | ≈ 0,09 ms | ×2 500 |

Les temps varient selon la machine ; le benchmark est refait à chaque
exécution.

---

## 4. Installation et exécution

### Prérequis

- Python 3.10 ou plus récent (testé avec Python 3.14)
- Le module `openpyxl` pour lire le fichier Excel

### Commandes

```powershell
cd "C:\Users\DELL\Documents\LICENCE 2\PROJET-L2\PYTHON\ANALYSE_DU_MARCHE"

# Activer l'environnement virtuel (déjà présent dans le projet)
.\.venv\Scripts\Activate.ps1

# Installer la dépendance
pip install -r requirements.txt

# Lancer l'analyse complète
python main.py

# Lancer les tests
python -m unittest discover -s tests -v
```

Si PowerShell refuse d'activer l'environnement virtuel, utilisez directement :

```powershell
.\.venv\Scripts\python.exe main.py
```

### Fichiers produits

| Fichier | Contenu |
|---|---|
| `reports/comparatif.csv` | tableau produit par produit (séparateur `;`, UTF-8 BOM pour Excel) |
| `reports/journal_nettoyage.csv` | toutes les anomalies et les actions appliquées |

---

## 5. Architecture MVC

```text
ANALYSE_DU_MARCHE/
├── main.py                         # point d'entrée
├── data/                           # les 5 fichiers de l'exercice
├── docs/LISEZ-MOI.md               # énoncé original du professeur
├── EXPLICATION.md                  # guide pédagogique et plan d'exposé
├── Models/                         # les objets métier
│   ├── Produit.py                  # produit du catalogue
│   ├── Offre.py                    # article vendu par une boutique
│   ├── Analyse.py                  # comparaison, synthèse, benchmark
│   ├── Panier.py                   # panier et totaux
│   ├── Journal.py                  # journal de nettoyage
│   └── Historique.py               # statistiques historiques
├── Services/                       # le traitement métier
│   ├── csv_service.py              # lecture du catalogue et de Marché Lagune
│   ├── json_service.py             # lecture de Baobab Shop
│   ├── excel_service.py            # lecture de Comptoir Ivoire
│   ├── normalisation_service.py    # noms, prix, unités, synonymes
│   ├── matching_service.py         # index inversé + score de rapprochement
│   ├── comparaison_service.py      # min/max/écart + synthèse
│   ├── panier_service.py           # coût par boutique + combinaison optimale
│   ├── historique.py               # chargement et analyse du Black Friday
│   └── benchmark_service.py        # mesure de la recherche dans l'historique
├── Views/                          # l'affichage
│   └── Interface.py                # vue console
├── Controllers/
│   └── Analyse_Controller.py       # orchestre le pipeline
├── tests/
│   └── test_services.py            # 10 tests unitaires
└── reports/                        # sorties générées
```

### Qui fait quoi ?

- **Modèle** (`Models/` + `Services/`) : les données et les règles métier.
  Il ne connaît pas la console.
- **Vue** (`Views/`) : met en forme les objets calculés. Elle ne calcule rien.
- **Contrôleur** (`Controllers/`) : appelle les services dans le bon ordre et
  transmet le résultat à la vue.

Les `Services` sont rangés avec le Modèle : ce sont des règles métier, pas
de l'affichage. C'est une séparation MVC un peu enrichie, courante en Python.

---

## 6. Les données et leurs pièges

Le fichier `docs/LISEZ-MOI.md` contient l'énoncé original. Voici les pièges
rencontrés dans les données et la façon dont ils sont traités.

| Piège | Exemple concret | Traitement |
|---|---|---|
| Doublons | `ML-1000` et `ML-1147` apparaissent deux fois | doublon ignoré, journalisé |
| Prix absent | `Prix sur demande`, cellule vide, `amount: null` | offre non comparable |
| Prix incohérent | 779 000 FCFA alors que l'ancien prix est 88 700 FCFA | offre écartée, journalisée |
| Rupture | `Rupture`, `stock: 0`, `Quantité en rayon: 0` | offre exclue de la comparaison |
| Marque mal orthographiée | `Samsun Galaxy A15` | corrigée en Samsung par similarité |
| Prix écrit en texte | `"279 300"` dans Excel | converti en `279300` |
| Unités différentes | `Go` / `GB`, `To` / `TB`, `CV` / `HP` | normalisées |
| Noms dans un autre ordre | `Galaxy A15 128GB - Samsung` | normalisation + ensemble de mots |
| Synonymes | frigo / fridge / réfrigérateur, blender / mixeur | dictionnaire de synonymes |
| Une seule boutique | P18, P19, P25, P30… | produit listé comme non comparable |

Le journal complet est dans `reports/journal_nettoyage.csv`. Il contient
l'étape, la source, la référence, le problème, l'action et la gravité.

---

## 7. Comment le programme reconnaît un produit

### 7.1 Normalisation

On transforme le nom en une forme canonique :

```text
"SAMSUNG GALAXY A15 (128GB)"       → "samsung galaxy a15 128gb"
"Galaxy A15 128GB - Samsung"       → "galaxy a15 128gb samsung"
"Samsun Galaxy A15 128Go"          → "samsun galaxy a15 128gb"
```

Étapes : minuscules, suppression des accents, ponctuation remplacée par des
espaces, unités unifiées, synonymes, mots trop généraux ignorés.

### 7.2 Signature

Pour chaque nom normalisé, on extrait :

- les **mots** ;
- la **marque** (Samsung, HP, Lenovo…) ;
- les **capacités** (`128gb`, `1tb`, `1.5l`, `1hp`) ;
- les **modèles** (`a15`, `g9`, `i5`, `m185`, `2720e`).

### 7.3 Index inversé

Au lieu de comparer chaque offre aux 30 produits, on construit :

```text
mot → liste des produits qui contiennent ce mot
```

Exemple : `hp → [P11, P17]`, `a15 → [P01]`, `1hp → [P24]`.

Une offre ne compare donc qu'aux produits qui partagent au moins un mot.
C'est ce qui fait passer la complexité de `O(n × m)` à `O(n × k)`, avec
`k` petit.

### 7.4 Règles de rejet

Un candidat est rejeté si :

- la **marque** est différente (`LG` vs `Hisense`) ;
- la **capacité** est différente (`128gb` vs `256gb`, `1hp` vs `1.5hp`) ;
- le **modèle** est différent (`a15` vs `a25`, `i3` vs `i5`).

C'est ce qui évite de confondre :

- Samsung Galaxy A15 / A25 / A55 ;
- HP 250 G9 / Lenovo IdeaPad 3 / Dell Inspiron 15 ;
- Climatiseur LG 1 CV / Climatiseur Hisense 1,5 CV.

### 7.5 Score

Pour les candidats restants, on calcule un score entre 0 et 1 :

```text
rappel    = mots communs / mots du produit de référence
précision = mots communs / mots de l'offre
F1        = 2 × rappel × précision / (rappel + précision)
score     = 0,7 × F1 + 0,2 × rappel + 0,1 × bonus de marque
```

Si le score est inférieur à **0,60**, l'offre n'est pas reconnue. Si le
score est inférieur à **0,80**, la correspondance est signalée dans le
journal pour vérification.

Exemple :

| Offre | Score | Décision |
|---|---:|---|
| `HP 250 G9 i5` (Comptoir) | 0,79 | associé à P11 |
| `Seagate Expansion 1TB` (Baobab) | 0,67 | associé à P15 |
| `Samsun Galaxy A15 128Go` | 0,92 | associé à P01, marque corrigée |

---

## 8. Comparaison et décision

Pour chaque produit disponible dans au moins deux boutiques :

```text
prix_min = minimum des prix payés
prix_max = maximum des prix payés
écart    = prix_max − prix_min
écart %  = écart / prix_min × 100
```

- La **meilleure boutique** est celle qui a le `prix_min`.
- En cas d'égalité, plusieurs boutiques sont affichées.
- L'**écart** est la marge réalisée si l'on évite la boutique la plus chère.
- Une **alerte** est affichée si l'écart dépasse **10 %**.

### Prix réellement payé

| Boutique | Formule |
|---|---|
| Marché Lagune | prix affiché (livraison incluse) |
| Baobab Shop | `amount + delivery_fee` |
| Comptoir Ivoire | `prix catalogue × (1 − remise / 100)` |

Un produit en rupture, sans prix, ou avec un prix incohérent n'est **jamais**
retenu comme le moins cher.

---

## 9. Panier : pourquoi la somme des minima est optimale

Le panier contient :

- 1 Tecno Spark 20 (P04)
- 1 Lenovo IdeaPad 3 (P12)
- 2 clés USB SanDisk (P14)
- 1 disque dur Seagate (P15)
- 1 micro-ondes Samsung (P28)

Ici, chaque article est **indépendant** : il n'y a pas de frais fixes par
commande ni de coût de déplacement. Donc acheter chaque article au prix le
plus bas est optimal. Le coût de la combinaison est la **somme des minima**,
et non le minimum des sommes.

> Si l'on ajoutait des frais de livraison fixes par boutique ou un coût de
> déplacement, le problème deviendrait plus complexe (proche d'un problème
> de couverture / sac à dos). C'est une extension possible.

Résultat : **477 575 FCFA** en éclatant les achats, contre **484 075 FCFA**
si tout est acheté chez Comptoir Ivoire, soit **6 500 FCFA d'économie**.

---

## 10. Historique et Black Friday

`historique_prix.csv` contient **20 876 lignes** du 01/11/2025 au 31/10/2026.
Les produits y sont déjà identifiés par `produit_id`.

Pour chaque enseigne :

```text
moyenne annuelle = moyenne de tous les prix
moyenne BF       = moyenne des prix du 24 au 30 novembre 2025
variation %      = (moyenne BF − moyenne annuelle) / moyenne annuelle × 100
```

Une variation négative signifie que le Black Friday était moins cher.

Pour Comptoir Ivoire, l'historique contient le **prix catalogue**, sans la
remise : c'est précisé dans l'énoncé.

Le programme calcule aussi le **mois le moins cher** pour chaque enseigne.

---

## 11. Complexité algorithmique

### Notations

- `n` : nombre de lignes lues (offres ou relevés historiques) ;
- `m` : nombre de produits du catalogue (30) ;
- `q` : nombre de requêtes ;
- `k` : nombre moyen de candidats après l'index (petit).

### Tableau des complexités

| Opération | Structure | Complexité |
|---|---|---|
| Lire un fichier | `csv.DictReader` / `json.load` | `O(n)` |
| Dédoublonner | `set` | `O(n)` |
| Normaliser un nom | expressions régulières | `O(longueur du nom)` |
| Construire l'index | `dict` / `set` | `O(n)` |
| Rapprocher les offres | index inversé | `O(n × k)`, proche de `O(n)` |
| Comparer les prix | `dict` + parcours du catalogue | `O(n + m)` |
| Trier le comparatif | `sorted` | `O(m log m)` |
| Chercher dans l'historique (naïf) | liste | `O(q × n)` |
| Chercher dans l'historique (index) | `dict` | `O(q)` |
| Panier | `dict` + 5 articles | `O(n + 5 × 3)` |

### Pourquoi `dict` et `set` sont rapides

Un dictionnaire ou un ensemble utilise une **table de hachage** : on calcule
une clé (`hash`) et on va presque directement à la case mémoire. En moyenne,
l'accès est `O(1)`, alors qu'une recherche dans une liste est `O(n)`.

C'est pour cela que :

- l'historique est indexé par `(source, produit_id)` ;
- les offres sont regroupées par `produit_id` ;
- le rapprochement utilise un index `mot → produits`.

### Mesure

Le benchmark compare, sur la même machine, **500 recherches** dans les
20 876 lignes :

- parcours complet de la liste ;
- dictionnaire indexé.

Les résultats sont affichés dans la console. Ils montrent que la version
indexée est plusieurs centaines de fois plus rapide.

---

## 12. Tests

```powershell
python -m unittest discover -s tests -v
```

Les 10 tests couvrent :

- la conversion des prix (`102 900 FCFA`, `Prix sur demande`, etc.) ;
- la normalisation des noms et des unités ;
- la correction de la marque `Samsun` → Samsung ;
- le calcul du prix payé (livraison, remise) ;
- l'exclusion d'un prix incohérent ;
- le dédoublonnage ;
- le rapprochement de deux produits ;
- la comparaison min/max/écart ;
- le panier et l'économie ;
- la moyenne Black Friday et l'égalité recherche naïve / recherche indexée.

---

## 13. Mettre le projet sur GitHub

Le dossier est déjà un dépôt Git local. Pour le publier, créer un dépôt
**vide** sur GitHub (sans README, sans `.gitignore`), puis :

```powershell
git remote add origin https://github.com/<votre-utilisateur>/<nom-du-depot>.git
git push -u origin main
```

Avec GitHub CLI :

```powershell
gh auth login
gh repo create <nom-du-depot> --public --source=. --remote=origin --push
```

Le fichier `.gitignore` exclut déjà `.venv/`, `__pycache__/` et `.idea/`.
Vérifiez avec :

```powershell
git status
```

Si Git demande une authentification, utilisez un **Personal Access Token**
GitHub, ou l'outil `gh`.

---

## 14. Limites et prolongements

- Le rapprochement est réglé pour ce catalogue : un nouveau catalogue peut
  nécessiter d'ajouter des synonymes ou d'ajuster le seuil `0,60`.
- L'historique est analysé par enseigne, pas produit par produit. On pourrait
  ajouter « pour chaque produit, quel mois était le moins cher ? ».
- Le panier suppose qu'il n'y a pas de frais fixes par commande. Avec des
  frais de livraison par boutique, il faudrait résoudre un problème
  d'optimisation plus complexe.
- Les données sont **fictives** et servent uniquement à l'exercice.

---

## 15. Contexte

Projet réalisé dans le cadre de la **DA Python — L2 Computer Science**,
séance 3 : analyse comparative de marché.

Données : `docs/LISEZ-MOI.md` (énoncé original).
