# ExclusionMS Package
This Python package provides a way to manage and query exclusion intervals. It uses a 1-dimensional 
IntervalTree to efficiently store exclusion intervals based on their neutral mass
and perform various operations on them. 

## Installation
To use this library, simply download or clone the repository and import the necessary classes and functions in your 
Python project.

**Repo:**
```
git clone https://github.com/pgarrett-scripps/ExclusionMs.git
cd ExclusionMs
pip install .
```

or 

**Pypi:**
```
pip install exclusionms
```

## Usage

### Import classes and functions

```
from exclusion_list.components import ExclusionInterval, ExclusionPoint
from exclusion_list.mass_interval_tree import MassIntervalTree
```

### Create an exclusion interval

```
ex_interval = ExclusionInterval(
    interval_id="ID1",
    charge=2,
    min_mass=100.0,
    max_mass=200.0,
    min_rt=10.0,
    max_rt=20.0,
    min_ook0=None,
    max_ook0=None,
    min_intensity=None,
    max_intensity=None,
)
```

### Create a mass interval tree and add exclusion intervals
```
tree = MassIntervalTree()
tree.add(ex_interval)
```

### Query intervals by ID, mass interval, or a specific data point
```
# Query by ID
result = tree.query_by_id("ID1")

# Query by interval
query_interval = ExclusionInterval(
    interval_id=None,
    charge=None,
    min_mass=50.0,
    max_mass=250.0,
    min_rt=None,
    max_rt=None,
    min_ook0=None,
    max_ook0=None,
    min_intensity=None,
    max_intensity=None,
)
result = tree.query_by_interval(query_interval)

# Query by point
point = ExclusionPoint(charge=2, mass=120.0, rt=15.0, ook0=None, intensity=None)
result = tree.query_by_point(point)
```

### Check if a data point is excluded by any of the intervals in the tree

```
is_excluded = tree.is_excluded(point)
```

### Remove exclusion intervals

```
removed_intervals = tree.remove(ex_interval)
```

### Save and load interval trees
```
tree.save("interval_tree.pickle")
tree.load("interval_tree.pickle")
```

### Clear all data in the interval tree
```
tree.clear()
```

# Handling None Values in Exclusion Intervals
When defining exclusion intervals, you may want to leave certain attributes unspecified by setting them to None. 
This can be useful when you want to represent a range that is unbounded or applicable to all values of that attribute.
Here's how the library handles None values for various attributes:

- **interval_id:** If the interval ID is set to None, the exclusion interval cannot be added to the interval tree. 
An exception will be raised if you attempt to do so.

- **charge:** If the charge is set to None, the interval represents all charge states. It will match any charge value 
when checking if a data point is excluded or when querying intervals.

- **min_bounds and max_bounds:** For attributes such as mass, retention time (rt), ook0, and intensity, you can 
set the lower (min_bounds) or upper (max_bounds) bounds to None. In such cases, the library will use the following 
values as default bounds:

  - Lower bound (min_bounds): -sys.float_info.max
  - Upper bound (max_bounds): sys.float_info.max
  - (This means that if you set the lower bound to None, it will be treated as the minimum representable float value. 
  Similarly, if you set the upper bound to None, it will be treated as the maximum representable float value. 
  This effectively makes the range unbounded for the respective attribute.)

By using None values in exclusion intervals, you can create more flexible and versatile exclusion rules that can 
match a broader range of data points.

## Stress Tester
stress_test.py is designed to stress test the ExclusionMS server by generating a large number of random points and 
intervals, and then querying the server to check for exclusions. The script also plots the query processing time, 
along with additional information such as the running average and interval addition events. The plot can be 
updated in real-time or saved as a PNG file.