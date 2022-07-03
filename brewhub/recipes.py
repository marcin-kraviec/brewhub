from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, json
import re
from brewhub.database_connector import DatabaseConnector
import os
import hashlib
import datetime
import smtplib
from email.message import EmailMessage
import codecs
from jinja2 import Environment, FileSystemLoader
from brewhub.database_config import PASSWORD_FOR_MAIL_ACCOUNT

recipes = Blueprint('recipes', __name__)

# data necessary to email sending service
EMAIL_ADDRESS = 'brewhub22@gmail.com'
EMAIL_PASSWORD = PASSWORD_FOR_MAIL_ACCOUNT


# email sending service
class MailService:
    def __init__(self):
        #   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as self.smtp:
        #   self.smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        self.smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
        self.smtpObj.ehlo()
        self.smtpObj.starttls()
        self.smtpObj.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    def sendRecipeViaEmail(self, firstName, emailUser, owner, recipe_name, recipe_id):
        msg = EmailMessage()
        msg['Subject'] = f'Brewhub: Recipe for you!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = emailUser

        username = firstName
        email = emailUser

        file_loader = FileSystemLoader('brewhub/templates')
        env = Environment(loader=file_loader)
        template = env.get_template('email_message.html')
        output = template.render(email=email, username=username, owner=owner, recipe_name=recipe_name,
                                 recipe_id=recipe_id)
        msg.add_alternative(output, subtype='html')
        self.smtpObj.send_message(msg)


m = MailService()


