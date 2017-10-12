#! /usr/bin/env python
# Copyright (C) 2017- The University of Notre Dame This software is distributed
# under the GNU General Public License.  See the file COPYING for details.

from FirstAllocation import  FirstAllocation
import sys
import csv

resources = ['cores', 'memory', 'disk']

steps     = {'cores'  : 1,
             'memory' : 50,   # group by [ 50i, 50(i+1) ) MB
             'disk'   : 50,   # group by [ 50i, 50(i+1) ) MB
             'time'   : 360   # group by [ 360i, 360(i+1) ) s (5 min)
             }


def read_input(filename):
  # Create an empty set of categories
  categories = {}

  all_cs = get_category(categories, '(all)')

  # Read resource report summaries as comma separated values, and add them to
  # the set of categories.
  with open(input_name) as cvsfile:
    reader = csv.DictReader(cvsfile)
    for row in reader:

        c = get_category(categories, row['category'])

        time  = float(row['wall_time'])
        for r in resources:
            value = float(row[r])
            fa = c[r]
            fa.add_data_point(value = value, time = time)
            all_cs[r].add_data_point(value = value, time = time)

  return categories


def get_category(categories, category): 
    if not categories.has_key(category):
        categories[category] = {}
        for r in resources:
            categories[category][r] = FirstAllocation(name = r,
                    value_resolution = steps[r],
                    time_resolution  = steps['time'])

    return categories[category] 



def report_allocations(fa):
    for mode in ['throughput', 'waste', 'fixed']:
        allocation = fa.first_allocation(mode)
        maximum    = fa.maximum_seen
        count      = fa.count
        retries    = fa.retries(allocation)
        waste      = fa.wastepercentage(allocation)
        throughput = fa.throughput(allocation)
        base_throughput = fa.throughput(maximum)

        print_row(mode, allocation, maximum, throughput/base_throughput, waste, retries, count)


def print_row(mode, allocation, maximum, throughput, waste, retries, count):
  print '%-10s: %5d %6.2lf %6.2lf %6d/%-5d' % (mode, allocation, throughput, waste, retries, count)

def print_header(category, resource):
  print '\n%s --- %s' % (category, resource)
  print '%-10s: %5s %6s %6s %6s/%-5s' % ('mode', 'alloc', 'throu', 'waste', 'retry', 'count')


if __name__ == '__main__':

  try:
    input_name = sys.argv[1]
  except IndexError:
    sys.stderr.write('Use: %s name-of-input.csv\n' % (sys.argv[0],))
    sys.stderr.flush()
    sys.exit(1)

  categories = read_input(input_name)

  for category in categories.keys():
    for resource in ['memory', 'disk', 'cores']:
      print_header(category, resource)
      report_allocations(categories[category][resource])

