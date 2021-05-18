from pydriller import RepositoryMining


class ExtractSourceFilesInfo:

    def __init__(self, repository_path):
        self._repository = RepositoryMining(repository_path)

    # Append multiple value to a key in dictionary
    def add_values_in_dict(sample_dict, key, list_of_values):
        if not key in sample_dict:
            sample_dict[key] = list()
        if not list_of_values in sample_dict[key]:
            sample_dict[key].append(list_of_values)
        return sample_dict

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

                commitDict = ExtractSourceFilesInfo.add_values_in_dict(commitDict, m.filename, commit.author.name)


        return commitDict


    def getFileFileDictionary(self):
        #listOfMethod = list()
        commitDict = dict()
        #commitLastModifiedLines = dict()

        for commit in self._repository.traverse_commits():
            for m in commit.modifications:
                listOfMethod = list()
                print(
                    "\nAuthor {}".format(commit.author.name),
                    "modified {}".format(m.filename),
                    "source code:\n{}".format(m.source_code)
                    # "commit last modified lines {}".format(gr.get_commits_last_modified_lines(commit))
                )

                for x in m.methods:
                    listOfMethod.append(x.name)


                # commitLastModifiedLines = gr.get_commits_last_modified_lines(commit)
                #commitDict = ExtractSourceFilesInfo.add_values_in_dict(commitDict, m.filename, listOfMethod)
                commitDict[m.filename] = listOfMethod


        print(commitDict)