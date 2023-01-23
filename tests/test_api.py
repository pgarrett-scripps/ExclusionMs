import unittest

import exclusionms.apihandler
from exclusionms.components import ExclusionInterval, ExclusionPoint

"""
Must have ExclusionMSAPI running!
"""

#IP = 'http://172.29.227.247:8000'
IP = 'http://127.0.0.1:8000'

interval1 = ExclusionInterval(interval_id='PEPTIDE',
                              charge=1,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=1000,
                              max_rt=1001,
                              min_ook0=1000,
                              max_ook0=1001,
                              min_intensity=1000,
                              max_intensity=1001)

interval2 = ExclusionInterval(interval_id=None,
                              charge=1,
                              min_mass=1000,
                              max_mass=None,
                              min_rt=None,
                              max_rt=1001,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=1000,
                              max_intensity=1001)

interval3 = ExclusionInterval(interval_id='PEPTIDE',
                              charge=1,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=500,
                              max_rt=1001,
                              min_ook0=1000,
                              max_ook0=1001,
                              min_intensity=1000,
                              max_intensity=1001)

point1 = ExclusionPoint(charge=1,
                        mass=1000,
                        rt=1000,
                        ook0=1000,
                        intensity=1000)

point2 = ExclusionPoint(charge=1,
                        mass=2000,
                        rt=1000,
                        ook0=1000,
                        intensity=1000)

class TestExclusionList(unittest.TestCase):

    def setUp(self) -> None:
        exclusionms.apihandler.clear(exclusion_api_ip=IP)

    def test_save_load(self):
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        exclusionms.apihandler.save(exclusion_api_ip=IP, exid='testingapi')
        exclusionms.apihandler.clear(exclusion_api_ip=IP)
        exclusionms.apihandler.load(exclusion_api_ip=IP, exid='testingapi')
        intervals = exclusionms.apihandler.search_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        self.assertEqual(len(intervals), 1)
        self.assertEqual(intervals[0], interval1)

    def test_add_interval(self):
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval1)

    def test_get_interval(self):
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        intervals = exclusionms.apihandler.search_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        self.assertEqual(len(intervals), 1)
        self.assertEqual(intervals[0], interval1)

    def test_get_multiple_interval(self):
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval3)

        intervals = exclusionms.apihandler.search_interval(exclusion_api_ip=IP, exclusion_interval=interval2)

        self.assertEqual(len(intervals), 2)
        self.assertTrue(interval1 in intervals)
        self.assertTrue(interval3 in intervals)

    def test_delete_interval(self):
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        intervals = exclusionms.apihandler.delete_interval(exclusion_api_ip=IP, exclusion_interval=interval2)
        self.assertEqual(len(intervals), 1)
        self.assertEqual(intervals[0], interval1)

        intervals = exclusionms.apihandler.delete_interval(exclusion_api_ip=IP, exclusion_interval=interval2)
        self.assertEqual(len(intervals), 0)

    def test_get_excluded_points(self):
        exclusionms.apihandler.add_interval(exclusion_api_ip=IP, exclusion_interval=interval1)
        excluded_flags = exclusionms.apihandler.exclusion_search_points(exclusion_api_ip=IP,
                                                                    exclusion_points=[point1, point1, point2])
        self.assertEqual(len(excluded_flags), 2)
        self.assertEqual(excluded_flags, [True, True, False])

    def test_stats(self):
        exclusionms.apihandler.get_statistics(exclusion_api_ip=IP)

    def test_get_excluded_interval(self):
        exclusionms.apihandler.add_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id='PEPTIDE',
                                                 charge=None,
                                                 min_mass=1000,
                                                 max_mass=1002,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))

        intervals = exclusionms.apihandler.search_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id=None,
                                                 charge=None,
                                                 min_mass=1000,
                                                 max_mass=1002,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))
        self.assertEqual(len(intervals), 1)

        intervals = exclusionms.apihandler.search_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id=None,
                                                 charge=None,
                                                 min_mass=999,
                                                 max_mass=1003,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))
        self.assertEqual(len(intervals), 1)

        intervals = exclusionms.apihandler.search_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id=None,
                                                 charge=None,
                                                 min_mass=1001,
                                                 max_mass=1002,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))
        self.assertEqual(len(intervals), 0)

        intervals = exclusionms.apihandler.search_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id=None,
                                                 charge=1,
                                                 min_mass=999,
                                                 max_mass=1003,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))
        self.assertEqual(len(intervals), 1)

    def test_get_excluded_interval2(self):
        exclusionms.apihandler.add_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id='PEPTIDE',
                                                 charge=1,
                                                 min_mass=1000,
                                                 max_mass=1002,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))

        intervals = exclusionms.apihandler.search_interval(
            exclusion_api_ip=IP,
            exclusion_interval=ExclusionInterval(interval_id=None,
                                                 charge=None,
                                                 min_mass=1000,
                                                 max_mass=1002,
                                                 min_rt=None,
                                                 max_rt=None,
                                                 min_ook0=None,
                                                 max_ook0=None,
                                                 min_intensity=None,
                                                 max_intensity=None))
        self.assertEqual(len(intervals), 1)


if __name__ == '__main__':
    unittest.main()
