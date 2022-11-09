import json
from typing import List, Dict

import requests

from .components import ExclusionPoint, ExclusionInterval
from .exceptions import UnexpectedStatusCodeException
from .queryfactory import make_save_query, make_load_query, make_stats_query, \
    make_exclusion_interval_query, make_clear_query, make_exclusion_points_query


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


def add_exclusion_interval_query(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> None:
    query = make_exclusion_interval_query(exclusion_api_ip=exclusion_api_ip,
                                          exclusion_interval=exclusion_interval)

    response = requests.post(query, timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def get_exclusion_interval_query(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> List[Dict]:
    query = make_exclusion_interval_query(exclusion_api_ip=exclusion_api_ip,
                                          exclusion_interval=exclusion_interval)

    response = requests.get(query, timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

    return json.loads(response.content)


def delete_exclusion_interval_query(exclusion_api_ip: str, exclusion_interval: ExclusionInterval, timeout=None) -> None:
    query = make_exclusion_interval_query(exclusion_api_ip=exclusion_api_ip,
                                          exclusion_interval=exclusion_interval)

    response = requests.delete(query, timeout=timeout)

    if response.status_code != 200:
        raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))


def get_excluded_points(exclusion_api_ip: str, exclusion_points: List[ExclusionPoint], timeout=None, chunk_size=100) -> List[bool]:

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    exclusion_points_chunks = divide_chunks(exclusion_points, chunk_size)
    combined_response = []
    for partial_exclusion_points in exclusion_points_chunks:
        query = make_exclusion_points_query(exclusion_api_ip=exclusion_api_ip,
                                            exclusion_points=partial_exclusion_points)

        response = requests.get(query, timeout=timeout)

        if response.status_code != 200:
            raise UnexpectedStatusCodeException(response.status_code, 200, response.content.decode(encoding='utf-8'))

        combined_response.extend(json.loads(response.content))

    return combined_response
