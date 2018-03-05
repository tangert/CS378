from __future__ import division
import math
import sys
from utils import get_unique_vals, get_counts, get_predictions, LABEL_LOCATION, convert_file


######################
# MARK: Helper classes
######################

class LeafNode:
    """
    stores the counts of the labels for a given set
    """
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
        example row (animal):
            tail    fur_color   weight  vegetarian
            yes     brown       100     no

        example split: fur color is brown
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

    # print "SPLIT: {}".format(split.attribute)

    branches = get_unique_vals(data, split.attribute)

    # print "BRANCHES: {}".format(branches)

    # stores the data in the form:
    # branch item: [list of partitioned data]
    partitioned_data = {}

    # initialize the new data dictionary to empty lists
    for branch_value in branches:
        partitioned_data[branch_value] = []

    for row in data:
        for branch_value in branches:
            if split.input_is_valid(row, branch_value):
                partitioned_data[branch_value].append(row)

    # print "new data: {}".format(partitioned_data)

    # for attr in new_data:
    #     print "Key: {}".format(attr)
    #     print "data: {}\n".format(new_data[attr])

    return partitioned_data


def calc_entropy(data):
    entropy = 0
    predictions = get_predictions(get_counts(data, LABEL_LOCATION))

    for label in predictions:
        entropy -= predictions[label] * math.log(predictions[label], 2)

    return entropy


def calc_info_gain(parent_data, attribute):

    current_split = Split(attribute)
    parent_entropy = calc_entropy(parent_data)

    parent_data_count = sum(get_counts(parent_data, LABEL_LOCATION).values())

    weighted_child_avg = 0

    # grab all of the child data sets from the current parent and split
    children = partition_data(parent_data, current_split)
    # print "children length: {}".format(len(children))

    # calculate the weighted average of the children
    for child in children:

        child_data = children[child]
        child_entropy = calc_entropy(child_data)
        child_data_count = sum(get_counts(child_data, LABEL_LOCATION).values())

        child_proportion = child_data_count / parent_data_count
        weighted_child_avg += child_entropy * child_proportion

    info_gain = parent_entropy - weighted_child_avg

    return info_gain


def calc_split_info(data):
    """
    """
    predictions = get_predictions(get_counts(data, LABEL_LOCATION))
    split_info = 1

    for label in predictions:
        split_info *= -1*predictions[label] * math.log(predictions[label], 2)

    return split_info


def calc_gain_ratio(data, attribute):

    to_return = {
        'info_gain': calc_info_gain(data, attribute),
        'split_info': calc_split_info(data)
    }

    if to_return['split_info'] == 0:
        to_return['gain_ratio'] = to_return['info_gain']
    else:
        to_return['gain_ratio'] = to_return['info_gain'] / to_return['split_info']

    return to_return


############################
# MARK: High level functions
############################

def get_best_split(data):
    """
        returns a split object which contains the
    """
    max_gain_ratio = 0

    best_split = {
        'info_gain': 0,
        'gain_ratio': 0,
        'split': None,
        'partitioned_data': []
    }

    for attribute in range(LABEL_LOCATION+1, len(data[0])):

        split = Split(attribute)

        # each column is an attribute
        all_data = calc_gain_ratio(data, attribute)
        current_gain_ratio = all_data['gain_ratio']

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


    for data_class in partitioned_data:
        print "size of class {}: {}".format(data_class, len(partitioned_data[data_class]))

    branches = []

    for data_class in partitioned_data:
        branched_data = partitioned_data[data_class]
        branch_tree = build_tree(branched_data)
        branches.append(branch_tree)

    print "decision node!"
    return DecisionNode(best_split, branches)

def print_tree(node, spacing=""):
    """World's most elegant tree printing function."""

    # Base case: we've reached a leaf
    if isinstance(node, LeafNode):
        print spacing + "Counts for leaf: ", node.counts
        return

    # Print the decision node
    print spacing + "---> Splitting on: ", str(node.split['split'].attribute)

    for branch in node.branches:
        print_tree(branch, spacing + "   ")

if __name__ == '__main__':
    print "Running c4.5 to build a decision tree."

    """
    3 command line parameters:
    1. Traning dataset file
    2. Test dataset file
    3. Output file
    """

    FILE_PATH = "mushroom.training.txt"
    data = convert_file(FILE_PATH)

    # training
    tree = build_tree(data)
    print_tree(tree)