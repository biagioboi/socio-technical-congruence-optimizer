from ExtractSourceFilesInfo import ExtractSourceFilesInfo
from ExtractDevelopersComunicationInfo import ExtractDevelopersCommunicationInfo

from_git_url = "https://github.com/square/javapoet.git"


toExtract = ExtractSourceFilesInfo(from_git_url)

print(toExtract.getFileFileMatrix())

print(toExtract.getFileDevMatrix())

toExtractDev = ExtractDevelopersCommunicationInfo('square/javapoet')

print(toExtractDev.get_communications_between_contributors())