@recipes.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    db = DatabaseConnector()
    user_id = session['id']

    style_data = {"American Light Lager": {"IBU": [8, 12], "SRM": [2, 3], "OG": [1.028, 1.040], "FG": [0.998, 1.008],
                                           "ABV": [2.8, 4.2]},
                  "American Lager": {"IBU": [8, 19], "SRM": [2, 3.5], "OG": [1.040, 1.050], "FG": [1.004, 1.010],
                                     "ABV": [4.2, 5.3]},
                  "Cream Ale": {"IBU": [8, 20], "SRM": [2, 5], "OG": [1.042, 1.055], "FG": [1.006, 1.012],
                                "ABV": [4.2, 5.6]},
                  "American Wheat Beer": {"IBU": [15, 30], "SRM": [3, 6], "OG": [1.040, 1.055], "FG": [1.008, 1.013],
                                          "ABV": [4.0, 5.5]},
                  "International Pale Lager": {"IBU": [18, 25], "SRM": [2, 6], "OG": [1.042, 1.050],
                                               "FG": [1.008, 1.012],
                                               "ABV": [4.5, 6]}}
    # get beer style names from style_data
    styles = style_data.keys()

    # get all user fermentables from database
    fermentables = db.select_from_fermentables(user_id)
    # put fermantables into combobox in creating recipe form
    fermentables_for_combobox = []
    for i in range(len(fermentables)):
        (name, color, gravity_contibution, price) = fermentables[i]
        fermentable = str(name)
        fermentables_for_combobox.append(fermentable)

    # get all user hops from database
    hops = db.select_from_hops(user_id)
    # put hops into combobox in creating recipe form
    hops_for_combobox = []
    for i in range(len(hops)):
        (name, alpha_acids, price) = hops[i]
        hop = str(name)
        hops_for_combobox.append(hop)

    # get all others hops from database
    others = db.select_from_others(user_id)
    # put others into combobox in creating recipe form
    others_for_combobox = []
    for i in range(len(others)):
        (name, info, price) = others[i]
        other = str(name)
        others_for_combobox.append(other)

    # get all yeasts hops from database
    yeasts = db.select_from_yeasts(user_id)
    # put yeats into combobox in creating recipe form
    yeasts_for_combobox = []
    for i in range(len(yeasts)):
        (name, attenuation, price) = yeasts[i]
        # yeast = str(name) + ' ' + str(float(attenuation)) +' %'
        yeast = str(name)
        yeasts_for_combobox.append(yeast)

    data = {
        'yeasts_names': yeasts_for_combobox,
        'yeasts': yeasts,
        'fermentables_names': fermentables_for_combobox,
        'fermentables': fermentables,
        'hops_names': hops_for_combobox,
        'hops': hops,
        'others_names': others_for_combobox,
        'others': others
    }

    if request.method == 'POST':

        # get data from html form
        # date
        recipe_date = datetime.date.today()
        # recipe name
        recipe_name = request.form['recipe_name']
        # recipe style
        recipe_style = request.form.get('recipe_style')
        # recipe type
        recipe_type = request.form.get('recipe_type')
        # visibility
        visibility = request.form.get('visibility')
        # batch size
        batch_size = request.form['batch_size']
        # boiling time
        boiling_time = request.form['boiling_time']
        # evaporation
        evaporation = request.form['evaporation']
        # boiling losses
        boiling_losses = request.form['boiling_losses']
        # fermentation losses
        fermentation_losses = request.form['fermentation_losses']
        # boil size
        boil_size = request.form['boil_size']
        # wort size
        wort_size = request.form['wort_size']

        # Fermentables
        fermentables1 = request.form.getlist('fermentable')
        fermentables1 = ",".join(fermentables1)
        print(fermentables1)

        fermentables_amounts = request.form.getlist('fermentable_amount')
        fermentables_amounts = ",".join(fermentables_amounts)
        print(fermentables_amounts)

        # Hops
        hops = request.form.getlist('hop')
        hops = ",".join(hops)
        print(hops)

        hops_usages = request.form.getlist('hop_usage')
        hops_usages = ",".join(hops_usages)
        print(hops_usages)

        hops_timings = request.form.getlist('hop_time')
        hops_timings = ",".join(hops_timings)
        print(hops_timings)

        hops_amounts = request.form.getlist('hop_amount')
        hops_amounts = ",".join(hops_amounts)
        print(hops_amounts)

        # Others
        others = request.form.getlist('other')
        others = ",".join(others)
        print(others)

        others_amounts = request.form.getlist('other_amount')
        others_amounts = ",".join(others_amounts)
        print(others_amounts)

        others_infos = request.form.getlist('other_info')
        others_infos = ",".join(others_infos)
        print(others_infos)

        # Fermentation
        yeast = request.form.get('yeast')
        print(yeast)

        primary_fermentation = request.form['primary_fermentation']
        print(primary_fermentation)

        secondary_fermentation = request.form['secondary_fermentation']
        print(secondary_fermentation)

        # Mash
        efficiency = request.form['efficiency']
        print(efficiency)

        temperature_stops = request.form.getlist('mash_temperature')
        temperature_stops = ",".join(temperature_stops)
        print(temperature_stops)

        stops_timings = request.form.getlist('mash_time')
        stops_timings = ",".join(stops_timings)
        print(stops_timings)

        # Notes
        if request.form['notes'] == '':
            notes = request.form['notes']
            print(notes)
        else:
            if not re.match(r'^[A-Za-z0-9\s\.\,\!\?]+[A-Za-z0-9]$', request.form['notes']):
                flash("Incorrect input data in notes field")
            else:
                notes = request.form['notes']
                print(notes)

        # get vital statistics from html form
        og = request.form["OGvalue"]
        print(og)
        fg = request.form["FGvalue"]
        print(fg)
        ibu = request.form["IBUvalue"]
        print(ibu)
        srm = request.form["SRMvalue"]
        print(srm)
        abv = request.form["ABVvalue"]
        print(abv)

        # temporary
        price = request.form["estimatedPrice"]
        print(price)

        # add recipe in database
        db.insert_into_recipes("\'" + str(user_id) + "\'", "\'" + recipe_name + "\'", "\'" + recipe_style + "\'",
                               "\'" + recipe_type + "\'", "\'" + visibility + "\'", "\'" + str(recipe_date) + "\'",
                               "\'" + str(batch_size) + "\'",
                               "\'" + boiling_time + "\'", "\'" + evaporation + "\'",
                               "\'" + boiling_losses + "\'", "\'" + fermentation_losses + "\'", "\'" + boil_size + "\'",
                               "\'" + wort_size + "\'", "\'" + fermentables1 + "\'",
                               "\'" + fermentables_amounts + "\'",
                               "\'" + hops + "\'", "\'" + hops_usages + "\'", "\'" + hops_timings + "\'",
                               "\'" + hops_amounts + "\'", "\'" + others + "\'", "\'" + others_amounts + "\'",
                               "\'" + others_infos + "\'",
                               "\'" + yeast + "\'",
                               "\'" + primary_fermentation + "\'", "\'" + secondary_fermentation + "\'",
                               "\'" + efficiency + "\'", "\'" + temperature_stops + "\'",
                               "\'" + stops_timings + "\'",
                               "\'" + og + "\'", "\'" + fg + "\'", "\'" + ibu + "\'", "\'" + srm + "\'",
                               "\'" + abv + "\'", "\'" + notes + "\'", "\'" + price + "\'")

        flash('Recipe has been added successfully')

    return render_template('recipe_form.html', styles=styles, fermentables_for_combobox=fermentables_for_combobox,
                           hops_for_combobox=hops_for_combobox, others_for_combobox=others_for_combobox,
                           yeasts_for_combobox=yeasts_for_combobox, yeasts=yeasts, data=data, style_data=style_data)


