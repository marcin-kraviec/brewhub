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
                                        "ABV": [4.5, 6]},
            "International Amber Lager": {"IBU": [8, 25], "SRM": [6, 14], "OG": [1.042, 1.055], "FG": [1.008, 1.014],
                                 "ABV": [4.5, 6]},
            "International Dark Lager": {"IBU": [8, 20], "SRM": [14, 30], "OG": [1.044, 1.056], "FG": [1.008, 1.012],
                                         "ABV": [4.2, 6]},
            "Czech Pale Lager": {"IBU": [20, 35], "SRM": [3, 6], "OG": [1.028, 1.044], "FG": [1.008, 1.014],
                                 "ABV": [3, 4.1]},
            "Czech Premium Pale Lager": {"IBU": [30, 45], "SRM": [3.5, 6], "OG": [1.044, 1.060], "FG": [1.013, 1.017],
                                         "ABV": [4.2, 5.8]},
            "Czech Amber Lager": {"IBU": [20, 35], "SRM": [10, 16], "OG": [1.044, 1.060], "FG": [1.013, 1.017],
                                  "ABV": [4.4, 5.8]},
            "Czech Dark Lager": {"IBU": [18, 34], "SRM": [17, 35], "OG": [1.044, 1.060], "FG": [1.013, 1.017],
                                  "ABV": [4.4, 5.8]},
            "Munich Helles": {"IBU": [16, 22], "SRM": [3, 5], "OG": [1.044, 1.060], "FG": [1.006, 1.012],
                              "ABV": [4.7, 5.4]},
            "Festbier": {"IBU": [18, 25], "SRM": [4, 6], "OG": [1.054, 1.057], "FG": [1.010, 1.012], "ABV": [5.8, 6.3]},
            "Helles Bock": {"IBU": [23, 35], "SRM": [6, 9], "OG": [1.064, 1.072], "FG": [1.011, 1.018],
                            "ABV": [6.3, 7.4]},
            "German Leichtbier": {"IBU": [15, 28], "SRM": [1.5, 4], "OG": [1.026, 1.034], "FG": [1.006, 1.010],
                                  "ABV": [2.4, 3.6]},
            "Kölsch": {"IBU": [18, 30], "SRM": [3.5, 5], "OG": [1.044, 1.050], "FG": [1.007, 1.011], "ABV": [4.4, 5.2]},
            "German Helles Exportbier": {"IBU": [20, 30], "SRM": [4, 6], "OG": [1.050, 1.058], "FG": [1.008, 1.015],
                                         "ABV": [5, 6]},
            "German Pils": {"IBU": [22, 40], "SRM": [2, 4], "OG": [1.044, 1.060], "FG": [1.008, 1.013],
                            "ABV": [4.4, 5.2]},
            "Märzen": {"IBU": [18, 24], "SRM": [8, 17], "OG": [1.054, 1.060], "FG": [1.010, 1.014], "ABV": [5.6, 6.3]},
            "Rauchbier": {"IBU": [20, 30], "SRM": [12, 22], "OG": [1.050, 1.057], "FG": [1.012, 1.016],
                          "ABV": [4.8, 6]},
            "Dunkles Bock": {"IBU": [20, 27], "SRM": [14, 22], "OG": [1.064, 1.072], "FG": [1.013], "ABV": [6.3, 7.2]},
            "Vienna Lager": {"IBU": [18, 30], "SRM": [9, 15], "OG": [1.048, 1.055], "FG": [1.010, 1.014],
                             "ABV": [4.7, 5.5]},
            "Altbier": {"IBU": [25, 50], "SRM": [9, 17], "OG": [1.044, 1.052], "FG": [1.008, 1.014], "ABV": [4.3, 5.5]},
            "Munich Dunkel": {"IBU": [18, 28], "SRM": [17, 28], "OG": [1.048, 1.056], "FG": [1.010, 1.016],
                              "ABV": [4.5, 5.6]},
            "Schwarzbier": {"IBU": [20, 35], "SRM": [19, 30], "OG": [1.046, 1.052], "FG": [1.010, 1.016],
                            "ABV": [4.4, 5.4]},
            "Doppelbock": {"IBU": [16, 26], "SRM": [6, 25], "OG": [1.072, 1.012], "FG": [1.016, 1.024], "ABV": [7, 10]},
            "Eisbock": {"IBU": [25, 35], "SRM": [17, 30], "OG": [1.078, 1.120], "FG": [1.020, 1.035], "ABV": [9, 14]},
            "Baltic Porter": {"IBU": [20, 40], "SRM": [17, 30], "OG": [1.060, 1.090], "FG": [1.016, 1.024],
                              "ABV": [6.5, 9.5]},
            "Weissbier": {"IBU": [8, 15], "SRM": [2, 6], "OG": [1.044, 1.053], "FG": [1.008, 1.014], "ABV": [4.3, 5.6]},
            "Dunkles Weissbier": {"IBU": [10, 18], "SRM": [14, 23], "OG": [1.044, 1.057], "FG": [1.008, 1.014],
                                  "ABV": [4.3, 5.6]},
            "Weizenbock": {"IBU": [15, 30], "SRM": [6, 25], "OG": [1.064, 1.090], "FG": [1.015, 1.022],
                           "ABV": [6.5, 9]},
            "Ordinary Bitter": {"IBU": [25, 35], "SRM": [8, 14], "OG": [1.030, 1.039], "FG": [1.007, 1.011],
                                "ABV": [3.2, 3.8]},
            "Best Bitter": {"IBU": [25, 40], "SRM": [8, 16], "OG": [1.040, 1.048], "FG": [1.008, 1.012],
                            "ABV": [3.8, 4.6]},
            "Strong Bitter": {"IBU": [30, 50], "SRM": [8, 18], "OG": [1.048, 1.060], "FG": [1.010, 1.016],
                              "ABV": [4.6, 6.2]},
            "British Golden Ale": {"IBU": [20, 45], "SRM": [2, 5], "OG": [1.038, 1.053], "FG": [1.006, 1.012],
                                   "ABV": [3.8, 5]},
            "Australian Sparkling Ale": {"IBU": [20, 35], "SRM": [4, 7], "OG": [1.038], "FG": [1.050], "ABV": [4.5, 6]},

            # "English IPA": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Dark Mild": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "British Brown Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "English Porter": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Scottish Light": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Scottish Heavy": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Scottish Export": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Irish Red Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Irish Stout": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Irish Extra Stout": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Sweet Stout": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Oatmeal Stout": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Tropical Stout": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Foreign Extra Stout": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "British Strong Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Old Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Wee Heavy": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "English Barleywine": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "Blonde Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "American Pale Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "American Amber Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "California Common": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "American Brown Ale": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "American Porter": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            # "": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []}

                  }




    styles = style_data.keys()

    fermentables = db.select_from_fermentables(user_id)
    print(fermentables)
    fermentables_for_combobox = []
    for i in range(len(fermentables)):
        (name, color, gravity_contibution, price) = fermentables[i]
        fermentable = str(name) + ' ' + str(float(color)) + ' SRM'
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
        yeast = str(name) + ' ' + str(float(attenuation)) +' %'
        yeasts_for_combobox.append(yeast)


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



    return render_template('recipe_form.html', styles=styles, fermentables=fermentables_for_combobox, hops=hops_for_combobox, others=others_for_combobox, yeasts=yeasts_for_combobox)


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






