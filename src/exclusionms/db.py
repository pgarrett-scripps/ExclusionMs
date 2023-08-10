"""
This module contains the MassIntervalTree class, which is a data structure for
managing ExclusionIntervals. ExclusionIntervals can be added, removed, and queried
by various methods. This module also provides utility functions for converting
ExclusionIntervals to mass intervals and querying the MassIntervalTree.
"""

import pickle
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Any, List, Generator
from intervaltree import IntervalTree, Interval

from .components import ExclusionInterval, ExclusionPoint, convert_min_bounds, convert_max_bounds


class IntervalStatus(IntEnum):
    NO_INTERVALS_FOUND = -1
    EXCLUDED = 0
    INCLUDED = 1
    EXCLUDED_INCLUDED = 2


def get_mass_interval(ex_interval: ExclusionInterval):
    """
    Convert an ExclusionInterval into a IntervalTree interval based on the exclusion intervals mass bounds.

    Args:
        ex_interval (ExclusionInterval): The exclusion interval to be converted.

    Returns:
        Interval: IntervalTree Interval
    """
    return Interval(convert_min_bounds(ex_interval.min_mass),
                    convert_max_bounds(ex_interval.max_mass),
                    ex_interval)


@dataclass
class MassIntervalTree:
    """
    A data structure for managing ExclusionIntervals.

    Attributes:
        interval_tree (IntervalTree): An interval tree for managing mass intervals.
        id_dict (Dict[str, set]): A dictionary for managing intervals by their ID.
    """

    interval_tree: IntervalTree = field(default_factory=IntervalTree)
    id_dict: Dict[str, set] = field(default_factory=dict)
    uuid_dict: Dict[str, ExclusionInterval] = field(default_factory=dict)

    def add(self, ex_interval: ExclusionInterval):
        """
           Add an ExclusionInterval to the tree. A Unique UUID will be generated for each valid exclusion interval.


           Args:
               ex_interval (ExclusionInterval): The exclusion interval to be added.

           Raises:
               Exception: If the interval_id is None.
        """
        if ex_interval.interval_id is None:
            raise ValueError('Cannot add an interval with id = None')

        ex_interval.generate_uuid()

        mass_interval = get_mass_interval(ex_interval)
        self.interval_tree.add(mass_interval)
        self.id_dict.setdefault(ex_interval.interval_id, set()).add(mass_interval)
        self.uuid_dict[ex_interval.interval_uuid] = ex_interval

    def remove(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
            Remove an ExclusionInterval from the tree.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be removed.

            Returns:
                List[ExclusionInterval]: A list of removed exclusion intervals.
        """
        mass_intervals = self._get_interval(ex_interval)
        intervals = [mass_interval.data for mass_interval in mass_intervals]

        if mass_intervals is None:
            return []

        for mass_interval in set(mass_intervals):
            self.interval_tree.remove(mass_interval)

        for mass_interval in mass_intervals:
            self.id_dict[mass_interval.data.interval_id].remove(mass_interval)
            if len(self.id_dict[mass_interval.data.interval_id]) == 0:
                self.id_dict.pop(mass_interval.data.interval_id)

        for interval in intervals:
            self.uuid_dict.pop(interval.interval_uuid)

        return intervals

    def remove_by_uuid(self, interval_uuid: str) -> ExclusionInterval:
        """
        Remove an ExclusionInterval from the tree by its UUID.
        :param interval_uuid: uuid of the interval to be removed.
        :return: Exclusion interval that was removed
        """

        if interval_uuid not in self.uuid_dict:
            raise ValueError(f'No interval with UUID: {interval_uuid}')

        interval = self.uuid_dict[interval_uuid]
        mass_interval = get_mass_interval(interval)
        self.interval_tree.remove(mass_interval)
        self.id_dict[interval.interval_id].remove(mass_interval)
        if len(self.id_dict[interval.interval_id]) == 0:
            self.id_dict.pop(interval.interval_id)
        self.uuid_dict.pop(interval.interval_uuid)

        return interval

    def _get_interval(self, ex_interval: ExclusionInterval) -> List[Interval]:
        """
            Get intervals based on the given ExclusionInterval.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be used as the search criteria.

            Returns:
                List[Interval]: A list of intervals matching the search criteria.
        """
        if ex_interval.interval_id is None:
            # retrieve intervals by bounds
            mass_intervals = self._get_intervals_by_bounds(ex_interval)
        else:
            # retrieve intervals by id
            mass_intervals = self._get_intervals_by_id(ex_interval.interval_id)
            mass_intervals = [i for i in mass_intervals if i.data.is_enveloped_by(ex_interval)]

        return mass_intervals

    def _get_intervals_by_bounds(self, ex_interval: ExclusionInterval) -> List[Interval]:
        """
        Retrieve the intervals that are enveloped by the given ExclusionInterval based on their mass bounds.

        Args:
            ex_interval (ExclusionInterval): The exclusion interval to be used as the search criteria.

        Returns:
            List[Interval]: A list of Interval objects that are enveloped by the given ExclusionInterval based on their
             mass bounds.
        """
        intervals = self.interval_tree.envelop(get_mass_interval(ex_interval))
        intervals = [i for i in intervals if i.data.is_enveloped_by(ex_interval)]
        return intervals

    def _get_intervals_by_id(self, interval_id: Any) -> List[Interval]:
        """
        Get intervals based on the given ID.

        Args:
            interval_id (Any): The ID of the intervals to be retrieved.

        Returns:
            List[Interval]: A list of intervals matching the given ID.
        """
        if interval_id in self.id_dict:
            return list(self.id_dict[interval_id])
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
                bool: True if the point is excluded by any of the intervals, False otherwise.
        """
        for _ in self.query_by_point(point):
            if _.exclusion is False:
                return True
        return False

    def point_status(self, point: ExclusionPoint) -> int:
        """
        Check the status of an exclusion point.

        0 - No intervals found
        1 - excluded
        2 - included
        3 - excluded + included

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
        return [mass_interval.data for mass_interval in self._get_interval(ex_interval)]

    def query_by_point(self, point: ExclusionPoint) -> Generator[ExclusionInterval, None, None]:
        """
            Get a list of exclusion intervals that exclude the given point.

            Args:
                point (ExclusionPoint): The point to be used as the search criteria.

            Returns:
                List[ExclusionInterval]: A list of exclusion intervals that exclude the search criteria.
        """
        if point.mass is None:
            intervals = list(self.interval_tree)
        else:
            intervals = self.interval_tree[point.mass]

        return (interval.data for interval in intervals if point.is_bounded_by_quick(interval.data))

    def query_by_id(self, interval_id: Any) -> List[ExclusionInterval]:
        """
            Get a list of exclusion intervals that match the given ID.

            Args:
                interval_id (Any): The ID of the intervals to be retrieved.

            Returns:
                List[ExclusionInterval]: A list of exclusion intervals that match the given ID.
        """
        return [interval.data for interval in self._get_intervals_by_id(interval_id)]

    def save(self, file_path: str):
        """
           Save the MassIntervalTree to a file.

           Args:
               file_path (str): The path of the file to be saved.
        """
        with open(file_path, "wb") as file:
            pickle.dump(self.interval_tree, file, -1)

    def load(self, file_path: str) -> None:
        """
            Load the MassIntervalTree from a file.

            Args:
                file_path (str): The path of the file to be loaded.
        """
        with open(file_path, "rb") as file:
            self.interval_tree = pickle.load(file)
            self.id_dict = {}
            for interval in self.interval_tree:
                data = interval.data
                self.id_dict.setdefault(data.interval_id, set()).add(interval)

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
        return iter((interval.data for interval in self.interval_tree))

    def stats(self):
        """
        Get statistics about the MassIntervalTree.

        Returns:
            Dict[str, Any]: A dictionary containing statistics about the tree.
        """
        return {'interval_tree': len(self),
                'id_dict': sum((len(self.id_dict[key]) for key in self.id_dict)),
                'uuid_dict': len(self.uuid_dict),
                'class': str(type(self))}
