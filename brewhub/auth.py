from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import re
from brewhub.database_connector import DatabaseConnector
import os
import hashlib

auth = Blueprint('auth', __name__)

db = DatabaseConnector()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        password_hash = hashlib.sha256(password.encode('utf-8'))
        password_hash_hex = password_hash.hexdigest()
        print(password_hash_hex)

        if '\'--' in username or '\'--' in password:
            flash('Incorrect username/password!')
            print(" '-- protect from sql comment ")

        else:
            # Check if account exists using MySQL
            existing_users = db.select_from('users', "\'" + username + "\'", "\'" + str(password_hash_hex) + "\'")
            print(existing_users)
            # If account exists in accounts table in out database
            if existing_users != [] and username == existing_users[0][1] and str(password_hash_hex) == \
                    existing_users[0][3]:
                session['logged_in'] = True
                session['id'] = existing_users[0][0]
                session['username'] = existing_users[0][1]
                session['email'] = existing_users[0][2]
                session['password'] = existing_users[0][3]
                session['age'] = existing_users[0][4]
                session['bio'] = existing_users[0][5]
                # Redirect to home page
                flash('Logged in successfully!')
                return render_template('index.html')
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password!')
    return render_template('login.html')


@auth.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('age', None)
    session.pop('bio', None)
    # Redirect to login page
    flash('Logged out...')
    return render_template('index.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    ages = list(range(18, 100))

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'confirm_password' in request.form and 'age' in request.form and 'bio' in request.form:

        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password = request.form['confirm_password']
        age = request.form['age']
        bio = request.form['bio']

        password_hash = hashlib.sha256(password.encode('utf-8'))
        password_hash_hex = password_hash.hexdigest()
        print(password_hash_hex)

        if '\'--' in username or '\'--' in password or '\'--' in confirm_password or '\'--' in email or '\'--' in bio:
            flash('Incorrect input data')
            print(" '-- protect from sql comment ")

        else:
            # Check if account exists using MySQL
            existing_users = db.select_from_registration('users')
            print(existing_users)

            # If account exists show error and validation checks
            if username in existing_users:
                flash('Account already exists!')

            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')

            elif not re.match(r'[A-Za-z0-9]+', username):
                flash('Username must contain only characters and numbers!')

            elif password != confirm_password:
                flash('Retyped password is not correct!')

            elif not username or not password or not email:
                flash('Please fill out the form!')

            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                db.insert_into('users', "\'" + username + "\'", "\'" + email + "\'",
                               "\'" + str(password_hash_hex) + "\'",
                               "\'" + str(age) + "\'", "\'" + bio + "\'")
                flash('You have successfully registered!')
                return render_template('login.html')

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form")

    # Show registration form with message (if any)
    return render_template('register.html', ages=ages)
