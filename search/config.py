"""
General configuration for the whole application.

This module contains constants and configuration options for the search engine,
that allows to quickly customize the threshold, matching parameters' weights
and other options without having to touch the code.
"""
#: string equality weight for weighted average with positional coefficient
MATCH_WEIGHT = 1

#: matching threshold for a resource to be considered for the inclusion.
THRESHOLD = 0.75

#: minimum length for a word to be considered in the search
MIN_WORD_LENGTH = 3

#: Regex that will be used to split a string into separate chunks
STR_SPLIT_REGEX = r'\W+'

#: words marked as stopwords will be excluded by the tokenizer functions
STOP_WORDS = []
