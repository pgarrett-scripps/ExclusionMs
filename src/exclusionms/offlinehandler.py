"""
OfflineHandler Functions
"""
import json
import time
from typing import List

from exclusionms.components import ExclusionPoint, ExclusionInterval
from exclusionms.db import MassIntervalTree, IntervalStatus

STATUS_TO_PRIORITY = {
    IntervalStatus.EXCLUDED.value: 0,
    IntervalStatus.EXCLUDED_INCLUDED.value: 0,
    IntervalStatus.INCLUDED.value: 2,
    IntervalStatus.NO_INTERVALS_FOUND.value: 1
}


def is_candidate_valid(c: 'Candidate') -> bool:
    return all([c.precursor.monoisotopic_mz, c.precursor.charge, c.one_over_k0])


def calculate_mass(mz: float, charge: int) -> float:
    return mz * charge - charge * 1.00727647


def candidate_to_point(candidate: 'Candidate', time: float):
    return ExclusionPoint(
        charge=candidate.precursor.charge,
        mass=calculate_mass(candidate.precursor.monoisotopic_mz, candidate.precursor.charge),
        rt=time,
        ook0=candidate.one_over_k0,
        intensity=candidate.precursor.intensity)


def setup_interval_tree(file_path: str = None) -> MassIntervalTree:
    tree = MassIntervalTree()

    # The filepath is a file that contains a large json object that is used to initialize the tree
    intervals = json.loads(open(file_path).read())
    intervals = [ExclusionInterval.from_dict(interval) for interval in intervals]

    for interval in intervals:
        tree.add(interval)

    return tree


def update_candidate_priorities(tree: MassIntervalTree, candidates: List['Candidate'], acquisition_time: float) -> None:
    for candidate in candidates:

        if not is_candidate_valid(candidate):
            continue

        point = candidate_to_point(candidate, acquisition_time)
        point_status = tree.point_status(point)
        priority = STATUS_TO_PRIORITY[point_status]
        candidate.scheduling_priority = priority


start_time = time.time()
tree = setup_interval_tree(r"C:\Users\Ty\Downloads\proteotypic_intervals.txt")
end_time = time.time()


execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")
