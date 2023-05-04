"""
The exclusion module provides classes to define and work with exclusion intervals, points, and tolerances
in a multidimensional space. These classes can be used to represent and manipulate excluded regions
in the context of data analysis and filtering.

Classes included in this module:

- ExclusionInterval: Represents an n-dimensional interval, defined by minimum and maximum bounds
  for charge, mass, retention time (rt), ook0, and intensity properties.

- ExclusionPoint: Represents a point in the excluded multidimensional space. Each dimension corresponds
  to a property such as charge, mass, retention time (rt), ook0, and intensity.

- DynamicExclusionTolerance: Represents a dynamic exclusion tolerance, which can be used to calculate bounds
  for exclusion intervals based on an ExclusionPoint. The class provides methods for calculating the bounds
  for mass, retention time (rt), ook0, and intensity properties, as well as constructing an ExclusionInterval
  based on the calculated bounds.

These classes provide methods for creating instances from serialized strings or dictionaries, checking
if points are bounded by intervals, and constructing new intervals based on dynamic exclusion tolerances.
"""


import ast
import sys
from typing import Union, Dict, Tuple, Any
from pydantic import BaseModel


def convert_min_bounds(min_bound: Union[float, None]) -> float:
    """
    Convert the minimum bound value to a float.

    If `min_bound` is None, returns the smallest negative finite float value
    representable by the system (i.e. -sys.float_info.max).
    Otherwise, returns `min_bound` as a float.

    Parameters:
        min_bound (Union[float, None]): The minimum bound value to convert.

    Returns:
        float: The minimum bound value as a float.
    """
    if min_bound is None:
        return float('-inf')
    return min_bound


def convert_max_bounds(max_bound: Union[float, None]) -> float:
    """
    Convert the maximum bound value to a float.

    If `max_bound` is None, returns the largest positive finite float value
    representable by the system (i.e. sys.float_info.max).
    Otherwise, returns `max_bound` as a float.

    Parameters:
        max_bound (Union[float, None]): The maximum bound value to convert.

    Returns:
        float: The maximum bound value as a float.
    """
    if max_bound is None:
        return float('inf')
    return max_bound


class ExclusionInterval(BaseModel):
    """
    ExclusionInterval represents an interval in a multidimensional space defined by several properties.
    These properties include mass, retention time (rt), ook0, intensity, and charge. The class provides
    methods for checking whether a given ExclusionInterval is enveloped by another, creating an instance
    from a dictionary or a string, and validating the interval's properties.
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
        """
        Check if the current ExclusionInterval is enveloped by another given ExclusionInterval.

        :param other: Another ExclusionInterval instance to compare with.
        :return: True if the current interval is enveloped by the other interval, False otherwise.
        """
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
        """
        Convert the ExclusionInterval to a dictionary with its properties rounded.

        :return: A dictionary containing the interval's properties with values rounded.
        """
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
        """
        Check if the ExclusionInterval is valid, i.e., the lower bounds are not greater than the upper bounds.

        :return: True if the interval is valid, False otherwise.
        """
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
        """
        Create an ExclusionInterval instance from a serialized string.

        :param serialized_interval: A string containing the serialized representation of an ExclusionInterval.
        :return: An ExclusionInterval instance.
        """
        res = ast.literal_eval(serialized_interval)
        return ExclusionInterval.from_dict(res)

    @staticmethod
    def from_dict(res: Dict) -> 'ExclusionInterval':
        """
        Create an ExclusionInterval instance from a dictionary.

        :param res: A dictionary containing the ExclusionInterval properties.
        :return: An ExclusionInterval instance.
        """
        exclusion_interval = ExclusionInterval(**res)
        return exclusion_interval

    def contains_point(self, point: 'ExclusionPoint') -> bool:
        """
        Check if the given ExclusionPoint is contained within the current ExclusionInterval.

        :param point: An ExclusionPoint instance to check.
        :return: True if the point is contained within the interval, False otherwise.
        """
        return point.is_bounded_by(interval=self)


class ExclusionPoint(BaseModel):
    """
    Represents a point in the excluded multidimensional space. Each dimension corresponds to a property
    such as charge, mass, retention time (rt), ook0, and intensity. None values for a property will be
    ignored during comparisons with ExclusionInterval objects. ExclusionPoint provides methods to check
    whether the point is bounded by a given ExclusionInterval and to create an instance from a serialized
    string or dictionary.
    """
    charge: Union[int, None]
    mass: Union[float, None]
    rt: Union[float, None]
    ook0: Union[float, None]
    intensity: Union[float, None]

    def is_bounded_by(self, interval: ExclusionInterval) -> bool:
        """
        Check if the ExclusionPoint is within the given ExclusionInterval.

        :param interval: An ExclusionInterval instance to check against.
        :return: True if the point is within the interval, False otherwise.
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
        """
        Create an ExclusionPoint instance from a serialized string.

        :param serialized_point: A string containing the serialized representation of an ExclusionPoint.
        :return: An ExclusionPoint instance.
        """
        res = ast.literal_eval(serialized_point)
        return ExclusionPoint.from_dict(res)

    @staticmethod
    def from_dict(res: Dict) -> 'ExclusionPoint':
        """
        Create an ExclusionPoint instance from a dictionary.

        :param res: A dictionary containing the ExclusionPoint properties.
        :return: An ExclusionPoint instance.
        """
        return ExclusionPoint(**res)


