import unittest
from creature import *
from gen import *
from globals import *
from world import *
from terrain import *

class TestCreature(unittest.TestCase):

	def setUp(self):
		cre1=Creature(1,1)
		self.world=World(True)
		self.world.makeTerrain(NoiseMapGenerator())
		self.world.populate()
	
	def test_alive(self):
		self.assertFalse(self.world.creatures[self.world.creatures.keys()[0]].isDead())
	
	def test_combine(self):
		cre1=self.world.creatures[self.world.creatures.keys()[0]]
		cre2=self.world.creatures[self.world.creatures.keys()[1]]
		newCre=cre1.combine(cre2)
		self.assertEqual(len(cre1.genome),len(newCre.genome))
		
	def tearDown(self):
		pass

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestCreature)
	unittest.TextTestRunner(verbosity=2).run(suite)