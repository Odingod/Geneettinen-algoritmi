# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *

NORTH = (0, -1)
EAST = (1, 0)
SOUTH = (0, 1)
WEST = (-1, 0)
WIDTH = 40
HEIGHT = 40
GRIDSIZE = 16
global USE_GRAPHICS
USE_GRAPHICS = True
CREATURE_PIC = [QImage('jpac.png').transformed(QTransform().rotate(a)) for a in xrange(0,360,90)]
FOOD_PIC = QImage('food16.png')
CORPSE_PIC = QImage('pacdead.png')
MUTATE = 10 #chance of mutation in ‰
TERRAINTYPES = {
    #format: 
    #'type' : (ID, (red, green, blue))
    'wall' : (0, (0, 0, 0)),
    'grass' : (1, (0, 255, 0)),
    'water' : (2, (0, 0, 255))

 }


IDINDEX = 0
RGBINDEX = 1

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
            
def getAssociatedID(rgb):
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
    for terrainType in TERRAINTYPES.values():
        if terrainType[RGBINDEX] == rgb:
            return terrainType[IDINDEX]

def getAssociatedKey(rgb):
    """
    Arguments:
    - `rgb`: rgb-value to lookup 

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
