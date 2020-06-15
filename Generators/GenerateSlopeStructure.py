import RNG
import logging
import utilityFunctions as utilityFunctions
from enum import Enum

MINIMUM_ROLLER_COASTER_LENGTH = 20
MAX_SAME_HEIGHT_RAIL_LENGTH = 5
MAX_INCREASING_LENGTH_TRIES = 6

max_rail_length = 0

## IMPROVEMENTS IDEAS :
## - being able to put multiple rails on the same (x, z) (for example when the rails are going down a mine)
## -

def generateSlopeStructure(matrix, wood_material, height_map, h_max, x_min, x_max, z_min, z_max, allowStraightRails = False):
    logging.info("Trying to generate roller coaster")

    cleanProperty(matrix, height_map, h_max, x_min, x_max, z_min, z_max)
    #spawnFlowers(matrix, height_map, x_min, x_max, z_min, z_max)

    ## Generates the roller coaster
    wooden_materials_kit = utilityFunctions.wood_IDs[wood_material]
    return_value = generateRollerCoaster(matrix, wooden_materials_kit, height_map, h_max, x_min, x_max, z_min, z_max, allowStraightRails)
    if return_value == 0:
        return 0
    slope = utilityFunctions.dotdict()
    slope.type = "rollerCoaster"
    slope.lotArea = utilityFunctions.dotdict({"y_min": 0, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
    slope.buildArea = utilityFunctions.dotdict({"y_min": 0, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
    slope.orientation = getOrientation()
    slope.entranceLot = (height_map[x_min][z_min], slope.lotArea.x_min, slope.lotArea.z_min)
    return slope

def spawnFlowers(matrix, height_map, x_min, x_max, z_min, z_max):
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            matrix.setValue(height_map[x][z], x, z, utilityFunctions.getBlockID("grass"))
            matrix.setValue(height_map[x][z] + 1, x, z, (utilityFunctions.getBlockID("flower"), RNG.randint(0, 9)))

def generateRollerCoaster(matrix, wooden_materials_kit, height_map, h_max, x_min, x_max, z_min, z_max, allowStraightRails, allowUpdateHeightMap=True):
    global max_rail_length

    ## set rail_map to 0's
    rail_map = [[-1 for z in range(z_max + 1)] for x in range(x_max + 1)]

    HPMap = highestPointsMap(height_map, x_min, x_max, z_min, z_max)
    highestPoint = HPMap[0]

    previous_max_rail_length = 0
    for HP in HPMap:
        logging.info("Attempt to generate roller coaster with highest point : {}".format(HP))
        rollRollerRoll(matrix, height_map, rail_map, 0, 0, MAX_SAME_HEIGHT_RAIL_LENGTH, x_min + 1, x_max - 1, z_min + 1, z_max - 1, HP[0], HP[1], 0)
        if previous_max_rail_length < max_rail_length:
            previous_max_rail_length = max_rail_length
            highestPoint = HP

    #logging.info("Final highest point : {}".format(highestPoint))

    ## cancel the run if the roller coaster is not long enough
    if max_rail_length < MINIMUM_ROLLER_COASTER_LENGTH:
        logging.info("Roller coaster is too short with length : {}, cancelling generation".format(max_rail_length))
        return 0

    ## first run
    rail_map = cleanRailMap(rail_map, x_max, z_max)
    railIndex = rollRollerRoll(matrix, height_map, rail_map, 0, 0, MAX_SAME_HEIGHT_RAIL_LENGTH, x_min + 1, x_max - 1, z_min + 1, z_max - 1, highestPoint[0], highestPoint[1], 1)

    ## second run
    for length in range(MAX_SAME_HEIGHT_RAIL_LENGTH, MAX_SAME_HEIGHT_RAIL_LENGTH + MAX_INCREASING_LENGTH_TRIES):
        logging.info("Try to connect rails with max same level length : {}".format(length))
        rail_map = cleanRailMap(rail_map, x_max, z_max, railIndex)
        return_value = rollRollerRoll(matrix, height_map, rail_map, 0, 0, length, x_min, x_max, z_min, z_max, highestPoint[0], highestPoint[1], 2, railIndex)
        if return_value != 0:
            break
    if not allowStraightRails and return_value == 0: # did not find a connecting path
        return 0

    ## reinitialize the starting point in the rail map
    rail_map[highestPoint[0]][highestPoint[1]] = railIndex - 1

    ## generate the rails
    generateRails(matrix, wooden_materials_kit, height_map, rail_map, x_min, x_max, z_min, z_max, highestPoint)
    generateChest(matrix, wooden_materials_kit, height_map, rail_map, highestPoint[0], highestPoint[1], x_min, x_max, z_min, z_max)

    ## reinitialize global variable
    max_rail_length = 0

    # set rail blocks in height_map to -1
    if allowUpdateHeightMap:
        updateHeightMap(height_map, rail_map, x_max, z_max)
    return 1

def updateHeightMap(height_map, rail_map, x_max, z_max):
    for x in range(x_max + 1):
        for z in range(z_max + 1):
            if rail_map[x][z] > 1:
                height_map[x][z] = -1

def cleanRailMap(rail_map, x_max, z_max, eraseFrom = 1):
    for x in range(x_max + 1):
        for z in range(z_max + 1):
            if rail_map[x][z] == 1 or rail_map[x][z] >= eraseFrom:
                rail_map[x][z] = -1
    return rail_map

def generateRails(matrix, wooden_materials_kit, height_map, rail_map, x_min, x_max, z_min, z_max, highestPoint):
    for x in range(x_min, x_max + 1):
        for z in range(z_min, z_max + 1):
            if rail_map[x][z] >= 2:
                #print("x:{} z:{} is {} with max rail length {}".format(x, z, rail_map[x][z], max_rail_length))
                ## check rail orientation using neighbouring rails
                binary_orientation_index = getRailOrientation(height_map, rail_map, x, z, x_max, z_max, max_rail_length)

                ## set rail orientation
                rail_orientation = getOrientationFromBinaryIndex(binary_orientation_index)

                ## generate the rail
                #logging.info("Generating a rail (index:{}) in x:{}, z:{}, y:{} with orientation:{}".format(rail_map[x][z], x, z, height_map[x][z], rail_orientation))
                matrix.setValue(height_map[x][z], x, z, wooden_materials_kit["log"])

                ## regular rail
                if binary_orientation_index < 16:
                    matrix.setValue(height_map[x][z] + 1, x, z, utilityFunctions.getBlockID("rail", rail_orientation))
                ## powered rail
                else:
                    matrix.setValue(height_map[x][z] + 1, x, z, utilityFunctions.getBlockID("golden_rail", rail_orientation))
                    matrix.setEntity(height_map[x][z] - 1, x, z, utilityFunctions.getBlockID("redstone_torch"), "redstone_torch")


def isOneOrLessDifferencial(n1, n2, end_value):
    if n1 < 2 or n2 < 2:
        return False
    if ((n1 == n2 + 1 or n1 == n2 - 1)
            or (n1 == 2 and n2 == end_value)
            or (n2 == 2 and n1 == end_value)):
        #print("n1 {} n2 {}".format(n1, n2))
        return True
    return False

def getRailOrientation(height_map, rail_map, x, z, x_max, z_max, end_value):
    binary_orientation_index = 0
    if isInBounds(x + 1, z, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x + 1][z], end_value):
        binary_orientation_index = 16 if height_map[x][z] + 1 == height_map[x + 1][z] else binary_orientation_index + 1
    if binary_orientation_index < 16 and isInBounds(x, z + 1, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x][z + 1], end_value):
        binary_orientation_index = 17 if height_map[x][z] + 1 == height_map[x][z + 1] else binary_orientation_index + 2
    if binary_orientation_index < 16 and isInBounds(x - 1, z, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x - 1][z], end_value):
        binary_orientation_index = 18 if height_map[x][z] + 1 == height_map[x - 1][z] else binary_orientation_index + 4
    if binary_orientation_index < 16 and isInBounds(x, z - 1, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x][z - 1], end_value):
        binary_orientation_index = 19 if height_map[x][z] + 1 == height_map[x][z - 1] else binary_orientation_index + 8
    return binary_orientation_index

