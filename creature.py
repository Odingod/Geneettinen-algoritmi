# -*- coding: utf-8 -*-

from PySide.QtCore import *
from PySide.QtGui import *
from random import randint
from random import choice
import random
import neuronnet

#from world import *
#from gen import *
#from world import *
from globals import *
import gen
import io


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
    def __init__(self, loc, heading, world, genome=None,test=False):
        self.loc = loc
        self.heading = heading
        self.sight = []
        self.walked = 0
        self.world=world
        self.accessibleTerrain = ['water', 'grass', 'forest', 'hill', 'coast']
        if genome is None:
            self.genome = neuronnet.NeuronNet(16,3,1,10)
        else: self.genome = genome
            
        self.eaten = 1
        self.calories = 1000
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
        terrain = getAssociatedKey(ID=self.world.terrain[newloc[0]][newloc[1]])    

        if self.loc != newloc:
            self.walked += 1
            if terrain == 'grass' or terrain == 'coast':
                self.calories -= 5
            elif terrain == 'water' or terrain == 'hill':
                self.calories -= 15
            elif terrain == 'forest':
                self.calories -= 10
            if self.world.getCreature(newloc) is None:
                if newloc not in self.miles:
                    self.miles.append(newloc)
    
                if self.calories < 0:
                    self.dead = True
                    
                self.world.updateLocation(self, newloc)
    
            if self.world.getFood(newloc) is not None:
                if GAMEOFLIFE:
                    if self.world.getFood(newloc).isAlive():
                        self.world.removeFood(self.world.getFood(newloc))
                        self.eaten += 1
                        self.calories += 100
                else:
                    self.world.removeFood(self.world.getFood(newloc))
                    self.eaten += 1
                    self.calories += 100
            return True
        return False
            
    def nextLoc(self):
        '''
        Tells the creature's next possible location
        '''
        newloc = (self.loc[0] + self.heading[0], self.loc[1] + self.heading[1])
        #print newloc
        #print self.heading

        if newloc[0] < 0:
            newloc = (0, newloc[1])
        elif newloc[0] > WIDTH:
            newloc = (WIDTH, newloc[1])
            
        if newloc[1] < 0:
            newloc = (newloc[0], 0)
        elif newloc[1] > HEIGHT:
            newloc = (newloc[0], HEIGHT)

        self.nextTerrainType = getAssociatedKey(ID=self.world.terrain[newloc[0]][newloc[1]])
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
        self.sight = self.see()
        
    
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
        
    def see(self):
        center = (self.loc[0] + self.heading[0], self.loc[1] + self.heading[1])
        if 0 > center[0] > WIDTH or 0 > center[1] > HEIGHT:
            return [0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1]
        up = (center[0] - 1, center[1])
        down = (center[0] + 1, center[1])
        left = (center[0], center[1] - 1)
        right = (center[0], center[1] + 1)
        if self.heading == NORTH: sights = [left,center,right,up]
        elif self.heading == WEST: sights = [down,center,up,left]
        elif self.heading == SOUTH: sights = [right,center,left,down]
        elif self.heading == EAST: sights = [up,center,down,right]
        newsight = []
        for sight in sights:
            if 0 > sight[0] or sight[0] >= WIDTH or 0 > sight[1] or sight[1] >= HEIGHT:
                newsight.append(0)
                newsight.append(0)
                newsight.append(0)
                newsight.append(1)
            elif self.world.terrain[sight[0]][sight[1]] == 1 or self.world.terrain[sight[0]][sight[1]] == 7:
                newsight.append(0)
                newsight.append(0)
                newsight.append(0)
                newsight.append(1)
            elif self.world.getCreature(sight) is not None:
                newsight.append(0)
                newsight.append(1)
                newsight.append(0)
                newsight.append(0)
            elif self.world.getFood(sight) is not None:
                newsight.append(0)
                newsight.append(0)
                newsight.append(1)
                newsight.append(0)
            else:
                newsight.append(1)
                newsight.append(0)
                newsight.append(0)
                newsight.append(0)
        if newsight[7] == 1:
            newsight[12] = 0
            newsight[13] = 0
            newsight[14] = 0
            newsight[15] = 1
        return newsight
            
        
                

        
    def doAction(self):
        '''
        Does the action defined by the genome
        '''
        output = self.genome.process(self.sight)
        
        if output[0] > output[1] and output[0] > output[2]: 
            self.turnLeft()
            self.moveSelf()
        elif output[2] > output[1] and output[2] > output[0]: 
            self.turnRight()
            self.moveSelf()
        else: 
            if not self.moveSelf():
                if output[0] > output[2]:
                    self.turnLeft()
                    self.moveSelf()
                else:
                    self.turnRight()
                    self.moveSelf()

    def fitness(self):
        if self.isDead():
            fit = 1
        else:    
            fit = len(self.miles) / 10 + self.eaten
        return fit
    
    def combine(self,other):
        '''
        Mates self and other and produces another creature and returns it.
        
        New creature's genome's first half comes from self and the second part from the other.
        The splitting point point is chosen by random.
        This could be a bit more elaborate.
        http://en.wikipedia.org/wiki/Crossover_%28genetic_algorithm%29
        '''
        
        newGenome = self.genome.mate(other.genome)

        if self.world.USE_GRAPHICS:
            return CreatureLabel(self.world, (randint(0, WIDTH), randint(0, HEIGHT)), newGenome)
        else:
            return Creature((randint(0, WIDTH), randint(0, HEIGHT)), NORTH, self.world, newGenome)
        
class CreatureLabel(QLabel, Creature):
    '''
    Class that inherits from Creature and QLabel and that can be added to the WorldLabel
    '''
    def __init__(self, parent, loc, genome=None):
 
        QLabel.__init__(self, parent)
        Creature.__init__(self, loc, NORTH,parent, genome)
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
    def __init__(self, size, world, creatures=None):
        self.size = size
        self.world=world
        if creatures is None:
            self.creatures = []

            for x in xrange(self.size):
                if world.USE_GRAPHICS:
                    self.creatures.append(CreatureLabel(world, (randint(0, WIDTH), randint(0, HEIGHT))))

                else: 
                    self.creatures.append(Creature((randint(0, WIDTH), randint(0, HEIGHT)), NORTH, world))

        else: self.creatures = creatures

    def rouletteSelection(self, fitness_list):
        total_fitness = sum(fitness_list)
        slice = random.random() * total_fitness
        
        total = 0
        for i in range(self.size):
            total += fitness_list[i]
            if total > slice:
                return self.creatures[i]

    def nextGeneration(self):
        '''
        Generates new generation and returns it.
        
        First it creates a list candidates which contains list indices of creatures.
        The more the creature has eaten and visited places the more places it gets on the candidate list.
        Then new creatures are created by randomly choosing the creatures to combine.
        '''
        fitness_list = [self.creatures[i].fitness() for i in xrange(len(self.creatures))]

        creatures = [self.creatures[fitness_list.index(max(fitness_list))]]

        for x in xrange(self.size-1):
            mother = self.rouletteSelection(fitness_list)
            father = self.rouletteSelection(fitness_list)
            newcre = mother.combine(father)
            creatures.append(newcre)

        return Generation(self.size,self.world, creatures)
    
    def totalFitness(self):
        total = 0
        for cre in self.creatures:
            total += cre.fitness()
        return total
    
    def fitnessFactor(self, creature, total):
        '''
        returns how many places creature should have on the candidate list
        '''
        part = float(creature.fitness()) / total
        places = int(part * 30)
        if places < 1 and not creature.isDead():
            return 1
        return places
    
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
