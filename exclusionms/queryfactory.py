from .components import ExclusionInterval, ExclusionPoint, ExclusionIntervalMsg, ExclusionPointMsg


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

    exclusion_interval_msg = ExclusionIntervalMsg.from_exclusion_interval(exclusion_interval)

    interval_query += f'&interval_id={exclusion_interval_msg.interval_id}'
    interval_query += f'&charge={exclusion_interval_msg.charge}'
    interval_query += f'&min_mass={exclusion_interval_msg.min_mass}'
    interval_query += f'&max_mass={exclusion_interval_msg.max_mass}'
    interval_query += f'&min_rt={exclusion_interval_msg.min_rt}'
    interval_query += f'&max_rt={exclusion_interval_msg.max_rt}'
    interval_query += f'&min_ook0={exclusion_interval_msg.min_ook0}'
    interval_query += f'&max_ook0={exclusion_interval_msg.max_ook0}'
    interval_query += f'&min_intensity={exclusion_interval_msg.min_intensity}'
    interval_query += f'&max_intensity={exclusion_interval_msg.max_intensity}'

    if interval_query:
        interval_query = '?' + interval_query[1:]

    add_interval_api_str = f'{exclusion_api_ip}/exclusionms/interval{interval_query}'

    return add_interval_api_str


def make_exclusion_point_query(exclusion_api_ip: str, exclusion_point: ExclusionPoint):
    exclusion_point_msg = ExclusionPointMsg.from_exclusion_point(exclusion_point)
    interval_query = ''
    interval_query += f'&charge={exclusion_point_msg.charge}'
    interval_query += f'&mass={exclusion_point_msg.mass}'
    interval_query += f'&rt={exclusion_point_msg.rt}'
    interval_query += f'&ook0={exclusion_point_msg.ook0}'
    interval_query += f'&intensity={exclusion_point_msg.intensity}'

    if interval_query:
        interval_query = '?' + interval_query[1:]

    return f'{exclusion_api_ip}/exclusionms/point{interval_query}'


def make_exclusion_points_query(exclusion_api_ip: str):
    query_points_api_str = f'{exclusion_api_ip}/exclusionms/excluded_points'
    return query_points_api_str
