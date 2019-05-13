from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBuG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fakdakt0pmjda>adalkkjfla'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') 

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'display_posts', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET']) #Messy but works (with old blogs page with all posts; still need to connect posts/owners, etc)
def login(): #REFACTORED to deal with login errors separately with error messages in instructions
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['username'] = username
                flash('Welcome Back, '+user.username)
                return redirect("/newpost")
            else:
                flash('The password you entered is not correct')
                return redirect("/login")
        if users.count() == 0:
            flash('The username you entered does not exist')
            return redirect("/login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        usernameError = ""
        passwordError = ""
        verifyError = ""

        if (not username) or (username.strip() == ""):
            usernameError = "You must enter a username"
        elif (len(username) < 3) or (" " in username):
            usernameError = "Your name must contain 3 characters and no spaces"
        
        if (not password) or (password.strip() == ""):
            passwordError = "You must enter a password"
        elif (len(password) < 3) or (" " in password):
            passwordError = "Your password must contain 3 characters and no spaces"
        
        if (not verify) or (verify.strip() == ""):
            verifyError = "You must complete this field"
        elif verify != password:
            verifyError = "The passwords you entered do not match. Please try again"

        if usernameError or passwordError or verifyError:
            return render_template("signup.html", title="SignUp", username=username, usernameError=usernameError, password="", passwordError=passwordError, verify="", verifyError=verifyError)

        #TODO Validation: DONE USING USER SIGNUP MAIN AND SIGNUP HTML...
        #Do I need to change others re flash messages??? Can they co-exist?

        else:
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("Logged in")
                return redirect("/newpost") # TODO Fix this to render at /newpost rather than signup; cannot get redirect to work; server errors!!
            else:
                flash('Username already exists')
                return render_template('signup.html') #This WORKS but lost styles.css when it rendered??????
    else:
        return render_template('signup.html')


@app.route('/', methods=['POST', 'GET']) #TODO Refactor index per directions and logout to login, I think. Right now, it goes here w/o all posts.
def index():
    compiled_users = User.query.all()
    return render_template('index.html', compiled_users=compiled_users)


@app.route('/blog', methods=['POST', 'GET'])
def display_posts():
    post_id = request.args.get('id')
    if (post_id):
        post = Blog.query.get(post_id)
        return render_template('single_blog_post.html', post=post)

    else:
        compiled_posts = Blog.query.all()
        return render_template('blog.html', compiled_posts=compiled_posts)

#DONE: refactor newpost route handler function since
#there is a new parameter (owner) to consider 
#need to define owner to be user in session and add owner argument to blog;
#TODO need to pass current user when gathering blog entries and single post for existing user...etc

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    if request.method == 'POST':
        new_post_name = request.form['name']
        new_post_body = request.form['body']
        
        if (not new_post_name) or (not new_post_body):
            flash("You must enter both a Name and content for your new Blog post")
            return render_template('newpost.html', new_post_name=new_post_name, new_post_body=new_post_body)
    
        else:     
            new_post = Blog(new_post_name, new_post_body, current_user())
            db.session.add(new_post)
            db.session.commit()

            new_url = "/blog?id=" + str(new_post.id)
            return redirect(new_url)
        
    else:
        return render_template('newpost.html')

#This is working a/o 5/11 8:21 p.m., in the sense that post blog posts new posts
#And they are added to the list of all blogs too.
#I've not yet tried to list all posts by a single user separately though, so...
def current_user(): 
    owner = User.query.filter_by(username=session['username']).first()
    return owner


@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect("/blog")


if __name__ == '__main__':
    app.run()
