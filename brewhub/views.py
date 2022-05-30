from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import re
from brewhub.database_connector import DatabaseConnector
import os
import hashlib

views = Blueprint('views', __name__)

db = DatabaseConnector()


@views.route('/')
def home():
    return render_template('index.html')


@views.route('/categories')
def categories():
    return render_template('categories.html')


@views.route('/test')
def test():
    return render_template('test.html')


@views.route('/login', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        password_hash = hashlib.sha256(password.encode('utf-8'))
        password_hash_hex = password_hash.hexdigest()
        print(password_hash_hex)

        # Check if account exists using MySQL
        existing_users = db.select_from('users', "\'" + username + "\'", "\'" + str(password_hash_hex) + "\'")
        print(existing_users)
        # If account exists in accounts table in out database
        if existing_users != [] and username == existing_users[0][1] and str(password_hash_hex) == existing_users[0][3]:
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


@views.route('/logout')
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


@views.route('/register', methods=['GET', 'POST'])
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
            db.insert_into('users', "\'" + username + "\'", "\'" + email + "\'", "\'" + str(password_hash_hex) + "\'",
                           "\'" + str(age) + "\'", "\'" + bio + "\'")
            flash('You have successfully registered!')
            return render_template('login.html')

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form")

    # Show registration form with message (if any)
    return render_template('register.html', ages=ages)


@views.route('/beer_styles', methods=['GET', 'POST'])
def beer_styles():
    american_light_lager = {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered',
                            'country': 'north-america', 'color': 'pale-color', 'family': 'pale-lager-family',
                            'strength': 'session-strength', 'style': 'traditional-style'}
    american_lager = {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered',
                      'country': 'north-america', 'color': 'pale-color', 'family': 'pale-lager-family',
                      'strength': 'standard-strength', 'style': 'traditional-style'}
    cream_ale = {'balance': 'balanced', 'fermentation': 'any-fermentation', 'country': 'north-america',
                 'color': 'pale-color', 'family': 'pale-ale-family', 'strength': 'standard-strength',
                 'style': 'traditional-style'}
    american_wheat_beer = {'fermentation': 'any-fermentation', 'balance': 'balanced', 'style': 'craft-style',
                           'country': 'north-america', 'color': 'pale-color', 'strength': 'standard-strength',
                           'family': 'wheat-beer-family'}
    international_pale_lager = {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered',
                                'color': 'pale-color', 'family': 'pale-lager-family', 'strength': 'standard-strength',
                                'style': 'traditional-style'}
    international_amber_lager = {'color': 'amber-color', 'family': 'amber-lager-family',
                                 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'malty': 'malty',
                                 'strength': 'standard-strength', 'style': 'traditional-style'}

    # put each beer style to one list
    styles = [american_light_lager, american_lager, cream_ale, american_wheat_beer, international_pale_lager,
              international_amber_lager]

    # get sectional parameters from html file
    balance = request.form.getlist('balance')
    fermentation = request.form.getlist('fermentation')
    lager = request.form.getlist('lager')
    malty = request.form.getlist('malty')
    country = request.form.getlist('country')
    color = request.form.getlist('color')
    family = request.form.getlist('family')
    strength = request.form.getlist('strength')
    style = request.form.getlist('style')

    # put all parameters into one dictionary
    filters = {'balance': balance, 'fermentation': fermentation, 'lager': lager, 'malty': malty, 'country': country,
               'color': color, 'family': family, 'strength': strength, 'style': style}

    check_american_light_lager = False
    check_american_lager = False
    check_cream_ale = False
    check_american_wheat_beer = False
    check_international_pale_lager = False
    check_international_amber_lager = False

    checks = [check_american_light_lager, check_american_lager, check_cream_ale, check_american_wheat_beer,
              check_international_pale_lager, check_international_amber_lager]

    for i in range(len(styles)):
        if (styles[i].get('balance') in filters.get('balance') or filters.get('balance') == []) \
                and (styles[i].get('fermentation') in filters.get('fermentation') or filters.get('fermentation') == []) \
                and (styles[i].get('lager') in filters.get('lager') or filters.get('lager') == []) \
                and (styles[i].get('malty') in filters.get('malty') or filters.get('malty') == []) \
                and (styles[i].get('country') in filters.get('country') or filters.get('country') == []) \
                and (styles[i].get('color') in filters.get('color') or filters.get('color') == []) \
                and (styles[i].get('family') in filters.get('family') or filters.get('family') == []) \
                and (styles[i].get('strength') in filters.get('strength') or filters.get('strength') == []) \
                and (styles[i].get('style') in filters.get('style') or filters.get('style') == []):
            checks[i] = True

    # check_american_light_lager = any(item in american_light_lager for item in filters)
    # check_american_lager = any(item in american_lager for item in filters)
    # check_cream_ale = any(item in cream_ale for item in filters)
    # check_american_wheat_beer = any(item in american_wheat_beer for item in filters)
    # check_international_pale_lager = any(item in international_pale_lager for item in filters)
    # check_international_amber_lager = any(item in international_amber_lager for item in filters)

    # if not filters:
    #     check_american_light_lager = True
    #     check_american_lager = True
    #     check_cream_ale = True
    #     check_american_wheat_beer = True
    #     check_international_pale_lager = True
    #     check_international_amber_lager = True

    # return render_template('beer_styles.html', check_american_light_lager=check_american_light_lager)

    return render_template('beer_styles.html', checks=checks)


@views.route('/beer_styles/<string:s>', methods=['GET', 'POST'])
def beer_styles_2(s=''):
    print(s)
    # styles = list()
    # styles.append('American Light Lager')
    # styles.append('American Lager')
    # print(styles)
    return render_template('beer_styles_2.html', s=s)


@views.route('/profile')
def view_profile():
    return render_template('profile.html')


@views.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']
        new_bio = request.form['bio']
        password = request.form['password']

        password_hash = hashlib.sha256(password.encode('utf-8'))
        password_hash_hex = password_hash.hexdigest()

        if new_username != '' and not re.match(r'[A-Za-z0-9]+', new_username):
            flash('Username must contain only characters and numbers!')

        elif new_email != '' and not re.match(r'[^@]+@[^@]+\.[^@]+', new_email):
            flash('Invalid email address!')

        elif password_hash_hex != session['password']:
            flash('Incorrect password')

        elif new_username == '' and new_email == '' and new_bio == '':
            flash('Fill in at least one field to update')

        else:
            if new_username == '':
                new_username = session['username']
            if new_email == '':
                new_email = session['email']
            if new_bio == '':
                new_bio = session['bio']

            db.update('users', "\'" + session['username'] + "\'", "\'" + new_username + "\'", "\'" + new_email + "\'", "\'" + new_bio + "\'")

            session['username'] = new_username
            session['email'] = new_email
            session['bio'] = new_bio

            flash('The profile has been successfully updated')

    return render_template('edit_profile.html')
