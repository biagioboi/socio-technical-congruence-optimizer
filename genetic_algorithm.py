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
        matrix_file_file.append(x[0:num_file]) #-1?
        if cont == num_file:
            break
        cont += 1
    # print(matrix_file_file)


    matrix_dev_dev = []
    cont2 = 1

    for x in matrix:
        if (cont2 <= num_file):
            cont2 += 1
            continue
        matrix_dev_dev.append(x[num_file:len(x)])
        if cont2 == num_file + num_dev:
            break
        cont2 += 1

    commDevelopers = 0
    for x in matrix_dev_dev:
        for element in x:
            commDevelopers += element

    # print(matrix_dev_dev)
    # print(commDevelopers)

    matrix_dev_file = []
    cont3 = 1

    for x in matrix:
        if (cont3 <= num_file):
            cont3 += 1
            continue
        matrix_dev_file.append(x[0:num_file])
        if cont3 == num_file + num_dev:
            break
        cont2 += 1


    sumElem = 0
    count = 0
    for x in matrix_file_file:
        for element in x:
            if element != 0:
                count += 1
                sumElem += element
    mean = int(sumElem / count)

    # for each file, check the number of commit by devs, in order to determine the importance of that file
    dev_worked = []
    for x in matrix[num_file:len(matrix)-1]:
        if not dev_worked:  # means that the list is empty, so initialize it
            dev_worked = x[0:num_file]
        else:  # otherwise update the current values
            for index in range(0, len(x)):
                dev_worked[index] += x[index]
                if index == len(dev_worked) - 1:
                    break
    # print(dev_worked)

    # problem constants:
    # length of the random list to create
    ONE_MAX_LENGTH = num_file  # length of bit string to be optimized

    # Genetic Algorithm constants:
    POPULATION_SIZE = 200
    P_CROSSOVER = 0.9  # probability for crossover
    P_MUTATION = 0.4  # probability for mutating an individual
    MAX_GENERATIONS = 500

    # set the random seed:
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    number_of_changes = []

    toolbox = base.Toolbox()

    def populator(num_files):
        to_return = []
        for x in range(0, num_files):
            to_return_partial = []
            for y in range(0, num_files):
                if(x == y):
                    to_return_partial.append(0)
                else:
                    to_return_partial.append(random.randint(0, 68))
            to_return.append(to_return_partial)
        return to_return

    def populator_zero():
        return 0

    def populator_comm_developers():
        return commDevelopers

    toolbox.register("PopFileMatrix", populator, num_file)

    # define a single objective, maximizing fitness strategy:
    creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0, 1.0))

    # create the Individual class based on list:
    creator.create("Individual", list, fitness=creator.FitnessMin)
    # creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

    toolbox.register("PopZero", populator_zero)

    toolbox.register("PopCommDevelopers", populator_comm_developers)


    # create the individual operator to fill up an Individual instance:
    toolbox.register("individualCreator", tools.initCycle, creator.Individual, (toolbox.PopFileMatrix,toolbox.PopZero, toolbox.PopCommDevelopers), 1)

    # create the population operator to generate a list of individuals:
    toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

    def checkDevDev_DevFile(actual_matrx, matrix_dev_dev, matrix_dev_file):
        index_devi = []
        index_devj = []

        # dato x il numero di dipendenze del file 1 su 2
        # dato z il numero di commit sul file 1
        # dato k il numero di developer moltiplicato al grado di comunicazione tra essi
        # punteggio da restituire k / x
        punteggio = 0
        for index1, file_list in zip(range(0, len(actual_matrx)), actual_matrx):
            z = 0
            punteggio_partial = 0
            # andiamoci a salvare gli indici dei dev che hanno almeno un commit
            dev_to_store = []
            for index_dev, element in zip(range(0, len(matrix_dev_file)), matrix_dev_file):
                if element[index1] > 0:
                    if index_dev not in dev_to_store:
                        dev_to_store.append(index_dev)

            # per ogni dev salvato andiamo a vedere il grado di comunicazione e lo sommiamo
            for i in range(len(dev_to_store) - 1):
                for k in range(i + 1, len(dev_to_store)):
                    dev1 = dev_to_store[i]
                    dev2 = dev_to_store[k]
                    z += matrix_dev_dev[dev1][dev2] * (matrix_dev_file[dev1][index1] + matrix_dev_file[dev2][index1])

            for value2 in file_list:
                punteggio_partial += value2

            if punteggio_partial != 0:
                punteggio = punteggio + z / punteggio_partial
        punteggio = punteggio / len(actual_matrx)
        # count_i = 0
        # count_j = 0
        #
        # for x in matrix_dev_dev:
        #     count_j = 0
        #     for element in x:
        #         if element != 0:
        #             index_devi.append(count_i)
        #             index_devj.append(count_j)
        #             element += 2 #valore simbolico (1st objective function)
        #         count_j += 1
        #     count_i += 1
        #
        #
        # for i, j in zip(index_devi, index_devj):
        #     row_i = matrix_dev_file[i]
        #     row_j = matrix_dev_file[j]
        #
        #     for count in range (0, len(row_i)):
        #         if (row_i[count] < row_j[count]):
        #             matrix_dev_file[i][count] += 2 #valore simbolico per la 2 objective function
        #
        #         elif (row_i[count] > row_j[count]):
        #             matrix_dev_file[j][count] += 2 #valore simbolico per la 2 objective function
        #
        #         else: #same values: increase both them
        #             matrix_dev_file[i][count] += 2  # valore simbolico per la 2 objective function
        #             matrix_dev_file[j][count] += 2  # valore simbolico per la 2 objective function
        return punteggio
        # print("DEV_FILE"+str(matrix_dev_file))

    def oneMaxFitness(individual):
        # let's find a way to compute the fitness function in relation to the big matrix
        # here we have a list composed by first position, the list considered, and second position, the number of changes
        summ = 0
        cont = 0
        for x in individual[0]:
            partial_sum = 0
            for index in range(0, len(x)):
                # 3rd objective function: minimize dependencies between files
                partial_sum += x[index] / dev_worked[index]
            summ += partial_sum
            cont += 1

        # checkDevDev_DevFile(matrix_dev_dev, matrix_dev_file)
        individual[2] = checkDevDev_DevFile(individual[0], matrix_dev_dev, matrix_dev_file)
        return summ, individual[1], individual[2] # return a tuple (30,70,,)


    toolbox.register("evaluate", oneMaxFitness)

    # genetic operators:

    # Tournament selection with tournament size of 3:
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Single-point crossover:
    toolbox.register("mate", tools.cxOnePoint)

    def mutPersonal (individual, ranger, probability, mean, current_file):
        # print(individual)
        for index, x in zip(range(0, len(individual)), individual):
            if (random.randint(0,1)<probability):
                if index == current_file:
                    continue
                if(random.randint(0,1)<0.5):
                    individual[index] = 0
                else:
                    individual[index] = min(x+random.randint(0, ranger), mean)
        # print(individual)
        return



    def mutateOperation(individual, mean):
        prob = individual[1]/10000
        individual[1] = 0
        for index, x in zip(range(0, len(individual[0])), individual[0]):
            mutPersonal(x, 10, prob, mean, index)
            for index_2, element in zip(range(0, len(x) - 1), x):
                if element != matrix_file_file[index][index_2]:
                    #4th objective function: minimize number of operations
                    individual[1] += abs(matrix_file_file[index][index_2] - element)
        return individual

    def populateChanges(population):
        for individual in population:
            for index, x in zip(range(0, len(individual[0]) - 1), individual[0]):
                for index_2, element in zip(range(0, len(x) - 1), x):
                    if element != matrix_file_file[index][index_2]:
                        individual[1] += abs(matrix_file_file[index][index_2] - element)
        return

    # Flip-bit mutation:
    # indpb: Independent probability for each attribute to be flipped
    toolbox.register("mutate", mutateOperation, mean=mean)


    # Genetic Algorithm flow:
    def main():
        # create initial population (generation 0):
        population = toolbox.populationCreator(n=POPULATION_SIZE)

        populateChanges(population)
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
        while generationCounter < MAX_GENERATIONS:
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
                    toolbox.mutate(mutant)
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
