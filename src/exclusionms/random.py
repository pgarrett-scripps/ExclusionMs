"""
This module provides utility functions for generating random ExclusionPoint and ExclusionInterval objects with
specified attribute ranges and exclusion tolerances.
"""

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
    Generates a random ExclusionPoint object with specified attribute ranges.

    Args:
        charge_range (Tuple[int, int], optional): Range of charge values for the point. Default: None
        mass_range (Tuple[float, float], optional): Range of mass values for the point. Default: None
        rt_range (Tuple[float, float], optional): Range of retention time values for the point. Default: None
        ook0_range (Tuple[float, float], optional): Range of ook0 values for the point. Default: None
        intensity_range (Tuple[float, float], optional): Range of intensity values for the point. Default: None

    Returns:
        ExclusionPoint: The generated random ExclusionPoint object.
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
    Generates a random ExclusionInterval object with specified attribute ranges and exclusion tolerance.

    Args:
        exclusion_tolerance (DynamicExclusionTolerance): The exclusion tolerance used to construct the interval.
        interval_id (str, optional): The ID of the interval. If not provided, a random UUID will be used. Default: None
        charge_range (Tuple[int, int], optional): Range of charge values for the interval points. Default: None
        mass_range (Tuple[float, float], optional): Range of mass values for the interval points. Default: None
        rt_range (Tuple[float, float], optional): Range of retention time values for the interval points. Default: None
        ook0_range (Tuple[float, float], optional): Range of ook0 values for the interval points. Default: None
        intensity_range (Tuple[float, float], optional): Range of intensity values for the interval points. Default: None

    Returns:
        ExclusionInterval: The generated random ExclusionInterval object.
    """

    if interval_id is None:
        interval_id = str(uuid.uuid4())

    random_point = generate_random_point(charge_range=charge_range,
                                         mass_range=mass_range,
                                         rt_range=rt_range,
                                         ook0_range=ook0_range,
                                         intensity_range=intensity_range)
    return exclusion_tolerance.construct_interval(interval_id, random_point)
