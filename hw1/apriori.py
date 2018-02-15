
from __future__ import division
from collections import Counter
import itertools as it
import time
import math
import sys

# globals
DATA_FILE_PATH = "T10I4D100K.dat"
MIN_SUPPORT = 500
TEST_LIMIT = 99999

##########################################
# MARK: File conversion and output methods
##########################################

def convert(filename):
    """
    Converts every line (transaction) in the DAT file into a 2D array
    """
    data = []

    for line in open(filename, 'r'):
        if len(data) < TEST_LIMIT:
            data.append(line.rstrip().split(" "))
        else:
            return data

    # for line in open(filename, 'r'):
    #     data.append(line.rstrip().split(" "))
    #
    # return data


def save_output():
    print "output"


######################################
# MARK: Speed / optimization functions
######################################

########
def create_single_frequent_itemset(transactions, min_support):
    """
     special method to handle creating a single itemset at first

     1. gets the item counts
     2. count how many times it shows up for each transaction
     3. if that count is above the min_support, add it to the frequent itemset
    """

    item_counts = Counter()

    for transaction in transactions:
        item_counts.update(transaction)

    frequent_item_set = set(item for item in item_counts
                            if item_counts[item] >= min_support)
    return frequent_item_set

#######
# Multi item set functions
def filter_transactions(transactions, current_candidate, first_candidate=True):
    """
    returns a new reference database to check support counts for
    remove transaction if all items have been discarded
    """
    filtered_transactions = []
    current_items = set()

    if not first_candidate:
        for subset in current_candidate:
            current_items = current_items.union(subset)
    else:
        current_items = current_candidate

    for transaction in transactions:
        all_found = True
        for item in transaction:
            if item not in current_items and all_found:
                all_found = False
        if all_found:
            # print "transaction's items all in current items!: {}".format(transaction)
            filtered_transactions.append(transaction)

    print "Filtered length: {}".format(len(filtered_transactions))

    return filtered_transactions


def get_supported_itemset(current_candidate, supports, min_support):
    """"
    returns the supported item set based on the counter
    """
    itemset = set()

    for item in current_candidate:
        if supports[str(item)] >= min_support:
            itemset.add(item)

    return itemset


def get_itemset_supports(transactions, itemset, candidate_count):

    """
    returns a counter filled with all items and their support counts
    """
    supports = {}

    for item in itemset:
        supports[str(item)] = 0

    for trans in transactions:

        # print "refererence transaction: {}".format(trans)
        # print "ref itemset: {}".format(itemset)

        for item in itemset:

            all_found = True

            if candidate_count < 2:
                if item not in trans:
                    all_found = False
            else:
                for sub_item in item:
                    if sub_item not in trans and all_found:
                        # print "subitem {} for item: {} NOT FOUND IN {}".format(sub_item, item, trans)
                        all_found = False
                    # else:
                    #     print "item {} found in {}".format(item, trans)
            if all_found:
                supports[str(item)] += 1

    return supports

#####################################
# MARK: Primary apriori set functions
#####################################
def self_join(itemset, candidate_count):
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

    if candidate_count == 2:
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

                if a[:candidate_count - 2] == b[:candidate_count - 2] and a != b:

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


def generate_candidate_set(transactions, min_support, itemset, candidate_count):
    """
    creates a new candidate set through self joining and pruning
    """

    joined = self_join(itemset, candidate_count)
    print "JOINED LENGTH: {}".format(len(joined))

    pruned = prune(joined, itemset)
    print "PRUNED LENGTH: {}".format(len(pruned))

    supports = get_itemset_supports(transactions, pruned, candidate_count)
    print "supports: {}".format(supports)
    support_set = get_supported_itemset(pruned, supports, min_support)
    print "SUPPORTED LENGTH: {} || SET: {}".format(len(support_set), support_set)

    return support_set


def apriori(transactions, min_support):
    """
    takes in data as a 2D array and runs the algorithm:
    1: create first candidate set
    2: generate new candidate set based on current candidate and increasing candidate count
    3: keep going until the length of the candidate is 0
    """

    # initialize current candidate set to the single frequent item set
    #start with the initial full transaction db

    print "INITIAL TRANSACTION DB LENGTH: {}".format(len(transactions))

    current_candidate = create_single_frequent_itemset(transactions, min_support)
    candidate_count = 1
    transactions = filter_transactions(transactions, current_candidate, first_candidate=True)

    print "CURRENT TRANSACTIONS LENGTH: {}".format(len(transactions))

    # filter the db references
    # new_db = filter_transactions(data, current_candidate)

    final_candidate = set()

    while len(current_candidate) != 0:

        # increment to increase the combination lengths
        candidate_count += 1

        print "\nCANDIDATE NUMBER: {}".format(candidate_count)

        #store the final candidate before it gets updated
        final_candidate = current_candidate

        # generate the current candidate based on the new count
        current_candidate = generate_candidate_set(transactions, min_support, current_candidate, candidate_count)
        transactions = filter_transactions(transactions, current_candidate,first_candidate=False)

        print "CURRENT TRANSACTIONS LENGTH: {}".format(len(transactions))

    return final_candidate

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