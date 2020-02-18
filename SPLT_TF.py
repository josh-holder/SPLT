from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
from tensorflow import keras
import numpy as np
import core

####Implement the architecture for a deep learning approach to SPL-T:
def get_input(gameBoard):
	"""
	Given a gameboard, returns 48x8 array. This is comprised of:
	16x8 array of integers representing the width of the box that exists in that location
	16x8 array of integers representing the height of the box that exists in that location
	16x8 array of integers representing the amount of points that exists in that location (-1 for void)
	"""
	width_array = np.ones((16,8),dtype=int)
	height_array = np.ones((16,8),dtype=int)
	point_array = -1*np.zeros((16,8),dtype=int)
	for box in gameBoard.box:
		#iterates over area of box
		for col in range(box.x,box.x+box.width):
			for row in range(box.y,box.y+box.height):
				width_array[row,col] = box.width
				height_array[row,col] = box.height
				point_array[row,col] = box.points

	input_array = np.concatenate((width_array,height_array,point_array))

	return input_array

if __name__ == "__main__":
	gameBoard = core.Board()
	array = get_input(gameBoard)