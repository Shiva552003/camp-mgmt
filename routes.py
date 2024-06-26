from main import app
from flask import session,request,render_template,flash,redirect,url_for
from model import User,db,Sponsor,Influencer
from werkzeug.security import generate_password_hash,check_password_hash
from wrappers import login_required

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
      passhash=generate_password_hash(password);
      user = User(username=username, password=passhash,role=role)
      db.session.add(user)
      db.session.commit()
      session['userId']=user.id

      if role == 'sponsor':
         return redirect(url_for('register_spon'))
      elif role == 'influencer':
         return redirect(url_for('register_influ'))
   
@app.route('/register_spon')
def register_spon():
   details = {}
   return render_template('/sponsor/register_spon.html',active="register",details=details)

@app.route('/register_spon', methods=['POST'])
def register_spon_post():
   name = request.form.get('name_html')
   company_name = request.form.get('company_name_html')
   industry = request.form.get('industry_html')
   desc = request.form.get('desc_html')
   cover_photo = request.files.get('cover_photo_html')

   details = {'name': name, 'company_name': company_name, 'industry': industry, 'desc': desc}

   if not name or not industry:
      flash('Please fill mandatory fields', "danger")
      return render_template('/sponsor/register_spon.html', active="register", details=details)

   cover_photo_data = None
   if cover_photo:
      mime_type = cover_photo.mimetype
      if mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
         cover_photo_data = cover_photo.read()
      else:
         flash('Invalid file format. Only PNG and JPEG are allowed.', 'danger')
         return render_template('/sponsor/register_spon.html', active="register", details=details)

   user = User.query.filter_by(id=session['userId']).first()
   sponsor = Sponsor(
      id=user.id,
      name=name,
      company_name=company_name,
      industry=industry,
      desc=desc,
      cover_photo=cover_photo_data
   )
   db.session.add(sponsor)
   db.session.commit()
   flash('Sponsor added successfully!', 'success')
   return redirect(url_for('login'))
    
@app.route('/register_influ')
def register_influ():
   details={}
   return render_template('/influencer/register_influ.html',active="register",details=details)

@app.route('/register_influ', methods=['POST'])
def register_influ_post():
   name = request.form.get('name_html')
   company_name = request.form.get('company_name_html')
   industry = request.form.get('industry_html')
   desc = request.form.get('desc_html')
   cover_photo = request.files.get('cover_photo_html')

   insta_id = request.form.get('insta_id_html')
   insta_followers = request.form.get('insta_followers_html')
   youtube_id = request.form.get('youtube_id_html')
   youtube_channel = request.form.get('youtube_channel_html')
   youtube_followers = request.form.get('youtube_followers_html')
   x_id = request.form.get('x_id_html')
   x_name = request.form.get('x_name_html')
   x_followers = request.form.get('x_followers_html')

   details = {
      'name': name,
      'company_name': company_name,
      'industry': industry,
      'desc': desc,
      'insta_id': insta_id,
      'insta_followers': insta_followers,
      'youtube_id': youtube_id,
      'youtube_channel': youtube_channel,
      'youtube_followers': youtube_followers,
      'x_id': x_id,
      'x_name': x_name,
      'x_followers': x_followers
   }

   if not name or not industry:
      flash('Please fill mandatory fields', "danger")
      return render_template('/influencer/register_influencer.html', active="register", details=details)

   cover_photo_data = None
   if cover_photo:
      mime_type = cover_photo.mimetype
      if mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
         cover_photo_data = cover_photo.read()
      else:
         flash('Invalid file format. Only PNG and JPEG are allowed.', 'danger')
         return render_template('/influencer/register_influencer.html', active="register", details=details)

   user = User.query.filter_by(id=session['userId']).first()
   influencer = Influencer(
      id=user.id,
      name=name,
      industry=industry,
      desc=desc,
      cover_photo=cover_photo_data,
      insta_id=insta_id,
      insta_followers=insta_followers,
      youtube_id=youtube_id,
      youtube_channel=youtube_channel,
      youtube_followers=youtube_followers,
      x_id=x_id,
      x_name=x_name,
      x_followers=x_followers
   )
   db.session.add(influencer)
   db.session.commit()
   flash('Influencer added successfully!', 'success')
   return redirect(url_for('login'))

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
   