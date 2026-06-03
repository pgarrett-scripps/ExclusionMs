"""
Expanded tests for MassIntervalTree (manzanita-backed).
Covers boundary semantics, None handling, multi-interval interactions,
stats/clear, large-scale behaviour, and edge cases.
"""
import os
import tempfile
import unittest
from copy import deepcopy

from exclusionms.components import ExclusionInterval, ExclusionPoint, DynamicExclusionTolerance
from exclusionms.db import MassIntervalTree, IntervalStatus


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_interval(
    interval_id='P',
    charge=1,
    min_mass=1000.0, max_mass=1001.0,
    min_rt=10.0, max_rt=20.0,
    min_ook0=0.5, max_ook0=1.5,
    min_intensity=1e4, max_intensity=1e6,
    exclusion=True,
    data=None,
):
    return ExclusionInterval(
        interval_id=interval_id, charge=charge,
        min_mass=min_mass, max_mass=max_mass,
        min_rt=min_rt, max_rt=max_rt,
        min_ook0=min_ook0, max_ook0=max_ook0,
        min_intensity=min_intensity, max_intensity=max_intensity,
        exclusion=exclusion, data=data,
    )


def make_point(charge=1, mass=1000.5, rt=15.0, ook0=1.0, intensity=5e4):
    return ExclusionPoint(charge=charge, mass=mass, rt=rt, ook0=ook0, intensity=intensity)


# ---------------------------------------------------------------------------
# 1. Add / remove
# ---------------------------------------------------------------------------

class TestAddRemove(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_add_single(self):
        self.tree.add(make_interval())
        self.assertEqual(len(self.tree), 1)

    def test_add_increments_all_dicts(self):
        iv = make_interval()
        self.tree.add(iv)
        stats = self.tree.stats()
        self.assertEqual(stats['interval_tree'], 1)
        self.assertEqual(stats['id_dict'], 1)
        self.assertEqual(stats['uuid_dict'], 1)

    def test_add_none_id_raises(self):
        with self.assertRaises(ValueError):
            self.tree.add(make_interval(interval_id=None))

    def test_add_generates_uuid(self):
        iv = make_interval()
        self.assertIsNone(iv.interval_uuid)
        self.tree.add(iv)
        self.assertIsNotNone(iv.interval_uuid)

    def test_duplicate_add_ignored(self):
        iv = make_interval()
        self.tree.add(iv)
        self.tree.add(iv)
        self.assertEqual(len(self.tree), 1)

    def test_add_two_distinct_intervals(self):
        self.tree.add(make_interval(interval_id='A', min_mass=100, max_mass=200))
        self.tree.add(make_interval(interval_id='B', min_mass=300, max_mass=400))
        self.assertEqual(len(self.tree), 2)

    def test_add_same_id_different_bounds(self):
        self.tree.add(make_interval(interval_id='P', min_mass=100, max_mass=200))
        self.tree.add(make_interval(interval_id='P', min_mass=300, max_mass=400))
        self.assertEqual(len(self.tree), 2)
        self.assertEqual(len(self.tree.query_by_id('P')), 2)

    def test_remove_by_id(self):
        iv = make_interval()
        self.tree.add(iv)
        self.tree.remove(iv)
        self.assertEqual(len(self.tree), 0)

    def test_remove_nonexistent_returns_empty(self):
        result = self.tree.remove(make_interval())
        self.assertEqual(result, [])

    def test_remove_by_uuid(self):
        iv = make_interval()
        self.tree.add(iv)
        self.tree.remove_by_uuid(iv.interval_uuid)
        self.assertEqual(len(self.tree), 0)
        self.assertEqual(len(self.tree.id_dict), 0)
        self.assertEqual(len(self.tree.uuid_dict), 0)

    def test_remove_by_uuid_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.tree.remove_by_uuid('nonexistent-uuid')

    def test_remove_cleans_id_dict(self):
        iv = make_interval()
        self.tree.add(iv)
        self.tree.remove(iv)
        self.assertNotIn('P', self.tree.id_dict)

    def test_remove_one_of_two_same_id(self):
        iv1 = make_interval(interval_id='P', min_mass=100, max_mass=200)
        iv2 = make_interval(interval_id='P', min_mass=300, max_mass=400)
        self.tree.add(iv1)
        self.tree.add(iv2)
        self.tree.remove_by_uuid(iv1.interval_uuid)
        self.assertEqual(len(self.tree), 1)
        self.assertIn('P', self.tree.id_dict)

    def test_remove_by_bounds(self):
        iv = make_interval()
        self.tree.add(iv)
        query = ExclusionInterval(
            interval_id=None, charge=1,
            min_mass=1000, max_mass=1001,
            min_rt=10, max_rt=20,
            min_ook0=0.5, max_ook0=1.5,
            min_intensity=1e4, max_intensity=1e6,
        )
        removed = self.tree.remove(query)
        self.assertEqual(len(removed), 1)
        self.assertEqual(len(self.tree), 0)

    def test_remove_returns_removed_intervals(self):
        iv = make_interval()
        self.tree.add(iv)
        removed = self.tree.remove(iv)
        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0], iv)


