from functools import wraps
from flask import session,flash,redirect,url_for
from model import User
user=''

# decorator
def login_required(func):
    @wraps(func)
    def wrapper():
        if 'username' not in session:
            flash("You need to login first","danger")
            return redirect(url_for('login'))
        retrieve_user()
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return func()
    return wrapper

def retrieve_user():
    global user
    user = User.query.filter_by(username=session['username']).first()


#these are called wrapper functions
# they take functional input and give function outputs

# they can also take, arguments like  def wrapper(*args, **kwagrgs)
# *args ->takes any no.of inputs ,all as an array
# **kwargs -> takes any no of inputs, all as key value pair (dictionary)

def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper():
        if user.username != session['username'] or user.role != session['role'] or user.role != 'admin':
            session.clear()
            flash("Not authorized","danger")
            return redirect(url_for('login'))
        return func()
    return wrapper