from __future__ import division
from collections import Counter

# MARK: Globals
# adapt this to wherever the label is inside the input file
LABEL_LOCATION = 0


def convert_file(filepath):
    """
     takes an input file and turns it into a 2D array
    """
    data = []

    for line in open("{}".format(filepath), 'r'):
        data.append(line.rstrip().split())

    # below accounts for missing data by appending empty strings to incomplete entries
    # max_length = len(max(data, key=len))

    # for row in data:
    #     if len(row) < max_length:
    #         for i in range(max_length-len(row)):
    #             data.append("")

    return data


def get_unique_vals(data, attribute):
    """
     returns a set of all of the unique values for an attribute
    """

    return set([row[attribute] for row in data])


def get_counts(rows, label_location):
    """
        returns a count of all the different classes
    """
    counts = Counter()

    for row in rows:
        label = row[label_location]
        counts.update(label)

    return counts


def get_predictions(counts):
    """
     returns the prediction values (as percentages) for each class label
    """
    predictions = {}
    total_count = sum(counts.values())

    for class_label in counts:
        predictions[class_label] = counts[class_label]/total_count

    return predictions