class DynamicExclusionTolerance(BaseModel):
    """
    Represents a dynamic exclusion tolerance which can be used to calculate bounds for exclusion intervals
    based on an ExclusionPoint. The class provides methods for calculating the bounds for mass, retention
    time (rt), ook0, and intensity properties, as well as constructing an ExclusionInterval based on the
    calculated bounds.
    """
    charge: bool
    mass: Union[float, None]
    rt: Union[float, None]
    ook0: Union[float, None]
    intensity: Union[float, None]

    @staticmethod
    def from_str(serialized_tolerance: str) -> 'DynamicExclusionTolerance':
        """
        Create a DynamicExclusionTolerance instance from a serialized string.

        :param serialized_tolerance: A string containing the serialized representation of a DynamicExclusionTolerance.
        :return: A DynamicExclusionTolerance instance.
        """
        res = ast.literal_eval(serialized_tolerance)
        return DynamicExclusionTolerance.from_dict(res)

    @staticmethod
    def from_dict(res: dict) -> 'DynamicExclusionTolerance':
        """
        Create a DynamicExclusionTolerance instance from a dictionary.

        :param res: A dictionary containing the DynamicExclusionTolerance properties.
        :return: A DynamicExclusionTolerance instance.
        """
        return DynamicExclusionTolerance(**res)

    def calculate_mass_bounds(self, mass: Union[float, None]) -> Tuple:
        """
        Calculate the mass bounds based on the given mass and the tolerance's mass property.

        :param mass: The mass of the ExclusionPoint.
        :return: A tuple containing the minimum and maximum mass bounds.
        """
        if self.mass and mass:
            min_mass = mass - mass * self.mass / 1_000_000
            max_mass = mass + mass * self.mass / 1_000_000
            return min_mass, max_mass
        return None, None

    def calculate_rt_bounds(self, rt: Union[float, None]) -> Tuple:
        """
        Calculate the retention time (rt) bounds based on the given rt and the tolerance's rt property.

        :param rt: The retention time of the ExclusionPoint.
        :return: A tuple containing the minimum and maximum rt bounds.
        """
        if self.rt and rt:
            min_rt = rt - self.rt
            max_rt = rt + self.rt
            return min_rt, max_rt
        return None, None

    def calculate_ook0_bounds(self, ook0: Union[float, None]) -> Tuple:
        """
        Calculate the ook0 bounds based on the given ook0 and the tolerance's ook0 property.

        :param ook0: The ook0 of the ExclusionPoint.
        :return: A tuple containing the minimum and maximum ook0 bounds.
        """
        if self.ook0 and ook0:
            min_ook0 = ook0 - self.ook0
            max_ook0 = ook0 + self.ook0
            return min_ook0, max_ook0
        return None, None

    def calculate_intensity_bounds(self, intensity: Union[float, None]) -> Tuple:
        """
        Calculate the intensity bounds based on the given intensity and the tolerance's intensity property.

        :param intensity: The intensity of the ExclusionPoint.
        :return: A tuple containing the minimum and maximum intensity bounds.
        """
        if self.intensity and intensity:
            min_intensity = intensity - intensity * self.intensity
            max_intensity = intensity + intensity * self.intensity
            return min_intensity, max_intensity
        return None, None

    def construct_interval(self, interval_id: str, exclusion_point: ExclusionPoint) -> ExclusionInterval:
        """
        Construct an ExclusionInterval based on the calculated bounds and the given ExclusionPoint.

        :param interval_id: The interval ID to be assigned to the new ExclusionInterval.
        :param exclusion_point: An ExclusionPoint instance used to calculate the bounds.
        :return: An ExclusionInterval instance with the calculated bounds.
        """
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
