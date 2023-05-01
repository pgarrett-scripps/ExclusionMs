import ast
import random
import sys
import uuid
from typing import Union, Dict, Tuple, Any
from pydantic import BaseModel


def convert_min_bounds(min_bound: Union[float, None]) -> float:
    if min_bound is None:
        return -sys.float_info.max
    return min_bound


def convert_max_bounds(max_bound: Union[float, None]) -> float:
    if max_bound is None:
        return sys.float_info.max
    return max_bound


class ExclusionInterval(BaseModel):
    """
    Represents an interval in the excluded space.

    id: The id of the interval. Does not have to be unique. If None: Represents all IDs.
    charge: The charge of the excluded interval. If None: the Interval represents all charges
    min_bounds: The lower 'inclusive' bound of the interval. If None: Will be set to sys.float_info.min
    max_bounds: The upper 'exclusive' bound of the interval. If None: Will be set to sys.float_info.max
    """
    interval_id: Union[str, None]
    charge: Union[int, None]
    min_mass: Union[float, None]
    max_mass: Union[float, None]
    min_rt: Union[float, None]
    max_rt: Union[float, None]
    min_ook0: Union[float, None]
    max_ook0: Union[float, None]
    min_intensity: Union[float, None]
    max_intensity: Union[float, None]
    data: Any = None

    def is_enveloped_by(self, other: 'ExclusionInterval') -> bool:

        if other.charge is not None and self.charge is not None and self.charge != other.charge:
            return False

        if convert_min_bounds(self.min_mass) < convert_min_bounds(other.min_mass) or \
                convert_max_bounds(self.max_mass) > convert_max_bounds(other.max_mass):
            return False

        if convert_min_bounds(self.min_rt) < convert_min_bounds(other.min_rt) or \
                convert_max_bounds(self.max_rt) > convert_max_bounds(other.max_rt):
            return False

        if convert_min_bounds(self.min_ook0) < convert_min_bounds(other.min_ook0) or \
                convert_max_bounds(self.max_ook0) > convert_max_bounds(other.max_ook0):
            return False

        if convert_min_bounds(self.min_intensity) < convert_min_bounds(other.min_intensity) or \
                convert_max_bounds(self.max_intensity) > convert_max_bounds(other.max_intensity):
            return False

        return True

    def to_dict_rounded(self) -> Dict[str, Union[str, int, float]]:
        return {
            'interval_id': self.interval_id if self.interval_id is not None else None,
            'charge': self.charge if self.charge is not None else None,
            'min_mass': round(self.min_mass, 4) if self.min_mass is not None else None,
            'max_mass': round(self.max_mass, 4) if self.max_mass is not None else None,
            'min_rt': round(self.min_rt, 2) if self.min_rt is not None else None,
            'max_rt': round(self.max_rt, 2) if self.max_rt is not None else None,
            'min_ook0': round(self.min_ook0, 2) if self.min_ook0 is not None else None,
            'max_ook0': round(self.max_ook0, 2) if self.max_ook0 is not None else None,
            'min_intensity': round(self.min_intensity, 2) if self.min_intensity is not None else None,
            'max_intensity': round(self.max_intensity, 2) if self.max_intensity is not None else None,
        }

    def is_valid(self) -> bool:
        if convert_min_bounds(self.min_mass) > convert_max_bounds(self.max_mass):
            return False
        if convert_min_bounds(self.min_rt) > convert_max_bounds(self.max_rt):
            return False
        if convert_min_bounds(self.min_ook0) > convert_max_bounds(self.max_ook0):
            return False
        if convert_min_bounds(self.min_intensity) > convert_max_bounds(self.max_intensity):
            return False
        return True

    @staticmethod
    def from_str(serialized_interval: str) -> 'ExclusionInterval':
        res = ast.literal_eval(serialized_interval)
        return ExclusionInterval.from_dict(res)

    @staticmethod
    def from_dict(res: Dict) -> 'ExclusionInterval':
        exclusion_interval = ExclusionInterval(**res)
        return exclusion_interval

    def contains_point(self, point: 'ExclusionPoint') -> bool:
        """
        Check if point given by is_excluded() is within interval
        """
        return point.is_bounded_by(interval=self)


