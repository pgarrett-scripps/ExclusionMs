import random
import uuid
from typing import Tuple

from exclusionms.components import DynamicExclusionTolerance, ExclusionPoint, ExclusionInterval


def generate_random_point(charge_range: Tuple[int, int] = None,
                          mass_range: Tuple[float, float] = None,
                          rt_range: Tuple[float, float] = None,
                          ook0_range: Tuple[float, float] = None,
                          intensity_range: Tuple[float, float] = None) -> ExclusionPoint:
    """
    Generate a random ExclusionPoint with the specified attribute ranges.

    :param charge_range: Tuple of min and max charge, inclusive. If not provided, charge is set to None.
    :param mass_range: Tuple of min and max mass. If not provided, mass is set to None.
    :param rt_range: Tuple of min and max rt. If not provided, rt is set to None.
    :param ook0_range: Tuple of min and max ook0. If not provided, ook0 is set to None.
    :param intensity_range: Tuple of min and max intensity. If not provided, intensity is set to None.
    :return: ExclusionPoint with randomly generated attributes within the specified ranges.
    """
    charge = None if charge_range is None else random.randint(charge_range[0], charge_range[1])
    mass = None if mass_range is None else random.uniform(mass_range[0], mass_range[1])
    rt = None if rt_range is None else random.uniform(rt_range[0], rt_range[1])
    ook0 = None if ook0_range is None else random.uniform(ook0_range[0], ook0_range[1])
    intensity = None if intensity_range is None else random.uniform(intensity_range[0], intensity_range[1])

    return ExclusionPoint(charge=charge, mass=mass, rt=rt, ook0=ook0, intensity=intensity)


def generate_random_interval(exclusion_tolerance: DynamicExclusionTolerance,
                             interval_id: str = None,
                             charge_range: Tuple[int, int] = None,
                             mass_range: Tuple[float, float] = None,
                             rt_range: Tuple[float, float] = None,
                             ook0_range: Tuple[float, float] = None,
                             intensity_range: Tuple[float, float] = None,
                             ) -> ExclusionInterval:
    """
    Generate a random ExclusionInterval using a random ExclusionPoint and specified exclusion tolerances.

    :param exclusion_tolerance: DynamicExclusionTolerance object containing the tolerances to construct the interval.
    :param interval_id: Optional identifier for the interval. If not provided, a random UUID will be assigned.
    :param charge_range: Tuple of min and max charge, inclusive. If not provided, charge is set to None.
    :param mass_range: Tuple of min and max mass. If not provided, mass is set to None.
    :param rt_range: Tuple of min and max rt. If not provided, rt is set to None.
    :param ook0_range: Tuple of min and max ook0. If not provided, ook0 is set to None.
    :param intensity_range: Tuple of min and max intensity. If not provided, intensity is set to None.
    :return: ExclusionInterval with randomly generated attributes within the specified ranges and tolerances.
    """
    if interval_id is None:
        interval_id = str(uuid.uuid4())

    random_point = generate_random_point(charge_range=charge_range, mass_range=mass_range, rt_range=rt_range, ook0_range=ook0_range, intensity_range=intensity_range)
    return exclusion_tolerance.construct_interval(interval_id, random_point)