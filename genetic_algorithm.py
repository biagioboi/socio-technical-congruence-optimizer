from deap import base
from deap import creator
from deap import tools

import random

import matplotlib.pyplot as plt
import seaborn as sns


def execute_ga(matrix, num_dev):
    # split the matrix in order to obtain the only file / file matrix
    num_file = len(matrix) - num_dev
    matrix_file_file = []
    cont = 1
    for x in matrix:
        matrix_file_file.append(x[0:num_file - 1])
        if cont == num_file:
            break
        cont += 1

    # for each file, check the number of commit by devs, in order to determine the importance of that file
    dev_worked = []
    for x in matrix[num_file:len(matrix)-1]:
        if not dev_worked:  # means that the list is empty, so initialize it
            dev_worked = x[0:num_file-1]
        else:  # otherwise update the current values
            for index in range(0, len(x) - 1):
                dev_worked[index] += x[index]
                if index == len(dev_worked) - 1:
                    break
    print(dev_worked)

    # problem constants:
    # length of the random list to create
    ONE_MAX_LENGTH = num_file  # length of bit string to be optimized

    # Genetic Algorithm constants:
    POPULATION_SIZE = 100
    P_CROSSOVER = 0.9  # probability for crossover
    P_MUTATION = 0.1  # probability for mutating an individual
    MAX_GENERATIONS = 50

    # set the random seed:
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    toolbox = base.Toolbox()

    def populator(num_files):
        to_return = []
        for x in range(0, num_files):
            to_return.append(random.randint(0, 10))
        return to_return
    toolbox.register("zeroOrOne", populator, num_file)

    # define a single objective, maximizing fitness strategy:
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

    # create the Individual class based on list:
    creator.create("Individual", list, fitness=creator.FitnessMin)
    # creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

    # create the individual operator to fill up an Individual instance:
    toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, ONE_MAX_LENGTH)

    # create the population operator to generate a list of individuals:
    toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

    def oneMaxFitness(individual):
        # let's find a way to compute the fitness function in relation to the big matrix

        # first of all we need to communicate to the algorithm that should not create
        # dependencies between a file and itself

        summ = 0
        cont = 0
        for x in individual:
            cont += 1
            partial_sum = 0
            for index in range(0, len(x) - 1):
                partial_sum += x[index] / dev_worked[index]
            summ += partial_sum
        return summ,  # return a tuple (30,70,,)


    toolbox.register("evaluate", oneMaxFitness)

    # genetic operators:

    # Tournament selection with tournament size of 3:
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Single-point crossover:
    toolbox.register("mate", tools.cxOnePoint)

    # Flip-bit mutation:
    # indpb: Independent probability for each attribute to be flipped
    toolbox.register("mutate", tools.mutFlipBit, indpb=1.0 / ONE_MAX_LENGTH)


    # Genetic Algorithm flow:
    def main():
        # create initial population (generation 0):
        population = toolbox.populationCreator(n=POPULATION_SIZE)
        generationCounter = 0

        # calculate fitness tuple for each individual in the population:
        fitnessValues = list(map(toolbox.evaluate, population))
        for individual, fitnessValue in zip(population, fitnessValues):
            individual.fitness.values = fitnessValue

        # extract fitness values from all individuals in population:
        fitnessValues = [individual.fitness.values[0] for individual in population]

        # initialize statistics accumulators:
        maxFitnessValues = []
        meanFitnessValues = []

        # main evolutionary loop:
        # stop if min fitness value reached the zero, that is the best result
        # OR if number of generations exceeded the preset value:
        while min(fitnessValues) > 0 and generationCounter < MAX_GENERATIONS:
            # update counter:
            generationCounter = generationCounter + 1

            # apply the selection operator, to select the next generation's individuals:
            offspring = toolbox.select(population, len(population))
            # javapoet the selected individuals:
            offspring = list(map(toolbox.clone, offspring))

            # apply the crossover operator to pairs of offspring:
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < P_CROSSOVER:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < P_MUTATION:
                    # foreach list inside the list of list (matrix), do the mutation process
                    for x in range(0, len(mutant) - 1):
                        toolbox.mutate(mutant[x])
                        del mutant.fitness.values

            # calculate fitness for the individuals with no previous calculated fitness value:
            freshIndividuals = [ind for ind in offspring if not ind.fitness.valid]
            freshFitnessValues = list(map(toolbox.evaluate, freshIndividuals))
            for individual, fitnessValue in zip(freshIndividuals, freshFitnessValues):
                individual.fitness.values = fitnessValue

            # replace the current population with the offspring:
            population[:] = offspring

            # collect fitnessValues into a list, update statistics and print:
            fitnessValues = [ind.fitness.values[0] for ind in population]

            maxFitness = max(fitnessValues)
            meanFitness = sum(fitnessValues) / len(population)
            maxFitnessValues.append(maxFitness)
            meanFitnessValues.append(meanFitness)
            print("- Generation {}: Max Fitness = {}, Avg Fitness = {}".format(generationCounter, maxFitness, meanFitness))

            # find and print best individual:
            best_index = fitnessValues.index(max(fitnessValues))
            print("Best Individual = ", *population[best_index], "\n")

        # Genetic Algorithm is done - plot statistics:
        sns.set_style("whitegrid")
        plt.plot(maxFitnessValues, color='red')
        plt.plot(meanFitnessValues, color='green')
        plt.xlabel('Generation')
        plt.ylabel('Max / Average Fitness')
        plt.title('Max and Average Fitness over Generations')
        plt.show()

    main()
