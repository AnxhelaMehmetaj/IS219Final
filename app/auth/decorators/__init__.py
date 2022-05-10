from functools import wraps
from flask_login import current_user
from flask import render_template, session, redirect


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin != 1:
            return render_template('403.html'), 403
        return f(*args, **kwargs)
    return decorated_function
def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

