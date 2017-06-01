"""
Search API core module

Contains the main functions to get match values and searching
"""
import jellyfish as jf

from search import utils, config


def get_match(query, string):
    """
    Calculate the match for the given `query` and `string`.

    The match is calculated using the `jaro winkler` for each set of the matrix
    (`query` x `string`) and takes into consideration the position difference
    into the strings.

    Arguments:
        query (str): search query
        string (str): string to test against

    Returns:
        float: normalized value indicating the probability of match, where
        0 means completely dissimilar and 1 means equal.
    """

    # split the two strings cleaning out some stuff
    query = utils.tokenize(query.lower())
    string = utils.tokenize(string.lower())

    # if one of the two strings is falsy (no content, or was passed with items
    # short enough to be trimmed out), return 0 here to avoid ZeroDivisionError
    # later on while processing.
    if len(query) == 0 or len(string) == 0:
        return 0

    shortest, longest = sorted((query, string), key=lambda x: len(x))

    # matrix of tuples for each segment of both query and string
    matrix = [(s1, s2) for s1 in longest for s2 in shortest]

    matches = {}
    for string1, string2 in matrix:
        # get the jaro winkler equality between the two strings
        match = jf.jaro_winkler(string1, string2)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        positional = utils.pos_dist(string1, string2, longest, shortest)

        # get them together and append to the matches dictionary
        match = (match, positional)
        matches.setdefault(string1, []).append(match)

    # get the highest value for each list, the apply the word-distance factor
    # the key takes the jaro winkler distance value to get the max value
    matches = [max(m, key=lambda x: x[0]) for m in matches.values()]
    _weights = (config.MATCH_WEIGHT, config.DIST_WEIGHT)
    matches = [utils.weighted_avg((m, d), _weights) for m, d in matches]

    # get the weighted mean for all the highest matches and apply the highest
    # match value found as coefficient as multiplier, to add weights to more
    # coherent matches.
    mean_match = (sum(matches) / len(matches)) * max(matches)
    return mean_match


def search(
        query, attributes, dataset, limit=-1,
        threshold=config.THRESHOLD, weights=None):
    """
    Main function of the package, allows to do a fuzzy full-text search on the
    rows of the given `table` model, looking up the value
    on the given `attributes` list against the passed `query` string.

    Extra arguments allows some customization on the search results (see below)

    Arguments:
        query (str): String to search for
        attributes (list): The names of thetable columns to search into.
        dataset (iterable): iterable of `objects` to lookup. All the objects
            in the dataset **must** have the specified attribute(s)
        limit (int): max number of results to return. if ``-1`` will return
            everything.
        threshold (float): value under which results are considered not valid.
        weights (list): matching `attributes` argument, describes the
            attributes weights. if not provided **or** if different length
            the weight will generated automatically, considering
            the index of the attribute name, reversed (first -> more weight).

    Returns:
        list: A list containing ``[0:limit]`` resources from the given table,
        sorted by relevance.

    Raises:
        AttributeError: if one of the object does not have one of the given
            attribute(s).

    Example:
        Assuming a random number of items in the Item table, that defines
        `name`, `category`, `description`, `availability`, one can do:

        >>> from models import Item
        >>> from search import search
        >>> results = search('awesome', ['name', 'category'], Item.select())
        [<Item name: 'awesome item' cat: 'generic'>]

    .. note::
        Since this function implements the core functionality, it has the
        shortcut import

        >>> from search.core import search
        >>> from search import search

        Will have the same effect
    """
    matches = []
    if not weights or len(weights) != len(attributes):
        # list of integers of the same length of `attributes` as in [3, 2, 1]
        # for attributes = ['a', 'b', 'c']
        weights = list(range(len(attributes), 0, -1))

    weights = utils.scale_to_one(weights)
    weights = {attr: w for attr, w in zip(attributes, weights)}

    if not threshold:
        threshold = 0

    for obj in dataset:
        partial_matches = []

        for attr in attributes:
            try:
                attrval = getattr(obj, attr)
            except AttributeError:
                msg = 'Search error: Cannot find field "{a}" in the resources.'
                raise AttributeError(msg.format(attrval))

            match = get_match(query, attrval)
            partial_matches.append({'attr': attr, 'match': match})

        # get the highest match for each attribute and multiply it by the
        # attribute weight, so we can get the weighted average to return
        match = max(partial_matches, key=lambda m: m['match'])
        match = match['match'] * weights[match['attr']]

        try:
            if match >= threshold:
                matches.append({'data': obj, 'match': match})
        except Exception:
            import pdb
            pdb.set_trace()

    matches.sort(key=lambda m: m['match'], reverse=True)

    if limit > 0:
        matches = matches[:limit]

    return [m['data'] for m in matches]
