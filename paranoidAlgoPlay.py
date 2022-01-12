"""
Algorithm used to get a sequence of 1053 splits! In short, saves a list of times
the algorithm chose to make a large group of point blocks, and if it loses, goes
back to the last time it made such a choice and makes the next best decision. 
Can also track times the algorithm made a very choice between options that were
very close in weight.

Takes no command line arguments. Instead, edit the continuation/piggyback flags based
on desired behavior, and edit the filenames to save/read data from.
"""
import sys 
from weighting import findWeights
from core_update import getScreenString
from core_update import HORIZONTAL
import core_update as core
import copy
import pickle
import heapq
from algorithm_play import playUntilEnd

if __name__ == "__main__":
	log_name = "sequences/logParanoid1_final.txt"

	#when continuation=True, picks up from where a previous sim left off
	continuation = False

	#when piggyback=True, the first run will follow the provided sequence,
	#allowing you to explore a promising sequence more deeply with the paranoid algorithm
	piggyback = False

	continuation_name = "sequences/paranoid_final_continuation.pkl"
	if continuation:
		with open(continuation_name,'rb') as f:
			cont_data = pickle.load(f)
			big_cluster_boards = cont_data[0]
			big_cluster_weights = cont_data[1]
			best_sequence_len = cont_data[2]
			exploring_from = cont_data[3] #splits
			restart_splits = cont_data[4]
			game_num = cont_data[5]

			#grab board and edited weights from last run
			game_board = big_cluster_boards.pop()
			game_board.weights = big_cluster_weights.pop()
	else:
		big_cluster_boards = []
		big_cluster_weights = []
		best_sequence_len = 0
		exploring_from = 2000 #splits
		restart_splits = 0
		#clear log
		log_file = open(log_name,'w')
		log_file.close()

		game_board = core.Board()
		game_num = 0

	#If you want to explore from an already existing sequence:
	if piggyback:
		sequenceFile = "sequences/1030wpotential.txt" #provide sequence here
		try:
			f = open(sequenceFile, "r")
		except:
			print("Couldn't open file",sequenceFile,", does it exist?")
			sys.exit(1)

		line=f.readline()
		f.close()
		if line[0] == "[": line = line[1:]
		if line[-1] == "]": line = line[:-1]
		piggyback_sequence=(line.rstrip('\n').split(', '))
		piggyback_sequence=[int(ii) for ii in piggyback_sequence]

	almost_as_good_tracker = 0

	while 1:
		moveOptions = game_board.getMoveOptions()

		if len(moveOptions) == 0:
			game_num += 1
			#Every 100 games, update the saved version of your continuation list
			if game_num % 100 == 0:
				with open(continuation_name,'wb') as cf:
					pickle.dump([big_cluster_boards,big_cluster_weights,best_sequence_len,exploring_from,restart_splits,game_num],cf)

			with open(log_name,'a') as lf:
				lf.write("\tLost at {} splits (base state = {})\n".format(len(game_board.splitRecord),exploring_from))
				#If this is a new record, record that
				if len(game_board.splitRecord) > best_sequence_len:
					print("---------------New Record! {} Splits ({} games)---------------".format(len(game_board.splitRecord),game_num))
					best_sequence_len = len(game_board.splitRecord)
					lf.write("~~New Record! {} Splits (after {} games)~~\n".format(best_sequence_len,game_num))
					lf.write("{}\n".format(game_board.splitRecord))
					print('\007',end='\r') #play boop

				#pop off last gameboard which caused a big cluster, restart from here
				if len(big_cluster_boards) > 0:
					game_board = big_cluster_boards.pop()
					game_board.weights = big_cluster_weights.pop()
					lf.write("\t\tRestarting at {} splits\n".format(len(game_board.splitRecord)))
					restart_splits = len(game_board.splitRecord)
				else:
					lf.write("Exhausted all options - no more big clusters to remove. Highest splits reached was {}".format(len(game_board.splitRecord)))
					print('\007',end='\r') #play boop

				#If this is the lowest split board we are expanding, log this:
				if len(game_board.splitRecord) < exploring_from:
					exploring_from = len(game_board.splitRecord)
					print("~~Exploring from new base state - {} splits~~".format(exploring_from))
					lf.write("Exploring from new base state - {} splits. Board:\n".format(exploring_from))
					lf.write(getScreenString(game_board))
					lf.write("Sequence:\n{}\n".format(game_board.splitRecord))
					print('\007',end='\r') #play boop

		#remove double weights for tractability
		seen_weights = set()
		for i,weight in enumerate(list(game_board.weights)):
			if weight not in seen_weights:
				seen_weights.add(weight)
			else:
				game_board.weights[i] = 0

		#grabs top two weighted splits
		high_weight_indices = heapq.nlargest(2,range(len(game_board.weights)), key=game_board.weights.__getitem__)
		best_split_ind = high_weight_indices[0]
		#only check weight difference if theres more than one weight (only matters on turn 1)
		if len(high_weight_indices) > 1:
			second_best_split_ind = high_weight_indices[1]
			weight_diff = game_board.weights[high_weight_indices[0]]-game_board.weights[high_weight_indices[1]]
		else: weight_diff = 100

		if piggyback and game_num == 0: #if piggybacking, select moves from sequence at first
			best_split_ind = piggyback_sequence[len(game_board.splitRecord)]

		print("Game {}, Split {} - (restart {}, base {})".format(game_num,len(game_board.splitRecord),restart_splits,exploring_from), end='\r')

		old_game_board = copy.deepcopy(game_board)

		core.makeMove(game_board,best_split_ind)

		#After making the move, if the most recent block has points and
		#is not 1x1, then it made an unecessarily big cluster and we should add it
		#OR if there was another split option within 3 weight but not identical
		most_recent_box = game_board.box[-1]

		split_created_big_cluster = ((most_recent_box.points != 0) and (most_recent_box.width != 1 or most_recent_box.height != 1))
		another_as_good_option = ((weight_diff < 3) and (weight_diff > 1) and len(game_board.splitRecord)>875)
		
		#don't add all almost as good options because the problem becoms intractible
		add_every_blank_good_options = 2
		if another_as_good_option:
			almost_as_good_tracker = (another_as_good_option+1) % add_every_blank_good_options
			if almost_as_good_tracker != 0:
				another_as_good_option = False
		# another_as_good_option = False #uncomment if you don't want to explore similarly weighted stuff

		if split_created_big_cluster or another_as_good_option:
			old_weights = list(old_game_board.weights)

			#only add it as an option to take differently if its not the only move
			weights_without_max = list(old_weights)
			weights_without_max.pop(best_split_ind) #remove the max weight split
			if max(weights_without_max) != 0:
				old_weights[second_best_split_ind] = old_weights[best_split_ind]
				old_weights[best_split_ind] = 0 #change weight of previously chosen split to zero to prevent it from being chosen again

				big_cluster_boards.append(old_game_board)
				big_cluster_weights.append(old_weights)