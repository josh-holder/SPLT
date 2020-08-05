import sys 
import math
import os
import core
import core_update as core_weight
import multiprocessing
import copy
import random
import datetime
import time

def PlayGameToEnd(random_threshhold):
	gameBoard = core_weight.Board()
	
	sequence = []

	while 1:
		# tstart = time.time()
		moveOptions = gameBoard.getMoveOptions()

		if len(moveOptions) == 0:
			return sequence
		
		if len(sequence) < random_threshhold:
			#true random
			# start = time.time()
			bestSplit=random.choice(moveOptions)
			# end = time.time()
			# print('chose random split in '+str(end-start))
			#weighted random
			# start = time.time()
			add_factor = (random_threshhold-len(sequence))*5
			for i, weight in enumerate(gameBoard.weights):
				if weight != 0:
					gameBoard.weights[i] = weight + add_factor

			remainingDistance = random.random()*sum(gameBoard.weights)

			bestSplit = -1

			for i,weight in enumerate(gameBoard.weights):
				remainingDistance -= weight
				if remainingDistance < 0:
					bestSplit = i
					break
			# end = time.time()
			# print('chose split in '+str(end-start))
		else:
			# start = time.time()
			bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)
			# end = time.time()
			# print('chose best weight in '+str(end-start))

		sequence.append(bestSplit)
		# start = time.time()
		core_weight.makeMove(gameBoard,bestSplit)
		# end = time.time()
		# print('made move in in core in '+str(end-start))
		# print('overall time for move in '+str(end-tstart))

def runSim(random_threshhold):
	saveName = "Mix_Algorithm_seq.txt"

	best_sequence = []

	#play games with increasingly high random threshholds
	game_num = 1

	while 1:
		print(game_num,len(best_sequence),end='\r')
		new_sequence = PlayGameToEnd(random_threshhold)

		if len(new_sequence) > len(best_sequence):
			best_sequence = new_sequence

		if game_num%50 == 0:
			saveFile = open(saveName,'w')
			saveFile.write(str(best_sequence))
			saveFile.close()

		game_num += 1

if __name__ == "__main__":
	runSim(200)
