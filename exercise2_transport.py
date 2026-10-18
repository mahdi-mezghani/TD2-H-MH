"""Exercice 2 - transport : recherche taboue et Branch and Bound.

Python 3, aucune dépendance externe. Lancer : python exercise2_transport.py
"""
from random import Random

DEMANDES = [4, 5, 8]
STOCKS = [8, 9]
# Lignes = dépôts D1, D2 ; colonnes = magasins M1, M2, M3
COUTS = [[5, 3, 4], [6, 7, 2]]


def verifier(demandes, stocks, couts):
    if not stocks or not demandes:
        raise ValueError("Il faut au moins un dépôt et un magasin.")
    if len(couts) != len(stocks) or any(len(ligne) != len(demandes) for ligne in couts):
        raise ValueError("La matrice des coûts doit avoir une ligne par dépôt et une colonne par magasin.")
    if any(type(v) is not int or v < 0 for v in demandes + stocks):
        raise ValueError("Les demandes et stocks doivent être des entiers positifs ou nuls.")
    if sum(stocks) < sum(demandes):
        raise ValueError("Le stock total est inférieur à la demande totale.")


def cout_total(x, couts):
    return sum(x[i][j] * couts[i][j]
               for i in range(len(x)) for j in range(len(x[0])))


def solution_gloutonne(demandes, stocks, couts):
    """Solution faisable de départ : traite les magasins dans l'ordre donné."""
    restant = stocks[:]
    x = [[0] * len(demandes) for _ in stocks]
    for j, besoin_initial in enumerate(demandes):
        besoin = besoin_initial
        for i in sorted(range(len(stocks)), key=lambda depot: couts[depot][j]):
            q = min(besoin, restant[i])
            x[i][j] += q
            restant[i] -= q
            besoin -= q
            if besoin == 0:
                break
        if besoin:
            raise ValueError("Impossible de satisfaire toutes les demandes avec les stocks fournis.")
    return x


def recherche_taboue(demandes, stocks, couts, iterations=200, duree_taboue=7, graine=0):
    """Recherche taboue avec transferts et échanges d'une unité entre deux magasins."""
    verifier(demandes, stocks, couts)
    nb_depots, nb_magasins = len(stocks), len(demandes)
    courant = solution_gloutonne(demandes, stocks, couts)
    meilleur = [ligne[:] for ligne in courant]
    cout_meilleur = cout_total(meilleur, couts)
    tabu = {}  # signature d'une solution -> itération d'expiration
    rng = Random(graine)

    for t in range(iterations):
        charges = [sum(ligne) for ligne in courant]
        voisins = {}
        # Transfert simple : utile si un dépôt a du stock inutilisé.
        for j in range(nb_magasins):
            for source in range(nb_depots):
                if courant[source][j] == 0:
                    continue
                for destination in range(nb_depots):
                    if source == destination or charges[destination] >= stocks[destination]:
                        continue
                    candidat = [ligne[:] for ligne in courant]
                    candidat[source][j] -= 1
                    candidat[destination][j] += 1
                    signature = tuple(tuple(ligne) for ligne in candidat)
                    voisins[signature] = cout_total(candidat, couts)
        # Echange : garde les demandes et stocks identiques; indispensable si tout le stock est utilisé.
        for a in range(nb_depots):
            for b in range(a + 1, nb_depots):
                for j in range(nb_magasins):
                    if courant[a][j] == 0:
                        continue
                    for k in range(nb_magasins):
                        if j == k or courant[b][k] == 0:
                            continue
                        candidat = [ligne[:] for ligne in courant]
                        candidat[a][j] -= 1
                        candidat[b][j] += 1
                        candidat[b][k] -= 1
                        candidat[a][k] += 1
                        signature = tuple(tuple(ligne) for ligne in candidat)
                        voisins[signature] = cout_total(candidat, couts)
        if not voisins:
            break

        admissibles = [(signature, cout) for signature, cout in voisins.items()
                       if tabu.get(signature, -1) <= t or cout < cout_meilleur]
        if not admissibles:  # diversification si tous les voisins sont tabous
            admissibles = list(voisins.items())
        cout_min = min(cout for _, cout in admissibles)
        signature, cout = rng.choice([(sig, c) for sig, c in admissibles if c == cout_min])
        ancienne_signature = tuple(tuple(ligne) for ligne in courant)
        courant = [list(ligne) for ligne in signature]
        tabu[ancienne_signature] = t + duree_taboue
        if cout < cout_meilleur:
            meilleur = [ligne[:] for ligne in courant]
            cout_meilleur = cout
    return meilleur, cout_meilleur


