# Explication complète du projet

**Analyse comparative de marché — trois boutiques, un catalogue**

Ce document est écrit pour toi, pas pour le correcteur. Il reprend le sujet
avec des mots simples, explique chaque fichier, chaque étape et chaque choix,
puis propose un plan d'exposé et les questions que le professeur peut poser.

> Conseil de lecture : lis d'abord les sections 1 à 4 pour comprendre
> l'objectif. Ensuite, garde les sections 6 et 7 ouvertes pendant que tu
> relis le code. La section 10 est ton plan d'exposé.

---

## 1. Le sujet raconté simplement

Un client à Abidjan veut acheter de l'électronique et de l'électroménager.
Trois enseignes vendent des produits proches :

- **Marché Lagune** : un site marchand, fichier CSV séparé par des `;` ;
- **Baobab Shop** : une application mobile, fichier JSON ;
- **Comptoir Ivoire** : une boutique d'Adjamé, fichier Excel.

Le problème n'est pas de lire les fichiers. Le problème est que **les trois
boutiques ne parlent pas le même langage** :

| Catalogue commun | Marché Lagune | Baobab Shop | Comptoir Ivoire |
|---|---|---|---|
| Samsung Galaxy A15 128 Go | `SAMSUNG GALAXY A15 (128GB)` | `Galaxy A15 128GB - Samsung` | `Samsun Galaxy A15 128Go` |
| Clé USB SanDisk 64 Go | `CLE USB SANDISK 64GB` | `SanDisk USB Flash Drive 64GB` | `Cle USB Sandisk 64 Go` |
| Climatiseur LG 1 CV | `CLIMATISEUR LG 1CV` | `LG Air Conditioner 1HP` | `Climatiseur LG 1 CV` |

Il faut donc :

1. **collecter** les trois sources dans une même structure ;
2. **nettoyer** les noms, les prix, les unités et les disponibilités ;
3. **rapprocher** chaque offre du bon produit du catalogue (`P01` à `P30`) ;
4. **comparer** les prix réellement payés ;
5. **décider** où acheter, et quels écarts surveiller.

La question finale à laquelle le programme répond est :

> Pour chaque produit, quelle boutique est la moins chère, quel est l'écart
> avec la plus chère, et que faut-il acheter où ?

### La phrase à retenir pour l'exposé

> « Trois boutiques, un même catalogue, des noms et des prix écrits
> différemment : mon programme les rapproche, compare le prix réellement payé,
> puis sort une décision et un journal de nettoyage. »

---

## 2. Ce que le professeur demande exactement

Le sujet contient huit consignes. Voici où chacune est traitée dans le code :

| Consigne du sujet | Fichier(s) principal(aux) | Ce que le programme fait |
|---|---|---|
| 1. Chargement des trois formats | `Services/csv_service.py`, `json_service.py`, `excel_service.py` | Transforme CSV, JSON et Excel en objets `Offre` |
| 2. Nettoyage + journal | `Services/normalisation_service.py`, `Models/Journal.py` | Corrige les noms et prix, note chaque anomalie |
| 3. Rapprochement | `Services/matching_service.py` | Associe chaque offre à un `produit_id` |
| 4. Comparatif + export CSV | `Services/comparaison_service.py` | Calcule min, max, écart FCFA et %, exporte |
| 5. Synthèse | `Services/comparaison_service.py` | Victoires, surcoût moyen, top 3 des écarts |
| 6. Panier | `Services/panier_service.py` | Coût par boutique + meilleure combinaison |
| 7. Historique / Black Friday | `Services/historique.py` | Moyenne annuelle, moyenne BF, meilleur mois |
| 8. Complexité | `Services/benchmark_service.py` | Compare recherche naïve et recherche indexée |

Et la consigne d'architecture :

| Rôle MVC | Dossier | Responsabilité |
|---|---|---|
| **Modèle** | `Models/` + `Services/` | Données et règles métier |
| **Vue** | `Views/` | Affichage console et HTML |
| **Contrôleur** | `Controllers/` | Orchestration du pipeline |

> En Python, il est courant de mettre les services métier avec le modèle.
> `Models/` contient les objets, `Services/` contient les traitements. Les deux
> forment la couche Modèle : ils ne connaissent ni la console ni le HTML.

---

## 3. Les cinq fichiers de données et leurs pièges

Les fichiers sont dans `data/`. L'énoncé original est dans
`docs/LISEZ-MOI.md`.

| Fichier | Format | Volume | Particularité |
|---|---|---:|---|
| `catalogue_reference.csv` | CSV `,` | 30 produits | Le socle commun : `P01` à `P30` |
| `marche_lagune.csv` | CSV `;` | 30 lignes | Prix en texte, livraison incluse |
| `baobab_shop.json` | JSON | 26 articles | Prix = `amount` + `delivery_fee` |
| `comptoir_ivoire.xlsx` | Excel | 22 articles | Prix catalogue − remise |
| `historique_prix.csv` | CSV `,` | 20 876 lignes | Du 01/11/2025 au 31/10/2026 |

Total collecté : **28 + 26 + 22 = 76 offres**. Les 30 lignes de Marché
Lagune deviennent 28 après suppression de deux doublons.

### Les pièges concrets

