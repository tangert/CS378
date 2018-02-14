
from __future__ import division
from collections import Counter
import itertools as it
import time
import math
import sys

# globals
DATA_FILE_PATH = "T10I4D100K.dat"
MIN_SUPPORT = 35
TEST_LIMIT = 1000


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


######################################
# MARK: Speed / optimization functions
######################################
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


def filter_transactions(transactions, current_candidate):
    """
    returns a new reference database to check support counts for
    remove transaction if all items have been discarded
    """
    filtered_transactions = []

    # 1. discard infrequent items
    # if an item does not occur at least CANDIDATE_COUNT amount of times
    #  in the current candidate, discard

    # 2. discard transactions if all items are discarded

    return filtered_transactions


def get_min_support_itemset(itemset_count, min_support):

    min_support_itemset = set(item for item in itemset_count
                              if itemset_count[item] >= min_support)

    return min_support_itemset


#####################################
# MARK: Primary apriori set functions
#####################################
def get_itemset_support(transactions, itemsets):

    support_set = Counter()

    for trans in transactions:
        subsets = [itemset for itemset in itemsets if itemset <= trans]
        support_set.update(subsets)

    return support_set


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

    if size == 2:
        return set(it.combinations(itemset, 2))
    else:
        new_items = []
        seen_items = {}

        #used to avoid unnecessary unions when both items have already been seen
        for item in itemset:
            seen_items[item] = False

        for a in itemset:

            # mark the item as seen
            seen_items[a] = True

            for b in itemset:

                # check if the k-2 elements are the same to
                # check joining compatibility

                if a[:size - 2] == b[:size - 2] and a != b:

                    if seen_items[b] is False:

                        # only form the union if item b hasn't been seen before
                        union = set(a).union(set(b))
                        new_items.append(tuple(union))
                        seen_items[b] = True

        return set(new_items)


def prune(current_itemset, previous_itemset):
    """
    prunes an itemset by checking subsets
    if subset is infrequent/not in the previous itemset, that element is removed/
    not placed into the new itemset
    """
    pruned = set()

    # print "\n\nPREVIOUS ITEMSET FOR PRUNING: {}".format(previous_itemset)

    for item in current_itemset:
        subsets = set(it.combinations(item, len(item)-1))

        # filter out the subsets that are not included in the previous itemset
        for subset in subsets:

            # for some reason, checking subsets gets funky with elements
            # with more than 2 elements so have to do some preprcoessing

            if len(item)-1 == 1:
                subset = set(subset)
            else:
                subset = set([subset])

            if subset.issubset(previous_itemset):
                pruned.add(item)

    return pruned


def generate_candidate_set(itemset, size):
    """
    creates a new candidate set through self joining and pruning
    """

    # 1: self join on all of the cleaned data
    joined = self_join(itemset, size)
    print "JOINED LENGTH: {} || SET: {}".format(len(joined), joined)

    # 2: prune the remaining joined data
    #   previous itemset is the input
    #   current itemset is the newly joined set
    pruned = prune(joined, itemset)
    print "PRUNED CANDIDATE LENGTH: {} || SET: {}".format(len(pruned), pruned)

    # 3: return the final pruned list as the new candidate set
    return pruned


def apriori(transactions, min_support):
    """
    takes in data as a 2D array and runs the algorithm:
    1: create first candidate set
    2: generate new candidate set based on current candidate and increasing candidate count
    3: keep going until the length of the candidate is 0
    """

    # initialize current candidate set to the single frequent item set
    current_candidate = create_single_frequent_itemset(transactions, min_support)
    candidate_count = 1

    # filter the db references
    # new_db = filter_transactions(data, current_candidate)

    print "SINGLE FREQUENT ITEMSET LENGTH: {} ||| SET: {}".format(len(current_candidate), current_candidate)

    while len(current_candidate) != 0:
        print "\nCANDIDATE NUMBER: {}".format(candidate_count)

        # increment to increase the combination lengths
        candidate_count += 1

        # generate the current candidate based on the new count
        current_candidate = generate_candidate_set(current_candidate, candidate_count)

        # filtered_candidates = get_itemset_support(transactions, current_candidate)

        # current_candidate = get_min_support_itemset(filtered_candidates, min_support)

        print "\n"

    return current_candidate

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
    candidate = apriori(transactions, MIN_SUPPORT)

    print "\nFINAL CANDIDATE: {}".format(candidate)

    # done!
    print("--- %s seconds ---" % (time.time() - start_time))