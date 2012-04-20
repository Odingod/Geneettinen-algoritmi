# -*- coding: utf-8 -*-

from PySide.QtCore import *
from PySide.QtGui import *
from random import randint
from random import choice

#from world import *
#from gen import *
#from world import *
from globals import *
import gen
import io


class WorldRetriever(object):
    def __init__(self, w):
        self.world = w
        global world
        world = self.world

choices = {
    'LEFT': 0,
    'RIGHT': 1,
    'AROUND': 2,
    'MOVE': 3
}

sights = {
    'NOTHING': 0,
    'CREATURE': 1,
    'VEGETABLE': 2,
    'WALL': 3
}

class Creature(object):
    '''
    Basic creature
    
    Contains all the necessary data to simulate the creature. 
    genome contains creature's genome, memory it's current state and loc it's location.
    Genome is a 16*4 array of tuples. Creature's next action and state is decided by the genome.
    It takes the tuple from genome[memory][sight] where sight is based on what's infront of the creature.
    Then it does the action based on the tuples first member and sets it's own memory to the second member.
    
    '''
    def __init__(self, loc, heading, genome=None,test=False):
        self.loc = loc
        self.heading = heading
        self.sight = 0
        self.memory = 0
        self.walked = 0
        self.accessibleTerrain = ['water', 'grass', 'forest', 'hill']
        if genome is None:
            self.genome = [[(randint(0, len(choices) - 1), randint(0, 15)) for y in xrange(4)] for x in xrange(16)]
        else: self.genome = genome
            
        self.eaten = 1
        self.calories = 500
        self.dead = False
        self.miles = []
        if test:
			# global USE_GRAPHICS 
			world.USE_GRAPHICS = False

        #io.creaturesToXML([self])


    def isDead(self):
        return self.dead
    
    def changePic(self):
        return
    
    def moveSelf(self):
        '''
        Moves self to the next location if it doesn't already contain a creature        
        Also eats food  if there is some on the new square
        '''

        newloc = self.nextLoc()     

        if self.loc != newloc:
            self.walked += 1
   
        if world.getCreature(newloc) is None:
            self.calories -= 10
            if newloc not in self.miles:
                self.miles.append(newloc)

            if self.calories < 0:
                self.dead = True
                
            world.updateLocation(self, newloc)

        if world.getFood(newloc) is not None:
            world.removeFood(world.getFood(newloc))
            self.eaten += 1
            self.calories += 50

            
    def nextLoc(self):
        '''
        Tells the creature's next possible location
        '''
        newloc = (self.loc[0] + self.heading[0], self.loc[1] + self.heading[1])
        #print newloc
#        print self.heading

        if newloc[0] < 0:
            newloc = (0, newloc[1])
        elif newloc[0] > WIDTH:
            newloc = (WIDTH, newloc[1])
            
        if newloc[1] < 0:
            newloc = (newloc[0], 0)
        elif newloc[1] > HEIGHT:
            newloc = (newloc[0], HEIGHT)

        self.nextTerrainType = getAssociatedKey(ID=world.terrain[newloc[0]][newloc[1]])
        if self.nextTerrainType not in self.accessibleTerrain:
            return (self.loc[0], self.loc[1])

        return newloc
    
    def turnSelf(self, heading):
        self.heading = heading
        
    def doTurn(self):
        '''
        Executes the turn
        
        First updates the sight and then does the action defined by the genome
        '''
        if not self.isDead():
            self.updateSelf()
            self.doAction()
    
    def updateSelf(self):
        '''
        Updates sight based on what is infront of the creature
        '''
        nextLocation = self.nextLoc()
        outOfBounds = nextLocation == self.loc
        
        if world.getCreature(nextLocation) is not None and world.getCreature(nextLocation) is not self: 
            self.sight = sights['CREATURE']

        elif world.getFood(nextLocation) is not None:
            self.sight = sights['VEGETABLE']
        elif outOfBounds or self.nextTerrainType == 'deep_water' or self.nextTerrainType == 'mountain':
            self.sight = sights['WALL']
        else: self.sight = sights['NOTHING']
    
    def turnLeft(self):
        if self.heading == NORTH: self.turnSelf(WEST)
        elif self.heading == WEST: self.turnSelf(SOUTH)
        elif self.heading == SOUTH: self.turnSelf(EAST)
        elif self.heading == EAST: self.turnSelf(NORTH)
    
    def turnRight(self):
        if self.heading == NORTH: self.turnSelf(EAST)
        elif self.heading == WEST: self.turnSelf(NORTH)
        elif self.heading == SOUTH: self.turnSelf(WEST)
        elif self.heading == EAST: self.turnSelf(SOUTH)

    def turnAround(self):
        if self.heading == NORTH: self.turnSelf(SOUTH)
        elif self.heading == WEST: self.turnSelf(EAST)
        elif self.heading == SOUTH: self.turnSelf(NORTH)
        elif self.heading == EAST: self.turnSelf(WEST)
        
    def foodAround(self):
        '''
        returns the direction where is food or False if there isn't food near
        '''
        if self.heading == NORTH:
            left = (self.loc[0] - 1, self.loc[1])
            right = (self.loc[0] + 1, self.loc[1])
        elif self.heading == WEST:
            left = (self.loc[0], self.loc[1] + 1)
            right = (self.loc[0], self.loc[1] - 1)
        elif self.heading == SOUTH:
            left = (self.loc[0] + 1, self.loc[1])
            right = (self.loc[0] - 1, self.loc[1])
        elif self.heading == EAST:
            left = (self.loc[0], self.loc[1] - 1)
            right = (self.loc[0], self.loc[1] + 1)
        if world.getFood(left) is not None:
            return "left"
        elif world.getFood(right) is not None:
            return "right"
        else:
            return False

        
    def doAction(self):
        '''
        Does the action defined by the genome
        '''
        #if self.sight!=0:  
