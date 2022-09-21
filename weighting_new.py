"""
Contains a new version of the weighting algorithm with two main updates:
-Attempting to find out if the best move will cause an unexpected cluster with falling blocks
-A more precise algorithm to determine if a point block will result in a new halving.

Despite both of these functions working (doesUnexpectedClusterForm() and doesPointBlockCauseNewHalving() respectively),
overall algorithm performance was worse using this weighting scheme, so it's not currently being used in the algorithms.

Not much effort was actually put into tweaking it to make it work, thoguh, and the architecture around 
doesPointBlockCreateNewHalving() in findWeights() has lost a lot of depth from the old version. If noe wanted to continue
trying, this would probably be the most effective place to put work in.
"""

import math
import copy
import time
from collections import defaultdict
import core_update as core

weightverbose = 0
timingInfo = 0
HORIZONTAL='-'
VERTICAL='|'

def findSplitsUntilFall(gameBoard):
	"""
	Given a gameboard object, finds the points until each block falls.
	INPUT: gameBoard object
	OUTPUT: splitsUntilFall, a dictionary with form {blockIndex:splitsUntilFall}
	"""
	if timingInfo: start = time.time()
	splitsUntilFall = {}

	# explosionImminent = 0
	# for box in gameBoard.box:
	# 	if box.points == 1:
	# 		explosionImminent = 1

	sufverbose = 0

	if sufverbose: print("Initializing splitsUntilFall of bottom row")

	#initialize the bottom row first
	for boxIndex in gameBoard.boxesInRow[gameBoard.height]:
		box = gameBoard.box[boxIndex]
		splitsUntilFall[boxIndex] = box.points

	#iterate through every other row, box by box
	for row in range(gameBoard.height-1,0,-1):
		if sufverbose: print("~~~Finding splits until fall of row " + str(row)+ "~~~")

		for boxIndex in gameBoard.boxesInRow[row]:
			if sufverbose: print("Calculating for box index " + str(boxIndex))

			box = gameBoard.box[boxIndex]
			maxSplitsToFall = 0

			#iterates through boxes in row directly below
			for otherBoxIndex in gameBoard.boxesInRow[row+1]:
				otherBox = gameBoard.box[otherBoxIndex]

				#SPECIAL CASE: When the split is vertical AND the box does not have points AND there is a point block about to explode AND a cluster would be formed, 
				#it actually will fall in two parts and matter
				#if explosionImminent and box.points == 0 and gameBoard.splitAction==VERTICAL:
					#find the splitsuntilfall for both sides of the block seperately, then take the smaller one of the two and make that splitsUntillFall.
					#NEEDS TO BE IMPLEMENTED, probably doesnt matter in most scenarios

				#only selects boxes in the correct columns to be below the box you're looking at
				if otherBox.x+otherBox.width > box.x and otherBox.x < box.x+box.width:
					if sufverbose: print("Box with index " + str(otherBoxIndex) + " is directly below. This box has " + str(splitsUntilFall[otherBoxIndex]) + " splits until fall.")

					if splitsUntilFall[otherBoxIndex] == 0:
						if sufverbose: print("This box below will not fall, so therefore the box above will not fall either.")
						maxSplitsToFall = 0
						break
					#finds box directly under the current box that will fall the latest
					if splitsUntilFall[otherBoxIndex] > maxSplitsToFall:
						if sufverbose: print("This is the new high splits until fall, so we update the max.")
						maxSplitsToFall = splitsUntilFall[otherBoxIndex]

			#the box with fall when its points run out, or a block below falls: whichever comes first. However, we only want to do this when the points are nonzero.
			if box.points != 0 and maxSplitsToFall != 0:
				splitsUntilFall[boxIndex] = min([box.points,maxSplitsToFall])
			else:
				splitsUntilFall[boxIndex] = maxSplitsToFall

			if sufverbose: print("We choose the minimum between " + str(box.points)+" and "+str(maxSplitsToFall)+" (excluding zero), yielding "+str(splitsUntilFall[boxIndex])+" for box "+str(boxIndex))

	if timingInfo: 
		end = time.time()
		print("Time to find splits until fall for turn "+str(curr_splits)+": "+str(end-start))

	return splitsUntilFall

