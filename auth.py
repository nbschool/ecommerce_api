"""Auth module handles authorization requests and checks."""

from flask_login import login_required, LoginManager

from models import User

login_manager = LoginManager()


class Auth:
    """
    Auth manager class, it offers methods to get the current user
    and to initialize the login manager of the app.
    """

    @staticmethod
    def login_required(*args, **kwargs):
        """Forward flask_login login_required method"""
        return login_required(*args, **kwargs)

    @property
    def current_user(self):
        """
        This method returns the currently logged user (``models.User``).
        We forward the flask_login current_user converted from a proxy object
        to our ``models.User``. We import the flask_login current_user inside
        the method to forbid a direct import from flask_login.
        Returns:
            models.User: currently logged user
        """
        from flask_login import current_user
        return current_user._get_current_object()

    @staticmethod
    def init_app(app):
        """
        Wrapper for the flask_login method ``LoginManager::init_app``.

        Args:
            Flask app (Flask): The Flask app to initialize with the
                login manager
        """
        return login_manager.init_app(app)


auth = Auth()


@login_manager.user_loader
def load_user(user_id):
    """
    Current user loading logic. If the user exists return it, otherwise None.

    Args:
        user_id (int): Peewee user id
    Returns:
        models.User: The requested user
    """
    try:
        return User.get(User.id == user_id)
    except User.DoesNotExist:
        return None


@login_manager.request_loader
def load_user_from_request(request):
    """
    User login validation logic. If the user exists with the given username
    and with the correct password then returns the user, otherwise None.

    Args:
        request (Request): The flask request object used in endpoint handlers
    Returns:
        models.User: The logged user, None if login fails
    """
    if not request.authorization:
        return None
    try:
        user = User.get(User.email == request.authorization['username'])
    except User.DoesNotExist:
        return None

    if user.verify_password(request.authorization['password']):
        return user
    return None
