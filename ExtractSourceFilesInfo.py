import pathlib
import subprocess
import json
from copy import deepcopy
from pydriller import RepositoryMining
import matplotlib.pyplot as plt
import networkx as nx


class ExtractSourceFilesInfo:

    # repository_path = name of the repository (same of github, and same of local repo)
    # path_to_file = path to the file, in order to avoid the computation of test files
    def __init__(self, repository_path, path_to_file):
        self._repository = RepositoryMining("https://www.github.com/" + repository_path + ".git")
        self._repository_path = repository_path
        self._path_to_file = path_to_file
        self._classNames = []

    # This function creates the file-developers dictionary
    def getFileDevDictionary(self):
        # dictionary instance
        commitDict = dict()

        # Iterating the commits...
        for commit in self._repository.traverse_commits():
            # N.B. Each commit may contain more than one modification: this is because a developer may modify more than
            # one file, and so may commit more modified file.
            # Iterating the modifications in the commit...
            for m in commit.modifications:

                # if the filename of the modification 'm' isn't already in the dictionary, let's add it as key of
                # commitDict: the corresponding value is another dictionary!
                # commitDict = {'filename': {} }
                if m.filename not in commitDict:
                    commitDict[m.filename] = dict()

                # if the author modify the file 'filename' for the FIRST TIME, let's put the author name as a key of
                # the internal dictionary
                # (in turn, it is the value of the corresponding filename of the commitDict dictionary)
                # and '1' as value: this value will be the counter of times that the author modify that file.!
                if commit.author.name not in commitDict[m.filename]:
                    commitDict[m.filename][commit.author.name] = 1

                # if the author modifiy the file 'filename' for the SECOND TIME (or more), let's increase the
                # corresponding value!
                else:
                    commitDict[m.filename][commit.author.name] += 1

        # Create the graph
        y = nx.Graph()

        file_name_list = []
        committer_list = []
        for x, committers in commitDict.items():
            file_name_list.append(x)
            for committer, num_commit in committers.items():
                if committer not in committer_list:
                    committer_list.append(committer)

        # Add edges to the graph
        y.add_nodes_from(file_name_list, bipartite=0)
        y.add_nodes_from(committer_list, bipartite=1)

        list_to_add = []
        for filename, committers in commitDict.items():
            for committer, num_commit in committers.items():
                list_to_add.append((filename, committer))
        y.add_edges_from(list_to_add)
        pos = nx.spring_layout(y, k=0.4, iterations=20)
        nx.draw_networkx_nodes(y, pos, node_size=40)
        nx.draw_networkx_edges(y, pos, edgelist=y.edges, edge_color="b", style="solid")
        nx.draw_networkx_labels(y, pos, font_size=7, font_family="sans-serif")

        # Show the graph
        plt.axis("off")
        plt.figure(figsize=(10, 8), dpi=300)
        plt.show()

        return commitDict

    # This function creates the file-file developers dictionary
    def getFileFileDictionary(self):
        repo_dir = self._repository_path + "/" + self._path_to_file
        subprocess.call(
            ['java', '-jar', 'depends/depends.jar', 'java', repo_dir, 'outputDep', '--auto-include',
             '-d=depends'])

    def getFileFileMatrix(self):
        self.getFileFileDictionary()
        with open("depends/outputDep.json") as f:
            data = json.load(f)

        # Get class names of the entire project
        name_of_classes = list()
        for key in data['variables']:
            filename = pathlib.PureWindowsPath(key)

            # Convert path to the right format for the current operating system
            path = pathlib.PurePath(filename)
            name_of_classes.append(path.name)

        self._classNames = name_of_classes

        dependencies = list()
        dependenciesRow = list()

        # Iterating all the pairs of classes that have dependencies: index goes from 0 to n (#number of classes)
        for i in range(0, len(data["variables"])):
            # Iterating all classes (from 0 to n)
            for j in range(0, len(data["variables"])):
                # Boolean variable that tell us whether any dependencies are found
                noDependencies = True
                # Iterating the dependencies found by "Depends":
                for index in range(0, len(data["cells"])):
                    # If there are dependencies from the class indexed as 'i'...
                    if (data["cells"][index]["src"] == i):
                        # ...to the class indexed as 'j'
                        if (data["cells"][index]["dest"] == j):
                            # DEPENDENCY FOUND! Put the boolean = False and compute the sum of the dependencies!
                            noDependencies = False
                            dependenciesRow.append(sum(data["cells"][index]["values"].values()))
                # No dependencies between the class 'i' and the class 'j': put 0 in the list
                if (noDependencies):
                    dependenciesRow.append(0)

            # We are going to the next row, this means that 'i' is going to change (another class is going to be
            # analyzed): let's copy in a support list the 'partialDepencies' list, in order to save results in the
            # 'dependencies' matrix, and re-use the 'dependenciesRow' list in another iteration!
            supportList = deepcopy(dependenciesRow)  # copy
            del dependenciesRow[:]  # empty the list
            dependencies.extend([supportList])  # dependencies matrix filling

        k = 0
        dict_to_return = dict()
        for class_name in name_of_classes:
            j = 0
            dict_to_return[class_name] = dict()
            for class_name_2 in name_of_classes:
                if dependencies[k][j] > 0:
                    dict_to_return[class_name][class_name_2] = dependencies[k][j]
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

        return dependencies, name_of_classes

    def getFileDevMatrix(self):
        # Getting data
        data = self.getFileDevDictionary()

        # Get all file names
        fileNames = (list)(data.keys())
        devNames = []

        # Get all developers names
        for file in self._classNames:
            for key in data[file].keys():
                if key not in devNames:
                    # print(key)
                    devNames.append(key)

        # File dev matrix
        fileDevMatrix = list()

        # A list, used for each row of the matrix: at each iteration is used and then empty, in order
        # to re-use it in the next iteration
        fileDevRow = []

        # Iterating file names
        for i in range(0, len(self._classNames)):
            # Iterating developers names
            for j in range(0, len(devNames)):
                # If a developer name is in the dictionary associated to a certain file... (this means that he made
                # at least 1 commit on that file
                if (devNames[j] in data[self._classNames[i]]):
                    # append the number of commits on that file
                    fileDevRow.append(data[self._classNames[i]][devNames[j]])
                else:  # otherwise put 0
                    fileDevRow.append(0)

            # We are going to the next row, this means that 'i' is going to change (another file is going to be
            # analyzed): let's copy in a support list the 'fileDevRow' list, in order to save results in the
            # matrix, and re-use the 'fileDevRow' list in another iteration!
            supportList = deepcopy(fileDevRow)  # copy
            del fileDevRow[:]  # empty the list
            fileDevMatrix.extend([supportList])  # matrix filling

        return fileDevMatrix, devNames