class ExclusionPoint(BaseModel):
    """
    Represents a point in the excluded space. None values will be ignored.
    """
    charge: Union[int, None]
    mass: Union[float, None]
    rt: Union[float, None]
    ook0: Union[float, None]
    intensity: Union[float, None]

    def is_bounded_by(self, interval: ExclusionInterval) -> bool:
        """
        Check if point given by is_excluded() is within interval
        """
        if self.charge is not None and interval.charge is not None and self.charge != interval.charge:
            return False

        if self.rt is not None and (self.rt < convert_min_bounds(interval.min_rt) or
                                    self.rt >= convert_max_bounds(interval.max_rt)):
            return False

        if self.ook0 is not None and (self.ook0 < convert_min_bounds(interval.min_ook0) or
                                      self.ook0 >= convert_max_bounds(interval.max_ook0)):
            return False

        if self.intensity is not None and (self.intensity < convert_min_bounds(interval.min_intensity) or
                                           self.intensity >= convert_max_bounds(interval.max_intensity)):
            return False

        if self.mass is not None and (self.mass < convert_min_bounds(interval.min_mass) or
                                      self.mass >= convert_max_bounds(interval.max_mass)):
            return False

        return True

    @staticmethod
    def from_str(serialized_point: str) -> 'ExclusionPoint':
        res = ast.literal_eval(serialized_point)
        return ExclusionPoint.from_dict(res)

    @staticmethod
    def from_dict(res: Dict) -> 'ExclusionPoint':
        return ExclusionPoint(**res)


class DynamicExclusionTolerance(BaseModel):
    charge: bool
    mass: Union[float, None]
    rt: Union[float, None]
    ook0: Union[float, None]
    intensity: Union[float, None]

    @staticmethod
    def from_str(serialized_tolerance: str) -> 'DynamicExclusionTolerance':
        res = ast.literal_eval(serialized_tolerance)
        return DynamicExclusionTolerance.from_dict(res)

    @staticmethod
    def from_dict(res: dict) -> 'DynamicExclusionTolerance':
        return DynamicExclusionTolerance(**res)

    def calculate_mass_bounds(self, mass: Union[float, None]) -> Tuple:
        if self.mass and mass:
            min_mass = mass - mass * self.mass / 1_000_000
            max_mass = mass + mass * self.mass / 1_000_000
            return min_mass, max_mass
        return None, None

    def calculate_rt_bounds(self, rt: Union[float, None]) -> Tuple:
        if self.rt and rt:
            min_rt = rt - self.rt
            max_rt = rt + self.rt
            return min_rt, max_rt
        return None, None

    def calculate_ook0_bounds(self, ook0: Union[float, None]) -> Tuple:
        if self.ook0 and ook0:
            min_ook0 = ook0 - self.ook0
            max_ook0 = ook0 + self.ook0
            return min_ook0, max_ook0
        return None, None

    def calculate_intensity_bounds(self, intensity: Union[float, None]) -> Tuple:
        if self.intensity and intensity:
            min_intensity = intensity - intensity * self.intensity
            max_intensity = intensity + intensity * self.intensity
            return min_intensity, max_intensity
        return None, None

    def construct_interval(self, interval_id: str, exclusion_point: ExclusionPoint) -> ExclusionInterval:

        charge = exclusion_point.charge
        if self.charge is False:
            charge = None

        min_mass, max_mass = self.calculate_mass_bounds(exclusion_point.mass)
        min_rt, max_rt = self.calculate_rt_bounds(exclusion_point.rt)
        min_ook0, max_ook0 = self.calculate_ook0_bounds(exclusion_point.ook0)
        min_intensity, max_intensity = self.calculate_intensity_bounds(exclusion_point.intensity)

        return ExclusionInterval(interval_id=interval_id, charge=charge, min_mass=min_mass,
                                 max_mass=max_mass, min_rt=min_rt, max_rt=max_rt, min_ook0=min_ook0,
                                 max_ook0=max_ook0, min_intensity=min_intensity, max_intensity=max_intensity)
