import re

STOP_WORDS = [
    'in', 'con', 'da', 'di', 'del', 'dal', 'su', 'per', 'tra', 'fra',
]


def _dec(fl):
    """Return a stringified more readable float."""
    return '{:.2f}'.format(fl)


def clean_split(string):
    """
    Given a string return a list of segments of the string,
    splitted by `r'\W+`, removing shorter than 3 strings.
    """
    return [
        w for w in re.split(r'\W+', string)
        if len(w) >= 3 and w not in STOP_WORDS
    ]


def get_max_moves(list_, idx):
    """
    Given a list an int in range(len(list_)), determine the maximum
    amount of `movements` available from that index position in the list.

    >>> max_moves(['a','b','c','d'], 2)
        # 2 -> 1 left, 2 right
    """

    l = len(list_)
    min_moves = l // 2
    moves = min_moves + abs(min_moves - idx + 1)
    # compensate for even length lists
    moves -= 1 if l % 2 == 0 and idx < min_moves else 0
    return moves


def pos_dist(s1, s2, l1, l2):
    """
    Get the inverted movement cost for s1 in l1 to s2 in l2, such as
    1 == no movement, ~ 0 == max movement possible.

    FIXME: Needs fixing for not retuning 0 values.
    Return value should be 1 if position is the same, lessening
    exponentially for every movement needed BUT NEVER reaching 0
    """
    if len(l2) == 1:
        return 1
    s1idx = l1.index(s1)
    s2idx = l2.index(s2)
    moves = abs(s1idx - s2idx)
    max_moves = get_max_moves(l1, idx=s2idx)

    # move_cost = 1 / max_moves
    return abs(1 - (moves / max_moves))
