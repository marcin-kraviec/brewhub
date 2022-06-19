from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import re
from brewhub.database_connector import DatabaseConnector
import os
import hashlib

recipes = Blueprint('recipes', __name__)


@recipes.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    db = DatabaseConnector()
    user_id = session['id']
    print(user_id)
    def dupa():
        return('dupa')

    style_data = {"American Light Lager": {"IBU": [8, 12], "SRM": [2, 3], "OG": [1.028, 1.040], "FG": [0.998, 1.008],
                                    "ABV": [2.8, 4.2]},
           "American Lager": {"IBU": [8, 19], "SRM": [2, 3.5], "OG": [1.040, 1.050], "FG": [1.004, 1.010],
                              "ABV": [4.2, 5.3]},
           "Cream Ale": {"IBU": [8, 20], "SRM": [2, 5], "OG": [1.042, 1.055], "FG": [1.006, 1.012], "ABV": [4.2, 5.6]},
           "American Wheat Beer": {"IBU": [15, 30], "SRM": [3, 6], "OG": [1.040, 1.055], "FG": [1.008, 1.013],
                                   "ABV": [4.0, 5.5]},
           "International Pale Lager": {"IBU": [18, 25], "SRM": [2, 6], "OG": [1.042, 1.050], "FG": [1.008, 1.012],
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
        hop = str(name) + ' AA. ' + str(float(alpha_acids)) + ' %'
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
        'fermentables': fermentables
    }



    if request.method == 'POST':

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

        #Fermentables
        fermentable = request.form.getlist('fermentable')
        print(fermentable)

        fermentable_amount = request.form.getlist('fermentable_amount')
        print(fermentable_amount)

        #Hops
        hop = request.form.getlist('hop')
        print(hop)

        hop_usage = request.form.getlist('hop_usage')
        print(hop_usage)

        time_value = request.form.getlist('time_value')
        print(time_value)

        time_option = request.form.getlist('time_option')
        print(time_option)

        hop_amount = request.form.getlist('hop_amount')
        print(hop_amount)

        #Others
        other = request.form.getlist('other')
        print(other)

        other_amount = request.form.getlist('other_amount')
        print(other_amount)

        other_info = request.form.getlist('other_info')
        print(other_info)

        #Fermentation
        yeast = request.form.get('yeast')
        print(yeast)

        primary_fermentation = request.form['primary_fermentation']
        print(primary_fermentation)

        secondary_fermentation = request.form['secondary_fermentation']
        print(secondary_fermentation)

        #Mash
        efficiency = request.form['efficiency']
        print(efficiency)

        water_grain_ratio = request.form['water_grain_ratio']
        print(water_grain_ratio)

        mash_temperature = request.form.getlist('mash_temperature')
        print(mash_temperature)

        mash_time = request.form.getlist('mash_time')
        print(mash_time)

        #Notes
        if request.form['notes'] == '':
            notes = request.form['notes']
            print(notes)
        else:
            if not re.match(r'^[A-Za-z0-9\s\.\,\!\?]+[A-Za-z0-9]$', request.form['notes']):
                flash("Incorrect input data in notes field")
            else:
                notes = request.form['notes']
                print(notes)



    return render_template('recipe_form.html', styles=styles, fermentables_for_combobox=fermentables_for_combobox, hops_for_combobox=hops_for_combobox, others_for_combobox=others_for_combobox, yeasts_for_combobox=yeasts_for_combobox, yeasts=yeasts, data=data)


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

        db.insert_into_fermentables(user_id, "\'" + fermentable_name + "\'", fermentable_color, gravity_contribution, fermentable_price)

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






