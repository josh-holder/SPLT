#the program allows you to leverage the algorithm to 
from replay import gameBoardDisplay, replaySequence
import core_update as core
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen,QBrush
from PyQt5.QtCore import *
from collections import deque
from copy import deepcopy
from algorithm_play import playUntilEnd

if __name__ == "__main__":
	gameBoard = core.Board()

	saveName = "sequences/playAssist_seq.txt"

	saveFile = open(saveName,'w')

	boards = deque(maxlen=50)

	app = QApplication(sys.argv)

	gameBoard=core.Board(8,16)

	graphicalDisplay = gameBoardDisplay(gameBoard)

	while 1:
		moveOptions = gameBoard.getMoveOptions()

		if len(moveOptions) == 0:
			print("Final Score: "+str(gameBoard.score))
			print("Final Splits: "+str(len(gameBoard.splitRecord)))
			backup = input("Enter b if you want to back up:")
			if backup == "b":
				pass
			else:
				break

		bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)
		print("Split " + str(len(gameBoard.splitRecord)), end='\r')

		graphicalDisplay.HighlightBox(bestSplit)
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
			newAlgoMaxLength = newAlgoMaxLength+len(gameBoard.splitRecord)
			print("New algorithm split record: %d" % newAlgoMaxLength)

		elif (type(userinput) == type(1)):
			splitRequest = userinput

			core.makeMove(gameBoard,splitRequest)
			boards.append(deepcopy(gameBoard))

			newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
			newAlgoMaxLength = newAlgoMaxLength+len(gameBoard.splitRecord)
			print("New algorithm split record: %d" % newAlgoMaxLength)

		elif userinput == "b":
			rewind = input("Input how many steps you want to rewind:")
			rewind = -1*int(rewind)-1
			gameBoard = boards[rewind]

			newAlgoMaxLength = playUntilEnd(deepcopy(gameBoard))
			newAlgoMaxLength = newAlgoMaxLength+len(gameBoard.splitRecord)
			print("New algorithm split record: %d" % newAlgoMaxLength)

		else:
			core.makeMove(gameBoard,bestSplit)
			boards.append(deepcopy(gameBoard))
		
	
	saveFile.write(str(gameBoard.splitRecord))

	sys.exit(app.exec_())