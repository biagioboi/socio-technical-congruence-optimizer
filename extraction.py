from ExtractSourceFilesInfo import ExtractSourceFilesInfo

from_git_url = "https://github.com/biagioboi/UniShip.git"

toExtract = ExtractSourceFilesInfo(from_git_url)

fileDevDict = toExtract.getFileDevDictionary()

toExtract.getFileFileDictionary()
