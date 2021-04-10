from pydriller import RepositoryMining


class ExtractSourceFilesInfo:

    def __init__(self, repository_path):
        self._repository = RepositoryMining(repository_path)