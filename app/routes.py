from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app
from app.forms import LoginForm
from app.models import User, Post

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

@app.route('/menu/')
def menu():
    return render_template('menu.html')

@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/file_list/')
def file_list():
    return render_template('file_list.html')

@app.route('/settings/')
def settings():
    return render_template('settings.html')