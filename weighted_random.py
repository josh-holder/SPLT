"""
Plays SPL-T in a pseudorandom fashion, using weights as probabilities
rather than pure weights.

Was not found to work super well - the weights are tuned to be descriptive
when compared to another but not as probabilities.
"""

import sys 
import math
import os
import core_update as core
import multiprocessing
import copy
import random
import datetime
import time

seedSequence=[]

progressUpdate = 0

##########################################
def getBoardFromSequence(sequence):
	# Recreate a game board by replaying the sequence that leads to it
##########################################
	gameBoard=core.Board(8,16)
	tempSequence=sequence[:]

	while 1:
		if len(tempSequence)==0:
			return gameBoard	

		chosenBox=tempSequence.pop(0)
		core.makeMove(gameBoard,chosenBox)	


##########################################
def playSplitRandomly(gameBoard):
	#Play a single game of SPL-T
##########################################	
	while 1:

		moveOptions=gameBoard.getMoveOptions()

		if len(moveOptions)==0:
			return gameBoard.score,gameBoard.splitRecord

		nextMove=random.choice(moveOptions)


		core.makeMove(gameBoard,nextMove,calcWeights=False)

def playSplitWeighted(gameBoard):
	#Play a single game of SPL-T
##########################################	
	while 1:

		moveOptions=gameBoard.getMoveOptions()

		if len(moveOptions)==0:
			return gameBoard.score,gameBoard.splitRecord

		remainingDistance = random.random()*sum(gameBoard.weights)

		move = -1

		for i,weight in enumerate(gameBoard.weights):
			remainingDistance -= weight
			if remainingDistance < 0:
				move = i
				break

		core.makeMove(gameBoard,move)
    
##########################################
def PlayGames(saveLabel,startSequence,rewindDepth,gamesPerBatch,rewindStep,rewindThreshold,scalingFactor):
	# Play many games of SPL-T, usually from a re-wound state rather than a clean board
##########################################

	saveFile_1_Name = "[weightedRandom"+saveLabel+"].txt"
	saveFile_2_Name = "[weightedRandom"+saveLabel+"]_bestSequences.txt"

	saveFile=open(saveFile_1_Name,'w')
	saveFile.close()

	saveFile=open(saveFile_2_Name,'w')
	saveFile.close()

	#For each game played, keep a record of:
	paths=[]
	pathLengths=[]	
	scores=[]

	#In addition, some meta-parameters:
	bestLength=0
	bestScore=0
	bestSequence=[]

	targetLength=len(startSequence)

	# Determine where to rewind to
	if len(startSequence) > (rewindDepth*rewindStep):

		startIndex=int((len(startSequence)-(rewindDepth*rewindStep)))
		print("startIndex",startIndex)

	else:

		print("Start sequence length is",targetLength,". Rewind was supposed to be",rewindDepth*rewindStep,"moves. Can't rewind past zero, so will take startIndex=0")
		startIndex=0

	# Rewind
	StartingBoard=getBoardFromSequence(startSequence[:startIndex])

	numGamesToPlay=int(gamesPerBatch*pow(rewindDepth,scalingFactor))

	for games in range(numGamesToPlay):

		# Initialize the board
		gameBoard=copy.deepcopy(StartingBoard)

		# Play
		score,path=playSplitWeighted(gameBoard)

		# Save the results to buffer
		paths.append(path)
		pathLengths.append(len(path))
		scores.append(score)

		if progressUpdate: print("Core "+saveLabel+", Game #"+str(games))

		if len(path)>bestLength:
			if progressUpdate: print("Core "+saveLabel + " found a new best sequence of "+str(len(path)))
			bestLength=len(path)
			saveFile=open(saveFile_2_Name,'a')
			saveFile.write("{0}\t{1}\t{2}\n".format(score,len(path),path))
			saveFile.close()
		
		#print(saveLabel+","+"\t Game: ",games,"\tLength: ",len(path),"\tMax: ",bestLength,"\tTarget:", targetLength,"\trewindDepth: ",rewindDepth,"(",numGamesToPlay,")")

	saveFile=open(saveFile_1_Name,'a')
	for index,path in enumerate(paths):
		saveFile.write("{0}\t{1}\n".format(scores[index],pathLengths[index]))
	saveFile.close()

##########################################
def loadDataFromPreviousRun():
	# Pull in data from a previous run of playScript5 by reading the [meta] output files
##########################################

	bestSequences=[]
	bestSequencesLengths=[]
	winningSequence=[]


	try:
		saveFileName="[weightedRandommetaBestSequences].txt"
		
		saveFile=open(saveFileName,'r')
		for line in saveFile:
			data=line.rstrip('\n').split("\t")
			bestSequencesLengths.append(int(data[0]))
			data[1]= ''.join(c for c in data[1] if c not in '[] ')
			path=data[1].split(",")
			for index,element in enumerate(path):
				path[index]=int(element)
			bestSequences.append(path)
		saveFile.close()

		maxSequenceLength=int(max(bestSequencesLengths))
		bestSequencesIndex=bestSequencesLengths.index(max(bestSequencesLengths))
		winningSequence=bestSequences[bestSequencesIndex]	

	except:

		print("No save files found - we must not be resuming a prior run")
		bestSequences=[0]
		bestSequencesLengths=[0]
		winningSequence=[0]
		maxSequenceLength=0

	return bestSequences,bestSequencesLengths,winningSequence

