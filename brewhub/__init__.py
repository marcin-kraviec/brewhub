from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import logging
import sys
from brewhub.database_connector import DatabaseConnector


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "7&Fa2sa23j"
    app.debug = True

    # Invalid URL
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('500.html'), 500

    from .views import views
    from .auth import auth
    from .recipes import recipes

    db = DatabaseConnector
    db.test()

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(recipes, url_prefix='/')

    return app