| Piège | Exemple dans les données | Traitement dans le code |
|---|---|---|
| Doublons | `ML-1000` et `ML-1147` apparaissent deux fois | `dedupliquer()` garde la première ligne et journalise |
| Prix absent | `Prix sur demande`, cellule vide, `amount: null` | `parser_prix()` renvoie `None`, l'offre est écartée |
| Prix incohérent | Tecno Spark 20 à `779 000 FCFA` avec ancien prix `88 700 FCFA` | ratio 8,78 : offre écartée et journalisée |
| Rupture | `Rupture`, `stock: 0`, `Quantité en rayon: 0` | `disponible = False`, jamais retenue comme moins chère |
| Marque mal orthographiée | `Samsun Galaxy A15` | `difflib` corrige en Samsung (similarité ≥ 0,85) |
| Prix écrit en texte | `"279 300"` dans Excel | `parser_prix()` le convertit en `279300` |
| Unités différentes | `Go`/`GB`, `To`/`TB`, `CV`/`HP` | normalisées en `gb`, `tb`, `hp` |
| Noms dans un autre ordre | `Galaxy A15 128GB - Samsung` | normalisation + ensemble de mots |
| Synonymes | frigo / fridge / réfrigérateur | dictionnaire `SYNONYMES` |
| Une seule boutique | P18, P19, P25, P30… | produit listé comme non comparable |

### Pourquoi avoir écarté le prix de 779 000 FCFA ?

Le prix affiché est `779 000 FCFA`, mais l'ancien prix est `88 700 FCFA`.
Le ratio vaut :

```text
779 000 / 88 700 ≈ 8,78
```

Un prix qui multiplie l'ancien prix par presque 9 est manifestement une erreur
de saisie. Le programme ne le « corrige » pas au hasard : il **écarte l'offre**
et écrit la raison dans le journal. C'est plus honnête que d'inventer un prix.

C'est aussi pour cela que le panier de Marché Lagune est **incomplet** : sans
cette offre, le Tecno Spark 20 n'a pas de prix exploitable chez Marché.

### Les trois formules de prix payé

| Boutique | Formule | Pourquoi |
|---|---|---|
| Marché Lagune | `prix affiché` | La livraison est déjà incluse |
| Baobab Shop | `amount + delivery_fee` | Le client paie les deux |
| Comptoir Ivoire | `prix catalogue × (1 − remise / 100)` | Le client vient chercher l'article |

C'est le **prix payé** qui est comparé, pas le prix affiché. C'est un point
important à dire à l'oral : deux boutiques peuvent afficher 100 000 FCFA et ne
pas coûter le même prix final.

---

## 4. Le pipeline complet

```text
Fichiers bruts
   │
   ├─ CSV Marché Lagune ─┐
   ├─ JSON Baobab ───────┤
   └─ Excel Comptoir ────┘
             │
             ▼
      1. COLLECTE
      → liste d'objets Offre (valeurs brutes)
             │
             ▼
      2. DÉDOUBLONNAGE + NORMALISATION
      → noms canoniques, prix entiers, disponibilité, journal
             │
             ▼
      3. RAPPROCHEMENT
      → chaque Offre reçoit un produit_id (P01…P30)
             │
             ▼
      4. COMPARAISON
      → prix min/max, écart FCFA et %, meilleure boutique
             │
             ├─ 5. PANIER
             ├─ 6. HISTORIQUE
             └─ 7. BENCHMARK
             │
             ▼
      8. EXPORTS
      → comparatif.csv, journal_nettoyage.csv, rapport.html
             │
             ▼
      9. VUES
      → console + rapport HTML
```

### Exemple concret : le HP 250 G9 (P11)

1. **Collecte** : Marché Lagune vend
   `PC PORTABLE HP 250 G9 I5 8GB/512GB` à `390 800 FCFA` ; Baobab vend un
   nom proche à `354 200 FCFA` ; Comptoir vend `HP 250 G9 i5 8Go 512Go` avec
   une remise.
2. **Normalisation** : les trois noms deviennent des formes canoniques
   comparables ; les prix deviennent des entiers.
3. **Rapprochement** : les trois offres reçoivent `P11`.
4. **Comparaison** : prix min = `354 200`, prix max = `407 000`,
   écart = `52 800 FCFA`, soit `14,9 %`.
5. **Décision** : acheter chez Baobab ; écart supérieur à 10 %, donc alerte.

C'est exactement le genre d'exemple à montrer en démonstration.

---

## 5. L'architecture MVC

### 5.1 Le schéma

```text
main.py
   │
   ▼
Controllers/Analyse_Controller.py
   │
   ├── appelle les Services (règles métier)
   │      ├── lecture CSV / JSON / Excel
   │      ├── normalisation
   │      ├── rapprochement
   │      ├── comparaison
   │      ├── panier
   │      ├── historique
   │      └── benchmark
   │
   ├── fabrique des objets Models
   │      └── Produit, Offre, Journal, Analyse, Panier, Historique
   │
   └── transmet le résultat aux Views
          ├── Interface.py  → console
          └── html_view.py  → rapport HTML
```

### 5.2 Qui fait quoi ?

- **Modèle** : les données (`Produit`, `Offre`, `Journal`…) et les règles
  (`normaliser`, `rapprocher`, `comparer`…). Il ne fait aucun `print`.
- **Vue** : elle reçoit un résultat déjà calculé et le met en forme. Elle ne
  calcule rien.
- **Contrôleur** : il choisit l'ordre des étapes, mesure les temps et appelle
  la bonne vue. Il ne contient pas la formule du score de rapprochement.

### 5.3 Pourquoi cette séparation est utile

- On peut changer l'affichage (console → HTML) sans toucher aux calculs.
- On peut tester les calculs sans lancer l'interface.
- Le code est plus facile à expliquer : chaque dossier a une seule mission.
- C'est la réponse attendue à la question « pourquoi MVC ? ».

### 5.4 Arborescence commentée