def branch_and_bound(demandes, stocks, couts):
    """Résolution exacte par séparation et évaluation, pour petites instances."""
    verifier(demandes, stocks, couts)
    nb_depots, nb_magasins = len(stocks), len(demandes)
    meilleur = solution_gloutonne(demandes, stocks, couts)
    cout_meilleur = cout_total(meilleur, couts)
    courant = [[0] * nb_magasins for _ in stocks]
    restant = stocks[:]
    noeuds = 0

    # Borne inférieure admissible : coût minimal indépendant pour chaque magasin restant.
    borne_suffixe = [0] * (nb_magasins + 1)
    for j in range(nb_magasins - 1, -1, -1):
        borne_suffixe[j] = borne_suffixe[j + 1] + demandes[j] * min(couts[i][j] for i in range(nb_depots))

    def allocations_magasin(j):
        allocation = [0] * nb_depots
        def generer(i, reste):
            if i == nb_depots - 1:
                if reste <= restant[i]:
                    allocation[i] = reste
                    yield allocation[:]
                return
            for q in range(min(reste, restant[i]) + 1):
                allocation[i] = q
                yield from generer(i + 1, reste - q)
        yield from generer(0, demandes[j])

    def explorer(j, cout_partiel):
        nonlocal meilleur, cout_meilleur, noeuds
        noeuds += 1
        if cout_partiel + borne_suffixe[j] >= cout_meilleur:
            return
        if j == nb_magasins:
            meilleur = [ligne[:] for ligne in courant]
            cout_meilleur = cout_partiel
            return
        options = list(allocations_magasin(j))
        options.sort(key=lambda a: sum(a[i] * couts[i][j] for i in range(nb_depots)))
        for allocation in options:
            cout_j = sum(allocation[i] * couts[i][j] for i in range(nb_depots))
            if cout_partiel + cout_j + borne_suffixe[j + 1] >= cout_meilleur:
                continue
            for i in range(nb_depots):
                courant[i][j] = allocation[i]
                restant[i] -= allocation[i]
            explorer(j + 1, cout_partiel + cout_j)
            for i in range(nb_depots):
                restant[i] += allocation[i]
                courant[i][j] = 0

    explorer(0, 0)
    return meilleur, cout_meilleur, noeuds


def afficher_solution(nom, x, demandes, stocks, couts, cout):
    print(f"\n{nom} — coût total : {cout}")
    print("       " + "  ".join(f"M{j + 1}" for j in range(len(demandes))) + "  Expédié/stock")
    for i, ligne in enumerate(x):
        print(f"D{i + 1:<5} " + "  ".join(f"{q:>2}" for q in ligne) + f"  {sum(ligne)}/{stocks[i]}")
    livres = [sum(x[i][j] for i in range(len(stocks))) for j in range(len(demandes))]
    print("Livré  " + "  ".join(f"{q:>2}/{demandes[j]}" for j, q in enumerate(livres)))


def main():
    verifier(DEMANDES, STOCKS, COUTS)
    glouton = solution_gloutonne(DEMANDES, STOCKS, COUTS)
    tabu, cout_tabu = recherche_taboue(DEMANDES, STOCKS, COUTS)
    exact, cout_exact, noeuds = branch_and_bound(DEMANDES, STOCKS, COUTS)
    afficher_solution("Solution gloutonne de départ", glouton, DEMANDES, STOCKS, COUTS,
                      cout_total(glouton, COUTS))
    afficher_solution("Recherche taboue", tabu, DEMANDES, STOCKS, COUTS, cout_tabu)
    afficher_solution("Branch and Bound", exact, DEMANDES, STOCKS, COUTS, cout_exact)
    print(f"Nœuds examinés par Branch and Bound : {noeuds}")


if __name__ == "__main__":
    main()
