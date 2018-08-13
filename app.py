import datetime
import json

from flask import Flask, render_template, request, session, redirect
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

with open('config.json', 'rb') as file:
    params = json.load(file)['params']
# print(params)

app = Flask(__name__)
url = "postgresql://" + params['username'] + ":" + params['password'] + "@" + params['local_uri'] + "/ratnesh_blog"
# print(url)
app.config['SQLALCHEMY_DATABASE_URI'] = url
db = SQLAlchemy(app)

app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
))
mail = Mail(app)

app.secret_key = "secret_super_key"


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    msg = db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    tagline = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    img_url = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=True)


import math


@app.route('/')
def index():
    posts = Posts.query.filter_by().all()
    nop = int(params['no_of_posts'])
    last = math.ceil(len(posts) / nop)

    page = request.args.get('page')

    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[(page - 1) * nop: (page - 1) * nop + nop]
    if page == 1:
        prev = '#'
        next = '/?page=' + str(page + 1)
    elif page == last:
        prev = '/?page=' + str(page - 1)
        next = '#'
    else:
        prev = '/?page=' + str(page - 1)
        next = '/?page=' + str(page + 1)

    return render_template("index.html", params=params, posts=posts, prev=prev, next=next)


@app.route('/post/<string:slug_post>', methods=['GET'])
def post_route(slug_post):
    post = Posts.query.filter_by(slug=slug_post).first()
    return render_template("post.html", params=params, post=post)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session and session['user'] == params['username']:
        posts = Posts.query.filter_by().all()
        return render_template("dashboard.html", params=params, posts=posts)

    if request.method == 'POST':
        if request.form.get('username') == params['username'] and request.form.get('password') == params['password']:
            posts = Posts.query.filter_by().all()
            session['user'] = params['username']
            return render_template("dashboard.html", params=params, posts=posts)

    return render_template("login.html", params=params)


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def create_update_post(sno):
    if 'user' in session and session['user'] == params['username']:

        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_url = request.form.get('img_url')

            if sno == '0':
                post = Posts(title=title, tagline=tagline, slug=slug, content=content, img_url=img_url,
                             date=datetime.datetime.now())
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.content = content
                post.tagline = tagline
                post.slug = slug
                post.img_url = img_url
                post.date = datetime.datetime.now()
                db.session.commit()

            return redirect('/edit/' + sno)
        else:
            post = Posts.query.filter_by(sno=sno).first()
            return render_template("edit.html", params=params, post=post)


@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete_post(sno):
    if 'user' in session and session['user'] == params['username']:
        post = Posts.query.filter_by(sno=sno).first()

        db.session.delete(post)
        db.session.commit()
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('user')
    return render_template('login.html', params=params)


@app.route('/about')
def about():
    return render_template('about.html', params=params)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    ''' Add values to contacts table '''

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, email=email, mobile=phone, msg=message, date=datetime.datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New user registered',
                          sender=params['gmail_user'],
                          recipients=[params['gmail_user'], email],
                          body='You have registered with mobile no.' + '\n' + phone + '\n Message:' + message)

    return render_template('contact.html', params=params)


app.run()
