from functools import wraps
from flask import session,flash,redirect,url_for
from model import User

# decorator
def login_required(func):
    @wraps(func)
    def wrapper():
        if 'username' not in session:
            flash("You need to login first","danger")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return func()
    return wrapper


#these are called wrapper functions
# they take functional input and give function outputs

# they can also take, arguments like  def wrapper(*args, **kwagrgs)
# *args ->takes any no.of inputs ,all as an array
# **kwargs -> takes any no of inputs, all as key value pair (dictionary)