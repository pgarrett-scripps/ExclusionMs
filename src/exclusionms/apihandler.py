"""
This module provides a set of utility functions and a Handler class for interacting with the Exclusion API, allowing
for easy management and manipulation of exclusion intervals and points.
"""

import json
import logging
import time
from dataclasses import dataclass
from math import ceil
from typing import List, Dict
from functools import wraps

import requests
import ujson

from .components import ExclusionPoint, ExclusionInterval

log = logging.getLogger(__name__)


def timer_decorator(func):
    """A decorator that measures the execution time of the decorated function.

    Args:
        func: The function to be decorated.

    Returns:
        A wrapper function that measures the execution time of the decorated function.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        log.info("%s took %.4f seconds to execute.", func.__name__, elapsed_time)
        return result

    return wrapper


@timer_decorator
def clear(exclusion_api_ip: str, timeout=None) -> int:
    """Clears the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        timeout: (Optional) The timeout for the API request.

    Returns:
        The number of exclusions that were cleared.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/clear',
                             timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


@timer_decorator
def load(exclusion_api_ip: str, exid: str, timeout=None):
    """Loads an exclusion list with the specified ID.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exid: The ID of the exclusion list to load.
        timeout: (Optional) The timeout for the API request.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/load?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


@timer_decorator
def save(exclusion_api_ip: str, exid: str, timeout=None):
    """Saves the exclusion list with the specified ID.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exid: The ID of the exclusion list to save.
        timeout: (Optional) The timeout for the API request.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/save?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


@timer_decorator
def delete(exclusion_api_ip: str, exid: str, timeout=None):
    """Deletes the exclusion list with the specified ID.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exid: The ID of the exclusion list to delete.
        timeout: (Optional) The timeout for the API request.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/delete?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


@timer_decorator
def get_statistics(exclusion_api_ip: str, timeout=None) -> Dict:
    """Gets statistics about the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A dictionary containing statistics about the exclusion list.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.get(url=f'{exclusion_api_ip}/exclusionms/statistics',
                            timeout=timeout)
    response.raise_for_status()

    return json.loads(response.content)


@timer_decorator
def get_len(exclusion_api_ip: str, timeout=None) -> Dict:
    """Gets the length of the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A dictionary containing the length of the exclusion list.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    return get_statistics(exclusion_api_ip,timeout)['len']


@timer_decorator
def get_files(exclusion_api_ip: str, timeout=None) -> List[str]:
    """Gets a list of files associated with the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of files associated with the exclusion list.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.get(url=f'{exclusion_api_ip}/exclusionms/file',
                            timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


def add_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> None:
    """Adds a single exclusion interval to the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_interval: The exclusion interval to add.
        timeout: (Optional) The timeout for the API request.

    """
    add_intervals(exclusion_api_ip, [exclusion_interval], timeout)


@timer_decorator
def add_intervals(exclusion_api_ip: str, exclusion_intervals: List[ExclusionInterval], timeout=None,
                  use_ujson=False, batch_size: int = None) -> None:
    """Adds multiple exclusion intervals to the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_intervals: The exclusion intervals to add.
        timeout: (Optional) The timeout for the API request.
        use_ujson: (Optional) Whether to use ujson instead of the standard JSON library.
        batch_size: (Optional) The batch size for adding intervals in batches.

    Raises:
        HTTPError: If the API request returns an error status code.

    """

    if batch_size is None:
        batch_size = len(exclusion_intervals)

    num_batches = ceil(len(exclusion_intervals) / batch_size)

    for batch_idx in range(num_batches):
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, len(exclusion_intervals))
        batch_intervals = exclusion_intervals[batch_start:batch_end]

        if use_ujson:
            response = requests.post(url=f'{exclusion_api_ip}/exclusionms/intervals',
                                     data=ujson.dumps([interval.dict() for interval in batch_intervals]),
                                     timeout=timeout)
        else:
            response = requests.post(url=f'{exclusion_api_ip}/exclusionms/intervals',
                                     json=[interval.dict() for interval in batch_intervals],
                                     timeout=timeout)

        response.raise_for_status()


def search_interval(exclusion_api_ip: str,
                    exclusion_interval: ExclusionInterval,
                    timeout=None) -> List[ExclusionInterval]:
    """Searches for a single exclusion interval in the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_interval: The exclusion interval to search for.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of exclusion intervals that match the search criteria.

    """
    return search_intervals(exclusion_api_ip, [exclusion_interval], timeout)[0]


