# THIS CODE IS MY OWN WORK AND WAS WRITTEN WITHOUT CONSULTING A TUTOR OR CODE WRITTEN BY OTHER STUDENTS
# -TYLER ANGERT

from __future__ import division
from collections import Counter
import itertools as it
import time
import sys

# global for storing candidates
ALL_CANDIDATES = []

##########################################
# MARK: File conversion and output methods
##########################################

def convert(filename):
    # converts every line in the dat file into a huge 2D array
    data = []
    for line in open("{}".format(filename), 'r'):
        data.append(line.rstrip().split(" "))
    return data

def save_output(candidates, file_name):

    output = open(file_name,"w+")

    for i in range(0, len(candidates)):
        if i > 0:
            for item in sorted(candidates[i]):
                output_str = ""

                for subitem in item:
                    output_str += "{} ".format(subitem)

                print output_str
                output.write("{} ({})\n".format(output_str, candidates[i][item]))
        else:
            for item in sorted(candidates[i]):
                print item
                output.write("{} ({})\n".format(item, candidates[i][item]))


######################################
# MARK: Speed / optimization functions
######################################

########
def create_single_frequent_itemset(transactions, min_support):

    item_counts = Counter()

    for transaction in transactions:
        item_counts.update(transaction)

    frequents = Counter(item for item in item_counts
                            if item_counts[item] >= min_support)

    for item in frequents:
        frequents[item] = item_counts[item]

    return frequents

def create_double_frequent_itemset(transactions, min_support):

    item_counts = Counter()

    # go through each transaction
    # count all of the combinations of two from each transaction as you go

    for transaction_group in transactions:
        for transaction in transaction_group:
            combos = set(it.combinations(transaction,2))
            for combo in combos:
                item_counts.update([combo])

    frequents = Counter(item for item in item_counts
                        if item_counts[item] >= min_support)

    for item in frequents:
        frequents[item] = item_counts[item]

    return frequents

# Multi item set functions
def filter_transactions(transactions, current_candidate, first_candidate=True):
    """
    returns a new reference database to check support counts for
    remove transaction if all items have been discarded
    #removes elements from each transaction that are not in the itemset at all
    #sorts the transactions by length, then groups them into groups of other
    transactions by that length for easy indexing
    """
    filtered_transactions = []
    current_items = set()

    if not first_candidate:
        for subset in current_candidate:
            current_items = current_items.union(subset)
    else:
        current_items = set(current_candidate)

    if first_candidate:
        for transaction in transactions:
                at_least_one_found = False

                for item in transaction:

                    if item in current_items:
                        at_least_one_found = True
                        break

                if at_least_one_found:
                    filtered = list(filter(lambda x: x in current_candidate, transaction))
                    filtered_transactions.append(filtered)

    else:
        # Once past the first group, everything is sorted into different length transactions
        for transaction_group in transactions:
            for transaction in transaction_group:

                at_least_one_found = False

                for item in transaction:
                    if item in current_items:
                        at_least_one_found = True
                        break

                if at_least_one_found:
                    filtered = list(filter(lambda x: x in current_candidate, transaction))
                    filtered_transactions.append(filtered)

    # sort them by length
    filtered_transactions = sorted(filtered_transactions, key=len)

    # split into subarrays also by length
    sublist = []
    total_transaction_list = []

    # now the transactions are sorted and arranged into groups by actual transaction length
    for i in range(0,len(filtered_transactions)-1):
        if len(filtered_transactions[i]) == len(filtered_transactions[i+1]):
            sublist.append(filtered_transactions[i])
        else:
            sublist.append(filtered_transactions[i])
            total_transaction_list.append(sublist)
            sublist = []

    return total_transaction_list

def get_supported_itemset(supports, min_support):
    """"
    returns the supported item set based on the counter
    """
    itemset = set()

    for item in supports:
        if supports[item] >= min_support:
            itemset.add(item)

    return itemset


def get_itemset_supports(transactions, itemset, candidate_count, min_support):

    """
    returns a counter filled with all items and their support counts
    """

    #dont check supersets of items with infrequent items
    #these combos are all made from frequent singles tho

    support_counter = Counter()
    start_time = time.time()

    # keep counts for individual elements
    subitem_counter = Counter()

    print "start time support counter: {}".format(start_time)
    print "Itemset: {}".format(itemset)

    # infrequent_items = []
    # store infrequent items as you go
    # if the next item contains either element ? no

    infrequent_item_transactions = {}
    itemset = sorted(itemset)

    #obviously you dont have to check every single combination
    #so if you go through all of the transactions for an item and find which item causes it to be infrequent

    for item in itemset:

        # initialize how many transactions ahve been found
        trans_count = 1

        # go through each of the transaction groups
        # each group represents an increasing length of the transactions inside, e.g.:
        # transactions[0] = all transactions of length 1
        # transactions[1] = all transactions of length 2, etc
        # this allows you to easily skip over entire groups of transactions that are shorter in length than the items you are checking

        for transaction_group_index in range(0, len(transactions)):

            if len(item) <= transaction_group_index+1:
                for trans in transactions[transaction_group_index]:

                        trans_count += 1

                        # assume all sub_elements found
                        all_found = True

                        for subitem in item:
                            if subitem not in trans:
                                all_found = False
                                break

                        #went through each item and found everything
                        if all_found:
                            support_counter.update([item])
            else:
                continue

    print "end time support counter: {}".format(time.time()-start_time)

    return support_counter

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

    new_items = []
    seen_items = {}

    # used to avoid unnecessary unions when both items have already been seen
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

                    #only add the union if it meets the support criteria?

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

    supports = get_itemset_supports(transactions, pruned, candidate_count, min_support)
    print "SUPPORTS: {}".format(supports)

    ALL_CANDIDATES.append(supports)

    supported_itemset = get_supported_itemset(supports, min_support)
    print "SUPPORTED SET: {}".format(supported_itemset)

    return supported_itemset


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
    ALL_CANDIDATES.append(current_candidate)

    final_candidate = current_candidate
    candidate_count = 1
    transactions = filter_transactions(transactions, current_candidate, first_candidate=True)

    current_candidate = create_double_frequent_itemset(transactions, min_support)
    ALL_CANDIDATES.append(current_candidate)

    while len(current_candidate) != 0:

        # increment to increase the combination lengths
        candidate_count += 1

        print "\nCANDIDATE NUMBER: {}".format(candidate_count)

        # generate the current candidate based on the new count
        current_candidate = generate_candidate_set(transactions, min_support, current_candidate, candidate_count)
        transactions = filter_transactions(transactions, current_candidate,first_candidate=False)

        print "CURRENT TRANSACTIONS LENGTH: {}".format(sum([len(l) for l in transactions]))

#####################################
# MARK: MAIN
#####################################

if __name__ == '__main__':

    # command line arguments
    INPUT_DATA = sys.argv[1]
    MIN_SUPPORT = int(sys.argv[2])
    OUTPUT_FILE = sys.argv[3]

    # turn the transactions into a 2D array
    transactions = convert(INPUT_DATA)

    # measure the start time
    start_time = time.time()

    # run the algorithm
    apriori(transactions, MIN_SUPPORT)

    # save all of the candidates into a file
    save_output(ALL_CANDIDATES, OUTPUT_FILE)

    # done!
    print "Number of frequent itemsets: {}".format(sum([len(can) for can in ALL_CANDIDATES]))
    print("--- %s seconds ---" % (time.time() - start_time))