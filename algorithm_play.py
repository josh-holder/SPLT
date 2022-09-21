"""
Uses the weighting defined in weighting.py to play a game of SPL-T until the end,
recording how long it is before defeat.

Usage - "python3 algorithm_play.py"
"""

import core_update as core

def playUntilEnd(gameBoard):
	"""
	Given a gameboard, takes the best move as recommended by the weighting
	until it runs out of splits
	"""
	while 1:
		moveOptions = gameBoard.getMoveOptions()

		if len(moveOptions) == 0:
			break

		bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)

		core.makeMove(gameBoard,bestSplit)

	return len(gameBoard.splitRecord)

if __name__ == "__main__":
	gameBoard = core.Board()

	saveName = "sequences/nonrandomAlgorithm_seq.txt"

	saveFile = open(saveName,'w')

	sequence = []

	while 1:
		moveOptions = gameBoard.getMoveOptions()

		if len(moveOptions) == 0:
			print("Final Score: "+str(gameBoard.score))
			print("Final Splits: "+str(len(gameBoard.splitRecord)))
			break
		
		bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)
		print("Split " + str(len(gameBoard.splitRecord)), end='\r')

		sequence.append(bestSplit)
		core.makeMove(gameBoard,bestSplit)
	
	saveFile.write(str(gameBoard.splitRecord))
	saveFile.close()

		

