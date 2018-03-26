# last element in the list
LABEL_LOCATION = -1

def convert_file(filepath):
    """
     takes an input file and turns it into a 2D array
    """
    data = []

    for line in open("{}".format(filepath), 'r'):
        data.append(line.rstrip().split(','))

    return data


# Data point object that keeps track of the current/previous centroid
class DataPoint:
    def __init__(self, data):
        self.data = data
        self.current_centroid = None
        self.previous_centroid = None


# Centroid object that stores the coordinate and the cluster number
class Centroid:
    def __init__(self, data, cluster):
        self.data = data
        self.cluster = cluster