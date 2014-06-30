#!/usr/bin/env python
__author__ = 'RackTop Systems'
__copyright__ = 'Copyright (c) 2014, RackTop Systems.'

""" System CPU stats collector """

import os
import sys
from common import kstat_fetch_metric, convert_kstat_string_to_map, make_nagios_output

# If keys returned will contain metrics for multiple of something, for example
# multiple CPU cores, where each is iterated with all the same metric points,
# set this to true, which will make sure that unique keys are correctly made.
os.environ["MVALUED"] = "true"

NAME        = "processor"
KEYS = ["cpu_stat:::anonfree", "cpu_stat:::anonpgin", "cpu_stat:::anonpgout", "cpu_stat:::as_fault",
        "cpu_stat:::bawrite", "cpu_stat:::bread", "cpu_stat:::bwrite", "cpu_stat:::cpumigrate", "cpu_stat:::dfree",
        "cpu_stat:::execfree", "cpu_stat:::execpgin", "cpu_stat:::execpgout", "cpu_stat:::fsfree", "cpu_stat:::fspgin",
        "cpu_stat:::fspgout", "cpu_stat:::swap", "cpu_stat:::swapin", "cpu_stat:::swapout", "cpu_stat:::physio",
        "cpu_stat:::rw_rdfails", "cpu_stat:::rw_wrfails", "cpu_stat:::scan", "cpu_stat:::pgin", "cpu_stat:::pgout",
        "cpu_stat:::intr", "cpu_stat:::intrblk", "cpu_stat:::intrthread", "cpu_stat:::inv_swtch", "cpu_stat:::iowait",
        "cpu_stat:::kernel", "cpu_stat:::syscall",]

def test():

    keys = " ".join(KEYS)
    result, _ = kstat_fetch_metric(keys)
    x = make_nagios_output(NAME, convert_kstat_string_to_map(result))
    print(x)

if __name__ == "__main__":
    sys.exit(test())