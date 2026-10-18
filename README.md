# TD2 - Métaheuristiques et optimisation

Solutions Python des exercices 2 et 3.

## Contenu du dépôt

- `exercise2_transport.py` : problème de transport, recherche taboue et Branch and Bound exact.
- `exercise2_solution.csv` : tableau des livraisons optimal de l'exercice 2.
- `exercise3_tsp.py` : problème du voyageur de commerce, recherche taboue et recuit simulé limité à 5 itérations.
- `solution.md` : formulation, calculs, résultats et comparaison détaillée.

Python 3 suffit ; aucune bibliothèque externe n'est nécessaire.

## Exécution

À partir du dossier du dépôt :

```bash
python exercise2_transport.py
python exercise3_tsp.py
```

Les données de chaque énoncé sont directement définies en haut des fichiers Python.

## Consigne suivie pour l'exercice 3

L'énoncé imprimé propose aussi un algorithme génétique, mais la consigne de l'enseignant transmise pour ce travail demande de traiter l'exercice 3 uniquement par recuit simulé et recherche taboue. Le code et le compte rendu suivent cette consigne.

## Résultats sur les données fournies

- Exercice 2 : la recherche taboue et Branch and Bound donnent un coût de transport de 52.
- Exercice 3 : le circuit initial coûte 103 ; la recherche taboue et le recuit simulé donnent chacun un meilleur circuit de coût 98 avec les paramètres documentés dans `solution.md`.
