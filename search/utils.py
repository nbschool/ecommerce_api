"""
Utility module for the search engine

Contains various functions to do common operations on strings and iterables,
such as normalization, tokenization, averages, splitting and walking through
the elements of the iterable/string.
"""
import re
from difflib import SequenceMatcher  # noqa

from search import config


# =====================================================================
# Ratio functions
# ---------------------------------------------------------------------
# Various functions that calculates best/worst match ratio against two
# strings, either directly or by splitting/tokenizing them first


def ratio(query, string):
    """
    Simple ratio between the whole strings. values 0 -> 1.
    Should be good for lengths == 1
    """
    return SequenceMatcher(None, query, string).ratio()


def best_partial_ratio(query, string):
    """
    Best partial ratio between query and string.
    `String` is walked with the shifter function and each segment's length
    is equal to the `query` length:
    """
    v = 0
    for str_segment in shifter(string, len(query)):
        m = ratio(query, str_segment)
        v = m if m > v else m
        if v > .995:
            return 1.0
    return v


# =====================================================================
# Tokenization and processing
# ---------------------------------------------------------------------
# Various functions that perform a tokenization of some sort on a
# string and return eiter a list or a set of tokens (substrings) that
# can be used for better matching.
# NOTE: When tokenizing be sure to use the same tokenizer function for
# both the query and each string to match against


def shifter(string, chunk_size):
    """
    Generator function that slides through a string and returns strings
    of (max) length `chunk_size`, sliding one character at a time.

    Args:
        string (str): the string to walk
        chunk_size (int): the size of each chunk

    Yield:
        one chunks of `string` of size `chunk_size` on each call such as

            >>> splitter('hello, world', 3)
            'hel', 'ell', 'llo', ...

    """
    l = len(string)
    if chunk_size <= 0:
        # if requested size is less than zero return the whole string
        chunk_size = l
    if l == 0 or chunk_size >= l:
        yield string
        return

    i = 0
    stop = l - chunk_size

    while i <= stop:
        yield string[i:i + chunk_size]
        i += 1


def tokenize(string,
             regexp=config.STR_SPLIT_REGEX,
             min_len=config.MIN_WORD_LENGTH):
    """
    Given a string return a ``list`` of segments of the string,
    splitted with :any:`config.STR_SPLIT_REGEX`, removing every word <
    :any:`config.MIN_WORD_LENGTH`.

    Arguments:
        string (str): string to tokenize
        regexp (regexp): regular expression to split the string with
        min_len (int): minimum word length

    Returns:
        list - all the tokens extracted from the string in the same
        order they were found.

    Example:
        >>> utils.tokenize('hello there, how are you')
        ['hello', 'there']

    """
    return [
        w for w in re.split(regexp, string.lower())
        if len(w) > min_len and w not in config.STOP_WORDS
    ]


def tokenize_set(string,
                 regexp=config.STR_SPLIT_REGEX,
                 min_len=config.MIN_WORD_LENGTH):
    """
    Given a string returns a ``set`` of unique segments of the strings (single
    words) splitted with :any:`config.STR_SPLIT_REGEX`, removing every word <
    :any:`config.MIN_WORD_LENGTH`.

    The differences with :any:`tokenize` is that returns a set instead of a
    list, so the values are unique.

    Arguments:
        string (str): string to tokenize
        regexp (regexp): regular expression to split the string with
        min_len (int): minimum word length

    Returns:
        set - all the tokens extracted from `string` in a set

    Example:
        >>> utils.tokenize('hello there, there are some fishes there!')
        ['hello', 'there']
    """
    s = tokenize(string, regexp, min_len)
    return set(s)


def sorted_unique_tokens(
        string, regexp=config.STR_SPLIT_REGEX,
        min_len=config.MIN_WORD_LENGTH):
    """
    Return a sorted list of unique tokens contained in the string
    """
    return sorted(tokenize_set(string, regexp, min_len))


def stringify_tokens(tokens):
    """
    Given a list or set of tokens, return them as a single string
    """
    return ''.join(tokens)


