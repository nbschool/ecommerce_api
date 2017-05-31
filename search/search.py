import jellyfish as jf
from search.utils import clean_split, pos_dist


def get_match(query, string):
    # split the two strings cleaning out some stuff
    query = clean_split(query.lower())
    string = clean_split(string.lower())
    # sort the two generated lists and set them in position
    shortest, longest = sorted((query, string), key=lambda x: len(x))

    # matrix of tuples for each segment of both query and string
    matrix = [(s1, string2) for s1 in longest for string2 in shortest]

    matches = {}
    for string1, string2 in matrix:
        # get the jaro winkler equality between the two strings
        match = jf.jaro_winkler(string1, string2, long_tolerance=True)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        pos_weight = pos_dist(string1, string2, longest, shortest)

        # get them together and append to the matches dictionary
        match = (match, pos_weight)
        matches.setdefault(string1, []).append(match)

    # get the highest value for each list, the apply the word-distance factor
    matches = [max(m, key=lambda x: x[0]) for m in matches.values()]
    matches = [(m + d) / 2 for m, d in matches]

    # get the weighted mean for all the highest matches and apply the
    # segments qty diff as coefficient, to consider the
    # missing/extra values on one of the lists
    mean_match = (sum(matches) / len(matches))
    print('TOTAL MEAN MATCH: {}'.format(mean_match))
    return mean_match
