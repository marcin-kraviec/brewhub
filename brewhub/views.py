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


@views.route('/beer_styles', methods=['GET', 'POST'])
def beer_styles():
    american_light_lager =      {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    american_lager =            {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    cream_ale =                 {'balance': 'balanced', 'fermentation': 'any-fermentation', 'lager': '-',       'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    american_wheat_beer =       {'balance': 'balanced', 'fermentation': 'any-fermentation', 'lager': '-',       'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'wheat-beer-family',  'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    international_pale_lager =  {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'international',  'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    international_amber_lager = {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'international',  'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    international_dark_lager =  {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'international',  'color': 'dark-color',  'family': 'dark-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    czech_pale_lager =          {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    czech_premium_pale_lager =  {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pilsner-family',     'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    czech_amber_lager =         {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    czech_dark_lager =          {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'dark-color',  'family': 'dark-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    munich_helles =             {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    festbier =                  {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    helles_bock =               {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'bock-family',        'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    german_leichtbier =         {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    kolsch =                    {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    german_helles_exportbier =  {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'pale-color',  'family': 'pale-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    german_pils =               {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'central-europe', 'color': 'pale-color',  'family': 'pilsner-family',     'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    marzen =                    {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    rauchbier =                 {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength',  'style': 'traditional-style', 'others': 'smoke'}
    dunkles_bock =              {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'bock-family',        'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    vienna_lager =              {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    altbier =                   {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    munich_dunkel =             {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'dark-color',  'family': 'dark-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    schwarzbier =               {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-',     'region': 'central-europe', 'color': 'dark-color',  'family': 'dark-lager-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    doppelbock =                {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'bock-family',        'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    eisbock =                   {'balance': '-',        'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'bock-family',        'strength': 'very-high-strength', 'style': 'traditional-style', 'others': '-'}
    baltic_porter =             {'balance': '-',        'fermentation': 'any-fermented',    'lager': 'lagered', 'feeling': '-',     'region': 'eastern-europe', 'color': 'dark-color',  'family': 'porter-family',      'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    weissbier =                 {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'wheat-beer-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    dunkles_weissbier =         {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'central-europe', 'color': 'amber-color', 'family': 'wheat-beer-family',  'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    weizenbock =                {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'central-europe', 'color': 'pale-color',  'family': 'wheat-beer-family',  'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    ordinary_bitter =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    best_bitter =               {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    strong_bitter =             {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    british_golden_ale =        {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'british-isles',  'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    australian_sparkling_ale =  {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'pacific',        'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    english_ipa =               {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'british-isles',  'color': 'pale-color',  'family': 'ipa-family',         'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    dark_mild =                 {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'dark-color',  'family': 'brown-ale-family',   'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    british_brown_ale =         {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'brown-ale-family',   'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    english_porter =            {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'dark-color',  'family': 'porter-family',      'strength': 'standard-strength',  'style': 'traditional-style', 'others': 'roasty'}
    scottish_light =            {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    scottish_heavy =            {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'session-strength',   'style': 'traditional-style', 'others': '-'}
    scottish_export =           {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    irish_red_ale =             {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    irish_stout =               {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'dark-color',  'family': 'stout-family',       'strength': 'standard-strength',  'style': 'traditional-style', 'others': 'roasty'}
    irish_extra_stout =         {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'dark-color',  'family': 'stout-family',       'strength': 'high-strength',      'style': 'traditional-style', 'others': 'roasty'}
    sweet_stout =               {'balance': 'sweet',    'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'dark-color',  'family': 'stout-family',       'strength': 'standard-strength',  'style': 'traditional-style', 'others': 'roasty'}
    oatmeal_stout =             {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'dark-color',  'family': 'stout-family',       'strength': 'standard-strength',  'style': 'traditional-style', 'others': 'roasty'}
    tropical_stout =            {'balance': 'sweet',    'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'dark-color',  'family': 'stout-family',       'strength': 'high-strength',      'style': 'traditional-style', 'others': 'roasty'}
    foreign_extra_stout =       {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'dark-color',  'family': 'stout-family',       'strength': 'high-strength',      'style': 'traditional-style', 'others': 'roasty'}
    british_strong_ale =        {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'strong-ale-family',  'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    old_ale =                   {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'strong-ale-family',  'strength': 'high-strength',      'style': 'traditional-style', 'others': 'aged'}
    wee_heavy =                 {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'british-isles',  'color': 'amber-color', 'family': 'strong-ale-family',  'strength': 'high-strength',      'style': 'traditional-style', 'others': '-'}
    english_barleywine =        {'balance': '-',        'fermentation': 'top-fermented',    'lager': '-',       'feeling': '-',     'region': 'british-isles',  'color': 'amber-color', 'family': 'strong-ale-family',  'strength': 'very-high-strength', 'style': 'traditional-style', 'others': '-'}
    blonde_ale =                {'balance': 'balanced', 'fermentation': 'any-fermented',    'lager': '-',       'feeling': '-',     'region': 'north-america',  'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    american_pale_ale =         {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family': 'pale-ale-family',    'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    american_amber_ale =        {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'amber-color', 'family': 'amber-ale-family',   'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    california_common =         {'balance': 'bitter',   'fermentation': 'bottom-fermented', 'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'amber-color', 'family': 'amber-lager-family', 'strength': 'standard-strength',  'style': 'traditional-style', 'others': '-'}
    american_brown_ale =        {'balance': 'balanced', 'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'dark-color',  'family': 'brown-ale-family',   'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    american_porter =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'dark-color',  'family': 'porter-family',      'strength': 'standard-strength',  'style': 'craft-style',       'others': '-'}
    american_stout =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'dark-color',  'family': 'stout-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': 'roasty'}
    imperial_stout =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'malty', 'region': 'north-america',  'color': 'dark-color',  'family': 'stout-family',      'strength': 'very-high-strength',  'style': 'traditional-style',       'others': 'roasty'}
    american_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family': 'ipa-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    belgian_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family':  'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    black_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'dark-color',  'family': 'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    brown_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'dark-color',  'family':  'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    brut_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family':  'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    red_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'amber-color',  'family':  'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    rye_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'amber-color',  'family': 'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    white_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family':  'specialty-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': 'spice'}
    hazy_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family': 'ipa-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    double_ipa =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'pale-color',  'family': 'ipa-family',      'strength': 'very-high-strength',  'style': 'craft-style',       'others': '-'}
    american_strong_ale =           {'balance': 'bitter',   'fermentation': 'top-fermented',    'lager': '-',       'feeling': 'hoppy', 'region': 'north-america',  'color': 'amber-color',  'family': 'strong-ale-family',      'strength': 'high-strength',  'style': 'craft-style',       'others': '-'}
    american_barleywine =           {'balance': 'bitter', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'hoppy',  'region': 'north-america', 'color': 'amber-color', 'family': 'strong-ale-family',   'strength': 'very-high-strength', 'style': 'craft-style', 'others': '-'}
    wheatwine =             {'balance': 'balanced', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'hoppy',  'region': 'north-america', 'color': 'amber-color', 'family': 'strong-ale-family',    'strength': 'very-high-strength', 'style': 'craft-style', 'others': '-'}
    berliner_weisse =           {'balance': 'sour', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-',    'region': 'central-europe', 'color': 'pale-color', 'family': 'wheat-beer-family',   'strength': 'session-strength', 'style': 'traditional-style', 'others': '-'}
    flanders_red_ale =          {'balance':  'sour', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'western-america', 'color': 'amber-color', 'family': 'sour-ale-family',     'strength': 'standard-strength', 'style': 'traditional-style', 'others': 'wood'}
    oud_bruin =             {'balance': 'sour', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'malty',  'region': 'western-europe', 'color': 'dark-color', 'family': 'sour-ale-family',    'strength': 'standard-strength', 'style': 'traditional-style', 'others': '-'}
    lambic =            {'balance': 'sour', 'fermentation': 'wild-fermented', 'lager': '-', 'feeling': '-',    'region': 'western-europe', 'color': 'pale-color', 'family': 'wheat-beer-family',  'strength': 'standard-strength', 'style': 'traditional-style', 'others': '-'}
    gueuze =            {'balance': 'sour', 'fermentation': 'wild-fermented', 'lager': '-', 'feeling': '-',    'region': 'western-europe', 'color': 'pale-color', 'family': 'wheat-beer-family',   'strength': 'high-strength', 'style': 'traditional-style', 'others': 'aged'}
    fruit_lambic =          {'balance': 'sour', 'fermentation': 'wild-fermented', 'lager': '-', 'feeling': '-',  'region': 'western-europe', 'color': 'pale-color', 'family': 'wheat-beer-family',    'strength': 'standard-strength', 'style': 'traditional-style', 'others': 'fruit'}
    gose =          {'balance': 'sour', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-',   'region': 'central-europe', 'color': 'pale-color', 'family': 'wheat-beer-family',    'strength': 'standard-strength', 'style': 'historical-style', 'others': 'spice'}
    witbier =           {'balance': '-', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-',   'region': 'western-europe', 'color': 'pale-color', 'family': 'wheat-beer-family',  'strength': 'standard-strength', 'style': 'traditional-style', 'others': 'spice'}
    belgian_pale_ale =          {'balance': 'balanced', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-',   'region': 'western-europe', 'color': 'amber-color', 'family': 'pale-ale-family', 'strength': 'standard-strength',   'style': 'traditional-style', 'others': '-'}
    biere_de_garde =            {'balance': 'bitter', 'fermentation': 'any-fermentation', 'lager': 'lagered', 'feeling': 'malty',  'region': 'western-europe', 'color': 'pale-color', 'family': 'amber-ale-family',   'strength': 'high-strength', 'style': 'traditional-style', 'others': '-'}
    belgian_blond_ale =             {'balance': 'balanced', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-',  'region': 'western-europe', 'color': 'pale-color', 'family': '-',    'strength': 'high-strength', 'style': 'traditional-style', 'others': '-'}
    saison =            {'balance': 'bitter', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'western-europe', 'color': 'pale-color', 'family': '-', 'strength': 'standard-strength', 'style': 'traditional-style', 'others': '-'}
    belgian_golden_strong_ale =             {'balance': 'bitter', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'western-europe', 'color': 'pale-color', 'family': '-', 'strength': 'very-high-strength', 'style': 'traditional-style', 'others': '-'}
    belgian_single =            {'balance': 'bitter', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'hoppy', 'region': 'western-europe', 'color': 'pale-color', 'family': '-',  'strength': 'standard-strength', 'style': 'craft-style', 'others': '-'}
    belgian_dubbel =            {'balance': '-', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'malty', 'region': 'western-america', 'color': 'amber-color', 'family': '-', 'strength': 'high-strength', 'style': 'traditional-style', 'others': '-'}
    belgian_tripel =            {'balance': 'bitter', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'western-europe', 'color': 'pale-color', 'family': 'sour-ale-family', 'strength': 'high-strength', 'style': 'traditional-style', 'others': '-'}
    belgian_dark_strong_ale =           {'balance': '-', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'malty', 'region': 'western-europe', 'color': 'amber-color', 'family': '-', 'strength': 'very-high-strength', 'style': 'traditional-style', 'others': '-'}
    kellerbier =            {'balance': 'balanced', 'fermentation': 'bottom-fermented', 'lager': 'lagered', 'feeling': '-', 'region': 'central-europe', 'color': 'pale-color', 'family': 'pale-lager-family', 'strength': 'standard-strength', 'style': 'traditional-style', 'others': '-'}
    kentucky_common =           {'balance': 'balanced', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'north-america', 'color': 'amber-color', 'family': '-', 'strength': 'standard-strength', 'style': 'historical-style', 'others': '-'}
    lichtenheiner =             {'balance': 'sour', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'central-europe', 'color': 'pale-color', 'family': 'wheat-beer-family', 'strength': 'standard-strength', 'style': 'historical-style', 'others': 'smoke'}
    london_brown_ale =          {'balance': 'sweet', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': 'malty', 'region': 'british-isles', 'color': 'dark-color', 'family': 'brown-ale-family', 'strength': 'session-strength', 'style': 'historical-style', 'others': '-'}
    piwo_grodziskie =           {'balance': 'bitter', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'central-europe', 'color': 'pale-color', 'family': 'wheat-beer-family', 'strength': 'session-strength', 'style': 'historical-style', 'others': 'smoke'}
    pre_prohibition_lager =             {'balance': 'bitter', 'fermentation': 'bottom_fermented', 'lager': 'lagered', 'feeling': 'hoppy', 'region': 'north-america', 'color': 'pale-color', 'family': 'pilsner-family', 'strength': 'standard-strength', 'style': 'historical-style', 'others': '-'}
    pre_probition_porter =          {'balance': '-', 'fermentation': 'any-fermentation', 'lager': '-', 'feeling': 'malty', 'region': 'north-america', 'color': 'dark-color', 'family': 'porter-family', 'strength': 'standard-strength', 'style': 'historical-style', 'others': '-'}
    roggenbier =            {'balance': '-', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': 'central-europe', 'color': 'amber-color', 'family': '-', 'strength': 'standard-strength', 'style': 'historical-style', 'others': '-'}
    sahti = {'balance': '-', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-',  'region': 'central-europe', 'color': 'amber-color', 'family': '-', 'strength': 'high-strength', 'style': 'historical-style', 'others': 'spice'}
    brett_beer = {'balance': '-', 'fermentation': 'wild-fermentation', 'lager': '-', 'feeling': '-', 'region': 'north-america', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': 'craft-style', 'others': '-'}
    mixed_fermentation_sour_beer = {'balance': 'sour', 'fermentation': 'wild-fermentation', 'lager': '-', 'feeling': '-', 'region': 'north-america', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': 'craft-style', 'others': '-'}
    wild_specialty_beer = {'balance': 'sour', 'fermentation': 'wild-fermentation', 'lager': '-', 'feeling': '-', 'region': 'north-america', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': 'craft_style', 'others': 'fruit'}
    straight_sour_beer = {'balance': 'sour', 'fermentation': 'top-fermented', 'lager': '-', 'feeling': '-', 'region': '-', 'color': 'pale-color', 'family': '-', 'strength': '-', 'style': '-', 'others': '-'}
    fruit_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-beer', 'strength': '-', 'style': '-', 'others': 'fruit'}
    fruit_and_spice_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'fruit'}
    specialty_fruit_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'fruit'}
    grape_ale = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'fruit'}
    spice_herb_or_vegetable_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'spice'}
    autumn_seasonal_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'spice'}
    winter_seasonal_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'spice'}
    specialty_spice_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'spice'}
    alternative_grain_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': '-'}
    alternative_sugar_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': '-'}
    classic_style_smoked_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'smoke'}
    specialty_smoked_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'smoke'}
    wood_aged_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'wood'}
    specialty_wood_aged_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': 'wood'}
    commercial_specialty_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': '-'}
    mixed_style_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': '-'}
    experimental_beer = {'balance': '-', 'fermentation': '-', 'lager': '-', 'feeling': '-', 'region': '-', 'color': '-', 'family': 'specialty-family', 'strength': '-', 'style': '-', 'others': '-'}

    styles = {'american_light_lager': american_light_lager, 'american_lager': american_lager, 'cream_ale': cream_ale, 'american_wheat_beer': american_wheat_beer, 'international_pale_lager': international_pale_lager, 'international_amber_lager': international_amber_lager, 'international_dark_lager': international_dark_lager,
    'czech_pale_lager': czech_pale_lager, 'czech_premium_pale_lager': czech_premium_pale_lager, 'czech_amber_lager': czech_amber_lager, 'czech_dark_lager': czech_dark_lager, 'munich_helles': munich_helles, 'festbier': festbier, 'helles_bock': helles_bock, 'german_leichtbier': german_leichtbier, 'kolsch': kolsch,
    'german_helles_exportbier': german_helles_exportbier, 'german_pils': german_pils, 'marzen': marzen, 'rauchbier': rauchbier, 'dunkles_bock': dunkles_bock, 'vienna_lager': vienna_lager, 'altbier': altbier, 'munich_dunkel': munich_dunkel, 'schwarzbier': schwarzbier, 'doppelbock': doppelbock, 'eisbock': eisbock,
    'baltic_porter': baltic_porter, 'weissbier': weissbier, 'dunkles_weissbier': dunkles_weissbier, 'weizenbock': weizenbock, 'ordinary_bitter': ordinary_bitter, 'best_bitter': best_bitter, 'strong_bitter': strong_bitter, 'british_golden_ale': british_golden_ale, 'australian_sparkling_ale': australian_sparkling_ale,
    'english_ipa': english_ipa, 'dark_mild': dark_mild, 'british_brown_ale': british_brown_ale, 'english_porter': english_porter, 'scottish_light': scottish_light, 'scottish_heavy': scottish_heavy, 'scottish_export': scottish_export, 'irish_red_ale': irish_red_ale, 'irish_stout': irish_stout, 'irish_extra_stout': irish_extra_stout,
    'sweet_stout': sweet_stout, 'oatmeal_stout': oatmeal_stout, 'tropical_stout': tropical_stout, 'foreign_extra_stout': foreign_extra_stout, 'british_strong_ale': british_strong_ale, 'old_ale': old_ale, 'wee_heavy': wee_heavy, 'english_barleywine': english_barleywine, 'blonde_ale': blonde_ale,
    'american_pale_ale': american_pale_ale, 'american_amber_ale': american_amber_ale, 'california_common': california_common, 'american_brown_ale': american_brown_ale, 'american_porter': american_porter, 'american_stout': american_stout, 'imperial_stout': imperial_stout, 'american_ipa': american_ipa, 'belgian_ipa': belgian_ipa,
    'black_ipa': black_ipa, 'brown_ipa': brown_ipa, 'brut_ipa': brut_ipa, 'red_ipa': red_ipa, 'rye_ipa': rye_ipa, 'white_ipa': white_ipa, 'hazy_ipa': hazy_ipa, 'double_ipa': double_ipa, 'american_strong_ale': american_strong_ale, 'american_barleywine': american_barleywine, 'wheatwine': wheatwine, 'berliner_weisse': berliner_weisse,
    'flanders_red_ale': flanders_red_ale, 'oud_bruin': oud_bruin, 'lambic': lambic, 'gueuze': gueuze, 'fruit_lambic': fruit_lambic, 'gose': gose, 'witbier': witbier, 'belgian_pale_ale': belgian_pale_ale, 'biere_de_garde': biere_de_garde, 'belgian_blond_ale': belgian_blond_ale, 'saison': saison,
    'belgian_golden_strong_ale': belgian_golden_strong_ale, 'belgian_single': belgian_single, 'belgian_dubbel': belgian_dubbel, 'belgian_tripel': belgian_tripel, 'belgian_dark_strong_ale': belgian_dark_strong_ale, 'kellerbier': kellerbier, 'kentucky_common': kentucky_common, 'lichtenheiner': lichtenheiner,
    'london_brown_ale': london_brown_ale, 'piwo_grodziskie': piwo_grodziskie, 'pre_prohibition_lager': pre_prohibition_lager, 'pre_probition_porter':pre_probition_porter, 'roggenbier': roggenbier, 'sahti': sahti, 'brett_beer': brett_beer, 'mixed_fermentation_sour_beer': mixed_fermentation_sour_beer,
    'wild_specialty_beer': wild_specialty_beer, 'straight_sour_beer': straight_sour_beer, 'fruit_beer': fruit_beer, 'fruit_and_spice_beer': fruit_and_spice_beer, 'specialty_fruit_beer': specialty_fruit_beer, 'grape_ale': grape_ale, 'spice_herb_or_vegetable_beer': spice_herb_or_vegetable_beer, 'autumn_seasonal_beer': autumn_seasonal_beer,
    'winter_seasonal_beer': winter_seasonal_beer, 'specialty_spice_beer': specialty_spice_beer, 'alternative_grain_beer': alternative_grain_beer, 'alternative_sugar_beer': alternative_sugar_beer, 'classic_style_smoked_beer': classic_style_smoked_beer, 'specialty_smoked_beer': specialty_smoked_beer, 'wood_aged_beer': wood_aged_beer,
    'specialty_wood_aged_beer': specialty_wood_aged_beer, 'commercial_specialty_beer': commercial_specialty_beer, 'mixed_style_beer': mixed_style_beer, 'experimental_beer': experimental_beer}

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
    others = request.form.getlist('others')

    # put all parameters into one dictionary
    filters = {'balance': balance, 'fermentation': fermentation, 'lager': lager, 'feeling': feeling, 'region': region, 'color': color, 'family': family, 'strength': strength, 'style': style, 'others': others}

    checks = {}
    for key in styles:
        checks[key] = False

    for key in styles:
        if (styles[key].get('balance') in filters.get('balance') or filters.get('balance') == []) \
                and (styles[key].get('fermentation') in filters.get('fermentation') or filters.get('fermentation') == []) \
                and (styles[key].get('lager') in filters.get('lager') or filters.get('lager') == []) \
                and (styles[key].get('feeling') in filters.get('feeling') or filters.get('feeling') == []) \
                and (styles[key].get('region') in filters.get('region') or filters.get('region') == []) \
                and (styles[key].get('color') in filters.get('color') or filters.get('color') == []) \
                and (styles[key].get('family') in filters.get('family') or filters.get('family') == []) \
                and (styles[key].get('strength') in filters.get('strength') or filters.get('strength') == []) \
                and (styles[key].get('style') in filters.get('style') or filters.get('style') == [])\
                and (styles[key].get('others') in filters.get('others') or filters.get('others') == []):
            checks[key] = True

    counter = 0
    for key in checks:
        if checks.get(key):
            counter += 1

    return render_template('beer_styles.html', checks=checks, counter=counter)


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
            db.update_users('users', "\'" + session['username'] + "\'", "\'" + new_username + "\'", "\'" + new_email + "\'",
                      "\'" + new_bio + "\'")

            session['username'] = new_username
            session['email'] = new_email
            session['bio'] = new_bio

            flash('The profile has been successfully updated')

    return render_template('edit_profile.html')

