import core_update as core_weight
import time

def TimeCalc():

	i = 0
	num_games = 100

	total_pre_move_time = 0
	total_move_time = 0
	total_cluster_time = 0
	total_weight_time = 0

	while i < num_games:
		splits = 0
		game_pre_move_time = 0
		game_move_time = 0
		game_cluster_time = 0
		game_weight_time = 0

		gameBoard = core_weight.Board()
		while 1:
			start = time.time()
		
			moveOptions = gameBoard.getMoveOptions()

			if len(moveOptions) == 0:
				break
			
			bestSplit = max(range(len(gameBoard.weights)), key=gameBoard.weights.__getitem__)

			end = time.time()
			game_pre_move_time += end-start

			move_time, cluster_time, weight_time = core_weight.makeMove(gameBoard,bestSplit)
			game_move_time += move_time
			game_cluster_time += cluster_time
			game_weight_time += weight_time

			splits += 1

		total_pre_move_time += game_pre_move_time/splits
		total_move_time += game_move_time/splits
		total_cluster_time += game_cluster_time/splits
		total_weight_time += game_weight_time/splits

		print('Game ' + str(i),end = '\r')
		i += 1
	
	total_pre_move_time = total_pre_move_time/num_games
	total_move_time = total_move_time/num_games
	total_cluster_time = total_cluster_time/num_games
	total_weight_time = total_weight_time/num_games
	
	print('Average time to execute weight selection/get move options = '+str(total_pre_move_time))
	print('Average time to execute move = '+str(total_move_time))
	print('Average time to calculate clusters = '+str(total_cluster_time))
	print('Average time to calculate weights = '+str(total_weight_time))

if __name__ == "__main__":
	TimeCalc()