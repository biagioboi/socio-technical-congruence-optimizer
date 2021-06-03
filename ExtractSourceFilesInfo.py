import pathlib
import subprocess
import json
from copy import deepcopy
from pydriller import RepositoryMining


class ExtractSourceFilesInfo:

    # repository_path = name of the repository (same of github, and same of local repo)
    # path_to_file = path to the file, in order to avoid the computation of test files
    def __init__(self, repository_path, path_to_file):
        self._repository = RepositoryMining("https://www.github.com/" + repository_path + ".git")
        self._repository_path = repository_path
        self._path_to_file = path_to_file

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
                # the internal dictionary (in turn, it is the value of the corresponding filename of the commitDict dictionary)
                # and '1' as value: this value will be the counter of times that the author modify that file.!
                if commit.author.name not in commitDict[m.filename]:
                    commitDict[m.filename][commit.author.name] = 1

                # if the author modifiy the file 'filename' for the SECOND TIME (or more), let's increase the
                # corresponding value!
                else:
                    commitDict[m.filename][commit.author.name] += 1

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
            # I've explicitly declared my path as being in Windows format, so I can use forward slashes in it.
            filename = pathlib.PureWindowsPath(key)
            # Convert path to the right format for the current operating system
            path = pathlib.PurePath(filename)
            name_of_classes.append(path.name)

        # classNames = data["variables"]
        # for i in range (0,43):
        # splitting after each '/': split() returns a list of substrings of the original string (entire path):
        # we are interested in the 9th element of the list
        # print(i,classNames[i].split('/')[9])

        # Dependencies matrix
        dependencies = []
        # A dependency list, used for each row of the matrix: at each iteration is used and then empty, in order
        # to re-use it in the next iteration
        dependenciesRow = []

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
                dict_to_return[class_name][class_name_2] = dependencies[k][j]
                j = j + 1
            k = k + 1
        return dependencies

    def getFileDevMatrix(self):
        #Getting data
        data = self.getFileDevDictionary()

        #Get all file names
        fileNames = (list)(data.keys())
        devNames = []

        #Get all developers names
        for file in fileNames:
            for key in data[file].keys():
                if key not in devNames:
                    # print(key)
                    devNames.append(key)

        # File dev matrix
        fileDevMatrix = []

        # A list, used for each row of the matrix: at each iteration is used and then empty, in order
        # to re-use it in the next iteration
        fileDevRow = []

        #Iterating file names
        for i in range (0, len(fileNames)):
            #Iterating developers names
            for j in range (0, len(devNames)):
                #If a developer name is in the dictionary associated to a certain file... (this means that he made
                #at least 1 commit on that file
                if (devNames[j] in data[fileNames[i]]):
                    #append the number of commits on that file
                    fileDevRow.append(data[fileNames[i]][devNames[j]])
                else: #otherwise put 0
                    fileDevRow.append(0)

            # We are going to the next row, this means that 'i' is going to change (another file is going to be
            # analyzed): let's copy in a support list the 'fileDevRow' list, in order to save results in the
            # matrix, and re-use the 'fileDevRow' list in another iteration!
            supportList = deepcopy(fileDevRow)  # copy
            del fileDevRow[:]  # empty the list
            fileDevMatrix.extend([supportList])  # matrix filling

        return fileDevMatrix