@timer_decorator
def search_intervals(exclusion_api_ip: str,
                     exclusion_intervals: List[ExclusionInterval],
                     timeout=None) -> List[List[ExclusionInterval]]:
    """Searches for multiple exclusion intervals in the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_intervals: The exclusion intervals to search for.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of lists of exclusion intervals that match the search criteria.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/intervals/search',
                             json=[interval.dict() for interval in exclusion_intervals],
                             timeout=timeout)

    response.raise_for_status()

    response_dicts = json.loads(response.content)
    exclusion_intervals = [[ExclusionInterval.from_dict(d) for d in l] for l in response_dicts]
    return exclusion_intervals


def delete_interval(exclusion_api_ip: str,
                    exclusion_interval: ExclusionInterval,
                    timeout=None) -> List[ExclusionInterval]:
    """Deletes a single exclusion interval from the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_interval: The exclusion interval to delete.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of exclusion intervals that were deleted.

    """
    return delete_intervals(exclusion_api_ip, [exclusion_interval], timeout)[0]


@timer_decorator
def delete_intervals(exclusion_api_ip: str,
                     exclusion_intervals: List[ExclusionInterval],
                     timeout=None) -> List[List[ExclusionInterval]]:
    """Deletes multiple exclusion intervals from the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_intervals: The exclusion intervals to delete.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of lists of exclusion intervals that were deleted.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.delete(url=f'{exclusion_api_ip}/exclusionms/intervals',
                               json=[interval.dict() for interval in exclusion_intervals],
                               timeout=timeout)

    response.raise_for_status()

    response_dicts = json.loads(response.content)
    exclusion_intervals = [[ExclusionInterval.from_dict(d) for d in l] for l in response_dicts]
    return exclusion_intervals


def search_point(exclusion_api_ip: str,
                 exclusion_point: ExclusionPoint,
                 timeout=None) -> List[ExclusionInterval]:
    """Searches a single exclusion point in the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_point: The exclusion point to search for.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of exclusion intervals that contain the exclusion point.

    """
    return search_points(exclusion_api_ip, [exclusion_point], timeout)[0]


@timer_decorator
def search_points(exclusion_api_ip: str,
                  exclusion_points: List[ExclusionPoint],
                  timeout=None) -> List[List[ExclusionInterval]]:
    """Searches multiple exclusion points in the exclusion list.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_points: The exclusion points to search for.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A list of lists of exclusion intervals that contain the exclusion points.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/points/search',
                             json=[point.dict() for point in exclusion_points],
                             timeout=timeout)

    response.raise_for_status()

    response_dicts = json.loads(response.content)
    exclusion_intervals = [[ExclusionInterval.from_dict(d) for d in l] for l in response_dicts]
    return exclusion_intervals


def exclusion_search_point(exclusion_api_ip: str, exclusion_point: ExclusionPoint, timeout=None) -> bool:
    """Checks if a single exclusion point is excluded.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_point: The exclusion point to check.
        timeout: (Optional) The timeout for the API request.

    Returns:
        True if the exclusion point is excluded, False otherwise.

    """
    return exclusion_search_points(exclusion_api_ip, [exclusion_point], timeout)[0]


@timer_decorator
def exclusion_search_points(exclusion_api_ip: str, exclusion_points: List[ExclusionPoint], timeout=None,
                            use_ujson=False) -> List[bool]:
    """Checks if multiple exclusion points are excluded.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        exclusion_points: The exclusion points to check.
        timeout: (Optional) The timeout for the API request.
        use_ujson: (Optional) Whether to use ujson instead of the standard JSON library.

    Returns:
        A list of booleans indicating whether the exclusion points are excluded.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    if use_ujson is True:
        response = requests.post(url=f'{exclusion_api_ip}/exclusionms/points/exclusion_search',
                                 data=ujson.dumps([point.dict() for point in exclusion_points]),
                                 timeout=timeout)
    else:
        response = requests.post(url=f'{exclusion_api_ip}/exclusionms/points/exclusion_search',
                                 json=[point.dict() for point in exclusion_points],
                                 timeout=timeout)

    response.raise_for_status()

    return json.loads(response.content)


@timer_decorator
def is_connected(exclusion_api_ip: str, timeout=None) -> bool:
    """Checks if the exclusion API is connected.

    Args:
        exclusion_api_ip: The IP address of the exclusion API.
        timeout: (Optional) The timeout for the API request.

    Returns:
        True if the exclusion API is connected, False otherwise.

    """
    try:
        get_statistics(exclusion_api_ip, timeout)
    except requests.exceptions.ConnectionError:
        return False

    return True


