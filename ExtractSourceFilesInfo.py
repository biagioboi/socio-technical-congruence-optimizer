from pydriller import RepositoryMining


git_url = "https://github.com/vuejs-templates/webpack-simple.git"


commitDict = dict()
authorList = list()

for commit in RepositoryMining(git_url).traverse_commits():
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
