# -*- coding: utf-8 -*-

from PySide.QtCore import *
from PySide.QtGui import *
from random import randint
from random import choice

from gen import *
from globals import *
#from world import *

class Food(object):
    '''
    Very basic food object
    '''
    def __init__(self, loc):
        self.loc = loc
        
        
class FoodLabel(QLabel, Food):
    '''
    Object that can be added to WorldLabel
    '''
    def __init__(self, parent, loc):
        QLabel.__init__(self, parent)
        Food.__init__(self, loc)
        self.resize(QSize(GRIDSIZE, GRIDSIZE))
        self.show()
        self.animationStep = 0
        self.originalPic = QPixmap.fromImage(FOOD_PIC)
        self.setPixmap(self.originalPic)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def animate(self):
        self.setPixmap(self.originalPic.transformed(QTransform().rotate([-45, 0, 45, 0][self.animationStep])))
        self.animationStep = (self.animationStep + 1) % 4  
    
    
