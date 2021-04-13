from pydriller import RepositoryMining


class ExtractSourceFilesInfo:

    def __init__(self, repository_path):
        self._repository = RepositoryMining(repository_path)

    def getFileDevDictionary(self):
        commitDict = dict()

        for commit in self._repository.traverse_commits():
            for m in commit.modifications:
                print(
                    "Author {}".format(commit.author.name),
                    "modified {}".format(m.filename),
                    " with a change type of {}".format(m.change_type.name),
                    " and the complexity is {}".format(m.complexity)
                )

                if not m.filename in commitDict:
                    commitDict[m.filename] = []

                if not commit.author.name in commitDict[m.filename]:
                    commitDict[m.filename].append(commit.author.name)
                    print(commitDict)

        return commitDict
