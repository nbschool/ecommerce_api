from flask_login import LoginManager

from models import User


login_manager = LoginManager()


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
