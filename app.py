from flask import Flask,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from flask_mail import Mail,Message
import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

with open('config.json','r') as c:
    params = json.load(c)["params"]

if (params['local_server']):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.secret_key = 'myKey'

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


@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
            # render_template('index.html',params=params,mesage=mesage)
            return redirect(url_for('login',mesage=mesage))

    elif request.method == 'POST':
        mesage = 'Please fill out the form !'

    return render_template('signUp.html', mesage = mesage)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
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
            return render_template('index.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'

    return render_template('login.html', mesage = mesage)

@app.route('/docCare')
def house():
    return render_template('index.html',params=params)

@app.route("/home")
def home():
    return render_template('index.html',params=params)

@app.route('/about')
def about():
    return render_template('about.html',params=params)

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

    return render_template('contact.html',params=params)

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post)


@app.route("/api/<input>")
def guess(input):
    predict_url = f"https://diseasepredict.azurewebsites.net/predict/{input}"
    predict_response = requests.get(predict_url)
    predict_data = predict_response.json()
    disease = predict_data["name"]
    
    return render_template("index.html",disease=disease,params=params)

if __name__ == '__main__':
    app.run(debug=True)

