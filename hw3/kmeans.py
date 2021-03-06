# THIS CODE WAS WRITTEN BY ME WITHOUT ANY ASSISTANCE FROM OTHER STUDENTS.
# I REFERENCED THE WIKIPEDIA PAGE FOR THE ALGORITHIM AS WELL AS SOME CONCEPTUAL TUTORIALS
# -TYLER ANGERT

from utils import convert_file, save_output, LABEL_LOCATION, DataPoint, Centroid
import random
import math
import sys

def calc_distance(point1, point2):

    """
    Calculates the euclidean distance between any two n-dimensional points
    """

    # groups all of the dimension values together from the points
    zipped = zip(point1, point2)
    difs = {}

    for dimension, values in enumerate(zipped):
        difs[dimension] = values[1] - values[0]

    total_dist = 0

    for dif in difs:
        total_dist += math.pow(difs[dif], 2)

    total_dist = math.sqrt(total_dist)

    return total_dist


def calc_average(data_points):

    """
     Calculates the average of an array of n-dimensional data points
    """

    sums = {}
    avgs = {}

    for point in data_points:
        for dimension, value in enumerate(point):
            if dimension not in sums:
                sums[dimension] = value
            else:
                sums[dimension] += value

    for sum in sums:
        avgs[sum] = sums[sum]/len(data_points)

    return avgs.values()


def calc_sse(centroids, data):
    """
     Calculates the sum of squared distances between data and centroids
    """

    # stores each cluster's squared sums
    cluster_difs = {}

    # Initialze cluster difs
    for centroid in centroids:
        cluster_difs[centroid.cluster] = 0

    # Iterate and calculate
    for point in data:

        # grab the centroid for this point
        centroid = point.current_centroid

        # calculate euclidean distance between this point and the cluster
        distance = calc_distance(centroid.data, point.data)

        # add the squared dist to the cluster's sum
        cluster_difs[centroid.cluster] += pow(distance, 2)

    return sum(cluster_difs.values())


def k_means(k, data):

    """
     Runs the k-means clustering algorithm on a given dataset
    """

    # 1.a. initialize the clusters with k random locations
    chosen = []
    centroids = []

    # assures that you pick unique random points
    for i in range(k):
        d = random.choice(data)
        if d not in chosen:
            chosen.append(d)
            c = Centroid(d, i)
            centroids.append(c)

    print "Initial centroids: {}".format([c.data for c in centroids])

    # 1.b. convert the raw data in data point objects that track their current/previous centroid
    data_points = [DataPoint(point) for point in data]

    # 2. Iterate and calculate
    iterations = 0

    while True:

        # Keeps track if all of the centroids are the same for each point
        all_centroids_same = True

        # 1. Assign the closest centroid to each point
        for point in data_points:

            min_dist = sys.float_info.max
            closest_centroid = None

            # print "all centroids: {}".format([c.data for c in centroids])

            for centroid in centroids:
                dist = calc_distance(point.data, centroid.data)
                if dist < min_dist:
                    min_dist = dist
                    closest_centroid = centroid

            # Assigns the relevant centroids to each point
            point.previous_centroid = point.current_centroid
            point.current_centroid = closest_centroid

            if point.previous_centroid is None:
                all_centroids_same = False
            else:
                if point.current_centroid is not point.previous_centroid \
                        or point.current_centroid.data != point.previous_centroid.data:
                    all_centroids_same = False

        # If you get past all of the cases and each centroid is the same as the previous, you have converged
        if all_centroids_same:
            print "Iteration {} : all centroids same! Converging!".format(iterations)
            break

        print "Iteration {} : calculating new centroids".format(iterations)

        # 2. Calculate new centroid locations
        for centroid in centroids:
            current_point_data = [point.data for point in data_points if point.current_centroid is centroid]
            new_location = calc_average(current_point_data)
            centroid.data = new_location

        iterations += 1

    return centroids, data_points, iterations


if __name__ == '__main__':

    # SYSTEM INPUT VARIABLES
    DATA_FILE_PATH = sys.argv[1]
    INPUT_K = int(sys.argv[2])
    OUTPUT_FILE = sys.argv[3]

    print "Running k means on {}!".format(DATA_FILE_PATH)

    # Convert original data into a 2d array
    data = convert_file(DATA_FILE_PATH)

    # Remove the label from each data
    # only for use with the original file
    unlabeled_data = [row[:LABEL_LOCATION] for row in data]

    # Converts each string data element into a float, removes any empty rows
    numerized_data = filter(lambda x: len(x) > 0, [[float(i) for i in row] for row in unlabeled_data])

    # store sse's for post analyses
    print "\nTESTING ON K = {}".format(INPUT_K)

    # Run k means on the numerized data
    centroids, results, iterations = k_means(INPUT_K, numerized_data)

    # Grab the labels in order
    predicted_labels = [r.current_centroid.cluster for r in results]

    # save the output
    save_output(predicted_labels, OUTPUT_FILE)

    # convenience print statements
    print "\nFinal centroids:"

    for centroid in [centroid.data for centroid in centroids]:
        print centroid

    sse = calc_sse(centroids, results)

    print "\nSSE: ", sse
    print "total iterations: ", iterations

    # FOR TESTING ON DIFFERENT VARIATIONS OF K
    # for i in range(2,6):
    #
    #     print "\n\nTESTING ON K = {}".format(i)
    #
    #     # Run k means on the numerized data
    #     centroids, results, iterations = k_means(i, numerized_data)
    #
    #     # Grab the labels in order
    #     predicted_labels = [r.current_centroid.cluster for r in results]
    #
    #     # save the output
    #     save_output(predicted_labels, OUTPUT_FILE)
    #
    #     # convenience print statements
    #     print "\nFinal centroids:"
    #
    #     for centroid in [centroid.data for centroid in centroids]:
    #         print centroid
    #
    #     sse = calc_sse(centroids, results)
    #
    #     sses[i] = sse
    #
    #     print "\nSSE: ", sse
    #     print "total iterations: ", iterations