```text
ANALYSE_DU_MARCHE/
├── main.py                         # point d'entrée, arguments CLI
├── data/                           # les 5 fichiers de l'exercice
├── docs/LISEZ-MOI.md               # énoncé original
├── Models/
│   ├── Produit.py                  # produit du catalogue (immuable)
│   ├── Offre.py                    # article vendu par une boutique
│   ├── Analyse.py                  # résultats de comparaison et benchmark
│   ├── Panier.py                   # panier et totaux
│   ├── Journal.py                  # journal de nettoyage
│   └── Historique.py               # statistiques historiques
├── Services/
│   ├── csv_service.py              # lecture catalogue + Marché Lagune
│   ├── json_service.py             # lecture Baobab Shop
│   ├── excel_service.py            # lecture Comptoir Ivoire
│   ├── normalisation_service.py    # noms, prix, unités, synonymes
│   ├── matching_service.py         # signature, index, score
│   ├── comparaison_service.py      # min/max/écart + synthèse
│   ├── panier_service.py           # coût par boutique + combinaison
│   ├── historique.py               # chargement et analyse du Black Friday
│   └── benchmark_service.py        # mesures de complexité
├── Views/
│   ├── Interface.py                # vue console
│   └── html_view.py                # rapport HTML autonome
├── Controllers/
│   └── Analyse_Controller.py       # orchestration
├── tests/
│   └── test_services.py            # 10 tests unitaires
├── reports/                        # sorties générées
├── EXPLICATION.md                  # ce document
├── README.md                       # documentation du projet
├── requirements.txt                # openpyxl
└── .gitignore
```

### 5.5 Le trajet d'un clic (ou d'une commande)

Quand on lance `python main.py` :

1. `main.py` lit les arguments (`--menu`, `--no-benchmark`).
2. Il crée `AnalyseController`.
3. Le contrôleur vérifie que les 5 fichiers existent.
4. Il appelle les services dans l'ordre : collecte → normalisation →
   rapprochement → comparaison → panier → historique → benchmark.
5. Il construit un `ResultatAnalyse`.
6. Il exporte les CSV et le HTML.
7. La vue console affiche le résultat.

Aucune vue ne lit un fichier. Aucun service ne fait de `print`. C'est le
principe du MVC.

---

## 6. Le code expliqué fichier par fichier

### 6.1 `main.py` : le point d'entrée

Rôle : lire les options et lancer le contrôleur.

```python
parseur.add_argument("--menu", action="store_true")
parseur.add_argument("--no-benchmark", action="store_true")
```

- `--menu` ouvre le menu interactif après l'analyse.
- `--no-benchmark` évite les mesures de temps (plus rapide).

`configurer_console()` force l'UTF-8 pour éviter les accents cassés sous
Windows.

### 6.2 `Controllers/Analyse_Controller.py` : le chef d'orchestre

La méthode centrale est `executer()`. Elle suit toujours le même ordre :

```python
produits = lire_catalogue(...)
offres  = lire_marche_lagune(...)
offres += lire_baobab(...)
offres += lire_comptoir(...)

offres = dedupliquer(offres, journal)
for offre in offres:
    normaliser_offre(offre, journal)

rapprocher_offres(offres, produits, journal)
comparaisons, synthese = comparer(offres, produits)
panier = analyser_panier(offres, produits)
historique = Historique(...).charger(journal)
```

Chaque étape est chronométrée avec `perf_counter()` et rangée dans
`temps["collecte"]`, `temps["normalisation"]`, etc.

Le contrôleur ne calcule pas les prix : il appelle les services. Il ne met pas
en forme : il appelle les vues.

### 6.3 Les modèles

#### `Produit`

Un produit du catalogue est **immuable** (`frozen=True`) : une fois créé, on ne
le modifie plus. Il sert de référence commune.

```python
@dataclass(frozen=True)
class Produit:
    produit_id: str
    nom: str
    categorie: str
    marque: str
```

#### `Offre`

C'est l'objet le plus important. Il contient deux couches :

- les **valeurs brutes** lues dans le fichier (`designation_brute`,
  `prix_source`, `frais_livraison`, `remise_pct`, `stock`…) ;
- les **valeurs calculées** (`designation`, `prix_brut`, `prix`,
  `disponible`, `produit_id`, `score_matching`).

La propriété `prix_effectif` est la garde finale :

```python
@property
def prix_effectif(self):
    if not self.disponible:
        return None
    return self.prix
```

Ainsi, une rupture ou un prix absent ne peut **jamais** être choisi comme
« moins cher », même si l'objet contient encore un ancien prix.

#### `Journal`

Chaque anomalie devient une ligne avec :

- l'étape (`COLLECTE`, `NORMALISATION`, `RAPPROCHEMENT`…) ;
- la source et la référence ;
- le problème constaté ;
- l'action appliquée ;
- la gravité (`INFO`, `AVERTISSEMENT`, `ERREUR`).

C'est la preuve que le nettoyage a été fait sérieusement. Le journal est
exporté dans `reports/journal_nettoyage.csv`.

#### `Analyse`, `Panier`, `Historique`

Ces modèles sont des **structures de résultat** :

- `LigneComparaison` : une ligne du tableau comparatif ;
- `Synthese` : victoires, surcoût moyen, top 3, produits non comparés ;
- `ResultatPanier` : lignes, totaux par boutique, total optimal, économie ;
- `StatsSource` : moyenne annuelle, Black Friday, meilleur mois.

Ils ne contiennent pas de logique : ils transportent des données entre les
services et les vues.

### 6.4 La collecte : trois formats, une seule structure

#### CSV

`csv_service.py` utilise `csv.DictReader`. Pour Marché Lagune, le séparateur
est `;` :

```python
lecteur = csv.DictReader(fichier, delimiter=";")
```

L'encodage `utf-8-sig` enlève le BOM invisible en début de fichier.

#### JSON

`json_service.py` lit `donnees["items"]`, puis chaque article devient une
`Offre`. Le prix payé chez Baobab est :

```python
frais_livraison = int(pricing.get("delivery_fee") or 0)
```

#### Excel

`excel_service.py` utilise `openpyxl`. Le fichier a un titre en ligne 1 et les
en-têtes en ligne 3. Plutôt que de coder `ligne 3` en dur, le code cherche la
ligne qui contient `Code` et `Article` :

```python
if any("code" in t for t in textes) and any("article" in t for t in textes):
    return index
```

