# THIS CODE WAS WRITTEN BY ME WITHOUT ANY ASSISTANCE FROM OTHER STUDENTS.
# I REFERENCED THE WIKIPEDIA PAGE FOR THE ALGORITHIM AS WELL AS SOME CONCEPTUAL TUTORIALS
# -TYLER ANGERT

from __future__ import division
import math
import time
import random
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
        self.data_class = None

    def assign_data_class(self, data_class):
        self.data_class = data_class


class DecisionNode:
    """
    contains a split which asks:
    does the input value match the question we are asking?
    """
    def __init__(self,
                 split,
                 gain_ratio,
                 branches):

        # Stores the subtree
        self.split = split
        self.gain_ratio = gain_ratio
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

    print "Calculating gain ratio for {}: {}".format(attribute, data['gain_ratio'])

    return data


############################
# MARK: High level functions
############################

def get_best_split(data):
    """
        returns a split object which contains the info gain, gain ratio, split object, and
        relevant partitioned data.
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

    # First get the best split to evaluate
    best_split = get_best_split(data)

    # BASE CASE
    # If the info gain is zero, no further splitting necessary
    if best_split['info_gain'] == 0:
        return LeafNode(data)

    print "\nBest split: {}".format(best_split['split'].attribute)

    partitioned_data = best_split['partitioned_data']
    branches = []

    for data_class in partitioned_data:
        branched_data = partitioned_data[data_class]
        branch_tree = build_tree(branched_data)

        if isinstance(branch_tree, LeafNode):
            #store the relevant data class in the leaf node
            branch_tree.data_class = data_class

        branches.append(branch_tree)

    # Return a decision node once all the leaves return
    return DecisionNode(best_split['split'], best_split['gain_ratio'], branches)


def print_tree(node, spacing=""):
    if isinstance(node, LeafNode):
        print spacing + "Leaf {} prediction: {}".format(node.data_class, node.predictions)
        return

    # Print the decision node
    print spacing + "---> Splitting on: {} | GAIN RATIO: {}".format(str(node.split.attribute), str(node.gain_ratio))

    for branch in node.branches:
        print_tree(branch, spacing + "   ")


def classify_data_set(data, trained_tree):
    classified_data = []

    for row in data:
        # get the row without the first label
        to_classify = row[1:]

        # get the prediction for the row
        prediction = classify_row(to_classify, trained_tree)

        # append the prediction to the unlabeled row
        to_classify.insert(0, prediction)

        # append to the classified data
        classified_data.append(to_classify)

    return classified_data


def classify_row(row, current_node):
    # return random.choice(['e','p'])

    # keep traversing until you hit a leaf, which has no branches
    next_node = None
    # since the label was removed, have to test everything one back
    test_value = row[current_node.split.attribute-1]

    # while you are at a decision node
    while current_node.branches is not None:

        # go through each of the branches and test which fits
        # go through each of the leaf nodes

        leaves = [branch for branch in current_node.branches if isinstance(branch, LeafNode)]
        decisions = [branch for branch in current_node.branches if isinstance(branch, DecisionNode)]

        # return early if you find a leaf
        if leaves is not None:
            for leaf in leaves:
                if leaf.data_class == test_value:
                    prediction = max(leaf.predictions.keys(), key=lambda k: leaf.predictions[k])
                    return prediction

        # couldn't find a leaf, so go down the decisions
        # pick the next decision node to go down
        for decision in decisions:
            leaves = [branch for branch in decision.branches if isinstance(branch, LeafNode)]
            if leaves is not None:
                leaf_values = [leaf.data_class for leaf in leaves]
                if test_value in leaf_values:
                    next_node = decision

        # else go to next decision node
        current_node = next_node


def test_accuracy(classified_data, test_data):
    correct_count = 0

    for i in range(len(test_data)):
        if classified_data[i][LABEL_LOCATION] == test_data[i][LABEL_LOCATION]:
            correct_count += 1

    return correct_count / len(test_data)


def save_output(data, accuracy, file_name):
    output = open("{}.txt".format(file_name), "w+")
    output.write("Decision tree accuracy: {}%\n".format(accuracy*100))
    for row in data:
        row[0] = "Predicted label: {}".format(row[0])
        output.write("{}\n".format(row))

if __name__ == '__main__':
    print "Running c4.5 to build a decision tree."

    TRAINING_FILE_PATH = sys.argv[1]
    TESTING_FILE_PATH = sys.argv[2]
    OUTPUT_FILE = sys.argv[3]

    training_data = convert_file(TRAINING_FILE_PATH)

    # training
    start_time = time.time()
    trained_tree = build_tree(training_data)
    print("--- %s seconds ---" % (time.time() - start_time))

    print "\n"
    print_tree(trained_tree)

    test_data = convert_file(TESTING_FILE_PATH)

    # classify the test data
    predicted = classify_data_set(test_data, trained_tree)
    accuracy = test_accuracy(predicted, test_data)

    print "\nAccuracy: {}%".format(accuracy*100)

    # write the output file
    save_output(predicted, accuracy, OUTPUT_FILE)