from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import re
from brewhub.database_connector import DatabaseConnector
import os
import hashlib
import datetime

recipes = Blueprint('recipes', __name__)


@recipes.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    db = DatabaseConnector()
    user_id = session['id']
    print(user_id)

    def dupa():
        return ('dupa')

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
    styles = style_data.keys()

    fermentables = db.select_from_fermentables(user_id)
    print(fermentables)
    fermentables_for_combobox = []
    for i in range(len(fermentables)):
        (name, color, gravity_contibution, price) = fermentables[i]
        fermentable = str(name)
        fermentables_for_combobox.append(fermentable)

    hops = db.select_from_hops(user_id)
    print(hops)
    hops_for_combobox = []
    for i in range(len(hops)):
        (name, alpha_acids, price) = hops[i]
        hop = str(name)
        hops_for_combobox.append(hop)

    others = db.select_from_others(user_id)
    print(others)
    others_for_combobox = []
    for i in range(len(others)):
        (name, info, price) = others[i]
        other = str(name) + ' ' + str(info)
        others_for_combobox.append(other)

    yeasts = db.select_from_yeasts(user_id)
    print(yeasts)
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
        'hops': hops
    }

    if request.method == 'POST':

        recipe_date = datetime.date.today()
        print(recipe_date)

        # Recipe info
        user_id = session['id']
        print(user_id)

        recipe_name = request.form['recipe_name']
        print(recipe_name)

        recipe_style = request.form.get('recipe_style')
        print(recipe_style)

        recipe_type = request.form.get('recipe_type')
        print(recipe_type)

        visibility = request.form.get('visibility')
        print(visibility)

        # Batch info
        batch_size = request.form['batch_size']
        print(batch_size)

        boiling_time = request.form['boiling_time']
        print(boiling_time)

        evaporation = request.form['evaporation']
        print(evaporation)

        boiling_losses = request.form['boiling_losses']
        print(boiling_losses)

        fermentation_losses = request.form['fermentation_losses']
        print(fermentation_losses)

        boil_size = request.form['boil_size']
        print(boil_size)

        wort_size = request.form['wort_size']
        print(wort_size)

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

        # hops_time_options = request.form.getlist('time_option')
        # print(hops_time_options)

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
        price = "0"
        print(price)

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

    return render_template('recipe_form.html', styles=styles, fermentables_for_combobox=fermentables_for_combobox,
                           hops_for_combobox=hops_for_combobox, others_for_combobox=others_for_combobox,
                           yeasts_for_combobox=yeasts_for_combobox, yeasts=yeasts, data=data, style_data=style_data)


@recipes.route('/public_recipes', methods=['GET'])
def show_recipes():
    db = DatabaseConnector()
    user_id = session['id']
    public_recipes = db.select_public_recipes_from_recipes()
    counter = len(public_recipes)

    print(public_recipes)
    return render_template('public_recipes.html', public_recipes=public_recipes, user_id=user_id, counter=counter)


@recipes.route('/public_recipes/<string:recipe_name>', methods=['GET', 'POST'])
def public_recipe(recipe_name=''):
    print(recipe_name)
    db = DatabaseConnector()
    chosen_recipe = db.select_from_recipes_by_recipe_name(recipe_name)
    likes_amount = len(db.select_from_likes(chosen_recipe[0][0]))
    if_liked = False
    if (chosen_recipe[0][0], session['id']) in db.select_from_likes(chosen_recipe[0][0]):
        if_liked = True
    print(chosen_recipe)

    # list of users who likes this recipe
    recipe_to_like_id = chosen_recipe[0][0]
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_to_like_id) + "\'")
    users_who_like = ''
    for i in range(len(current_likes_this_recipe)):
        users_who_like += (db.select_from_users_by_id("\'" + str(current_likes_this_recipe[i][1]) + "\'")[0][1]) + ',\n'

    return render_template('public_recipe.html', recipe_name=recipe_name, chosen_recipe=chosen_recipe[0],
                           likes_amount=likes_amount, if_liked=if_liked, users_who_like=users_who_like)


@recipes.route('/public_recipes/like/<string:recipe_name>', methods=['POST'])
def like_recipe(recipe_name=''):
    possibility_to_like = True
    user_id = session['id']
    db = DatabaseConnector()
    recipe_to_like = db.select_from_recipes_by_recipe_name(recipe_name)
    recipe_to_like_id = recipe_to_like[0][0]
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_to_like_id) + "\'")
    for like in current_likes_this_recipe:
        if like[0] == recipe_to_like_id and like[1] == user_id:
            possibility_to_like = False
    if possibility_to_like:
        db.insert_into_likes("\'" + str(recipe_to_like_id) + "\'", "\'" + str(user_id) + "\'")
        possibility_to_like = False
    else:
        db.delete_from_likes("\'" + str(recipe_to_like_id) + "\'", "\'" + str(user_id) + "\'")
        possibility_to_like = True
    # update the list of likes
    current_likes_this_recipe = db.select_from_likes("\'" + str(recipe_to_like_id) + "\'")
    print(current_likes_this_recipe)
    users_who_like = ''
    for i in range(len(current_likes_this_recipe)):
        users_who_like += (db.select_from_users_by_id("\'" + str(current_likes_this_recipe[i][1]) + "\'")[0][1]) + ',\n'
    return jsonify({"likes": len(current_likes_this_recipe), "liked": (not possibility_to_like), "users_who_like": users_who_like})


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

    if request.method == 'POST' and 'hop_name' in request.form:
        hop_name = request.form['hop_name']
        print(hop_name)

        alpha_acids = request.form['alpha_acids']
        print(alpha_acids)

        hop_price = request.form['hop_price']
        print(hop_price)

        db.insert_into_hops(user_id, "\'" + hop_name + "\'", alpha_acids, hop_price)

    if request.method == 'POST' and 'yeast_name' in request.form:
        yeast_name = request.form['yeast_name']
        print(yeast_name)

        yeast_attenuation = request.form['yeast_attenuation']
        print(yeast_attenuation)

        yeast_price = request.form['yeast_price']
        print(yeast_price)

        db.insert_into_yeasts(user_id, "\'" + yeast_name + "\'", "\'" + yeast_attenuation + "\'", yeast_price)

    if request.method == 'POST' and 'other_name' in request.form:
        other_name = request.form['other_name']
        print(other_name)

        optional_info = request.form['optional_info']
        print(optional_info)

        other_price = request.form['other_price']
        print(other_price)

        db.insert_into_others(user_id, "\'" + other_name + "\'", "\'" + optional_info + "\'", other_price)

    return render_template('ingredients_form.html')
