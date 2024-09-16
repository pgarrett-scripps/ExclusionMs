import unittest

import exclusionms.apihandler as hand
from exclusionms.components import ExclusionInterval, ExclusionPoint

"""
Must have ExclusionMSAPI running!
"""

EXCLUSIONMS_IP = 'http://172.29.226.111:8000'
EXCLUSIONMS_IP = 'http://127.0.0.1:8000'

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

point1 = ExclusionPoint(charge=1, mass=1000.5, rt=None, ook0=1000.5, intensity=1000.5)


class TestExclusionList(unittest.TestCase):

    def test_clear(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))

    def test_save_load_delete(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.save(EXCLUSIONMS_IP, 'testing')
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(2, hand.get_len(EXCLUSIONMS_IP))
        self.assertTrue('testing' in hand.get_files(EXCLUSIONMS_IP))
        hand.load(EXCLUSIONMS_IP, 'testing')
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        hand.delete(EXCLUSIONMS_IP, 'testing')
        self.assertFalse('testing' in hand.get_files(EXCLUSIONMS_IP))
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))

    def test_get_statistics(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.get_statistics(EXCLUSIONMS_IP)

    def test_add_interval(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))

    def test_add_intervals(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2, interval3])
        self.assertEqual(3, hand.get_len(EXCLUSIONMS_IP))

    def test_search_interval(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        intervals = hand.search_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, len(intervals))

    def test_search_intervals(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2, interval3])
        self.assertEqual(3, hand.get_len(EXCLUSIONMS_IP))
        intervals = hand.search_intervals(EXCLUSIONMS_IP, [interval1, interval2, interval3, interval4])
        self.assertEqual(4, len(intervals))
        self.assertEqual(1, len(intervals[0]))
        self.assertEqual(1, len(intervals[1]))
        self.assertEqual(1, len(intervals[2]))
        self.assertEqual(0, len(intervals[3]))

    def test_delete_interval(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        hand.delete_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))

    def test_delete_intervals(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2, interval3])
        self.assertEqual(3, hand.get_len(EXCLUSIONMS_IP))
        hand.delete_intervals(EXCLUSIONMS_IP, [interval1, interval2, interval3])
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))

    def test_search_point(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        intervals = hand.search_point(EXCLUSIONMS_IP, point1)
        self.assertEqual(1, len(intervals))

    def test_search_points(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2])
        self.assertEqual(2, hand.get_len(EXCLUSIONMS_IP))
        intervals = hand.search_points(EXCLUSIONMS_IP, [point1, point1])
        self.assertEqual(2, len(intervals))
        self.assertEqual(1, len(intervals[0]))
        self.assertEqual(1, len(intervals[0]))

    def test_exclusion_search_point(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        is_excluded = hand.exclusion_search_point(EXCLUSIONMS_IP, point1)
        self.assertEqual(True, is_excluded)

    def test_inclusion_search_point(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        is_excluded = hand.inclusion_search_point(EXCLUSIONMS_IP, point1)
        self.assertEqual(False, is_excluded)

    def test_status_search_point(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_interval(EXCLUSIONMS_IP, interval1)
        self.assertEqual(1, hand.get_len(EXCLUSIONMS_IP))
        is_excluded = hand.status_search_point(EXCLUSIONMS_IP, point1)
        self.assertEqual(False, is_excluded)

    def test_exclusion_search_points(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2])
        self.assertEqual(2, hand.get_len(EXCLUSIONMS_IP))
        intervals = hand.exclusion_search_points(EXCLUSIONMS_IP, [point1, point1])
        self.assertEqual(2, len(intervals))
        self.assertEqual(True, intervals[0])
        self.assertEqual(True, intervals[0])

        intervals = hand.exclusion_search_points(EXCLUSIONMS_IP, [point1, point1], batch=True)
        self.assertEqual(2, len(intervals))
        self.assertEqual(True, intervals[0])
        self.assertEqual(True, intervals[0])

        intervals = hand.exclusion_search_points(EXCLUSIONMS_IP, [point1, point1], batch=True, use_ujson=True)
        self.assertEqual(2, len(intervals))
        self.assertEqual(True, intervals[0])
        self.assertEqual(True, intervals[0])

    def test_inclusion_search_points(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2])
        self.assertEqual(2, hand.get_len(EXCLUSIONMS_IP))

        intervals = hand.inclusion_search_points(EXCLUSIONMS_IP, [point1, point1])
        self.assertEqual(2, len(intervals))
        self.assertEqual(False, intervals[0])
        self.assertEqual(False, intervals[0])

        intervals = hand.inclusion_search_points(EXCLUSIONMS_IP, [point1, point1], batch=True)
        self.assertEqual(2, len(intervals))
        self.assertEqual(False, intervals[0])
        self.assertEqual(False, intervals[0])

        intervals = hand.inclusion_search_points(EXCLUSIONMS_IP, [point1, point1], batch=True, use_ujson=True)
        self.assertEqual(2, len(intervals))
        self.assertEqual(False, intervals[0])
        self.assertEqual(False, intervals[0])

    def test_points_status(self):
        hand.clear(EXCLUSIONMS_IP)
        self.assertEqual(0, hand.get_len(EXCLUSIONMS_IP))
        hand.add_intervals(EXCLUSIONMS_IP, [interval1, interval2])
        self.assertEqual(2, hand.get_len(EXCLUSIONMS_IP))

        intervals = hand.status_search_points(EXCLUSIONMS_IP, [point1, point1])
        self.assertEqual(2, len(intervals))
        self.assertEqual(False, intervals[0])
        self.assertEqual(False, intervals[0])

        intervals = hand.status_search_points(EXCLUSIONMS_IP, [point1, point1], batch=True)
        self.assertEqual(2, len(intervals))
        self.assertEqual(False, intervals[0])
        self.assertEqual(False, intervals[0])

        intervals = hand.status_search_points(EXCLUSIONMS_IP, [point1, point1], batch=True, use_ujson=True)
        self.assertEqual(2, len(intervals))
        self.assertEqual(False, intervals[0])
        self.assertEqual(False, intervals[0])


if __name__ == '__main__':
    unittest.main()
