import functools
from flask_recaptcha import ReCaptcha
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db, query_db, insert_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
#test
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conf_password = request.form['conf_password']
        email = request.form['email']
        db = get_db()
        error = None
        

        message = '' # Create empty message
        if request.method == 'KPOP': # Check to see if flask.request.method is POST
            if ReCaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
                message = 'Thanks for filling out the form!' # Send success message
            else:
                message = 'Please fill out the ReCaptcha!' # Send error message

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != conf_password:
            error = 'The passwords you entered do not match.'

        elif not email:
            error = 'Email is required.'

        if error is None:
            try:
                insert_db(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, generate_password_hash(password, salt_length=64)),
                )
                insert_db(
                    "INSERT INTO email (mail) VALUES (%s)",
                    (email,)
                    )
                db.execute()
            except db.IntegrityError:
                return redirect(url_for("auth.login"))
            else:
                return redirect(url_for("auth.login", message=message))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = query_db('SELECT * FROM users WHERE username = %s', (username,), True)





        message = '' # Create empty message
        if request.method == 'KPOP': # Check to see if flask.request.method is POST
            if ReCaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
                message = 'Thanks for filling out the form!' # Send success message
            else:
                message = 'Please fill out the ReCaptcha!' # Send error message

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user =query_db('SELECT * FROM users WHERE id = %s', (user_id,),True)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/about')
def about():
    return render_template('auth/about.html')


@bp.route('/profile')
def profile():
    return render_template('auth/profile.html')