def sorted_intersect(query_tokens, string_tokens):
    """
    return the sorted intersection and remainders of the two iterables

    Arguments:
        query_tokens(iterable): first elements group to intersect
        string_tokens(iterable): second elements group to intersect

    Returns:
        tuple of lists:
        * sorted intersected list - all values common to both iterables
        * sorted remainders for `query_tokens`
        * sorted remainders for `string_tokens`

    Example:

        >>> sorted_intersect([1, 3, 2, 4], [3, 4, 5])
        [3, 4], [1, 2], [5]
    """
    common = [i for i in query_tokens for j in string_tokens if i == j]
    rest_query = (el for el in query_tokens if el not in common)
    rest_string = (el for el in string_tokens if el not in common)
    return sorted(common), sorted(rest_query), sorted(rest_string)


# =====================================================================
# Normalization
# ---------------------------------------------------------------------
# Various normalization function, that given an iterable of values
# (numbers) return a list of normalized values.
# Normalization can be either scaled to 1 (higher value == 1) or
# that sums to 1 (sum of all normalized values == 1)

def normalize(iterable):
    """
    Normalize an iterable of numbers in a series that sums up to 1.

    Arguments:
        iterable(numbers): an iterable containing numbers
            (either `int` or `float`) to normalize.

    Returns:
        list: Normalized float values, in the same order as the one provided.

    Example:
        >>> normalize([3, 2, 1])
        [0.5, 0.333333, 0.166667]

    """
    tot = sum(iterable)
    return [float(v) / tot for v in iterable]


def scale_to_one(iterable):
    """
    Scale an iterable of numbers proportionally such as the highest number
    equals to 1

    Example:
        >>> scale_to_one([5, 4, 3, 2, 1])
        [1, 0.8, 0.6, 0.4, 0.2]
    """
    m = max(iterable)
    return [v / m for v in iterable]


# =====================================================================
# Averages and weighting
# ---------------------------------------------------------------------
# Functions that allows calculating arithmetic average, weighted mean
# or list elements distances (such as max_distance that returns the
# max distance from the given index to the farthest end of the list)

def average(values):
    """Return the arithmetic average of the values."""
    return sum(values) / len(values)


def weighted_average(values, weights=None):
    """Calculate the weighted mean average between two iterables of `values`
    and matching `weights`. If weights is ``None`` they will be autogenerated

    Args:
        values(iterable): Values to average, either `int` or `float`
        weights(iterable): Matching weights iterable

    Returns:
        float: weighted average

    """
    if not weights:
        weights = generate_weights(values)

    if len(values) != len(weights):
        raise ValueError(
            'Values and Weights length do not match for weighted average')
    val = sum(m * w for m, w in zip(values, weights))
    weights = sum(weights)
    return val / weights


def generate_weights(iterable, normalizer=scale_to_one):
    """
    Generate normalized weights for the iterable elements in reversed order.

    Arguments:
        iterable (iterable): iterable to generate weights for
        normalizer (func): normalizer function. one of :any:`utils.normalize`
            :any:`utils.scale_to_one` (default) or any function that operates
            similarly

    Returns:
        list - normalized floats with length matching the given iterable
        length.
    """
    weights = list(range(len(iterable), 0, -1))
    if not normalizer:
        return weights
    return normalizer(weights)


def generate_weights_from_matches(matches_list):
    """
    Given a list of matches (generated by the :any:`SearchEngine.search`),
    in the form of a list of dictionaries with an ``attr`` sortable key,
    generate a new set of weights, calculated considering how many matches
    come from a given attribute.
    This can be used to adjust the rating of the results trying to guess
    by which attribute the query was sent (i.e. a user was searching by
    a `category` attribute name), giving that attribute more weight.

    Returns:
        dict - ``{'<attribute_name:str>': <float>}```
    """
    counter = {}
    for m in matches_list:
        counter.setdefault(m['attr'], 0)
        counter[m['attr']] += 1

    sorted_attr = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    # extract only the attribute names, but in order
    sorted_attr = [a[0] for a in sorted_attr]
    # calculate a set of weights, normalized and not scaled since these are
    # adjustment weights and should have a lesser weight
    weights = generate_weights(sorted_attr, normalizer=normalize)

    return dict(zip(sorted_attr, weights))
