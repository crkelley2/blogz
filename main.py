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
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET']) #Messy but works (with old blogs page with all posts; still need to connect posts/owners, etc)
def login(): #REFACTOR to deal with login errors separately with error messages indicated below!
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                flash('Welcome Back, '+user.username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")
#TODO REMOVE THIS WHEN DONE! def login(): #POST /login not working yet; 500 error when "submit" with accurate info
#    if request.method == 'POST':
#        username = request.form('username')
#       password = request.form('password')
#       user = User.query.filter_by(username=username).first()
#       if user and (User.password == password):
#           session['username'] = username
#           flash("Logged in")
#           return render_template('newpost.html')#actually need to redirect but haven't succeeded with signup; getting error 500 here
#       elif user and (User.password != password):
#           flash('The password you entered is incorrect', 'error')
#       elif not user:
#           flash('The username you entered does not exist', 'error')
            
#   return render_template('login.html')

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

        #TODO Add validation: DONE USING USER SIGNUP MAIN AND SIGNUP HTML...
        #If pull code from user signup, do I change base html re flash messages???
        #If no code from user signup, change signup html re flash messages

        else:
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("Logged in")
                return render_template('newpost.html')#TODO Fix this to render at /newpost rather than signup; could not get redirect to work!
            else:
                flash('Username already exists')
                return render_template('signup.html')
    else:
        return render_template('signup.html')


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

#TODO refactor newpost route handler function since
#there is a new parameter (owner) to consider 
#when creating a blog entry. I put owner below in new_post argument but
#need to define owner to be user in session and add owner argument to blog;
#Also need to pass user logged in when gathering blog entries and single post for existing user...etc

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    new_post_name = ""
    new_post_body = ""
    new_url = ""

    if request.method == 'POST':
        new_post_name = request.form['name']
        new_post_body = request.form['body']
        new_post = Blog(new_post_name, new_post_body, owner)

        if (not new_post_name) or (not new_post_body):
            flash("You must enter both a Name and content for your new Blog post")
            return render_template('newpost.html', new_post_name=new_post_name, new_post_body=new_post_body)
    
        else:     
            db.session.add(new_post)
            db.session.commit()

            new_url = "/blog?id=" + str(new_post.id)
            return redirect(new_url)
        
    else:
        return render_template('newpost.html', new_post_name=new_post_name, new_post_body=new_post_body)


@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")


if __name__ == '__main__':
    app.run()
