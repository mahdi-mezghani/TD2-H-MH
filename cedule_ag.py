import random

# ==========================================
# 1. DONNÉES DU PROBLÈME
# ==========================================
capacites = [20, 15, 35, 40, 15, 15, 10]
durees = [2, 2, 1, 1, 1, 1, 1]
demandes = [80, 90, 65, 70]
capacite_totale = sum(capacites)

# Blocs valides pour chaque unité (représentation binaire sur 4 intervalles)
blocs_valides = {
    0: ['1100', '0110', '0011'], # Unité 1 (durée 2)
    1: ['1100', '0110', '0011'], # Unité 2 (durée 2)
    2: ['1000', '0100', '0010', '0001'], # Unité 3 (durée 1)
    3: ['1000', '0100', '0010', '0001'], # Unité 4
    4: ['1000', '0100', '0010', '0001'], # Unité 5
    5: ['1000', '0100', '0010', '0001'], # Unité 6
    6: ['1000', '0100', '0010', '0001']  # Unité 7
}

# ==========================================
# 2. FONCTIONS UTILITAIRES & FITNESS
# ==========================================
def calculer_fitness(chromosome):
    """Calcule la réserve minimale (fitness). Si réserve < 0, fitness = 0."""
    reserves = []
    for t in range(4):
        puissance_perdue = 0
        for i in range(7):
            if chromosome[i][t] == '1':
                puissance_perdue += capacites[i]
        
        reserve = capacite_totale - puissance_perdue - demandes[t]
        if reserve < 0:
            return 0  # Pénalité pour non-respect de la contrainte
        reserves.append(reserve)
    return min(reserves)

def generer_population(taille_pop):
    """Génère une population initiale valide."""
    population = []
    for _ in range(taille_pop):
        chromosome = [random.choice(blocs_valides[i]) for i in range(7)]
        population.append(chromosome)
    return population

# ==========================================
# 3. OPÉRATEURS GÉNÉTIQUES
# ==========================================
def selection_loterie(population, fitnesses):
    """Sélection par loterie (Roulette Wheel)."""
    somme_fitness = sum(fitnesses)
    if somme_fitness == 0:
        return random.choice(population) # Si tout est à 0, sélection aléatoire
    
    tirage = random.uniform(0, somme_fitness)
    cumul = 0
    for ind, fit in zip(population, fitnesses):
        cumul += fit
        if cumul >= tirage:
            return ind
    return population[-1]

def croisement(parent1, parent2):
    """Croisement à un point, uniquement entre les blocs (frontières de 4 bits)."""
    # Point de coupure entre 1 et 6 (pour éviter de couper au milieu d'un bloc)
    point = random.randint(1, 6)
    enfant1 = parent1[:point] + parent2[point:]
    enfant2 = parent2[:point] + parent1[point:]
    return enfant1, enfant2

def mutation_inversion(chromosome):
    """
    Mutation par inversion : on inverse une séquence de bits aléatoire.
    Comme cela casse la structure des blocs, on applique une réparation.
    """
    chrom_list = list(''.join(chromosome))
    # Choisir deux points d'inversion
    pt1 = random.randint(0, 27)
    pt2 = random.randint(pt1 + 1, 28)
    
    # Inversion de la sous-séquence
    sous_seq = chrom_list[pt1:pt2]
    sous_seq.reverse()
    chrom_list[pt1:pt2] = sous_seq
    
    # Réparation : on s'assure que chaque bloc de 4 bits redevient valide
    nouveau_chromosome = []
    for i in range(7):
        bloc = ''.join(chrom_list[i*4:(i+1)*4])
        if bloc not in blocs_valides[i]:
            # Si le bloc a été corrompu par l'inversion, on le remplace
            # par un bloc valide aléatoire
            bloc = random.choice(blocs_valides[i])
        nouveau_chromosome.append(bloc)
    return nouveau_chromosome

def mutation_bloc(chromosome):
    """Mutation par bloc (telle que décrite dans le PDF)."""
    index_unite = random.randint(0, 6)
    chromosome[index_unite] = random.choice(blocs_valides[index_unite])
    return chromosome

# ==========================================
# 4. ALGORITHME GÉNÉTIQUE PRINCIPAL
# ==========================================
def algorithme_genetique(taille_pop=50, generations=100, taux_croisement=0.8, taux_mutation=0.1, type_mutation="inversion"):
    population = generer_population(taille_pop)
    meilleur_global = None
    meilleure_fitness_globale = -1

    for gen in range(generations):
        # 1. Évaluation
        fitnesses = [calculer_fitness(ind) for ind in population]
        
        # Mise à jour du meilleur global
        max_fit = max(fitnesses)
        if max_fit > meilleure_fitness_globale:
            meilleure_fitness_globale = max_fit
            meilleur_global = population[fitnesses.index(max_fit)][:]

        # 2. Nouvelle génération
        nouvelle_population = []
        
        # Élitisme : on garde le meilleur individu
        nouvelle_population.append(meilleur_global)

        while len(nouvelle_population) < taille_pop:
            # Sélection
            p1 = selection_loterie(population, fitnesses)
            p2 = selection_loterie(population, fitnesses)

            # Croisement
            if random.random() < taux_croisement:
                e1, e2 = croisement(p1, p2)
            else:
                e1, e2 = p1[:], p2[:]

            # Mutation
            if random.random() < taux_mutation:
                if type_mutation == "inversion":
                    e1 = mutation_inversion(e1)
                else:
                    e1 = mutation_bloc(e1)
            
            if random.random() < taux_mutation:
                if type_mutation == "inversion":
                    e2 = mutation_inversion(e2)
                else:
                    e2 = mutation_bloc(e2)

            nouvelle_population.extend([e1, e2])

        population = nouvelle_population[:taille_pop]

        # Affichage de la progression
        if gen % 10 == 0 or gen == generations - 1:
            print(f"Génération {gen:3d} | Meilleure fitness : {meilleure_fitness_globale}")

    return meilleur_global, meilleure_fitness_globale

# ==========================================
# 5. EXÉCUTION
# ==========================================
if __name__ == "__main__":
    print("=== AG avec Mutation par Inversion ===")
    best_ind, best_fit = algorithme_genetique(taille_pop=50, generations=100, type_mutation="inversion")
    
    print("\n--- Résultat Final ---")
    print("Meilleur chromosome :", best_ind)
    print("Réserve minimale (Fitness) :", best_fit, "MW")
    
    # Affichage détaillé de la réserve par intervalle
    print("\nDétail de la réserve par intervalle :")
    for t in range(4):
        perdue = sum(capacites[i] for i in range(7) if best_ind[i][t] == '1')
        reserve = capacite_totale - perdue - demandes[t]
        print(f"  Intervalle {t+1} : Puissance perdue = {perdue} MW | Réserve = {reserve} MW")