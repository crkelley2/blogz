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

    
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('blog.html')

@app.route('/blog', methods=['POST', 'GET'])
def display_posts():
    post_id = request.args.get('id')
    if (post_id):
        post = Blog.query.get(post_id)
        return render_template('single_blog_post.html', post=post)

    else:
        compiled_posts = Blog.query.all()
        return render_template('blog.html', compiled_posts=compiled_posts)

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
        #TODO Need to add to main blog page listing all blogs,
        #including title as a link to the single blog page with get query for id
    else:
        return render_template('newpost.html', new_post_name=new_post_name, new_post_body=new_post_body)

if __name__ == '__main__':
    app.run()
