from __future__ import division
import random
import math
from collections import Counter
from utils import convert_file, LABEL_LOCATION, get_unique_vals, mean, standard_deviation


# MARK: main functions
def test_accuracy(classified_data, test_data):
    correct_count = 0

    for i in range(len(test_data)):
        if classified_data[i][LABEL_LOCATION] == test_data[i][LABEL_LOCATION]:
            correct_count += 1

    return correct_count / len(test_data)


if __name__ == '__main__':

    TRAINING_FILE_PATH = "mushroom.training.txt"
    training_data = convert_file(TRAINING_FILE_PATH)

    label_counts = Counter()
    data_length = len(training_data)

    for row in training_data:
        label = row[LABEL_LOCATION]
        label_counts.update(label)

    label_probabilities = {}
    evidence_probabilities = {}
    evidence_counts = {}

    # get the initial label probabilities for p and e
    for label in label_counts:
        label_probabilities[label] = label_counts[label] / len(training_data)

    # get all of the evidence terms for each attribute
    for column in range(1, len(training_data[0])):

        column_vals = get_unique_vals(training_data, column)
        evidence_probabilities[column] = {}
        evidence_counts[column] = {}

        column_val_counts = Counter()

        for row in training_data:
            for val in column_vals:
                if row[column] == val:
                    column_val_counts.update(val)

        for val in column_val_counts:
            evidence_probabilities[column][val] = column_val_counts[val] / data_length
            evidence_counts[column][val] = column_val_counts[val]


    column_probabilities = {}

    # stores the p and e data sets
    labeled_data_sets = {}

    for label in label_probabilities:
        labeled_set = [row for row in training_data if row[LABEL_LOCATION] == label]
        labeled_data_sets[label] = labeled_set

    for label in labeled_data_sets:
        data_set = labeled_data_sets[label]
        column_probabilities[label] = {}

        for column in range(1, len(data_set[0])):

            # go through each attribute

            column_values = get_unique_vals(data_set, column)
            column_value_counts = Counter()
            # print "column: {} attr vals: {}".format(column, column_values)
            # go through each row

            for row in data_set:
                # for each unique item in an attribute
                for val in column_values:
                    # check if the row's attribute equals the val
                    if row[column] == val:
                        column_value_counts.update(val)

            # print "for label {}: {}\n".format(label, attr_val_counts)
            #
            column_val_probs = {}

            for val in column_value_counts:
                column_val_probs[val] = column_value_counts[val] / len(data_set)

            column_probabilities[label][column] = column_val_probs

    # now you can classify!
    TESTING_FILE_PATH = "mushroom.test.txt"
    test_data = convert_file(TESTING_FILE_PATH)

    # this will store the probabilities for each row
    conditional_probs = {}

    # calculate and compare in one function
    correct_count = 0

    for row in test_data:

        to_classify = row[1:]
        row_probabilities = {}
        normalized_probs = {}

        # for p and e
        for label in label_probabilities:

            # get all of the p's for a row, then all of the e's
            curr_label_probabilities = column_probabilities[label]
            current_data_conditional_prob = 1
            p_evidence = 1

            for column in range(0, len(to_classify)):

                current_attr = to_classify[column]

                # now that you have the attribute and the label
                # find the conditional probability of that attribute given the label
                if current_attr in curr_label_probabilities[column+1]:
                    # print curr_label_probabilities
                    prob = curr_label_probabilities[column+1][current_attr]
                    current_data_conditional_prob *= prob
                else:
                    # didn't find it in the current label, this wont work
                    current_data_conditional_prob = 0

                # have the probability per label per row
                evidence = evidence_probabilities[column+1][to_classify[column]]
                p_evidence *= evidence

            row_probabilities[label] = current_data_conditional_prob * label_probabilities[label]

            for label in row_probabilities:
                normalized = row_probabilities[label] / p_evidence
                normalized_probs[label] = normalized

        # make the prediction
        prediction = max(normalized_probs.keys(), key=lambda k: normalized_probs[k])

        if prediction == row[LABEL_LOCATION]:
            correct_count += 1



    print "Accuracy: {}%".format(correct_count / len(test_data) * 100)







