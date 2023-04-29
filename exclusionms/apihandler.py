import json
import logging
import time
from math import ceil
from typing import List, Dict

import requests
import ujson

from .components import ExclusionPoint, ExclusionInterval

from functools import wraps

log = logging.getLogger(__name__)


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        log.info(f"{func.__name__} took {elapsed_time:.4f} seconds to execute.")
        return result

    return wrapper


@timer_decorator
def clear(exclusion_api_ip: str, timeout=None) -> int:
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/clear',
                             timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


@timer_decorator
def load(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/load?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


@timer_decorator
def save(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/save?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


@timer_decorator
def delete(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/delete?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


@timer_decorator
def get_statistics(exclusion_api_ip: str, timeout=None) -> Dict:
    response = requests.get(url=f'{exclusion_api_ip}/exclusionms/statistics',
                            timeout=timeout)
    response.raise_for_status()

    return json.loads(response.content)


@timer_decorator
def get_len(exclusion_api_ip: str, timeout=None) -> Dict:
    return get_statistics(exclusion_api_ip)['len']


@timer_decorator
def get_files(exclusion_api_ip: str, timeout=None) -> List[str]:
    response = requests.get(url=f'{exclusion_api_ip}/exclusionms/file',
                            timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


def add_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> None:
    add_intervals(exclusion_api_ip, [exclusion_interval], timeout)


@timer_decorator
def add_intervals(exclusion_api_ip: str, exclusion_intervals: List[ExclusionInterval], timeout=None,
                  use_ujson=False, batch_size: int = None) -> None:
    """
    Add intervals to the exclusion API in batches.

    :param exclusion_api_ip: The IP address of the exclusion API.
    :param exclusion_intervals: A list of ExclusionInterval objects to add.
    :param timeout: Optional timeout for the requests.
    :param use_ujson: Whether to use ujson for data serialization.
    :param batch_size: The number of intervals to send in a single batch. If not provided, all intervals are sent in one batch.
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


def search_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> List[
    ExclusionInterval]:
    return search_intervals(exclusion_api_ip, [exclusion_interval], timeout)[0]


@timer_decorator
def search_intervals(exclusion_api_ip: str, exclusion_intervals: List[ExclusionInterval], timeout=None) -> List[
    List[ExclusionInterval]]:
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/intervals/search',
                             json=[interval.dict() for interval in exclusion_intervals],
                             timeout=timeout)

    response.raise_for_status()

    response_dicts = json.loads(response.content)
    exclusion_intervals = [[ExclusionInterval.from_dict(d) for d in l] for l in response_dicts]
    return exclusion_intervals


def delete_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> List[
    ExclusionInterval]:
    return delete_intervals(exclusion_api_ip, [exclusion_interval], timeout)[0]


@timer_decorator
def delete_intervals(exclusion_api_ip: str, exclusion_intervals: List[ExclusionInterval], timeout=None) -> \
        List[List[ExclusionInterval]]:
    response = requests.delete(url=f'{exclusion_api_ip}/exclusionms/intervals',
                               json=[interval.dict() for interval in exclusion_intervals],
                               timeout=timeout)

    response.raise_for_status()

    response_dicts = json.loads(response.content)
    exclusion_intervals = [[ExclusionInterval.from_dict(d) for d in l] for l in response_dicts]
    return exclusion_intervals


def search_point(exclusion_api_ip: str, exclusion_point: ExclusionPoint, timeout=None) -> List[
    ExclusionInterval]:
    return search_points(exclusion_api_ip, [exclusion_point], timeout)[0]


@timer_decorator
def search_points(exclusion_api_ip: str, exclusion_points: List[ExclusionPoint], timeout=None) -> List[List[
    ExclusionInterval]]:
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/points/search',
                             json=[point.dict() for point in exclusion_points],
                             timeout=timeout)

    response.raise_for_status()

    response_dicts = json.loads(response.content)
    exclusion_intervals = [[ExclusionInterval.from_dict(d) for d in l] for l in response_dicts]
    return exclusion_intervals


def exclusion_search_point(exclusion_api_ip: str, exclusion_point: ExclusionPoint, timeout=None) -> bool:
    return exclusion_search_points(exclusion_api_ip, [exclusion_point], timeout)[0]


@timer_decorator
def exclusion_search_points(exclusion_api_ip: str, exclusion_points: List[ExclusionPoint], timeout=None,
                            use_ujson=False) -> List[bool]:
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
def is_connected(exclusion_api_ip: str) -> bool:
    try:
        get_statistics(exclusion_api_ip)
    except requests.exceptions.ConnectionError:
        return False

    return True


@timer_decorator
def load_or_clear_exclusion_list(exid: str, exclusionms_ip: str):
    available_exclusion_lists = get_files(exclusionms_ip)
    if exid not in available_exclusion_lists:
        clear(exclusionms_ip)
    else:
        load(exclusionms_ip, exid)


@timer_decorator
def get_timings(exclusionms_ip: str, timeout=None) -> {}:
    response = requests.get(url=f'{exclusionms_ip}/exclusionms/timing', timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)
