"""
This module contains the MassIntervalTree class, which is a data structure for
managing ExclusionIntervals. ExclusionIntervals can be added, removed, and queried
by various methods. This module also provides utility functions for converting
ExclusionIntervals to mass intervals and querying the MassIntervalTree.
"""

import pickle
from dataclasses import dataclass, field
from typing import Dict, Any, List

from intervaltree import IntervalTree, Interval

from .components import ExclusionInterval, ExclusionPoint, convert_min_bounds, convert_max_bounds


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

    def add(self, ex_interval: ExclusionInterval):
        """
           Add an ExclusionInterval to the tree.

           Args:
               ex_interval (ExclusionInterval): The exclusion interval to be added.

           Raises:
               Exception: If the interval_id is None.
        """
        if ex_interval.interval_id is None:
            raise ValueError('Cannot add an interval with id = None')
        mass_interval = get_mass_interval(ex_interval)
        self.interval_tree.add(mass_interval)
        self.id_dict.setdefault(ex_interval.interval_id, set()).add(mass_interval)

    def remove(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
            Remove an ExclusionInterval from the tree.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be removed.

            Returns:
                List[ExclusionInterval]: A list of removed exclusion intervals.
        """
        mass_intervals = self._get_interval(ex_interval)
        if mass_intervals is None:
            return []

        for mass_interval in set(mass_intervals):
            self.interval_tree.remove(mass_interval)

        for mass_interval in mass_intervals:
            self.id_dict[mass_interval.data.interval_id].remove(mass_interval)

        return [mass_interval.data for mass_interval in mass_intervals]

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
            return True
        return False

    def query_by_interval(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """
            Get a list of exclusion intervals that overlap with the given exclusion interval.

            Args:
                ex_interval (ExclusionInterval): The exclusion interval to be used as the search criteria.

            Returns:
                List[ExclusionInterval]: A list of exclusion intervals that overlap with the search criteria.
        """
        return [mass_interval.data for mass_interval in self._get_interval(ex_interval)]

    def query_by_point(self, point: ExclusionPoint) -> List[ExclusionInterval]:
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

        return [interval.data for interval in intervals if point.is_bounded_by(interval.data)]

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
        return {'len': len(self),
                'id_table_len': sum((len(self.id_dict[key]) for key in self.id_dict)),
                'class': str(type(self))}
