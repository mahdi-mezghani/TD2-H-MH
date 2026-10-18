"""Exercice 3 - TSP : recherche taboue et recuit simulé.

Le graphe est non orienté et les tirets du tableau représentent des liaisons interdites.
Python 3, aucune dépendance externe. Lancer : python exercise3_tsp.py
"""
from math import exp, log
from random import Random

NB_VILLES = 8
# Tableau triangulaire supérieur retranscrit depuis l'énoncé.
DONNEES = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}
COUTS = [[None] * NB_VILLES for _ in range(NB_VILLES)]
for (a, b), cout in DONNEES.items():
    COUTS[a - 1][b - 1] = cout
    COUTS[b - 1][a - 1] = cout

TOUR_INITIAL = [1, 2, 3, 4, 5, 6, 7, 8]


def cout_tour(tour):
    total = 0
    for pos, ville in enumerate(tour):
        suivante = tour[(pos + 1) % len(tour)]
        cout = COUTS[ville - 1][suivante - 1]
        if cout is None:
            return None
        total += cout
    return total


def voisins_par_echange(tour):
    """Voisins obtenus en échangeant deux positions; la ville 1 reste en position initiale."""
    voisins = []
    for i in range(1, len(tour) - 1):
        for j in range(i + 1, len(tour)):
            candidat = tour[:]
            candidat[i], candidat[j] = candidat[j], candidat[i]
            cout = cout_tour(candidat)
            if cout is not None:
                voisins.append((candidat, cout))
    return voisins


def recherche_taboue(tour_initial=TOUR_INITIAL, iterations=100, duree_taboue=5):
    """Meilleur voisin admissible; états récents tabous, avec aspiration vers le meilleur global."""
    cout_initial = cout_tour(tour_initial)
    if cout_initial is None:
        raise ValueError("Le circuit initial emprunte une liaison interdite.")
    courant = tour_initial[:]
    meilleur = courant[:]
    cout_meilleur = cout_initial
    tabu = {}  # tuple du circuit -> itération d'expiration
    historique = [(0, courant[:], cout_initial)]

    for t in range(1, iterations + 1):
        candidats = []
        for tour, cout in voisins_par_echange(courant):
            sig = tuple(tour)
            if tabu.get(sig, -1) < t or cout < cout_meilleur:
                candidats.append((tour, cout))
        if not candidats:
            break
        tour_suivante, cout_suivant = min(candidats, key=lambda item: item[1])
        tabu[tuple(courant)] = t + duree_taboue
        courant = tour_suivante
        historique.append((t, courant[:], cout_suivant))
        if cout_suivant < cout_meilleur:
            meilleur = courant[:]
            cout_meilleur = cout_suivant
    return meilleur, cout_meilleur, historique


def temperature_initiale_empirique(tour_initial, probabilite_acceptation=0.80):
    """Calibre T0 pour accepter une hausse moyenne avec la probabilité cible donnée."""
    cout0 = cout_tour(tour_initial)
    hausses = [cout - cout0 for _, cout in voisins_par_echange(tour_initial) if cout > cout0]
    if not hausses:
        return 1.0
    hausse_moyenne = sum(hausses) / len(hausses)
    return -hausse_moyenne / log(probabilite_acceptation)


def recuit_simule(tour_initial=TOUR_INITIAL, iterations=5, refroidissement=0.80,
                   probabilite_initiale=0.80, graine=20):
    """Recuit simulé avec cinq itérations par défaut et refroidissement géométrique."""
    cout_initial = cout_tour(tour_initial)
    if cout_initial is None:
        raise ValueError("Le circuit initial emprunte une liaison interdite.")
    temperature0 = temperature_initiale_empirique(tour_initial, probabilite_initiale)
    courant = tour_initial[:]
    cout_courant = cout_initial
    meilleur = courant[:]
    cout_meilleur = cout_courant
    temperature = temperature0
    rng = Random(graine)
    trace = []

    for k in range(1, iterations + 1):
        voisins = voisins_par_echange(courant)
        if not voisins:
            trace.append({"iteration": k, "temperature": temperature, "mouvement": "aucun voisin",
                          "delta": 0, "accepte": False, "tour": courant[:], "cout": cout_courant})
            temperature *= refroidissement
            continue
        propose, cout_propose = rng.choice(voisins)
        delta = cout_propose - cout_courant
        if delta <= 0:
            accepte = True
        else:
            accepte = rng.random() < exp(-delta / temperature)
        if accepte:
            courant = propose
            cout_courant = cout_propose
            if cout_courant < cout_meilleur:
                meilleur = courant[:]
                cout_meilleur = cout_courant
        trace.append({"iteration": k, "temperature": temperature, "mouvement": propose[:],
                      "delta": delta, "accepte": accepte, "tour": courant[:], "cout": cout_courant})
        temperature *= refroidissement
    return meilleur, cout_meilleur, temperature0, trace


def afficher_tour(nom, tour, cout):
    print(f"{nom}: {'-'.join(map(str, tour + [tour[0]]))} ; coût = {cout}")


def main():
    cout_initial = cout_tour(TOUR_INITIAL)
    afficher_tour("Circuit initial", TOUR_INITIAL, cout_initial)

    tabu_tour, tabu_cout, historique = recherche_taboue()
    afficher_tour("Meilleur circuit tabou", tabu_tour, tabu_cout)
    print(f"Itérations tabou exécutées : {len(historique) - 1}; meilleur coût : {tabu_cout}")
    print("Premières étapes (itération, coût courant):", [(t, c) for t, _, c in historique[:11]])

    sa_tour, sa_cout, temp0, trace = recuit_simule()
    print(f"Température initiale empirique T0 = {temp0:.3f}; refroidissement alpha = 0.80")
    print("Itérations du recuit simulé :")
    for ligne in trace:
        print(f"  {ligne['iteration']}: T={ligne['temperature']:.3f}, "
              f"delta={ligne['delta']}, accepté={ligne['accepte']}, coût courant={ligne['cout']}")
    afficher_tour("Meilleur circuit recuit simulé", sa_tour, sa_cout)


if __name__ == "__main__":
    main()
