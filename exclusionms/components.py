import ast
import sys
from dataclasses import dataclass, asdict
from typing import Union, Dict

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


def convert_min_bounds(min_bound: Union[float, None]) -> float:
    if min_bound is None:
        return sys.float_info.min
    return min_bound


def convert_max_bounds(max_bound: Union[float, None]) -> float:
    if max_bound is None:
        return sys.float_info.max
    return max_bound


def convert_charge(charge: Union[int, None]) -> int:
    if charge is None:
        return 0
    return charge


class ExclusionInterval:
    """
    Represents an interval in the excluded space.

    id: The Id of the interval. Does not have to be unique. If None: Represents all IDs.
    charge: The charge of the excluded interval. If None: the Interval represents all charges
    min_bounds: The lower 'inclusive' bound of the interval. If None: Will be set to sys.float_info.min
    max_bounds: The upper 'exclusive' bound of the interval. If None: Will be set to sys.float_info.max
    """

    def __init__(self,
                 interval_id: Union[str, None],
                 charge: Union[int, None],
                 min_mass: Union[float, None],
                 max_mass: Union[float, None],
                 min_rt: Union[float, None],
                 max_rt: Union[float, None],
                 min_ook0: Union[float, None],
                 max_ook0: Union[float, None],
                 min_intensity: Union[float, None],
                 max_intensity: Union[float, None]
                 ):

        self._interval_id = interval_id
        self._charge = charge
        self._min_mass = min_mass
        self._max_mass = max_mass
        self._min_rt = min_rt
        self._max_rt = max_rt
        self._min_ook0 = min_ook0
        self._max_ook0 = max_ook0
        self._min_intensity = min_intensity
        self._max_intensity = max_intensity

    @property
    def interval_id(self) -> Union[None, str]:
        return self._interval_id

    @interval_id.setter
    def interval_id(self, interval_id: Union[str, None]):
        self._interval_id = interval_id

    @property
    def charge(self) -> Union[int, None]:
        return self._charge

    @charge.setter
    def charge(self, charge: Union[int, None]):
        self._charge = charge

    @property
    def min_mass(self) -> float:
        return convert_min_bounds(self._min_mass)

    @min_mass.setter
    def min_mass(self, min_mass: Union[float, None]):
        self._min_mass = min_mass

    @property
    def max_mass(self) -> float:
        return convert_max_bounds(self._max_mass)

    @max_mass.setter
    def max_mass(self, max_mass: Union[float, None]):
        self._max_mass = max_mass

    @property
    def min_rt(self) -> float:
        return convert_min_bounds(self._min_rt)

    @min_rt.setter
    def min_rt(self, min_rt: Union[float, None]):
        self._min_rt = min_rt

    @property
    def max_rt(self) -> float:
        return convert_max_bounds(self._max_rt)

    @max_rt.setter
    def max_rt(self, max_rt: Union[float, None]):
        self._max_rt = max_rt

    @property
    def min_ook0(self) -> float:
        return convert_min_bounds(self._min_ook0)

    @min_ook0.setter
    def min_ook0(self, min_ook0: Union[float, None]):
        self._min_ook0 = min_ook0

    @property
    def max_ook0(self) -> float:
        return convert_max_bounds(self._max_ook0)

    @max_ook0.setter
    def max_ook0(self, max_ook0: Union[float, None]):
        self._max_ook0 = max_ook0

    @property
    def min_intensity(self) -> float:
        return convert_min_bounds(self._min_intensity)

    @min_intensity.setter
    def min_intensity(self, min_intensity: Union[float, None]):
        self._min_intensity = min_intensity

    @property
    def max_intensity(self) -> float:
        return convert_max_bounds(self._max_intensity)

    @max_intensity.setter
    def max_intensity(self, max_intensity: Union[float, None]):
        self._max_intensity = max_intensity

    def __eq__(self, other: 'ExclusionInterval') -> bool:
        return self.interval_id == other.interval_id and self.charge == other.charge and self.min_mass == other.min_mass and self.max_mass == other.max_mass \
               and self.min_rt == other.min_rt and self.max_rt == other.max_rt and self.min_ook0 == other.min_ook0 and self.max_ook0 == other.max_ook0 \
               and self.min_intensity == other.min_intensity and self.max_intensity == other.max_intensity

    def __str__(self):
        return str(f'interval_id: {self._interval_id}, charge: {self._charge}, min/max mass: {self._min_mass, self._max_mass}, '
                   f'min/max rt: {self._min_rt, self._max_rt}, min/max ook0: {self._min_ook0, self._max_ook0}, '
                   f'min/max intensity: {self._min_intensity, self._max_intensity}')

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
        return {'interval_id': str(self._interval_id),
                'charge': str(self._charge),
                'min_mass': str(self._min_mass),
                'mas_mass': str(self._max_mass),
                'min_rt': str(self._min_rt),
                'max_rt': str(self._max_rt),
                'min_ook0': str(self._min_ook0),
                'max_ook0': str(self._max_ook0),
                'min_intensity': str(self._min_intensity),
                'max_intensity': str(self.max_intensity)
                }

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

        interval_id = parse_str_str(res.get('interval_id'))
        charge = parse_int_str(res.get('charge'))
        min_mass = parse_float_str(res.get('min_mass'))
        max_mass = parse_float_str(res.get('max_mass'))
        min_rt = parse_float_str(res.get('min_rt'))
        max_rt = parse_float_str(res.get('max_rt'))
        min_ook0 = parse_float_str(res.get('min_ook0'))
        max_ook0 = parse_float_str(res.get('max_ook0'))
        min_intensity = parse_float_str(res.get('min_intensity'))
        max_intensity = parse_float_str(res.get('max_intensity'))

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

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

    @staticmethod
    def from_str(serialized_point: str):
        res = ast.literal_eval(serialized_point)
        return ExclusionPoint.from_dict(res)

    @staticmethod
    def from_dict(res: Dict):
        charge = parse_int_str(res.get('charge'))
        mass = parse_float_str(res.get('mass'))
        rt = parse_float_str(res.get('rt'))
        ook0 = parse_float_str(res.get('ook0'))
        intensity = parse_float_str(res.get('intensity'))

        exclusion_point = ExclusionPoint(charge=charge,
                                         mass=mass,
                                         rt=rt,
                                         ook0=ook0,
                                         intensity=intensity,
                                         )
        return exclusion_point


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

        return ExclusionInterval(interval_id=interval_id, charge=charge, min_mass=min_mass,
                                 max_mass=max_mass, min_rt=min_rt, max_rt=max_rt, min_ook0=min_ook0,
                                 max_ook0=max_ook0, min_intensity=min_intensity, max_intensity=max_intensity)