##########################################
if __name__ == '__main__':
##########################################

	try:
		gamesPerBatch=int(sys.argv[1])		
		rewindStep=int(sys.argv[2])			
		rewindThreshold=int(sys.argv[3])		
		scalingFactor=float(sys.argv[4])	
	except:
		print("\nProblem interpreting arguments\n\nExpected usage is playScript05.py <gamesPerBatch> <rewindStep> <rewindThreshold> <scalingFactor>")	
		sys.exit(1)
	

	print("\n--------Random+ SPL-T--------\n")

	numCores=multiprocessing.cpu_count()
	print("\nCPU cores available=",numCores)    

	saveLabelList=['a','b','c','d','e','f','g','h','i','j','k','l']


	print("Reading existing savefiles (if any)...")
	bestSequences,bestSequencesLengths,winningSequence = loadDataFromPreviousRun()

	print("Longest known sequence so far is ",len(winningSequence))

	totalGamesPlayed=0
	rewindDepth=1

	metaSaveFileName="[weightedRandommeta].txt"
	metaBestSequences="[weightedRandommetaBestSequences].txt"
	metaComparison = "[weightedRandomComparison].txt"

	if not os.path.isfile(metaSaveFileName):
		saveFile=open(metaSaveFileName,'w')
		saveFile.write("RewindDepth\ttarget\tbestLength_thisBatch\ttotalGamesPlayed\n")
		saveFile.close(	)	

	timeFile = open(metaComparison,'w')
	timeFile.write("Time\tGames\tLongest Sequence\n")
	timeFile.close()

	start = time.time()
	while True:

		jobs=[]
		for index in range(numCores):	
			process = multiprocessing.Process(target=PlayGames, args=(saveLabelList[index],winningSequence,rewindDepth,gamesPerBatch,rewindStep,rewindThreshold,scalingFactor,))
			jobs.append(process)
			process.start()

		for job in jobs:
			job.join()	


		print("Collating results...")

		bestSequences=[]
		bestSequencesLengths=[]

		for index in range(numCores):
			saveFileName= "[weightedRandom"+saveLabelList[index]+"]_bestSequences.txt"
			saveFile=open(saveFileName,'r')
			for line in saveFile:
				data=line.rstrip('\n').split("\t")
				bestSequencesLengths.append(int(data[1]))
				data[2]= ''.join(c for c in data[2] if c not in '[] ')
				path=data[2].split(",")
				for index,element in enumerate(path):
					path[index]=int(element)
				bestSequences.append(path)
			saveFile.close()


		lengths=[]
		for index in range(numCores):
			saveFileName= "[weightedRandom"+saveLabelList[index]+"].txt"
			saveFile=open(saveFileName,'r')
			for line in saveFile:
				data=line.rstrip('\n').split("\t")
				lengths.append(int(data[0]))
			saveFile.close()


		maxSequenceLength=int(max(bestSequencesLengths))
		totalGamesPlayed+=len(lengths)
		print("Currently chasing a target sequence length of",int(len(winningSequence)))
		print("Maximum length sequence found in this batch was",maxSequenceLength)
		print("Total number of games played this session:",totalGamesPlayed)

		saveFile=open(metaSaveFileName,'a')
		saveFile.write("{0}\t{1}\t{2}\t{3}\n".format(rewindDepth,len(winningSequence),maxSequenceLength,totalGamesPlayed))
		saveFile.close()

		if maxSequenceLength > len(winningSequence):
			print("********************** New maximum sequence length = ",maxSequenceLength,"**********************")
			bestSequencesIndex=bestSequencesLengths.index(max(bestSequencesLengths))
			winningSequence=bestSequences[bestSequencesIndex]
			rewindDepth=1
			saveFile=open(metaBestSequences,'a')
			saveFile.write("{0}\t{1}\n".format(maxSequenceLength,winningSequence))

		elif maxSequenceLength > (len(winningSequence)-rewindThreshold):
			rewindDepth+=1

		else:
			print("Exceeded maximum difference (target-maxFound)>rewindThreshold")
			print("Changing target to maxFound")
			bestSequencesIndex=bestSequencesLengths.index(max(bestSequencesLengths))
			winningSequence=bestSequences[bestSequencesIndex]	
			rewindDepth=1
		
		end = time.time()
		timeFile = open(metaComparison,'a')
		timeFile.write(str(end-start)+"\t"+str(totalGamesPlayed)+"\t"+str(len(winningSequence))+"\n")
		timeFile.close()

