import math
import copy
import time
from collections import defaultdict
import core_update as core

weightverbose = 0
timingInfo = 0
HORIZONTAL='-'
VERTICAL='|'

def findCluster(gameBoard):
	#Given a gameBoard, finds the clusters that would be caused by a split of any box in the board
	#INPUT: gameBoard, the gameboard object
	#OUTPUT: clusters, a list of sets. Each inner set contains the indices of boxes that are involved in a cluster when a given box is split.
	#The inner list is an empty list when splitting a given box results in no cluster

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

def findSplitsUntilFall(gameBoard):
	"""
	Given a gameboard object, finds the points until each block falls.
	INPUT: gameBoard object
	OUTPUT: splitsUntilFall, a dictionary with form {blockIndex:splits_until_fall}
	pointBlocksBelow, a dictionary with form {blockIndex:[points of point blocks below]}
	"""
	if timingInfo: start = time.time()
	splitsUntilFall = {}
	pointBlocksBelow = defaultdict(list)

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
		pointBlocksBelow[boxIndex] = [box.points]

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
						pointBlocksBelow[boxIndex] = copy.copy(pointBlocksBelow[otherBoxIndex])


			#the box with fall when its points run out, or a block below falls: whichever comes first. However, we only want to do this when the points are nonzero.
			if box.points != 0 and maxSplitsToFall != 0:

				#if it was also a point block, just one of higher value than the minimum, add it's points to pointBlocksBelow
				if box.points > maxSplitsToFall and box.points not in pointBlocksBelow[boxIndex]:
					pointBlocksBelow[boxIndex].append(box.points)

				splitsUntilFall[boxIndex] = min([box.points,maxSplitsToFall])
			else:
				splitsUntilFall[boxIndex] = maxSplitsToFall

			if sufverbose: print("We choose the minimum between " + str(box.points)+" and "+str(maxSplitsToFall)+" (excluding zero), yielding "+str(splitsUntilFall[boxIndex])+" for box "+str(boxIndex))
	
	if timingInfo: 
		end = time.time()
		print("Time to find splits until fall for turn "+str(curr_splits)+": "+str(end-start))

	return splitsUntilFall, pointBlocksBelow
	
def findSoonestSplit(gameBoard):
	soonest_split = float('inf')
	for box in gameBoard.box:
		if box.points != 0 and box.points:
			splitsLeft += (box.width * box.height) - 1
	
	return splitsLeft

