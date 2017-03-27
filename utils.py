"""
Utilities module for the app.
"""


def non_empty_str(val, name):
    """ Custom type for reqparser, blocking empty strings. """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


def user_exists(email):
    """
    Check that an user exists by checking the email field (unique).
    """
    user = User.select().where(User.email == email)

    return user.exists()
