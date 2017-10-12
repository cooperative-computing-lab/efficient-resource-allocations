#! /usr/bin/env python
#
# Copyright (C) 2017- The University of Notre Dame This software is distributed
# under the GNU General Public License.  See the file COPYING for details.

from FirstAllocation import FirstAllocation

import random
import sys

# Generate syntetic resource samples according to beta(2, 5)
def beta(start, end, alpha = 1.5, beta = 10):
    return int((end - start) * random.betavariate(alpha, beta)) + start

# Generate syntetic resource samples according to exp(1.25)
def exponential(start, end, lambd = 1.25):
    return int((end - start) * random.expovariate(lambd)) + start

# Generate syntetic resource samples according to triangular(0.1)
def triangular(start, end, mode = 0.1):
    return int(random.triangular(start, end, start + mode*(end - start)))

if __name__ == '__main__':
    # set seed so that we can compare runs.
    random.seed(42)

    # wall time in seconds. For this examples, all jobs execute exactly with
    # the same duration. (Any positive value here would do. Units should only
    # be consistent across data points.)
    wall_time   = 1

    # min memory, say in MB
    memory_min  = 50

    # max memory, say in MB
    memory_max  = 10000

    # number of memory samples to generate
    number_of_samples = 10

    # generate samples according to the beta distribution, grouping memory each
    # 50 MB
    name = "memory beta(%d,%d)" % (memory_min, memory_max)
    fa_beta = FirstAllocation(name = name, value_resolution = 50)
    while(fa_beta.count < number_of_samples):
        value = beta(memory_min, memory_max)
        fa_beta.add_data_point(value = value, time = wall_time)

    # generate samples according to the exponential distribution
    name = "memory exponential(%d,%d)" % (memory_min, memory_max)
    fa_exp = FirstAllocation(name = name, value_resolution = 50)
    while(fa_exp.count < number_of_samples):
        value = exponential(memory_min, memory_max)
        fa_exp.add_data_point(value = value, time = wall_time)

    # generate samples according to the exponential distribution
    name = "memory triangular(%d,%d)" % (memory_min, memory_max)
    fa_tra = FirstAllocation(name = name, value_resolution = 50)
    while(fa_tra.count < number_of_samples):
        value = triangular(memory_min, memory_max)
        fa_tra.add_data_point(value = value, time = wall_time)

    # print the first allocations found
    for fa in [fa_beta, fa_exp, fa_tra]:
        print "--- %s ---" % (fa.name,)
        print '%-15s: %5s %5s %5s %5s' % ('mode', 'alloc', 'throu', 'waste', 'retry')

        # we will compare the throughput to that one that use the maximum value
        # seen.
        throughput_base = fa.throughput(fa.maximum_seen)

        for mode in ['fixed', 'throughput', 'waste']:
            allocation = fa.first_allocation(mode)
            waste      = fa.wastepercentage(allocation)
            throughput = fa.throughput(allocation) / throughput_base
            retries    = fa.retries(allocation)
            print '%-15s: %5d %5.2f %5.0f%% %5.0f%%' % (mode, allocation, throughput, waste, retries)

    sys.exit(0)

