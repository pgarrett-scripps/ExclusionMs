from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Union, Dict

from .exceptions import IncorrectToleranceException
from pydantic import BaseModel


def parse_float_str(val: str) -> Union[float, None]:
    if type(val) == str:
        if val == '':
            val = None
        elif str.lower(val) == 'none':
            val = None
        else:
            try:
                val = float(val)
            except ValueError:
                pass

    elif type(val) == int:
        val = float(val)

    if type(val) != float and val is not None:
        raise IncorrectToleranceException(f'val: {val} cannot be parsed into float.')
    return val


def parse_int_str(val: str) -> Union[int, None]:
    if type(val) == str:
        if val == '':
            val = None
        elif str.lower(val) == 'none':
            val = None
        else:
            try:
                val = int(val)
            except ValueError:
                pass
    if type(val) != int and val is not None:
        raise IncorrectToleranceException(f'val: {val} cannot be parsed into int.')
    return val


def parse_str_str(val: str) -> Union[str, None]:
    if type(val) == str:
        if val == '':
            val = None
        elif str.lower(val) == 'none':
            val = None
    if type(val) != str and val is not None:
        raise IncorrectToleranceException(f'val: {val} cannot be parsed into str.')
    return val


def parse_bool_str(val: str) -> Union[bool, None]:
    if type(val) == str:
        if val == '':
            val = None
        elif str.lower(val) == 'none':
            val = None
        elif str.lower(val) == 'true':
            val = True
        elif str.lower(val) == 'false':
            val = False

    if type(val) != bool and val is not None:
        raise IncorrectToleranceException(f'val: {val} cannot be parsed into bool.')

    return val


def convert_min_bounds(min_bound: Union[float, None]) -> float:
    if min_bound is None:
        return -sys.float_info.max
    return min_bound


def convert_max_bounds(max_bound: Union[float, None]) -> float:
    if max_bound is None:
        return sys.float_info.max
    return max_bound


def convert_charge(charge: Union[int, None]) -> int:
    if charge is None:
        return 0
    return charge


# TODO: Use StrEnum in pyton 3.11
class IntervalKey(Enum):
    INTERVAL_ID = 'interval_id'
    CHARGE = 'charge'
    MIN_MASS = 'min_mass'
    MAX_MASS = 'max_mass'
    MIN_RT = 'min_rt'
    MAX_RT = 'max_rt'
    MIN_OOK0 = 'min_ook0'
    MAX_OOK0 = 'max_ook0'
    MIN_INTENSITY = 'min_intensity'
    MAX_INTENSITY = 'max_intensity'

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

    def is_enveloped_by(self, other: 'ExclusionInterval'):

        if other.charge is not None and self.charge is not None and self.charge != other.charge:  # data must have correct charge
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

    def is_valid(self):
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
    def from_str(serialized_interval: str):
        res = ast.literal_eval(serialized_interval)
        return ExclusionInterval.from_dict(res)

    @staticmethod
    def from_dict(res: Dict):

        interval_id = parse_str_str(res.get(IntervalKey.INTERVAL_ID.value))
        charge = parse_int_str(res.get(IntervalKey.CHARGE.value))
        min_mass = parse_float_str(res.get(IntervalKey.MIN_MASS.value))
        max_mass = parse_float_str(res.get(IntervalKey.MAX_MASS.value))
        min_rt = parse_float_str(res.get(IntervalKey.MIN_RT.value))
        max_rt = parse_float_str(res.get(IntervalKey.MAX_RT.value))
        min_ook0 = parse_float_str(res.get(IntervalKey.MIN_OOK0.value))
        max_ook0 = parse_float_str(res.get(IntervalKey.MAX_OOK0.value))
        min_intensity = parse_float_str(res.get(IntervalKey.MIN_INTENSITY.value))
        max_intensity = parse_float_str(res.get(IntervalKey.MAX_INTENSITY.value))

        exclusion_interval = ExclusionInterval(interval_id=interval_id,
                                               charge=charge,
                                               min_mass=min_mass,
                                               max_mass=max_mass,
                                               min_rt=min_rt,
                                               max_rt=max_rt,
                                               min_ook0=min_ook0,
                                               max_ook0=max_ook0,
                                               min_intensity=min_intensity,
                                               max_intensity=max_intensity
                                               )
        return exclusion_interval


# TODO: Use StrEnum in pyton 3.11
class PointKey(Enum):
    CHARGE = 'charge'
    MASS = 'mass'
    RT = 'rt'
    OOK0 = 'ook0'
    INTENSITY = 'intensity'


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
        if self.mass is not None and (self.mass < convert_min_bounds(interval.min_mass) or
                                      self.mass >= convert_max_bounds(interval.max_mass)):
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

        return True

    @staticmethod
    def from_str(serialized_point: str):
        res = ast.literal_eval(serialized_point)
        return ExclusionPoint.from_dict(res)

    @staticmethod
    def from_dict(res: Dict):
        charge = parse_int_str(res.get(PointKey.CHARGE.value))
        mass = parse_float_str(res.get(PointKey.MASS.value))
        rt = parse_float_str(res.get(PointKey.RT.value))
        ook0 = parse_float_str(res.get(PointKey.OOK0.value))
        intensity = parse_float_str(res.get(PointKey.INTENSITY.value))

        exclusion_point = ExclusionPoint(charge=charge,
                                         mass=mass,
                                         rt=rt,
                                         ook0=ook0,
                                         intensity=intensity,
                                         )
        return exclusion_point


