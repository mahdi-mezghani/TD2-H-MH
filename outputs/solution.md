# Compte rendu : optimisation des livraisons

## 1. Problème

Une entreprise doit livrer trois magasins à partir de deux dépôts. Les containers sont indivisibles. Le but est de satisfaire toutes les demandes tout en minimisant le coût de transport.

### Données

| Dépôt | Coût vers M1 | Coût vers M2 | Coût vers M3 | Stock |
|---|---:|---:|---:|---:|
| D1 | 5 | 3 | 4 | 8 |
| D2 | 6 | 7 | 2 | 9 |
| Demande | 4 | 5 | 8 | |

Le stock total vaut `8 + 9 = 17`, et la demande totale vaut `4 + 5 + 8 = 17`. Il faut donc utiliser tout le stock.

## 2. Formulation en programmation linéaire en nombres entiers

On définit `x_ij` comme le nombre de containers expédiés de `D_i` vers `M_j`. La fonction objectif est :

`Min Z = 5x11 + 3x12 + 4x13 + 6x21 + 7x22 + 2x23`

Contraintes de demande :

- `x11 + x21 = 4` (M1)
- `x12 + x22 = 5` (M2)
- `x13 + x23 = 8` (M3)

Contraintes de stock :

- `x11 + x12 + x13 <= 8` (D1)
- `x21 + x22 + x23 <= 9` (D2)

Enfin, `x_ij` est entier et positif ou nul.

## 3. Solution proposée

| Dépôt | M1 | M2 | M3 | Total expédié / stock |
|---|---:|---:|---:|---:|
| D1 | 3 | 5 | 0 | 8 / 8 |
| D2 | 1 | 0 | 8 | 9 / 9 |
| Total livré / demande | 4 / 4 | 5 / 5 | 8 / 8 | |

Vérification du coût : `3×5 + 5×3 + 1×6 + 8×2 = 15 + 15 + 6 + 16 = 52`.

## 4. Pourquoi cette répartition est optimale

Puisque les stocks totalisent exactement 17, toute solution faisable expédie 8 unités de D1 et 9 de D2. On peut comparer chaque container de D1 avec le coût qu'aurait le même container depuis D2 :

- vers M1, D1 économise `6 - 5 = 1` ;
- vers M2, D1 économise `7 - 3 = 4` ;
- vers M3, D1 coûte `4 - 2 = 2` de plus.

Pour utiliser les 8 containers de D1, il est donc optimal de servir d'abord M2 (5 unités, économie de 20), puis 3 unités de M1 (économie de 3). Les 1 unité restante de M1 et les 8 unités de M3 viennent de D2. On obtient le coût 52.

On peut aussi vérifier que les huit unités de D1 contribuent au moins à `5×3 + 3×5 = 30` pour cette affectation optimale tandis que les volumes restants de D2 coûtent `1×6 + 8×2 = 22` ; total 52. Les économies par container ci-dessus montrent que toute autre affectation de D1 a un coût égal ou supérieur.

## 5. Méthodes comparées

### Méthode gloutonne

Elle parcourt les magasins dans l'ordre et affecte chaque demande aux dépôts proposant le coût unitaire le plus faible parmi ceux qui ont encore du stock. Elle est facile et rapide, mais une décision locale peut consommer un stock utile pour un autre magasin. Ici, elle donne `D1 = (4, 4, 0)` et `D2 = (0, 1, 8)`, soit un coût de 55.

### Recherche taboue

La solution initiale est gloutonne. À chaque itération, le voisinage essaie des transferts d'un container vers un dépôt ayant de la capacité disponible et des échanges d'un container entre deux dépôts sur deux magasins. Les échanges sont indispensables ici, car toute la capacité est consommée : un simple transfert serait impossible. Une liste taboue empêche de revisiter immédiatement certains états ; le critère d'aspiration autorise un état tabou s'il améliore le meilleur résultat global. Sur les données de l'exercice, la recherche atteint le coût 52.

La recherche taboue est une heuristique. Elle ne prouve pas l'optimalité pour toutes les instances ; le résultat peut dépendre de la solution initiale, de la graine aléatoire, du nombre d'itérations et de la durée taboue.

### Branch and Bound

Cette méthode exacte explore les allocations entières possibles magasin par magasin. Elle conserve la meilleure solution connue et coupe une branche lorsque sa borne inférieure ne peut pas battre cette solution. Elle retourne 52 et garantit que c'est l'optimum. Le temps de calcul peut toutefois augmenter fortement avec le nombre de dépôts, de magasins et les volumes.

| Algorithme | Coût sur l'exemple | Conclusion |
|---|---:|---|
| Glouton | 55 | Très rapide, résultat initial non optimal |
| Recherche taboue | 52 | Atteint l'optimum ici, sans preuve générale |
| Branch and Bound | 52 | Optimum prouvé pour ces données |

L'écart relatif de la recherche taboue par rapport à l'optimum exact est de 0 % sur cet exemple.

## 6. Exécution

Exécuter `python transport.py` depuis le dossier contenant le fichier. Le script ne nécessite pas de bibliothèque supplémentaire. Les données modifiables se trouvent en haut du script.

## 7. Conclusion

La livraison la moins coûteuse consiste à envoyer 3 containers de D1 à M1, 5 de D1 à M2, 1 de D2 à M1 et 8 de D2 à M3. Le coût minimal est de 52 unités monétaires. La recherche taboue fournit rapidement une bonne solution, tandis que Branch and Bound confirme l'optimalité sur cette petite instance.

