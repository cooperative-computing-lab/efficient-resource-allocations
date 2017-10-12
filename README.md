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
given maximum. [In the accompanying paper (to appear in IEEE Transactions on Parallel and Distributed Systems)](http://ccl.cse.nd.edu/research/papers/Tovar-job-sizing-TPDS2017.pdf), we
show that such retry strategy leads to an increase in throughput from 10% to
400% across data we have available on different workflows.

## Code Example

```python
from FirstAllocation import FirstAllocation

fa = FirstAllocation(name = "my memory usage")

# Add resource data points. A data point consists of the peak memory usage of a
job, and the duration the job was executing:

fa.add_data_point(value = 100, time = 360)
fa.add_data_point(value = 960, time = 360)
fa.add_data_point(value =  50, time = 50)

# Obtain the computed first allocations for maximum throughput, and the maximum
# resources seen:

first_allocation = fa.first_allocation(mode = 'throughput')
maximum_seen     = fa.maximum_seen

print first_allocation
print maximum_seen
```


## Running the examples

```sh
git clone https://github.com/cooperative-computing-lab/efficient-resource-allocations.git
cd efficient-resource-allocations

# computing allocations from real workflow data:
./real_data_examples.py data/bioblast.csv
./real_data_examples.py data/lobsterCMSanalysis.csv
./real_data_examples.py data/lobsterCMSsimulation.csv

# simulation examples using beta, exponential, and triangular distributions:
./simulation_examples.py
```


## Installation

Clone the repository as above, and add the resulting directory to your `PYTHONPATH`:

```sh
cd efficient-resource-allocations
export PYTHONPATH=$(pwd)/efficient-resource-allocations:${PYTHONPATH}
```

Alternatively, you can copy the file
`efficient-resource-allocations/FirstAllocation.py` to a location already in
your `PYTHONPATH`.


## License

Copyright (C) 2016- The University of Notre Dame This software is distributed
under the GNU General Public License.  See the file COPYING for details.

