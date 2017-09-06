from __future__ import print_function, division, unicode_literals
import shutil
import re
import os


# ==============================================================================
#                                                              MAYBE_MAKE_PARDIR
# ==============================================================================
def maybe_make_pardir(file):
    """ Takes a path to a file, and creates the necessary directory structure
        on the system to ensure that the parent directory exists (if it does
        not already exist)
    """
    pardir = os.path.dirname(file)
    if pardir.strip() != "": # ensure pardir is not an empty string
        if not os.path.exists(pardir):
            os.makedirs(pardir)


# ==============================================================================
#                                                                       FILE2STR
# ==============================================================================
def file2str(f):
    with open(f, "r") as textFile:
        return textFile.read()


# ==============================================================================
#                                                                       STR2FILE
# ==============================================================================
def str2file(s, file):
    maybe_make_pardir(file)
    with open(file, mode="w") as textFile:
        textFile.write(s)


