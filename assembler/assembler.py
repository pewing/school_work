"""
**************************************************************************

FILE: assembler.py

AUTHOR: Philip Ewing

ASSIGNMENT: Assembler

DESCRIPTION: Create an assembler for a SIC XE program

**************************************************************************
"""

import sys
import re

splitLine = []
currentLine = 0
extendedStatus = False
basedStatus = False
indirectStatus = False
immediateStatus = False
pcRelativeStatus = False
indexStatus = False
fullFile = []
currentBased = "0"


opcodeDictionary = {"ADD":"18", "ADDF":"58", "ADDR":"90", "AND":"40",
                    "CLEAR":"B4", "COMP":"28", "COMPF":"88", "COMPR":"A0",
                    "DIV":"24", "DIVF":"64", "DIVR":"9C", "FIX":"C4",
                    "FLOAT":"C0", "HIO":"F4", "J":"3C", "JEQ":"30", "JGT":"34",
                    "JLT":"38", "JSUB":"48", "LDA":"00", "LDB":"68",
                    "LDCH":"50", "LDF":"70", "LDL":"08", "LDS":"6C",
                    "LDT":"74", "LDX":"04", "LPS":"D0", "MUL":"20", "MULF":"60",
                    "MULR":"98", "NORM":"C8", "OR":"44", "RD":"D8", "RMO":"AC",
                    "RSUB":"4C", "SHIFTL":"A4", "SHIFTR":"A8", "SIO":"F0",
                    "SSK":"EC", "STA":"0C", "STB":"78", "STCH":"54", "STF":"80",
                    "STI":"D4", "STL":"14", "STS":"7C", "STSW":"E8", "STT":"84",
                    "STX":"10", "SUB":"1C", "SUBF":"5C", "SUBR":"94",
                    "SVC":"B0", "TD":"E0", "TIO":"F8", "TIX":"2C", "TIXR":"B8",
                    "WD":"DC"}

typeDictionary = {"ADD":"3", "ADDF":"3", "ADDR":"2", "AND":"3",
                    "CLEAR":"2", "COMP":"3", "COMPF":"3", "COMPR":"2",
                    "DIV":"3", "DIVF":"3", "DIVR":"2", "FIX":"1",
                    "FLOAT":"1", "HIO":"1", "J":"3", "JEQ":"3", "JGT":"3",
                    "JLT":"3", "JSUB":"3", "LDA":"3", "LDB":"3",
                    "LDCH":"3", "LDF":"3", "LDL":"3", "LDS":"3",
                    "LDT":"3", "LDX":"3", "LPS":"3", "MUL":"3", "MULF":"3",
                    "MULR":"2", "NORM":"1", "OR":"3", "RD":"3", "RMO":"2",
                    "RSUB":"3", "SHIFTL":"2", "SHIFTR":"2", "SIO":"1",
                    "SSK":"3", "STA":"3", "STB":"3", "STCH":"3", "STF":"3",
                    "STI":"3", "STL":"3", "STS":"3", "STSW":"3", "STT":"3",
                    "STX":"3", "SUB":"3", "SUBF":"3", "SUBR":"2",
                    "SVC":"2", "TD":"3", "TIO":"1", "TIX":"3", "TIXR":"2",
                    "WD":"3"}

locationDictionary = {"A":"0", "X":"1", "L":"2", "PC":"8", "SW":"9", "B":"3",
                      "S":"4", "T":"5", "F":"6"}



def regularExpressionSplit(line):
# Uses a regular expression to split the given line

    global splitLine

    global extendedStatus
    global basedStatus
    global indirectStatus
    global immediateStatus
    global pcRelativeStatus
    global indexStatus

    splitLine = []

    extendedStatus = False
    basedStatus = False
    indirectStatus = False
    immediateStatus = False
    pcRelativeStatus = False
    indexStatus = False


    regexMatch = re.match("^(\w+|\s?)\s*(\+|\s)\s*(\w+)\s*(\@|\#|\s)\s*([a-zA-Z'_0-9]+|\s*)\s*(\,?|\s*)\s*(\w+|\s*)",
                     line)

    if isAComment(line):
        splitLine = "$$COMMENT$$"

    elif regexMatch:
        splitLine.append(regexMatch.group(1))    # splitLine[0] == label

        if regexMatch.group(2) == "+":
            extendedStatus = True

        splitLine.append(regexMatch.group(3))     # splitLine[1] == operator

        if regexMatch.group(4) == "@":
            indirectStatus = True
        elif regexMatch.group(4) == "#":
            immediateStatus = True

        splitLine.append(regexMatch.group(5))       # splitLine[2] == operand

        if regexMatch.group(7) == "X":
            indexStatus = True
        splitLine.append(regexMatch.group(7))  # splitLine[3] == second operand


    else:
        splitLine = "$$NOT_VALID$$"

    return splitLine