def getOrientationFromBinaryIndex(binary_orientation_index):
    orientations = {
        0: utilityFunctions.Orientation.HORIZONTAL.value,
        1: utilityFunctions.Orientation.HORIZONTAL.value,
        2: utilityFunctions.Orientation.VERTICAL.value,
        3: utilityFunctions.Orientation.NORTH_EAST.value,
        4: utilityFunctions.Orientation.HORIZONTAL.value,
        5: utilityFunctions.Orientation.HORIZONTAL.value,
        6: utilityFunctions.Orientation.SOUTH_EAST.value,
        7: utilityFunctions.Orientation.HORIZONTAL.value, # should never happen
        8: utilityFunctions.Orientation.VERTICAL.value,
        9: utilityFunctions.Orientation.NORTH_WEST.value,
        10: utilityFunctions.Orientation.VERTICAL.value,
        11: utilityFunctions.Orientation.VERTICAL.value, # should never happen
        12: utilityFunctions.Orientation.SOUTH_WEST.value,
        13: utilityFunctions.Orientation.HORIZONTAL.value, # should never happen
        14: utilityFunctions.Orientation.VERTICAL.value, # should never happen
        15: utilityFunctions.Orientation.NORTH_EAST.value, # should never happen
        16: utilityFunctions.Orientation.NORTH.value,
        17: utilityFunctions.Orientation.EAST.value,
        18: utilityFunctions.Orientation.SOUTH.value,
        19: utilityFunctions.Orientation.WEST.value
    }

    return orientations[binary_orientation_index] - 1