@recipes.route('/user_recipes/<int:recipe_id>/edit', methods=['GET'])
def edit_recipe_get(recipe_id):
    db = DatabaseConnector()
    user_id = session['id']

    # select all params of recipe to edit from database
    recipe_params = db.select_from_recipes_by_id("\'" + str(recipe_id) + "\'")[0]
    print(recipe_params)

    style_data = {"American Light Lager": {"IBU": [8, 12], "SRM": [2, 3], "OG": [1.028, 1.040], "FG": [0.998, 1.008],
                                           "ABV": [2.8, 4.2]},
                  "American Lager": {"IBU": [8, 19], "SRM": [2, 3.5], "OG": [1.040, 1.050], "FG": [1.004, 1.010],
                                     "ABV": [4.2, 5.3]},
                  "Cream Ale": {"IBU": [8, 20], "SRM": [2, 5], "OG": [1.042, 1.055], "FG": [1.006, 1.012],
                                "ABV": [4.2, 5.6]},
                  "American Wheat Beer": {"IBU": [15, 30], "SRM": [3, 6], "OG": [1.040, 1.055], "FG": [1.008, 1.013],
                                          "ABV": [4.0, 5.5]},
                  "International Pale Lager": {"IBU": [18, 25], "SRM": [2, 6], "OG": [1.042, 1.050],
                                               "FG": [1.008, 1.012],
                                               "ABV": [4.5, 6]}}
    # get beer style names from style_data
    styles = style_data.keys()

    # get all user fermentables from database
    fermentables = db.select_from_fermentables(user_id)
    # put fermantables into combobox in creating recipe form
    fermentables_for_combobox = []
    for i in range(len(fermentables)):
        (name, color, gravity_contibution, price) = fermentables[i]
        fermentable = str(name)
        fermentables_for_combobox.append(fermentable)

    # get all user hops from database
    hops = db.select_from_hops(user_id)
    # put hops into combobox in creating recipe form
    hops_for_combobox = []
    for i in range(len(hops)):
        (name, alpha_acids, price) = hops[i]
        hop = str(name)
        hops_for_combobox.append(hop)

    # get all others hops from database
    others = db.select_from_others(user_id)
    # put others into combobox in creating recipe form
    others_for_combobox = []
    for i in range(len(others)):
        (name, info, price) = others[i]
        other = str(name)
        others_for_combobox.append(other)

    # get all yeasts hops from database
    yeasts = db.select_from_yeasts(user_id)
    # put yeats into combobox in creating recipe form
    yeasts_for_combobox = []
    for i in range(len(yeasts)):
        (name, attenuation, price) = yeasts[i]
        # yeast = str(name) + ' ' + str(float(attenuation)) +' %'
        yeast = str(name)
        yeasts_for_combobox.append(yeast)

    data = {
        'yeasts_names': yeasts_for_combobox,
        'yeasts': yeasts,
        'fermentables_names': fermentables_for_combobox,
        'fermentables': fermentables,
        'hops_names': hops_for_combobox,
        'hops': hops,
        'others_names': others_for_combobox,
        'others': others
    }

    return render_template('recipe_edit.html', recipe_params=recipe_params, styles=styles,
                           fermentables_for_combobox=fermentables_for_combobox,
                           hops_for_combobox=hops_for_combobox, others_for_combobox=others_for_combobox,
                           yeasts_for_combobox=yeasts_for_combobox, yeasts=yeasts, data=data, style_data=style_data)