def isAComment(line):

    line = list(line)

    for i in range(len(line)):
        if line[i] == ".":
            return True
        elif line[i].isspace():
            pass
        else:
            return False

    return True





def locationUpdate():
# Updates the global dictionary containing the locations of all the labels.
# Also removes any line in fullFile that is either before "START", after "END", or is a comment


    global readFileName
    global currentLine
    global fullFile
    global locationDictionary
    global currentLocation
    global currentLine

    currentLine = 0

    linesToDelete = []

    for line in fullFile:
        splitLine = regularExpressionSplit(line)
        if splitLine[1].upper() == "START":
            currentLocation = splitLine[2]
            savedName = splitLine[0]
            savedLineCounter = currentLine
            break
        currentLine += 1

    currentLine = savedLineCounter + 1

    while currentLine < (len(fullFile) - 1):
        splitLine = regularExpressionSplit(fullFile[currentLine].upper())

        operatorSize = 0

        if splitLine[1] == "END":
            while len(linesToDelete) != 0:
                tempIndex = linesToDelete.pop()
                fullFile.pop(tempIndex)
            fullFile = fullFile[savedLineCounter:currentLine]


        elif splitLine == "$$NOT_VALID$$":
            operatorSize == 0
            linesToDelete.append(currentLine)

        elif splitLine == "$$COMMENT$$":
            linesToDelete.append(currentLine)

        else:
            if splitLine[0].isspace():
                if typeDictionary.has_key(splitLine[1]):
                    operatorSize = int(typeDictionary[splitLine[1]])
                    if operatorSize == 3:
                        if extendedStatus:
                            operatorSize = operatorSize + 1

                else:
                    operatorSize = labelLocation(splitLine)

            else:     # If it does have a label
                if locationDictionary.has_key(splitLine[0]):
                    print "error"
                    errorCall()
                else:
                    locationDictionary[splitLine[0]] = currentLocation

                if typeDictionary.has_key(splitLine[1]):
                    operatorSize = int(typeDictionary[splitLine[1]])
                    if operatorSize == 3:
                        if extendedStatus:
                            operatorSize = operatorSize + 1

                else:
                    operatorSize = labelLocation(splitLine)

        currentLocation = hexUpdater(currentLocation, operatorSize, 1)
        currentLine += 1
    return savedName, savedLineCounter

def labelLocation(splitLine):
    global basedStatus
    global currentBased

    operatorSize = 0
    if splitLine[1] == "BYTE":
        if splitLine[2][0] == "C" or splitLine[2][0] == "X":
            operatorSize = 1
        else:
             operatorSize = int(splitLine[2])

    elif splitLine[1] == "WORD":
        operatorSize = 3

    elif splitLine[1] == "RESB":
        operatorSize = int(splitLine[2])

    elif splitLine[1] == "RESW":
        operatorSize = int(splitLine[2]) * 3

    elif splitLine[1] == "BASED":
        currentBased = currentLocation
        basedSatus = True

    elif splitLine[1] == "NOBASED":
        basedStatus = False

    else:
        print "AAAAH PROBLEM IN LABEL LOCATION"
        errorCall()

    return operatorSize

def hexUpdater(loc, size, number):
# Takes the current location, the size of whatever needs to be added, then adds the two.

    # hexList = ["0", "1", "2", "3", "4", "5", "6", "7",
    #            "8", "9", "A", "B", "C", "D", "E", "F"]

    newSize = len(loc)

    loc = int(loc, 16)
    newLoc = loc + size
    newLoc = "%x" %newLoc
    newLoc = "".join(newLoc)

    while len(newLoc) < newSize:
        newLoc = "0" + newLoc

    return newLoc.upper()

