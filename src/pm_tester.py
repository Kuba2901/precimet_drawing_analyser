import unittest
import os
from .pm_analyser import PMAnalyser

class PMTester(unittest.TestCase):
    def setUp(self):
        TEST_DIR = "assets"
        self.test_files = [f"{TEST_DIR}/{filename}" for filename in os.listdir(TEST_DIR) if "#" not in filename]
        self.test_files.sort()
        print(self.test_files)
        self.holes_count = [3, 1, 4, 4, 3, 5, 1, 30]
        self.total_length = [247.984, 886.735, 150.078, 267.115, 4599.98, 4248.53, 429.124, 1953.4]
        self.turns_count = [4, 4, 8, 8, 12, 20, 6, 88]

    def run_test_with_stats(self, test_name, test_function):
        print(f"\n{'=' * 20} {test_name.upper()} {'=' * 20}")
        success_count = 0
        failure_count = 0

        for idx, test_file in enumerate(self.test_files):
            try:
                test_function(idx, test_file)
                print(f"SUCCESS IN FILE: {test_file}")
                success_count += 1
            except AssertionError as e:
                print(f"FAILURE IN FILE: {test_file}")
                print("ERROR: ", e)
                failure_count += 1
            print()

        print(f"{test_name} Summary:")
        print(f"Total tests: {len(self.test_files)}")
        print(f"Successes: {success_count}")
        print(f"Failures: {failure_count}")
        print("=" * 50)

    def test_get_holes_count(self):
        """Ensure that the number of holes in the drawing is correct"""
        def test_function(idx, test_file):
            analyser = PMAnalyser(test_file)
            expected_holes_count = self.holes_count[idx]
            cut_ins = analyser.cut_ins_count
            self.assertEqual(cut_ins, expected_holes_count, 
                             f"Mismatch in {test_file}, got: {cut_ins}, expected: {expected_holes_count}")

        self.run_test_with_stats("Holes Count Test", test_function)

    def test_get_total_length(self):
        """Ensure that the total length of the drawing is correct"""
        def test_function(idx, test_file):
            analyser = PMAnalyser(test_file)
            expected_total_length = self.total_length[idx]
            total_length = analyser.total_cutting_length
            self.assertAlmostEqual(total_length, expected_total_length, places=2,
                                   msg=f"Mismatch in {test_file}, got: {total_length}, expected: {expected_total_length}")

        self.run_test_with_stats("Total Length Test", test_function)

    def test_get_turns_count(self):
        """Ensure that the number of turns in the drawing is correct"""
        def test_function(idx, test_file):
            analyser = PMAnalyser(test_file)
            expected_turns_count = self.turns_count[idx]
            turns = analyser.turns_count
            self.assertEqual(turns, expected_turns_count,
                             f"Mismatch in {test_file}, got: {turns}, expected: {expected_turns_count}")

        self.run_test_with_stats("Turns Count Test", test_function)

if __name__ == '__main__':
    unittest.main()