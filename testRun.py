import unittest
from creature import *
from gen import *
from globals import *
from world import *
from terrain import *
from io import *

class TestCreature(unittest.TestCase):

	def setUp(self):
		cre1=Creature(1,1)
		self.world=World(True)
		self.world.makeTerrain(NoiseMapGenerator())
		self.world.populate()
	
	def test_alive(self):
		self.assertFalse(self.world.creatures[self.world.creatures.keys()[0]].isDead())
	def test_destruction(self):
		#Teemu Leivo
		self.world.removeEverything()
		self.assertFalse(self.world.creatures)
		self.assertFalse(self.world.foods)
	def test_combine(self):
		cre1=self.world.creatures[self.world.creatures.keys()[0]]
		cre2=self.world.creatures[self.world.creatures.keys()[1]]
		newCre=cre1.combine(cre2)
		self.assertEqual(len(cre1.genome),len(newCre.genome))
		
	def tearDown(self):
		pass

class TestIO(unittest.TestCase):
    #Student: Jussi Lopponen

	def setUp(self):
		pass
    
	def test_terrain(self):
		terrain = NoiseMapGenerator()
		terrain.generate()
		terrain.saveMap('testi.data')
		anotherTerrain = mapFileToArray('testi.data')
		self.assertEqual(terrain.getTerrainData(),anotherTerrain)

	def tearDown(self):
		pass

class TestWorld(unittest.TestCase):
	#Created by Oskari Nousiainen, aka. Xywzel
	def setUp(self):
		self.world = World(False, True)
		self.generator = NoiseMapGenerator(3, globals.WIDTH+1, globals.HEIGHT+1, 6.0, 1111111)
		self.world.makeTerrain(self.generator)
		
	def test_world(self):
		self.world.populate()
		self.assertIsNotNone(self.world.creatures, "There should now bee creatures") 
		
	def tearDown(self):
		pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCreature)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIO)
    unittest.TextTestRunner(verbosity=2).run(suite)
