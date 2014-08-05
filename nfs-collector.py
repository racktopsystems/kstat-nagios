#!/usr/bin/env python
__author__ = 'RackTop Systems'
__copyright__ = 'Copyright (c) 2014, RackTop Systems.'

""" System NFSv* filesystem stats collector """

import os
import sys
from common import kstat_fetch_metric, convert_kstat_string_to_map, make_nagios_output

# If keys returned will contain metrics for multiple of something, for example
# multiple CPU cores, where each is iterated with all the same metric points,
# set this to true, which will make sure that unique keys are correctly made.
os.environ["MVALUED"] = "false"

NAME = "nfs"
KEYS = ["unix:0:vopstats_nfs3:",
        # "unix:0:vopstats_nfs4:",  # If using NFSv4, uncomment this line
        ]

def test():

    keys = " ".join(KEYS)
    result, _ = kstat_fetch_metric(keys)
    x = make_nagios_output(NAME, convert_kstat_string_to_map(result))
    print(x)

if __name__ == "__main__":
    sys.exit(test())