@recipes.route('/user_recipes/<int:recipe_id>/edit', methods=['POST'])
def edit_recipe_post(recipe_id):
    db = DatabaseConnector()
    user_id = session['id']
    if request.method == 'POST':

        # get data from html form
        # date
        recipe_date = datetime.date.today()
        # recipe name
        recipe_name = request.form['recipe_name']
        # recipe style
        recipe_style = request.form.get('recipe_style')
        # recipe type
        recipe_type = request.form.get('recipe_type')
        # visibility
        visibility = request.form.get('visibility')
        # batch size
        batch_size = request.form['batch_size']
        # boiling time
        boiling_time = request.form['boiling_time']
        # evaporation
        evaporation = request.form['evaporation']
        # boiling losses
        boiling_losses = request.form['boiling_losses']
        # fermentation losses
        fermentation_losses = request.form['fermentation_losses']
        # boil size
        boil_size = request.form['boil_size']
        # wort size
        wort_size = request.form['wort_size']

        # Fermentables
        fermentables1 = request.form.getlist('fermentable')
        fermentables1 = ",".join(fermentables1)
        print(fermentables1)

        fermentables_amounts = request.form.getlist('fermentable_amount')
        fermentables_amounts = ",".join(fermentables_amounts)
        print(fermentables_amounts)

        # Hops
        hops = request.form.getlist('hop')
        hops = ",".join(hops)
        print(hops)

        hops_usages = request.form.getlist('hop_usage')
        hops_usages = ",".join(hops_usages)
        print(hops_usages)

        hops_timings = request.form.getlist('hop_time')
        hops_timings = ",".join(hops_timings)
        print(hops_timings)

        hops_amounts = request.form.getlist('hop_amount')
        hops_amounts = ",".join(hops_amounts)
        print(hops_amounts)

        # Others
        others = request.form.getlist('other')
        others = ",".join(others)
        print(others)

        others_amounts = request.form.getlist('other_amount')
        others_amounts = ",".join(others_amounts)
        print(others_amounts)

        others_infos = request.form.getlist('other_info')
        others_infos = ",".join(others_infos)
        print(others_infos)

        # Fermentation
        yeast = request.form.get('yeast')
        print(yeast)

        primary_fermentation = request.form['primary_fermentation']
        print(primary_fermentation)

        secondary_fermentation = request.form['secondary_fermentation']
        print(secondary_fermentation)

        # Mash
        efficiency = request.form['efficiency']
        print(efficiency)

        water_grain_ratio = request.form['water_grain_ratio']
        print(water_grain_ratio)

        temperature_stops = request.form.getlist('mash_temperature')
        temperature_stops = ",".join(temperature_stops)
        print(temperature_stops)

        stops_timings = request.form.getlist('mash_time')
        stops_timings = ",".join(stops_timings)
        print(stops_timings)

        # Notes
        if request.form['notes'] == '':
            notes = request.form['notes']
            print(notes)
        else:
            if not re.match(r'^[A-Za-z0-9\s\.\,\!\?]+[A-Za-z0-9]$', request.form['notes']):
                flash("Incorrect input data in notes field")
            else:
                notes = request.form['notes']
                print(notes)

        # get vital statistics from html form
        og = request.form["OGvalue"]
        print(og)
        fg = request.form["FGvalue"]
        print(fg)
        ibu = request.form["IBUvalue"]
        print(ibu)
        srm = request.form["SRMvalue"]
        print(srm)
        abv = request.form["ABVvalue"]
        print(abv)

        # temporary
        price = request.form["estimatedPrice"]
        print(price)

        # add recipe in database
        db.update_recipe("\'" + str(user_id) + "\'", "\'" + recipe_name + "\'", "\'" + recipe_style + "\'",
                         "\'" + recipe_type + "\'", "\'" + str(visibility) + "\'", "\'" + str(recipe_date) + "\'",
                         "\'" + str(batch_size) + "\'",
                         "\'" + boiling_time + "\'", "\'" + evaporation + "\'",
                         "\'" + boiling_losses + "\'", "\'" + fermentation_losses + "\'", "\'" + boil_size + "\'",
                         "\'" + wort_size + "\'", "\'" + fermentables1 + "\'",
                         "\'" + fermentables_amounts + "\'",
                         "\'" + hops + "\'", "\'" + hops_usages + "\'", "\'" + hops_timings + "\'",
                         "\'" + hops_amounts + "\'", "\'" + others + "\'", "\'" + others_amounts + "\'",
                         "\'" + others_infos + "\'",
                         "\'" + str(yeast) + "\'",
                         "\'" + primary_fermentation + "\'", "\'" + secondary_fermentation + "\'",
                         "\'" + efficiency + "\'", "\'" + temperature_stops + "\'",
                         "\'" + stops_timings + "\'",
                         "\'" + og + "\'", "\'" + fg + "\'", "\'" + ibu + "\'", "\'" + srm + "\'",
                         "\'" + abv + "\'", "\'" + notes + "\'", "\'" + price + "\'",
                         "\'" + str(recipe_id) + "\'")

        flash('Recipe has been updated successfully')

    return redirect(url_for('recipes.edit_recipe_get', recipe_id=recipe_id))


