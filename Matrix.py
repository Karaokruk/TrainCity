class Matrix:

	min_x = max_x = min_y = max_y = min_z = max_z = -1
	width = height = depth = -1
	matrix = None

	def __init__(self, level, box, height, width, depth):
		self.level = level
		self.width = width
		self.height = height
		self.depth = depth
		self.y_min = box.miny
		self.y_max = box.maxy
		self.x_min = box.minx
		self.x_max = box.maxx
		self.z_min = box.minz
		self.z_max = box.maxz
		self.matrix = [[[None for z in range(depth)] for x in range(width)] for y in range(height)]
		self.changed = [[[False for z in range(depth)] for x in range(width)] for y in range(height)]

	def getValue(self, y,x,z):
		if self.changed[y][x][z] == True:
			return self.matrix[y][x][z]
		else:
			return self.level.blockAt(x,y,z)

	def setValue(self, y,x,z, value):
		self.matrix[y][x][z] = value
		self.changed[y][x][z] = True

	def isChanged(self, y,x,z):
		return self.changed[y][x][z]

	def getWorldX(self, x):
		for world_x, matrix_x in zip(range(self.x_min,self.x_max), range(0,self.width)):
			if matrix_x == x:
				return world_x

	def getWorldZ(self, z):
		for world_z, matrix_z in zip(range(self.z_min,self.z_max), range(0,self.depth)):
			if matrix_z == z:
				return world_z

	def getWorldY(self, y):
		for world_y, matrix_y in zip(range(self.y_min,self.y_max), range(0,self.height)):
			if matrix_y == y:
				return world_y

	def getMatrixX(self, x):
		for world_x, matrix_x in zip(range(self.x_min,self.x_max), range(0, self.width)):
			if world_x == x:
				return matrix_x

	def getMatrixZ(self, z):
		for world_z, matrix_z in zip(range(self.z_min,self.z_max), range(0, self.depth)):
			if world_z == z:
				return matrix_z

	def getMatrixY(self, y):
		for world_y, matrix_y in zip(range(self.y_min,self.y_max), range(0, self.height)):
			if world_y == y:
				return matrix_y

	def updateWorld(self):
		for y, h in zip(range(self.y_min,self.y_max), range(0, self.height)):
			for x, w in zip(range(self.x_min,self.x_max), range(0, self.width)):
				for z, d in zip(range(self.z_min,self.z_max), range(0,self.depth)):
					if self.isChanged(h,w,d):
						block = self.getValue(h,w,d)
						if type(block) == tuple:
							#setBlock(level, (block[0], block[1]), x, y, z)
							self.level.setBlockAt((int)(x),(int)(y),(int)(z), block[0])
							self.level.setBlockDataAt((int)(x),(int)(y),(int)(z), block[1])
						else:
							self.level.setBlockAt((int)(x),(int)(y),(int)(z), block)
							#setBlock(level, (block, 0), x, y, z)
						