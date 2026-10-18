# Compte rendu - TD2 : optimisation combinatoire

Ce compte rendu traite les exercices 2 et 3 à partir des données communiquées. Tous les coûts sont exprimés en unités de coût, puisque l'énoncé ne précise pas de monnaie.

## Exercice 2 - Problème de transport

### Données

Les demandes sont M1 = 4, M2 = 5, M3 = 8 containers. Les stocks et coûts unitaires lus dans le tableau sont :

| Dépôt | M1 | M2 | M3 | Stock |
|---|---:|---:|---:|---:|
| D1 | 5 | 3 | 4 | 8 |
| D2 | 6 | 7 | 2 | 9 |
| Demande | 4 | 5 | 8 | |

Le stock total est 17 et la demande totale est 17 : toutes les unités disponibles doivent être livrées.

### Modèle en programmation linéaire en nombres entiers

Soit `x_ij` le nombre entier de containers transportés du dépôt `D_i` au magasin `M_j`.

Minimiser :

`Z = 5x11 + 3x12 + 4x13 + 6x21 + 7x22 + 2x23`

Sous les contraintes de demandes :

- `x11 + x21 = 4` (M1)
- `x12 + x22 = 5` (M2)
- `x13 + x23 = 8` (M3)

Et les contraintes de stock :

- `x11 + x12 + x13 <= 8` (D1)
- `x21 + x22 + x23 <= 9` (D2)
- `x_ij` entier et positif ou nul.

### Solution

| Dépôt | M1 | M2 | M3 | Total expédié / stock |
|---|---:|---:|---:|---:|
| D1 | 3 | 5 | 0 | 8 / 8 |
| D2 | 1 | 0 | 8 | 9 / 9 |
| Total livré / demande | 4 / 4 | 5 / 5 | 8 / 8 | |

Coût : `3×5 + 5×3 + 1×6 + 8×2 = 15 + 15 + 6 + 16 = 52`.

### Recherche taboue et Branch and Bound

Le point de départ glouton livre M1 depuis D1 jusqu'à épuisement du besoin, puis fait de même pour M2 et M3. Il trouve `D1 = (4, 4, 0)` et `D2 = (0, 1, 8)`, de coût 55.

Dans la recherche taboue, un voisin déplace une unité vers un dépôt ayant du stock libre ou échange une unité entre deux magasins et deux dépôts. L'échange est nécessaire ici, car tout le stock est utilisé. La recherche taboue trouve l'allocation ci-dessus, de coût 52. La liste taboue retient des états récents pour limiter les retours immédiats ; le critère d'aspiration autorise un état tabou s'il améliore le meilleur coût connu.

Le Branch and Bound explore les répartitions entières magasin par magasin. Sa borne inférieure estime le coût minimal possible des demandes restantes en ignorant provisoirement les limites de stock ; elle ne surestime donc pas le coût d'une solution réalisable. Les branches qui ne peuvent plus battre la meilleure solution connue sont coupées. Sur ces données, il confirme le coût optimal 52 (5 nœuds examinés par l'implémentation fournie).

| Méthode | Coût | Interprétation |
|---|---:|---|
| Glouton (solution de départ) | 55 | Rapide, mais pas optimal ici |
| Recherche taboue | 52 | Bonne solution heuristique |
| Branch and Bound | 52 | Optimum prouvé pour cette instance |

### Vérification de l'optimalité

Comme le stock total est égal à la demande, les 8 containers de D1 sont tous utilisés. Par rapport à D2, chaque container de D1 économise 1 unité de coût pour M1, 4 pour M2, et ajoute 2 pour M3. Il faut donc affecter les 5 unités de M2 à D1 (économie 20), puis les 3 unités restantes de D1 à M1 (économie 3). Les autres unités viennent de D2. Cela donne 52 et explique l'allocation trouvée.

## Exercice 3 - Voyageur de commerce

### Graphe et hypothèses

Les tirets du tableau représentent des liaisons interdites. Le problème est traité comme un graphe non orienté : le coût de `i` vers `j` est égal à celui de `j` vers `i`, conformément à la présentation triangulaire des données. Un circuit n'est valide que si toutes ses liaisons figurent dans le tableau.

