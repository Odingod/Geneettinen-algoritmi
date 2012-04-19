import unittest
from creature import *

class TestCreature(unittest.TestCase):

	def setUp(self):
		self.cre1=Creature((0,0),1)
	
	def test_alive(self):
		self.assertFalse(self.cre1.isDead())
	


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestCreature)
	unittest.TextTestRunner(verbosity=2).run(suite)