from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from models import db, User, Policy
#from forms import RegistrationForm, LoginForm, PolicyForm
from django import forms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load user by ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for homepage
@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

# Route for registering a new user
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Route for user login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

# Dashboard route for viewing policies
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    policies = Policy.query.filter_by(user_id=current_user.id).all()
    form = PolicyForm()
    if form.validate_on_submit():
        policy = Policy(policy_number=form.policy_number.data,
                        policy_name=form.policy_name.data,
                        premium_amount=form.premium_amount.data,
                        start_date=form.start_date.data,
                        expiry_date=form.expiry_date.data,
                        holder=current_user)
        db.session.add(policy)
        db.session.commit()
        flash('Policy added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', form=form, policies=policies)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