@recipes.route('/user_recipes/<int:recipe_id>/delete')
def delete_recipe(recipe_id):
    db = DatabaseConnector()
    try:
        db.delete_from_recipes("\'" + str(recipe_id) + "\'")
        flash("Recipe has been deleted")
    except Exception:
        flash("Error, your recipe cannot be deleted now")
    return redirect(url_for('recipes.show_user_recipes'))


@recipes.route('/public_recipes', methods=['GET'])
def show_recipes():
    db = DatabaseConnector()
    user_id = session['id']

    # select all public recipes from database
    public_recipes = db.select_public_recipes_from_recipes()

    # count amount of public recipes <- for pagination
    counter = len(public_recipes)

    # select all likes from database
    all_likes = db.select_all('likes')

    # select all comments from database
    all_comments = db.select_all('comments')

    return render_template('public_recipes.html', public_recipes=public_recipes, user_id=user_id, counter=counter,
                           all_likes=all_likes, all_comments=all_comments)


@recipes.route('/user_recipes', methods=['GET'])
def show_user_recipes():
    db = DatabaseConnector()
    user_id = session['id']

    # select user's recipes from database by user_id
    user_recipes = db.select_from_recipes("\'" + str(user_id) + "\'")

    # count amount of user's recipes <- for pagination
    counter = len(user_recipes)

    # select all likes and comments from database
    all_likes = db.select_all('likes')
    all_comments = db.select_all('comments')

    return render_template('user_recipes.html', user_recipes=user_recipes, user_id=user_id, counter=counter,
                           all_likes=all_likes, all_comments=all_comments)


@recipes.route('/user_recipes/<int:recipe_id>', methods=['GET', 'POST'])
def user_recipe(recipe_id):
    db = DatabaseConnector()

    # select chosen recipe from database
    chosen_recipe = db.select_from_recipes_by_id("\'" + str(recipe_id) + "\'")
    recipe_to_like_id = chosen_recipe[0][0]

    # select amount of likes for chosen recipe
    likes_amount = len(db.select_from_likes("\'" + str(recipe_id) + "\'"))

    # list of users who likes this recipe
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_id) + "\'")
    users_who_like = ''
    for i in range(len(current_likes_this_recipe)):
        users_who_like += (db.select_from_users_by_id("\'" + str(current_likes_this_recipe[i][1]) + "\'")[0][1]) + ',\n'

    # select all comments and their authors for this recipe
    comments = db.select_from_comments("\'" + str(recipe_id) + "\'")
    users_who_comment_ids = []
    for comment in comments:
        users_who_comment_ids.append(comment[1])
    users_who_comment_ids = set(users_who_comment_ids)
    users_who_comment_ids = list(users_who_comment_ids)

    users_who_comment_usernames = []
    for id in users_who_comment_ids:
        username = db.select_from_users_by_id(id)[0][1]
        users_who_comment_usernames.append(username)

    # list of users who commented this recipe
    users_who_comment = ''
    for username in users_who_comment_usernames:
        users_who_comment += (str(username) + ", \n")

    existing_users = db.select_all('users')
    existing_users_usernames = []
    for user in existing_users:
        existing_users_usernames.append(user[1])

    return render_template('user_recipe.html', chosen_recipe=chosen_recipe[0],
                           likes_amount=likes_amount, users_who_like=users_who_like,
                           comments=comments, users_who_comment=users_who_comment,
                           existing_users_usernames=json.dumps(existing_users_usernames))


