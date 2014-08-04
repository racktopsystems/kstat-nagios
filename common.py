__author__ = 'RackTop Systems'
__copyright__ = 'Copyright (c) 2014, RackTop Systems.'

import re
import os
import subprocess
from subprocess import PIPE

import shlex
import string
from types import StringType

DEBUG           = False
REPEAT          = 1 if not "NAGIOS_REPEAT" in os.environ else int(os.environ["NAGIOS_REPEAT"])
HARD_LIMIT      = 60  # Do not allow more than 60 iterations
MULTIVARIATES   = ["cpu"]
SORTED          = {
    "yes"   : 1,
    "no"    : 0,
    "custom": -1
}


class FailedAcquireKstatMetric(Exception):
    pass


def limit_repeat(count):
    return count if count < HARD_LIMIT else HARD_LIMIT


def str_to_num(s):
    """ Function takes a string, and if it has a `.` assumes it is a float,
    else it must be an int. We apply proper conversion function to the string
    making it a number.

    :param s: string repesenting numeric value, float or integer
    :return: float or integer from given string
    """

    method = {
        "float":    string.atof,
        "int":      string.atoi
    }

    if not type(s) is StringType:
        return 0

    if "." in s:
        return method["float"](s)
    else:
        return method["int"](s, 10)


def str2bool(s):
    if s.lower() in ("yes", "true", "t", "1"):
        return True
    return False


def transform_key(s):

    slices = s.split(":")

    try:
        if str2bool(os.environ["MVALUED"]):
            return "_".join([slices[-1], slices[1]])
    except KeyError:
        pass
    return slices[-1]


def make_new_key(idx, key, d):
    """ Function is recursive, yes some hate recursion, but I come from ML and Scheme.
    This approach is more elegant than alternative.
    If a key already exists in the dict, just adding it again means we drop last value, not good.

    :param idx: integer - index, starting at 0, and will be incremented with each function call
    :param key: string - this is the key from the string conversion, i.e. `unix:0:system_pages:availrmem`
    :param d: dict - this is the dictionary where key/value mappings are being stored
    :return: string - newly created key, which should be unique
    """

    new_key = "%s_%d" % (key, idx)
    if new_key in d:
        return make_new_key(idx + 1, key, d)
    return new_key


def convert_kstat_string_to_map(metric_string):
    """ Function takes a string given back by kstat command and creates a
    key/value mapping of all items in the string. We split string on newlines `\n`,
    which is a per metric delimiter. And for each individual metric we split that
    string on tabs `\t`, since that is what separates key from value.

    :param metric_string:
    :return:
    """

    mdict = {}
    kstat_array = metric_string.split("\n")

    if len(kstat_array) < 1:
        return {}

    for entry in kstat_array:
        try:
            k, v = entry.split("\t")

            k = transform_key(k)  # Simplify the key, stripping off part of the namespace.

            if k in mdict:  # Update key to be unique, if one already exists in dict.
                k = make_new_key(0, k, mdict)

            mdict[k] = str_to_num(v)
        except ValueError:
            continue

    return mdict


def kstat_fetch_metric(metric_keys):
    """ Function takes a metric key, assuming valid and gets its metric from kstat.
    Yes, this is an ugly wrapper around kstat, but it is faster than doing anything else.

    Same rules of kstat apply, the less of a namespace we give here, the more data we get back,
    since this is basically regex matching of sorts.

    :param metric_key: string - example: unix:0:system_pages:availrmem
    :return: :raise FailedAcquireKstatMetric:
    """

    params = shlex.split("/usr/bin/kstat -p %s 1 %d" % (metric_keys, limit_repeat(REPEAT)))
    stats = subprocess.Popen(params, shell=False, bufsize=4096,
                             stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)

    stdout, stderr = stats.communicate()

    if stderr:
        raise FailedAcquireKstatMetric(metric_keys, REPEAT)

    return stdout, stderr


def make_nagios_output(label, d, sort=None):
    """ Function makes a string suitable for nagios to make sense of the data being passed.
    Mainly, we are taking a dict with key/values and building a key/value string
    where k/v pairs are being separated by `=` and each metric separated by `;` from next one.

    :param label: string - name of the collector to pass as the hint before the `|` symbol
    :param d: dict - k/v pairs are being read from this dict
    :return: string - a new string appropriate for nagios to process.
    """

    drop = lambda _: True if _ in ("snaptime", "crtime") else False  # Drop any snaptime and crtime keys
    atoms = []
    for k, v in d.items():
        if drop(k):
            continue
        else:
            atoms.append("%s=%s" % (k, v))  # Add key/value mapping as a string of strings joined with `=`.

    if not sort:  # No sorting if the argument is not specified at all.
        pass
    elif sort == -1:  # Custom sort, less likely than just normal sorting.
        atoms = sorted(atoms, cmp=comparator)  # Fixme: should pass sort function to make_nagios_output
    elif sort:  # This should be good enough in most cases.
        atoms = sorted(atoms)

    joined_metrics = "; ".join(atoms)
    return "%s|%s" % (label, joined_metrics)


def comparator(a, b):
    """ comparator takes two arguments, both being metrics such as `anonfree_0=0`, `anonfree_1=0`
    and returns a -1 or a 1 depending upon if the number that follows underscore `_` is larger in a or b.

    :param a: string - first of two items to compare; key/value pair joined with a `=`
    :param b: string - second of two items to compare; key/value pair joined with a `=`
    :return: int 1 if var a > var b, -1 if var a < var b and 0 if var a == var b
    """
    a = re.split("[_=]", a)[-2]
    b = re.split("[_=]", b)[-2]
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0

__ALL__ = ["kstat_fetch_metric", "convert_kstat_string_to_map", "make_nagios_output", "SORTED"]