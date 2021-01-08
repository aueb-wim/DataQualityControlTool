# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from copy import deepcopy

from nltk import edit_distance

from mipqctool import config


# Module API

def getsubfolders(rootfolder):
    """Returns dict with keys subfolders and values a list
    of the containing dcm files in each folder."""
    dirtree = os.walk(rootfolder)
    result = {}
    for root, dirs, files in dirtree:
        del dirs  # Not used
        # Get all the visible subfolders
        for name in files:
            subfolder, filename = removeroot(os.path.join(root, name),
                                             rootfolder)
            if subfolder in result.keys():
                result[subfolder].append(filename)
            else:
                result[subfolder] = [filename]
    return result


def getsubfolders2list(rootfolder):
    """Returns dict with keys subfolders and values a list
    of the containing dcm files in each folder."""
    dirtree = os.walk(rootfolder)
    subfolders = set()
    result = []
    for root, dirs, files in dirtree:
        del dirs  # Not used
        # Get all the visible subfolders
        for name in files:
            subfolder, filename = removeroot(os.path.join(root, name),
                                             rootfolder)
            if subfolder in subfolders:
                result.append([subfolder, filename])
            else:
                result[subfolder] = [filename]
    return result


def removeroot(filepath, rootfolder):
    """Removes the root path from a given filepath."""
    subfolder = os.path.dirname(os.path.relpath(filepath, rootfolder))
    filename = os.path.basename(filepath)
    return (subfolder, filename)


def splitdict(bigdict, n):
    """Split a dictionary to n parts."""
    chunksize = len(bigdict) / float(n)
    for i in range(n):
        start = int(round(i * chunksize))
        end = int(round((i + 1) * chunksize))
        yield dict(list(bigdict.items())[start:end])


def expand_qcfield_descriptor(descriptor):
    descriptor = deepcopy(descriptor)
    descriptor.setdefault('MIPType', config.DEFAULT_QCFIELD_MIPTYPE)
    return descriptor


def edit_distance_f1(s1, s2, substitution_cost=1, transpositions=False) -> float:
    """A modified f1-like similarity measure based on lenenstein distance.
    The edit distance(ED) is considerd to be the number of True Negatives. 
    The True Positives(TP) is assumed that are equal to max(l1,l2) - ED, where
    l1, l2 the lenght of the s1, s2 strings. 
    As precision is calculated the TP / min(l1,l2) and recall TP / max(l1,l2)
    f1_score 2 * (precision * recall) / (precision + recall)
    
    :param s1, s2: The strings to be analysed
    :param transpositions: Whether to allow transposition edits
    :type s1: str
    :type s2: str
    :type substitution_cost: int
    :type transpositions: bool
    :rtype int
    """
    ed = edit_distance(s1, s2,
                       substitution_cost=substitution_cost,
                       transpositions=transpositions)
    l1 = len(s1)
    l2 = len(s2)
    found = max(l1, l2) - ed
    precision = found / min(l1, l2)
    recall = found / max(l1, l2)
    try:
        f1 = 2 * (precision * recall) / (precision + recall)
    except ZeroDivisionError:
        f1 = 0
    
    return f1
