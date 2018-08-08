import datetime, json
from flask_mail import Mail
from flask import Flask, render_template, request
from sqlalchemy.databases import postgresql, postgres
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
    slug = db.Column(db.String(25), nullable=False)
    img_url = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=True)


@app.route('/')
def index():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template("index.html", params=params, posts=posts)


@app.route('/post/<string:slug_post>', methods=['GET'])
def post_route(slug_post):
    post = Posts.query.filter_by(slug=slug_post).first()
    return render_template("post.html", params=params, post=post)


@app.route('/about')
def about():
    return render_template('about.html', params=params)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    '''Add values to contacts table'''

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


if __name__ == '__main__':
    app.run(debug=True)
