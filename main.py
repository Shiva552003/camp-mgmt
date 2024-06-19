from flask import Flask,render_template,request
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
secret_key=os.getenv('SECRET_KEY')

@app.route('/')
def hello_world():
  return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
  username=request.form.get('exampleInputEmail1')
  password=request.form.get('exampleInputPassword1')

  if username == "abc" and password== "1234":
    return "Correct"
  else:
    return "incorrect"

if __name__ == '__main__':
  app.run(debug=True)
