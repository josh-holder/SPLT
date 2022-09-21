"""
Tool to explore games of SPL-T manually.

Options to follow an existing sequence, back up,
follow the algorithm recommendation, get more detailed info on weights,
and manually select boxes to split.
"""

from weighting import findWeights
from weighting_new import doesPointBlockCauseNewHalving, doesUnexpectedClusterForm
from replayWithAlgo import gameBoardDisplay
import core_update as core
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen,QBrush
from PyQt5.QtCore import *
from collections import deque
from copy import deepcopy
from algorithm_play import playUntilEnd
import itertools

if __name__ == "__main__":
    saveName = "sequences/playAssist_seq.txt"

    piggyBackSeqName = "sequences/1208seq.txt"

    try:
        f = open(piggyBackSeqName, "r")
    except:
        print("Couldn't open file",piggyBackSeqName,", does it exist?")
        sys.exit(1)

    line=f.readline()
    f.close()
    if line[0] == "[": line = line[1:]
    if line[-1] == "]": line = line[:-1]
    piggyback_sequence=(line.rstrip('\n').split(', '))
    piggyback_sequence=[int(ii) for ii in piggyback_sequence]

    saveFile = open(saveName,'w')

    boards = deque(maxlen=201)

    app = QApplication(sys.argv)

    gameBoard=core.Board(8,16)

    graphicalDisplay = gameBoardDisplay(gameBoard)

    print("Green highlight = algorithm next move")
    print("Blue highlight = equal priority given by algorithm")
    print("Red highlight = followed sequence next move")
    print("Green fill = splitting this box causes a new halving")
    print("Red fill = splitting this box causes an unexpected halving")
    print("------------------------")
    print("Type number of box to split if desired,\nw to display weights, ww for verbose weights,\
        \nb to begin rewind, and s__ to jump ahead by __ splits along the provided sequence.")
    print("Default Algorithm Record: {}".format(playUntilEnd(deepcopy(gameBoard))))

    while 1:
        moveOptions = gameBoard.getMoveOptions()
        if len(moveOptions) == 0:
            core.drawScreen(gameBoard)
            print("Final Score: "+str(gameBoard.score))
            print("Final Splits: "+str(len(gameBoard.splitRecord)))
            backup = input("Enter b if you want to back up:")
            if backup == "b":
                rewind = int(input("Num splits?"))
                for i in range(rewind):
                    boards.pop()
                gameBoard = boards[-1]

                newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
                print("New algorithm split record: %d" % newAlgoMaxLength)
                pass
            else:
                break

        bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)

        best_indices = [i for i, x in enumerate(gameBoard.weights) if x == max(gameBoard.weights)]

        graphicalDisplay.HighlightNextBox(bestSplit)
        graphicalDisplay.HighlightAlgoBoxes(best_indices)

        newHalvingOptions = []
        unexpectedClusterOptions = []
        for boxIndex in moveOptions:
            if doesPointBlockCauseNewHalving(gameBoard, boxIndex): newHalvingOptions.append(boxIndex)
            if doesUnexpectedClusterForm(gameBoard, boxIndex): unexpectedClusterOptions.append(boxIndex)
        graphicalDisplay.PaintBoxesWhichCauseNewHalvings(newHalvingOptions)
        graphicalDisplay.PaintBoxesWhichCauseUnexpectedClusters(unexpectedClusterOptions)
        
        graphicalDisplay.Update(gameBoard)
        userinput = input("Split %d:" % len(gameBoard.splitRecord))
        try: 
            userinput = int(userinput)
        except ValueError:
            pass

        if userinput == "w":
            print(gameBoard.splitAction)
            for box, weight in enumerate(gameBoard.weights):
                if weight != 0: print("Weight of box %d is %d" % (box,weight))
            splitRequest = input("Input box to split:")
            try: 
                splitRequest = int(splitRequest)
            except ValueError:
                splitRequest = bestSplit

            core.makeMove(gameBoard,splitRequest)
            boards.append(deepcopy(gameBoard))

            newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
            print("New algorithm split record: %d" % newAlgoMaxLength)


        elif userinput == "ww":
            findWeights(gameBoard,weightverbose=1)
            splitRequest = input("Input box to split:")
            try: 
                splitRequest = int(splitRequest)
            except ValueError:
                splitRequest = bestSplit

            core.makeMove(gameBoard,splitRequest)
            boards.append(deepcopy(gameBoard))

            newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
            print("New algorithm split record: %d" % newAlgoMaxLength)

        elif (type(userinput) == type(1)):
            splitRequest = userinput
            if splitRequest not in moveOptions:
                splitRequest = int(input("Can't do that - split is {}. Try again".format(gameBoard.splitAction)))

            core.makeMove(gameBoard,splitRequest)
            boards.append(deepcopy(gameBoard))

            newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
            print("New algorithm split record: %d" % newAlgoMaxLength)
            

        elif userinput == "b":
            rewind = int(input("Input how many steps you want to rewind:"))
            for i in range(rewind):
                boards.pop()
            gameBoard = boards[-1]

            newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
            print("New algorithm split record: %d" % newAlgoMaxLength)


        elif userinput.startswith("s"):
            num_moves = int(userinput[1:])
            for i in range(num_moves):
                core.makeMove(gameBoard,piggyback_sequence[len(gameBoard.splitRecord)])
                boards.append(deepcopy(gameBoard))

        else:
            core.makeMove(gameBoard,bestSplit)
            boards.append(deepcopy(gameBoard))
    
    print("?")
    print(str(gameBoard.splitRecord))
    saveFile.write(str(gameBoard.splitRecord))

    sys.exit(app.exec_())