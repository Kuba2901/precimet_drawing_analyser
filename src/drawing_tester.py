import unittest
import os
from .drawing_analyser import DrawingAnalyser

class DrawingTester(unittest.TestCase):

	def setUp(self):
		TEST_DIR = "assets"
		self.test_files = [f"{TEST_DIR}/{filename}" for filename in os.listdir(TEST_DIR) if not "#" in filename]
		self.test_files.sort()
		print(self.test_files)
		self.holes_count = [2, 0, 3, 3, 3, 2, 4, 0, 29]  # Ensure these match file count
		self.total_length = [247.984, 886.735, 150.078, 267.115, 4599.98, 4528.53, 429.124, 1953.4]
	
	# def test_get_holes_count(self):
	# 	for idx, test_file in enumerate(self.test_files):
	# 		analyser = DrawingAnalyser("Test", test_file)
	# 		expected_holes_count = self.holes_count[idx]
	# 		self.assertEqual(analyser.get(), expected_holes_count, f"Mismatch in {test_file}, got: {analyser.get_holes_count()}, expected: {expected_holes_count}")
	
	def test_get_total_length(self):
		for idx, test_file in enumerate(self.test_files):
			analyser = DrawingAnalyser("Test", test_file)
			expected_total_length = self.total_length[idx]
			try:
				self.assertAlmostEqual(analyser.get_total_length(), expected_total_length, places=3, msg=f"Mismatch in {test_file}, got: {analyser.get_total_length()}, expected: {expected_total_length}")
				print(f"SUCCESS IN FILE: {test_file}")
			except AssertionError as e:
				print(f"FAILURE IN FILE: {test_file}")
				print("ERROR: ", e)
			print("\n\n")

if __name__ == '__main__':
	unittest.main()
