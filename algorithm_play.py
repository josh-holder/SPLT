import sys 
import math
import os
import core_update as core
import multiprocessing
import copy
import random
import datetime
import time

if __name__ == "__main__":
	gameBoard = core.Board()

	saveName = "nonrandomAlgorithm_seq.txt"

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
	
	print(sequence)
	saveFile.write(str(sequence))

		