@recipes.route('/user_recipe/share/<int:recipe_id>/<string:username>', methods=['POST'])
def share_user_recipe(recipe_id, username):
    db = DatabaseConnector()
    print(recipe_id)
    print(username)
    owner_id = session['id']
    owner_username = db.select_from_users_by_id("\'" + str(owner_id) + "\'")[0][1]
    receiver_email = db.select_from_users_by_username("\'" + username + "\'")[0][2]
    recipe_params = db.select_from_recipes_by_id("\'" + str(recipe_id) + "\'")[0]
    recipe_name = recipe_params[2]
    try:
        m.sendRecipeViaEmail(username, receiver_email, owner_username, recipe_name, recipe_id)
    except Exception as e:
        print("Something went wrong, maybe your email address is incorrect.")
        print("Exception: " + e)
    return ''


@recipes.route('/shared_recipe/<int:recipe_id>', methods=['GET'])
def open_shared_recipe(recipe_id):
    db = DatabaseConnector()
    shared_recipe = db.select_from_recipes_by_id("\'" + str(recipe_id) + "\'")[0]
    return render_template('shared_recipe.html', shared_recipe=shared_recipe)


@recipes.route('/public_recipes/<int:recipe_id>', methods=['GET', 'POST'])
def public_recipe(recipe_id):
    print(recipe_id)
    db = DatabaseConnector()
    chosen_recipe = db.select_from_recipes_by_id("\'" + str(recipe_id) + "\'")[0]
    likes_amount = len(db.select_from_likes("\'" + str(recipe_id) + "\'"))
    if_liked = False
    if (str(recipe_id), session['id']) in db.select_from_likes("\'" + str(recipe_id) + "\'"):
        if_liked = True

    # list of users who likes this recipe
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_id) + "\'")
    users_who_like = ''
    for i in range(len(current_likes_this_recipe)):
        users_who_like += (db.select_from_users_by_id("\'" + str(current_likes_this_recipe[i][1]) + "\'")[0][1]) + ',\n'

    comments = db.select_from_comments("\'" + str(recipe_id) + "\'")

    users_who_comment_ids = []
    for comment in comments:
        users_who_comment_ids.append(comment[1])
    users_who_comment_ids = set(users_who_comment_ids)
    users_who_comment_ids = list(users_who_comment_ids)

    users_who_comment_usernames = []
    for id in users_who_comment_ids:
        username = db.select_from_users_by_id(id)[0][1]
        users_who_comment_usernames.append(username)

    users_who_comment = ''
    for username in users_who_comment_usernames:
        users_who_comment += (str(username) + ", \n")

    return render_template('public_recipe.html', chosen_recipe=chosen_recipe,
                           likes_amount=likes_amount, if_liked=if_liked, users_who_like=users_who_like,
                           comments=comments, users_who_comment=users_who_comment)


@recipes.route('/public_recipes/<int:recipe_id>/comments', methods=['GET', 'POST'])
def add_comment(recipe_id):
    data = request.get_json(force=True)
    comment_text = data['content']
    user_id = session['id']
    db = DatabaseConnector()

    user_who_add_comment_username = db.select_from_users_by_id(user_id)[0][1]
    print(user_who_add_comment_username)

    date_created = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if not comment_text:
        print("You cannot add empty comment.")
    else:
        db.insert_into_comments("\'" + str(recipe_id) + "\'", "\'" + str(user_id) + "\'",
                                "\'" + str(user_who_add_comment_username) + "\'",
                                "\'" + str(comment_text) + "\'", "\'" + str(date_created) + "\'")

    comments = db.select_from_comments("\'" + str(recipe_id) + "\'")

    users_who_comment_ids = []
    for comment in comments:
        users_who_comment_ids.append(comment[1])
    users_who_comment_ids = set(users_who_comment_ids)
    users_who_comment_ids = list(users_who_comment_ids)

    users_who_comment_usernames = []
    for id in users_who_comment_ids:
        username = db.select_from_users_by_id(id)[0][1]
        users_who_comment_usernames.append(username)

    users_who_comment = ''
    for username in users_who_comment_usernames:
        users_who_comment += (str(username) + ", \n")
    print(users_who_comment)

    return jsonify(
        {"comments": len(comments), "users_who_comment": users_who_comment, "new_comment_content": comment_text,
         "date_created": date_created, 'user_who_add_comment': str(user_who_add_comment_username)})


