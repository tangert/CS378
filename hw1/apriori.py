
from __future__ import division
from collections import Counter
import itertools as it
import time
import math
import sys

# globals
DATA_FILE_PATH = "T10I4D100K.dat"
MIN_SUPPORT = 3
TEST_LIMIT = 500

def convert(filename):
    """
    Converts every line (transaction) in the DAT file into a 2D array
    """
    transactions = []

    for line in open(filename, 'r'):
        if len(transactions) < TEST_LIMIT:
            transactions.append(line.rstrip().split(" "))
        else:
            return transactions

def get_support(item, itemset):
    """
     calculates the frequency of an item's elements in an itemset by
     checking each transaction

     EX:
     item: ABC
     itemset: {
        ABCD
        ABEC
        ABC
        BCD
     }

     SUPPORT: 3 {
      [ABC]D,
      [AB]E[C],
      [ABC]
      }
    """

def prune(itemset):
    """
    prunes an itemset by checking subsets
    if subset is infrequent/not in the previous itemset, that element is removed/
    not placed into the new itemset

    returns back a new itemset pruned

    EX:

    { abc, abd, acd, ace, bcd }
    join = union
    union abc and abd, = abcd
    union acd and ace = acde
    drop bcd
    """

    return set()

def self_join(itemset):
    """
     goes through an itemset and forms unions on each element with the next
     as long as the k-1 elements are the same

    EX:
    abcd = abc, abd, bcd
    acde =  || ade  ||, acd
    ade is not in Lk-1, so acde is pruned out
    """

    return set()

def generate_candidate_set(itemset):
    """
    creates a new candidate set through self joining and pruning
    """
    joined = self_join(itemset)
    return prune(joined)

# MARK: Main apriori algorithm functions
def apriori(data, min_support):
    """
    takes in data as a 2D array and runs the algorithm:

    you are consistently pruning/editing 2 data structures:
    1. the candidate set
    2. the original transaction db

    CONCEPTUALLY:

    1:
    find all of the single item sets


    """



if __name__ == '__main__':

    # command line arguments
    # INPUT_DATA = sys.argv[0]
    # MIN_SUPPORT = sys.argv[1]
    # OUTPUT_FILE = sys.argv[2]

    # turn the transactions into a 2D array
    transactions = convert(DATA_FILE_PATH)

    # measure the start time
    start_time = time.time()

    # run the algorithm
    apriori(transactions, MIN_SUPPORT)

    # done!
    print("--- %s seconds ---" % (time.time() - start_time))