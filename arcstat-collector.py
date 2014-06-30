#!/usr/bin/env python
__author__ = 'RackTop Systems'
__copyright__ = 'Copyright (c) 2014, RackTop Systems.'

""" System ZFS (ARC-specific) filesystem stats collector """

import os
import sys
from common import kstat_fetch_metric, convert_kstat_string_to_map, make_nagios_output

# If keys returned will contain metrics for multiple of something, for example
# multiple CPU cores, where each is iterated with all the same metric points,
# set this to true, which will make sure that unique keys are correctly made.
os.environ["MVALUED"] = "false"

NAME = "arcstat"
KEYS = ["zfs:0:arcstats:deleted", "zfs:0:arcstats:c", "zfs:0:arcstats:p", "zfs:0:arcstats:size",
        "zfs:0:arcstats:data_size", "zfs:0:arcstats:mfu_ghost_hits",
        "zfs:0:arcstats:mru_ghost_hits", "zfs:0:arcstats:mfu_hits", "zfs:0:arcstats:mru_hits", "zfs:0:arcstats:hits",
        "zfs:0:arcstats:misses", "zfs:0:arcstats:memory_throttle_count", ]

def test():

    keys = " ".join(KEYS)
    result, _ = kstat_fetch_metric(keys)
    x = make_nagios_output(NAME, convert_kstat_string_to_map(result))
    print(x)

if __name__ == "__main__":
    sys.exit(test())