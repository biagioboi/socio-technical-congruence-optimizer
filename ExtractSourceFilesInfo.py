from pydriller import RepositoryMining


class ExtractSourceFilesInfo:

    def __init__(self, repository_path):
        self._repository = RepositoryMining(repository_path)

#This function creates the file-developers dictionary
    def getFileDevDictionary(self):
        #dictionary instance
        commitDict = dict()

        #Iterating the commits...
        for commit in self._repository.traverse_commits():
            #N.B. Each commit may contain more than one modification: this is because a developer may modify more than
            # one file, and so may commit more modified file.

            #Iterating the modifications in the commit...
            for m in commit.modifications:
                # print(
                #     "{}".format(commit.author.name),
                #     "modified {}".format(m.filename)
                # )

                #if the filename of the modification 'm' isn't already in the dictionary, let's add it as key of
                #commitDict: the corresponding value is another dictionary!
                #commitDict = {'filename': {} }
                if not m.filename in commitDict:
                    commitDict[m.filename] = dict()
                    # print(commitDict)

                #if the author modify the file 'filename' for the FIRST TIME, let's put the author name as a key of
                #the internal dictionary (in turn, it is the value of the corresponding filename of the commitDict dictionary)
                #and '1' as value: this value will be the counter of times that the author modify that file.!
                if not commit.author.name in commitDict[m.filename]:
                    commitDict[m.filename][commit.author.name] = 1
                    # print(commitDict)

                #if the author modifiy the file 'filename' for the SECOND TIME (or more), let's increase the
                # corresponding value!
                else:
                    commitDict[m.filename][commit.author.name] +=1

        return commitDict
