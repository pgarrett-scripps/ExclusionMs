import json
from typing import List, Dict

import requests

from .components import ExclusionPoint, ExclusionInterval


def clear(exclusion_api_ip: str, timeout=None) -> int:
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/clear',
                             timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


def load(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/load?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


def save(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/save?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


def delete(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/delete?exid={exid}',
                             timeout=timeout)
    response.raise_for_status()


def get_statistics(exclusion_api_ip: str, timeout=None) -> Dict:
    response = requests.get(url=f'{exclusion_api_ip}/exclusionms/statistics',
                            timeout=timeout)
    response.raise_for_status()

    return json.loads(response.content)


def get_len(exclusion_api_ip: str, timeout=None) -> Dict:
    return get_statistics(exclusion_api_ip)['len']


def get_files(exclusion_api_ip: str, timeout=None) -> List[str]:
    response = requests.get(url=f'{exclusion_api_ip}/exclusionms/file',
                            timeout=timeout)
    response.raise_for_status()
    return json.loads(response.content)


def add_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> None:
    add_intervals(exclusion_api_ip, [exclusion_interval], timeout)


def add_intervals(exclusion_api_ip: str, exclusion_intervals: List[ExclusionInterval], timeout=None) -> None:
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/intervals',
                             json=[interval.dict() for interval in exclusion_intervals],
                             timeout=timeout)
    response.raise_for_status()


def search_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> List[
    ExclusionInterval]:
    return search_intervals(exclusion_api_ip, [exclusion_interval], timeout)[0]


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


def exclusion_search_points(exclusion_api_ip: str, exclusion_points: List[ExclusionPoint], timeout=None) -> List[bool]:
    response = requests.post(url=f'{exclusion_api_ip}/exclusionms/points/exclusion_search',
                             json=[point.dict() for point in exclusion_points],
                             timeout=timeout)

    response.raise_for_status()

    return json.loads(response.content)

def is_connected(exclusion_api_ip: str) -> bool:
    try:
        get_statistics(exclusion_api_ip)
    except requests.exceptions.ConnectionError:
        return False

    return True
