
def non_empty_str(val, name):
    """ Custom type for reqparser, blocking empty strings. """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)
