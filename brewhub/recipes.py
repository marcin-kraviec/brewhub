from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import re
from brewhub.database_connector import DatabaseConnector
import os
import hashlib

recipes = Blueprint('recipes', __name__)


@recipes.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    styles = ['American Light Lager', 'American Lager', 'Cream Ale', 'American Wheat Beer', 'International Pale Lager',
              'International Amber Lager']


    # Recipe info
    if request.method == 'POST':

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



    return render_template('recipe_form.html', styles=styles)