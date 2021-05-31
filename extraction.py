from ExtractSourceFilesInfo import ExtractSourceFilesInfo

from_git_url = "https://github.com/fpalomba/aDoctor.git"


toExtract = ExtractSourceFilesInfo(from_git_url)

# fileDevDict = toExtract.getFileDevDictionary()
# fileFileDict = toExtract.getFileFileDictionary()
toExtract.getFileFileMatrix()
# print(fileDevDict)
toExtract.getFileDevMatrix()
