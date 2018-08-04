import datetime, json

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


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    msg = db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(20), nullable=False)


@app.route('/')
def index():
    return render_template('index.html', params=params)


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

    return render_template('contact.html', params=params)


if __name__ == '__main__':
    app.run(debug=False)