@dataclass
class ExclusionIntervalMsg:
    interval_id: str
    charge: str
    min_mass: str
    max_mass: str
    min_rt: str
    max_rt: str
    min_ook0: str
    max_ook0: str
    min_intensity: str
    max_intensity: str

    def dict(self) -> dict:
        return {k: v for k, v in asdict(self).items()}

    def to_exclusion_interval(self) -> ExclusionInterval:
        return ExclusionInterval.from_dict(self.dict())

    @staticmethod
    def from_exclusion_interval(exclusion_interval: ExclusionInterval) -> 'ExclusionIntervalMsg':
        return ExclusionIntervalMsg(interval_id=str(exclusion_interval._interval_id),
                                    charge=str(exclusion_interval._charge),
                                    min_mass=str(exclusion_interval._min_mass),
                                    max_mass=str(exclusion_interval._max_mass),
                                    min_rt=str(exclusion_interval._min_rt),
                                    max_rt=str(exclusion_interval._max_rt),
                                    min_ook0=str(exclusion_interval._min_ook0),
                                    max_ook0=str(exclusion_interval._max_ook0),
                                    min_intensity=str(exclusion_interval._min_intensity),
                                    max_intensity=str(exclusion_interval._max_intensity),
                                    )


@dataclass
class ExclusionPointMsg:
    charge: str
    mass: str
    rt: str
    ook0: str
    intensity: str

    def dict(self) -> dict:
        return {k: v for k, v in asdict(self).items()}

    def to_exclusion_point(self) -> ExclusionPoint:
        return ExclusionPoint.from_dict(self.dict())

    @staticmethod
    def from_exclusion_point(exclusion_point: ExclusionPoint) -> 'ExclusionPointMsg':
        return ExclusionPointMsg(
            charge=str(exclusion_point.charge),
            mass=str(exclusion_point.mass),
            rt=str(exclusion_point.rt),
            ook0=str(exclusion_point.ook0),
            intensity=str(exclusion_point.intensity),
        )