# ---------------------------------------------------------------------------
# 2. Point exclusion – boundary semantics
# ---------------------------------------------------------------------------

class TestBoundarySemantics(unittest.TestCase):
    """Lower bounds are inclusive, upper bounds are exclusive."""

    def setUp(self):
        self.tree = MassIntervalTree()
        self.tree.add(make_interval(
            min_mass=1000.0, max_mass=1001.0,
            min_rt=10.0, max_rt=20.0,
            min_ook0=0.5, max_ook0=1.5,
            min_intensity=1e4, max_intensity=1e6,
        ))

    # mass
    def test_mass_lower_inclusive(self):
        self.assertTrue(self.tree.is_excluded(make_point(mass=1000.0)))

    def test_mass_upper_exclusive(self):
        self.assertFalse(self.tree.is_excluded(make_point(mass=1001.0)))

    def test_mass_middle(self):
        self.assertTrue(self.tree.is_excluded(make_point(mass=1000.5)))

    def test_mass_below_lower(self):
        self.assertFalse(self.tree.is_excluded(make_point(mass=999.999)))

    def test_mass_above_upper(self):
        self.assertFalse(self.tree.is_excluded(make_point(mass=1001.001)))

    # rt
    def test_rt_lower_inclusive(self):
        self.assertTrue(self.tree.is_excluded(make_point(rt=10.0)))

    def test_rt_upper_exclusive(self):
        self.assertFalse(self.tree.is_excluded(make_point(rt=20.0)))

    def test_rt_below(self):
        self.assertFalse(self.tree.is_excluded(make_point(rt=9.999)))

    def test_rt_above(self):
        self.assertFalse(self.tree.is_excluded(make_point(rt=20.001)))

    # ook0
    def test_ook0_lower_inclusive(self):
        self.assertTrue(self.tree.is_excluded(make_point(ook0=0.5)))

    def test_ook0_upper_exclusive(self):
        self.assertFalse(self.tree.is_excluded(make_point(ook0=1.5)))

    # intensity
    def test_intensity_lower_inclusive(self):
        self.assertTrue(self.tree.is_excluded(make_point(intensity=1e4)))

    def test_intensity_upper_exclusive(self):
        self.assertFalse(self.tree.is_excluded(make_point(intensity=1e6)))

    # charge
    def test_wrong_charge_not_excluded(self):
        self.assertFalse(self.tree.is_excluded(make_point(charge=2)))

    def test_correct_charge_excluded(self):
        self.assertTrue(self.tree.is_excluded(make_point(charge=1)))


# ---------------------------------------------------------------------------
# 3. None handling in intervals
# ---------------------------------------------------------------------------

