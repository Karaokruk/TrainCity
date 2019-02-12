from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math

def houseGenerator(level,box,options, min_h=10, min_w=8, min_d=8):
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	matrix = utilityFunctions.generateMatrix(width,depth,height,options)

	if height < min_h or width < min_w or depth < min_d:
		return 

	h = random.randint(min_h, height)
	w = random.randint(min_w, width)
	d = random.randint(min_d, depth)

	initial_x = (width/2)-(w/2)
	initial_z = (depth/2)-(d/2)

	print("height: "+str(height)+", width: "+str(width)+", depth: "+str(depth))
	print("initial_x: "+str(initial_x)+", initial_z: "+str(initial_z))
	print("h: "+str(h)+", w: "+str(w)+", d: "+str(d))

	generateHouse(matrix, 0, h-1, initial_x, initial_x+w-1, initial_z, initial_z+d-1, options)

	for y, h in zip(range(box.miny,box.maxy), range(0,height)):
		for x, w in zip(range(box.minx,box.maxx), range(0,width)):
			for z, d in zip(range(box.minz,box.maxz), range(0,depth)):
				if matrix[h][w][d] != (0,0):
					utilityFunctions.setBlock(level, (matrix[h][w][d][0], matrix[h][w][d][1]), x, y, z)

def generateHouse(matrix, h_min, h_max, x_min, x_max, z_min, z_max, options):

	if h_max-h_min < 10 or x_max-x_min < 8 or z_max-z_min < 8:
		return 

	h_max = 15 if h_max > 15 else h_max
	
	wall = (options["Walls Material Type"].ID, random.randint(options["Walls Material Subtype (min)"],options["Walls Material Subtype (max)"]))
	ceiling = (options["Ceiling Material Type"].ID, random.randint(options["Ceiling Material Subtype (min)"],options["Ceiling Material Subtype (max)"]))
	floor = wall
	door = (0,0)

	ceiling_bottom = h_max -int((h_max-h_min) * 0.5)

	walls_pos = [x_min+1, x_max-1, z_min+1, z_max-1]

	# generate walls from x_min+1, x_max-1, etc to leave space for the roof
	generateWalls(matrix, h_min, ceiling_bottom, h_max, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], wall)
	generateFloor(matrix, h_min, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], floor)

	if random.random() > 0.5:
		generateDoor_x(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, door, door)
		generateWindow_x(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, wall)
		generateCeiling_x(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, wall, 0)
	else:
		generateDoor_z(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, door, door)
		generateWindow_z(matrix, walls_pos[0], walls_pos[1], walls_pos[2], walls_pos[3], h_min+1, ceiling_bottom, wall)
		generateCeiling_z(matrix, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, ceiling, wall, 0)

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix[h][x][z] = floor

def generateWalls(matrix, h_min, ceiling_bottom, h_max, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix[y][x][z_max] = wall
			matrix[y][x][z_min] = wall

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix[y][x_max][z] = wall
			matrix[y][x_min][z] = wall

def generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	if x_min+recr+1 <= x_max-recr-1:
		for z in range(z_min, z_max+1):					  # intended pitched roof effect
			matrix[h_min+recr][x_min+recr][z] = ceiling   #       _  
			matrix[h_min+recr][x_max-recr][z] = ceiling   #     _| |_
			matrix[h_min+recr][x_min+recr+1][z] = ceiling #   _|     |_
			matrix[h_min+recr][x_max-recr-1][z] = ceiling # _|         |_
		for x in range(x_min+recr+2, x_max-recr-1):
			matrix[h_min+recr][x][z_min+1] = wall
			matrix[h_min+recr][x][z_max-1] = wall

	if recr < h_max-h_min:
		generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
	 	old_recr = h_min+recr
	 	while x_min+recr+1 < x_max-recr-1:
	 		recr += 1
	 		for z in range (z_min, z_max+1):
	 			matrix[old_recr][x_min+recr+1][z] = ceiling
	 			matrix[old_recr][x_max-recr-1][z] = ceiling

def generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	if z_min+recr+1 <= z_max-recr-1:
		for x in range(x_min, x_max+1):
			matrix[h_min+recr][x][z_min+recr] = ceiling
			matrix[h_min+recr][x][z_max-recr] = ceiling
			matrix[h_min+recr][x][z_min+recr+1] = ceiling
			matrix[h_min+recr][x][z_max-recr-1] = ceiling
		for z in range(z_min+recr+2, z_max-recr-1):
			matrix[h_min+recr][x_min+1][z] = wall
			matrix[h_min+recr][x_max-1][z] = wall

	if recr < h_max-h_min:
		generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
		old_recr = h_min+recr
		while  z_min+recr+1 < z_max-recr-1:
			recr += 1
			for x in range (x_min, x_max+1):
				matrix[old_recr][x][z_min+recr+1] = ceiling
				matrix[old_recr][x][z_max-recr-1] = ceiling

def generateDoor_x(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	pos = random.randint(x_min+1,x_max-1)
	chance = random.random()
	if chance < 0.50:
		matrix[h_min+1][pos][z_min] = (64,8)
		matrix[h_min][pos][z_min] = (64,1)
	else:
		matrix[h_min+1][pos][z_max] = (64,8)
		matrix[h_min][pos][z_max] = (64,3)

def generateDoor_z(matrix, x_min, x_max, z_min, z_max, h_min, h_max, door_up, door_down):

	pos = random.randint(z_min+1,z_max-1)
	chance = random.random()
	if chance < 0.50:
		matrix[h_min+1][x_min][pos] = (64,9)
		matrix[h_min][x_min][pos] = (64,0)
	else:
		matrix[h_min+1][x_max][pos] = (64,9)
		matrix[h_min][x_max][pos] = (64,2)

def generateWindow_x(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

	window_height = h_max - int((h_max - h_min)/1.5)
	whmin = h_max - int((h_max - h_min)/1.5)
	whmax = h_max - int((h_max - h_min)/2.5)

	width = z_max - z_min
	pos_min = random.randint(z_min+int(width*0.1),z_min+int(width*0.4))
	pos_max = random.randint(z_min+int(width*0.6),z_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][x_min][p] = (20,0)

	width = z_max - z_min
	pos_min = random.randint(z_min+int(width*0.1),z_min+int(width*0.4))
	pos_max = random.randint(z_min+int(width*0.6),z_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][x_max][p] = (20,0)

def generateWindow_z(matrix, x_min, x_max, z_min, z_max, h_min, h_max, wall):

	window_height = h_max - int((h_max - h_min)/1.5)
	whmin = h_max - int((h_max - h_min)/1.5)
	whmax = h_max - int((h_max - h_min)/2.5)

	width = x_max - x_min
	pos_min = random.randint(x_min+int(width*0.1),x_min+int(width*0.4))
	pos_max= random.randint(x_min+int(width*0.6),x_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][p][z_min] = (20,0)

	width = x_max - x_min
	pos_min = random.randint(x_min+int(width*0.1),x_min+int(width*0.4))
	pos_max= random.randint(x_min+int(width*0.6),x_min+int(width*0.9))

	for p in range(pos_min, pos_max):
		for w in range(whmin, whmax):
			matrix[w][p][z_max] = (20,0)
