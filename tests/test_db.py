import unittest
from copy import deepcopy

from exclusionms.components import ExclusionInterval, ExclusionPoint
from exclusionms.db import MassIntervalTree as ExclusionList, IntervalStatus

intervals = [
    ExclusionInterval(interval_id='PEPTIDE',
                      charge=1,
                      min_mass=1000,
                      max_mass=1001,
                      min_rt=1000,
                      max_rt=1001,
                      min_ook0=1000,
                      max_ook0=1001,
                      min_intensity=1000,
                      max_intensity=1001),
    ExclusionInterval(interval_id='PEPTIDE',
                      charge=1,
                      min_mass=1000,
                      max_mass=1001,
                      min_rt=1000,
                      max_rt=1002,
                      min_ook0=1000,
                      max_ook0=1001,
                      min_intensity=1000,
                      max_intensity=1001)
]


class TestExclusionList(unittest.TestCase):

    def setUp(self) -> None:
        self.exlist = ExclusionList()

    def test_add(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))

    def test_iter(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))

        for i in self.exlist:
            self.assertEqual(intervals[0], i)

    def test_duplicate_add(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))

    def test_remove(self):
        self.exlist.remove(intervals[0])
        self.assertEqual(0, len(self.exlist))

    def test_remove_by_uuid(self):
        self.exlist.add(intervals[0])
        interval = [interval for interval in self.exlist][0]
        self.exlist.remove_by_uuid(interval.interval_uuid)
        self.assertEqual(0, len(self.exlist))

        self.assertTrue(len(self.exlist.interval_tree) == 0)
        self.assertTrue(len(self.exlist.id_dict) == 0)
        self.assertTrue(len(self.exlist.uuid_dict) == 0)

    def test_add_remove(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        tmp_msg = deepcopy(intervals[0])
        self.exlist.remove(tmp_msg)
        self.assertEqual(0, len(self.exlist))

    def test_add_remove_bounds(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        tmp_msg = ExclusionInterval(interval_id=None,
                                    charge=1,
                                    min_mass=1000,
                                    max_mass=1001,
                                    min_rt=1000,
                                    max_rt=1001,
                                    min_ook0=1000,
                                    max_ook0=1001,
                                    min_intensity=1000,
                                    max_intensity=1001)
        self.exlist.remove(tmp_msg)
        self.assertEqual(0, len(self.exlist))

    def test_exclude(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_exclude_lower_mass(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000, rt=1000.5,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_exclude_upper_mass(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1001, rt=1000.5,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_exclude_lower_retention_time(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_exclude_upper_retention_time(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1001,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_exclude_lower_ook0(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000, intensity=1000.5)))

    def test_exclude_upper_ook0(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                                ook0=1001, intensity=1000.5)))

    def test_exclude_lower_intensity(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000.5, intensity=1000)))

    def test_exclude_upper_intensity(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                                ook0=1000.5, intensity=1001)))

    def test_exclude_wrong_charge(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        print(list(self.exlist.query_by_point(ExclusionPoint(charge=2, mass=1000.5, rt=1000.5,
                                                             ook0=1000.5, intensity=1000.5))))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=2, mass=1000.5, rt=1000.5,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_none_point_charge(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=None, mass=1000.5, rt=1000.5,
                                                   ook0=1000.5, intensity=1000.5)))

    def test_none_point_mass(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=None, rt=1000.5,
                                                   ook0=1000.5, intensity=1000.5)))

    def test_none_point_rt(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=None,
                                                   ook0=1000.5, intensity=1000.5)))

    def test_none_point_ook0(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                   ook0=None, intensity=1000.5)))

    def test_none_point_intensity(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                   ook0=None, intensity=None)))

    def test_none_interval_attributes(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=1000,
                                                                                max_mass=1001,
                                                                                min_rt=1000,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=1001,
                                                                                min_rt=1000,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=1000,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=None,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=None,
                                                                                max_intensity=None))))

        self.assertEqual(0, len(self.exlist.query_by_interval(ExclusionInterval(interval_id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=2000,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=None,
                                                                                max_intensity=None))))

    def test_save_load(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.exlist.save("tmp.pkl")
        self.exlist.clear()
        self.exlist.load("tmp.pkl")
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5)))

    def test_query_by_id(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertEqual(intervals[0], self.exlist.query_by_id('PEPTIDE')[0])

    def test_exclusion_interval_equality(self):
        self.assertEqual(intervals[0], intervals[0])
        self.assertNotEqual(intervals[0], intervals[1])

    def test_exclusion_point_equality(self):
        self.assertEqual(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5),
                         ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5))
        self.assertNotEqual(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5),
                            ExclusionPoint(charge=2, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5))

    def test_excluded_points(self):
        self.exlist.add(ExclusionInterval(interval_id='PEPTIDE',
                                          charge=None,
                                          min_mass=500,
                                          max_mass=1000,
                                          min_rt=None,
                                          max_rt=None,
                                          min_ook0=None,
                                          max_ook0=None,
                                          min_intensity=None,
                                          max_intensity=None))

        excluded_flag = self.exlist.is_excluded(ExclusionPoint(charge=1, mass=600, rt=None, ook0=None, intensity=None))

        self.assertTrue(excluded_flag)

    def test_excluded_interval(self):
        self.exlist.add(ExclusionInterval(interval_id='PEPTIDE',
                                          charge=None,
                                          min_mass=500,
                                          max_mass=1000,
                                          min_rt=None,
                                          max_rt=None,
                                          min_ook0=None,
                                          max_ook0=None,
                                          min_intensity=None,
                                          max_intensity=None))

        results = self.exlist.query_by_interval(ExclusionInterval(interval_id=None,
                                                                  charge=None,
                                                                  min_mass=400,
                                                                  max_mass=1100,
                                                                  min_rt=None,
                                                                  max_rt=None,
                                                                  min_ook0=None,
                                                                  max_ook0=None,
                                                                  min_intensity=None,
                                                                  max_intensity=None))

        self.assertTrue(len(results) == 1)

    def test_excluded_interval_with_data_as_string(self):
        interval = ExclusionInterval(interval_id='PEPTIDE',
                                     charge=None,
                                     min_mass=500,
                                     max_mass=1000,
                                     min_rt=None,
                                     max_rt=None,
                                     min_ook0=None,
                                     max_ook0=None,
                                     min_intensity=None,
                                     max_intensity=None,
                                     data='Just a flesh wound')

        self.exlist.add(interval)

        results = self.exlist.query_by_interval(ExclusionInterval(interval_id=None,
                                                                  charge=None,
                                                                  min_mass=400,
                                                                  max_mass=1100,
                                                                  min_rt=None,
                                                                  max_rt=None,
                                                                  min_ook0=None,
                                                                  max_ook0=None,
                                                                  min_intensity=None,
                                                                  max_intensity=None))

        self.assertTrue(len(results) == 1)
        self.assertEqual(interval, results[0])

    def test_excluded_interval_with_data_as_dict(self):
        interval = ExclusionInterval(interval_id='PEPTIDE',
                                     charge=None,
                                     min_mass=500,
                                     max_mass=1000,
                                     min_rt=None,
                                     max_rt=None,
                                     min_ook0=None,
                                     max_ook0=None,
                                     min_intensity=None,
                                     max_intensity=None,
                                     data={'status': 'Just a flesh wound'})

        self.exlist.add(interval)

        results = self.exlist.query_by_interval(ExclusionInterval(interval_id=None,
                                                                  charge=None,
                                                                  min_mass=400,
                                                                  max_mass=1100,
                                                                  min_rt=None,
                                                                  max_rt=None,
                                                                  min_ook0=None,
                                                                  max_ook0=None,
                                                                  min_intensity=None,
                                                                  max_intensity=None))

        self.assertTrue(len(results) == 1)
        self.assertEqual(interval, results[0])

    def test_excluded_interval_with_exclusion_false(self):
        interval = ExclusionInterval(interval_id='PEPTIDE',
                                     charge=None,
                                     min_mass=500,
                                     max_mass=1000,
                                     min_rt=None,
                                     max_rt=None,
                                     min_ook0=None,
                                     max_ook0=None,
                                     min_intensity=None,
                                     max_intensity=None,
                                     exclusion=False)

        self.exlist.add(interval)

        results = self.exlist.query_by_interval(ExclusionInterval(interval_id=None,
                                                                  charge=None,
                                                                  min_mass=400,
                                                                  max_mass=1100,
                                                                  min_rt=None,
                                                                  max_rt=None,
                                                                  min_ook0=None,
                                                                  max_ook0=None,
                                                                  min_intensity=None,
                                                                  max_intensity=None))

        self.assertTrue(len(results) == 1)
        self.assertEqual(interval, results[0])

    def test_excluded_interval_status(self):
        interval1 = ExclusionInterval(interval_id='PEPTIDE',
                                      charge=None,
                                      min_mass=500,
                                      max_mass=800,
                                      min_rt=None,
                                      max_rt=None,
                                      min_ook0=None,
                                      max_ook0=None,
                                      min_intensity=None,
                                      max_intensity=None,
                                      exclusion=True)

        interval2 = ExclusionInterval(interval_id='PEPTIDE',
                                      charge=None,
                                      min_mass=700,
                                      max_mass=1000,
                                      min_rt=None,
                                      max_rt=None,
                                      min_ook0=None,
                                      max_ook0=None,
                                      min_intensity=None,
                                      max_intensity=None,
                                      exclusion=False)

        self.exlist.add(interval1)
        self.exlist.add(interval2)

        self.assertEqual(self.exlist.point_status(ExclusionPoint(mass=500)), IntervalStatus.EXCLUDED)
        self.assertEqual(self.exlist.point_status(ExclusionPoint(mass=400)), IntervalStatus.NO_INTERVALS_FOUND)
        self.assertEqual(self.exlist.point_status(ExclusionPoint(mass=800)), IntervalStatus.INCLUDED)
        self.assertEqual(self.exlist.point_status(ExclusionPoint(mass=700)), IntervalStatus.EXCLUDED_INCLUDED)

    def test_include_false(self):
        self.exlist.add(intervals[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_included(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_include_true(self):
        interval = ExclusionInterval(interval_id='PEPTIDE',
                                     charge=1,
                                     min_mass=1000,
                                     max_mass=1001,
                                     min_rt=1000,
                                     max_rt=1001,
                                     min_ook0=1000,
                                     max_ook0=1001,
                                     min_intensity=1000,
                                     max_intensity=1001,
                                     exclusion=False)
        self.exlist.add(interval)
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_included(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_add_remove2(self):
        interval1 = ExclusionInterval(interval_id='PEPTIDE',
                                      charge=1,
                                      min_mass=1000,
                                      max_mass=1001,
                                      min_rt=1000,
                                      max_rt=1001,
                                      min_ook0=1000,
                                      max_ook0=1001,
                                      min_intensity=1000,
                                      max_intensity=1001,
                                      exclusion=False)
        self.exlist.add(interval1)

        interval2 = ExclusionInterval(interval_id='PEPTIDE',
                                      charge=1,
                                      min_mass=1000,
                                      max_mass=1001,
                                      min_rt=1000,
                                      max_rt=1001,
                                      min_ook0=1000,
                                      max_ook0=1001,
                                      min_intensity=1000,
                                      max_intensity=1001,
                                      exclusion=False)
        self.exlist.add(interval2)
        self.assertEqual(len(self.exlist), 2)

        intervals = self.exlist.query_by_interval(interval1)

        self.exlist.remove_by_uuid(intervals[0].interval_uuid)
        self.assertEqual(len(self.exlist), 1)

        self.exlist.remove(interval1)
        self.assertEqual(len(self.exlist), 0)


if __name__ == '__main__':
    unittest.main()