class TestNoneIntervalBounds(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_none_mass_bounds_match_any_mass(self):
        self.tree.add(make_interval(min_mass=None, max_mass=None, charge=None,
                                    min_rt=None, max_rt=None, min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertTrue(self.tree.is_excluded(make_point(mass=0)))
        self.assertTrue(self.tree.is_excluded(make_point(mass=1e9)))
        self.assertTrue(self.tree.is_excluded(make_point(mass=-1e9)))

    def test_none_rt_bounds_match_any_rt(self):
        self.tree.add(make_interval(min_rt=None, max_rt=None, charge=None,
                                    min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertTrue(self.tree.is_excluded(make_point(rt=0)))
        self.assertTrue(self.tree.is_excluded(make_point(rt=1e9)))

    def test_none_charge_matches_any_charge(self):
        self.tree.add(make_interval(charge=None, min_rt=None, max_rt=None,
                                    min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertTrue(self.tree.is_excluded(make_point(charge=1)))
        self.assertTrue(self.tree.is_excluded(make_point(charge=99)))

    def test_none_ook0_bounds_match_any_ook0(self):
        self.tree.add(make_interval(charge=None, min_rt=None, max_rt=None,
                                    min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertTrue(self.tree.is_excluded(make_point(ook0=0)))
        self.assertTrue(self.tree.is_excluded(make_point(ook0=100)))

    def test_none_intensity_bounds_match_any_intensity(self):
        self.tree.add(make_interval(charge=None, min_rt=None, max_rt=None,
                                    min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertTrue(self.tree.is_excluded(make_point(intensity=0)))
        self.assertTrue(self.tree.is_excluded(make_point(intensity=1e15)))

    def test_partial_none_mass_lower_only(self):
        self.tree.add(make_interval(min_mass=None, max_mass=1500.0, charge=None,
                                    min_rt=None, max_rt=None, min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertTrue(self.tree.is_excluded(make_point(mass=-1000.0)))
        self.assertTrue(self.tree.is_excluded(make_point(mass=1000.0)))
        self.assertFalse(self.tree.is_excluded(make_point(mass=1500.0)))

    def test_partial_none_mass_upper_only(self):
        self.tree.add(make_interval(min_mass=500.0, max_mass=None, charge=None,
                                    min_rt=None, max_rt=None, min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        self.assertFalse(self.tree.is_excluded(make_point(mass=499.0)))
        self.assertTrue(self.tree.is_excluded(make_point(mass=500.0)))
        self.assertTrue(self.tree.is_excluded(make_point(mass=1e9)))


# ---------------------------------------------------------------------------
# 4. None handling in points
# ---------------------------------------------------------------------------

class TestNonePointFields(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()
        self.tree.add(make_interval())

    def test_none_charge_bypasses_charge_check(self):
        self.assertTrue(self.tree.is_excluded(make_point(charge=None)))

    def test_none_mass_queries_all_intervals(self):
        self.assertTrue(self.tree.is_excluded(make_point(mass=None)))

    def test_none_rt_bypasses_rt_check(self):
        self.assertTrue(self.tree.is_excluded(make_point(rt=None)))

    def test_none_ook0_bypasses_ook0_check(self):
        self.assertTrue(self.tree.is_excluded(make_point(ook0=None)))

    def test_none_intensity_bypasses_intensity_check(self):
        self.assertTrue(self.tree.is_excluded(make_point(intensity=None)))

    def test_all_none_point_matches_specific_interval(self):
        p = ExclusionPoint(charge=None, mass=None, rt=None, ook0=None, intensity=None)
        self.assertTrue(self.tree.is_excluded(p))

    def test_none_mass_point_matches_interval_with_none_mass(self):
        self.tree.clear()
        self.tree.add(make_interval(min_mass=None, max_mass=None, charge=None,
                                    min_rt=None, max_rt=None, min_ook0=None, max_ook0=None,
                                    min_intensity=None, max_intensity=None))
        p = ExclusionPoint(charge=None, mass=None, rt=None, ook0=None, intensity=None)
        self.assertTrue(self.tree.is_excluded(p))


# ---------------------------------------------------------------------------
# 5. IntervalStatus / point_status
# ---------------------------------------------------------------------------

class TestPointStatus(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_no_intervals(self):
        self.assertEqual(self.tree.point_status(make_point()), IntervalStatus.NO_INTERVALS_FOUND)

    def test_excluded_only(self):
        self.tree.add(make_interval(exclusion=True))
        self.assertEqual(self.tree.point_status(make_point()), IntervalStatus.EXCLUDED)

    def test_included_only(self):
        self.tree.add(make_interval(exclusion=False))
        self.assertEqual(self.tree.point_status(make_point()), IntervalStatus.INCLUDED)

    def test_mixed_status(self):
        self.tree.add(make_interval(interval_id='A', exclusion=True))
        self.tree.add(make_interval(interval_id='B', exclusion=False))
        self.assertEqual(self.tree.point_status(make_point()), IntervalStatus.EXCLUDED_INCLUDED)

    def test_no_match_outside_mass(self):
        self.tree.add(make_interval())
        self.assertEqual(
            self.tree.point_status(make_point(mass=9999.0)),
            IntervalStatus.NO_INTERVALS_FOUND,
        )

    def test_status_enum_values(self):
        self.assertEqual(IntervalStatus.NO_INTERVALS_FOUND, -1)
        self.assertEqual(IntervalStatus.EXCLUDED, 0)
        self.assertEqual(IntervalStatus.INCLUDED, 1)
        self.assertEqual(IntervalStatus.EXCLUDED_INCLUDED, 2)

    def test_is_excluded_true(self):
        self.tree.add(make_interval(exclusion=True))
        self.assertTrue(self.tree.is_excluded(make_point()))

    def test_is_excluded_false_when_no_match(self):
        self.tree.add(make_interval(exclusion=True))
        self.assertFalse(self.tree.is_excluded(make_point(mass=9999.0)))

    def test_is_included_true(self):
        self.tree.add(make_interval(exclusion=False))
        self.assertTrue(self.tree.is_included(make_point()))

    def test_is_included_false_when_exclusion_only(self):
        self.tree.add(make_interval(exclusion=True))
        self.assertFalse(self.tree.is_included(make_point()))

    def test_is_excluded_false_when_inclusion_only(self):
        self.tree.add(make_interval(exclusion=False))
        self.assertFalse(self.tree.is_excluded(make_point()))


# ---------------------------------------------------------------------------
# 6. query_by_point
# ---------------------------------------------------------------------------

class TestQueryByPoint(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_returns_matching_interval(self):
        iv = make_interval()
        self.tree.add(iv)
        results = list(self.tree.query_by_point(make_point()))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], iv)

    def test_returns_empty_for_no_match(self):
        self.tree.add(make_interval())
        results = list(self.tree.query_by_point(make_point(mass=9999.0)))
        self.assertEqual(len(results), 0)

    def test_returns_multiple_matching(self):
        self.tree.add(make_interval(interval_id='A'))
        self.tree.add(make_interval(interval_id='B'))
        results = list(self.tree.query_by_point(make_point()))
        self.assertEqual(len(results), 2)

    def test_overlapping_intervals_both_returned(self):
        self.tree.add(make_interval(interval_id='A', min_mass=900, max_mass=1100))
        self.tree.add(make_interval(interval_id='B', min_mass=950, max_mass=1050))
        results = list(self.tree.query_by_point(make_point(mass=1000.0)))
        self.assertEqual(len(results), 2)

    def test_non_overlapping_intervals_correct_one_returned(self):
        self.tree.add(make_interval(interval_id='A', min_mass=100, max_mass=200))
        self.tree.add(make_interval(interval_id='B', min_mass=800, max_mass=1200))
        results = list(self.tree.query_by_point(make_point(mass=150.0)))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].interval_id, 'A')

    def test_none_mass_point_matches_all_intervals(self):
        self.tree.add(make_interval(interval_id='A', min_mass=100, max_mass=200))
        self.tree.add(make_interval(interval_id='B', min_mass=800, max_mass=1200))
        results = list(self.tree.query_by_point(ExclusionPoint(charge=None, mass=None, rt=None, ook0=None, intensity=None)))
        self.assertEqual(len(results), 2)


# ---------------------------------------------------------------------------
# 7. query_by_interval
# ---------------------------------------------------------------------------

class TestQueryByInterval(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_query_returns_enveloped_interval(self):
        iv = make_interval()
        self.tree.add(iv)
        query = ExclusionInterval(
            interval_id=None, charge=None,
            min_mass=900, max_mass=1100,
            min_rt=None, max_rt=None,
            min_ook0=None, max_ook0=None,
            min_intensity=None, max_intensity=None,
        )
        results = self.tree.query_by_interval(query)
        self.assertEqual(len(results), 1)

    def test_query_none_bounds_returns_all(self):
        self.tree.add(make_interval(interval_id='A'))
        self.tree.add(make_interval(interval_id='B', min_mass=2000, max_mass=3000))
        query = ExclusionInterval(
            interval_id=None, charge=None,
            min_mass=None, max_mass=None,
            min_rt=None, max_rt=None,
            min_ook0=None, max_ook0=None,
            min_intensity=None, max_intensity=None,
        )
        results = self.tree.query_by_interval(query)
        self.assertEqual(len(results), 2)

    def test_query_too_narrow_returns_empty(self):
        self.tree.add(make_interval(min_mass=1000, max_mass=1001))
        query = ExclusionInterval(
            interval_id=None, charge=None,
            min_mass=1000.3, max_mass=1000.7,
            min_rt=None, max_rt=None,
            min_ook0=None, max_ook0=None,
            min_intensity=None, max_intensity=None,
        )
        results = self.tree.query_by_interval(query)
        self.assertEqual(len(results), 0)

    def test_query_by_id_returns_matching(self):
        iv = make_interval(interval_id='TARGET')
        self.tree.add(iv)
        self.tree.add(make_interval(interval_id='OTHER', min_mass=5000, max_mass=6000))
        results = self.tree.query_by_id('TARGET')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].interval_id, 'TARGET')

    def test_query_by_id_missing_returns_empty(self):
        results = self.tree.query_by_id('MISSING')
        self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# 8. Stats and clear
# ---------------------------------------------------------------------------

class TestStatsAndClear(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_stats_empty(self):
        s = self.tree.stats()
        self.assertEqual(s['interval_tree'], 0)
        self.assertEqual(s['id_dict'], 0)
        self.assertEqual(s['uuid_dict'], 0)

    def test_stats_after_add(self):
        self.tree.add(make_interval(interval_id='A'))
        self.tree.add(make_interval(interval_id='B', min_mass=2000, max_mass=3000))
        s = self.tree.stats()
        self.assertEqual(s['interval_tree'], 2)
        self.assertEqual(s['id_dict'], 2)
        self.assertEqual(s['uuid_dict'], 2)

    def test_stats_same_id(self):
        self.tree.add(make_interval(interval_id='P', min_mass=100, max_mass=200))
        self.tree.add(make_interval(interval_id='P', min_mass=300, max_mass=400))
        s = self.tree.stats()
        self.assertEqual(s['id_dict'], 2)

    def test_clear_resets_all(self):
        self.tree.add(make_interval())
        self.tree.clear()
        self.assertEqual(len(self.tree), 0)
        self.assertEqual(len(self.tree.id_dict), 0)
        self.assertEqual(len(self.tree.uuid_dict), 0)

    def test_clear_then_readd(self):
        iv = make_interval()
        self.tree.add(iv)
        self.tree.clear()
        iv2 = make_interval()
        self.tree.add(iv2)
        self.assertEqual(len(self.tree), 1)

    def test_len_empty(self):
        self.assertEqual(len(self.tree), 0)

    def test_len_after_adds(self):
        for i in range(10):
            self.tree.add(make_interval(interval_id=str(i), min_mass=i * 100, max_mass=i * 100 + 50))
        self.assertEqual(len(self.tree), 10)

    def test_iter(self):
        iv = make_interval()
        self.tree.add(iv)
        items = list(self.tree)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], iv)

    def test_stats_class_key(self):
        s = self.tree.stats()
        self.assertIn('class', s)


# ---------------------------------------------------------------------------
# 9. Save / load
# ---------------------------------------------------------------------------

class TestSaveLoad(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_save_load_roundtrip(self):
        iv = make_interval()
        self.tree.add(iv)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            path = f.name
        try:
            self.tree.save(path)
            t2 = MassIntervalTree()
            t2.load(path)
            self.assertEqual(len(t2), 1)
            self.assertEqual(list(t2)[0], iv)
        finally:
            os.unlink(path)

    def test_save_load_query_works(self):
        self.tree.add(make_interval())
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            path = f.name
        try:
            self.tree.save(path)
            t2 = MassIntervalTree()
            t2.load(path)
            self.assertTrue(t2.is_excluded(make_point()))
        finally:
            os.unlink(path)

    def test_save_load_multiple_intervals(self):
        for i in range(5):
            self.tree.add(make_interval(interval_id=str(i), min_mass=i * 100, max_mass=i * 100 + 50))
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            path = f.name
        try:
            self.tree.save(path)
            t2 = MassIntervalTree()
            t2.load(path)
            self.assertEqual(len(t2), 5)
            s = t2.stats()
            self.assertEqual(s['id_dict'], 5)
            self.assertEqual(s['uuid_dict'], 5)
        finally:
            os.unlink(path)

    def test_load_rebuilds_id_dict(self):
        self.tree.add(make_interval(interval_id='PEPT'))
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            path = f.name
        try:
            self.tree.save(path)
            t2 = MassIntervalTree()
            t2.load(path)
            results = t2.query_by_id('PEPT')
            self.assertEqual(len(results), 1)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 10. Inclusion intervals
# ---------------------------------------------------------------------------

class TestInclusionIntervals(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_inclusion_interval_not_excluded(self):
        self.tree.add(make_interval(exclusion=False))
        self.assertFalse(self.tree.is_excluded(make_point()))

    def test_inclusion_interval_is_included(self):
        self.tree.add(make_interval(exclusion=False))
        self.assertTrue(self.tree.is_included(make_point()))

    def test_exclusion_not_included(self):
        self.tree.add(make_interval(exclusion=True))
        self.assertFalse(self.tree.is_included(make_point()))

    def test_mixed_both_flags(self):
        self.tree.add(make_interval(interval_id='A', exclusion=True))
        self.tree.add(make_interval(interval_id='B', exclusion=False))
        self.assertTrue(self.tree.is_excluded(make_point()))
        self.assertTrue(self.tree.is_included(make_point()))


# ---------------------------------------------------------------------------
# 11. Data field on intervals
# ---------------------------------------------------------------------------

class TestDataField(unittest.TestCase):

    def setUp(self):
        self.tree = MassIntervalTree()

    def test_string_data_preserved(self):
        iv = make_interval(data='hello')
        self.tree.add(iv)
        results = list(self.tree.query_by_point(make_point()))
        self.assertEqual(results[0].data, 'hello')

    def test_dict_data_preserved(self):
        iv = make_interval(data={'key': 'value', 'count': 42})
        self.tree.add(iv)
        results = list(self.tree.query_by_point(make_point()))
        self.assertEqual(results[0].data['key'], 'value')
        self.assertEqual(results[0].data['count'], 42)

    def test_list_data_preserved(self):
        iv = make_interval(data=[1, 2, 3])
        self.tree.add(iv)
        results = list(self.tree.query_by_point(make_point()))
        self.assertEqual(results[0].data, [1, 2, 3])

    def test_none_data(self):
        iv = make_interval(data=None)
        self.tree.add(iv)
        results = list(self.tree.query_by_point(make_point()))
        self.assertIsNone(results[0].data)

    def test_data_survives_save_load(self):
        iv = make_interval(data={'score': 99})
        self.tree.add(iv)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            path = f.name
        try:
            self.tree.save(path)
            t2 = MassIntervalTree()
            t2.load(path)
            results = list(t2.query_by_point(make_point()))
            self.assertEqual(results[0].data['score'], 99)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 12. Large-scale / stress tests
# ---------------------------------------------------------------------------

class TestLargeScale(unittest.TestCase):

    def test_add_many_non_overlapping(self):
        tree = MassIntervalTree()
        n = 500
        for i in range(n):
            tree.add(make_interval(
                interval_id=str(i),
                min_mass=float(i * 10),
                max_mass=float(i * 10 + 5),
            ))
        self.assertEqual(len(tree), n)

    def test_query_in_large_tree(self):
        tree = MassIntervalTree()
        for i in range(500):
            tree.add(make_interval(
                interval_id=str(i),
                min_mass=float(i * 10),
                max_mass=float(i * 10 + 5),
                min_rt=None, max_rt=None,
                min_ook0=None, max_ook0=None,
                min_intensity=None, max_intensity=None,
                charge=None,
            ))
        # The interval at index 250 covers mass [2500, 2505)
        results = list(tree.query_by_point(ExclusionPoint(
            charge=None, mass=2502.0, rt=None, ook0=None, intensity=None,
        )))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].interval_id, '250')

    def test_bulk_remove_by_uuid(self):
        tree = MassIntervalTree()
        intervals = []
        for i in range(100):
            iv = make_interval(interval_id=str(i), min_mass=float(i * 10), max_mass=float(i * 10 + 5))
            tree.add(iv)
            intervals.append(iv)
        for iv in intervals:
            tree.remove_by_uuid(iv.interval_uuid)
        self.assertEqual(len(tree), 0)
        self.assertEqual(len(tree.id_dict), 0)
        self.assertEqual(len(tree.uuid_dict), 0)

    def test_clear_large_tree(self):
        tree = MassIntervalTree()
        for i in range(200):
            tree.add(make_interval(interval_id=str(i), min_mass=float(i), max_mass=float(i + 1)))
        tree.clear()
        self.assertEqual(len(tree), 0)


# ---------------------------------------------------------------------------
# 13. DynamicExclusionTolerance integration
# ---------------------------------------------------------------------------

class TestDynamicExclusionTolerance(unittest.TestCase):

    def test_construct_interval_adds_to_tree(self):
        tol = DynamicExclusionTolerance(
            charge=True, mass=10.0, rt=30.0, ook0=0.05, intensity=None
        )
        point = ExclusionPoint(charge=2, mass=1000.0, rt=60.0, ook0=1.0, intensity=None)
        iv = tol.construct_interval('TEST', point)
        tree = MassIntervalTree()
        tree.add(iv)
        self.assertEqual(len(tree), 1)
        self.assertTrue(tree.is_excluded(point))

    def test_mass_ppm_tolerance(self):
        tol = DynamicExclusionTolerance(
            charge=True, mass=10.0, rt=None, ook0=None, intensity=None
        )
        point = ExclusionPoint(charge=1, mass=1000.0, rt=None, ook0=None, intensity=None)
        iv = tol.construct_interval('TEST', point)
        # 10 ppm of 1000 = 0.01 Da
        self.assertAlmostEqual(iv.min_mass, 999.99, places=4)
        self.assertAlmostEqual(iv.max_mass, 1000.01, places=4)

    def test_tolerance_produces_exclusion_true(self):
        tol = DynamicExclusionTolerance(charge=True, mass=5.0, rt=10.0, ook0=None, intensity=None)
        point = ExclusionPoint(charge=1, mass=500.0, rt=100.0, ook0=None, intensity=None)
        iv = tol.construct_interval('TEST', point)
        self.assertTrue(iv.exclusion)


# ---------------------------------------------------------------------------
# 14. Consistency checks across id_dict / uuid_dict / interval_tree
# ---------------------------------------------------------------------------

class TestInternalConsistency(unittest.TestCase):

    def _assert_consistent(self, tree):
        """All three data structures must agree on count."""
        tree_len = len(tree.interval_tree)
        uuid_len = len(tree.uuid_dict)
        id_total = sum(len(v) for v in tree.id_dict.values())
        self.assertEqual(tree_len, uuid_len, "interval_tree vs uuid_dict mismatch")
        self.assertEqual(tree_len, id_total, "interval_tree vs id_dict mismatch")

    def test_consistent_after_adds(self):
        tree = MassIntervalTree()
        for i in range(20):
            tree.add(make_interval(interval_id=str(i % 5), min_mass=float(i * 10), max_mass=float(i * 10 + 5)))
        self._assert_consistent(tree)

    def test_consistent_after_removes(self):
        tree = MassIntervalTree()
        ivs = []
        for i in range(10):
            iv = make_interval(interval_id=str(i), min_mass=float(i * 10), max_mass=float(i * 10 + 5))
            tree.add(iv)
            ivs.append(iv)
        for iv in ivs[:5]:
            tree.remove(iv)
        self._assert_consistent(tree)

    def test_consistent_after_remove_by_uuid(self):
        tree = MassIntervalTree()
        ivs = []
        for i in range(10):
            iv = make_interval(interval_id=str(i), min_mass=float(i * 10), max_mass=float(i * 10 + 5))
            tree.add(iv)
            ivs.append(iv)
        for iv in ivs[5:]:
            tree.remove_by_uuid(iv.interval_uuid)
        self._assert_consistent(tree)

    def test_consistent_after_clear(self):
        tree = MassIntervalTree()
        for i in range(10):
            tree.add(make_interval(interval_id=str(i), min_mass=float(i * 10), max_mass=float(i * 10 + 5)))
        tree.clear()
        self._assert_consistent(tree)

    def test_consistent_after_save_load(self):
        tree = MassIntervalTree()
        for i in range(5):
            tree.add(make_interval(interval_id=str(i), min_mass=float(i * 10), max_mass=float(i * 10 + 5)))
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            path = f.name
        try:
            tree.save(path)
            t2 = MassIntervalTree()
            t2.load(path)
            self._assert_consistent(t2)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