def spawnChest(matrix, wooden_materials_kit, h, x, z, socle = "False"):
    ## generate oak log under chest
    if socle == True: matrix.setValue(h - 1, x, z, wooden_materials_kit["log"])
    ## generate the chest
    matrix.setEntity(h, x, z, utilityFunctions.getBlockID("chest", 2), "chest")

def generateChest(matrix, wooden_materials_kit, height_map, rail_map, x, z, x_min, x_max, z_min, z_max):
    ## check every neighbouring block
    for i in range(x - 1, x + 2):
        for j in range(z - 1, z + 2):
            if isInBounds(i, j, 0, x_max, 0, z_max) and rail_map[i][j] < 2:
                spawnChest(matrix, wooden_materials_kit, height_map[i][j] + 1, i, j, True)
                return
    ## floating chest if no free block
    spawnChest(matrix, wooden_materials_kit, height_map[x][z] + 3, x, z)

## Recursive function
## @parameter: generatorIndex is 0 for initial run, 1 for final first path, 2 for second run, 3 for final second path
def rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, generatorIndex, railIndex=2, previous_x=-1, previous_z=-1):
    y = height_map[x][z]
    rail_map[x][z] = 1
    rail_length += 1
    current_height_rail_length += 1

    ## Two straigth rails if it is going down
    return_value = 0
    if isNotSameLevel(height_map, x, z, previous_x, previous_z):
        current_height_rail_length = 0
        next_x = x if previous_x == x else x + (x - previous_x)
        next_z = z if previous_z == z else z + (z - previous_z)
        if canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, next_x, next_z):
            return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, next_x, next_z, generatorIndex, railIndex, x, z)
    ## Random direction otherwise
    else:
        return_value = choseRandomDirection(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, generatorIndex, railIndex, previous_x, previous_z)
    if return_value >= 1:
        rail_map[x][z] = return_value
        if generatorIndex == 1:
            return_value += 1
        else:
            return_value -= 1
    return return_value