def exceptionCheck(opcode):
    if splitLine[1] == "BYTE":
       return True

    elif splitLine[1] == "WORD":
        return True

    elif splitLine[1] == "RESB":
        return True

    elif splitLine[1] == "RESW":
        return True

    elif splitLine[1] == "BASED":
        return True

    elif splitLine[1] == "NOBASED":
        return True

    elif splitLine[1] == "END":
        return True

    return False


def sicMode():
    return

def typeOne(line):

    return opcodeDictionary[line[1]]

def typeTwo(line):

    if not locationDictionary.has_key(line[2]) or not locationDictionary.has_key(line[3]):
        errorCall()

    firstOperand = locationDictionary[line[2]]
    secondOperand = locationDictionary[line[3]]

    opcode = opcodeDictionary[line[1]]

    final = opcode + firstOperand + secondOperand

    return final

def typeThree(line):
    XBPE = "0"
    opcode = opcodeDictionary[line[1]]
    addressCode = "000"

    if extendedStatus:
        final = typeFour(line)


    else:
        if pcCheck(line, 3):
            final = pcRelative(line, 3)
        else:

            if indirectStatus:
                if immediateStatus:
                    opcode = hexUpdater(opcode, 3, 1)  #Add 3 to hex value of opcode
                else:
                    opcode = hexUpdater(opcode, 2, 1)
            else:
                if immediateStatus:
                    opcode = hexUpdater(opcode, 1, 1)  #Add 1 to hex value of opcode
                else:
                    opcode = hexUpdater(opcode, 3, 1)

            if indexStatus:
                XBPE = hexUpdate(XBPE, 8, 1)

            if locationDictionary.has_key(line[2]):
                addressCode = hexUpdater(addressCode, locationDictionary[line[2]], 1)
                final = opcode + XBPE + addressCode

            elif immediateStatus:
                addressCode = hexUpdater(addressCode, int(line[2], 16), 1)
                final = opcode + XBPE + addressCode

            else:
                errorCall()




    return final

def pcCheck(line, opType):
    global currentLocation
    operandLoc = locationDictionary[line[2]]
    if opType == 3 :
        if int(locationDictionary[line[2]],16) >= 2^12:
            return True
    return False

def turnIntoBased(line):
    global currentBased

    basedAddress = int(locationDictionary[line[2]], 16) - int(currentBased, 16)

    if basedAddress >= 2^12:
        print "Based address too big"
        errorCall()

    return addressCode

def pcRelative(line, opType):
    global currentLocation

    XBPE = "0"
    if indexStatus:
        XBPE = hexUpdater(XBPE, 8, 1)

    opcode = opcodeDictionary[line[1]]

    newLoc = int(locationDictionary[line[2]], 16) - (int(currentLocation, 16) + opType)

    if newLoc < 2^12:
        XBPE = hexUpdater(XBPE, 2, 1)
        if newLoc < 0:
            newLoc = twosComplement(newLoc)
        newLoc2 = "%x" % newLoc


    elif basedStatus:
        XBPE = hexUpdater(XBPE, 4, 1)
        addressCode = turnIntoBased(line)

    elif int(locationDictionary[line[2]], 16) < 2^15 :    # Turn into sic mode
        return turnIntoSic(line)

    else:
        errorCall()

    if indirectStatus:
        if immediateStatus:
            print "Indirect and Immediate - error"
            errorCall()
        else:
            opcode = hexUpdater(opcode, 2, 1)
    else:
        if immediateStatus:
            opcode = hexUpdater(opcode, 1, 1)  #Add 1 to hex value of opcode
        else:
            opcode = hexUpdater(opcode, 3, 1)

    if locationDictionary.has_key(line[2]):
        addressCode = locationDictionary[line[2]]
        final = opcode + XBPE + addressCode

    elif immediateStatus:
        addressCode = "000"
        addressCode = hexUpdater(addressCode, int(line[2], 16), 1)
        final = opcode + XBPE + addressCode

    else:
        errorCall()

    final = opcode.upper() + XBPE.upper() + addressCode.upper()
    return final

