"""Optimisation des livraisons - recherche taboue et Branch and Bound.

Aucune bibliothèque externe n'est nécessaire. Lancer : python transport.py
Les données de l'exercice figurent dans EXAMPLE_* ci-dessous.
"""
from itertools import product
from random import Random

EXAMPLE_DEMAND = [4, 5, 8]
EXAMPLE_STOCK = [8, 9]
# lignes = dépôts D1, D2 ; colonnes = magasins M1, M2, M3
EXAMPLE_COSTS = [[5, 3, 4], [6, 7, 2]]


def validate(demand, stock, costs):
    m, n = len(stock), len(demand)
    if not m or not n:
        raise ValueError("Il faut au moins un dépôt et un magasin.")
    if len(costs) != m or any(len(row) != n for row in costs):
        raise ValueError("La matrice des coûts doit être de taille dépôts x magasins.")
    if any(type(v) is not int or v < 0 for v in demand + stock):
        raise ValueError("Demandes et stocks doivent être des entiers positifs ou nuls.")
    if sum(stock) < sum(demand):
        raise ValueError("Le stock total ne permet pas de satisfaire la demande totale.")


def total_cost(x, costs):
    return sum(x[i][j] * costs[i][j]
               for i in range(len(x)) for j in range(len(x[0])))


def greedy(demand, stock, costs):
    """Heuristique de départ : magasin par magasin, routes les moins chères d'abord."""
    remaining = stock[:]
    x = [[0] * len(demand) for _ in stock]
    for j, need in enumerate(demand):
        for i in sorted(range(len(stock)), key=lambda d: costs[d][j]):
            q = min(need, remaining[i])
            x[i][j] += q
            remaining[i] -= q
            need -= q
            if need == 0:
                break
        if need:
            raise ValueError("Stock insuffisant pour construire une solution.")
    return x


def tabu_search(demand, stock, costs, iterations=500, tenure=7, seed=0):
    """Recherche taboue avec mouvements unitaires et échanges entre deux magasins."""
    validate(demand, stock, costs)
    m, n = len(stock), len(demand)
    current = greedy(demand, stock, costs)
    current_cost = total_cost(current, costs)
    best = [row[:] for row in current]
    best_cost = current_cost
    loads = [sum(row) for row in current]
    tabu_states = {}  # état visité -> itération d'expiration
    rng = Random(seed)

    for t in range(iterations):
        neighbors = []
        # Déplacement d'une unité vers un dépôt qui a de la capacité libre.
        for j in range(n):
            for src in range(m):
                if current[src][j] == 0:
                    continue
                for dst in range(m):
                    if src == dst or loads[dst] >= stock[dst]:
                        continue
                    candidate = [row[:] for row in current]
                    candidate[src][j] -= 1
                    candidate[dst][j] += 1
                    neighbors.append(candidate)
        # Échange entre deux dépôts et deux magasins; les stocks restent constants.
        for a in range(m):
            for b in range(a + 1, m):
                for j in range(n):
                    if current[a][j] == 0:
                        continue
                    for k in range(n):
                        if j == k or current[b][k] == 0:
                            continue
                        candidate = [row[:] for row in current]
                        candidate[a][j] -= 1
                        candidate[b][j] += 1
                        candidate[b][k] -= 1
                        candidate[a][k] += 1
                        neighbors.append(candidate)
        if not neighbors:
            break

        # Ne garder que le meilleur coût de chaque état distinct.
        unique = {}
        for candidate in neighbors:
            key = tuple(tuple(row) for row in candidate)
            unique[key] = total_cost(candidate, costs)
        allowed = []
        for key, value in unique.items():
            is_tabu = tabu_states.get(key, -1) > t
            if not is_tabu or value < best_cost:  # critère d'aspiration
                allowed.append((value, key))
        if not allowed:
            # La recherche peut repartir de la meilleure solution connue.
            current = [row[:] for row in best]
            current_cost = best_cost
            tabu_states.clear()
            continue
        low = min(v for v, _ in allowed)
        value, key = rng.choice([(v, k) for v, k in allowed if v == low])
        old_key = tuple(tuple(row) for row in current)
        current = [list(row) for row in key]
        current_cost = value
        tabu_states[old_key] = t + tenure
        if current_cost < best_cost:
            best = [row[:] for row in current]
            best_cost = current_cost
    return best, best_cost


