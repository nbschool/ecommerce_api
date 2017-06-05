"""
This module contains constants and configuration options for the search engine,
that allows to quickly customize the threshold, matching parameters' weights
and other options without having to touch the code.
"""
#: string equality weight for weighted average with positional coefficient
MATCH_WEIGHT = 0.2

#: positional coeff weight for weighted avg with equality match
DIST_WEIGHT = 0.8

#: matching threshold for a resource to be considered for the inclusion.
THRESHOLD = 0.75

#: minimum length for a word to be considered in the search
MIN_WORD_LENGTH = 3

#: Regex that will be used to split a string into separate chunks
STR_SPLIT_REGEX = r'\W+'