def turnIntoSic(line):
    opcode = opcodeDictionary[line[1]]
    address = "0000"
    if indexStatus:
        address = hexUpdater(address, 32678, 1)
    if locationDictionary.has_key(locationDictionary[line[2]]):
        address = hexUpdater(address, locationDictionary[line[2]])
    else:
        print "Invalid operand"
        errorCall()

    final = opcode + address
    
    return final


def twosComplement(value):
    value = (-1)*(value - 1)

    return (~ value)


def typeFour(line):
    XBPE = "0"
    XBPE = hexUpdater(XBPE, 1, 1)       # Extended since Type 4
    opcode = opcodeDictionary[line[1]]


    if indirectStatus:
        if immediateStatus:
            opcode = hexUpdater(opcode, 3, 1)  #Add 3 to hex value of opcode
        else:
            opcode = hexUpdater(opcode, 2, 1)
    else:
        if immediateStatus:
            opcode = hexUpdater(opcode, 1, 1)  #Add 1 to hex value of opcode
        else:
            opcode = hexUpdater(opcode, 3, 1)

    if indexStatus:
        XBPE = hexUpdater(XBPE, 8, 1)

    addressCode = "00000"

    if locationDictionary.has_key(line[2]):
        addressCode = hexUpdater(addressCode,int(locationDictionary[line[2]], 16), 1)
        final = opcode + XBPE + addressCode

    elif immediateStatus:
        addressCode = hexUpdater(addressCode, int(line[2], 16), 1)
        final = opcode + XBPE + addressCode

    else:
        errorCall()

    return

def errorCall():
    print "Error on line: ", currentLine
    sys.exit(1)
    return


def makeHeader(fileName, outputFile):



    return


def processCode(startLoc, newFileName, outputFileName):

    global currentLine
    global fullFile

    for line in fullFile:
        print line

    fileString = outputFileName
    print fileString

    byteCounter = 0

    splitLine = regularExpressionSplit(fullFile[0].upper())
    currentLocation = splitLine[2]

    currentLine = 1

    while currentLine != len(fullFile) - 1:



        splitLine = regularExpressionSplit(fullFile[currentLine].upper())

        if opcodeDictionary.has_key(splitLine[1]):
            if typeDictionary[splitLine[1]] == "1":
                line = typeOne(splitLine)
                currentLocation = hexUpdater(currentLocation, 1, 1)

            elif typeDictionary[splitLine[1]] == "2":
                line = typeTwo(splitLine)
                currentLocation = hexUpdater(currentLocation, 2, 1)

            elif typeDictionary[splitLine[1]] == "3":
                if extendedStatus:
                    line = typeFour(splitLine)
                    currentLocation = hexUpdater(currentLocation, 4, 1)
                else:
                    line = typeThree(splitLine)
                    currentLocation = hexUpdater(currentLocation, 3, 1)

            else:
                print "Error with Type Selection"
                errorCall()

            print fullFile[currentLine]
            print line

        elif exceptionCheck(splitLine[1]):
            size = labelLocation(splitLine)
            currentLocation = hexUpdater(currentLocation, size, 1)
        else:
            print "Invalid operator"
            errorCall()



        currentLine += 1
    return


def assembler():


    address = "0000"
    address = hexUpdater(address, 32768, 1)
    print address


    global outputFileName
    global currentLine

    global fullFile

    readFile = ""

    if sys.argv[1] == '-S':
        if sys.argv[2] == '-l':
            listFileStatus = True
            readFileName = sys.argv[3]
            outputFileName = sys.argv[4]
        else:
            readFileName = sys.argv[2]
            outputFileName = sys.argv[3]
        sicMode()
    else:
        if sys.argv[1] == '-l':
            listFileStatus = True
            readFileName = sys.argv[2]
            outputFileName = sys.argv[3]
        else:
            readFileName = sys.argv[1]
            outputFileName = sys.argv[2]

    readFile = open(readFileName)

    for line in readFile:
        fullFile.append(line)

    newFileName, startLoc = locationUpdate()

    processCode(startLoc, newFileName, outputFileName)


if __name__ == "__main__":
    assembler()
