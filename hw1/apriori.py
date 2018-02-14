
from __future__ import division
from collections import Counter
import itertools as it
import time
import math
import sys

# globals
DATA_FILE_PATH = "T10I4D100K.dat"
MIN_SUPPORT = 20
TEST_LIMIT = 500


##########################################
# MARK: File conversion and output methods
##########################################

def convert(filename):
    """
    Converts every line (transaction) in the DAT file into a 2D array
    """

    """
    when done testing, use the one line version:

       data = [line.rstrip().split(" ") for line in open(filename, 'r')]
       return data
    """

    data = []

    for line in open(filename, 'r'):
        if len(data) < TEST_LIMIT:
            data.append(line.rstrip().split(" "))
        else:
            return data


def save_output():
    print "output"


################################
# MARK: Helper methods for speed
################################
def get_item_count(items):
    """
    takes in a list and returns the amount of times each element appears
    """
    distinct = Counter()

    for item in items:
        distinct.update(item)

    return distinct


def create_single_frequent_itemset(transactions, min_support):
    """
     special method to handle creating a single itemset at first

     1. gets the item counts
     2. count how many times it shows up for each transaction
     3. if that count is above the min_support, add it to the frequent itemset
    """

    item_counts = get_item_count(transactions)
    frequent_item_set = set(item for item in item_counts
                            if item_counts[item] >= min_support)
    return frequent_item_set


def filter_transactions(data, filtered_items):
    """
    returns a new reference database to check support counts for
    filtered by removing all of the transactions with infrequent itemsets from the previous candidate set
    """


#####################################
# MARK: Primary apriori set functions
#####################################

def get_support(input_item, itemset):
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
    support = 0

    for item in itemset:
        """
        check if each element in the input_item is in the item
        if it is, update the counter
        """
        all_items_found = True

        for sub_item in input_item:
            if item not in sub_item:
                all_items_found = False

        if all_items_found:
            support += 1

    return support

def self_join(itemset, size):
    """
     goes through an itemset and forms unions on each element with the next
     as long as the k-1 elements are the same

    EX:

    { abc, abd, acd, ace, bcd }
    {
    join = union
    union abc and abd, = abcd
    union acd and ace = acde
    drop bcd

    """
    itemset = sorted(itemset)

    if size == 2:
        return set(it.combinations(itemset,2))
    else:

        #store which prefixes (of length size-1) occur
        prefix_counts = Counter()

        #store the actual joined tuples
        joins = set()

        print "size greater than 2"
        print "INPUT ITEMSET FOR JOINING: {}".format(itemset)

        for item in itemset:
            prefix_counts.update(item[:size-2])

        itemset = filter(lambda item: , itemset)
        """
        find all unions of elements
        if the prefix of that element has a count higher than one
        essentiall conditional combinations.
        """

        print prefix_counts

    return set()

def prune(current_itemset, previous_itemset):
    """
    prunes an itemset by checking subsets
    if subset is infrequent/not in the previous itemset, that element is removed/
    not placed into the new itemset

    returns back a new itemset pruned

    EX:
    abcd = abc, abd, bcd
    acde =  || ade  ||, acd
    ade is not in Lk-1, so acde is pruned out
    """
    pruned = set()

    for item in current_itemset:
        subsets = set(it.combinations(item, len(item)-1))
        for subset in subsets:
            if previous_itemset.issuperset(subset) and not pruned.issuperset(item):
                pruned.add(item)

    return pruned

def generate_candidate_set(itemset, size):
    """
    creates a new candidate set through self joining and pruning
    """

    # 1: remove all items from itemset that don't meet the min_support
    supported = set(itemset)
    print "SUPPORTED: {}".format(supported)

    # 2 : self join on all of the cleaned data
    joined = self_join(supported, size)
    print "JOINED LENGTH: {} || SET: {}".format(len(joined), joined)

    # 3: prune the remaining joined data
    #previous itemset is the input
    #current itemset is the newly joined set
    pruned = prune(joined, itemset)
    print "PRUNED LENGTH: {} || SET: {}".format(len(pruned), pruned)

    # 4: return the final pruned list as the new candidate set
    return pruned


def apriori(data, min_support):
    """
    takes in data as a 2D array and runs the algorithm:

    you are consistently pruning/editing 2 data structures:
    1. the candidate set
    2. the original transaction db
        remove transaction

    CONCEPTUALLY:

    1: CREATE FIRST CANDIDATE SET
    2(LOOP): CHECK EACH CONSECUTIVE NEW SET
    """

    # initialize current candidate set to the single frequent item set
    current_candidate = create_single_frequent_itemset(data, min_support)
    previous_candidate = set()

    print "SINGLE FREQUENT ITEMSET LENGTH: {} ||| SET: {}".format(len(current_candidate), current_candidate)

    # filter the db references
    new_db = filter_transactions(data, current_candidate)

    # initialize the candidate_count to 2
    candidate_count = 2

    # now that we have the frequent first frequent item set, we will start our loop
    current_candidate = generate_candidate_set(current_candidate, candidate_count)

    print "\n"
    candidate_count+=1
    current_candidate = generate_candidate_set(current_candidate, candidate_count)

# while len(current_candidate) != 0:
    #
    #     current_candidate = generate_candidate_set(current_candidate, candidate_count)
    #
    #     # previous_candidate = current_candidate.copy()
    #
    # return previous_candidate
#####################################
# MARK: MAIN
#####################################

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