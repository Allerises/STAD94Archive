import os

class TeamResult: #Result object
    ID = ''
    Driver1 = ''
    Driver2 = ''
    PosD1 = 0
    PosD2 = 0
    GapD1 = 0
    GapD2 = 0

resultList = []

def TranslateToResult(result): #Take table line and turn it into  result object
    curSnippet = result[result.find('\t')+1:] #Trimming row number

    id = curSnippet[:curSnippet.find('\t')]
    curSnippet = curSnippet[curSnippet.find('\t')+1:]

    driver = curSnippet[:curSnippet.find('\t')]
    curSnippet = curSnippet[curSnippet.find('\t')+1:]

    pos = curSnippet[:curSnippet.find('\t')]
    curSnippet = curSnippet[curSnippet.find('\t')+1:]

    gap = curSnippet

    elementExists = False
    existingElementIndex = 0


    if len(resultList) == 0: #Create first element if list is empty
        #print("List is empty, making first element")
        resultList.append(TeamResult())
        resultList[0].ID = id
        resultList[0].Driver1 = driver
        resultList[0].PosD1 = pos
        resultList[0].GapD1 = gap
    else: #Find index if team exists for current result
        #print("Searching for existing result")
        for i in range(0, len(resultList)):
            if resultList[i].ID == id:
                elementExists = True
                existingElementIndex = i
                break

    if elementExists: #Adding second driver details to result
        #print("Existing result found, entering data for 2nd driver")
        resultList[existingElementIndex].Driver2 = driver
        resultList[existingElementIndex].PosD2 = pos
        resultList[existingElementIndex].GapD2 = gap
    else: #Creating new result entry with first driver details
        #print("Creating new result")
        resultList.append(TeamResult())
        lastIndex = len(resultList)-1
        resultList[lastIndex].ID = id
        resultList[lastIndex].Driver1 = driver
        resultList[lastIndex].PosD1 = pos
        resultList[lastIndex].GapD1 = gap


data = open("RQ_Combined.txt", "r").read() #reading data file


for i in range(0, data.count('\n')): #traversing data file
    print(i)
    TranslateToResult(data[:data.find('\n')])
    data = data[data.find('\n')+1:]

filename = os.path.dirname(__file__) + "\\" + "ActuallyWideResults" + ".txt"
newFile = open(filename, 'w')
newFile.write("ID\tDriver1\tDriver2\tPosDriver1\tPosDriver2\tQualiDriver1\tQualiDriver2\n")

for i in resultList: #Rewriting widened results as relative gaps in the same row
    newFile.write(i.ID + "\t")
    newFile.write(i.Driver1 + "\t")
    newFile.write(i.Driver2 + "\t")
    newFile.write(str(int(i.PosD2) - int(i.PosD1)) + "\t")
    newFile.write(str(int(i.PosD1) - int(i.PosD2)) + "\t")
    newFile.write(str(round(float(i.GapD2) - float(i.GapD1), 3)) + "\t")
    newFile.write(str(round(float(i.GapD1) - float(i.GapD2), 3)) + "\n")

filename = os.path.dirname(__file__) + "\\" + "SingleDriverRelative" + ".txt"
newFile = open(filename, 'w')
newFile.write("ID\tDriver\tRelativePos\tRelativeQuali\n")

for i in resultList: #Rewriting widened results as relative gaps with each driver in their own row
    newFile.write(i.ID + "\t")
    newFile.write(i.Driver1 + "\t")
    newFile.write(str(int(i.PosD2) - int(i.PosD1)) + "\t")
    newFile.write(str(round(float(i.GapD2) - float(i.GapD1), 3)) + "\n")

    newFile.write(i.ID + "\t")
    newFile.write(i.Driver2 + "\t")
    newFile.write(str(int(i.PosD1) - int(i.PosD2)) + "\t")
    newFile.write(str(round(float(i.GapD1) - float(i.GapD2), 3)) + "\n")