def findLowestAvailableBox(gameBoard):
	"""
	Given a gameboard, determines the lowest box without points to split in the column.
	Based on the assumption that the gameboard will be organized into 4 clear columns and
	8 clear rows, we only save information on this. (This will only be used to influence
	splits after 300 splits, when the board has stabilized into this predicatbale form.)
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

	splitsUntilFall,pointBlocksBelow = findSplitsUntilFall(gameBoard)

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
				
				extraSplitsBelow = len(pointBlocksBelow[boxToBeWeightedIndex])-1
				difference = (curr_splits+1) - (pointBlocksBelow[boxToBeWeightedIndex][-1]-1) 

				#now we add weight to boxes differently depending on whether splitting the box will cause a cluster.
				if createPoints:
					#Determine if adding another cluster in this row will cause another halving to occur - only happens when the difference is more than 2^number of halvings
					#If so, apply a small extra weight to splitting this  box, and a large extra weight to the box if splitting it would cause a cluster
					#weight this extra weight based on the number of splits left until the block falls. Use ceil(splitsUntilFall/2)

					if weightverbose: print("There are "+str(extraSplitsBelow)+" extra halvings occuring on this box before it reaches 0. The difference between the next lowest point block in the column is "+str(difference)+".")

					if difference >= 2**extraSplitsBelow:
						if weightverbose: print("This difference is enough to cause another halving, so we increase the block's weight.")
						#eyeballed to add 40 points of weight when this is the last chance to create the cluster, exponentially decreasing to 20 points when it is not urgent
						#If the difference is less than 2^(splitsUntilFall+1), then decrease the weight increase by 15% because its harder to 
						#take full advantage of the double split, but it's still a double split
						turns = math.ceil(splitsUntilFall[boxToBeWeightedIndex]/2)

						weightToAdd = (29.53/(1+.1518*math.exp(1.14*turns)))+20

						if weightverbose: 
							print("Splitting this box WILL cause a cluster, so we add weight accordingly.")
							print("There are "+str(turns)+" opportunities to make this cluster until the split is made, so we add "+str(weightToAdd)+" weight.")

						if difference < 2**(extraSplitsBelow+1): 
							weightToAdd = weightToAdd*.85
							if weightverbose: print("-Difference is small enough that the blocks will end up one apart. We penalize the weight by 15%, yielding: "+str(weightToAdd))
					
					else:
						if weightverbose: print("Making this point block will not lead to another halving, so we assign no extra weight to it.")
				
				#otherwise, if splitting the box won't cause a cluster, we prioritize splitting boxes in this row, but less aggressively
				else:
					a = 13
					b = 1.6
					c = -0.2
					if difference >= 2**extraSplitsBelow or splitsUntilFall[boxToBeWeightedIndex] <= 5:
						#Eyeball the weight to be highest (~16) at 4 splits left, decreasing to zero at 13 splits away
						if 2 < splitsUntilFall[boxToBeWeightedIndex] < 13:
							#weightToAdd = -.15625*splitsUntilFall[boxToBeWeightedIndex]**2+3.125*splitsUntilFall[boxToBeWeightedIndex]-5.625
							weightToAdd = c*splitsUntilFall[boxToBeWeightedIndex]**2+b*splitsUntilFall[boxToBeWeightedIndex]+a
						else:
							weightToAdd = 0
						
						if weightverbose: 
							print("Splitting this box WILL NOT cause a cluster, so we add weight accordingly.")
							print("There are "+str(splitsUntilFall[boxToBeWeightedIndex])+" splits until the block is halved, so we add "+str(weightToAdd)+" weight.")

						#if you're too late to make this split, calculate based on the next split that will happen
						if splitsUntilFall[boxToBeWeightedIndex] <=2 and len(pointBlocksBelow[boxToBeWeightedIndex]) > 1:
							newPointBlocksBelow = pointBlocksBelow[boxToBeWeightedIndex][1:]
							tillFall = math.ceil((min(newPointBlocksBelow)-splitsUntilFall[boxToBeWeightedIndex])/2)
							
							#weight the same way as above, but using the new number of splits until fall
							if 2 < tillFall < 13:
								weightToAdd = c*splitsUntilFall[boxToBeWeightedIndex]**2+b*splitsUntilFall[boxToBeWeightedIndex]+a
							else:
								weightToAdd = 0
							
							if weightverbose:
								print("This block will fall in "+str(splitsUntilFall[boxToBeWeightedIndex])+" splits, so there's no chance we make a point block before this.")
								print("Entire list of point blocks beneath, minus the lowest:")
								print(newPointBlocksBelow)
								print("New splits until falling: "+str(tillFall))
								print("Using this number of splitsUntilFall, we add "+str(weightToAdd)+" weight.")	
				
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
			if len(pointBlocksBelow[boxToBeWeightedIndex]) != 0 and curr_splits > 800:
				curr_highest_split_pct = (curr_splits-pointBlocksBelow[boxToBeWeightedIndex][-1])/curr_splits
				weightToAdd = 9*curr_highest_split_pct
				weight += weightToAdd

				if weightverbose:
					print("~~~Finding weight from highest point block beneath:~~~")
					print("Highest point block below is {} ({} pct of splits), so adding {} weight"\
						.format(pointBlocksBelow[boxToBeWeightedIndex][-1],curr_highest_split_pct,weightToAdd))
					print("Total weight is now {}".format(weight))
				

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

if __name__ == '__main__':
	gb = core.Board()
	core.makeMove(gb,0)
	core.makeMove(gb,0)
	core.makeMove(gb,0)
	core.makeMove(gb,0)
	core.makeMove(gb,1)
	findCluster(gb)