def doesUnexpectedClusterForm(gb_input,chosenBox):
	"""
	Modelled strongly off of makeMove in core_update.py. Aims to answer the question of
	whether or not a cluster forms unexpectedly by falling blocks. Removes all parts of
	makeMove which do not serve this purpose and returns True if an unexpected cluster is formed,
	and False otherwise.
	"""
	gameBoard = copy.deepcopy(gb_input)
	##########################################	
	# -------- 1. Try to execute the split: -------------------------------------------------------------------------------------
	#
	if gameBoard.split(gameBoard.box[chosenBox])==0: print("exiting"); exit()

	gameBoard.splitRecord.append(chosenBox)

	# -------- 2. Determine whether four or more similar boxes are now adjacent   -----------------------------------------------
	#
	# Algorithm:
	# 	Scan through all boxes, for each check whether it is in the upper left hand corner of a set of at least 4 identical boxes
	#
	# 	If there is a set of 6, it will register twice: once as the correct set of 6 plus another again as a subset of 4
	# 	This doesn't matter beyond efficiency concerns! The end effect is still correct

	# 	Optimization: The only clusters that could have formed at this stage involve the box you just split
	# 	So while scanning through the boxes, only subscan boxes which are the same size (box equality method compares size)
	
	#We've already scanned and found which blocks would be clusters, so we just read them off from the clusters variable
	pointsToAdd = len(gameBoard.splitRecord)+1

	for index in gameBoard.clusters[chosenBox]:
		gameBoard.box[index].points = pointsToAdd

	# -------- 3. Process decrement of point blocks  ----------------------------------------------------------------------------
	#
	for box in gameBoard.box:
		if box.points>1:
			box.points-=1

		elif box.points==1:
			box.points=-1 #-1 is a special value to denote 'just exploded'
		else:
			pass



	# -------- 4. Process destruction of point blocks which have counted down to zero -------------------------------------------
	#
	rowsWithDestruction=[]

	for box in gameBoard.box:
		if box.points<0: #box should be destroyed
			for ii in range(box.y,box.y+box.height):
				if not ii in rowsWithDestruction: rowsWithDestruction.append(ii)
	#Remove the boxes from gameBoard.box[]
	gameBoard.box[:] = [box for box in gameBoard.box if box.points>=0]

	# -------- 5. Process falling of blocks which now have voids below them -----------------------------------------------------
	#
	# e.g.
	#		   __	 	
	#		  |__|  
	#          		-->	  __    
	#		   __	 	 |__| 
	#		  |__|  	 |__|			     
	# 
	#
	# We do this by looping through every box. If a box falls, it may causes other boxes 
	# above it to also fall. So we then loop again, and repeat until there is no movement of any block

	core.updateScreenBuffer(gameBoard)

	columnsWithFalling=[]

	#Optimization: first figure out which columns have voids. We can then cheaply check whether a box is eligible for falling
	columnsWithVoids=[]

	for ii in range(gameBoard.width):	
		for jj in range(gameBoard.height):
			if gameBoard.screenBuffer[((jj)*2)+1][((ii)*2)+1] =='*':
				if not ii in columnsWithVoids: columnsWithVoids.append(ii)


	fallingHappened=False
	movementScanRequired=True

	while movementScanRequired is True: # Continue looping until nothing falls

		movementScanRequired=False #Assume nothing falls - we'll reset this if needed

		for boxindex,box in enumerate(gameBoard.box):	

			if not box.x in columnsWithVoids:	#The left side of this box is not on a column with voids in it, so it can't fall
				pass

			elif (box.y+box.height==gameBoard.height): #This box is already on the floor, so it can't fall
				pass 

			else: 				
				# We want to know if every tile in contact with the bottom edge of this box is void, and to what 
				# depth that is true. An easy way to do it is by looking at the ascii screen buffer
				
				distanceToFall=9999 #assume the box will fall a long way, then adjust it down to the true value
				
				for ii in range(box.width):
					
					stopFound=False	
					jj=0	# jj= number of voids below the ii'th column of this box
					while stopFound==False:
						if box.y+box.height+jj<gameBoard.height:
							if gameBoard.screenBuffer[((box.y+jj+box.height)*2)+1][((box.x+ii)*2)+1] !='*':
								stopFound=True
							else:
								jj+=1	
						else:
							stopFound=True

					if jj<distanceToFall:
						distanceToFall=jj

					if jj==0:	#If any column of the box has no voids below it, it can't fall so we can stop immediately.
						break

				# If falling needs to happen, do it
				if distanceToFall>0:
					box.modify(box.x,box.y+distanceToFall,box.width,box.height,box.points)
					if box.points>0: box.fellFlag=1 	#Make a note to halve the points later - it's too soon to do it now
					fallingHappened=True

					for ii in range(box.x,box.x+box.width):
						if not ii in columnsWithFalling: columnsWithFalling.append(ii)

					core.updateScreenBuffer(gameBoard)

					movementScanRequired=True 	#Setting this flag causes the parent loop to run through all blocks one more time

				# else this box should not fall
				else:
					pass 

	columnsWithFalling.sort()

	# -------- 6. Process new blocks coming in from the top ---------------------------------------------------------------------
	#

	#------------- 6.1. Scan across columns to maps out the space that need filling ----------
	# 	
	# There is some strangeness here: pre-existing voids are never filled, unless a block has fallen through it.
	# For this reason we kept track of 'columnsWithFalling'

	core.updateScreenBuffer(gameBoard)	
	voidCount=0
	numVoids=[] #If for example the gameboard has a 2x2 pocket in the upper left corner, numVoids will be [2,2,0,0,0,0,0,0]

	if len(columnsWithFalling)==0 and len(rowsWithDestruction)>0:
		for column in range(gameBoard.width):	#For each column on the game board		
			row=0 				#Start scanning down the rows starting at zero (top of the board)
			stopRowScan=False 
						
			while stopRowScan==False:
				if gameBoard.screenBuffer[(row*2)+1][(column*2)+1] =='*' and row in rowsWithDestruction: voidCount+=1
				else: stopRowScan=True # As soon as you hit a non-void, you're done with this column

				row+=1

				# If you get to the bottom of the game board, you're done. -1 because we count rows from zero
				if row>(gameBoard.height-1): stopRowScan=True	

			numVoids.append(voidCount)
			voidCount=0		
	else:
		for column in range(gameBoard.width):	
			row=0 				#Start scanning down the rows starting at zero (top of the board)
			stopRowScan=False 
						
			while stopRowScan==False:
				if gameBoard.screenBuffer[(row*2)+1][(column*2)+1] =='*': voidCount+=1
				else: stopRowScan=True # As soon as you hit a non-void, you're done with this column

				row+=1

				# If you get to the bottom of the game board, you're done. -1 because we count rows from zero
				if row>(gameBoard.height-1): stopRowScan=True

			numVoids.append(voidCount)
			voidCount=0

	#------------- 6.2. Fill the space with new blocks from the top ----------
	# 	

	if all(ii == 0 for ii in numVoids):
		continueFilling=False	

	# If you have partially filled the void, at what height should the next filling block be placed?
	# numVoidsOffset array tells you this. If numVoids=[6,6,0,0,0,0,0,0] and numVoidsOffset=[4,4,0,0,0,0,0,0],
	# then the final 2x2 block you make should be positioned at a y value of (6-4)=2 
	numVoidsOffset=[]	
	for column in range(gameBoard.width):
		numVoidsOffset.append(0)

	continueFilling=True
	fillingHappened=False

	while continueFilling==True:
	
		if all(v == 0 for v in numVoids):
			continueFilling=False
			break
		
		#	Scan through the numVoids list left to right. Identify the the first isolated pocket you come across 
		#	(i.e. bordered by an edge or zero depth).

		pocketFound=0

		for index,voidCount in enumerate(numVoids):
			if voidCount>0 and pocketFound==0:
				pocketFound=1
				pocketStartIndex=index

			if voidCount==0 and pocketFound==1:
				pocketEndIndex=index-1
				pocketFound=2


		if pocketFound==1:
			pocketEndIndex=index
		

		#	Identify the deepest depth in this pocket. Create the largest single block which will fit in it, subject to some extra rules:
		#
		#	1. Only pieces with side lengths of 2^n can exist on the board. This means, for example, that a 6xN void is filled by 
		#		a 4xN block and a 2xN block
		#
		#	2. 1xN or Nx1 voids are ignored 
		#
		#	3. When multiple blocks are required, filling happens from the bottom up, not top down.

		if pocketStartIndex==pocketEndIndex:
			numVoids[pocketStartIndex]=0
		else:
			deepestDepth=max(numVoids[pocketStartIndex:pocketEndIndex+1])
			valleyStartX=numVoids.index(deepestDepth)

			# The pocket may consist of a 'cityscape' profile rather than a simple flat bottom
			# For this reason we identify the deepest valley in the pocket, and treat that as the subspace to be filled
			
			valleyWidth=0
			for ii in numVoids[valleyStartX:]:
				if ii==deepestDepth:	valleyWidth+=1
				else:break
		
			# Round the width down to the nearest 2^n value
			reducedWidth=0
			for ii in [1,2,4,8,16,32]:
				if valleyWidth>=ii:
					reducedWidth=ii
			valleyWidth=reducedWidth

			if valleyWidth==1:
				for jj in range(0,valleyWidth):
					numVoids[valleyStartX+jj]-=1
					numVoidsOffset[valleyStartX+jj]+=1

			elif (deepestDepth%2==1):
				for jj in range(0,valleyWidth):
					numVoids[valleyStartX+jj]-=1
					numVoidsOffset[valleyStartX+jj]+=1

			else:
				for ii in [32,16,8,4,2]:
					
					if deepestDepth>=ii:

						height=ii
						y=numVoids[valleyStartX]-height	+numVoidsOffset[valleyStartX]
						y=0
						gameBoard.makeBox(valleyStartX,y,valleyWidth,height,0)
						core.updateScreenBuffer(gameBoard)

						distanceToFall=999
						for kk in range(valleyStartX,valleyStartX+valleyWidth):
							stopFound=False
							jj=0
							while stopFound==False:
								if height+jj<gameBoard.height:
									if gameBoard.screenBuffer[((height+jj)*2)+1][((kk)*2)+1] !='*':
										stopFound=True
									else:
										jj+=1
								else:
									stopFound=True

							if distanceToFall>jj:
								distanceToFall=jj

						if distanceToFall>0:	
							box=gameBoard.box[-1]
							box.modify(box.x,box.y+distanceToFall,box.width,box.height,box.points)

						core.updateScreenBuffer(gameBoard)
						fillingHappened=True
						for jj in range(0,valleyWidth):
							numVoids[valleyStartX+jj]-=ii
							deepestDepth-=ii


	# -------- 7. Determine whether four or more similar boxes are now adjacent   -----------------------------------------------
	#
	#	This is almost a copy paste of step 2, except there we only had to look in the vicinity of the box we just split. Now we
	#	have to scan all boxes
	if fallingHappened:
		for box in gameBoard.box:
			if box.points==0:
				
				setMembers=[] #Set of identical neighbours for this box	

				for otherboxindex,otherbox in enumerate(gameBoard.box):
					if otherbox.points==0:
						if box==otherbox:	#Equality method compares width, height and number of points.				
							# If otherbox is beside box
							if otherbox.x==(box.x+box.width) and otherbox.y==box.y:	setMembers.append(otherboxindex)
							# If otherbox is diagonal to box
							elif otherbox.x==(box.x+box.width) and otherbox.y==(box.y+box.height):	setMembers.append(otherboxindex)
							# If otherbox is below box
							elif otherbox.x==box.x and otherbox.y==(box.y+box.height):	setMembers.append(otherboxindex)

				if len(setMembers)==3:
					# We found a set of four, and {box} is the one in the upper left
					# So we should assign points to the whole set
					# For now we just make a note to assign these points, but don't actually do it until the end of the scan. Otherwise we'll mess up the ongoing scan
					# e.g. if you find a group of 4 and immediately make them point blocks, you will not notice if they are actually part of 6+ block cluster
					box.temppoints=len(gameBoard.splitRecord)+1
					gameBoard.box[setMembers[0]].temppoints=len(gameBoard.splitRecord)+1
					gameBoard.box[setMembers[1]].temppoints=len(gameBoard.splitRecord)+1
					gameBoard.box[setMembers[2]].temppoints=len(gameBoard.splitRecord)+1
					return True

		# Any newly created clusters should also be immediately decremented and points awarded (they weren't around when the rest of the blocks had this done)
		for box in gameBoard.box:
			if box.temppoints != 0:
				box.points+=box.temppoints-1
				countDownScore+=1
				box.temppoints=0

	# -------- 8. Process halving of points from falling   ----------------------------------------------------------------------
	#
	#	Simogo's SPL-T rounds UP, e.g if a 5 point block falls the new point count will be 3 instead of 2
	#   not necessary
	
	#-------------------------------UPDATES GAMEBOARD PROPERTIES----------------------
    #updates number of horizontal and vertical splits in the gameboard (adds for each box with no points)
	# not necessary

	return False

