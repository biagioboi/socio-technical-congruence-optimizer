from ExtractSourceFilesInfo import ExtractSourceFilesInfo
from ExtractDevelopersComunicationInfo import ExtractDevelopersCommunicationInfo


# You need to store the repository and then you can start the script

repo = "square/javapoet"
toExtract = ExtractSourceFilesInfo(repo, "src/main")
print(toExtract.getFileFileDictionary())
print(toExtract.getFileDevMatrix())
toExtractDev = ExtractDevelopersCommunicationInfo(repo)
print(toExtractDev.get_communications_between_contributors())