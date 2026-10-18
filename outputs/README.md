# Optimisation des livraisons de containers

Ce projet résout le problème de transport de l'exercice avec une recherche taboue, puis compare le résultat à une résolution exacte par Branch and Bound.

## Données de l'énoncé

- Demandes : M1 = 4, M2 = 5, M3 = 8 containers.
- Stocks : D1 = 8, D2 = 9 containers.
- Coût par container :

| Dépôt | M1 | M2 | M3 | Stock |
|---|---:|---:|---:|---:|
| D1 | 5 | 3 | 4 | 8 |
| D2 | 6 | 7 | 2 | 9 |
| Demande | 4 | 5 | 8 |  |

Les stocks totalisent 17, exactement comme les demandes.

## Modèle mathématique

Soit `x[i][j]` le nombre entier de containers envoyés du dépôt `i` au magasin `j`, `c[i][j]` leur coût unitaire, `s[i]` le stock du dépôt et `d[j]` la demande du magasin.

Minimiser `sum(c[i][j] * x[i][j])`, sous les contraintes :

- pour chaque magasin `j`, `sum_i x[i][j] = d[j]` ;
- pour chaque dépôt `i`, `sum_j x[i][j] <= s[i]` ;
- `x[i][j]` est un entier positif ou nul.

## Solution obtenue

| Dépôt | M1 | M2 | M3 | Total expédié |
|---|---:|---:|---:|---:|
| D1 | 3 | 5 | 0 | 8 / 8 |
| D2 | 1 | 0 | 8 | 9 / 9 |
| Total livré | 4 / 4 | 5 / 5 | 8 / 8 |  |

Coût : `3×5 + 5×3 + 1×6 + 8×2 = 52` unités monétaires.

## Comparaison des méthodes

- **Glouton** : affecte les magasins dans l'ordre et choisit à chaque fois les trajets les moins chers encore disponibles. C'est rapide et fournit une solution de départ, mais l'ordre peut la rendre sous-optimale. Ici, il trouve un coût de 55.
- **Recherche taboue** : explore les solutions voisines en faisant des transferts unitaires ou des échanges entre deux magasins. La liste taboue évite les retours immédiats vers des solutions récentes. C'est une heuristique : elle peut trouver une excellente solution, sans garantie générale d'optimalité. Ici, elle atteint 52.
- **Branch and Bound** : explore les répartitions entières possibles et élimine les branches dont une borne inférieure suffit déjà à prouver qu'elles ne peuvent battre la meilleure solution connue. Il garantit l'optimum, mais peut devenir lent sur de grandes instances. Ici, l'optimum est 52.

| Méthode | Coût obtenu | Garantie d'optimalité |
|---|---:|---|
| Glouton | 55 | Non |
| Recherche taboue | 52 | Non en général |
| Branch and Bound | 52 | Oui |

L'écart relatif de la taboue à l'optimum est `(52 - 52) / 52 × 100 = 0 %` pour ces données. Cette égalité sur un exemple ne constitue pas une garantie pour d'autres données.

## Lancer le programme

Python 3 suffit, sans paquet externe :

```bash
python transport.py
```

Le programme affiche les solutions gloutonne, taboue et exacte, les quantités livrées, les stocks utilisés, le coût et le nombre de nœuds examinés par Branch and Bound.

## Modifier les données

En haut de `transport.py`, modifiez :

- `EXAMPLE_DEMAND` : une demande par magasin ;
- `EXAMPLE_STOCK` : un stock par dépôt ;
- `EXAMPLE_COSTS` : une ligne par dépôt et une colonne par magasin.

La recherche taboue emploie une graine fixe (`seed=0`) pour faciliter la reproductibilité. Ses paramètres (`iterations`, `tenure`) peuvent être ajustés dans l'appel de `tabu_search`.

## Limites

L'énumération Branch and Bound fournie est pédagogique et convient surtout aux petits problèmes. Pour de grandes instances, un solveur spécialisé (par exemple un solveur MILP) est préférable. Le programme suppose des coûts linéaires par container, des demandes obligatoires, des stocks maximaux et aucun coût fixe d'ouverture ou de tournée.