C'est plus robuste si le professeur décale les colonnes.

### 6.5 La normalisation : le vrai nettoyage

#### `normaliser_texte()`

Elle transforme un nom en forme canonique. Exemple :

```text
"SAMSUNG GALAXY A15 (128GB)"
→ "samsung galaxy a15 128gb"

"Galaxy A15 128GB - Samsung"
→ "galaxy a15 128gb samsung"

"Samsun Galaxy A15 128Go"
→ "samsun galaxy a15 128gb"
```

Étapes :

1. minuscules ;
2. suppression des accents (`É` → `E`) ;
3. ponctuation remplacée par des espaces ;
4. unités unifiées (`Go` → `gb`, `To` → `tb`, `CV` → `hp`) ;
5. synonymes (`frigo` → `refrigerateur`, `blender` → `mixeur`) ;
6. suppression des mots trop généraux (`pc`, `portable`, `sans`, `fil`…).

On ne modifie **pas** le nom affiché : on garde `SAMSUNG GALAXY A15 (128GB)`
pour l'utilisateur, et on utilise la forme normalisée pour comparer.

#### `parser_prix()`

Elle gère :

- `"102 900 FCFA"` → `102900` ;
- `"279 300"` → `279300` ;
- `109400` → `109400` ;
- `"Prix sur demande"` → `None` ;
- `""` → `None` ;
- `None` → `None`.

Elle gère aussi les séparateurs de milliers et la virgule décimale.

#### `normaliser_offre()`

Pour chaque offre :

1. nettoie le nom pour l'affichage ;
2. calcule le nom normalisé ;
3. détecte une éventuelle faute de marque ;
4. convertit le prix ;
5. vérifie la cohérence avec l'ancien prix ;
6. calcule le prix payé (remise + livraison) ;
7. applique la disponibilité.

C'est ici que le prix de `779 000 FCFA` est écarté.

#### `dedupliquer()`

Utilise un `set` de couples `(source, référence)`. Si le couple est déjà vu,
la ligne est ignorée et journalisée. Complexité : `O(n)`.

### 6.6 Le rapprochement : reconnaître le même produit

C'est la partie la plus interessante du projet.

#### Étape 1 : la signature

Pour chaque nom normalisé, on extrait :

- les **mots** ;
- la **marque** (Samsung, HP, Lenovo…) ;
- les **capacités** (`128gb`, `1tb`, `1.5l`, `1hp`) ;
- les **modèles** (`a15`, `g9`, `i5`, `m185`, `2720e`).

Exemple :

```text
"hp 250 g9 i5 8gb 512gb"
→ mots     : {hp, 250, g9, i5, 8gb, 512gb}
→ marque   : HP
→ capacités: {8gb, 512gb}
→ modèles  : {g9, i5}
```

#### Étape 2 : l'index inversé

Au lieu de comparer chaque offre aux 30 produits, on construit :

```text
mot → liste des produits qui contiennent ce mot
```

Exemple :

```text
hp   → [P11, P17]
a15  → [P01]
1hp  → [P24]
```

Une offre ne compare donc qu'aux produits qui partagent au moins un mot. C'est
ce qui évite le `O(n × m)`.

#### Étape 3 : les règles de rejet

Un candidat est refusé si :

- la **marque** est différente (`LG` vs `Hisense`) ;
- la **capacité** est différente (`128gb` vs `256gb`) ;
- le **modèle** est différent (`a15` vs `a25`, `i3` vs `i5`).

C'est ce qui évite de confondre :

- Samsung Galaxy A15 / A25 / A55 ;
- HP 250 G9 / Lenovo IdeaPad 3 / Dell Inspiron 15 ;
- Climatiseur LG 1 CV / Climatiseur Hisense 1,5 CV.

#### Étape 4 : le score

Pour les candidats restants :

```text
rappel    = mots communs / mots du produit de référence
précision = mots communs / mots de l'offre
F1        = 2 × rappel × précision / (rappel + précision)
score     = 0,7 × F1 + 0,2 × rappel + 0,1 × bonus de marque
```

- `rappel` : « ai-je retrouvé les mots importants du catalogue ? »
- `précision` : « l'offre contient-elle beaucoup de mots parasites ? »
- `F1` : compromis entre les deux.
- `bonus de marque` : 1 si la marque est la même, 0 sinon.

Si le score est inférieur à **0,60**, l'offre n'est pas reconnue. Si le score
est inférieur à **0,80**, la correspondance est acceptée mais signalée dans le
journal pour vérification.

Exemples réels :

| Offre | Score | Décision |
|---|---:|---|
| `HP 250 G9 i5` (Comptoir) | 0,79 | associé à P11 |
| `Seagate Expansion 1TB` (Baobab) | 0,67 | associé à P15 |
| `Samsun Galaxy A15 128Go` | 0,92 | associé à P01, marque corrigée |

#### Pourquoi le seuil 0,60 ?

Il a été choisi après observation des scores sur ce catalogue :

- les vrais matchs sont généralement au-dessus de 0,65 ;
- les faux matchs (A15 vs A25) sont bloqués par les règles de modèle ;
- 0,60 laisse passer les noms très différents comme `Seagate Expansion 1TB`,
  tout en restant prudent.

C'est un **paramètre métier**, pas une vérité absolue. On pourrait l'ajuster
avec un autre catalogue.

### 6.7 La comparaison

`comparer()` regroupe les offres par `produit_id` :

```python
par_produit[offre.produit_id][offre.source] = offre
```

Si une boutique propose deux fois le même produit, on garde la moins chère.

Ensuite, pour chaque produit du catalogue :

- s'il y a moins de deux boutiques disponibles → `ProduitNonCompare` ;
- sinon → calcul :

```text
prix_min = min(prix payés)
prix_max = max(prix payés)
écart    = prix_max − prix_min
écart %  = écart / prix_min × 100
```

