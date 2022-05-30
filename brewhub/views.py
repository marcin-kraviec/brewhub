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


@views.route('/beer_styles', methods=['GET', 'POST'])
def beer_styles():
    american_light_lager =      {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'session-strength',  'style': 'traditional-style'}
    american_lager =            {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    cream_ale =                 {'balance': 'balanced', 'fermentation': 'any-fermentation', 'lager': '-',       'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength', 'style': 'traditional-style'}
    american_wheat_beer =       {'balance': 'balanced', 'fermentation': 'any-fermentation', 'lager': '-',       'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'wheat-beer-family',  'strength': 'standard-strength', 'style': 'craft-style'}
    international_pale_lager =  {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'international',  'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    international_amber_lager = {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'international',  'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength', 'style': 'traditional-style'}
    international_dark_lager =  {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'international',  'color': 'dark-color',  'family': 'dark-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    czech_pale_lager =          {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'session-strength',  'style': 'traditional-style'}
    czech_premium_pale_lager =  {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pilsner-family',     'strength': 'standard-strength', 'style': 'traditional-style'}
    czech_amber_lager =         {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength', 'style': 'traditional-style'}
    czech_dark_lager =          {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'dark-color',  'family': 'dark-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    munich_helles =             {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    festbier =                  {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    helles_bock =               {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'bock-family',        'strength': 'high-strength',     'style': 'traditional-style'}
    german_leichtbier =         {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'session-strength',  'style': 'traditional-style'}
    kolsch =                    {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength', 'style': 'traditional-style'}
    german_helles_exportbier =  {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength', 'style': 'traditional-style'}
    german_pils =               {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pilsner-family',     'strength': 'standard-strength', 'style': 'traditional-style'}
    marzen =                    {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength', 'style': 'traditional-style'}
    rauchbier =                 {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength', 'style': 'traditional-style'}
    dunkles_bock =              {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'bock-family',        'strength': 'high-strength',     'style': 'traditional-style'}
    vienna_lager =              {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength', 'style': 'traditional-style'}
    altbier =                   {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'standard-strength', 'style': 'traditional-style'}

    # put each beer style to one list
    styles = [american_light_lager, american_lager, cream_ale, american_wheat_beer, international_pale_lager, international_amber_lager, international_dark_lager, czech_pale_lager, czech_premium_pale_lager, czech_amber_lager, czech_dark_lager, munich_helles, festbier, helles_bock,
              german_leichtbier, kolsch, german_helles_exportbier, german_pils, marzen, rauchbier, dunkles_bock, vienna_lager, altbier]

    # get sectional parameters from html file
    balance = request.form.getlist('balance')
    fermentation = request.form.getlist('fermentation')
    lager = request.form.getlist('lager')
    feeling = request.form.getlist('feeling')
    region = request.form.getlist('region')
    color = request.form.getlist('color')
    family = request.form.getlist('family')
    strength = request.form.getlist('strength')
    style = request.form.getlist('style')

    # put all parameters into one dictionary
    filters = {'balance': balance, 'fermentation': fermentation, 'lager': lager, 'feeling': feeling, 'region': region, 'color': color, 'family': family, 'strength': strength, 'style': style}

    check_american_light_lager = False
    check_american_lager = False
    check_cream_ale = False
    check_american_wheat_beer = False
    check_international_pale_lager = False
    check_international_amber_lager = False
    check_international_dark_lager = False
    check_czech_pale_lager = False
    check_czech_premium_pale_lager = False
    check_czech_amber_lager = False
    check_czech_dark_lager = False
    check_munich_helles = False
    check_festbier = False
    check_helles_bock = False
    check_german_leichtbier = False
    check_kolsch = False
    check_german_helles_exportbier = False
    check_german_pils = False
    check_marzen = False
    check_rauchbier = False
    check_dunkles_bock = False
    check_vienna_lager = False
    check_altbier = False

    checks = [check_american_light_lager, check_american_lager, check_cream_ale, check_american_wheat_beer, check_international_pale_lager, check_international_amber_lager, check_international_dark_lager, check_czech_pale_lager, check_czech_premium_pale_lager,
              check_czech_amber_lager, check_czech_dark_lager, check_munich_helles, check_festbier, check_helles_bock, check_german_leichtbier, check_kolsch, check_german_helles_exportbier, check_german_pils, check_marzen, check_rauchbier, check_dunkles_bock,
              check_vienna_lager, check_altbier]

    for i in range(len(styles)):
        if (styles[i].get('balance') in filters.get('balance') or filters.get('balance') == []) \
                and (styles[i].get('fermentation') in filters.get('fermentation') or filters.get('fermentation') == []) \
                and (styles[i].get('lager') in filters.get('lager') or filters.get('lager') == []) \
                and (styles[i].get('feeling') in filters.get('feeling') or filters.get('feeling') == []) \
                and (styles[i].get('region') in filters.get('region') or filters.get('region') == []) \
                and (styles[i].get('color') in filters.get('color') or filters.get('color') == []) \
                and (styles[i].get('family') in filters.get('family') or filters.get('family') == []) \
                and (styles[i].get('strength') in filters.get('strength') or filters.get('strength') == []) \
                and (styles[i].get('style') in filters.get('style') or filters.get('style') == []):
            checks[i] = True

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

        elif new_username == session['username'] and new_email == session['email'] and new_bio == session['bio']:
            flash('There is nothing to update')

        else:
            db.update('users', "\'" + session['username'] + "\'", "\'" + new_username + "\'", "\'" + new_email + "\'",
                      "\'" + new_bio + "\'")

            session['username'] = new_username
            session['email'] = new_email
            session['bio'] = new_bio

            flash('The profile has been successfully updated')

    return render_template('edit_profile.html')


@views.route('/add_recipe')
def add_recipe():
    styles = ['American Light Lager', 'American Lager', 'Cream Ale', 'American Wheat Beer', 'International Pale Lager',
              'International Amber Lager']
    return render_template('recipe_form.html', styles=styles)
