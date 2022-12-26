from flask import Flask,flash,render_template,request,redirect,url_for,session,abort
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from flask_mail import Mail,Message
import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import os
import pathlib
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests



app = Flask(__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

with open('config.json','r') as c:
    params = json.load(c)["params"]

if (params['local_server']):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.secret_key = 'myKey'

GOOGLE_CLIENT_ID = "73820933913-b8q6s1a77gkufpd9cd6nuctfvrt662ov.apps.googleusercontent.com"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent,"client_secret.json")

flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets_file,
                                    scopes=["https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email","openid"],
                                    redirect_uri="http://127.0.0.1:5000/callback"    )

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'   
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mycontactdb'

mysql = MySQL(app)

mail = Mail(app)
app.config.update(
    MAIL_SERVER = 'stmp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-pass']
)

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer,primary_key=True )
    name = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String(30),nullable=False )
    phone_no = db.Column(db.String(13),nullable=False )
    mesg = db.Column(db.String(100),nullable=False )
    date = db.Column(db.String(20),nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer,primary_key=True )
    title = db.Column(db.String(50),nullable=False)
    slug = db.Column(db.String(25),nullable=False)
    content = db.Column(db.String(300),nullable=False )
    date = db.Column(db.String(20),nullable=True)
    img_file = db.Column(db.String(20),nullable=True)

x = None
def login_is_required(function):
    def wrapper(*args,**kwargs):
        if "google_id" not in session and session['loggedin'] is False:
            abort(401) # authentication requires
        else:
            return function()   
    return wrapper   

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        re_password = request.form['re_pass']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        
        elif not userName or not password or not email :
            mesage = 'Please fill out the form !'
            
        elif userName and re_password:
            if userName != re_password:
                mesage = 'Please re_enter Password correctly'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
            # render_template('index.html',params=params,mesage=mesage)
            return redirect(url_for('login',mesage=mesage))

    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
        return render_template('signUp.html',mesage=mesage)


    return render_template('signUp.html', mesage = mesage)

@app.route('/',methods =['GET', 'POST'])
@app.route('/login/<mesage>', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            
            #return render_template('index.html', mesage = mesage,params=params)
            session['loggedin'] = True
            return redirect('/house')
        else:
            mesage = 'Please enter correct email / password !'
            flash('Please enter correct email/password')
            # redirect(url_for('login'))
            # return render_template('login.html',mesage=mesage,params=params)

    return render_template('login.html', mesage=mesage,params = params)

@app.route('/login_google')
def login_google():
    authorization_url,state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response= request.url)
    if not session["state"] == request.args["state"]:
        abort(500) # state doesnot match

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    global x
    x = id_info

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["picture"] = id_info.get("picture")
    # return id_info
    return redirect("/house")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/house",methods=['GET','POST'])
@login_is_required
def house():
    return render_template('index.html',params=params,ur_name = session['name'],pic=session["picture"])

@app.route('/about')
def about():
    return render_template('about.html',params=params,pic=session["picture"])

@app.route('/contact',methods = ['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNo = request.form.get('phoneNo')
        messg = request.form.get('messg')
        entry = Contacts(name=name,email=email,phone_no=phoneNo,mesg=messg,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
       
        # msg = Message(
        #         'Message from' + name,
        #         sender = email,
        #         recipients = [params['gmail-user']]
        #        )
        # msg.body = 'Hello Flask message sent from Flask-Mail'
        # mail.send(msg)
        
    
    return render_template('contact.html',params=params,infor=x,pic=session["picture"])

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post,pic=session["picture"])


@app.route("/api/<input>")
def guess(input):
    predict_url = f"https://diseasepredictapp.azurewebsites.net/predict/{input}"
    predict_response = requests.get(predict_url)
    predict_data = predict_response.json()
    disease = predict_data["name"]
    
    return render_template("index.html",disease=disease,params=params,pic=session["picture"])

@app.route("/heart-report-analysis",methods=['GET','POST'])
def report():
    dict={}
    if request.method == 'POST':
        dict['age']=float(request.form.get('age'))
        dict['sex']=float(request.form.get('sex'))
        dict['chest']=float(request.form.get('chest'))
        dict['BP']=float(request.form.get('BP'))
        dict['cholesterol'] = float(request.form.get('cholesterol'))
        dict['FBS']=float(request.form.get('FBS'))
        dict['EKG']=float(request.form.get('EKG'))
        dict['hr']=float(request.form.get('hr'))
        dict['angina']=float(request.form.get('angina'))
        dict['st']=float(request.form.get('st'))
        dict['slope']=float(request.form.get('slope'))
        dict['vessels']=float(request.form.get('vessels'))
        dict['thallium']=float(request.form.get('thallium'))


        dict['age'] = (dict['age']-29)/(77-29)
        dict['chest'] = (dict['chest']-1)/(4-1)
        dict['BP'] = (dict['BP']-29)/(200-94)
        dict['cholesterol'] = (dict['cholesterol']-126)/(564-126)
        dict['EKG'] = (dict['EKG']-0)/(2-0)
        dict['hr'] = (dict['hr']-71)/(202-71)
        dict['st'] = (dict['st']-0)/(6.2-0)
        dict['slope'] = (dict['slope']-1)/(3-1)
        dict['vessels'] = (dict['vessels']-0)/(3-0)
        dict['thallium'] = (dict['thallium']-3)/(7-3)

        strg=""
        for key in dict:
            strg+=str(dict[key])
            strg+="_"
        
        strg=strg[:-1]

        predict_url = f"https://diseasepredictapp.azurewebsites.net/heartdisease/{strg}"
        predict_response = requests.get(predict_url)
        predict_data = predict_response.json()
        result=predict_data["result"]
        return render_template('heartdisease.html',result=result,params=params,ur_name = session['name'])

    return render_template('heartdisease.html',params=params,ur_name = session['name'],pic=session["picture"])

@app.route("/heartdisease/<input>")
def heart(input):
        return render_template('heartdisease.html',pic=session["picture"])

if __name__ == '__main__':
    app.run(debug=True)

