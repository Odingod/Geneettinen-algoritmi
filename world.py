# -*- coding: utf-8 -*-
from gen import *

class World(object):
    '''
    Object that contains all the creatures of the generation and food
    '''
    def __init__(self):
        self.creatures={}
        self.foods={}
        self.statistics = []
   
        
    def addCreature(self,creature):
        '''
        Adds creature if there's no other creature at the same spot, else tries to put creature somewhere else
        '''
        try:
            self.creatures[creature.loc]
        except KeyError:
            self.creatures[creature.loc]=creature
            return
        creature.loc=(randint(0,WIDTH),randint(0,HEIGHT))
        self.addCreature(creature)
        
    
    def addFood(self, food):
        '''
        Adds food if there's no other creature at the same spot, else tries to put food somewhere else
        '''
        try:
            self.foods[food.loc]
        except KeyError:
            self.foods[food.loc]=food
            return
        food.loc=(randint(0,WIDTH),randint(0,HEIGHT))
        self.addFood(food)
    
    def removeFood(self,food):
        del self.foods[food.loc]
    
    def removeCreature(self,cre):
        del self.creatures[cre.loc]

    def updateLocation(self,creature,newloc):
        del self.creatures[creature.loc]
        self.creatures[newloc]=creature
        creature.loc=newloc
        if creature.isDead():
            creature.changePic()
        
    def getCreature(self,loc):
        try:
            return self.creatures[loc]
        except KeyError:
            return None
        
    def getFood(self,loc):
        try:
            return self.foods[loc]
        except KeyError:
            return None
        
    def removeEverything(self):
        for creature in self.creatures.values():
            self.removeCreature(creature)
        for food in self.foods.values():
            self.removeFood(food)
        
    def populate(self,generation=None, food_location='random'):
        if generation!= None:
            for cre in generation.creatures:
                self.addCreature(cre)
        else:
            for x in range(10):
                self.addCreature(Creature((randint(0,WIDTH),randint(0,HEIGHT)),NORTH) if not USE_GRAPHICS else CreatureLabel(self,(randint(0,WIDTH),randint(0,HEIGHT))))
        
        if food_location=='random':
            for x in range(200):
                self.addFood(Food((randint(0,WIDTH),randint(0,HEIGHT))) if not USE_GRAPHICS else FoodLabel(self,(randint(0,WIDTH),randint(0,HEIGHT))))
        elif food_location=='middle':
            for i in range(15, 26):
                for j in range(15, 26):
                    self.addFood((Food(i, j) if not USE_GRAPHICS else FoodLabel(self, (i,j))))      
        elif food_location=='corner':
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    if (i<5 or i>WIDTH-6) and (j<5 or j>HEIGHT-6):
                        self.addFood((Food(i, j) if not USE_GRAPHICS else FoodLabel(self, (i,j))))  


class Statistics():
    def __init__(self, totaleaten, totalwalked):
        self.totaleaten = totaleaten
        self.totalwalked = totalwalked
    

                
class WorldLabel(QWidget,World):
    def __init__(self,parent=None):        
        QWidget.__init__(self,parent)
        World.__init__(self)
        self.setLayout(None)
        self.resize(GRIDSIZE*WIDTH,GRIDSIZE*HEIGHT)
        self.bool=False
        
   
    
    def sizeHint(self, *args, **kwargs):
        return QSize(GRIDSIZE*(WIDTH+1),GRIDSIZE*(HEIGHT+1))
    
    def update(self):
        for loc,cre in self.creatures.iteritems():
            cre.move(loc[0]*GRIDSIZE,loc[1]*GRIDSIZE)
    
    def updateFoods(self):
        for loc,food in self.foods.iteritems():
            food.move(loc[0]*GRIDSIZE,loc[1]*GRIDSIZE)
    
    def removeFood(self,food):
        food.setParent(None)
        super(WorldLabel,self).removeFood(food)
    
    def removeCreature(self,creature):
        creature.setParent(None)
        super(WorldLabel,self).removeCreature(creature)
    
    def populate(self,generation=None):
        super(WorldLabel,self).populate(generation)
        self.updateFoods()
        self.update()
        