def choseRandomDirection(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, generatorIndex, railIndex, previous_x, previous_z):
    global max_rail_length
    return_value = 0
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x - 1, z):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x - 1, z, generatorIndex, railIndex, x, z)
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x, z - 1):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z - 1, generatorIndex, railIndex, x, z)
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x + 1, z):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x + 1, z, generatorIndex, railIndex, x, z)
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x, z + 1):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z + 1, generatorIndex, railIndex, x, z)
    #logging.info("current rail length : {}".format(rail_length))
    if isSameLevel(height_map, x, z, previous_x, previous_z):
        if generatorIndex == 0:
            if rail_length > max_rail_length:
                max_rail_length = rail_length
        elif generatorIndex == 1:
            if rail_length == max_rail_length:
                return_value = railIndex
    if generatorIndex == 2:
        if (hasReachedEnd(height_map, rail_map, x, z, x_min, x_max, z_min, z_max, previous_x, previous_z)):
            if max_rail_length < railIndex + rail_length - 2:
                max_rail_length = railIndex + rail_length - 2
            return_value = railIndex + rail_length - 2
    return return_value

def isNotSameLevel(height_map, x, z, previous_x, previous_z):
    return previous_x != -1 and previous_z != -1 and height_map[previous_x][previous_z] != height_map[x][z]

def isSameLevel(height_map, x, z, previous_x, previous_z):
    return previous_x != -1 and previous_z != -1 and height_map[previous_x][previous_z] == height_map[x][z]

def hasReachedEnd(height_map, rail_map, x, z, x_min, x_max, z_min, z_max, previous_x, previous_z):
    #logging.info("Trying to find ending point at coordinates: x:{}, z:{} with x_min:{}, x_max:{}, z_min:{}, z_max:{}".format(x, z, x_min, x_max, z_min, z_max))
    return ((isInBounds(x + 1, z, x_min, x_max, z_min, z_max) and rail_map[x + 1][z] == 2 and height_map[x][z] == height_map[x + 1][z])
            or (isInBounds(x, z + 1, x_min, x_max, z_min, z_max) and rail_map[x][z + 1] == 2 and height_map[x][z] == height_map[x][z + 1])
            or (isInBounds(x - 1, z, x_min, x_max, z_min, z_max) and rail_map[x - 1][z] == 2 and height_map[x][z] == height_map[x - 1][z])
            or (isInBounds(x, z - 1, x_min, x_max, z_min, z_max) and rail_map[x][z - 1] == 2 and height_map[x][z] == height_map[x][z - 1]))

def canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x1, z1, x2, z2):
    return (not areRailsTooLongForThisHeight(current_height_rail_length, max_height_rail_length, x1, z1)
            and isInBounds(x2, z2, x_min, x_max, z_min, z_max)
            and isNextBlockSameHeightOrOneLower(height_map, x1, z1, x2, z2)
            and not isAlreadyRail(matrix, height_map, rail_map, x2, z2))

def areRailsTooLongForThisHeight(current_height_rail_length, max_height_rail_length, x, z):
    return current_height_rail_length >= max_height_rail_length

def isInBounds(x, z, x_min, x_max, z_min, z_max):
    return (x >= x_min and x <= x_max and z >= z_min and z <= z_max)

def isNextBlockSameHeightOrOneLower(height_map, x1, z1, x2, z2):
    score = height_map[x1][z1] - height_map[x2][z2]
    return score == 0 or score == 1

def isAlreadyRail(matrix, height_map, rail_map, x, z):
    return rail_map[x][z] >= 1

def cleanProperty(matrix, height_map, h_max, x_min, x_max, z_min, z_max):
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            for y in range(height_map[x][z] + 1, h_max):
                matrix.setValue(y, x, z, utilityFunctions.getBlockID("air"))

def highestPointsMap(height_map, x_min, x_max, z_min, z_max):
    highestPoint = utilityFunctions.getHighestPoint(height_map, x_min, x_max, z_min, z_max)
    h_max = height_map[highestPoint[0]][highestPoint[1]]

    map = []
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            if height_map[x][z] == h_max:
                map.append((x, z))
    return map

def getOrientation():
	return "S"
