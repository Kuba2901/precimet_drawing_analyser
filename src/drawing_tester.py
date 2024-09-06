import unittest
import os
from .drawing_analyser import DrawingAnalyser

class DrawingTester(unittest.TestCase):

	def setUp(self):
		TEST_DIR = "assets"
		self.test_files = [f"{TEST_DIR}/{filename}" for filename in os.listdir(TEST_DIR) if not "#" in filename]
		self.test_files.sort()
		print(self.test_files)
		self.holes_count = [3, 1, 4, 4, 3, 5, 1, 30]
		self.total_length = [247.984, 886.735, 150.078, 267.115, 4599.98, 4248.53, 429.124, 1953.4]
	
	def test_get_holes_count(self):
		"""
		Ensure that the number of holes in the drawing is correct
		"""
		print("HOLES COUNT TEST")
		for idx, test_file in enumerate(self.test_files):
			analyser = DrawingAnalyser("Test", test_file)
			expected_holes_count = self.holes_count[idx]
			cut_ins = analyser.get_cut_ins_count()
			try:
				self.assertEqual(cut_ins, expected_holes_count, f"Mismatch in {test_file}, got: {cut_ins}, expected: {expected_holes_count}")
				print(f"SUCCESS IN FILE: {test_file}")
			except AssertionError as e:
				print(f"FAILURE IN FILE: {test_file}")
				print("ERROR: ", e)
			print("\n")
	
	def test_get_total_length(self):
		"""
		Ensure that the total length of the drawing is correct
		"""
		print("TOTAL LENGTH TEST")
		for idx, test_file in enumerate(self.test_files):
			analyser = DrawingAnalyser("Test", test_file)
			expected_total_length = self.total_length[idx]
			try:
				self.assertAlmostEqual(analyser.get_total_length(), expected_total_length, places=2, msg=f"Mismatch in {test_file}, got: {analyser.get_total_length()}, expected: {expected_total_length}")
				print(f"SUCCESS IN FILE: {test_file}")
			except AssertionError as e:
				print(f"FAILURE IN FILE: {test_file}")
				print("ERROR: ", e)
			print("\n")

if __name__ == '__main__':
	unittest.main()
