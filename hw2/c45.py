from __future__ import division
import math
import time
import sys
from utils import get_unique_vals, get_counts, get_predictions, LABEL_LOCATION, convert_file


######################
# MARK: Helper classes
######################

class LeafNode:
    """
    stores the counts of the labels for a given set
    """
    # store the thing in the leaf
    def __init__(self, rows):
        self.counts = get_counts(rows, LABEL_LOCATION)
        self.predictions = get_predictions(self.counts)


class DecisionNode:
    """
    contains a split which asks:
    does the input value match the question we are asking?
    """
    def __init__(self,
                 split,
                 branches):

        # Stores the subtree
        self.split = split
        self.branches = branches

class Split:
    """
    Stores a given attribute and value for easy access at decision nodes
    """
    def __init__(self,
                 attribute):
        # in this case, an attribute is a column number
        self.attribute = attribute

    def input_is_valid(self, row, comparison_value):
        """
        checks if a given row's data matches the split criteria
        ex:
        row (animal):
            tail    fur_color   weight  vegetarian
            yes     brown       100     no

        split: fur color is brown
            check row[fur_color] == brown
        """
        test_value = row[self.attribute]
        return test_value == comparison_value


#############################
# MARK: Information functions
#############################
def partition_data(data, split):
    """
        partitions the data set into the appropriate classes
        based on whether or not they meet the split criteria
    """

    branches = get_unique_vals(data, split.attribute)
    partitioned_data = {}

    # initialize the new data dictionary to empty lists
    for branch_value in branches:
        partitioned_data[branch_value] = []

    for row in data:
        for branch_value in branches:
            if split.input_is_valid(row, branch_value):
                partitioned_data[branch_value].append(row)

    return partitioned_data


def calc_entropy(data):
    entropy = 0
    predictions = get_predictions(get_counts(data, LABEL_LOCATION))

    for label in predictions:
        entropy -= predictions[label] * math.log(predictions[label], 2)

    return entropy


def calc_gain_ratio(parent_data, attribute):
    """
     Pseudocode:

     INFO GAIN:
     Entropy of parent data set - weight average of child entropies
                                -> sum ( child proportion of parent set * child entropy )

     Calculates reduction in disorder / increase in organization

     SPLIT INFO:
     sum of child proportions * log(child proportions)

    """

    current_split = Split(attribute)
    parent_entropy = calc_entropy(parent_data)
    parent_data_count = sum(get_counts(parent_data, LABEL_LOCATION).values())
    children_data_sets = partition_data(parent_data, current_split)

    # Initialize metrics
    weighted_child_avg = 0
    split_info = 0
    
    for child in children_data_sets:

        child_data = children_data_sets[child]
        child_entropy = calc_entropy(child_data)
        child_data_count = sum(get_counts(child_data, LABEL_LOCATION).values())
        child_proportion = child_data_count / parent_data_count

        split_info -= child_proportion * math.log(child_proportion, 2)
        weighted_child_avg += child_proportion * child_entropy

    info_gain = parent_entropy - weighted_child_avg

    # Store info gain, split info, and gain ratio all in one object
    # initialize with info gain and split info
    data = {
        'info_gain': info_gain,
        'split_info': split_info
    }

    # calculate gain ratio simply from the other two metrics
    if data['split_info'] == 0:
        data['gain_ratio'] = 0
    else:
        data['gain_ratio'] = data['info_gain'] / \
                             data['split_info']

    return data


############################
# MARK: High level functions
############################

def get_best_split(data):
    """
        returns a split object which contains the
    """
    max_gain_ratio = 0

    # Initialize the split object in case info gain is zero,
    # in which case a leaf node will be returned
    best_split = {
        'info_gain': 0,
        'gain_ratio': 0,
        'split': None,
        'partitioned_data': []
    }

    # Start after the label,
    # Stop at the length of a sample row in the data set (in this case just the first one)
    for attribute in range(LABEL_LOCATION+1, len(data[0])):

        # each column is an attribute
        split = Split(attribute)

        # grab the gain ratio data object
        all_data = calc_gain_ratio(data, attribute)

        current_gain_ratio = all_data['gain_ratio']

        # find the max gain ratio
        if current_gain_ratio > max_gain_ratio:

            max_gain_ratio = current_gain_ratio

            best_split['info_gain'] = all_data['info_gain']
            best_split['gain_ratio'] = max_gain_ratio
            best_split['split'] = split
            best_split['partitioned_data'] = partition_data(data, split)

    return best_split


def build_tree(data):
    """
     Recursively builds the decision tree.

     Pseudocode:
     1. Find the best split (highest gain ratio)

     2. Check base case:
        1. All samples in split belong to same classs
            -> Create leaf node

     3. Recur on the subtrees

     4. Return decision node
    """
    best_split = get_best_split(data)

    # BASE CASE
    if best_split['info_gain'] == 0:
        print "leaf node!"
        return LeafNode(data)

    print "\nbest split: {}".format(best_split['split'].attribute)

    #replace with data branches
    partitioned_data = best_split['partitioned_data']
    print "partitioned data length: {}".format(len(partitioned_data))

    branches = []

    print "all classes: "
    for data_class in partitioned_data:
        print data_class

    for data_class in partitioned_data:
        branched_data = partitioned_data[data_class]
        branch_tree = build_tree(branched_data)
        branches.append(branch_tree)

    return DecisionNode(best_split, branches)


def print_tree(node, spacing=""):
    if isinstance(node, LeafNode):
        print spacing + "Counts for leaf: ", node.counts
        return

    # Print the decision node
    print spacing + "---> Splitting on: ", str(node.split['split'].attribute)

    for branch in node.branches:
        print_tree(branch, spacing + "   ")


def test_data(data, tree):
    print "testing"


if __name__ == '__main__':
    print "Running c4.5 to build a decision tree."

    """
    3 command line parameters:
    1. Traning dataset file
    2. Test dataset file
    3. Output file

    Derek, if you're reading this, I hope you appreciate how readable my code is.
    Also ur handsome.
    """

    TRAINING_FILE_PATH = "mushroom.training.txt"
    training_data = convert_file(TRAINING_FILE_PATH)

    # training
    start_time = time.time()
    tree = build_tree(training_data)
    print("--- %s seconds ---" % (time.time() - start_time))

    print "\n"
    print_tree(tree)

    TESTING_FILE_PATH = "mushroom.test.txt"
    test_data = convert_file(TESTING_FILE_PATH)