from typing import List

from .components import ExclusionInterval, ExclusionPoint


def make_clear_query(exclusion_api_ip: str):
    return f'{exclusion_api_ip}/exclusionms'


def make_save_query(exclusion_api_ip: str, exid: str):
    return f'{exclusion_api_ip}/exclusionms?save=True&exclusion_list_name={exid}'


def make_load_query(exclusion_api_ip: str, exid: str):
    return f'{exclusion_api_ip}/exclusionms?save=False&exclusion_list_name={exid}'


def make_stats_query(exclusion_api_ip: str):
    return f'{exclusion_api_ip}/exclusionms'


def make_exclusion_interval_query(exclusion_api_ip: str, exclusion_interval: ExclusionInterval) -> str:
    interval_query = ''
    if exclusion_interval.id:
        interval_query += f'&interval_id={exclusion_interval.id}'
    if exclusion_interval.charge:
        interval_query += f'&charge={exclusion_interval.charge}'
    if exclusion_interval.min_mass:
        interval_query += f'&min_mass={exclusion_interval.min_mass}'
    if exclusion_interval.max_mass:
        interval_query += f'&max_mass={exclusion_interval.max_mass}'
    if exclusion_interval.min_rt:
        interval_query += f'&min_rt={exclusion_interval.min_rt}'
    if exclusion_interval.max_rt:
        interval_query += f'&max_rt={exclusion_interval.max_rt}'
    if exclusion_interval.min_ook0:
        interval_query += f'&min_ook0={exclusion_interval.min_ook0}'
    if exclusion_interval.max_ook0:
        interval_query += f'&max_ook0={exclusion_interval.max_ook0}'
    if exclusion_interval.min_intensity:
        interval_query += f'&min_intensity={exclusion_interval.min_intensity}'
    if exclusion_interval.max_intensity:
        interval_query += f'&max_intensity={exclusion_interval.max_intensity}'

    if interval_query:
        interval_query = '?' + interval_query[1:]

    add_interval_api_str = f'{exclusion_api_ip}/exclusionms/interval{interval_query}'

    return add_interval_api_str


def make_exclusion_point_query(exclusion_api_ip: str, exclusion_point: ExclusionPoint):
    interval_query = ''
    if exclusion_point.charge:
        interval_query += f'&charge={exclusion_point.charge}'
    if exclusion_point.mass:
        interval_query += f'&mass={exclusion_point.mass}'
    if exclusion_point.rt:
        interval_query += f'&rt={exclusion_point.rt}'
    if exclusion_point.ook0:
        interval_query += f'&ook0={exclusion_point.ook0}'
    if exclusion_point.intensity:
        interval_query += f'&intensity={exclusion_point.intensity}'

    if interval_query:
        interval_query = '?' + interval_query[1:]

    return f'{exclusion_api_ip}/exclusionms/point{interval_query}'


def make_exclusion_points_query(exclusion_api_ip: str):
    query_points_api_str = f'{exclusion_api_ip}/exclusionms/excluded_points'
    return query_points_api_str
