import json
from typing import List, Dict

import requests

from .components import ExclusionPoint, ExclusionInterval
from .exceptions import UnexpectedStatusCodeException
from .queryfactory import make_save_query, make_load_query, make_stats_query, \
    make_exclusion_interval_query, make_clear_query, make_exclusion_points_query, make_exclusion_point_query


def clear_active_exclusion_list(exclusion_api_ip: str, timeout=None):
    response = requests.delete(make_clear_query(exclusion_api_ip), timeout=timeout)
    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def load_active_exclusion_list(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(make_load_query(exclusion_api_ip, exid), timeout=timeout)
    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def save_active_exclusion_list(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.post(make_save_query(exclusion_api_ip, exid), timeout=timeout)
    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def get_active_exclusion_list_stats(exclusion_api_ip: str, timeout=None) -> List[str]:
    response = requests.get(make_stats_query(exclusion_api_ip), timeout=timeout)
    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    else:
        return json.loads(response.content)['active_exclusion_list']


def get_exclusion_list_files(exclusion_api_ip: str, timeout=None) -> List[str]:
    response = requests.get(make_stats_query(exclusion_api_ip), timeout=timeout)
    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    else:
        return json.loads(response.content)['files']


def download_exclusion_list_save(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.get(f'{exclusion_api_ip}/exclusionms/file?exclusion_list_name={exid}', timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    else:
        return response.content


def delete_exclusion_list_save(exclusion_api_ip: str, exid: str, timeout=None):
    response = requests.delete(f'{exclusion_api_ip}/exclusionms/file?exclusion_list_name={exid}', timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def add_exclusion_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> None:
    query = f'{exclusion_api_ip}/exclusionms/interval'

    response = requests.post(query, json=exclusion_interval.dict(), timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def add_exclusion_intervals(exclusion_api_ip: str, exclusion_intervals: List[ExclusionInterval], timeout=None) -> None:
    query = f'{exclusion_api_ip}/exclusionms/intervals'

    json_msg = [interval.dict() for interval in exclusion_intervals]

    response = requests.post(query, json=json_msg, timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def get_exclusion_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> List[ExclusionInterval]:
    query = make_exclusion_interval_query(exclusion_api_ip=exclusion_api_ip,
                                          exclusion_interval=exclusion_interval)

    response = requests.get(query, timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    response_dicts = json.loads(response.content)
    exclusion_intervals = [ExclusionInterval.from_dict(d) for d in response_dicts]
    return exclusion_intervals


def delete_exclusion_interval(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> List[ExclusionInterval]:
    query = f'{exclusion_api_ip}/exclusionms/interval'
    response = requests.delete(query, json=exclusion_interval.dict(), timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    response_dicts = json.loads(response.content)
    exclusion_intervals = [ExclusionInterval.from_dict(d) for d in response_dicts]
    return exclusion_intervals


def get_intervals_from_point(exclusion_api_ip: str, exclusion_point: ExclusionPoint, timeout=None) -> List[ExclusionInterval]:
    query = make_exclusion_point_query(exclusion_api_ip=exclusion_api_ip, exclusion_point=exclusion_point)
    response = requests.get(query, timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    response_dicts = json.loads(response.content)
    exclusion_intervals = [ExclusionInterval.from_dict(d) for d in response_dicts]
    return exclusion_intervals


def get_excluded_points(exclusion_api_ip: str, exclusion_points: List[ExclusionPoint], timeout=None) -> List[bool]:
    query = make_exclusion_points_query(exclusion_api_ip=exclusion_api_ip)
    response = requests.post(query, json=[point.dict() for point in exclusion_points], timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    return json.loads(response.content)

