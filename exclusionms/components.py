import ast
import random
import sys
from dataclasses import dataclass, asdict
from typing import Union, Dict, List

from .exceptions import IncorrectToleranceException


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


@dataclass
class ExclusionInterval:
    """
    Represents an interval in the excluded space.

    id: The Id of the interval. Does not have to be unique. If None: Represents all IDs.
    charge: The charge of the excluded interval. If None: the Interval represents all charges
    min_bounds: The lower 'inclusive' bound of the interval. If None: Will be set to sys.float_info.min
    max_bounds: The upper 'exclusive' bound of the interval. If None: Will be set to sys.float_info.max
    """
    id: Union[str, None]
    charge: Union[int, None]
    min_mass: Union[float, None]
    max_mass: Union[float, None]
    min_rt: Union[float, None]
    max_rt: Union[float, None]
    min_ook0: Union[float, None]
    max_ook0: Union[float, None]
    min_intensity: Union[float, None]
    max_intensity: Union[float, None]

    def convert_none(self):
        """
        If any bounds are None, set them to either min/max float
        """

        if self.min_mass is None:
            self.min_mass = sys.float_info.min

        if self.max_mass is None:
            self.max_mass = sys.float_info.max

        if self.min_rt is None:
            self.min_rt = sys.float_info.min

        if self.max_rt is None:
            self.max_rt = sys.float_info.max

        if self.min_ook0 is None:
            self.min_ook0 = sys.float_info.min

        if self.max_ook0 is None:
            self.max_ook0 = sys.float_info.max

        if self.min_intensity is None:
            self.min_intensity = sys.float_info.min

        if self.max_intensity is None:
            self.max_intensity = sys.float_info.max

        return self

    def convert_to_none(self):
        """
        If any bounds are None, set them to either min/max float
        """

        if self.min_mass == sys.float_info.min:
            self.min_mass = None

        if self.max_mass == sys.float_info.max:
            self.max_mass = None

        if self.min_rt == sys.float_info.min:
            self.min_rt = None

        if self.max_rt == sys.float_info.max:
            self.max_rt = None

        if self.min_ook0 == sys.float_info.min:
            self.min_ook0 = None

        if self.max_ook0 == sys.float_info.max:
            self.max_ook0 = None

        if self.min_intensity == sys.float_info.min:
            self.min_intensity = None

        if self.max_intensity == sys.float_info.max:
            self.max_intensity = None

        return self

    def is_enveloped_by(self, other: 'ExclusionInterval'):

        if other.charge is not None and self.charge != other.charge:  # data must have correct charge
            return False

        if self.min_mass < other.min_mass or self.max_mass > other.max_mass:
            return False

        if self.min_rt < other.min_rt or self.max_rt > other.max_rt:
            return False

        if self.min_ook0 < other.min_ook0 or self.max_ook0 > other.max_ook0:
            return False

        if self.min_intensity < other.min_intensity or self.max_intensity > other.max_intensity:
            return False

        return True

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

    def is_point(self):
        if self.min_mass != self.max_mass:
            return False
        if self.min_rt != self.max_rt:
            return False
        if self.min_ook0 != self.max_ook0:
            return False
        if self.min_intensity != self.max_intensity:
            return False
        return True

    def is_valid(self):
        if self.min_mass > self.max_mass:
            return False
        if self.min_rt > self.max_rt:
            return False
        if self.min_ook0 > self.max_ook0:
            return False
        if self.min_intensity > self.max_intensity:
            return False
        return True

    @staticmethod
    def from_str(serialized_interval: str):
        res = ast.literal_eval(serialized_interval)
        return ExclusionInterval.from_dict(res)

    @staticmethod
    def from_dict(res: Dict):

        id = parse_str_str(res.get('id'))
        charge = parse_int_str(res.get('charge'))
        min_mass = parse_float_str(res.get('min_mass'))
        max_mass = parse_float_str(res.get('max_mass'))
        min_rt = parse_float_str(res.get('min_rt'))
        max_rt = parse_float_str(res.get('max_rt'))
        min_ook0 = parse_float_str(res.get('min_ook0'))
        max_ook0 = parse_float_str(res.get('max_ook0'))
        min_intensity = parse_float_str(res.get('min_intensity'))
        max_intensity = parse_float_str(res.get('max_intensity'))

        exclusion_interval = ExclusionInterval(id=id,
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




@dataclass()
class ExclusionPoint:
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
        if self.mass is not None and (self.mass < interval.min_mass or self.mass >= interval.max_mass):
            return False
        if self.rt is not None and (self.rt < interval.min_rt or self.rt >= interval.max_rt):
            return False
        if self.ook0 is not None and (self.ook0 < interval.min_ook0 or self.ook0 >= interval.max_ook0):
            return False
        if self.intensity is not None and (self.intensity < interval.min_intensity or
                                           self.intensity >= interval.max_intensity):
            return False
        return True

    @staticmethod
    def generate_random(min_charge: int, max_charge: int, min_mass: float, max_mass: float, min_rt: float,
                        max_rt: float, min_ook0: float, max_ook0: float, min_intensity: float, max_intensity: float):
        charge = random.randint(min_charge, max_charge)
        mass = random.uniform(min_mass, max_mass)
        rt = random.uniform(min_rt, max_rt)
        ook0 = random.uniform(min_ook0, max_ook0)
        intensity = random.uniform(min_intensity, max_intensity)
        return ExclusionPoint(charge=charge, mass=mass, rt=rt, ook0=ook0, intensity=intensity)

    @staticmethod
    def from_str(serialized_point: str):
        res = ast.literal_eval(serialized_point)
        charge = parse_int_str(res.get('charge'))
        mass = parse_float_str(res.get('mass'))
        rt = parse_float_str(res.get('rt'))
        ook0 = parse_float_str(res.get('ook0'))
        intensity = parse_float_str(res.get('intensity'))
        exclusion_point = ExclusionPoint(charge=charge,
                                         mass=mass,
                                         rt=rt,
                                         ook0=ook0,
                                         intensity=intensity)
        return exclusion_point

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class DynamicExclusionTolerance:
    exact_charge: bool
    mass_tolerance: Union[float, None]
    rt_tolerance: Union[float, None]
    ook0_tolerance: Union[float, None]
    intensity_tolerance: Union[float, None]

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

    @staticmethod
    def from_tolerance_dict(tolerance_dict: dict) -> 'DynamicExclusionTolerance':
        exact_charge = parse_bool_str(tolerance_dict.get('exact_charge'))
        if exact_charge is None:
            raise ValueError(f'exact charge cannot be None!')
        return DynamicExclusionTolerance(
            exact_charge=exact_charge,
            mass_tolerance=parse_float_str(tolerance_dict.get('mass')),
            rt_tolerance=parse_float_str(tolerance_dict.get('rt')),
            ook0_tolerance=parse_float_str(tolerance_dict.get('ook0')),
            intensity_tolerance=parse_float_str(tolerance_dict.get('intensity'))
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
            min_intensity = intensity - self.intensity_tolerance
            max_intensity = intensity + self.intensity_tolerance
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

        return ExclusionInterval(id=interval_id, charge=charge, min_mass=min_mass,
                                 max_mass=max_mass, min_rt=min_rt, max_rt=max_rt, min_ook0=min_ook0,
                                 max_ook0=max_ook0, min_intensity=min_intensity, max_intensity=max_intensity)
