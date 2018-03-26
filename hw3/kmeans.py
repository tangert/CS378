from utils import convert_file, LABEL_LOCATION, DataPoint, Centroid
import random
import random
import math
import sys


# Calculates the euclidean distance between any two n-dimensional points
def calc_distance(point1, point2):

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


def euclidean_average(data_points):

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

    # stores each cluster's squared sums
    # ex:
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

        # square the difference / error
        squared_dist = pow(distance, 2)

        # add the squared dist to the cluster's sum
        cluster_difs[centroid.cluster] += squared_dist

    sse = sum(cluster_difs.values())

    return sse


def k_means(k, data):

    # 1.a. initialize the clusters with k random locations
    centroids = [Centroid(random.choice(data), i) for i in range(k)]

    # 1.b. convert the raw data in data point objects that track their current/previous centroid
    data_points = [DataPoint(point) for point in data]

    print "Initial centroids: ", [centroid.data for centroid in centroids]

    # 2. Iterate and calculate
    converged = False
    iterations = 0

    while not converged:

        print "ITERATIONS: ", iterations

        # Keeps track if all of the centroids are the same for each point
        all_same = True

        # 1. Assign the closest centroid to each point
        for point in data_points:

            min_dist = sys.float_info.max
            closest_centroid = None

            for centroid in centroids:
                dist = calc_distance(point.data, centroid.data)

                if dist <= min_dist:
                    min_dist = dist
                    closest_centroid = centroid

            # Assigns the relevant centroids to each point
            point.previous_centroid = point.current_centroid
            point.current_centroid = closest_centroid

            if point.current_centroid is not point.previous_centroid:
                all_same = False

        # 2. Calculate new centroid locations

        for centroid in centroids:
            current_points = [point for point in data_points if point.current_centroid is centroid]
            current_point_data = [point.data for point in current_points]
            new_location = euclidean_average(current_point_data)
            centroid.data = new_location

        # If you get past all of the cases and each centroid is the same as the previous, you have converged
        if all_same:
            converged = True

        iterations += 1

    return centroids, data_points, iterations


if __name__ == '__main__':
    print "running k means!"

    # SYSTEM INPUT VARIABLES

    # Convert original data into a 2d array
    data = convert_file("iris.data.txt")

    # Remove the label from each data
    unlabeled_data = [row[:LABEL_LOCATION] for row in data]

    # Converts each string data element into a float
    numerized_data = [[float(i) for i in row] for row in unlabeled_data]

    # Run k means on the numerized data
    centroids, results, iterations = k_means(3, numerized_data)

    for i in range(len(data)):
        print "\ncorrect label: ", data[i][-1]
        r = results[i]
        print "data: {} | centroid: {}".format(r.data, r.current_centroid.cluster)
        print "prev: {} | current: {}".format(r.previous_centroid.cluster, r.current_centroid.cluster)

    print "\nall centroids: ", [centroid.data for centroid in centroids]

    for centroid in centroids:
        size = len([point for point in results if point.current_centroid is centroid])
        print "centroid {} size: {}".format(centroid.cluster, size)

    print "\nSSE: ", calc_sse(centroids, results)
    print "total iterations: ", iterations