La meilleure boutique est celle qui a le `prix_min`. En cas d'égalité,
plusieurs boutiques sont affichées.

La synthèse calcule :

- le nombre de victoires par boutique (égalités comprises) ;
- le surcoût moyen :

```text
surcoût moyen = moyenne((prix_boutique − prix_min) / prix_min × 100)
```

- le top 3 des écarts en FCFA ;
- le top 3 des écarts en pourcentage ;
- la liste des produits non comparés.

Le tableau est trié par écart décroissant : les décisions les plus
intéressantes apparaissent en haut.

### 6.8 Le panier

Le panier imposé est :

```python
PANIER_RENTREE = [
    ("P04", 1),   # Tecno Spark 20
    ("P12", 1),   # Lenovo IdeaPad 3
    ("P14", 2),   # 2 clés USB SanDisk
    ("P15", 1),   # disque dur Seagate
    ("P28", 1),   # micro-ondes Samsung
]
```

Pour chaque article, on prend l'offre disponible la moins chère, puis on
multiplie par la quantité. Le total optimal est la **somme des minima**.

#### Pourquoi la somme des minima est-elle optimale ?

Parce que les articles sont **indépendants** :

- pas de frais fixes par commande ;
- pas de coût de déplacement ;
- pas de contrainte « tout dans la même boutique ».

Donc si un article coûte moins cher chez A et un autre moins cher chez B, il
faut acheter le premier chez A et le second chez B. Le coût total est la somme
des meilleurs prix. Ce n'est **pas** le minimum des totaux par boutique.