def branch_and_bound(demand, stock, costs):
    """Résolution exacte par énumération avec élagage (adaptée aux petites instances)."""
    validate(demand, stock, costs)
    m, n = len(stock), len(demand)
    incumbent = greedy(demand, stock, costs)
    best_cost = total_cost(incumbent, costs)
    best = [row[:] for row in incumbent]
    current = [[0] * n for _ in range(m)]
    remaining = stock[:]
    nodes = 0
    # Borne inférieure optimiste : chaque demande restante prend son trajet
    # le moins cher, même si ce dépôt n'a plus de capacité. Elle ne surestime
    # donc jamais le coût réalisable et permet un élagage sûr.
    suffix_lb = [0] * (n + 1)
    for j in range(n - 1, -1, -1):
        suffix_lb[j] = suffix_lb[j + 1] + demand[j] * min(costs[i][j] for i in range(m))

    def allocations_for_store(j):
        alloc = [0] * m
        def generate(i, left):
            if i == m - 1:
                if left <= remaining[i]:
                    alloc[i] = left
                    yield alloc[:]
                return
            for q in range(min(left, remaining[i]) + 1):
                alloc[i] = q
                yield from generate(i + 1, left - q)
        yield from generate(0, demand[j])

    def visit(j, cost_so_far):
        nonlocal best, best_cost, nodes
        nodes += 1
        if cost_so_far + suffix_lb[j] >= best_cost:
            return
        if j == n:
            best_cost = cost_so_far
            best = [row[:] for row in current]
            return
        choices = list(allocations_for_store(j))
        choices.sort(key=lambda a: sum(a[i] * costs[i][j] for i in range(m)))
        for allocation in choices:
            added = sum(allocation[i] * costs[i][j] for i in range(m))
            if cost_so_far + added + suffix_lb[j + 1] >= best_cost:
                continue
            for i in range(m):
                current[i][j] = allocation[i]
                remaining[i] -= allocation[i]
            visit(j + 1, cost_so_far + added)
            for i in range(m):
                remaining[i] += allocation[i]
                current[i][j] = 0

    visit(0, 0)
    return best, best_cost, nodes


def print_solution(title, x, demand, stock, costs, cost):
    print(f"\n{title} — coût total = {cost}")
    print("       " + "  ".join(f"M{j+1}" for j in range(len(demand))) + "  Total")
    for i, row in enumerate(x):
        print(f"D{i+1:<5} " + "  ".join(f"{q:>2}" for q in row) + f"  {sum(row):>2}/{stock[i]}")
    totals = [sum(x[i][j] for i in range(len(stock))) for j in range(len(demand))]
    print("Livrés " + "  ".join(f"{q:>2}" for q in totals) + "  (demande satisfaite)")


def main():
    d, s, c = EXAMPLE_DEMAND, EXAMPLE_STOCK, EXAMPLE_COSTS
    initial = greedy(d, s, c)
    tabu, tabu_cost = tabu_search(d, s, c)
    exact, exact_cost, nodes = branch_and_bound(d, s, c)
    print_solution("Départ glouton", initial, d, s, c, total_cost(initial, c))
    print_solution("Recherche taboue", tabu, d, s, c, tabu_cost)
    print_solution("Branch and Bound (exact)", exact, d, s, c, exact_cost)
    print(f"Nœuds visités par Branch and Bound : {nodes}")
    gap = 100 * (tabu_cost - exact_cost) / exact_cost if exact_cost else 0
    print(f"Écart taboue / optimum exact : {gap:.2f} %")


if __name__ == "__main__":
    main()
