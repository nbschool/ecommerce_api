"""
Utility module for the search engine, contains various functions to do common
operations on lists and set of iterables
"""
import re
from search import config


def _dec(fl):
    """Return a stringified more readable float, for debugging purposes."""
    return '{:.2f}'.format(fl)


def normalize(iterable):
    """
    Normalize an iterable of numbers in a series that sums up to 1.

    Arguments:
        iterable (numbers): an iterable containing numbers (either `int` or
            `float`) to normalize.

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
        >>> scale_to_one([5,4,3,2,1])
        [1, 0.8, 0.6, 0.4, 0.2]
    """
    m = max(iterable)
    return [v / m for v in iterable]


def weighted_avg(values, weights):
    """Calculate the weighted mean average between two iterables of `values`
    and matching `weights`

    Args:
        values(iterable): Values to average, either `int` or `float`
        weights(iterable): Matching weights iterable

    Returns:
        float: weighted average

    """
    if len(values) != len(weights):
        raise ValueError(
            'Values and Weights length do not match for weighted average')
    val = sum(m * w for m, w in zip(values, weights))
    weights = sum(weights)
    return val / weights


def tokenize(string):
    """
    Given a string return a list of segments of the string,
    splitted with :any:`config.STR_SPLIT_REGEX`, removing every word <=
    :any:`config.MIN_WORD_LENGTH`.

    Example:
        >>> utils.tokenize('hello there, how are you')
        ['hello', 'there']

    """
    return [
        w for w in re.split(config.STR_SPLIT_REGEX, string)
        if len(w) > config.MIN_WORD_LENGTH
    ]


def get_max_moves(list_, idx):
    """
    Given a list an int in range(len(list_)), determine the maximum
    amount of `movements` available from that index position in the list.

    Arguments:
        list_(any with __len__): iterable to calculate the maximum moves into.
            It's used only to get its `len`, so any object that implements the
            `__len__` method will do.
        idx(int): integer representing the index of the position to count
            from. The value ** must ** be `>= 0` but ** can ** be over the length
            of the list.

    Returns:
        int: maximum moves available in any direction.

    Example:
        >>> utils.get_max_moves(['a', 'b', 'c', 'd', 'e'], 1)
        4  # idx 1 -> 'b', so max is 4 moves right
        >>> utils.get_max_moves(['a', 'b', 'c', 'd', 'e'], 6)
        5  # can move left 5
    """

    length = len(list_)
    return max(idx, (length - (idx + 1)))


def pos_dist(s1, s2, l1, l2):
    """
    Get the normalized inverted movement cost for for between `s1` and s2`
    on the `l2` iterable.

    The function is used to get a value describing how far two words are in a
    phrase(as list, as in ``string.split(' ')`` or, in our case through
    :func:`search.utils.tokenize').

    Moves are relative to s1 on l1, which `should` be the longest set for the
    function to work properly.

    .. note: : The given strings ** MUST ** be inside the corresponding list.

    Arguments:
        s1(str): string inside ``l1`` iterable
        s2(str): string inside ``l2`` iterable
        l1(iterable): iterable allowing the ``index`` method, should be the
            longest of the two iterables
        l2(iterable): iterable allowing the ``index`` method, should be the
            shortest of the two iterables

    Returns:
        float: value ``0 -> 1`` representing how far the two words are afar,
        where ``1`` represent the closest(same position) and tending to zero
        the farthest on the maximum available moves possible on ``l1``

    """
    if len(l2) == 1:
        return 1
    s1idx = l1.index(s1)
    s2idx = l2.index(s2)
    moves = abs(s1idx - s2idx)
    max_moves = get_max_moves(l1, idx=s1idx)

    return abs(1 - (moves / max_moves))
