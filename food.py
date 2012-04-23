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
    def __init__(self, loc, parent=None, alive=None):
        self.loc = loc
        if GAMEOFLIFE:
            self.parent=parent
            self.parent.foods[self.loc]=self
            self.neighbours=self.getNeighbours()
            if alive!=None:
                self.alive=alive
            else:
                self.alive=True
    
    def isAlive(self):
        return self.alive
        
    def getNeighbours(self): 
        neighbours=[]   
        x=self.loc[0]
        y=self.loc[1]
        neighbourhood=[(x-1, y-1),(x, y-1), (x+1, y-1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y), (x+1, y+1) ]
        for location in neighbourhood:
            if self.parent.foods.has_key(location):
                neighbours.append(self.parent.foods[location])
        return neighbours
        
    def die(self):
        self.alive=False
        
    def resurrect(self):
        self.alive=True

class FoodLabel(QLabel, Food):
    '''
    Object that can be added to WorldLabel
    '''
    def __init__(self, parent, loc, alive=None):
        QLabel.__init__(self, parent)
        Food.__init__(self, loc, parent, alive)
        self.resize(QSize(GRIDSIZE, GRIDSIZE))
        self.show()
        self.animationStep = 0
        self.originalPic = QPixmap.fromImage(FOOD_PIC)
        self.setPixmap(self.originalPic)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def animate(self):
        self.setPixmap(self.originalPic.transformed(QTransform().rotate([-45, 0, 45, 0][self.animationStep])))
        self.animationStep = (self.animationStep + 1) % 4
        
        
class FoodGeneration(object):
    '''
    Contains all the foods of one generation
    
    Has function to produce new foodgeneration based on the current one by using principles of 
    Conway's Game of Life
    '''
    def __init__(self, size, parent, foods=None):
        self.size = size
        self.parent=parent
        if foods is None:
            self.foods = {}
            i=0
            for i in range(0, WIDTH):
                for j in range(0, HEIGHT):
                    loc=i,j
                    if USE_GRAPHICS:
                        self.foods[loc]=FoodLabel(self.parent, loc, False)
    
                    else: 
                        self.foods[loc]=Food(loc, self.parent, False)
            while i < self.size:
                x=randint(0, WIDTH-1)
                y=randint(0, HEIGHT-1)
                loc=x,y
                terrainType=getAssociatedKey(ID=self.parent.terrain[x][y])
                if terrainType!='wall' and not self.foods[loc].isAlive():
                    self.foods[loc].resurrect()
                    i+=1     
        else: 
            self.foods=foods

    def nextFoodGeneration(self):
        
        dead=[]
        resurrected=[]
        
        for loc, food in self.foods.iteritems():
            n=0
            for neighbour in food.neighbours:
                if neighbour.isAlive():
                    n+=1
            if food.isAlive():
                if n < 2:
                    dead.append(loc)
                elif n > 3:
                    dead.append(loc)
            else:
                if n==3:
                    resurrected.append(loc)
              
        for loc in dead:
            self.foods[loc].die()
            
        for food in resurrected:
            self.foods[loc].resurrect()
        
        alive=0
        dead=0
        for food in self.foods.values():
            if food.isAlive():
                alive+=1
            else:
                dead+=1
        print str(alive) + '/' + str(dead)   
        return self
        
    def totalAlive(self):
        i=0
        for food in self.foods.values():
            if food.isAlive():
                i+=1
        return i
        