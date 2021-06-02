from ExtractSourceFilesInfo import ExtractSourceFilesInfo
from ExtractDevelopersComunicationInfo import ExtractDevelopersCommunicationInfo
import numpy

from_git_url = "https://github.com/square/javapoet.git"


toExtract = ExtractSourceFilesInfo(from_git_url)

# print(toExtract.getFileFileMatrix())

# print(toExtract.getFileDevMatrix())
toExtractDev = ExtractDevelopersCommunicationInfo('square/javapoet')


# print(toExtractDev.get_communications_between_contributors())

def createMatrix():
    fileFileMatrix, name_of_classes = toExtract.getFileFileMatrix()
    fileDevMatrix, devNames = toExtract.getFileDevMatrix()

    devDevDictionary = toExtractDev.get_communications_between_contributors()

    finalMatrix = []
    finalMatrixRow = []


    for i in range (0, len(fileFileMatrix)):
        finalMatrixRow = []
        finalMatrixRow = fileFileMatrix[i]+fileDevMatrix[i]

        finalMatrix.append(finalMatrixRow)

    finalToAdd = []
    for dev in devNames:
        toAdd = []
        for dev2 in devNames:
            if dev not in devDevDictionary:
                toAdd.append(0)
                continue
            if dev2 in devDevDictionary[dev]:
                toAdd.append(devDevDictionary[dev][dev2])
            else:
                toAdd.append(0)
        finalToAdd.append(toAdd)

    trasp = numpy.transpose(fileDevMatrix)
    trasp = trasp.tolist()

    print("TRASP " + str(trasp))
    print("DEVS " + str(finalToAdd))
    print("DEVDEV"+str(devDevDictionary))
    print("FILEFIL"+str(fileFileMatrix))

    cont = 0
    for x in trasp:
        x = x + finalToAdd[cont]
        cont = cont + 1

    finalMatrix.append(trasp)

    print(finalMatrix)





createMatrix()