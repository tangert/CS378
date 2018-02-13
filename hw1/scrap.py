def calc_support(length, input_item, reference_items):

    input_elements = set()

    if length == 1:
        input_elements.add(input_item)
    else:
        input_elements = input_item

    support = 0

    for item in reference_items:
        common = set(item).intersection(input_elements)
        if len(common) == len(input_elements):
            support += 1

    return support

def get_combos(input_list, num):
    if num == 1:
        return set(input_list)
    else:
        print "GETTING COMBOS WITH LENGTH:{} || {}".format(len(input_list), input_list)
        toreturn = it.combinations(input_list, num)
        print "COMBO : {}".format(toreturn)
        return toreturn



# MARK: Main apriori algorithm functions
def apriori(data, min_support):
    """
    takes in data as a 2D array and runs the algorithm
    """

    print "Running apriori algorithm on {} elements".format(len(data))

    #get the initial data set
    candidate_count = 1
    freq_1_items = set()
    curr_candidate = set()

    ####NEED TO PRUNE THE DATASET
    #use set.update, not set.union

    for sub in data:
        freq_1_items = freq_1_items.union(set(sub))

    for item in freq_1_items:
        # print "{} SUPPORT: {}".format(item, calc_support(item, data))
        support = calc_support(candidate_count, item, data)

        if support >= min_support:
            curr_candidate.add(item)


    #set it to 2 before the while loop
    candidate_count += 1

    while len(curr_candidate) != 0:
        print "ANOTHER CYCLE: {}".format(candidate_count)

        combos = get_combos(curr_candidate, candidate_count)

        print "GOT COMBOS: {}".format(combos)
        curr_candidate.clear()

        for item in combos:

            #FIXME: prune the data each time
            support = calc_support(candidate_count, item, data)

            if candidate_count > 2:
                print "SUPPORT : {}".format(support)

            if support >= min_support:
                print "ADDING: {} ||| SUPPORT: {}".format(item, support)
                curr_candidate.add(item)

        print curr_candidate

        candidate_count += 1

    return curr_candidate