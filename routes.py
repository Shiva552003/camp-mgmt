from main import app
from flask import session,request,render_template,flash,redirect,url_for
from model import User,db
from werkzeug.security import generate_password_hash,check_password_hash
from wrappers import login_required

@app.route('/')
@login_required
def home():
   if 'username' in session and 'role' in session:
      if session['role']=='admin':
         return redirect(url_for('admin_home'))
      if session['role']=='influencer':
         return redirect(url_for('influ_home'))
      if session['role']=='sponsor':
         return redirect(url_for('spon_home'))
   else:
      flash('User not logged in',"danger")
      return redirect(url_for('login'))
   

@app.route('/login')
def login():
  return render_template('login.html',active="login")

@app.route('/login', methods=['POST'])
def login_Post():
  username=request.form.get('username_html')
  password=request.form.get('password_html')

  user=User.query.filter_by(username=username).first()
  if not user or not check_password_hash(user.password,password):
    flash("Username or password is incorrect, Please try again","danger")
    return redirect(url_for('login'))
  else:
    session['username'] = username
    session['role']=user.role
    return redirect(url_for('home'))
  
@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))
  
@app.route('/register')
def register():
    return render_template('register.html',active="register")

@app.route('/register',methods=['POST'])
def register_Post():

   username=request.form.get('username_html')
   password=request.form.get('password_html')
   confirm_pwd=request.form.get('confirm_pwd_html')
   role=request.form.get('role')

   if not role or not username or not password:
      flash("Please fill all the details","warning")
      return redirect(url_for('register'))

   if not password == confirm_pwd:
      flash("Password and Confirm Password are not matching","danger")
      return redirect(url_for('register'))
    
   user=User.query.filter_by(username=username).first()
   if user:
      print(user)
      flash("Username already exists, choose another.","info")
      return redirect(url_for('register'))

   if role and password and username:
   # return render_template('register.html',username=username,password=password,role=role,confirm_pwd=confirm_pwd, sponsor=True)

      passhash=generate_password_hash(password);
      user = User(username=username, password=passhash,role=role)
      db.session.add(user)
      db.session.commit()

      flash("Registration Successful","success")
      return redirect(url_for('login'))
