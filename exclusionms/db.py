import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List

from intervaltree import IntervalTree, Interval

from .components import ExclusionInterval, ExclusionPoint


@dataclass
class ExclusionList(ABC):

    @abstractmethod
    def add(self, interval: ExclusionInterval):
        """
        adds an interval to the list
        :param interval:
        :return: None
        """
        pass

    @abstractmethod
    def remove(self, interval: ExclusionInterval):
        """
        removes intervals from the list
        :param interval:
        :return: None
        """
        pass

    @abstractmethod
    def query_by_interval(self, interval: ExclusionInterval) -> List[ExclusionInterval]:
        pass

    @abstractmethod
    def query_by_point(self, point: ExclusionPoint) -> List[ExclusionInterval]:
        pass

    @abstractmethod
    def query_by_id(self, interval_id: Any) -> List[ExclusionInterval]:
        pass

    @abstractmethod
    def is_excluded(self, point: ExclusionPoint) -> bool:
        pass

    @abstractmethod
    def save(self, file_path: str):
        pass

    @abstractmethod
    def load(self, file_path: str):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def __len__(self):
        pass


@dataclass
class MassIntervalTree(ExclusionList):
    """
    ExclusionList store excluded intervals. Excluded intervals or stored in a 1D IntervalTree based on mass.
    Therefore, only a single interval can be stored for each unique mass interval, adding another interval
    with the same underlying mass interval will override the stored object
    """

    interval_tree: IntervalTree = field(default_factory=lambda: IntervalTree())
    id_dict: Dict[str, list] = field(default_factory=lambda: dict())

    def add(self, ex_interval: ExclusionInterval):
        if ex_interval.interval_id is None:
            raise Exception('Cannot add an interval with id = None')
        mass_interval = Interval(ex_interval.min_mass, ex_interval.max_mass, ex_interval)
        self.interval_tree.add(mass_interval)
        self.id_dict.setdefault(ex_interval.interval_id, []).append(mass_interval)

    def remove(self, ex_interval: ExclusionInterval) -> list[ExclusionInterval]:
        mass_intervals = self._get_interval(ex_interval)
        if mass_intervals is None:
            return []

        for mass_interval in set(mass_intervals):
            self.interval_tree.remove(mass_interval)

        for mass_interval in mass_intervals:
            self.id_dict[mass_interval.data.interval_id].remove(mass_interval)

        return [mass_interval.data for mass_interval in mass_intervals]

    def _get_interval(self, ex_interval: ExclusionInterval) -> List[Interval]:
        if ex_interval.interval_id is None:
            # retrieve intervals by bounds
            mass_intervals = self._get_intervals_by_bounds(ex_interval)
        else:
            # retrieve intervals by id
            mass_intervals = self._get_intervals_by_id(ex_interval.interval_id)
            mass_intervals = [i for i in mass_intervals if i.data.is_enveloped_by(ex_interval)]

        return mass_intervals

    def _get_intervals_by_bounds(self, ex_interval: ExclusionInterval) -> List[Interval]:
        intervals = self.interval_tree.envelop(Interval(ex_interval.min_mass, ex_interval.max_mass, ex_interval))
        intervals = [i for i in intervals if i.data.is_enveloped_by(ex_interval)]
        return intervals

    def _get_intervals_by_id(self, interval_id: Any) -> List[Interval]:
        intervals = self.id_dict.get(interval_id)
        if intervals is None:
            return []
        return intervals

    def is_excluded(self, point: ExclusionPoint) -> bool:
        return len(self.query_by_point(point)) > 0

    def query_by_interval(self, ex_interval: ExclusionInterval) -> List[ExclusionInterval]:
        return [mass_interval.data for mass_interval in self._get_interval(ex_interval)]

    def query_by_point(self, point: ExclusionPoint) -> List[ExclusionInterval]:
        if point.mass is None:
            intervals = [interval for interval in self.interval_tree]
        else:
            intervals = self.interval_tree[point.mass]

        return [interval.data for interval in intervals if point.is_bounded_by(interval.data)]

    def query_by_id(self, interval_id: Any) -> List[ExclusionInterval]:
        return [interval.data for interval in self._get_intervals_by_id(interval_id)]

    def save(self, file_path: str):
        """
        Save a the interval tree as a pickled obj
        """
        with open(file_path, "wb") as file:
            pickle.dump(self.interval_tree, file, -1)

    def load(self, file_path: str) -> None:
        """
        Loads a pickled interval tree and then populates id_dict
        """
        with open(file_path, "rb") as file:
            self.interval_tree = pickle.load(file)
            self.id_dict = {}
            for interval in self.interval_tree:
                data = interval.data
                self.id_dict.setdefault(data.interval_id, []).append(interval)

    def clear(self) -> None:
        """
        Clears all data
        """
        self.interval_tree.clear()
        self.id_dict = {}

    def __len__(self):
        return len(self.interval_tree)

    def stats(self):
        return {'len': len(self), 'id_table_len': sum([len(self.id_dict[key]) for key in self.id_dict]), 'class': str(type(self))}
