from deap import base
from deap import creator
from deap import tools
import random
import matplotlib.pyplot as plt


def execute_ga(matrix, num_dev):
    # split the matrix in order to obtain the only file / file matrix
    allChanges = []
    allScores = []
    num_file = len(matrix) - num_dev
    matrix_file_file = []
    cont = 1
    for x in matrix:
        matrix_file_file.append(x[0:num_file]) #-1?
        if cont == num_file:
            break
        cont += 1

    # Re - Construct matrix dev / dev
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

    # Compute the sum of commits among all developers
    commDevelopers = 0
    for x in matrix_dev_dev:
        for element in x:
            commDevelopers += element

    # Re - Construct the matrix dev / file
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

    # Retrieve the mean of dependencies, excluding the zero
    sumElem = 0
    count = 0
    for x in matrix_file_file:
        for element in x:
            if element != 0:
                count += 1
                sumElem += element
    mean = int(sumElem / count)

    # Genetic Algorithm constants:
    POPULATION_SIZE = 200
    P_CROSSOVER = 0.4  # probability for crossover
    P_MUTATION = 0.2  # probability for mutating an individual
    MAX_GENERATIONS = 500

    # set the random seed:
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    toolbox = base.Toolbox()

    # Return the initial random matrix
    def populator(num_files):
        to_return = []
        for x in range(0, num_files):
            to_return_partial = []
            for y in range(0, num_files):
                if x == y:
                    to_return_partial.append(0)
                else:
                    to_return_partial.append(random.randint(0, 68))
            to_return.append(to_return_partial)
        return to_return

    # Return zero
    def populator_zero():
        return 0

    # Return the degree of communication, initially the same for all
    def populator_comm_developers():
        return commDevelopers

    # Re-Compute the value of changes for the first iteration
    def populateChanges(population):
        for individual in population:
            for index, x in zip(range(0, len(individual[0]) - 1), individual[0]):
                for index_2, element in zip(range(0, len(x) - 1), x):
                    if element != matrix_file_file[index][index_2]:
                        individual[1] += abs(matrix_file_file[index][index_2] - element)

    # Declare the fitness function
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, 1.0))

    # create the Individual class based on list:
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    # Register the attributes (matrix, num_of_dependencies, communication_degree)
    toolbox.register("PopFileMatrix", populator, num_file)
    toolbox.register("PopZero", populator_zero)
    toolbox.register("PopCommDevelopers", populator_comm_developers)

    toolbox.register("individualCreator", tools.initCycle, creator.Individual, (toolbox.PopFileMatrix,toolbox.PopZero, toolbox.PopCommDevelopers), 1)
    toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

    def checkDevDev_DevFile(actual_matrx, matrix_dev_dev, matrix_dev_file):
        # Be x the number of dependencies between file 1 and 2
        # Be z the number of commit on file 1
        # Be k the number of dev multiply by the degree of communication between them
        # Return k / x
        score = 0
        for index1, file_list in zip(range(0, len(actual_matrx)), actual_matrx):
            z = 0
            punteggio_partial = 0
            # Store the index of dev that have at least one commit
            dev_to_store = []
            for index_dev, element in zip(range(0, len(matrix_dev_file)), matrix_dev_file):
                if element[index1] > 0:
                    if index_dev not in dev_to_store:
                        dev_to_store.append(index_dev)

            # For each dev stored check the communication degree in order to sum it
            for i in range(len(dev_to_store) - 1):
                for k in range(i + 1, len(dev_to_store)):
                    dev1 = dev_to_store[i]
                    dev2 = dev_to_store[k]
                    z += matrix_dev_dev[dev1][dev2] * (matrix_dev_file[dev1][index1] + matrix_dev_file[dev2][index1])

            for value2 in file_list:
                punteggio_partial += value2

            if punteggio_partial != 0:
                score = score + z / punteggio_partial
        score = score / len(actual_matrx)

        return score


    def oneMaxFitness(individual):
        # Let's find a way to compute the fitness function in relation to the big matrix
        # here we have a list composed by
        # 1. the list considered
        # 2. the number of changes
        # 3. the degree of communication between devs considering that matrix
        summ = 0
        cont = 0
        for x in individual[0]:
            partial_sum = 0
            for index in range(0, len(x)):
                # 3rd objective function: minimize dependencies between files
                partial_sum += x[index]
            summ += partial_sum
            cont += 1

        individual[2] = checkDevDev_DevFile(individual[0], matrix_dev_dev, matrix_dev_file)
        return summ, individual[1], individual[2]

    # Register the evaluate function
    toolbox.register("evaluate", oneMaxFitness)

    # Tournament selection with tournament size of 3:
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Single-point crossover:
    toolbox.register("mate", tools.cxOnePoint)

    # Customized mutation function
    def mutPersonal(individual, ranger, probability, mean, current_file):
        for index, x in zip(range(0, len(individual)), individual):
            if (random.randint(0,1)<probability):
                if index == current_file:
                    continue
                if(random.randint(0,1)<0.2):
                    individual[index] = 0
                else:
                    individual[index] = min(x+random.randint(0, ranger), mean)

    # Customized mutate operation
    def mutateOperation(individual, mean):
        prob = individual[1]/10000
        individual[1] = 0
        for index, x in zip(range(0, len(individual[0])), individual[0]):
            mutPersonal(x, 10, prob, mean, index)
            for index_2, element in zip(range(0, len(x) - 1), x):
                if element != matrix_file_file[index][index_2]:
                    individual[1] += abs(matrix_file_file[index][index_2] - element)
        return individual

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
        fitnessValues = [individual.fitness.values[0] + individual.fitness.values[1] - individual.fitness.values[2]
                             for individual in population]

        # initialize statistics accumulators:
        counter_gen = list()
        num_dependencies = list()
        mean_num_dependencies = list()
        mean_num_changes = list()
        mean_deg_comm = list()

        best_list = list()

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

            # extract fitness values from all individuals in population:
            fitnessValues = [individual.fitness.values[0] + individual.fitness.values[1] - individual.fitness.values[2]
                             for individual in population]

            # apply the crossover operator to pairs of offspring:
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < P_CROSSOVER:
                    toolbox.mate(child1[0], child2[0])
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
            fitnessValuesDependencies = [ind.fitness.values[0] for ind in population]
            maxFitnessDependencies = max(fitnessValuesDependencies)
            meanFitnessDependencies = sum(fitnessValuesDependencies) / len(population)

            fitnessValueNumChanges = [ind.fitness.values[1] for ind in population]
            maxFitnessNumChanges = max(fitnessValueNumChanges)
            meanFitnessNumChanges = sum(fitnessValueNumChanges) / len(population)

            fitnessValueComm = [ind.fitness.values[2] for ind in population]
            maxFitnessComm = max(fitnessValueComm)
            meanFitnessComm = sum(fitnessValueComm) / len(population)

            print("- Generation {}: Max Fitness Dependencies = {}, Avg Fitness Dependencies = {}".format(generationCounter, maxFitnessDependencies, meanFitnessDependencies))
            print("Max Fitness Num Changes = {}, Avg Fitness Num Changes = {}".format(maxFitnessNumChanges, meanFitnessNumChanges))
            print("Max Fitness Deg. Communications = {}, Avg Fitness Deg. Communications = {}".format(maxFitnessComm, meanFitnessComm))


            # find and print best individual:
            best_index = fitnessValues.index(min(fitnessValues))
            print("Best Individual = ", *population[best_index], "\n")
            num_dependencies.append(population[best_index].fitness.values[0])
            mean_num_dependencies.append(meanFitnessDependencies)
            allChanges.append(population[best_index][1])
            mean_num_changes.append(meanFitnessNumChanges)
            allScores.append(population[best_index][2])
            mean_deg_comm.append(meanFitnessComm)

            best_list = population[best_index][0]
            counter_gen.append(generationCounter)

        fig, ax1 = plt.subplots(1, 1)
        ax1.plot(counter_gen, num_dependencies, color='red')
        ax1.plot(counter_gen, mean_num_dependencies, color='green')
        ax1.set_title("Number of dependencies between files evolution")
        fig.tight_layout()
        plt.show()

        fig, ax1 = plt.subplots(1, 1)
        ax1.plot(counter_gen, allChanges, color='red')
        ax1.plot(counter_gen, mean_num_changes, color='green')
        ax1.set_title("Individual changes evolution")
        fig.tight_layout()
        plt.show()

        fig, ax1 = plt.subplots(1, 1)
        ax1.plot(counter_gen, allScores, color='red')
        ax1.plot(counter_gen, mean_deg_comm, color='green')
        ax1.set_title("Communication degree evolution")
        fig.tight_layout()
        plt.show()

        return best_list

    return main()