@timer_decorator
def load_or_clear_exclusion_list(exid: str, exclusionms_ip: str, timeout=None):
    """Loads or clears the exclusion list with the specified ID.

    If the exclusion list with the specified ID exists, it is loaded. If it does not exist,
    the exclusion list is cleared.

    Args:
        exid: The ID of the exclusion list to load or clear.
        exclusionms_ip: The IP address of the exclusion API.
        timeout: (Optional) The timeout for the API request.

    """
    available_exclusion_lists = get_files(exclusionms_ip, timeout)
    if exid not in available_exclusion_lists:
        clear(exclusionms_ip, timeout)
    else:
        load(exclusionms_ip, exid, timeout)


@timer_decorator
def get_log_entries(exclusionms_ip: str, num_entries: int = 500, timeout=None) -> {}:
    """Gets the most recent log entries.

    Args:
        exclusionms_ip: The IP address of the exclusion API.
        num_entries: (Optional) The number of log entries to retrieve.
        timeout: (Optional) The timeout for the API request.

    Returns:
        A dictionary containing the most recent log entries.

    Raises:
        HTTPError: If the API request returns an error status code.

    """
    response = requests.get(url=f'{exclusionms_ip}/logs/entries?num_entries={num_entries}', timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


@dataclass
class Handler:
    """A simple wrapper around the exclusion API functions.

    Attributes:
        exclusion_api_ip: The IP address of the exclusion API.
        timeout: The timeout for the API request.
        use_ujson: (Optional) Whether to use ujson instead of the default JSON library.
        batch_size: (Optional) The batch size to use for adding exclusion intervals.

    """
    exclusion_api_ip: str
    timeout: float
    use_ujson: bool = False
    batch_size: int = None

    def clear(self) -> int:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return clear(self.exclusion_api_ip, self.timeout)

    def load(self, exid: str):
        """Calls equivalent apihandler function with the Handlers attributes"""
        return load(self.exclusion_api_ip, exid, self.timeout)

    def save(self, exid: str):
        """Calls equivalent apihandler function with the Handlers attributes"""
        return save(self.exclusion_api_ip, exid, self.timeout)

    def delete(self, exid: str):
        """Calls equivalent apihandler function with the Handlers attributes"""
        return delete(self.exclusion_api_ip, exid, self.timeout)

    def get_statistics(self) -> Dict:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return get_statistics(self.exclusion_api_ip, self.timeout)

    def get_len(self) -> Dict:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return get_len(self.exclusion_api_ip, self.timeout)

    def get_files(self) -> Dict:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return get_files(self.exclusion_api_ip, self.timeout)

    def add_interval(self, exclusion_interval: ExclusionInterval) -> None:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return add_interval(self.exclusion_api_ip, exclusion_interval)

    def add_intervals(self, exclusion_intervals: List[ExclusionInterval]) -> None:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return add_intervals(self.exclusion_api_ip, exclusion_intervals, self.timeout, self.use_ujson, self.batch_size)

    def search_interval(self, exclusion_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return search_interval(self.exclusion_api_ip, exclusion_interval, self.timeout)

    def search_intervals(self, exclusion_intervals: List[ExclusionInterval]) -> List[ExclusionInterval]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return search_intervals(self.exclusion_api_ip, exclusion_intervals, self.timeout)

    def delete_interval(self, exclusion_interval: ExclusionInterval) -> List[ExclusionInterval]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return delete_interval(self.exclusion_api_ip, exclusion_interval, self.timeout)

    def delete_intervals(self, exclusion_intervals: List[ExclusionInterval]) -> List[List[ExclusionInterval]]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return delete_intervals(self.exclusion_api_ip, exclusion_intervals, self.timeout)

    def search_point(self, exclusion_point: ExclusionPoint) -> List[ExclusionInterval]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return search_point(self.exclusion_api_ip, exclusion_point, self.timeout)

    def search_points(self, exclusion_points: List[ExclusionPoint]) -> List[List[ExclusionInterval]]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return search_points(self.exclusion_api_ip, exclusion_points, self.timeout)

    def exclusion_search_point(self, exclusion_point: ExclusionPoint) -> bool:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return exclusion_search_point(self.exclusion_api_ip, exclusion_point, self.timeout)

    def exclusion_search_points(self, exclusion_points: List[ExclusionPoint]) -> List[bool]:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return exclusion_search_points(self.exclusion_api_ip, exclusion_points, self.timeout)

    def is_connected(self) -> bool:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return is_connected(self.exclusion_api_ip, self.timeout)

    def load_or_clear_exclusion_list(self):
        """Calls equivalent apihandler function with the Handlers attributes"""
        return load_or_clear_exclusion_list(self.exclusion_api_ip, self.timeout)

    def get_log_entries(self) -> {}:
        """Calls equivalent apihandler function with the Handlers attributes"""
        return search_intervals(self.exclusion_api_ip, self.timeout)
