from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
from tensorflow import keras
import numpy as np
import core

####Implement the architecture for a deep learning approach to SPL-T:
def get_gs(gameBoard):
	"""
	Given a gameboard, returns 48x8 array. This is comprised of:
	16x8 array of integers representing the width of the box with a top left corner that exists in that location
	16x8 array of integers representing the height of the box with a top left corner that exists in that location
	16x8 array of integers representing the amount of points that exists with a top left corner in that location
	"""

	width_array = np.zeros((16,8),dtype=int)
	height_array = np.zeros((16,8),dtype=int)
	point_array = np.zeros((16,8),dtype=int)
	
	for box in gameBoard.box:
		width_array[box.y,box.x] = box.width
		height_array[box.y,box.x] = box.height
		point_array[box.y,box.x] = box.points

	input_array = np.concatenate((width_array,height_array,point_array))

	return input_array



def build_nn(input_array):
	"""
	Builds neural network
	"""
	model = keras.Sequential([
		keras.layers.Flatten(input_shape(48,8)),
		keras.layers.Dense(128,activation='relu'),
		keras.layers.Dense(128,activation='relu'),
		keras.layers.Dense(10)
	])

if __name__ == "__main__":
	gameBoard = core.Board()
	core.makeMove(gameBoard,0)
	core.makeMove(gameBoard,0)
	array = get_gs(gameBoard)
	print(array)