| Ville | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | - | 14 | 15 | - | - | - | - | 17 |
| 2 | 14 | - | 13 | 14 | 20 | - | - | 21 |
| 3 | 15 | 13 | - | 11 | 21 | 17 | 9 | 9 |
| 4 | - | 14 | 11 | - | 11 | 10 | 8 | 20 |
| 5 | - | 20 | 21 | 11 | - | 15 | 18 | - |
| 6 | - | - | 17 | 10 | 15 | - | 9 | - |
| 7 | - | - | 9 | 8 | 18 | 9 | - | 13 |
| 8 | 17 | 21 | 9 | 20 | - | - | 13 | - |

Le circuit initial imposé est `1-2-3-4-5-6-7-8-1`. Son coût est :

`14 + 13 + 11 + 11 + 15 + 9 + 13 + 17 = 103`.

### Voisinage commun

Les deux algorithmes gardent la ville 1 en première position et construisent des voisins en échangeant les positions de deux autres villes. Les circuits qui utilisent une liaison interdite sont rejetés.

### Recherche taboue

La recherche examine les voisins faisables, choisit le meilleur voisin non tabou (même s'il est temporairement plus coûteux), et garde le meilleur circuit global. Les états visités sont tabous pendant 5 itérations ; un circuit qui améliore le meilleur connu reste autorisé (aspiration). La limite d'exécution est 100 itérations.

Meilleur circuit obtenu : `1-2-4-5-6-7-3-8-1`.

Coût : `14 + 14 + 11 + 15 + 9 + 9 + 9 + 17 = 98`.

### Recuit simulé

Le recuit simulé part du même circuit initial et effectue exactement 5 itérations. Une proposition de coût inférieur ou égal est acceptée. Une hausse `Δ` est acceptée avec probabilité `exp(-Δ/T)`.

Pour choisir empiriquement `T0`, on calcule la hausse moyenne positive `Δmoy` parmi les voisins faisables du circuit initial, puis on règle `T0 = -Δmoy / ln(0,80)`. Cette calibration donne une probabilité initiale de 80 % d'accepter une hausse de taille moyenne. La température décroît ensuite selon `T(k+1) = 0,80 × T(k)`. La graine pseudo-aléatoire fixe à 20 rend le parcours reproductible.

| Itération | T avant l'itération | Variation Δ | Décision | Coût courant après décision |
|---:|---:|---:|---|---:|
| Départ | - | - | - | 103 |
| 1 | 36,972 | +9 | Acceptée | 112 |
| 2 | 29,577 | -1 | Acceptée | 111 |
| 3 | 23,662 | -12 | Acceptée | 99 |
| 4 | 18,929 | -1 | Acceptée | 98 |
| 5 | 15,144 | +11 | Rejetée | 98 |

Meilleur circuit obtenu en 5 itérations : `1-2-4-5-6-7-3-8-1`, de coût 98.

### Comparaison

| Méthode | Paramètres | Meilleur coût | Circuit correspondant |
|---|---|---:|---|
| Circuit initial | - | 103 | 1-2-3-4-5-6-7-8-1 |
| Recherche taboue | 100 itérations max., durée taboue 5 | 98 | 1-2-4-5-6-7-3-8-1 |
| Recuit simulé | 5 itérations, `T0=36,972`, `alpha=0,80`, graine 20 | 98 | 1-2-4-5-6-7-3-8-1 |

Les deux méthodes améliorent le circuit initial de 5 unités de coût, soit environ 4,85 %. Ce résultat compare seulement les paramètres indiqués ; le recuit simulé étant stochastique et limité à 5 itérations, d'autres graines ou réglages peuvent produire un autre résultat. Aucun algorithme génétique n'est inclus, conformément à la consigne de l'enseignant transmise pour l'exercice 3.

## Exécution

Depuis la racine du dépôt, avec Python 3 :

```bash
python exercise2_transport.py
python exercise3_tsp.py
```

Aucune bibliothèque tierce n'est requise.

