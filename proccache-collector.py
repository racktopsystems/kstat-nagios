#!/usr/bin/env python
__author__ = 'RackTop Systems'
__copyright__ = 'Copyright (c) 2014, RackTop Systems.'

""" System Process cache stats collector """

import os
import sys
from common import kstat_fetch_metric, convert_kstat_string_to_map, make_nagios_output

# If keys returned will contain metrics for multiple of something, for example
# multiple CPU cores, where each is iterated with all the same metric points,
# set this to true, which will make sure that unique keys are correctly made.
os.environ["MVALUED"] = "false"

NAME = "proc-cache"
KEYS = ["unix:0:process_cache:alloc",
        "unix:0:process_cache:free",
        "unix:0:process_cache:slab_size",
        "unix:0:process_cache:buf_inuse",
        "unix:0:process_cache:buf_total"]

def test():

    keys = " ".join(KEYS)
    result, _ = kstat_fetch_metric(keys)
    x = make_nagios_output(NAME, convert_kstat_string_to_map(result))
    print(x)

if __name__ == "__main__":
    sys.exit(test())