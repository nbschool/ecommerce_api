"""
Matcher functions to determine similarity between two strings

Using different algorithms and given two strings, each function returns a
value between 0 and 1, where 0 is completely different and 1 represent complete
equality (as in "hello world", "hello world")
"""
from search import utils


# =====================================================================
# String similarity functions
# ---------------------------------------------------------------------
# A set of functions that calculate the edit distance between two
# strings

def simple_ratio(query, string):
    return utils.ratio(query, string)


def best_token_ratio(query, string, tokenize=True):
    if tokenize:
        query = utils.sorted_unique_tokens(query)
        string = utils.sorted_unique_tokens(string)

    string = utils.stringify_tokens(string)

    prob = 0
    for segment in query:
        match = utils.best_partial_ratio(segment, string)  # shift string
        if match > .995:
            return 1.0
        prob = match if match > prob else prob
    return prob


def token_sort_ratio(query, string, tokenize=True):
    """
    generate tokens from query and string, then for each query token
    find the best partial ratio on the string and get the average value
    """
    if tokenize:
        query = utils.sorted_unique_tokens(query)
        string = utils.sorted_unique_tokens(string)

    matches = {}
    for q_token in query:
        # loop every token in the query, adding a default similarity == 0
        # to the matches dictionary
        matches[q_token] = 0
        # loop for every word in the searched string
        for token in string:
            # and call the slider on each of them, getting the similariy
            # for every extracted token
            match = utils.ratio(q_token, token)
            if match > matches[q_token]:
                if match > .995:
                    return 1.0
                matches[q_token] = match

    return max(matches.values())


def intersect_token_ratio(query, string, tokenize=True):
    """
    Perform a match utilizing the intersection method.
    """
    if tokenize:
        query = utils.sorted_unique_tokens(query)
        string = utils.sorted_unique_tokens(string)

    common, diff_q, diff_s = utils.sorted_intersect(query, string)
    t0 = ' '.join(common)            # common elements for query and string
    t1 = ' '.join(common + diff_q)   # common plus the diff elements on query
    t2 = ' '.join(common + diff_s)   # common plus diff elements on string
    best = 0
    for (q, s) in ((t0, t1), (t1, t2), (t0, t2)):
        match = utils.ratio(q, s)
        if match > best:
            best = match
            if best == 1:
                break

    return best

# =====================================================================
# Full matchers functions
# ---------------------------------------------------------------------
# A set of functions that perform various checks and matches agains
# a query and a string and return a comprehensive value representing
# the equality of the two strings


def lazy_match(query, string):
    q_tokens = utils.sorted_unique_tokens(query)
    s_tokens = utils.sorted_unique_tokens(string)
    shortest, longest = sorted((q_tokens, s_tokens), key=lambda x: len(x))
    len_short, len_long = len(shortest), len(longest)

    # If the longest has no length it's useless to continue
    if len_long == 0:
        return 0

    elif len_long == 1:
        # len_short == 1 too, so 1 word against 1 word
        return simple_ratio(query, string)

    elif len_short == 1 and len_long <= 4:
        # one word against a short string, 1 < diff < 3
        return best_token_ratio(q_tokens, s_tokens, tokenize=False)

    elif 1 <= len_short <= 4 and len_long <= 10:
        # token length diff between 8 and 6
        return token_sort_ratio(q_tokens, s_tokens, tokenize=False)

    else:
        # in any other condition, such as short query against very long string
        # go with the intersect.
        # This option SHOULD go only with fairly long queries - as far as a
        # query can be long - against long strings
        return intersect_token_ratio(q_tokens, s_tokens, tokenize=False)