@recipes.route('/public_recipes/<int:recipe_id>/comments/<string:date>', methods=['DELETE'])
def delete_comment(recipe_id, date):
    db = DatabaseConnector()
    user_id = session['id']
    db.delete_from_comments("\'" + str(user_id) + "\'", "\'" + date + "\'")

    comments = db.select_from_comments("\'" + str(recipe_id) + "\'")

    users_who_comment_ids = []
    for comment in comments:
        users_who_comment_ids.append(comment[1])
    users_who_comment_ids = set(users_who_comment_ids)
    users_who_comment_ids = list(users_who_comment_ids)

    users_who_comment_usernames = []
    for id in users_who_comment_ids:
        username = db.select_from_users_by_id(id)[0][1]
        users_who_comment_usernames.append(username)

    users_who_comment = ''
    for username in users_who_comment_usernames:
        users_who_comment += (str(username) + ", \n")

    print(users_who_comment)

    return jsonify({"comments": len(comments), "users_who_comment": users_who_comment})


@recipes.route('/public_recipes/like/<int:recipe_id>', methods=['POST'])
def like_recipe(recipe_id):
    possibility_to_like = True
    user_id = session['id']
    db = DatabaseConnector()
    recipe_to_like = db.select_from_recipes_by_id("\'" + str(recipe_id) + "\'")
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_id) + "\'")
    for like in current_likes_this_recipe:
        if like[0] == recipe_id and like[1] == user_id:
            possibility_to_like = False
    if possibility_to_like:
        db.insert_into_likes("\'" + str(recipe_id) + "\'", "\'" + str(user_id) + "\'")
        possibility_to_like = False
    else:
        db.delete_from_likes("\'" + str(recipe_id) + "\'", "\'" + str(user_id) + "\'")
        possibility_to_like = True
    # update the list of likes
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_id) + "\'")
    print(current_likes_this_recipe)
    users_who_like = ''
    for i in range(len(current_likes_this_recipe)):
        users_who_like += (db.select_from_users_by_id("\'" + str(current_likes_this_recipe[i][1]) + "\'")[0][1]) + ',\n'

    return jsonify(
        {"likes": len(current_likes_this_recipe), "liked": (not possibility_to_like), "users_who_like": users_who_like})


@recipes.route('/add_ingredients', methods=['GET', 'POST'])
def add_ingredients():
    db = DatabaseConnector()
    user_id = session['id']
    print(user_id)

    if request.method == 'POST' and 'fermentable_name' in request.form:
        fermentable_name = request.form['fermentable_name']
        print(fermentable_name)

        fermentable_color = request.form['fermentable_color']
        print(fermentable_color)

        gravity_contribution = request.form['gravity_contribution']
        print(gravity_contribution)

        fermentable_price = request.form['fermentable_price']
        print(fermentable_price)

        db.insert_into_fermentables(user_id, "\'" + fermentable_name + "\'", fermentable_color, gravity_contribution,
                                    fermentable_price)
        flash(fermentable_name + " has been added")

    if request.method == 'POST' and 'hop_name' in request.form:
        hop_name = request.form['hop_name']
        print(hop_name)

        alpha_acids = request.form['alpha_acids']
        print(alpha_acids)

        hop_price = request.form['hop_price']
        print(hop_price)

        db.insert_into_hops(user_id, "\'" + hop_name + "\'", alpha_acids, hop_price)
        flash(hop_name + " has been added")

    if request.method == 'POST' and 'yeast_name' in request.form:
        yeast_name = request.form['yeast_name']
        print(yeast_name)

        yeast_attenuation = request.form['yeast_attenuation']
        print(yeast_attenuation)

        yeast_price = request.form['yeast_price']
        print(yeast_price)

        db.insert_into_yeasts(user_id, "\'" + yeast_name + "\'", "\'" + yeast_attenuation + "\'", yeast_price)
        flash(yeast_name + " has been added")

    if request.method == 'POST' and 'other_name' in request.form:
        other_name = request.form['other_name']
        print(other_name)

        optional_info = request.form['optional_info']
        print(optional_info)

        other_price = request.form['other_price']
        print(other_price)

        db.insert_into_others(user_id, "\'" + other_name + "\'", "\'" + optional_info + "\'", other_price)
        flash(other_name + " has been added")



    return render_template('ingredients_form.html')
