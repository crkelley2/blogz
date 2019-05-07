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
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form('username')
        password = request.form('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and user.password != password:
            flash('The password you entered is incorrect', 'error')
        elif not user:
            flash('The username you entered does not exist', 'error')
            
    return render_template('login.html')
#TODO Don't forget nav bar in login.html to "Create Account" directed to /signup page

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        usernameError = ""
        passwordError = ""
        verifyError = ""

        if (not username) or (username.strip() == ""):
            nameError = "You must enter a username"
        elif (len(name) < 3) or (" " in name):
            nameError = "Your name must contain 3 characters and no spaces"
        
        if (not password) or (password.strip() == ""):
            passwordError = "You must enter a password"
        elif (len(password) < 3) or (" " in password):
            passwordError = "Your password must contain 3 characters and no spaces"
        
        if (not verify) or (verify.strip() == ""):
            passwordError = "You must complete this field"
        elif verify != password:
            verifyError = "The passwords you entered do not match. Please try again"

        if nameError or passwordError or verifyError:
            return render_template("signup.html", title="SignUp", name=name, nameError=nameError, password="", passwordError=passwordError, verify="", verifyError=verifyError)

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
                return redirect('/newpost')
            else:
                flash('Username already exists')
                return render_template('signup.html')

    return render_template('signup.html')

@app.route('/signup', methods=['GET'])
def signup_page():
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
#when creating a blog entry. Tried owner below in new_post =
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

if __name__ == '__main__':
    app.run()