#        print self.memory,self.sight
        a, b = self.genome[self.memory][self.sight]
        if self.sight == sights['VEGETABLE']:
            self.moveSelf()
        elif self.foodAround() != False:
            if self.foodAround() == "left":
                self.turnLeft()
            else:
                self.turnRight()
        else:
            if a == choices['LEFT']: self.turnLeft()
            elif a == choices['RIGHT']: self.turnRight()
            elif a == choices['AROUND']: self.turnAround()
            elif a == choices['MOVE']: self.moveSelf()

        self.memory = b
        
    def fitness(self):
        return (len(self.miles) + self.eaten - 1)
        
    def combine(self,other):
        '''
        Mates self and other and produces another creature and returns it.
        
        New creature's genome's first half comes from self and the second part from the other.
        The splitting point point is chosen by random.
        This could be a bit more elaborate.
        http://en.wikipedia.org/wiki/Crossover_%28genetic_algorithm%29
        ''' 
        newGenome = [[None] * 4 for x in xrange(16)]
        a, b = randint(0, len(choices) - 1), randint(0, 15)

        for x in xrange(16):
            for y in xrange(4):
                if randint(0, 1000) < MUTATE:
                    newGenome[x][y] = (randint(0, len(choices) - 1), randint(0, 15))
                elif x is b and y > a:
                    newGenome[x][y] = other.genome[x][y]
                elif x > b:
                    newGenome[x][y] = other.genome[x][y]
                else:
                    newGenome[x][y] = self.genome[x][y]

        if world.USE_GRAPHICS:
            return CreatureLabel(world, (randint(0, WIDTH), randint(0, HEIGHT)), newGenome)
        else:
            return Creature((randint(0, WIDTH), randint(0, HEIGHT)), NORTH, newGenome)
        
        

class CreatureLabel(QLabel, Creature):
    '''
    Class that inherits from Creature and QLabel and that can be added to the WorldLabel
    '''
    def __init__(self, parent, loc, genome=None):
 
        QLabel.__init__(self, parent)
        Creature.__init__(self, loc, NORTH, genome)
        self.resize(GRIDSIZE, GRIDSIZE)
        self.show()
        self.setPixmap(QPixmap.fromImage(CREATURE_PIC[3]))


    def turnSelf(self, heading):
        '''
        Turns the picture
        '''
        super(CreatureLabel, self).turnSelf(heading)
        a = 0
        if heading == NORTH: a = 3
        elif heading == EAST: a = 0
        elif heading == SOUTH: a = 1
        elif heading == WEST: a = 2
        self.setPixmap(QPixmap.fromImage(CREATURE_PIC[a]))

    def changePic(self):
        '''
        pic changes to corpse if creature dies
        '''
        super(CreatureLabel, self).changePic()
        self.setPixmap(QPixmap.fromImage(CORPSE_PIC))

class Generation(object):
    '''
    Contains all the creatures of one generation
    
    Has function to produce new generation based on the current one
    '''
    def __init__(self, size, creatures=None):
        self.size = size

        if creatures is None:
            self.creatures = []

            for x in xrange(self.size):
                if world.USE_GRAPHICS:
                    self.creatures.append(CreatureLabel(world, (randint(0, WIDTH), randint(0, HEIGHT))))

                else: 
                    self.creatures.append(Creature((randint(0, WIDTH), randint(0, HEIGHT)), NORTH))

        else: self.creatures = creatures


    def nextGeneration(self):
        '''
        Generates new generation and returns it.
        
        First it creates a list candidates which contains list indices of creatures.
        The more the creature has eaten and visited places the more places it gets on the candidate list.
        Then new creatures are created by randomly choosing the creatures to combine.
        '''
        
        candidates = sum([[i] * self.creatures[i].fitness() for i in xrange(len(self.creatures))], [])
        # sum is used to flatten the list of lists
        print dict((candidate, candidates.count(candidate)) for candidate in candidates)
        creatures = []

        for x in xrange(self.size):
            creatures.append(self.creatures[choice(candidates)].combine(self.creatures[choice(candidates)]))

        return Generation(self.size, creatures)
    
    def totalEaten(self):
        '''
        Returns how much the entire genearation has eaten
        '''
        i = 0
        for cre in self.creatures:
            i += cre.eaten - 1
        return i
    
    def totalWalked(self):
        '''
        Return how much the entire generation has walked
        '''
    
        i = 0
        for cre in self.creatures:
            i += cre.walked
        return i    
