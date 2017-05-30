from collections import defaultdict
import re
import jellyfish as jf

def split_clean(string):
    s = re.split(r'\W+', string)
    return [v for v in s if len(v) >= 3]

def similarity(query, string):
    # split the two strings cleaning out some stuff
    query = split_clean(query)
    string = split_clean(string)
    # sort the two generated lists, longest first
    longest, shortest = sorted([query, string])
    # similary of length (0-1)
    l_similar = len(longest) / len(shortest)

    # generator matrix of tuples for each segment of both query and string
    matrix = ((s1, s2) for s1 in longest for s2 in shortest)
    # calculate the similarity (distance) for each tuple of the matrix
    # and group them by the longest string's segments. this allows us
    # to be sure to have all the combinations to reduce
    matches = defaultdict(list)
    [matches[s1].append(jf.jaro_winkler(s1, s2)) for s1, s2 in matrix]

    # get the highest value for each list
    matches = [max(m) for m in matches.values()]

    # get the weighted mean for all the highest matches and apply the
    # segments qty diff as coefficient, to consider the
    # missing/extra values on one of the lists
    mean_match =(sum(matches) / len(matches)) * l_similar
    return mean_match