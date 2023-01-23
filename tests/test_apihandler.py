import unittest

import exclusionms.apihandler as hand
from exclusionms.components import ExclusionInterval, ExclusionPoint

"""
Must have ExclusionMSAPI running!
"""

IP = 'http://127.0.0.1:8000'

interval1 = ExclusionInterval(interval_id='PEPTIDE', charge=1,
                              min_mass=1000, max_mass=1001,
                              min_rt=None, max_rt=None,
                              min_ook0=1000, max_ook0=None,
                              min_intensity=None, max_intensity=1001)
interval2 = ExclusionInterval(interval_id='PEPTIDE', charge=2,
                              min_mass=1000, max_mass=1001,
                              min_rt=None, max_rt=None,
                              min_ook0=1000, max_ook0=None,
                              min_intensity=None, max_intensity=1001)
interval3 = ExclusionInterval(interval_id='PEPTIDE', charge=3,
                              min_mass=1000, max_mass=1001,
                              min_rt=None, max_rt=None,
                              min_ook0=1000, max_ook0=None,
                              min_intensity=None, max_intensity=1001)
interval4 = ExclusionInterval(interval_id='PEPTIDE', charge=4,
                              min_mass=1000, max_mass=1001,
                              min_rt=None, max_rt=None,
                              min_ook0=1000, max_ook0=None,
                              min_intensity=None, max_intensity=1001)

point1 = ExclusionPoint(charge=1,mass=1000.5,rt=None,ook0=1000.5,intensity=1000.5)


class TestExclusionList(unittest.TestCase):

    def test_clear(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))

    def test_save_load_delete(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.save(IP, 'testing')
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        self.assertTrue('testing' in hand.get_files(IP))
        hand.load(IP, 'testing')
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        hand.delete(IP, 'testing')
        self.assertFalse('testing' in hand.get_files(IP))
        self.assertEqual(1, hand.get_len(IP))

    def test_get_statistics(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.get_statistics(IP)

    def test_add_interval(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))

    def test_add_intervals(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_intervals(IP, [interval1, interval2, interval3])
        self.assertEqual(3, hand.get_len(IP))

    def test_search_interval(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        intervals = hand.search_interval(IP, interval1)
        self.assertEqual(1, len(intervals))

    def test_search_intervals(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_intervals(IP, [interval1, interval2, interval3])
        self.assertEqual(3, hand.get_len(IP))
        intervals = hand.search_intervals(IP, [interval1, interval2, interval3, interval4])
        self.assertEqual(4, len(intervals))
        self.assertEqual(1, len(intervals[0]))
        self.assertEqual(1, len(intervals[1]))
        self.assertEqual(1, len(intervals[2]))
        self.assertEqual(0, len(intervals[3]))

    def test_delete_interval(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        hand.delete_interval(IP, interval1)
        self.assertEqual(0, hand.get_len(IP))

    def test_delete_intervals(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_intervals(IP, [interval1, interval2, interval3])
        self.assertEqual(3, hand.get_len(IP))
        hand.delete_intervals(IP, [interval1, interval2, interval3])
        self.assertEqual(0, hand.get_len(IP))

    def test_search_point(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        intervals = hand.search_point(IP, point1)
        self.assertEqual(1, len(intervals))

    def test_search_points(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_intervals(IP, [interval1, interval2])
        self.assertEqual(2, hand.get_len(IP))
        intervals = hand.search_points(IP, [point1, point1])
        self.assertEqual(2, len(intervals))
        self.assertEqual(1, len(intervals[0]))
        self.assertEqual(1, len(intervals[0]))

    def test_exclusion_search_point(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_interval(IP, interval1)
        self.assertEqual(1, hand.get_len(IP))
        is_excluded = hand.exclusion_search_point(IP, point1)
        self.assertEqual(True, is_excluded)

    def test_exclusion_search_points(self):
        hand.clear(IP)
        self.assertEqual(0, hand.get_len(IP))
        hand.add_intervals(IP, [interval1, interval2])
        self.assertEqual(2, hand.get_len(IP))
        intervals = hand.exclusion_search_points(IP, [point1, point1])
        self.assertEqual(2, len(intervals))
        self.assertEqual(True, intervals[0])
        self.assertEqual(True, intervals[0])


if __name__ == '__main__':
    unittest.main()
