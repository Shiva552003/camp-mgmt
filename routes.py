from main import app
from flask import session,request,render_template,flash,redirect,url_for
from model import User,db
from werkzeug.security import generate_password_hash,check_password_hash

@app.route('/')
def home():
   if session['username']:
      return render_template('dashboard.html')
   else:
      flash('User not logged in',"danger")
      return redirect(url_for('login'))
   

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_Post():
  username=request.form.get('username_html')
  password=request.form.get('password_html')

  user=User.query.filter_by(username=username).first()
  if not user or check_password_hash(user.password,password):
    flash("Username or password is incorrect, Please try again","danger")
    return redirect(url_for('login'))
  else:
    session['username'] = username
    flash("Login Successful","success")
    return redirect(url_for('home'))
  
@app.route('/register')
def register():
    # user=session['username']
    user=''
    return render_template('register.html',username=user)

@app.route('/register',methods=['POST'])
def register_Post():

    username=request.form.get('username_html')
    password=request.form.get('password_html')
    confirm_pwd=request.form.get('confirm_pwd_html')
    role=request.form.get('role')

    user=User.query.filter_by(username=username).first()
    if user:
       print(user)
       flash("Username already exists, choose another.","info")
       return redirect(url_for('register'))

    if not password == confirm_pwd:
        flash("Password and Confirm Password are not matching","danger")
        return redirect(url_for('register'))
    
    if not role:
       flash("Please select role","warning")
       return redirect(url_for('register'))

    
    if role and password and username:
        passhash=generate_password_hash(password);
        user = User(username=username, password=passhash,role=role)
        db.session.add(user)
        db.session.commit()

        flash("Registration Successful","success")
        return redirect(url_for('login'))


#Todo try these out today-20th June