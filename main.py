from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBuG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fakdakt0pmjda>adalkkjfla'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    completed = db.Column(db.Boolean) 

    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.completed = False

    def is_valid(self):
        if self.name and self.body:
            return True
        else:
            return False

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('blog.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    return render_template('blog.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    new_post_name = ""
    new_post_body = ""
    new_url = ""

    if request.method == 'POST':
        new_post_name = request.form['name']
        new_post_body = request.form['body']
        new_post = Blog(new_post_name, new_post_body)

        if (not new_post_name) or (not new_post_body):
            flash("You must enter both a Name and content for your new Blog post")
            return render_template('newpost.html', new_post_name=new_post_name, new_post_body=new_post_body)
    
        else:     
            db.session.add(new_post)
            db.session.commit()

            new_url = "/blog?id=" + str(new_post.id)
            return redirect(new_url)
        #TODO Need to show new post on page alone and add to main list page too
    else:
        return render_template('newpost.html', new_post_name=new_post_name, new_post_body=new_post_body)

if __name__ == '__main__':
    app.run()
