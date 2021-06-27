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

###########################################
def playSplitMixed(gameBoard,targetSequenceLength):
	#Play a single game of SPL-T using a mix of random weighting and deterministic algorithm play
	#targetSequenceLength is the target sequence length
###########################################
	while 1:

		moveOptions = gameBoard.getMoveOptions()

		if len(moveOptions)==0:
			return gameBoard.score,gameBoard.splitRecord
		
		splitNum = len(gameBoard.splitRecord)

		#if you have not yet reached a record, play in random weighted fashion
		if splitNum <= targetSequenceLength:
			#scale weights according to how close you are to the target - more random further from target
			meanWeight = sum(gameBoard.weights) / len(gameBoard.weights)
			for weight in gameBoard.weights: #scale all non-zero weights
				if weight > 0:
					weight = meanWeight*((targetSequenceLength-splitNum)/targetSequenceLength) + (splitNum/targetSequenceLength)*weight
			
			#make move random weighted
			remainingDistance = random.random()*sum(gameBoard.weights)

			move = -1

			for i,weight in enumerate(gameBoard.weights):
				remainingDistance -= weight
				if remainingDistance < 0:
					move = i
					break

			core.makeMove(gameBoard,move)

		else: #if you have already reached a record, play deterministically according to the weights
			if targetSequenceLength > 300: #only play deterministically if the algorithm is at a reasonable record: if starting from record of zero, want to play randomly
				bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)

				core.makeMove(gameBoard,bestSplit)
			
			else: #if our target is low (<300), just play new records completely randomly.
				move=random.choice(moveOptions)
				core.makeMove(gameBoard,move)

##########################################
def PlayGames(saveLabel,startSequence,rewindDepth,gamesPerBatch,rewindStep,rewindThreshold,scalingFactor,targetSequenceLength):
	# Play many games of SPL-T, usually from a re-wound state rather than a clean board
##########################################

	saveFile_1_Name = "[mixPlay"+saveLabel+"].txt"
	saveFile_2_Name = "[mixPlay"+saveLabel+"]_bestSequences.txt"

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
		score,path=playSplitMixed(gameBoard,targetSequenceLength)

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
	targetSequence=[]


	try:
		saveFileName="[mixPlaymetaBestSequences].txt"
		
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
		targetSequence=bestSequences[bestSequencesIndex]	

	except:

		print("No save files found - we must not be resuming a prior run")
		bestSequences=[0]
		bestSequencesLengths=[0]
		targetSequence=[0]
		maxSequenceLength=0

	return bestSequences,bestSequencesLengths,targetSequence

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
	
	lenSessionMaxSequence = 0
	reversionsSinceRecord = 0

	print("\n--------Random+ SPL-T--------\n")

	numCores=multiprocessing.cpu_count()
	print("\nCPU cores available=",numCores)    

	saveLabelList=['a','b','c','d','e','f','g','h','i','j','k','l']


	print("Reading existing savefiles (if any)...")
	bestSequences,bestSequencesLengths,targetSequence = loadDataFromPreviousRun()

	print("Longest known sequence so far is ",len(targetSequence))

	totalGamesPlayed=0
	rewindDepth=1

	metaSaveFileName="[mixPlaymeta].txt"
	metaBestSequences="[mixPlaymetaBestSequences].txt"
	metaComparison = "[mixPlayComparison].txt"

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
			process = multiprocessing.Process(target=PlayGames, args=(saveLabelList[index],targetSequence,rewindDepth,gamesPerBatch,rewindStep,rewindThreshold,scalingFactor,len(targetSequence),))
			jobs.append(process)
			process.start()

		for job in jobs:
			job.join()	


		print("Collating results...")

		bestSequences=[]
		bestSequencesLengths=[]

		for index in range(numCores):
			saveFileName= "[mixPlay"+saveLabelList[index]+"]_bestSequences.txt"
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
			saveFileName= "[mixPlay"+saveLabelList[index]+"].txt"
			saveFile=open(saveFileName,'r')
			for line in saveFile:
				data=line.rstrip('\n').split("\t")
				lengths.append(int(data[0]))
			saveFile.close()


		maxSequenceLength=int(max(bestSequencesLengths))
		totalGamesPlayed+=len(lengths)
		print("Currently chasing a target sequence length of "+str(len(targetSequence)) \
			+" (session max "+str(lenSessionMaxSequence)+")")
		print("Maximum length sequence found in this batch was",maxSequenceLength)
		print("Total number of games played this session:",totalGamesPlayed)

		saveFile=open(metaSaveFileName,'a')
		saveFile.write("{0}\t{1}\t{2}\t{3}\n".format(rewindDepth,len(targetSequence),maxSequenceLength,totalGamesPlayed))
		saveFile.close()

		if maxSequenceLength > len(targetSequence):
			print("********************** New target sequence length = ",maxSequenceLength,"**********************")
			bestSequencesIndex=bestSequencesLengths.index(max(bestSequencesLengths))
			targetSequence=bestSequences[bestSequencesIndex]
			rewindDepth=1
			if maxSequenceLength > lenSessionMaxSequence:
				saveFile=open(metaBestSequences,'a')
				saveFile.write("{0}\t{1}\n".format(maxSequenceLength,targetSequence))

		elif maxSequenceLength > (len(targetSequence)-rewindThreshold):
			rewindDepth+=1

		else:
			print("Exceeded maximum difference (target-maxFound)>rewindThreshold")
			print("Changing target to maxFound")
			bestSequencesIndex=bestSequencesLengths.index(max(bestSequencesLengths))
			targetSequence=bestSequences[bestSequencesIndex]	
			rewindDepth=1
			reversionsSinceRecord += 1 #record that a reversion has occured.
			#if a certain amount of reversions have occured without reaching a new overall record, then start fresh
			if (lenSessionMaxSequence > 700) and (reversionsSinceRecord >= (lenSessionMaxSequence-250)//50): 
				reversionsSinceRecord = -5
				targetSequence = [0]

		
		if len(targetSequence) > lenSessionMaxSequence:
			lenSessionMaxSequence = len(targetSequence)
			reversionsSinceRecord = 0

		end = time.time()
		timeFile = open(metaComparison,'a')
		timeFile.write(str(end-start)+"\t"+str(totalGamesPlayed)+"\t"+str(len(targetSequence))+"\n")
		timeFile.close()

