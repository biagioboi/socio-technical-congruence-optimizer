from ExtractSourceFilesInfo import ExtractSourceFilesInfo

from_git_url = "https://github.com/vuejs-templates/webpack-simple.git"

toExtract = ExtractSourceFilesInfo(from_git_url)

fileDevDict = toExtract.getFileDevDictionary()