> Si on ajoutait des frais de livraison fixes par boutique, le problème
> deviendrait plus complexe (proche d'un problème de couverture / sac à dos).
> C'est une extension possible, à mentionner comme limite.

Le programme calcule aussi le coût si l'on achète **tout dans une seule
boutique**, mais seulement si cette boutique a tous les articles. C'est ce qui
permet de comparer :

- `477 575 FCFA` en éclatant les achats ;
- `484 075 FCFA` chez Comptoir Ivoire ;
- économie : `6 500 FCFA`.

### 6.9 L'historique

`historique_prix.csv` contient 20 876 lignes. Le chargement construit deux
index en une seule lecture :

```python
self.par_source[source].append(releve)
self.par_cle[(source, produit_id)].append(releve)
```

- `par_source` sert aux moyennes par enseigne ;
- `par_cle` sert à la recherche d'un produit dans une enseigne.

Pour chaque enseigne :

```text
moyenne annuelle = moyenne de tous les prix
moyenne BF       = moyenne des prix du 24 au 30 novembre 2025
variation %      = (moyenne BF − moyenne annuelle) / moyenne annuelle × 100
```

Une variation négative signifie que le Black Friday était moins cher.

Le programme calcule aussi le **mois le moins cher** : il regroupe les prix par
`AAAA-MM`, fait la moyenne, puis prend le mois dont la moyenne est minimale.

Point important : pour Comptoir Ivoire, l'historique contient le **prix
catalogue**, sans la remise. C'est précisé dans l'énoncé. C'est pour cela que
sa variation Black Friday n'est pas comparable directement aux deux autres.

### 6.10 Le benchmark

Le benchmark répond à la consigne « mesurer le temps et expliquer les choix de
structures de données ».

#### Recherche dans l'historique

- **Naïve** : parcourir les 20 876 lignes pour chaque requête → `O(q × n)`.
- **Indexée** : dictionnaire `(source, produit_id)` → `O(1)` par requête,
  donc `O(q)` pour `q` requêtes.

```python
def rechercher_naif(self, source, produit_id):
    return [r for r in self.releves
            if r.source == source and r.produit_id == produit_id]

def rechercher_index(self, source, produit_id):
    return self.par_cle.get((source, produit_id), [])
```

#### Recherche dans un catalogue synthétique

Le benchmark crée des catalogues de 1 000, 5 000 et 20 000 produits, puis
compare :

- une boucle qui parcourt tout le catalogue ;
- un dictionnaire `nom → produit`.

Résultat typique : la version indexée est plusieurs fois plus rapide, et
l'écart se creuse quand le catalogue grandit.

#### Pourquoi les temps varient

Les temps dépendent de la machine, du système et des autres programmes. Les
chiffres du README sont des exemples. Ce qui compte, c'est le **rapport** entre
les deux versions, pas la milliseconde près.

### 6.11 Les vues

#### `Views/Interface.py`

Affiche :

- les titres et tableaux console ;
- le comparatif ;
- la synthèse ;
- le panier ;
- l'historique ;
- le journal ;
- le benchmark ;
- les temps.

Elle ne calcule rien : elle reçoit `ResultatAnalyse` et formate.

#### `Views/html_view.py`

Génère un fichier HTML **autonome** : pas de serveur, pas de bibliothèque
externe. On peut l'ouvrir directement dans un navigateur ou l'envoyer au
professeur.

Le HTML contient :

- la collecte et le rapprochement ;
- le journal ;
- le comparatif ;
- la synthèse ;
- le panier ;
- l'historique ;
- le benchmark ;
- les temps par étape.

### 6.12 Les tests

`tests/test_services.py` contient 10 tests :

1. conversion des prix ;
2. normalisation des noms et unités ;
3. correction de la marque `Samsun` → Samsung ;
4. prix payé avec livraison et avec remise ;
5. exclusion d'un prix incohérent ;
6. dédoublonnage ;
7. rapprochement de deux produits ;
8. comparaison min/max/écart ;
9. panier et économie ;
10. moyenne Black Friday et égalité naïve/indexée.

Le chiffre à retenir est « 10 tests unitaires ».

Pourquoi tester ? Pour prouver que les règles fonctionnent sans lancer tout le
programme, et pour éviter les régressions quand on modifie le code.

---

## 7. Les résultats à présenter

### 7.1 Chiffres globaux

| Indicateur | Valeur |
|---|---:|
| Produits de référence | 30 |
| Offres collectées | 76 |
| Produits comparés | 23 |
| Produits non comparés | 7 |

Les 7 produits non comparés :

- **P03** Samsung Galaxy A55 : aucune offre disponible (ruptures) ;
- **P08, P13, P18, P19, P25, P30** : une seule boutique disponible.

### 7.2 Victoires

| Boutique | Produits où elle est la moins chère |
|---|---:|
| Comptoir Ivoire | 10 |
| Baobab Shop | 9 |
| Marché Lagune | 6 |

Il y a **2 égalités** : souris Logitech M185 (P16) et fer Philips (P27),
moins chers au même prix chez Marché et Comptoir.

### 7.3 Surcoût moyen par rapport au prix le plus bas

| Boutique | Surcoût moyen |
|---|---:|
| Comptoir Ivoire | 2,8 % |
| Marché Lagune | 3,8 % |
| Baobab Shop | 4,7 % |

### 7.4 Top 3 des marges en FCFA

| Produit | Meilleure boutique | Prix min | Prix max | Écart |
|---|---|---:|---:|---:|
| P11 — HP 250 G9 | Baobab Shop | 354 200 | 407 000 | **52 800 FCFA** |
| P09 — iPhone 13 | Baobab Shop | 417 200 | 443 700 | **26 500 FCFA** |
| P24 — Climatiseur LG 1 CV | Baobab Shop | 253 300 | 279 300 | **26 000 FCFA** |

### 7.5 Top 3 des écarts relatifs (à surveiller)

| Produit | Écart |
|---|---:|
| P29 — Bouilloire 1,7 L | **26,1 %** |
| P14 — Clé USB SanDisk 64 Go | **19,7 %** |
| P21 — Congélateur Nasco 200 L | **16,0 %** |

### 7.6 Panier

| Boutique | Coût si tout est acheté sur place |
|---|---:|
| Marché Lagune | incomplet (Tecno Spark 20 écarté) |
| Baobab Shop | 491 500 FCFA |
| Comptoir Ivoire | **484 075 FCFA** |

**Meilleure combinaison** : 477 575 FCFA

- 1 Tecno chez Baobab ;
- 1 Lenovo chez Comptoir ;
- 2 clés USB chez Marché ;
- 1 disque dur chez Marché ;
- 1 micro-ondes chez Baobab.

**Économie** : 6 500 FCFA par rapport à la meilleure boutique unique.

### 7.7 Historique

| Boutique | Moyenne annuelle | Black Friday | Variation |
|---|---:|---:|---:|
| Marché Lagune | 161 978 | 143 894 | **−11,2 %** |
| Baobab Shop | 140 913 | 124 579 | **−11,6 %** |
| Comptoir Ivoire | 154 843 | 160 604 | **+3,7 %** |

Le Black Friday était intéressant chez Marché Lagune et Baobab Shop, mais pas
chez Comptoir Ivoire. Le mois le moins cher est **septembre 2026** pour les
trois enseignes.

### 7.8 Benchmark

Exemple de mesure (les temps varient à chaque exécution) :

| Opération | Version naïve | Version indexée | Gain |
|---|---:|---:|---:|
| 500 recherches dans 20 876 lignes | ≈ 254 ms | ≈ 0,1 ms | ×2 300 |
| 100 recherches dans 20 000 produits | ≈ 21 ms | ≈ 1,9 ms | ×11 |

---

## 8. La complexité expliquée simplement

### 8.1 Les lettres

- `n` : nombre de lignes lues (offres ou relevés historiques) ;
- `m` : nombre de produits du catalogue (30) ;
- `q` : nombre de requêtes ;
- `k` : nombre moyen de candidats après l'index (petit).

### 8.2 Les complexités du projet

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

### 8.3 Pourquoi `dict` et `set` sont rapides

Un dictionnaire ou un ensemble utilise une **table de hachage** : on calcule
une clé (`hash`) et on va presque directement à la case mémoire. En moyenne,
l'accès est `O(1)`, alors qu'une recherche dans une liste est `O(n)`.

C'est pour cela que :

- l'historique est indexé par `(source, produit_id)` ;
- les offres sont regroupées par `produit_id` ;
- le rapprochement utilise un index `mot → produits`.

### 8.4 Naïf vs indexé : l'image à retenir

- **Naïf** : chercher une personne dans un annuaire en lisant toutes les pages.
- **Indexé** : ouvrir directement la page grâce à l'index alphabétique.

Le benchmark montre la différence en temps réel.

---

## 9. Lancer le projet

### 9.1 Installation

```powershell
cd "C:\Users\DELL\Documents\LICENCE 2\PROJET-L2\PYTHON\ANALYSE_DU_MARCHE"

# Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# Installer la dépendance
pip install -r requirements.txt
```

Si PowerShell refuse l'activation :

```powershell
.\.venv\Scripts\python.exe -X utf8 main.py
```

### 9.2 Commandes utiles

```powershell
# Analyse complète
python main.py

# Menu interactif
python main.py --menu

# Sans benchmark (plus rapide)
python main.py --no-benchmark

# Tests
python -m unittest discover -s tests -v
```

### 9.3 Fichiers produits

| Fichier | Contenu |
|---|---|
| `reports/comparatif.csv` | tableau produit par produit |
| `reports/journal_nettoyage.csv` | toutes les anomalies et actions |
| `reports/rapport.html` | rapport visuel autonome |

### 9.4 Vérifications avant de rendre

```powershell
python -m unittest discover -s tests -v
python main.py
```

Puis ouvrir `reports/rapport.html` dans un navigateur et vérifier que les
tableaux s'affichent.

---

## 10. Plan d'exposé oral (10–12 minutes)

### Slide 1 — Le problème (1 min)

- Trois boutiques, mêmes produits, noms et prix différents.
- Question : où acheter, et quel écart ?
- Annoncer le pipeline : collecter → normaliser → rapprocher → comparer →
  décider.

### Slide 2 — Les données (1 min 30)

- Les 5 fichiers et les 3 formats.
- Les pièges : doublons, prix en texte, rupture, `779 000 FCFA`, `Samsun`.
- Le journal de nettoyage comme preuve.

### Slide 3 — Architecture MVC (1 min)

- Schéma : Controller → Services/Models → Views.
- Pourquoi : séparer calcul, affichage et orchestration.
- Une phrase : « la vue ne calcule rien, le service ne fait pas de print ».

### Slide 4 — Normalisation et rapprochement (2 min)

- Exemple A15 écrit de trois façons.
- Signature : mots, marque, capacité, modèle.
- Index inversé et score F1.
- Seuil 0,60 et règles de rejet.

### Slide 5 — Comparaison (1 min 30)

- Min, max, écart FCFA et %.
- Exemple HP 250 G9 : 52 800 FCFA, 14,9 %.
- Alerte au-delà de 10 %.

### Slide 6 — Résultats (1 min 30)

- 23 produits comparés sur 30.
- Comptoir 10 victoires, Baobab 9, Marché 6, 2 égalités.
- Top 3 des écarts.

### Slide 7 — Panier (1 min)

- Liste des 5 articles.
- Somme des minima = 477 575 FCFA.
- Meilleure boutique unique = 484 075 FCFA.
- Économie = 6 500 FCFA.
- Pourquoi la somme des minima est optimale ici.

### Slide 8 — Historique (1 min)

- Black Friday : −11,2 % Marché, −11,6 % Baobab, +3,7 % Comptoir.
- Meilleur mois : septembre 2026.
- Limite : Comptoir = prix catalogue sans remise.

### Slide 9 — Complexité (1 min)

- `O(q × n)` vs `O(q)`.
- Résultat du benchmark.
- Pourquoi `dict` et `set`.

### Slide 10 — Conclusion et limites (30 s)

- Ce que le programme sait faire.
- Limites : seuil de matching, pas de frais fixes, historique par enseigne.
- Ouverture : ajouter un nouveau catalogue, optimiser le panier avec des frais.

### Démonstration en direct

Ordre conseillé :

1. montrer l'arborescence ;
2. lancer `python main.py` ;
3. montrer le journal ;
4. montrer le comparatif ;
5. ouvrir `reports/rapport.html` ;
6. lancer les tests.

### Phrases utiles

- « Le prix affiché n'est pas toujours le prix payé : j'ajoute la livraison
  chez Baobab et j'applique la remise chez Comptoir. »
- « Le rapprochement ne compare pas tous les produits à toutes les offres :
  l'index inversé réduit le nombre de candidats. »
- « Une rupture ou un prix absent ne peut jamais gagner la comparaison, grâce
  à `prix_effectif`. »
- « Le panier est optimal article par article car il n'y a pas de frais fixes
  par commande. »

---

## 11. Questions probables du professeur (et réponses)

### 1. Pourquoi avoir choisi le MVC ?

Pour séparer les responsabilités : le modèle contient les données et les
règles, la vue affiche, le contrôleur orchestre. On peut changer l'affichage
ou tester les calculs sans toucher au reste.

### 2. Pourquoi les services sont-ils dans le modèle ?

Parce que ce sont des règles métier, pas de l'affichage. `Models/` contient les
objets, `Services/` contient les traitements. Ensemble, ils forment la couche
Modèle. C'est une séparation MVC enrichie, courante en Python.

### 3. Pourquoi ne pas avoir utilisé pandas ?

Le sujet demande de comprendre les structures de données et la complexité.
Avec pandas, le nettoyage et le rapprochement seraient cachés derrière des
fonctions toutes faites. Ici, tout est explicite : `csv`, `json`, `openpyxl`,
`dict`, `set`. Une seule dépendance externe : `openpyxl`.

### 4. Comment reconnaissez-vous que deux noms désignent le même produit ?

Normalisation (accents, unités, synonymes), signature (marque, capacité,
modèle), index inversé, règles de rejet, puis score F1 + bonus de marque. Le
seuil est 0,60.

### 5. Pourquoi le seuil 0,60 ?

Il laisse passer les vrais matchs (souvent ≥ 0,65) tout en restant prudent. Les
faux matchs sont surtout bloqués par les règles de marque/capacité/modèle. Le
seuil est un paramètre à ajuster selon le catalogue.

### 6. Pourquoi avoir écarté le prix de 779 000 FCFA ?

Parce que l'ancien prix est 88 700 FCFA : le ratio 8,78 est impossible. Plutôt
que d'inventer une correction, le programme écarte l'offre et l'écrit dans le
journal.

### 7. Pourquoi le panier est-il la somme des minima ?

Parce que les articles sont indépendants : pas de frais fixes, pas de
contrainte de boutique. Acheter chaque article au moins cher est donc optimal.
Si on ajoutait des frais fixes, il faudrait un vrai problème d'optimisation.

### 8. Pourquoi seulement 23 produits comparés sur 30 ?

Parce qu'un produit doit être disponible dans au moins deux boutiques avec un
prix exploitable. 7 produits sont soit en rupture partout, soit vendus dans une
seule boutique.

### 9. Pourquoi 2 égalités ?

La souris Logitech M185 et le fer Philips sont au même prix chez Marché et
Comptoir. Le programme affiche les deux boutiques au lieu d'en choisir une au
hasard.

### 10. Pourquoi Comptoir Ivoire a-t-il une variation Black Friday positive ?

Parce que son historique contient le prix catalogue, sans la remise. La
variation mesure donc le prix catalogue, pas le prix réellement payé. C'est une
limite de l'historique fourni, précisée dans l'énoncé.

### 11. Pourquoi les temps du benchmark changent-ils ?

Parce qu'ils dépendent de la machine, du système et de la charge. Ce qui compte
est le rapport entre la version naïve et la version indexée, pas la valeur
exacte.

### 12. Qu'est-ce que le `O(n)` ?

C'est une façon de dire que le temps d'exécution augmente proportionnellement
au nombre d'éléments. `O(n × m)` signifie que l'on compare chaque offre à
chaque produit. `O(1)` signifie un accès direct, presque indépendant de la
taille.

### 13. Que se passe-t-il si un produit n'existe pas dans le catalogue ?

Le rapprochement ne trouve pas de candidat au-dessus du seuil ; l'offre est
ignorée et journalisée. C'est visible dans le journal.

### 14. Quelles sont les limites du projet ?

- Le seuil de matching est réglé pour ce catalogue.
- L'historique est analysé par enseigne, pas produit par produit.
- Le panier suppose l'absence de frais fixes.
- Les données sont fictives.

### 15. Comment ajouter une nouvelle boutique ?

Créer un service de lecture qui produit des `Offre`, ajouter la source dans
`ORDRE_SOURCES`, puis l'appeler dans le contrôleur. Le reste du pipeline ne
change pas : c'est l'intérêt du MVC et des services.

### 16. Pourquoi un journal de nettoyage ?

Pour prouver que les anomalies ont été vues et traitées, et pour permettre au
professeur de vérifier chaque décision. C'est une exigence explicite du sujet.

### 17. Pourquoi un rapport HTML ?

Pour avoir une preuve visuelle, autonome et facile à ouvrir. Le HTML ne dépend
d'aucun serveur : c'est un simple fichier.

---

## 12. Mettre le projet sur GitHub

Le dossier n'est pas encore un dépôt Git au moment de la rédaction. Depuis la
racine du projet :

```powershell
git init
git add .
git commit -m "Analyse comparative de marché - MVC"
git branch -M main
```

Créer ensuite un dépôt **vide** sur GitHub (sans README, sans `.gitignore`),
puis :

```powershell
git remote add origin https://github.com/<votre-utilisateur>/<nom-du-depot>.git
git push -u origin main
```

Avec GitHub CLI :

```powershell
gh auth login
gh repo create <nom-du-depot> --public --source=. --remote=origin --push
```

### Ce qui ne doit pas être commité

Le `.gitignore` exclut déjà :

- `.venv/` ;
- `venv/` ;
- `__pycache__/` ;
- `.idea/` ;
- les fichiers temporaires.

Vérifier avant de pousser :

```powershell
git status
```

### Ce qui doit être commité

- le code (`Models/`, `Services/`, `Views/`, `Controllers/`, `tests/`) ;
- `main.py`, `README.md`, `EXPLICATION.md` ;
- `data/` (les données fictives de l'exercice) ;
- `docs/LISEZ-MOI.md` ;
- `requirements.txt`, `.gitignore` ;
- éventuellement `reports/` si le professeur veut voir les sorties.

> Ne jamais publier de token, de mot de passe ou de clé API. Ici, il n'y en a
> pas.

---

## 13. Checklist avant de rendre

- [ ] `python -m unittest discover -s tests -v` : 10 tests OK.
- [ ] `python main.py` : le programme se termine sans erreur.
- [ ] `reports/rapport.html` s'ouvre dans le navigateur.
- [ ] `reports/comparatif.csv` s'ouvre dans Excel.
- [ ] `reports/journal_nettoyage.csv` contient les anomalies.
- [ ] `README.md` explique l'installation et les résultats.
- [ ] `EXPLICATION.md` est présent.
- [ ] `git status` ne montre pas `.venv/`.
- [ ] Le dépôt GitHub est créé et le `push` est fait.
- [ ] Je sais expliquer :
  - [ ] le pipeline en 5 étapes ;
  - [ ] le rôle de chaque dossier MVC ;
  - [ ] la normalisation et le matching ;
  - [ ] le calcul min/max/écart ;
  - [ ] pourquoi le panier est la somme des minima ;
  - [ ] la différence entre recherche naïve et indexée ;
  - [ ] les limites du projet.

---

## 14. Résumé en une page (pour réviser juste avant)

```text
SUJET
Trois boutiques, un catalogue commun, des noms et des prix différents.
Objectif : dire où acheter chaque produit et quel écart surveiller.

DONNÉES
30 produits, 76 offres, 5 fichiers (CSV, JSON, Excel, historique 20 876 lignes).

PIPELINE
Collecter → Normaliser → Rapprocher → Comparer → Décider → Exporter.

MVC
Models + Services = règles métier.
Views = affichage.
Controllers = orchestration.

NETTOYAGE
Doublons, prix texte, prix absents, ruptures, fautes de marque, unités.
Chaque anomalie → journal.

MATCHING
Normalisation + signature + index inversé + règles + score F1.
Seuil 0,60 ; alerte sous 0,80.

COMPARAISON
Prix payé = prix affiché (Marché), + livraison (Baobab), − remise (Comptoir).
Min, max, écart FCFA, écart %, alerte si ≥ 10 %.

RÉSULTATS
23 produits comparés / 30.
Comptoir 10, Baobab 9, Marché 6, 2 égalités.
Panier optimal 477 575 FCFA ; boutique unique 484 075 FCFA ; économie 6 500.
Black Friday : −11,2 % Marché, −11,6 % Baobab, +3,7 % Comptoir.

COMPLEXITÉ
Naïf O(q × n), indexé O(q) grâce aux dict/set.
Benchmark : plusieurs centaines de fois plus rapide sur l'historique.

LIMITES
Seuil de matching, historique par enseigne, pas de frais fixes, données fictives.
```

---

**Fin du document.** Si tu sais expliquer les sections 4, 5, 6 et 7 avec tes
mots, tu sais présenter le projet.
