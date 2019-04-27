from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBuG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    completed = db.Column(db.Boolean) 

    def __init__(self, name):
        self.name = name
        self.body = body
        self.completed = False

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('blog.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    return render_template('blog.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
