# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *

import random

SEED = random.random()
NORTH = (0, -1)
EAST = (1, 0)
SOUTH = (0, 1)
WEST = (-1, 0)
WIDTH = 80
HEIGHT = 60
GRIDSIZE = 16
SCALEDPOPULATION = WIDTH * HEIGHT / 200
SCALEDFOOD = WIDTH * HEIGHT / 10
global USE_GRAPHICS
USE_GRAPHICS = True
CREATURE_PIC = [QImage('jpac.png').transformed(QTransform().rotate(a)) for a in xrange(0,360,90)]
FOOD_PIC = QImage('food16.png')
CORPSE_PIC = QImage('pacdead.png')

WALL_PIC = QImage('wall.png')

DEEP_WATER_PIC = QImage('deep_water.png')
WATER_PIC = QImage('water.png')
COAST_PIC = QImage('coast.png')
GRASS_PIC = QImage('grass.png')
FOREST_PIC = QImage('forest.png')
HILL_PIC = QImage('hill.png')
MOUNTAIN_PIC = QImage('mountain.png')



MUTATE = 10 #chance of mutation in ‰
CROSSOVERRATE = 70 #chance of crossover in %

TERRAINTYPES = {
    #format: 
    #'type' : (ID, (red, green, blue))
    'wall': (0, (0, 0, 0)),
    'deep_water': (1, (0, 0, 105)),
    'water': (2, (0, 0, 255)),
    'coast': (3, (255, 255, 0)),
    'grass': (4, (0, 255, 0)),
    'forest': (5, (0, 105, 0)),
    'hill': (6, (135, 65, 15)),
    'mountain': (7, (150, 150, 150)),
    
    
    
 }

TERRAINTYPEIMAGE = {
    'wall': WALL_PIC,
    'deep_water': DEEP_WATER_PIC,
    'water': WATER_PIC,
    'coast': COAST_PIC,
    'grass': GRASS_PIC,
    'forest': FOREST_PIC,
    'hill': HILL_PIC,
    'mountain': MOUNTAIN_PIC
}


IDINDEX = 0
RGBINDEX = 1
GAMEOFLIFE=False


def getAssociatedRGB(terrainKey="", terrainID=-1):
    """
    Arguments:
    - `terrainKey`: String that defines terrain type
    - `terrainID`: ID that defines terrain type
    - NOTE: giving both arguments causes error

    Returns:
    RGB-color as tuple

    Example:
    rgb = globals.getAssociatedRGB(terrainKey="grass")
    print rgb
    Output:
    (0, 255, 0)
    """

    if terrainKey != "" and terrainID == -1:
        return TERRAINTYPES['terrainKey'][RGBINDEX]

    elif terrainKey == "" and terrainID != -1:
        for terrainType in TERRAINTYPES.values():
            if terrainType[IDINDEX] == terrainID:
                return terrainType[RGBINDEX]
            
def getAssociatedID(rgb=None, key=None):
    """
    Arguments:
    - `rgb`: rgb-value to lookup 

    Returns:
    ID associated with given rgb-value

    Example:
    id = globals.getAssociatedID((0, 0, 0))
    print id
    Output: 0
    """
    if key is None:
        for terrainType in TERRAINTYPES.values():
            if terrainType[RGBINDEX] == rgb:
                return terrainType[IDINDEX]
    elif key is not None:
        return TERRAINTYPES[key][IDINDEX]

def getAssociatedKey(rgb=None, ID=None):
    """
    Arguments:
    - `rgb`: rgb-value to lookup
    - `ID`: ID to lookup 

    Returns:
    key associated with given rgb-value

    Example:
    key = globals.getAssociatedKey((0, 0, 0))
    print key
    Output: "wall"
    
    """
    for key, value in TERRAINTYPES.items():
        if value[RGBINDEX] == rgb:
            return key
        elif value[IDINDEX] == ID:
            return key

    
