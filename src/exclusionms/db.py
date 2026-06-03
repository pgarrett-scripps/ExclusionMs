"""
This module contains the MassIntervalTree class, which is a data structure for
managing ExclusionIntervals. ExclusionIntervals can be added, removed, and queried
by various methods.
"""

import pickle
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Any, List, Generator
from manzanita import IntervalTree

from .components import ExclusionInterval, ExclusionPoint, convert_min_bounds, convert_max_bounds


class IntervalStatus(IntEnum):
    NO_INTERVALS_FOUND = -1
    EXCLUDED = 0
    INCLUDED = 1
    EXCLUDED_INCLUDED = 2


def _mass_bounds(ex_interval: ExclusionInterval):
    """Return (begin, end) mass bounds for use with manzanita IntervalTree."""
    return convert_min_bounds(ex_interval.min_mass), convert_max_bounds(ex_interval.max_mass)


@dataclass
class MassIntervalTree:
    """
    A data structure for managing ExclusionIntervals.

    Attributes:
        interval_tree (IntervalTree): A manzanita interval tree for managing mass intervals.
        id_dict (Dict[str, set]): A dictionary for managing intervals by their ID.
        uuid_dict (Dict[str, ExclusionInterval]): A dictionary for managing intervals by UUID.
    """

    interval_tree: IntervalTree = field(default_factory=IntervalTree)
    id_dict: Dict[str, Dict[str, ExclusionInterval]] = field(default_factory=dict)
    uuid_dict: Dict[str, ExclusionInterval] = field(default_factory=dict)

    def add(self, ex_interval: ExclusionInterval):
        """
           Add an ExclusionInterval to the tree. A Unique UUID will be generated for each valid exclusion interval.

           Args:
               ex_interval (ExclusionInterval): The exclusion interval to be added.

           Raises:
               ValueError: If the interval_id is None.
        """
        if ex_interval.interval_id is None:
            raise ValueError('Cannot add an interval with id = None')

        if ex_interval.interval_uuid is not None and ex_interval.interval_uuid in self.uuid_dict:
            return

        ex_interval.generate_uuid()

        begin, end = _mass_bounds(ex_interval)
        self.interval_tree.addi(begin, end, ex_interval)
        self.id_dict.setdefault(ex_interval.interval_id, {})[ex_interval.interval_uuid] = ex_interval
        self.uuid_dict[ex_interval.interval_uuid] = ex_interval

    def remove(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
            Remove an ExclusionInterval from the tree.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be removed.

            Returns:
                List[ExclusionInterval]: A list of removed exclusion intervals.
        """
        intervals = self._get_interval(ex_interval)

        for interval in intervals:
            begin, end = _mass_bounds(interval)
            self.interval_tree.removei(begin, end, interval)
            self.id_dict[interval.interval_id].pop(interval.interval_uuid, None)
            if len(self.id_dict[interval.interval_id]) == 0:
                self.id_dict.pop(interval.interval_id)
            self.uuid_dict.pop(interval.interval_uuid)

        return intervals

    def remove_by_uuid(self, interval_uuid: str) -> ExclusionInterval:
        """
        Remove an ExclusionInterval from the tree by its UUID.

        Args:
            interval_uuid: uuid of the interval to be removed.

        Returns:
            ExclusionInterval that was removed.
        """
        if interval_uuid not in self.uuid_dict:
            raise ValueError(f'No interval with UUID: {interval_uuid}')

        interval = self.uuid_dict[interval_uuid]
        begin, end = _mass_bounds(interval)
        self.interval_tree.removei(begin, end, interval)
        self.id_dict[interval.interval_id].pop(interval.interval_uuid, None)
        if len(self.id_dict[interval.interval_id]) == 0:
            self.id_dict.pop(interval.interval_id)
        self.uuid_dict.pop(interval.interval_uuid)

        return interval

    def _get_interval(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
            Get intervals based on the given ExclusionInterval.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be used as the search criteria.

            Returns:
                List[ExclusionInterval]: A list of intervals matching the search criteria.
        """
        if ex_interval.interval_id is None:
            return self._get_intervals_by_bounds(ex_interval)
        else:
            candidates = self._get_intervals_by_id(ex_interval.interval_id)
            return [i for i in candidates if i.is_enveloped_by(ex_interval)]

    def _get_intervals_by_bounds(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
        Retrieve intervals enveloped by the given ExclusionInterval based on their mass bounds.

        Args:
            ex_interval (ExclusionInterval): The exclusion interval to be used as the search criteria.

        Returns:
            List[ExclusionInterval]: Intervals enveloped by the given ExclusionInterval.
        """
        begin, end = _mass_bounds(ex_interval)
        mass_intervals = list(self.interval_tree.envelop(begin, end))
        return [iv.data for iv in mass_intervals if iv.data.is_enveloped_by(ex_interval)]

    def _get_intervals_by_id(self, interval_id: Any) -> List[ExclusionInterval]:
        """
        Get intervals based on the given ID.

        Args:
            interval_id (Any): The ID of the intervals to be retrieved.

        Returns:
            List[ExclusionInterval]: A list of intervals matching the given ID.
        """
        if interval_id in self.id_dict:
            return list(self.id_dict[interval_id].values())
        return []

    def is_excluded(self, point: ExclusionPoint) -> bool:
        """
            Check if a point is excluded by any of the exclusion intervals.

            Args:
                point (ExclusionPoint): The point to be checked.

            Returns:
                bool: True if the point is excluded by any of the intervals, False otherwise.
        """
        for _ in self.query_by_point(point):
            if _.exclusion is True:
                return True
        return False

    def is_included(self, point: ExclusionPoint) -> bool:
        """
            Check if a point is included by any of the exclusion intervals.

            Args:
                point (ExclusionPoint): The point to be checked.

            Returns:
                bool: True if the point is included by any of the intervals, False otherwise.
        """
        for _ in self.query_by_point(point):
            if _.exclusion is False:
                return True
        return False

    def point_status(self, point: ExclusionPoint) -> int:
        """
        Check the status of an exclusion point.

        Args:
            point (ExclusionPoint): The point to be checked.

        Returns:
            IntervalStatus: The status of the exclusion point.
        """
        intervals = list(self.query_by_point(point))

        if len(intervals) == 0:
            return IntervalStatus.NO_INTERVALS_FOUND

        exclusion_flags = [interval.exclusion for interval in intervals]

        if all(exclusion_flags):
            return IntervalStatus.EXCLUDED
        if not any(exclusion_flags):
            return IntervalStatus.INCLUDED

        return IntervalStatus.EXCLUDED_INCLUDED

    def query_by_interval(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
            Get a list of exclusion intervals that overlap with the given exclusion interval.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be used as the search criteria.

            Returns:
                List[ExclusionInterval]: A list of exclusion intervals that overlap with the search criteria.
        """
        return self._get_interval(ex_interval)

    def query_by_point(self, point: ExclusionPoint) -> Generator[ExclusionInterval, None, None]:
        """
            Get a generator of exclusion intervals that contain the given point.

            Args:
                point (ExclusionPoint): The point to be used as the search criteria.

            Returns:
                Generator[ExclusionInterval]: Exclusion intervals containing the point.
        """
        if point.mass is None:
            intervals = list(self.interval_tree)
        else:
            intervals = self.interval_tree.at(point.mass)

        return (iv.data for iv in intervals if point.is_bounded_by_quick(iv.data))

    def query_by_id(self, interval_id: Any) -> List[ExclusionInterval]:
        """
            Get a list of exclusion intervals that match the given ID.

            Args:
                interval_id (Any): The ID of the intervals to be retrieved.

            Returns:
                List[ExclusionInterval]: A list of exclusion intervals that match the given ID.
        """
        return self._get_intervals_by_id(interval_id)

    def save(self, file_path: str):
        """
           Save the MassIntervalTree to a file.

           Args:
               file_path (str): The path of the file to be saved.
        """
        intervals = list(self)
        with open(file_path, "wb") as file:
            pickle.dump(intervals, file, -1)

    def load(self, file_path: str) -> None:
        """
            Load the MassIntervalTree from a file.

            Args:
                file_path (str): The path of the file to be loaded.
        """
        with open(file_path, "rb") as file:
            intervals = pickle.load(file)

        self.clear()
        if isinstance(intervals, list):
            # new format: list of ExclusionInterval
            for interval in intervals:
                begin, end = _mass_bounds(interval)
                self.interval_tree.addi(begin, end, interval)
                self.id_dict.setdefault(interval.interval_id, {})[interval.interval_uuid] = interval
                self.uuid_dict[interval.interval_uuid] = interval
        else:
            # legacy format: old intervaltree IntervalTree object
            for iv in intervals:
                interval = iv.data
                begin, end = _mass_bounds(interval)
                self.interval_tree.addi(begin, end, interval)
                self.id_dict.setdefault(interval.interval_id, {})[interval.interval_uuid] = interval
                self.uuid_dict[interval.interval_uuid] = interval

    def clear(self) -> None:
        """
        Clear the MassIntervalTree.
        """
        self.interval_tree.clear()
        self.id_dict = {}
        self.uuid_dict = {}

    def __len__(self):
        """
            Get the number of intervals in the MassIntervalTree.

            Returns:
                int: The number of intervals in the tree.
        """
        return len(self.interval_tree)

    def __iter__(self):
        """
        Iterate over the ExclusionIntervals in the MassIntervalTree.

        Yields:
            ExclusionInterval: The next ExclusionInterval in the tree.
        """
        return iter((iv.data for iv in self.interval_tree))

    def stats(self):
        """
        Get statistics about the MassIntervalTree.

        Returns:
            Dict[str, Any]: A dictionary containing statistics about the tree.
        """
        return {'interval_tree': len(self),
                'id_dict': sum(len(v) for v in self.id_dict.values()),
                'uuid_dict': len(self.uuid_dict),
                'class': str(type(self))}
