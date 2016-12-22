## Synopsis

As users of virtual machines, clouds, grids, opportunistic resources, etc., we
have many options to run millions of tasks. If we want to use such resources
efficiently, such as maximizing throughput (i.e., how many tasks are completed
per hour), or minimizing waste (i.e., how many resources were committed but not
used to finish tasks),  we need a way to select the *slice* of resources
assigned to each task. 

The challenge is that resource usage is seldom uniform. Even tasks of the same
type often have different resource needs, which are only known until runtime.
Assigning too many resources, leads to an underutilized system with low
throughput; similarly, assigning too few resources, leads to many tasks leads
to resource contention, which causes low throughput, and possibly task
failures. 

To solve this problem, we created the present library. Historical resource
usage is analyzed, and a *first allocation* for a task is generated. Such the
task use more resources than this first allocation, the task is re-run using a
given maximum. In an accompanying paper, we show that such retry strategy leads
to an increase in throughput from 10% to 400% across data we have available on
different workflows.

## Code Example

```python
from ResourceMonitor import Categories

# Create an empty set of categories. A category is a set of tasks qualitatively
# labeled by the user (e.g., 'analysis', or 'parameter-x'). In an ideal world,
# tasks in a category would have the same resource consumption.

cs = Categories()

# Add resource summary reports. Reports are dictionaries which keys such as
# 'category', 'wall_time', 'cores', 'memory', and 'disk'. At least the keys
# 'category' and 'wall_time' (time of execution) should be present.

categories.accumulate_summary( { 'category': 'my_category',       'memory': 100, 'wall_time': 360} )
categories.accumulate_summary( { 'category': 'my_category',       'memory': 960, 'wall_time':  30} )
categories.accumulate_summary( { 'category': 'my_other_category', 'memory':  50, 'wall_time':  72} )

# Obtain the computed first allocations for maximum throughput, and the maximum
# resources seen, per category:
for name in categories.category_names():
    first_allocation = categories.first_allocation(mode = 'throughput', category = name)
    maximum_seen     = categories.maximum_seen(category = name)

    print first_allocation['memory']
    print maximum_seen['memory']
```

## Installation

Currently, this repository only contains examples of the python bindings from
our C implementation. The C implementation is part of our CCTools library
suite.

### Binary installation

To install a binary version

Download the appropiate

### Installation from source

Make sure you have swig and the development files for python installed. For
example: `apt-get install build-essentials swig python2.7-dev`

## Running the examples

```sh
git clone https://github.com/cooperative-computing-lab/efficient-resource-allocations.git
cd efficient-resource-allocations
# computing allocations from real workflow data:
./allocations_from_data data/bioblast.csv
# synthetic examples using beta, exponential, and triangular distributions:
./synthetic_examples
```

## License

Copyright (C) 2016- The University of Notre Dame This software is distributed
under the GNU General Public License.  See the file COPYING for details.

