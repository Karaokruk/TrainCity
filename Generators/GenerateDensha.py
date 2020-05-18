import logging
import utilityFunctions as utilityFunctions

HEIGHT_FROM_GROUND = 10
SMOOTHING_RANGE = 10

def generateDensha(matrix, wood_material, simple_height_map, h_max, x_min, x_max, z_min, z_max):
	logging.info("Generating densha")
	print("{}, {}, {}, {}".format(x_min, x_max, z_min, z_max))

	## Create densha height map
	densha_height_map = createDenshaHeighMap(simple_height_map, h_max, x_min, x_max, z_min, z_max)

	#generateRails(matrix, simple_height_map, x_min, x_max, z_min, z_max)
	generateRails(matrix, densha_height_map, x_min, x_max, z_min, z_max)

def isOneOrLessDifferencial(x, y):
	return ((x - y == 0) or (x - y == 1) or (x - y == -1))

def isDenshaHeightMapContinuous(densha_height_map, x_min, x_max, z_min, z_max):
	logging.info("Smoothing the rails network")
	print("Smoothing the rails network")
	for x in range(x_min + 1 + SMOOTHING_RANGE // 2, x_max - SMOOTHING_RANGE // 2):
		#print("x z_min {} {}".format(densha_height_map[x][z_min], densha_height_map[x + 1][z_min]))
		if not isOneOrLessDifferencial(densha_height_map[x][z_min], densha_height_map[x + 1][z_min]):
			return False
		#print("x z_max {} {}".format(densha_height_map[x][z_max], densha_height_map[x + 1][z_max]))
		if not isOneOrLessDifferencial(densha_height_map[x][z_max], densha_height_map[x + 1][z_max]):
			return False
	for z in range(z_min + 1 + SMOOTHING_RANGE // 2, z_max - SMOOTHING_RANGE // 2):
		#print("x_min z {} {}".format(densha_height_map[x_min][z], densha_height_map[x_min][z + 1]))
		if not isOneOrLessDifferencial(densha_height_map[x_min][z], densha_height_map[x_min][z + 1]):
			return False
		#print("x_max z {} {}".format(densha_height_map[x_max][z], densha_height_map[x_max][z + 1]))
		if not isOneOrLessDifferencial(densha_height_map[x_max][z], densha_height_map[x_max][z + 1]):
			return False
	return True

def movingAverageSmoothing(simple_height_map, h_max, x_min, x_max, z_min, z_max, x, z, direction):
	height_sum = 0;
	for i in range((0 - SMOOTHING_RANGE) // 2, SMOOTHING_RANGE // 2):
		if ((direction == 1 and x - x_min > SMOOTHING_RANGE // 2) or
			(direction == 1 and x_max - x > SMOOTHING_RANGE // 2) or
			(direction == 0 and z - z_min > SMOOTHING_RANGE // 2) or
			(direction == 0 and z_max - z > SMOOTHING_RANGE // 2)):
			height_sum += simple_height_map[x + i][z] if direction == 1 else simple_height_map[x][z + i]
	return height_sum // SMOOTHING_RANGE# + HEIGHT_FROM_GROUND

def createDenshaHeighMap(simple_height_map, h_max, x_min, x_max, z_min, z_max):
	densha_height_map = [row[:] for row in simple_height_map] # copy the simple height map

	while not isDenshaHeightMapContinuous(densha_height_map, x_min, x_max, z_min, z_max):
		tmp_height_map = [row[:] for row in densha_height_map]
		for x in range(x_min, x_max + 1):
			densha_height_map[x][z_min] = movingAverageSmoothing(tmp_height_map, h_max, x_min, x_max, z_min, x_max, x, z_min, 1)
			densha_height_map[x][z_max] = movingAverageSmoothing(tmp_height_map, h_max, x_min, x_max, z_min, x_max, x, z_max, 1)
		for z in range(z_min, z_max + 1):
			densha_height_map[x_min][z] = movingAverageSmoothing(tmp_height_map, h_max, x_min, x_max, z_min, x_max, x_min, z, 0)
			densha_height_map[x_max][z] = movingAverageSmoothing(tmp_height_map, h_max, x_min, x_max, z_min, x_max, x_max, z, 0)

	return densha_height_map

def generateRails(matrix, simple_height_map, x_min, x_max, z_min, z_max):

	#(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.6)
	for x in range(x_min, x_max + 1):
		if (x % 10 == 0):
			for y in range(simple_height_map[x][z_min] + 1, simple_height_map[x][z_min] + 10):
				matrix.setValue(y, x, z_min, utilityFunctions.getBlockID("stone", 6))
			for y in range(simple_height_map[x][z_max] + 1, simple_height_map[x][z_max] + 10):
				matrix.setValue(y, x, z_max, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_min] + 10, x, z_min + 1, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_max] + 10, x, z_max - 1, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_min] + 10, x, z_min, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_max] + 10, x, z_max, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_min] + 10, x, z_min - 1, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_max] + 10, x, z_max + 1, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x][z_min] + 11, x, z_min, utilityFunctions.getBlockID("rail", 1))
		matrix.setValue(simple_height_map[x][z_max] + 11, x, z_max, utilityFunctions.getBlockID("rail", 1))
	for z in range(z_min, z_max + 1):
		if (z % 10 == 0):
			for y in range(simple_height_map[x_min][z] + 1, simple_height_map[x_min][z] + 10):
				matrix.setValue(y, x_min, z, utilityFunctions.getBlockID("stone", 6))
			for y in range(simple_height_map[x_max][z] + 1, simple_height_map[x_max][z] + 10):
				matrix.setValue(y, x_max, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_min][z] + 10, x_min + 1, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_max][z] + 10, x_max - 1, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_min][z] + 10, x_min, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_max][z] + 10, x_max, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_min][z] + 10, x_min - 1, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_max][z] + 10, x_max + 1, z, utilityFunctions.getBlockID("stone", 6))
		matrix.setValue(simple_height_map[x_min][z] + 11, x_min, z, utilityFunctions.getBlockID("rail", 0))
		matrix.setValue(simple_height_map[x_max][z] + 11, x_max, z, utilityFunctions.getBlockID("rail", 0))
	matrix.setValue(simple_height_map[x_max][z_min] + 11, x_max, z_min, utilityFunctions.getBlockID("rail", 7))
	matrix.setValue(simple_height_map[x_min][z_min] + 11, x_min, z_min, utilityFunctions.getBlockID("rail", 6))
	matrix.setValue(simple_height_map[x_max][z_max] + 11, x_max, z_max, utilityFunctions.getBlockID("rail", 8))
	matrix.setValue(simple_height_map[x_min][z_max] + 11, x_min, z_max, utilityFunctions.getBlockID("rail", 9))
