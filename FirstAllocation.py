# Copyright (C) 2017- The University of Notre Dame This software is distributed
# under the GNU General Public License.
# See the file COPYING for details.
#
## @package FirstAllocation
#

import math


##
# Class to collect all of the usage data points of a resource, and to compute
# efficient allocations. A data point consists of the peak resource usage of a
# job, and the duration the job was executing:
#
# @code
# fa = FirstAllocation(name = 'my memory allocations')
# fa.add_data_point(value = 200, time = 60)
# fa.add_data_point(value = 400, time = 183)
# # (etc.)
# print fa.first_allocation(mode = 'throughput')
# print fa.first_allocation(mode = 'waste')
# print fa.first_allocation(mode = 'fixed')
# @endcode
#

class FirstAllocation:
    ##
    # @param self                Reference to the current object.
    # @param name                Arbitrary string to describe this data set
    # @param value_resolution    Discretize resource values to this resolution 
    # @param time_resolution     Discretize resource time values to this resolution 
    def __init__(self, name, value_resolution = 1, time_resolution = 1):
        self.value_resolution = value_resolution
        self.time_resolution  = time_resolution

        self.label = name
        self.maximum = None

        self.values = []
        self.times  = []

        self.histogram = {}

    ##
    # Return the string describing this data set.
    # @param self                Reference to the current object.
    # @code
    # print fa.name
    # @endcode
    @property
    def name(self):
        return self.label

    ##
    # Return the number of data points.
    # @param self                Reference to the current object.
    # @code
    # print fa.count
    # @endcode
    @property
    def count(self):
        return len(self.values)

    ##
    # Return the maximum value seen.
    # @param self                Reference to the current object.
    # @code
    # print fa.maximum_seen
    # @endcode
    @property
    def maximum_seen(self):
        return self.maximum



    ##
    # Add a data point.
    # @param self                Reference to the current object.
    # @param value               Peak resource usage of a job.
    # @param time                Duration of the job.
    #
    # Units should be consistent across data points.
    #
    # @code
    # print fa.add_data_point(value = 50, time = 360)
    # @endcode
    def add_data_point(self, value, time):
        self.values.append(value)
        self.times.append(time)

        value_bucket = math.ceil(float(value)/self.value_resolution) * self.value_resolution
        time_bucket  = math.ceil(float(time)/self.time_resolution) * self.time_resolution

        if not self.maximum or self.maximum < value_bucket:
            self.maximum = value_bucket

        if not self.histogram.has_key(value_bucket):
            self.histogram[value_bucket] = {}

        if not self.histogram[value_bucket].has_key(time_bucket):
            self.histogram[value_bucket][time_bucket] = 0

        self.histogram[value_bucket][time_bucket] += 1

        return self.histogram[value_bucket][time_bucket]


    ##
    # Compute and return the first allocation.
    #
    # @param self                Reference to the current object.
    # @param mode                Optimization mode. One of 'throughput', 'waste', or 'fixed'.
    #
    # @code
    # v = fa.first_allocation(mode = 'throughput')
    # @endcode
    def first_allocation(self, mode = 'throughput'):
        valid_modes = ['throughput', 'waste', 'fixed']

        if mode == 'fixed':
            return self.maximum_seen
        elif mode == 'throughput':
            return self.__first_allocation_by_throughput()
        elif mode == 'waste':
            return self.__first_allocation_by_waste()
        else:
            raise ValueError('mode not one of %s', ','.join(valid_modes))

    ##
    # Return the waste (unit x time) that would be produced if the accumulated
    # values were run under the given allocation.
    #
    # @param self                Reference to the current object.
    # @param allocation          Value of allocation to test.
    def waste(self, allocation):
        waste = 0
        for i in xrange(0,len(self.values)):
            v = self.values[i]
            t = self.times[i]

            if v <= allocation:
                waste += t * (allocation - v)
            else:
                waste += t * (allocation + self.maximum_seen - v)
        return waste

    ##
    # Return the usage (unit x time) if the accumulated values were run under
    # the given allocation.
    #
    # @param self                Reference to the current object.
    def usage(self):
        usage = 0
        for i in xrange(0,len(self.values)):
            v = self.values[i]
            t = self.times[i]
            usage += t * v
        return usage

    ##
    # Return the percentage of wasted resources that would be produced if the accumulated
    # values were run under the given allocation.
    #
    # @param self                Reference to the current object.
    # @param allocation          Value of allocation to test.
    def wastepercentage(self, allocation):
        waste = self.waste(allocation)
        usage = self.usage()

        return (100.0 * waste)/(waste + usage)

    ##
    # Return the throughput of a single node if the accumulated values values
    # were run under the given allocation. Assumes an infinite number of tasks.
    #
    # @param self                Reference to the current object.
    # @param allocation          Value of allocation to test.
    def throughput(self, allocation):
        maximum = float(self.maximum_seen)

        tasks      = 0
        total_time = 0

        for i in xrange(0,len(self.values)):
            v = self.values[i]
            t = self.times[i]

            if v <= allocation:
                tasks      += maximum/allocation
                total_time += t
            else:
                tasks      += 1
                total_time += 2*t

        return tasks/total_time


    ##
    # Return the number of tasks that would be retried if the accumulated
    # values were run under the given allocation.
    #
    # @param self                Reference to the current object.
    # @param allocation          Value of allocation to test.
    def retries(self, allocation):
        retries = 0
        for v in self.values:
            if v > allocation:
                retries += 1
        return retries


    def __first_allocation_by_waste(self):
        values = self.histogram.keys()

        # computation below is easier if values are sorted in reversed.
        values.sort(reverse = True)
        times  = [ self.__accum_times_per_value(value) for value in values ]

        n = len(values)

        # average time for jobs with usage larger than value[i]
        running_avg = [0] * n
        for i in xrange(1, n):
            running_avg[i] = running_avg[i - 1] + times[i - 1]/self.count

        # average time for all jobs
        tb = running_avg[-1] + times[-1]/self.count

        # maximum value seen
        am = values[0]
        a  = am
        Ea = a*tb

        # compute the argmin for the allocation
        for i in xrange(0, n):
            ai = values[i]
            ti = running_avg[i]

            # See Equation 1 in 'A Job Sizing Strategy for High-Throughput Scientific Workflows'
            Eai = ai*tb + am*ti

            if Eai < Ea:
                Ea = Eai
                a  = ai
        return a


    def __first_allocation_by_throughput(self):
        values = self.histogram.keys()

        # computation below is easier if values are sorted in reversed.
        values.sort(reverse = True)
        times  = [ self.__accum_times_per_value(value) for value in values ]
        counts = [ self.__count_of_value(value) for value in values ]

        n = len(values)

        #Pa[i] is P(X > values[i])
        Pa = [0] * n
        Pa[-1] = self.count

        for i in xrange(1, n):
            Pa[i] = float(counts[i-1])/self.count + Pa[i-1] 

        # average time for jobs with usage larger than value[i]
        running_avg = [0] * n
        for i in xrange(1, n):
            running_avg[i] = running_avg[i - 1] + times[i - 1]/self.count

        # average time for all jobs
        tb = running_avg[-1] + times[-1]/self.count

        # maximum value seen
        am = values[0]
        a  = am
        Ea = ((am/a)*(1 - Pa[0]) + Pa[0])/tb

        # compute the argmax of the allocation
        for i in xrange(0, n):
            ai = values[i]
            ti = running_avg[i]
            Pi = Pa[i]

            # See Equation 3 in 'A Job Sizing Strategy for High-Throughput Scientific Workflows'
            Eai = ((am/ai)*(1 - Pi) + Pi)/(tb + ti)

            if Eai > Ea:
                Ea = Eai
                a  = ai
        return a



    def __count_of_value(self, value):
        count = 0
        for time in self.histogram[value].keys():
            count += self.histogram[value][time]
        return count

    def __accum_times_per_value(self, value):
        total_time = 0
        for time in self.histogram[value].keys():
            count = self.histogram[value][time]
            total_time += count * time
        return total_time



