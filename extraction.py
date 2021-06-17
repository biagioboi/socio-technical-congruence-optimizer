from ExtractSourceFilesInfo import ExtractSourceFilesInfo
from ExtractDevelopersComunicationInfo import ExtractDevelopersCommunicationInfo
import numpy
import networkx as nx
from genetic_algorithm import execute_ga
import matplotlib.pyplot as plt


# You need to store the repository and then you can start the script
repo = "square/javapoet"
toExtract = ExtractSourceFilesInfo(repo, "src/main")
toExtractDev = ExtractDevelopersCommunicationInfo(repo)


def create_matrix():

    # Call the method to retrieve the matrices
    fileFileMatrix, name_of_classes = toExtract.getFileFileMatrix()
    fileDevMatrix, devNames = toExtract.getFileDevMatrix()
    devDevDictionary = toExtractDev.get_communications_between_contributors()
    finalMatrix = []

    # Construct the final matrix, where all the three matrices are merged into one
    for i in range(0, len(fileFileMatrix)):
        finalMatrixRow = fileFileMatrix[i]+fileDevMatrix[i]
        finalMatrix.append(finalMatrixRow)

    finalToAdd = list()
    for dev in devNames:
        toAdd = list()
        for dev2 in devNames:
            if dev not in devDevDictionary:
                toAdd.append(0)
                continue
            if dev2 in devDevDictionary[dev]:
                toAdd.append(devDevDictionary[dev][dev2])
            else:
                toAdd.append(0)
        finalToAdd.append(toAdd)

    trasp = numpy.transpose(fileDevMatrix)
    trasp = trasp.tolist()

    cont = 0
    for x in trasp:
        row = list()
        row.append(x + finalToAdd[cont])
        cont = cont + 1
        finalMatrix.extend(row)

    # Execute the GA and print the resulting graph
    print_final_graph(execute_ga(finalMatrix, len(devNames)), name_of_classes)


def print_final_graph(matrix_ga, name_of_classes):
    k = 0
    dict_to_return = dict()
    for class_name in name_of_classes:
        j = 0
        dict_to_return[class_name] = dict()
        for class_name_2 in name_of_classes:
            if matrix_ga[k][j] > 0:
                dict_to_return[class_name][class_name_2] = matrix_ga[k][j]
            j = j + 1
        k = k + 1

    # Create the graph
    y = nx.Graph()
    for file, file_dep in dict_to_return.items():
        for file2, val in file_dep.items():
            y.add_edge(file, file2, weight=val)

    # Add the edges to the graph
    pos = nx.spring_layout(y)
    nx.draw_networkx_nodes(y, pos, node_size=70)
    nx.draw_networkx_edges(y, pos, edgelist=y.edges, edge_color="b", style="solid")
    nx.draw_networkx_labels(y, pos, font_size=5, font_family="sans-serif")

    # Print the graph
    plt.axis("off")
    plt.show()


create_matrix()