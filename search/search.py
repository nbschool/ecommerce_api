import jellyfish as jf
from search.utils import clean_split, pos_dist

#: string equality weight for weighted average with positional coefficient
MATCH_WEIGHT = .25
#: positional coeff weight for weighted avg with equality match
DIST_WEIGHT = 1


def get_match(query, string):
    # split the two strings cleaning out some stuff
    if len(query) == 0 or len(string) == 0:
        return 0

    query = clean_split(query.lower())
    string = clean_split(string.lower())
    # sort the two generated lists and set them in position
    shortest, longest = sorted((query, string), key=lambda x: len(x))

    # matrix of tuples for each segment of both query and string
    matrix = [(s1, s2) for s1 in longest for s2 in shortest]

    matches = {}
    for string1, string2 in matrix:
        # get the jaro winkler equality between the two strings
        match = jf.jaro_winkler(string1, string2)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        positional = pos_dist(string1, string2, longest, shortest)

        # get them together and append to the matches dictionary
        match = (match, positional)
        matches.setdefault(string1, []).append(match)

    def weighted_avg(m, d):
        val = (m * MATCH_WEIGHT) + (d * DIST_WEIGHT)
        weights = MATCH_WEIGHT + DIST_WEIGHT
        return val / weights

    # get the highest value for each list, the apply the word-distance factor
    # the key takes the jaro winkler distance value to get the max value
    matches = [max(m, key=lambda x: x[0]) for m in matches.values()]
    matches = [weighted_avg(m, d) for m, d in matches]

    # get the weighted mean for all the highest matches and apply the
    # segments qty diff as coefficient, to consider the
    # missing/extra values on one of the lists
    mean_match = (sum(matches) / len(matches)) * max(matches)
    return mean_match


def search(query, attributes, table, limit=-1, threshold=0.75, weights=None):
    """
    Search the given `query` inside the `table` model, looking up the value
    on the given `attributes`.

    Arguments:
        query (str): String to search for
        attributes (list:str): A list of ``str`` describing the names of the
            table columns to search into.
        table (:any:`BaseModel`): Database table model.
        limit (int): max number of results to return. if ``-1`` will return
            everything.
        threshold (float): value under which results are considered not valid.
        weights (list:int): matching `attributes` argument, describing the
            attributes weights. if not provided the weight will be considered
            the index of the attribute name, reversed (first -> more weight).

    Returns:
        list: A list containing `0-limit` resources from the given table, sorted
            by relevance.
    """
    matches = []  # return value

    if not weights or len(weights) != len(attributes):
        weights = sorted(list(range(1, len(attributes) + 1)), reverse=True)

    weights = {attr: w for attr, w in zip(attributes, weights)}

    for object in table.select():
        partial_matches = []

        for attr in attributes:
            try:
                attrval = getattr(object, attr)
            except AttributeError:
                msg = 'Search error: "{t}" table does not have {a} field.'
                raise AttributeError(msg.format(table.__name__, attrval))

            match = get_match(query, attrval)
            partial_matches.append({'attr': attr, 'match': match})

        match = max(partial_matches, key=lambda m: m['match'])
        match = match['match'] * weights[match['attr']]

        if match >= threshold:
            matches.append({'data': object, 'match': match})

    matches.sort(key=lambda m: m['match'], reverse=True)

    if limit > 0:
        matches = matches[:limit]

    return [m['data'] for m in matches]
