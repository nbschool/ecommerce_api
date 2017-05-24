from flask_login import login_required, LoginManager
from flask_login import current_user

from models import User


login_manager = LoginManager()


class Auth:
    @property
    def current_user(self):
        return current_user._get_current_object()


auth = Auth()
auth.login_required = login_required


def init_app(app):
    return login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(User.id == user_id)
    except User.DoesNotExist:
        return None


@login_manager.request_loader
def load_user_from_request(request):
    if not request.authorization:
        return None
    try:
        user = User.get(User.email == request.authorization['username'])
    except User.DoesNotExist:
        return None

    if user.verify_password(request.authorization['password']):
        return user
    return None
