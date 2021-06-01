from ExtractSourceFilesInfo import ExtractSourceFilesInfo
from ExtractDevelopersComunicationInfo import ExtractDevelopersCommunicationInfo

from_git_url = "https://github.com/fpalomba/aDoctor.git"


toExtract = ExtractSourceFilesInfo(from_git_url)

print("test")
print(toExtract.getFileFileMatrix())

print(toExtract.getFileDevMatrix())

toExtractDev = ExtractDevelopersCommunicationInfo('fpalomba/aDoctor')

print(toExtractDev.get_communications_between_contributors())