# TODO: Use StrEnum in pyton 3.11
class ToleranceKey(Enum):
    EXACT_CHARGE = 'exact_charge'
    MASS = 'mass'
    RT = 'rt'
    OOK0 = 'ook0'
    INTENSITY = 'intensity'


@dataclass
class DynamicExclusionTolerance:
    exact_charge: bool
    mass_tolerance: Union[float, None]
    rt_tolerance: Union[float, None]
    ook0_tolerance: Union[float, None]
    intensity_tolerance: Union[float, None]

    def dict(self):
        return {ToleranceKey.EXACT_CHARGE.value: 'true' if self.exact_charge == True else 'false',
                ToleranceKey.MASS.value: str(self.mass_tolerance) if self.mass_tolerance else '',
                ToleranceKey.RT.value: str(self.rt_tolerance) if self.rt_tolerance else '',
                ToleranceKey.OOK0.value: str(self.ook0_tolerance) if self.ook0_tolerance else '',
                ToleranceKey.INTENSITY.value: str(self.intensity_tolerance) if self.intensity_tolerance else ''}

    @staticmethod
    def from_tolerance_dict(tolerance_dict: dict) -> 'DynamicExclusionTolerance':
        exact_charge = parse_bool_str(tolerance_dict.get(ToleranceKey.EXACT_CHARGE.value))
        if exact_charge is None:
            raise ValueError(f'exact charge cannot be None!')
        return DynamicExclusionTolerance(
            exact_charge=exact_charge,
            mass_tolerance=parse_float_str(tolerance_dict.get(ToleranceKey.MASS.value)),
            rt_tolerance=parse_float_str(tolerance_dict.get(ToleranceKey.RT.value)),
            ook0_tolerance=parse_float_str(tolerance_dict.get(ToleranceKey.OOK0.value)),
            intensity_tolerance=parse_float_str(tolerance_dict.get(ToleranceKey.INTENSITY.value))
        )

    @staticmethod
    def from_strings(exact_charge: str, mass_tolerance: str, rt_tolerance: str, ook0_tolerance: str,
                     intensity_tolerance: str) -> 'DynamicExclusionTolerance':
        exact_charge = parse_bool_str(exact_charge)
        if exact_charge is None:
            raise ValueError(f'exact charge cannot be None!')
        return DynamicExclusionTolerance(
            exact_charge=exact_charge,
            mass_tolerance=parse_float_str(mass_tolerance),
            rt_tolerance=parse_float_str(rt_tolerance),
            ook0_tolerance=parse_float_str(ook0_tolerance),
            intensity_tolerance=parse_float_str(intensity_tolerance)
        )

    def calculate_mass_bounds(self, mass: Union[float, None]):
        if self.mass_tolerance and mass:
            min_mass = mass - mass * self.mass_tolerance / 1_000_000
            max_mass = mass + mass * self.mass_tolerance / 1_000_000
            return min_mass, max_mass
        return None, None

    def calculate_rt_bounds(self, rt: Union[float, None]):
        if self.rt_tolerance and rt:
            min_rt = rt - self.rt_tolerance
            max_rt = rt + self.rt_tolerance
            return min_rt, max_rt
        return None, None

    def calculate_ook0_bounds(self, ook0: Union[float, None]):
        if self.ook0_tolerance and ook0:
            min_ook0 = ook0 - self.ook0_tolerance
            max_ook0 = ook0 + self.ook0_tolerance
            return min_ook0, max_ook0
        return None, None

    def calculate_intensity_bounds(self, intensity: Union[float, None]):
        if self.intensity_tolerance and intensity:
            min_intensity = intensity - intensity * self.intensity_tolerance
            max_intensity = intensity + intensity * self.intensity_tolerance
            return min_intensity, max_intensity
        return None, None

    def construct_interval(self, interval_id: str, exclusion_point: ExclusionPoint):

        charge = exclusion_point.charge
        if self.exact_charge is False:
            charge = None

        min_mass, max_mass = self.calculate_mass_bounds(exclusion_point.mass)
        min_rt, max_rt = self.calculate_rt_bounds(exclusion_point.rt)
        min_ook0, max_ook0 = self.calculate_ook0_bounds(exclusion_point.ook0)
        min_intensity, max_intensity = self.calculate_intensity_bounds(exclusion_point.intensity)

        return ExclusionInterval(interval_id=interval_id, charge=charge, min_mass=min_mass,
                                 max_mass=max_mass, min_rt=min_rt, max_rt=max_rt, min_ook0=min_ook0,
                                 max_ook0=max_ook0, min_intensity=min_intensity, max_intensity=max_intensity)