from datetime import datetime as dt

from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Post


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = dt.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index/')
@login_required
def index():
    title = 'Home'
    posts = Post.query.filter_by(author=current_user).all()
    return render_template('index.html', title=title, posts=posts)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    title = 'Sign In'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title=title, form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/users/', methods=['GET', 'POST'])
@login_required
def users():
    form = RegistrationForm()
    users = User.query.all()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
                    surname=form.surname.data,
                    email=form.email.data,
                    birthday=form.birthday.data
                    )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered!')
        return redirect(url_for('users'))
    return render_template('users.html', form=form, users=users)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts
    return render_template('user.html', user=user, posts = posts)

@app.route('/edit_profile/<username>/', methods=['GET', 'POST'])
def edit_profile(username):
    form = EditProfileForm()
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        return redirect(url_for('edit_profile', username=user.username))
    elif request.method == 'GET':
        form.username.data = user.username.title()
        form.surname.data = user.surname
        form.email.data = user.email
        form.birthday.data = user.birthday
    return render_template('edit_profile.html', form=form, user=user)