def findCluster(gameBoard):
	"""
	Given a gameBoard, finds the clusters that would be caused by a split of any box in the board
	INPUT: gameBoard, the gameboard object
	OUTPUT: clusters, a list of sets. Each inner set contains the indices of boxes that are involved in a cluster when a given box is split.
	The inner list is an empty list when splitting a given box results in no cluster
	written in this gross way for efficiency reasons
	"""
	if timingInfo: start = time.time()
	clusters = []
	
	for boxToBeCheckedIndex, boxToBeChecked in enumerate(gameBoard.box):
		newClusters = set()
		if boxToBeChecked.splitPossible(gameBoard.splitAction):
			#Generate clusters for horizontal case
			if gameBoard.splitAction == HORIZONTAL:
				#DETERMINE WHAT CLUSTERS HAVE BEEN FORMED
				#index 0 contains box index of bottom box, index 1 is the top
				leftBoxes = [-1,-1] #primary clusters
				rightBoxes = [-1,-1] #primary clusters
				topBoxes = [-1,-1,-1] #secondary clusters
				bottomBoxes = [-1,-1,-1] #secondary clusters
				for otherBoxIndex, otherBox in enumerate(gameBoard.box):
					if (otherBox.height == boxToBeChecked.height//2 and otherBox.width == boxToBeChecked.width \
					and otherBox.points == 0):
						if (otherBox.x == boxToBeChecked.x + boxToBeChecked.width):
							if (otherBox.y == boxToBeChecked.y - boxToBeChecked.height//2):
								topBoxes[2] = otherBoxIndex #top right
							elif (otherBox.y == boxToBeChecked.y): 
								rightBoxes[1] = otherBoxIndex #right top
							elif (otherBox.y == boxToBeChecked.y + boxToBeChecked.height//2):
								rightBoxes[0] = otherBoxIndex #right bottom
							elif (otherBox.y == boxToBeChecked.y + boxToBeChecked.height):
								bottomBoxes[2] = otherBoxIndex #bottom right

						elif (otherBox.x == boxToBeChecked.x - boxToBeChecked.width):
							if (otherBox.y == boxToBeChecked.y - boxToBeChecked.height//2):
								topBoxes[0] = otherBoxIndex #top left
							elif (otherBox.y == boxToBeChecked.y):
								leftBoxes[1] = otherBoxIndex #left top
							elif (otherBox.y == boxToBeChecked.y + boxToBeChecked.height//2):
								leftBoxes[0] = otherBoxIndex #left bottom
							elif (otherBox.y == boxToBeChecked.y + boxToBeChecked.height):
								bottomBoxes[0] = otherBoxIndex #bottom left
						
						elif (otherBox.x == boxToBeChecked.x):
							if (otherBox.y == boxToBeChecked.y - boxToBeChecked.height//2):
								topBoxes[1] = otherBoxIndex #top middle
							elif (otherBox.y == boxToBeChecked.y + boxToBeChecked.height):
								bottomBoxes[1] = otherBoxIndex #bottom middle
						
						else:
							pass

				#If right cluster formed
				if (rightBoxes[0] != -1 and rightBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(len(gameBoard.box))
					newClusters.update(rightBoxes)
				
				#If bottom right cluster formed
				if (rightBoxes[0] != -1 and bottomBoxes[2] != -1 and bottomBoxes[1] != -1):
					newClusters.add(len(gameBoard.box))
					newClusters.add(rightBoxes[0])
					newClusters.update(bottomBoxes[1:3])

				#If bottom left cluster formed
				if (bottomBoxes[1] != -1 and bottomBoxes[0] != -1 and leftBoxes[0] != -1):
					newClusters.add(len(gameBoard.box))
					newClusters.add(leftBoxes[0])
					newClusters.update(bottomBoxes[0:2])
				
				#If left cluster formed
				if (leftBoxes[0] != -1 and leftBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(len(gameBoard.box))
					newClusters.update(leftBoxes)

				# If top left cluster formed
				if (leftBoxes[1] != -1 and topBoxes[0] != -1 and topBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(leftBoxes[1])
					newClusters.update(topBoxes[0:2])
				
				#If top right cluster formed
				if (topBoxes[1] != -1 and topBoxes[2] != -1 and rightBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(rightBoxes[1])
					newClusters.update(topBoxes[1:3])

			#Generate clusters for vertical case
			else:
				#DETERMINE WHAT CLUSTERS HAVE BEEN FORMED
				#index 0 contains box index of left box, index 1 is the right
				topBoxes = [-1,-1] #primary clusters
				bottomBoxes = [-1,-1] #primary clusters
				leftBoxes = [-1,-1,-1] #secondary clusters
				rightBoxes = [-1,-1,-1] #secondary clusters
				for otherBoxIndex, otherBox in enumerate(gameBoard.box):
					if (otherBox.height == boxToBeChecked.height and otherBox.width == boxToBeChecked.width//2 \
					and otherBox.points == 0):
						if (otherBox.y == boxToBeChecked.y - boxToBeChecked.height):
							if (otherBox.x == boxToBeChecked.x - boxToBeChecked.width//2):
								leftBoxes[2] = otherBoxIndex #left top
							elif (otherBox.x == boxToBeChecked.x): 
								topBoxes[0] = otherBoxIndex #top left
							elif (otherBox.x == boxToBeChecked.x + boxToBeChecked.width//2):
								topBoxes[1] = otherBoxIndex #top right
							elif (otherBox.x == boxToBeChecked.x + boxToBeChecked.width):
								rightBoxes[2] = otherBoxIndex #right top

						elif (otherBox.y == boxToBeChecked.y + boxToBeChecked.height):
							if (otherBox.x == boxToBeChecked.x - boxToBeChecked.width//2):
								leftBoxes[0] = otherBoxIndex #left bottom
							elif (otherBox.x == boxToBeChecked.x):
								bottomBoxes[0] = otherBoxIndex #bottom left
							elif (otherBox.x == boxToBeChecked.x + boxToBeChecked.width//2):
								bottomBoxes[1] = otherBoxIndex #bottom right
							elif (otherBox.x == boxToBeChecked.x + boxToBeChecked.width):
								rightBoxes[0] = otherBoxIndex #right bottom
						
						elif (otherBox.y == boxToBeChecked.y):
							if (otherBox.x == boxToBeChecked.x - boxToBeChecked.width//2):
								leftBoxes[1] = otherBoxIndex #left middle
							elif (otherBox.x == boxToBeChecked.x + boxToBeChecked.width):
								rightBoxes[1] = otherBoxIndex #right middle
						
						else:
							pass

				#If top cluster formed
				if (topBoxes[0] != -1 and topBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(len(gameBoard.box))
					newClusters.update(topBoxes)
				
				#If top right cluster formed
				if (topBoxes[1] != -1 and rightBoxes[2] != -1 and rightBoxes[1] != -1):
					newClusters.add(len(gameBoard.box))
					newClusters.add(topBoxes[1])
					newClusters.update(rightBoxes[1:3])
				
				#If bottom right cluster formed
				if (rightBoxes[1] != -1 and rightBoxes[0] != -1 and bottomBoxes[1] != -1):
					newClusters.add(len(gameBoard.box))
					newClusters.add(bottomBoxes[1])
					newClusters.update(rightBoxes[0:2])
				
				#If bottom cluster formed
				if (bottomBoxes[0] != -1 and bottomBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(len(gameBoard.box))
					newClusters.update(bottomBoxes)
				
				#If bottom left cluster formed
				if (bottomBoxes[0] != -1 and leftBoxes[0] != -1 and leftBoxes[1] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(bottomBoxes[0])
					newClusters.update(leftBoxes[0:2])
				
				#If top left cluster formed
				if (leftBoxes[1] != -1 and leftBoxes[2] != -1 and topBoxes[0] != -1):
					newClusters.add(boxToBeCheckedIndex)
					newClusters.add(topBoxes[0])
					newClusters.update(leftBoxes[1:3])
				
		clusters.append(newClusters)
		
	if timingInfo: 
		end = time.time()
		print("Time to find clusters for turn "+str(curr_splits)+": "+str(end-start))
	return clusters

def findLowestAvailableBox(gameBoard):
	"""
	Given a gameboard, determines the lowest box without points to split in the column.
	Based on the assumption that the gameboard will be organized into 4 clear columns and
	8 clear rows, we only save information on this. (This will only be used to influence
	splits after 300 splits, when the board has stabilized into this predictable form.)
	INPUTS: gameBoard, the current gameBoard object
	OUTPUTS: lowest_in_col, a dictionary
		-keys corresponding to column number (x=0-1->col=0, x=2-3->col=1, etc.)
		-values corresponding to row number (y=0-1->row=0,y=2-3->row=1)
	"""
	lowest_in_col = defaultdict(int)
	for box in gameBoard.box:
		if box.points == 0: #only care about boxes that are still available to split
			row = math.floor(box.y/2)
			col = math.floor(box.x/2)
			if row > lowest_in_col[col]:
				lowest_in_col[col] = row

	return lowest_in_col

def findPointBlockStackBelow(gameBoard, boxIndex):
	"""
	Given a gameboard and box index to split, returns a list of point block values
	below the given box. Assumes that every box below each block in the chain has
	the same value. If not (a block is supported by two blocks, each of which fall at separate times)
	things get super complicated and infeasible.

	Returns in top down order: i.e. if block w 200 is on block w 100, returns [200, 100]
	"""
	pbsverbose = 0
	box = gameBoard.box[boxIndex]
	rowBelowBox = box.y + box.height + 1

	point_blocks = []

	point_blocks.append(len(gameBoard.splitRecord)+1)

	current_x = box.x
	current_width = box.width

	#iterate downward by rows
	for row in range(rowBelowBox, gameBoard.height+1):
		if pbsverbose: print(f"~Looking in row {row}~")
		point_block_value_below = None
		for otherBoxIndex in gameBoard.boxesInRow[row]:
			otherBox = gameBoard.box[otherBoxIndex]

			#only selects boxes in the correct columns to be below the box you're looking at
			if otherBox.x+otherBox.width > current_x and otherBox.x < current_x+current_width:
				next_row_relevant_x = otherBox.x
				next_row_relevant_width = otherBox.width

				if pbsverbose: print(f"Found block {otherBoxIndex} under block {boxIndex} in row {row}")

				#add the value of this point block (minus 1) to the sequence, as long as the desired block isn't resting on multiple
				#blocks with different point values (in this case it's too complicated and we give up)
				if (point_block_value_below != None) and ((otherBox.points-1) != point_block_value_below):
					if pbsverbose:
						print(f"Different point value than previous block found under current block on stack (current: {otherBox.points-1} old: {point_block_value_below})")
						print("Thus, exiting function because the problem is now too complex.")
					return False

				if (otherBox.points == 0):
					if pbsverbose: print(f"Block {otherBoxIndex} below will not explode, so stopping chain here")
					return point_blocks
				
				point_block_value_below = otherBox.points-1
		
		current_x = next_row_relevant_x
		current_width = next_row_relevant_width
		
		if pbsverbose: print(f"Adding {point_block_value_below} from row {row}")
		point_blocks.append(point_block_value_below)

	return point_blocks

def decrementPointBlocks(point_block_stack):
	"""
	Given a stack of point blocks in top-down order i.e.
	[100, 50, 10, 1] -> [49, 24, 4] -> [22, 10] -> [12, 0]
	decrements the stack according to rules of SPLT (including halvings)
	until the new block is alone with one other block.

	Returns the entire stack when the top block reaches 0
	"""


	while point_block_stack[0] > 0:
		if 0 in point_block_stack:
			lowest_block_exploding_index =  next(i for i in reversed(range(len(point_block_stack))) if point_block_stack[i] == 0)

			#only split blocks that come before in the list (are above the exploding block)
			for i in range(lowest_block_exploding_index):
				#splits round down, unless the block is at 1
				if point_block_stack[i] == 1: pass
				else: point_block_stack[i] = point_block_stack[i]//2

			point_block_stack = [point_block for point_block in point_block_stack if point_block != 0] #removes 0s at this point
		
		point_block_stack = [point_block-1 for point_block in point_block_stack]
	
	return point_block_stack


def doesPointBlockCauseNewHalving(gameBoard, boxIndex):
	"""
	Given a gameboard and a box index to split which will create point blocks,
	determines if the split will cause a new halving to occur. Return True if so, False if not
	"""
	boxIndexesInCluster = gameBoard.clusters[boxIndex]
	if boxIndexesInCluster == set() or boxIndexesInCluster == []: pass #if set is empty, then this doesn't create a cluster and this function shouldn't have been called
	else:
		workingGb = copy.deepcopy(gameBoard)
		workingGb.split(workingGb.box[boxIndex])
		boxIndexesInCluster.add(len(workingGb.box)-1)
		#Now we need to find representative boxes from this new cluster of point blocks which
		#we can use to determine if these point blocks will result in a new halving.
		#We want the box from the cluster with the highest y value in each x location. (lowest on the board)
		maxYofCluster = max([workingGb.box[clusterBoxInd].y for clusterBoxInd in boxIndexesInCluster])

		for clusterBoxIndex in boxIndexesInCluster:
			clusterBox = workingGb.box[clusterBoxIndex]
			if clusterBox.y == maxYofCluster:
				point_blocks_below = findPointBlockStackBelow(workingGb, clusterBoxIndex)
				if point_blocks_below == False: pass #too complex to tell, so just skip it
				else: 
					stack_when_new_block_about_to_explode = decrementPointBlocks(point_blocks_below)
					
					#If only one block is exploding when the new point block is, then it caused a new halving
					#(we know that the new point block is the only one with it's initial value in point_blocks_below)
					if stack_when_new_block_about_to_explode.count(0) == 1: return True

	#if you made it this far without finding a new halving, there is no halving
	return False

def findWeights(gameBoard,weightverbose=0):
	"""
	Given a gameboard and thus the list of boxes in the gameboard, gameBoard.box, finds the weights of each box in the gameboard.
	Factors that are considered:
	-Split Imbalance: the difference between the number of vertical and horizontal lights in the board, in proportion to the total splits,
	is considered. For example, creating many vertical splits with a split when there are already many more vertical split opportunities on the board
	recieves a negative weight.
	-Aspect Ratio: An aspect ratio of 1 is ideal. Splitting blocks such that the aspect ratio increases recieves a penalty. 
	No bonus is recieved for lowering the aspect ratio.
	-Point Block Locations: creating clusters above point blocks that are about to explode recieve large positive weights.
	Splitting boxes without creating clusters is still prioritized above point blocks that are about to explode
	-Split Height: Splitting blocks and making point blocks at lower locations on the board is prioritized
	INPUTS: gameBoard, the current gameBoard object
	OUTPUTS: weights, a list of numbers corresponding to the statistical weighting of a given box being split
	"""
	if timingInfo: start = time.time()

	weights = []

	total_splits = gameBoard.hor_splits+gameBoard.ver_splits
	splitImbalance = gameBoard.hor_splits-gameBoard.ver_splits

	curr_splits = len(gameBoard.splitRecord)

	splitsUntilFall = findSplitsUntilFall(gameBoard)

	aboutToLose = (total_splits < min(splitsUntilFall.values()))

	lowest_in_col = findLowestAvailableBox(gameBoard)

	if weightverbose: 
		print("_________________________________________________________")
		print("Calculating weights for move "+str(curr_splits))
		print("_________________________________________________________")

	for boxToBeWeightedIndex, boxToBeWeighted in enumerate(gameBoard.box):
		#only assign a weight to boxes that don't already have points and that can be split this turn
		if boxToBeWeighted.points == 0 and boxToBeWeighted.splitPossible(gameBoard.splitAction):
			weight = 0 #default weight

			createPoints = gameBoard.clusters[boxToBeWeightedIndex] != set()

			#----------------------IMBALANCE WEIGHT-------------------------------- 
			#weight depending on the balance of horizontal to vertical splits in the board

			if weightverbose: 
				print(" ")
				print("BLOCK "+str(boxToBeWeightedIndex))
				print("~~~Finding weight from imbalance for block "+str(boxToBeWeightedIndex)+":~~~") 
				print(str(splitImbalance) + " more hor than ver splits for split " + str(curr_splits))
				

			if gameBoard.splitAction == HORIZONTAL:
				#ensures that splitting the box wouldnt make a cluster: if it does, this weight is irrelevant
				if not createPoints:
					verticalSplitsToAdd = (boxToBeWeighted.width-1)
					if weightverbose: print("Splitting box " + str(boxToBeWeightedIndex) + " would create " + str(verticalSplitsToAdd) + " new vertical splits.")

					#if there are more vertical than horizontal splits, negative weighting increases linearly with vertical splits added
					if splitImbalance <= 0:
						
						weightToAdd = (-15/7)*verticalSplitsToAdd #Eyeballed to provide -15 weight when adding the max
						#Scales based off how urgent the imbalance is relative to how many total splits are left. 2x weight when the imbalance is 50% of the total splits left
						weightToAdd = weightToAdd*(4*abs(splitImbalance)/total_splits)

						if weightverbose: print("More vertical than horizontal splits, so we add weight of " + str(weightToAdd))

					#if there are more horizontal than vertical splits, positive weighting follows parabola
					elif splitImbalance >0:
						#quadratic regression is eyeballed to be 0 at 0%, 5 at 200%, 15 at 100% 
						percent = verticalSplitsToAdd/abs(splitImbalance)
						weightToAdd = -12.5*percent**2+27.5*percent

						#Scales based off how urgent the imbalance is relative to how many total splits are left. 2x weight when the imbalance is 50% of the total splits left
						weightToAdd = weightToAdd*(4*abs(splitImbalance)/total_splits)

						if weightverbose: print("More horizontal than vertical splits, so we add weight of " + str(weightToAdd))
					
					#If you're gonna lose inevitably, this is the only thing that matters:
					if aboutToLose: 
						weightToAdd *= 100

					weight += weightToAdd

				else:
					if weightverbose: print("Splitting this box would cause a cluster, so we don't weight it.")	
					pass
			
			#calculate imbalance weight for vertical splits
			else:
				#ensures that splitting the box wouldnt make a cluster: if it does, this weight is irrelevant
				if not createPoints:
					horizontalSplitsToAdd = (boxToBeWeighted.height-1)
					if weightverbose: print("Splitting box " + str(boxToBeWeightedIndex) + " would create " + str(horizontalSplitsToAdd) + " new horizontal splits.")

					#if there are more horizontal than vertical splits, negative weighting increases linearly with horizontal splits added
					if splitImbalance >= 0:
						
						weightToAdd = (-15/7)*horizontalSplitsToAdd #Eyeballed to provide -15 weight when adding the 7 new horizontal splits
						#Scales based off how urgent the imbalance is relative to how many total splits are left. 2x weight when the imbalance is 50% of the total splits left
						weightToAdd = weightToAdd*(4*abs(splitImbalance)/total_splits)

						if weightverbose: print("More horizontal than vertical splits, so we add weight of " + str(weightToAdd))

					#if there are more vertical than horizontal splits, positive weighting follows parabola
					elif splitImbalance <0:
						#quadratic regression is eyeballed to be 0 at 0%, 5 at 200%, 15 at 100% 
						percent = horizontalSplitsToAdd/abs(splitImbalance)
						weightToAdd = -12.5*percent**2+27.5*percent

						#Scales based off how urgent the imbalance is relative to how many total splits are left. 2x weight when the imbalance is 50% of the total splits left
						weightToAdd = weightToAdd*(4*abs(splitImbalance)/total_splits)

						if weightverbose: print("More vertical than horizontal splits, so we add weight of " + str(weightToAdd))
					
					weight += weightToAdd

				else:
					if weightverbose: print("Splitting this box would cause a cluster, so weighting based on imbalance is irrelevant.")
					pass
			

			#----------------------------------ASPECT RATIO WEIGHT---------------------------------
			if weightverbose: 
				print("Total weight is now "+str(weight))
				print("~~~Finding weight from aspect ratio:~~~")

			aspectRatio = max(boxToBeWeighted.width,boxToBeWeighted.height)/min(boxToBeWeighted.width,boxToBeWeighted.height)

			weightToAdd = 0
			if gameBoard.splitAction == HORIZONTAL:
				newaspectRatio = max(boxToBeWeighted.width,boxToBeWeighted.height/2)/min(boxToBeWeighted.width,boxToBeWeighted.height/2)
			else:
				newaspectRatio = max(boxToBeWeighted.width/2,boxToBeWeighted.height)/min(boxToBeWeighted.width/2,boxToBeWeighted.height)
			
			#only applies a penalty to making a worse aspect ratio
			if newaspectRatio - aspectRatio > 1:
				#eyeballed to remove 10 points when taking an aspect ratio from 4 to 8, remove 2 points when taking an aspect ratio from 2 to 4
				if (newaspectRatio - aspectRatio) >=4:
					weightToAdd = -20
				elif (newaspectRatio - aspectRatio) >=2:
					weightToAdd = -10
					if curr_splits > 450:
						weightToAdd = -15
				if weightverbose: 
					print("Aspect ratio is getting worse, going from "+str(aspectRatio)+" to "+str(newaspectRatio))
					print("We add a penalty weight of "+str(weightToAdd))
			else:
				if weightverbose: print("Aspect ratio is getting no worse, so no penalty is added")
			
			weight += weightToAdd


			#--------------------------------------POINT BLOCK WEIGHT------------------------------------
			#Weight based on how soon the next point block explosion in the boxes column will occur
			if weightverbose: 
				print("Total weight is now "+str(weight))
				print("~~~Finding weight from point block explosions:~~~")
				print("There are "+str(splitsUntilFall[boxToBeWeightedIndex])+" splits until the box falls.")


			weightToAdd = 0
			#only assigns weight if the box is sitting on a point block
			if splitsUntilFall[boxToBeWeightedIndex] != 0:

				#now we add weight to boxes differently depending on whether splitting the box will cause a cluster.
				if createPoints:
					#Determine if adding another cluster in this row will cause another halving to occur:
					turns = math.ceil(splitsUntilFall[boxToBeWeightedIndex]/2)

					if doesPointBlockCauseNewHalving(gameBoard, boxToBeWeightedIndex):
						# weightToAdd = 2*(22.1475/(1+.1518*math.exp(1.14*turns)))
						weightToAdd = 15 #If you're creating a new halving, you always wanna do this! The sooner you do this, the sooner you can make another
						# weightToAdd = max(5,-15/14*splitsUntilFall[boxToBeWeightedIndex]+15+15/14)
						weightToAdd = (29.53/(1+.1518*math.exp(1.14*turns)))+20
						if weightverbose: print(f"There is an extra halving that occurs by splitting this block. Add {weightToAdd} points!")
					else:
						#eyeballed to add 20 points of weight when this is the last chance to create the cluster, exponentially decreasing to 0 points when it is not urgent
						weightToAdd = (22.1475/(1+.1518*math.exp(1.14*turns)))
						# weightToAdd = (29.53/(1+.1518*math.exp(1.14*turns)))+20

						if weightverbose: 
							print("This will (probably) not create a new halving, so we add weight based on urgency.")
							print("There are "+str(turns)+" opportunities to make this cluster until the split is made, so we add "+str(weightToAdd)+" weight.")
				
				#otherwise, if splitting the box won't cause a cluster, we prioritize splitting boxes in this row, but less aggressively
				else:
					a = 13
					b = 1.6
					c = -0.2
					#Eyeball the weight to be highest (~16) at 4 splits left, decreasing to zero at 13 splits away
					if 4 <= splitsUntilFall[boxToBeWeightedIndex] < 13:
						weightToAdd = c*splitsUntilFall[boxToBeWeightedIndex]**2+b*splitsUntilFall[boxToBeWeightedIndex]+a
					elif splitsUntilFall[boxToBeWeightedIndex] == 3:
						weightToAdd = 10 #doesn't fit in exponential, but should be significantly less valued than 4 splits left
					else:
						weightToAdd = 0
					
					if weightverbose: 
						print("Splitting this box WILL NOT cause a cluster, so we add weight accordingly.")
						print("There are "+str(splitsUntilFall[boxToBeWeightedIndex])+" splits until the block is halved, so we add "+str(weightToAdd)+" weight.")

					# #if you're too late to make this split, calculate based on the next split that will happen
					# if splitsUntilFall[boxToBeWeightedIndex] <=2 and len(pointBlocksBelow[boxToBeWeightedIndex]) > 1:
					# 	newPointBlocksBelow = pointBlocksBelow[boxToBeWeightedIndex][1:]
					# 	tillFall = math.ceil((min(newPointBlocksBelow)-splitsUntilFall[boxToBeWeightedIndex])/2)
						
					# 	#weight the same way as above, but using the new number of splits until fall
					# 	if 2 < tillFall < 13:
					# 		weightToAdd = c*splitsUntilFall[boxToBeWeightedIndex]**2+b*splitsUntilFall[boxToBeWeightedIndex]+a
					# 	else:
					# 		weightToAdd = 0
						
					# 	if weightverbose:
					# 		print("This block will fall in "+str(splitsUntilFall[boxToBeWeightedIndex])+" splits, so there's no chance we make a point block before this.")
					# 		print("Entire list of point blocks beneath, minus the lowest:")
					# 		print(newPointBlocksBelow)
					# 		print("New splits until falling: "+str(tillFall))
					# 		print("Using this number of splitsUntilFall, we add "+str(weightToAdd)+" weight.")	
				
				#Penalize weight by 50% if theres another available point block in a lower row in this column.
				#This means that you will strand a higher point block lower down, effectively losing the benefit of this split
				#Only activate at splits>300, when the board position normalizes further
				if curr_splits > 300:
					box_row = math.floor(boxToBeWeighted.y/2)
					box_col = math.floor(boxToBeWeighted.x/2)
					if box_row < lowest_in_col[box_col]:
						weightToAdd *= 0.5
						if weightverbose: print("Not in the lowest row in this column, so dividing weight by 2")
						
			else:
				if weightverbose: print("This block is sitting on no point blocks, so we assign no extra split weight.")

			weight += weightToAdd

			if weightverbose: 
				print("Total box weight is now "+str(weight))
				print("~~~Finding weight from height:~~~")

			#---------------------------NEXT HIGHEST IN COL WEIGHT----------------
			# Add weight if the next highest block in the column is way lower the current number of splits		
			# if len(pointBlocksBelow[boxToBeWeightedIndex]) != 0 and curr_splits > 800:
			# 	curr_highest_split_pct = (curr_splits-pointBlocksBelow[boxToBeWeightedIndex][-1])/curr_splits
			# 	weightToAdd = 9*curr_highest_split_pct
			# 	weight += weightToAdd

			# 	if weightverbose:
			# 		print("~~~Finding weight from highest point block beneath:~~~")
			# 		print("Highest point block below is {} ({} pct of splits), so adding {} weight"\
			# 			.format(pointBlocksBelow[boxToBeWeightedIndex][-1],curr_highest_split_pct,weightToAdd))
			# 		print("Total weight is now {}".format(weight))
				

			# --------------------------HEIGHT WEIGHT-----------------------------
			# Adds bonus weight of up to 7.5 when splitting blocks at the bottom of the board. 
			# This factor is extra important if the split would create a cluster. (200%)

			if createPoints:

				#determine the lowest height of the cluster that is created 
				maxHeight = 0
				for boxIndex in gameBoard.clusters[boxToBeWeightedIndex]:

					#clusters includes the box that would be created in the split in the list, so if it tries to use this we just ignore it
					try:
						candHeight = gameBoard.box[boxIndex].y + gameBoard.box[boxIndex].height
					except:
						candHeight = 0
						pass
					
					if candHeight> maxHeight:
						maxHeight = candHeight

				weightToAdd = 20*(maxHeight/gameBoard.height)**2

				if weightverbose: 
					print("This will create point blocks with a bottom at "+str(maxHeight)+".")
					print("Add " + str(weightToAdd) + " weight.")
			
			else:
				weightToAdd = 10*((boxToBeWeighted.y+boxToBeWeighted.height)/gameBoard.height)**2

				if weightverbose: 
					print("Bottom of the block is at "+str(boxToBeWeighted.y+boxToBeWeighted.height)+", but will not create a point block.")
					print("Add " + str(weightToAdd) + " weight.")
			
			weight += weightToAdd

			if weightverbose: 
				print("Total box weight is now "+str(weight))
				print("~~~Finding weight from point block size:~~~")

			#----------------------POINT BLOCK SIZE WEIGHT----------------------------------
			if createPoints:
				#determine how many total points are left in the board
				max_splits = 0
				for box in gameBoard.box:
					if box.points == 0:
						max_splits += box.width*box.height-1

				clusterSquares = (boxToBeWeighted.width*boxToBeWeighted.height)/2*(len(gameBoard.clusters[boxToBeWeightedIndex]))

				# #determine how many squares the cluster will be
				# if gameBoard.splitAction == HORIZONTAL:
				# 	splitsAvailable = (box.width*box.height)-1
				# else:
				# 	splitsAvailable = (box.width*box.height)-1

				# clusterSquares = len(gameBoard.clusters[boxToBeWeightedIndex])/2*splitsAvailable

				#if clustersquares is not the minimum (4), apply a penalty based on the proportion 
				# of the remaining squares that the cluster takes up
				if clusterSquares > 4:
					weightToAdd = -60*(clusterSquares/total_splits)*(curr_splits/200)
				else:
					weightToAdd=0
				
				weight += weightToAdd

				if weightverbose:
					print("This cluster takes up "+str(clusterSquares)+" available splits.")
					print("There are "+str(max_splits)+" splits left on the board.")
					print("We add "+str(weightToAdd)+" to the weight.")
					print("Total weight is now: {}".format(weight))

			else:
				if weightverbose: print("`This block doesn`'t create point blocks, so we do nothing.")

			# if createPoints:
			# 	weightToAdd = 0
			# 	if gameBoard.splitAction == HORIZONTAL:
			# 		if (box.width != 1 or box.height != 2) and curr_splits > 50:
			# 			weightToAdd = -50
			# 		# splitsAvailable = (box.width*box.height)-1
			# 	else:
			# 		if (box.width != 2 or box.height != 1) and curr_splits > 50:
			# 			weightToAdd = -50

			# 	weight += weightToAdd
			
			#---------------------- CLUSTER BETWEEN ROW/COLUMN WEIGHT PENALTY----------------
			#clusters that start in the middle of columns or rows
			if len(gameBoard.clusters[boxToBeWeightedIndex]) > 4:
				weightToAdd = -10
			else:
				weightToAdd = 0

			if weightverbose:
				print("~~~Finding weight from mid-column/row penalties~~~")
			
			weightToAdd = 0
			if createPoints:
				if weightverbose:
					print("Splitting this box would create a cluster, so we check if the cluster ends in the middle of any rows/colums")
				#find the where the rightmost and bottommost clusters in the cluster are
				minX = 8
				minY = 16
				maxX = 0
				maxY = 0
				clusters = gameBoard.clusters[boxToBeWeightedIndex]
				for clusterBoxIndex in clusters:
					if clusterBoxIndex < len(gameBoard.box): #ensure that you're not trying to check box that doesn't exist yet
						if gameBoard.box[clusterBoxIndex].x > maxX:
							maxX = gameBoard.box[clusterBoxIndex].x
						if gameBoard.box[clusterBoxIndex].y > maxY:
							maxY = gameBoard.box[clusterBoxIndex].y
						if gameBoard.box[clusterBoxIndex].x < minX:
							minX = gameBoard.box[clusterBoxIndex].x
						if gameBoard.box[clusterBoxIndex].y < minY:
							minY = gameBoard.box[clusterBoxIndex].y

				#determine height and width of boxes in cluster based on type of split
				clusterTop = minY
				clusterLeft = minX
				if gameBoard.splitAction == HORIZONTAL:
					clusterBottom = maxY+boxToBeWeighted.height//2
					clusterRight = maxX+boxToBeWeighted.width
					if weightverbose:
						print("Min Y from created cluster is "+str(clusterTop))
						print("Min X from created cluster is "+str(clusterLeft))
						print("Max Y from created cluster is "+str(clusterBottom))
						print("Max X from created cluster is "+str(clusterRight))
				else:
					clusterBottom = maxY+boxToBeWeighted.height
					clusterRight = maxX+boxToBeWeighted.width//2
					if weightverbose:
						print("Min Y from created cluster is "+str(clusterTop))
						print("Min X from created cluster is "+str(clusterLeft))
						print("Max Y from created cluster is "+str(clusterBottom))
						print("Max X from created cluster is "+str(clusterRight))
		
				if (clusterBottom % 2) != 0 or (clusterTop % 2) != 0:
					weightToAdd -= 50
					if weightverbose: print("Cluster starts or ends in odd row, so add a weight of "+str(weightToAdd))
				if (clusterRight % 2) != 0 or (clusterLeft % 2) != 0:
					weightToAdd -= 50
					if weightverbose: print("Cluster start or ends in odd column, so add a weight of "+str(weightToAdd))


			weight += weightToAdd

			#----------------------BREAKING UP BIG HORIZONTAL BONUS----------------
			#clusters that start in the middle of columns or rows
			weightToAdd = 0
			if weightverbose: print("~~~Finding penalties bonuses related to wide blocks~~~")
			if gameBoard.splitAction == HORIZONTAL:
				if boxToBeWeighted.height > 2 and boxToBeWeighted.width > 2:
					weightToAdd = -5
					if weightverbose:
						print("Creates multiple wide blocks (height = {}, width = {}, splitting horizontally)".format(boxToBeWeighted.height,boxToBeWeighted.width))
						print("Thus, {} weight".format(weightToAdd))
			else:
				if boxToBeWeighted.width > 2:
					weightToAdd = 5
					if weightverbose:
						print("Splits wide block (width = {}, splitting horizontally)".format(boxToBeWeighted.width))
						print("Thus, {} weight".format(weightToAdd))
			
			weight += weightToAdd


			#----------------------AVOID TRIPLE EDGE CASE----------------
			#if splitting a block would prevent you from creating a cluster below, weight it very slightly less
			# -------			-------	            -------		
			# |     |			|  |  |             |     |
			# -------			-------             -------
			# |     |	THIS	|	  |	    NOT     |  |  | 
			# ------- 	---->   -------   --XX-->   ------- 
			# |  |  |           |  |  |             |  |  |
			# |  |  |           |  |  |             |  |  |
			# |  |  |           |  |  |             |  |  |
			# -------           -------             -------
			weightToAdd = 0
			if boxToBeWeighted.width == 2 and boxToBeWeighted.height == 1 and gameBoard.splitAction == VERTICAL:
				#check if there is a small box and tall box below
				uprightBox = 0
				smallBox = 0
				for box in gameBoard.box:
					if (box.x == boxToBeWeighted.x) or (box.x == boxToBeWeighted.x+1):
						if box.width == 1 and box.y == boxToBeWeighted.y+1:
							if box.height == 2:
								uprightBox = 1
							elif box.height == 1:
								smallBox = 1
				if uprightBox and smallBox: 
					weightToAdd = -1
					if weightverbose: print("Forced triple edge case! Subtracting 1 to make the difference")
			
			#TODO: Could also do other edge case here, the horizontal equivalent. Comes up less often
			
			weight += weightToAdd

			if weightverbose: print("FINAL weight is: {}".format(weight))

			weights.append(weight)

		else:
			weights.append(0)

	if weightverbose:
		print(" ")
		print("All weights before adjustment:")
		print(weights)
		print(" ")

	#Once we have the highest weight, make sure that it doesnt cause an unexpected cluster.
	#Keep going through all the best choices until you find one that doesn't cause an unexpected cluster, or until
	#the best choice is one that does cause an unexpected cluster
	wasUnexpectedClusterFormed = True #starts as true
	splits_that_cause_unexpected_cluster = set()
	while wasUnexpectedClusterFormed:
		best_choice = max(range(len(weights)), key=weights.__getitem__) #index of max weight
		if weightverbose: print(f"Block {best_choice} is the best choice after final weighting.")
		if best_choice not in splits_that_cause_unexpected_cluster: splits_that_cause_unexpected_cluster.add(best_choice)
		else: 
			if weightverbose: print(f"Block {best_choice} would cause unexpected cluster but is still the best choice, so we finalize weights.")
			break #if the best choice does cause unexpected cluster even after penalization, it is still the best choice
		
		if gameBoard.box[best_choice].splitPossible(gameBoard.splitAction): #need to make sure the new best_choice is possible to split - if not, subtract so that it's hopefully no longer best choice
			gb_copy = copy.deepcopy(gameBoard)
			wasUnexpectedClusterFormed = doesUnexpectedClusterForm(gb_copy, best_choice)
			if wasUnexpectedClusterFormed:
				weights[best_choice] -= .02*len(gameBoard.splitRecord)
				if weightverbose: print(f"Block {best_choice} would cause unexpected cluster, so decrease it's weight by {.02*len(gameBoard.splitRecord)}.")
			elif weightverbose: print("Best choice does not cause unexpected cluster, so we finalize weights.")
		else:
			if weightverbose: print(f"Block {best_choice} is not a valid split - subtracting 15 and moving to next box.")
			weights[best_choice] -= 15

	#to prevent negative weights, we take the lowest weight and add it to the entire list, making the worst block have no shot at being chosen 
	#and other negative blocks with a low chance at being chosen
	minWeight = min(weights)
	if minWeight <=0:
		minWeight = -minWeight
		weights = [x+minWeight+.01 for x in weights]

	for boxind, box in enumerate(gameBoard.box):
		if not box.splitPossible(gameBoard.splitAction):
			weights[boxind] = 0
	
	if weightverbose: 
		print("Final weights vector:") 
		print(weights)

	if timingInfo: 
		end = time.time()
		print("Time to calculate weights until fall for turn {}: {}".format(curr_splits,end-start))
	return weights

def causeNewHalvingTestSuite():
	gb = core.Board()
	gb.box = []
	gb.makeBox(4, 0, 2, 4, 0) #to be split

	gb.makeBox(0, 0, 4, 16, 0) #left side box
	gb.makeBox(6, 0, 2, 16, 0) #right side box

	gb.makeBox(4, 4, 1, 4, 0)
	gb.makeBox(5, 4, 1, 4, 0)

	gb.makeBox(4, 8, 1, 1, 200)
	gb.makeBox(4, 9, 1, 1, 200)
	gb.makeBox(5, 8, 1, 1, 200)
	gb.makeBox(5, 9, 1, 1, 200)

	gb.makeBox(4, 10, 1, 1, 170)
	gb.makeBox(4, 11, 1, 1, 170)
	gb.makeBox(5, 10, 1, 1, 170)
	gb.makeBox(5, 11, 1, 1, 170)
	# gb.makeBox(4,10, 2, 2, 170)

	gb.makeBox(4, 12, 1, 1, 150)
	gb.makeBox(4, 13, 1, 1, 150)
	gb.makeBox(5, 12, 1, 1, 150)
	gb.makeBox(5, 13, 1, 1, 150)

	gb.makeBox(4, 14, 1, 1, 100)
	gb.makeBox(4, 15, 1, 1, 100)
	gb.makeBox(5, 14, 1, 1, 0)
	gb.makeBox(5, 15, 1, 1, 0)

	# gb.clusters = []
	# for i in range(len(gb.box)):
	# 	gb.clusters.append(set())
	# print(gb.clusters)
	gb.splitAction = VERTICAL
	gb.boxesInRow = defaultdict(list)
	for boxIndex,box in enumerate(gb.box):
		if box.points == 0:
			gb.hor_splits += box.height-1
			gb.ver_splits += box.width-1
		for row in range(1,gb.height+1):
			if box.y < row <= box.y + box.height:
				gb.boxesInRow[row].append(boxIndex)
	gb.splitRecord = [0]*210

	# print(findCluster(gb))

	# findWeights(gb)
	gb.clusters = findCluster(gb)
	print(gb.clusters)
	core.drawScreen(gb)

	print(doesPointBlockCauseNewHalving(gb, 0))

if __name__ == '__main__':
	# gb = core.Board()
	# # core.makeMove(gb,0)
	# # core.makeMove(gb,0)
	# # core.makeMove(gb,0)
	# # core.makeMove(gb,0)
	# # core.makeMove(gb,1)
	# # findCluster(gb)

	# core.makeMove(gb,0)
	# core.makeMove(gb,1)
	# core.makeMove(gb,2)
	# core.makeMove(gb,3)
	# core.makeMove(gb,3)
	# core.makeMove(gb,2)
	# core.makeMove(gb,4)
	# core.makeMove(gb,1)
	# core.makeMove(gb,6)
	# core.makeMove(gb,6)
	# core.makeMove(gb,6)
	# core.makeMove(gb,9)
	# core.makeMove(gb,10)
	# core.makeMove(gb,0)
	# core.makeMove(gb,5)
	# core.makeMove(gb,10)
	# core.makeMove(gb,8)
	# core.makeMove(gb,0)
	# core.makeMove(gb,13)
	# core.makeMove(gb,16)
	# core.makeMove(gb,2)
	# core.drawScreen(gb)
	# # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	# # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	# # suf, pbb = findSplitsUntilFall(gb)
	# # print(suf)
	# # print(pbb)
	# print(findSplitsUntilFall(gb))
	# doesPointBlockCauseNewHalving(gb, 9)
	# causeNewHalvingTestSuite()
	print(decrementPointBlocks([300, 20, 200]))