import unittest
import os

class DrawingTester(unittest.TestCase):
	def __init__(self):
		TEST_DIR = "assets"
		self.test_files = [f"{TEST_DIR}/{filename}" for filename in os.listdir(TEST_DIR)]
		print(self.test_files)
