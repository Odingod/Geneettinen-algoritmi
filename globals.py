# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *

NORTH=(0,-1)
EAST=(1,0)
SOUTH=(0,1)
WEST=(-1,0)
WIDTH=40
HEIGHT=40
GRIDSIZE=16
global USE_GRAPHICS
USE_GRAPHICS=True
CREATURE_PIC=[QImage('jpac.png').transformed(QTransform().rotate(a)) for a in xrange(0,360,90)]
FOOD_PIC=QImage('food16.png')
CORPSE_PIC=QImage('pacdead.png')
MUTATE=10 #chance of mutation in ‰
