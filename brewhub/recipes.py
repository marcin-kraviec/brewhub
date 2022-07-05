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

            "English IPA": {"IBU": [40, 60], "SRM": [6, 14], "OG": [1.050, 1.070], "FG": [1.010, 1.015],
                            "ABV": [5, 7.5]},
            "Dark Mild": {"IBU": [10, 25], "SRM": [14, 25], "OG": [1.030, 1.038], "FG": [1.008, 1.013],
                          "ABV": [3, 3.8]},
            "British Brown Ale": {"IBU": [20, 30], "SRM": [12, 22], "OG": [1.040, 1.052], "FG": [1.008, 1.013],
                                  "ABV": [4.2, 5.9]},
            "English Porter": {"IBU": [18, 35], "SRM": [20, 30], "OG": [1.040, 1.052], "FG": [1.008, 1.014],
                               "ABV": [4, 5.4]},
            "Scottish Light": {"IBU": [10, 20], "SRM": [17, 25], "OG": [1.030, 1.035], "FG": [1.010, 1.013],
                               "ABV": [2.5, 3.3]},
            "Scottish Heavy": {"IBU": [10, 20], "SRM": [12, 20], "OG": [1.035, 1.040], "FG": [1.010, 1.015],
                               "ABV": [3.3, 3.9]},
            "Scottish Export": {"IBU": [15, 30], "SRM": [12, 20], "OG": [1.040, 1.060], "FG": [1.010, 1.016],
                                "ABV": [3.9, 6]},
            "Irish Red Ale": {"IBU": [18, 28], "SRM": [9, 14], "OG": [1.036, 1.046], "FG": [1.010, 1.014],
                              "ABV": [3.8, 5]},
            "Irish Stout": {"IBU": [25, 45], "SRM": [25, 40], "OG": [1.036, 1.044], "FG": [1.007, 1.011],
                            "ABV": [4, 4.5]},
            "Irish Extra Stout": {"IBU": [35, 50], "SRM": [30, 40], "OG": [1.052, 1.062], "FG": [1.010,1.014],
                                  "ABV": [5, 6.5]},
            "Sweet Stout": {"IBU": [20, 40], "SRM": [30, 40], "OG": [1.044, 1.060], "FG": [1.012, 1.024],
                            "ABV": [4, 6]},
            "Oatmeal Stout": {"IBU": [25, 40], "SRM": [22, 40], "OG": [1.045, 1.065], "FG": [1.010, 1.018],
                              "ABV": [4.2, 5.9]},
            "Tropical Stout": {"IBU": [30, 50], "SRM": [30, 40], "OG": [1.056, 1.075], "FG": [1.010, 1.018],
                               "ABV": [5.5, 8]},
            "Foreign Extra Stout": {"IBU": [50, 70], "SRM": [30, 40], "OG": [1.056, 1.075], "FG": [1.010, 1.018],
                                    "ABV": [6.3, 8]},
            "British Strong Ale": {"IBU": [30, 60], "SRM": [8, 22], "OG": [1.055, 1.080], "FG": [1.025, 1.022],
                                   "ABV": [5.5, 8]},
            "Old Ale": {"IBU": [30, 60], "SRM": [10, 22], "OG": [1.055, 1.088], "FG": [1.015, 1.022],
                        "ABV": [5.5, 9]},
            "Wee Heavy": {"IBU": [17, 35], "SRM": [14, 25], "OG": [1.070, 1.130], "FG": [1.018, 1.040],
                          "ABV": [6.5, 10]},
            "English Barleywine": {"IBU": [35, 70], "SRM": [8, 22], "OG": [1.080, 1.120], "FG": [1.018, 1.030],
                                   "ABV": [8, 12]},
            "Blonde Ale": {"IBU": [15, 28], "SRM": [3, 6], "OG": [1.038, 1.054], "FG": [1.008, 1.013],
                           "ABV": [3.8, 5.5]},
            "American Pale Ale": {"IBU": [30, 50], "SRM": [5, 10], "OG": [1.045, 1.060], "FG": [1.010, 1.015],
                                  "ABV": [4.5, 6.2]},
            "American Amber Ale": {"IBU": [25, 40], "SRM": [10, 17], "OG": [1.045, 1.060], "FG": [1.010, 1.015],
                                   "ABV": [4.5, 6.2]},
            "California Common": {"IBU": [30, 45], "SRM": [9, 14], "OG": [1.048, 1.054], "FG": [1.011, 1.014],
                                  "ABV": [4.5, 5.5]},
            "American Brown Ale": {"IBU": [20, 30], "SRM": [18, 35], "OG": [1.045, 1.060], "FG": [1.010, 1.016],
                                   "ABV": [4.3, 6.2]},
            "American Porter": {"IBU": [25, 50], "SRM": [22, 40], "OG": [1.050, 1.070], "FG": [1.012, 1.018],
                                "ABV": [4.8, 6.5]},
            "American Stout": {"IBU": [35, 75], "SRM": [30, 40], "OG": [1.050, 1.075], "FG": [1.010, 1.022],
                               "ABV": [5, 7]},
            "Imperial Stout": {"IBU": [50, 90], "SRM": [30, 40], "OG": [1.075, 1.115], "FG": [1.028, 1.030],
                               "ABV": [8, 12]},
            "American IPA": {"IBU": [40, 70], "SRM": [6, 14], "OG": [1.056, 1.070], "FG": [1.008, 1.014],
                             "ABV": [5.5, 7.5]},
            "Belgian IPA": {"IBU": [50, 100], "SRM": [5, 8], "OG": [1.08, 1.080], "FG": [1.008, 1.016],
                            "ABV": [6.2, 9.5]},
            "Black IPA": {"IBU": [50, 90], "SRM": [25, 40], "OG": [1.050, 1.085], "FG": [1.010, 1.018],
                          "ABV": [5.5, 9]},
            "Brown IPA": {"IBU": [40, 70], "SRM": [18, 35], "OG": [1.056, 1.070], "FG": [1.008, 1.016],
                          "ABV": [5.5, 7.5]},
            "Brut IPA": {"IBU": [20, 30], "SRM": [2, 4], "OG": [1.046, 1.057], "FG": [0.990, 1.004], "ABV": [6, 7.5]},
            "Red IPA": {"IBU": [40, 70], "SRM": [11, 17], "OG": [1.056, 1.070], "FG": [1.008, 1.016],
                        "ABV": [5.5, 7.5]},
            "Rye IPA": {"IBU": [50, 75], "SRM": [6, 14], "OG": [1.056, 1.075], "FG": [1.008, 1.014], "ABV": [5.5, 8]},
            "White IPA": {"IBU": [40, 70], "SRM": [5, 6], "OG": [1.056, 1.065], "FG": [1.010, 1.016], "ABV": [5.5, 7]},
            "Hazy IPA": {"IBU": [25, 60], "SRM": [3, 7], "OG": [1.060, 1.085], "FG": [1.010, 1.015], "ABV": [6, 9]},
            "Double IPA": {"IBU": [60, 100], "SRM": [6, 14], "OG": [1.065, 1.085], "FG": [1.008, 1.018],
                           "ABV": [7.5, 10]},
            "American Strong Ale": {"IBU": [50, 100], "SRM": [7, 18], "OG": [1.062, 1.090], "FG": [1.014, 1.024],
                                    "ABV": [6.3, 10]},
            "American Barleywine": {"IBU": [50, 100], "SRM": [9, 18], "OG": [1.080, 1.120], "FG": [1.016, 1.030],
                                    "ABV": [8, 12]},
            "Wheatwine": {"IBU": [30, 60], "SRM": [6, 14], "OG": [1.080, 1.120], "FG": [1.016, 1.030],
                          "ABV": [8, 12]},
            "Berliner Weisse": {"IBU": [3, 8], "SRM": [2, 3], "OG": [1.028, 1.032], "FG": [1.003, 1.006],
                                "ABV": [2.8, 3.8]},
            "Flanders Red Ale": {"IBU": [10, 25], "SRM": [10, 17], "OG": [1.048, 1.057], "FG": [1.002, 1.012],
                                 "ABV": [4.6, 6.5]},
            "Oud Bruin": {"IBU": [20, 25], "SRM": [17, 22], "OG": [1.040, 1.074], "FG": [1.008, 1.012],
                          "ABV": [4, 8]},
            "Lambic": {"IBU": [0, 10], "SRM": [3, 6], "OG": [1.040, 1.054], "FG": [1.001, 1.010], "ABV": [5, 6.5]},
            "Gueuze": {"IBU": [0, 10], "SRM": [5, 6], "OG": [1.040, 1.054], "FG": [1.000, 1.006], "ABV": [5, 8]},
            "Fruit Lambic": {"IBU": [0, 10], "SRM": [3, 7], "OG": [1.040, 1.060], "FG": [1.000, 1.010], "ABV": [5, 7]},
            "Gose": {"IBU": [5, 12], "SRM": [3, 4], "OG": [1.036, 1.056], "FG": [1.006, 1.010], "ABV": [4.2, 4.8]},
            "Witbier": {"IBU": [8, 20], "SRM": [2, 4], "OG": [1.044, 1.052], "FG": [1.008, 1.012], "ABV": [4.5, 5.5]},
            "Belgian Pale Ale": {"IBU": [20, 30], "SRM": [8, 14], "OG": [1.048, 1.054], "FG": [1.010, 1.014],
                                 "ABV": [4.8, 5.5]},
            "Bière de Garde": {"IBU": [18, 28], "SRM": [6, 19], "OG": [1.060, 1.080], "FG": [1.008, 1.016],
                               "ABV": [6, 8.5]},
            "Belgian Blond Ale": {"IBU": [15, 30], "SRM": [4, 6], "OG": [1.062, 1.075], "FG": [1.008, 1.018],
                                  "ABV": [6, 7.5]},
            "Saison": {"IBU": [20, 35], "SRM": [5, 14], "OG": [1.048, 1.065], "FG": [1.002, 1.008],
                       "ABV": [5, 7]},
            "Belgian Golden Strong Ale": {"IBU": [22, 35], "SRM": [3, 6], "OG": [1.070, 1.095], "FG": [1.005, 1.016],
                                          "ABV": [7.5, 10.5]},
            "Belgian Single": {"IBU": [25, 45], "SRM": [3, 5], "OG": [1.044, 1.054], "FG": [1.004, 1.010],
                               "ABV": [4.8, 6]},
            "Belgian Dubbel": {"IBU": [15, 25], "SRM": [10, 17], "OG": [1.062, 1.075], "FG": [1.008, 1.018],
                               "ABV": [6, 7.6]},
            "Belgian Tripel": {"IBU": [20, 40], "SRM": [4.5, 7], "OG": [1.075, 1.085], "FG": [1.008, 1.014],
                               "ABV": [7.5, 9.5]},
            "Belgian Dark Strong Ale": {"IBU": [20, 35], "SRM": [12, 22], "OG": [1.075, 1.110], "FG": [1.010, 1.024],
                                        "ABV": [8, 12]},
            "Kellerbier": {"IBU": [20, 35], "SRM": [3, 7], "OG": [1.045, 1.051], "FG": [1.008, 1.012],
                           "ABV": [4.7, 5.4]},
            "Kentucky Common": {"IBU": [15, 30], "SRM": [11, 20], "OG": [1.044, 1.055], "FG": [1.010, 1.018],
                                "ABV": [4, 5.5]},
            "Lichtenhainer": {"IBU": [5, 12], "SRM": [3, 6], "OG": [1.032, 1.040], "FG": [1.004, 1.008],
                              "ABV": [3.5, 4.7]},
            "London Brown Ale": {"IBU": [15, 20], "SRM": [22, 35], "OG": [1.033, 1.038], "FG": [1.012, 1.015],
                                 "ABV": [2.8, 3.6]},
            "Piwo Grodziskie": {"IBU": [20, 35], "SRM": [3, 6], "OG": [1.028, 1.032], "FG": [1.006, 1.012],
                                "ABV": [2.5, 3.3]},
            "Pre-Prohibition Lager": {"IBU": [25, 40], "SRM": [3, 6], "OG": [1.044, 1.060], "FG": [1.010, 1.015],
                                      "ABV": [4.5, 6]},
            "Pre-Prohibition Porter": {"IBU": [20, 30], "SRM": [20, 30], "OG": [1.046, 1.016], "FG": [1.010, 1.016],
                                       "ABV": [4.5, 6]},
            "Roggenbier": {"IBU": [10, 20], "SRM": [14, 19], "OG": [1.046, 1.056], "FG": [1.010, 1.014],
                           "ABV": [4.5, 6]},
            "Sahti": {"IBU": [0, 15], "SRM": [4, 22], "OG": [1.076, 1.120], "FG": [1.016, 1.038], "ABV": [7, 11]},
            "Brett Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Mixed-Fermentation Sour Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Wild Specialty Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Straight Sour Beer": {"IBU": [3, 8], "SRM": [2, 3], "OG": [1.048, 1.065], "FG": [1.006, 1.013],
                                   "ABV": [4.5, 7]},
            "Fruit Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Fruit and Spice Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Specialty Fruit Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Grape Ale": {"IBU": [10, 30], "SRM": [4, 8], "OG": [1.059, 1.075], "FG": [1.004, 1.013], "ABV": [6, 8.5]},
            "Spiced Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Spice, Herb, or Vegetable Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Autumn Seasonal Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Winter Seasonal Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Specialty Spice Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Alternative Grain Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Alternative Sugar Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Classic Style Smoked Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Specialty Smoked Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Wood-Aged Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Specialty Wood-Aged Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Commercial Specialty Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Mixed-Style Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
            "Experimental Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []}}


    styles = style_data.keys()

    # get all user fermentables from database
    fermentables = db.select_from_fermentables(user_id)
    # put fermantables into combobox in creating recipe form
    fermentables_for_combobox = []
    for i in range(len(fermentables)):
        (name, color, gravity_contibution, price, id) = fermentables[i]
        fermentable = str(name)
        fermentables_for_combobox.append(fermentable)

    # get all user hops from database
    hops = db.select_from_hops(user_id)
    # put hops into combobox in creating recipe form
    hops_for_combobox = []
    for i in range(len(hops)):
        (name, alpha_acids, price, id) = hops[i]
        hop = str(name)
        hops_for_combobox.append(hop)

    # get all others hops from database
    others = db.select_from_others(user_id)
    # put others into combobox in creating recipe form
    others_for_combobox = []
    for i in range(len(others)):
        (name, info, price, id) = others[i]
        other = str(name)
        others_for_combobox.append(other)
    print(others)

    # get all yeasts hops from database
    yeasts = db.select_from_yeasts(user_id)
    # put yeats into combobox in creating recipe form
    yeasts_for_combobox = []
    for i in range(len(yeasts)):
        (name, attenuation, price, id) = yeasts[i]
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

        all_recipes = db.select_all('recipes')
        possibility_to_create_recipe = True
        for r in all_recipes:
            if recipe_name == r[2]:
                possibility_to_create_recipe = False

        # add recipe in database
        if possibility_to_create_recipe:
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
        else:
            flash('Recipe with this name already exists')

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
                                               "ABV": [4.5, 6]},
                  "Czech Premium Pale Lager": {"IBU": [30, 45], "SRM": [3.5, 6], "OG": [1.044, 1.060],
                                               "FG": [1.013, 1.017],
                                               "ABV": [4.2, 5.8]},
                  "Czech Amber Lager": {"IBU": [20, 35], "SRM": [10, 16], "OG": [1.044, 1.060], "FG": [1.013, 1.017],
                                        "ABV": [4.4, 5.8]},
                  "Czech Dark Lager": {"IBU": [18, 34], "SRM": [17, 35], "OG": [1.044, 1.060], "FG": [1.013, 1.017],
                                       "ABV": [4.4, 5.8]},
                  "Munich Helles": {"IBU": [16, 22], "SRM": [3, 5], "OG": [1.044, 1.060], "FG": [1.006, 1.012],
                                    "ABV": [4.7, 5.4]},
                  "Festbier": {"IBU": [18, 25], "SRM": [4, 6], "OG": [1.054, 1.057], "FG": [1.010, 1.012],
                               "ABV": [5.8, 6.3]},
                  "Helles Bock": {"IBU": [23, 35], "SRM": [6, 9], "OG": [1.064, 1.072], "FG": [1.011, 1.018],
                                  "ABV": [6.3, 7.4]},
                  "German Leichtbier": {"IBU": [15, 28], "SRM": [1.5, 4], "OG": [1.026, 1.034], "FG": [1.006, 1.010],
                                        "ABV": [2.4, 3.6]},
                  "Kölsch": {"IBU": [18, 30], "SRM": [3.5, 5], "OG": [1.044, 1.050], "FG": [1.007, 1.011],
                             "ABV": [4.4, 5.2]},
                  "German Helles Exportbier": {"IBU": [20, 30], "SRM": [4, 6], "OG": [1.050, 1.058],
                                               "FG": [1.008, 1.015],
                                               "ABV": [5, 6]},
                  "German Pils": {"IBU": [22, 40], "SRM": [2, 4], "OG": [1.044, 1.060], "FG": [1.008, 1.013],
                                  "ABV": [4.4, 5.2]},
                  "Märzen": {"IBU": [18, 24], "SRM": [8, 17], "OG": [1.054, 1.060], "FG": [1.010, 1.014],
                             "ABV": [5.6, 6.3]},
                  "Rauchbier": {"IBU": [20, 30], "SRM": [12, 22], "OG": [1.050, 1.057], "FG": [1.012, 1.016],
                                "ABV": [4.8, 6]},
                  "Dunkles Bock": {"IBU": [20, 27], "SRM": [14, 22], "OG": [1.064, 1.072], "FG": [1.013],
                                   "ABV": [6.3, 7.2]},
                  "Vienna Lager": {"IBU": [18, 30], "SRM": [9, 15], "OG": [1.048, 1.055], "FG": [1.010, 1.014],
                                   "ABV": [4.7, 5.5]},
                  "Altbier": {"IBU": [25, 50], "SRM": [9, 17], "OG": [1.044, 1.052], "FG": [1.008, 1.014],
                              "ABV": [4.3, 5.5]},
                  "Munich Dunkel": {"IBU": [18, 28], "SRM": [17, 28], "OG": [1.048, 1.056], "FG": [1.010, 1.016],
                                    "ABV": [4.5, 5.6]},
                  "Schwarzbier": {"IBU": [20, 35], "SRM": [19, 30], "OG": [1.046, 1.052], "FG": [1.010, 1.016],
                                  "ABV": [4.4, 5.4]},
                  "Doppelbock": {"IBU": [16, 26], "SRM": [6, 25], "OG": [1.072, 1.012], "FG": [1.016, 1.024],
                                 "ABV": [7, 10]},
                  "Eisbock": {"IBU": [25, 35], "SRM": [17, 30], "OG": [1.078, 1.120], "FG": [1.020, 1.035],
                              "ABV": [9, 14]},
                  "Baltic Porter": {"IBU": [20, 40], "SRM": [17, 30], "OG": [1.060, 1.090], "FG": [1.016, 1.024],
                                    "ABV": [6.5, 9.5]},
                  "Weissbier": {"IBU": [8, 15], "SRM": [2, 6], "OG": [1.044, 1.053], "FG": [1.008, 1.014],
                                "ABV": [4.3, 5.6]},
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
                  "Australian Sparkling Ale": {"IBU": [20, 35], "SRM": [4, 7], "OG": [1.038], "FG": [1.050],
                                               "ABV": [4.5, 6]},
                  "English IPA": {"IBU": [40, 60], "SRM": [6, 14], "OG": [1.050, 1.070], "FG": [1.010, 1.015],
                                  "ABV": [5, 7.5]},
                  "Dark Mild": {"IBU": [10, 25], "SRM": [14, 25], "OG": [1.030, 1.038], "FG": [1.008, 1.013],
                                "ABV": [3, 3.8]},
                  "British Brown Ale": {"IBU": [20, 30], "SRM": [12, 22], "OG": [1.040, 1.052], "FG": [1.008, 1.013],
                                        "ABV": [4.2, 5.9]},
                  "English Porter": {"IBU": [18, 35], "SRM": [20, 30], "OG": [1.040, 1.052], "FG": [1.008, 1.014],
                                     "ABV": [4, 5.4]},
                  "Scottish Light": {"IBU": [10, 20], "SRM": [17, 25], "OG": [1.030, 1.035], "FG": [1.010, 1.013],
                                     "ABV": [2.5, 3.3]},
                  "Scottish Heavy": {"IBU": [10, 20], "SRM": [12, 20], "OG": [1.035, 1.040], "FG": [1.010, 1.015],
                                     "ABV": [3.3, 3.9]},
                  "Scottish Export": {"IBU": [15, 30], "SRM": [12, 20], "OG": [1.040, 1.060], "FG": [1.010, 1.016],
                                      "ABV": [3.9, 6]},
                  "Irish Red Ale": {"IBU": [18, 28], "SRM": [9, 14], "OG": [1.036, 1.046], "FG": [1.010, 1.014],
                                    "ABV": [3.8, 5]},
                  "Irish Stout": {"IBU": [25, 45], "SRM": [25, 40], "OG": [1.036, 1.044], "FG": [1.007, 1.011],
                                  "ABV": [4, 4.5]},
                  "Irish Extra Stout": {"IBU": [35, 50], "SRM": [30, 40], "OG": [1.052, 1.062], "FG": [1.010, 1.014],
                                        "ABV": [5, 6.5]},
                  "Sweet Stout": {"IBU": [20, 40], "SRM": [30, 40], "OG": [1.044, 1.060], "FG": [1.012, 1.024],
                                  "ABV": [4, 6]},
                  "Oatmeal Stout": {"IBU": [25, 40], "SRM": [22, 40], "OG": [1.045, 1.065], "FG": [1.010, 1.018],
                                    "ABV": [4.2, 5.9]},
                  "Tropical Stout": {"IBU": [30, 50], "SRM": [30, 40], "OG": [1.056, 1.075], "FG": [1.010, 1.018],
                                     "ABV": [5.5, 8]},
                  "Foreign Extra Stout": {"IBU": [50, 70], "SRM": [30, 40], "OG": [1.056, 1.075], "FG": [1.010, 1.018],
                                          "ABV": [6.3, 8]},
                  "British Strong Ale": {"IBU": [30, 60], "SRM": [8, 22], "OG": [1.055, 1.080], "FG": [1.025, 1.022],
                                         "ABV": [5.5, 8]},
                  "Old Ale": {"IBU": [30, 60], "SRM": [10, 22], "OG": [1.055, 1.088], "FG": [1.015, 1.022],
                              "ABV": [5.5, 9]},
                  "Wee Heavy": {"IBU": [17, 35], "SRM": [14, 25], "OG": [1.070, 1.130], "FG": [1.018, 1.040],
                                "ABV": [6.5, 10]},
                  "English Barleywine": {"IBU": [35, 70], "SRM": [8, 22], "OG": [1.080, 1.120], "FG": [1.018, 1.030],
                                         "ABV": [8, 12]},
                  "Blonde Ale": {"IBU": [15, 28], "SRM": [3, 6], "OG": [1.038, 1.054], "FG": [1.008, 1.013],
                                 "ABV": [3.8, 5.5]},
                  "American Pale Ale": {"IBU": [30, 50], "SRM": [5, 10], "OG": [1.045, 1.060], "FG": [1.010, 1.015],
                                        "ABV": [4.5, 6.2]},
                  "American Amber Ale": {"IBU": [25, 40], "SRM": [10, 17], "OG": [1.045, 1.060], "FG": [1.010, 1.015],
                                         "ABV": [4.5, 6.2]},
                  "California Common": {"IBU": [30, 45], "SRM": [9, 14], "OG": [1.048, 1.054], "FG": [1.011, 1.014],
                                        "ABV": [4.5, 5.5]},
                  "American Brown Ale": {"IBU": [20, 30], "SRM": [18, 35], "OG": [1.045, 1.060], "FG": [1.010, 1.016],
                                         "ABV": [4.3, 6.2]},
                  "American Porter": {"IBU": [25, 50], "SRM": [22, 40], "OG": [1.050, 1.070], "FG": [1.012, 1.018],
                                      "ABV": [4.8, 6.5]},
                  "American Stout": {"IBU": [35, 75], "SRM": [30, 40], "OG": [1.050, 1.075], "FG": [1.010, 1.022],
                                     "ABV": [5, 7]},
                  "Imperial Stout": {"IBU": [50, 90], "SRM": [30, 40], "OG": [1.075, 1.115], "FG": [1.028, 1.030],
                                     "ABV": [8, 12]},
                  "American IPA": {"IBU": [40, 70], "SRM": [6, 14], "OG": [1.056, 1.070], "FG": [1.008, 1.014],
                                   "ABV": [5.5, 7.5]},
                  "Belgian IPA": {"IBU": [50, 100], "SRM": [5, 8], "OG": [1.08, 1.080], "FG": [1.008, 1.016],
                                  "ABV": [6.2, 9.5]},
                  "Black IPA": {"IBU": [50, 90], "SRM": [25, 40], "OG": [1.050, 1.085], "FG": [1.010, 1.018],
                                "ABV": [5.5, 9]},
                  "Brown IPA": {"IBU": [40, 70], "SRM": [18, 35], "OG": [1.056, 1.070], "FG": [1.008, 1.016],
                                "ABV": [5.5, 7.5]},
                  "Brut IPA": {"IBU": [20, 30], "SRM": [2, 4], "OG": [1.046, 1.057], "FG": [0.990, 1.004],
                               "ABV": [6, 7.5]},
                  "Red IPA": {"IBU": [40, 70], "SRM": [11, 17], "OG": [1.056, 1.070], "FG": [1.008, 1.016],
                              "ABV": [5.5, 7.5]},
                  "Rye IPA": {"IBU": [50, 75], "SRM": [6, 14], "OG": [1.056, 1.075], "FG": [1.008, 1.014],
                              "ABV": [5.5, 8]},
                  "White IPA": {"IBU": [40, 70], "SRM": [5, 6], "OG": [1.056, 1.065], "FG": [1.010, 1.016],
                                "ABV": [5.5, 7]},
                  "Hazy IPA": {"IBU": [25, 60], "SRM": [3, 7], "OG": [1.060, 1.085], "FG": [1.010, 1.015],
                               "ABV": [6, 9]},
                  "Double IPA": {"IBU": [60, 100], "SRM": [6, 14], "OG": [1.065, 1.085], "FG": [1.008, 1.018],
                                 "ABV": [7.5, 10]},
                  "American Strong Ale": {"IBU": [50, 100], "SRM": [7, 18], "OG": [1.062, 1.090], "FG": [1.014, 1.024],
                                          "ABV": [6.3, 10]},
                  "American Barleywine": {"IBU": [50, 100], "SRM": [9, 18], "OG": [1.080, 1.120], "FG": [1.016, 1.030],
                                          "ABV": [8, 12]},
                  "Wheatwine": {"IBU": [30, 60], "SRM": [6, 14], "OG": [1.080, 1.120], "FG": [1.016, 1.030],
                                "ABV": [8, 12]},
                  "Berliner Weisse": {"IBU": [3, 8], "SRM": [2, 3], "OG": [1.028, 1.032], "FG": [1.003, 1.006],
                                      "ABV": [2.8, 3.8]},
                  "Flanders Red Ale": {"IBU": [10, 25], "SRM": [10, 17], "OG": [1.048, 1.057], "FG": [1.002, 1.012],
                                       "ABV": [4.6, 6.5]},
                  "Oud Bruin": {"IBU": [20, 25], "SRM": [17, 22], "OG": [1.040, 1.074], "FG": [1.008, 1.012],
                                "ABV": [4, 8]},
                  "Lambic": {"IBU": [0, 10], "SRM": [3, 6], "OG": [1.040, 1.054], "FG": [1.001, 1.010],
                             "ABV": [5, 6.5]},
                  "Gueuze": {"IBU": [0, 10], "SRM": [5, 6], "OG": [1.040, 1.054], "FG": [1.000, 1.006], "ABV": [5, 8]},
                  "Fruit Lambic": {"IBU": [0, 10], "SRM": [3, 7], "OG": [1.040, 1.060], "FG": [1.000, 1.010],
                                   "ABV": [5, 7]},
                  "Gose": {"IBU": [5, 12], "SRM": [3, 4], "OG": [1.036, 1.056], "FG": [1.006, 1.010],
                           "ABV": [4.2, 4.8]},
                  "Witbier": {"IBU": [8, 20], "SRM": [2, 4], "OG": [1.044, 1.052], "FG": [1.008, 1.012],
                              "ABV": [4.5, 5.5]},
                  "Belgian Pale Ale": {"IBU": [20, 30], "SRM": [8, 14], "OG": [1.048, 1.054], "FG": [1.010, 1.014],
                                       "ABV": [4.8, 5.5]},
                  "Bière de Garde": {"IBU": [18, 28], "SRM": [6, 19], "OG": [1.060, 1.080], "FG": [1.008, 1.016],
                                     "ABV": [6, 8.5]},
                  "Belgian Blond Ale": {"IBU": [15, 30], "SRM": [4, 6], "OG": [1.062, 1.075], "FG": [1.008, 1.018],
                                        "ABV": [6, 7.5]},
                  "Saison": {"IBU": [20, 35], "SRM": [5, 14], "OG": [1.048, 1.065], "FG": [1.002, 1.008],
                             "ABV": [5, 7]},
                  "Belgian Golden Strong Ale": {"IBU": [22, 35], "SRM": [3, 6], "OG": [1.070, 1.095],
                                                "FG": [1.005, 1.016],
                                                "ABV": [7.5, 10.5]},
                  "Belgian Single": {"IBU": [25, 45], "SRM": [3, 5], "OG": [1.044, 1.054], "FG": [1.004, 1.010],
                                     "ABV": [4.8, 6]},
                  "Belgian Dubbel": {"IBU": [15, 25], "SRM": [10, 17], "OG": [1.062, 1.075], "FG": [1.008, 1.018],
                                     "ABV": [6, 7.6]},
                  "Belgian Tripel": {"IBU": [20, 40], "SRM": [4.5, 7], "OG": [1.075, 1.085], "FG": [1.008, 1.014],
                                     "ABV": [7.5, 9.5]},
                  "Belgian Dark Strong Ale": {"IBU": [20, 35], "SRM": [12, 22], "OG": [1.075, 1.110],
                                              "FG": [1.010, 1.024],
                                              "ABV": [8, 12]},
                  "Kellerbier": {"IBU": [20, 35], "SRM": [3, 7], "OG": [1.045, 1.051], "FG": [1.008, 1.012],
                                 "ABV": [4.7, 5.4]},
                  "Kentucky Common": {"IBU": [15, 30], "SRM": [11, 20], "OG": [1.044, 1.055], "FG": [1.010, 1.018],
                                      "ABV": [4, 5.5]},
                  "Lichtenhainer": {"IBU": [5, 12], "SRM": [3, 6], "OG": [1.032, 1.040], "FG": [1.004, 1.008],
                                    "ABV": [3.5, 4.7]},
                  "London Brown Ale": {"IBU": [15, 20], "SRM": [22, 35], "OG": [1.033, 1.038], "FG": [1.012, 1.015],
                                       "ABV": [2.8, 3.6]},
                  "Piwo Grodziskie": {"IBU": [20, 35], "SRM": [3, 6], "OG": [1.028, 1.032], "FG": [1.006, 1.012],
                                      "ABV": [2.5, 3.3]},
                  "Pre-Prohibition Lager": {"IBU": [25, 40], "SRM": [3, 6], "OG": [1.044, 1.060], "FG": [1.010, 1.015],
                                            "ABV": [4.5, 6]},
                  "Pre-Prohibition Porter": {"IBU": [20, 30], "SRM": [20, 30], "OG": [1.046, 1.016],
                                             "FG": [1.010, 1.016],
                                             "ABV": [4.5, 6]},
                  "Roggenbier": {"IBU": [10, 20], "SRM": [14, 19], "OG": [1.046, 1.056], "FG": [1.010, 1.014],
                                 "ABV": [4.5, 6]},
                  "Sahti": {"IBU": [0, 15], "SRM": [4, 22], "OG": [1.076, 1.120], "FG": [1.016, 1.038], "ABV": [7, 11]},
                  "Brett Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Mixed-Fermentation Sour Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Wild Specialty Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Straight Sour Beer": {"IBU": [3, 8], "SRM": [2, 3], "OG": [1.048, 1.065], "FG": [1.006, 1.013],
                                         "ABV": [4.5, 7]},
                  "Fruit Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Fruit and Spice Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Specialty Fruit Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Grape Ale": {"IBU": [10, 30], "SRM": [4, 8], "OG": [1.059, 1.075], "FG": [1.004, 1.013],
                                "ABV": [6, 8.5]},
                  "Spiced Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Spice, Herb, or Vegetable Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Autumn Seasonal Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Winter Seasonal Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Specialty Spice Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Alternative Grain Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Alternative Sugar Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Classic Style Smoked Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Specialty Smoked Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Wood-Aged Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Specialty Wood-Aged Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Commercial Specialty Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Mixed-Style Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []},
                  "Experimental Beer": {"IBU": [], "SRM": [], "OG": [], "FG": [], "ABV": []}}


    # get beer style names from style_data
    styles = style_data.keys()

    # get all user fermentables from database
    fermentables = db.select_from_fermentables(user_id)
    # put fermantables into combobox in creating recipe form
    fermentables_for_combobox = []
    for i in range(len(fermentables)):
        (name, color, gravity_contibution, price, id) = fermentables[i]
        fermentable = str(name)
        fermentables_for_combobox.append(fermentable)

    # get all user hops from database
    hops = db.select_from_hops(user_id)
    # put hops into combobox in creating recipe form
    hops_for_combobox = []
    for i in range(len(hops)):
        (name, alpha_acids, price, id) = hops[i]
        hop = str(name)
        hops_for_combobox.append(hop)

    # get all others hops from database
    others = db.select_from_others(user_id)
    # put others into combobox in creating recipe form
    others_for_combobox = []
    for i in range(len(others)):
        (name, info, price, id) = others[i]
        other = str(name)
        others_for_combobox.append(other)

    # get all yeasts hops from database
    yeasts = db.select_from_yeasts(user_id)
    # put yeats into combobox in creating recipe form
    yeasts_for_combobox = []
    for i in range(len(yeasts)):
        (name, attenuation, price, id) = yeasts[i]
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
    author = db.select_from_users_by_id("\'" + str(chosen_recipe[1]) + "\'")[0][1]

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
                           comments=comments, users_who_comment=users_who_comment, author=author)


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


@recipes.route('/add_ingredients', methods=['POST'])
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

        possibility_to_add_fermentable = True
        current_fermentables = db.select_from_fermentables("\'" + str(user_id) + "\'")
        for fermentable in current_fermentables:
            if fermentable_name == fermentable[0]:
                possibility_to_add_fermentable = False

        if possibility_to_add_fermentable:
            db.insert_into_fermentables(user_id, "\'" + fermentable_name + "\'", fermentable_color,
                                        gravity_contribution,
                                        fermentable_price)
            flash(fermentable_name + " has been added")
        else:
            flash("You already have ingredient with this name")

    if request.method == 'POST' and 'hop_name' in request.form:
        hop_name = request.form['hop_name']
        print(hop_name)

        alpha_acids = request.form['alpha_acids']
        print(alpha_acids)

        hop_price = request.form['hop_price']
        print(hop_price)

        possibility_to_add_hop = True
        current_hops = db.select_from_hops("\'" + str(user_id) + "\'")
        for hop in current_hops:
            if hop_name == hop[0]:
                possibility_to_add_hop = False

        if possibility_to_add_hop:
            db.insert_into_hops(user_id, "\'" + hop_name + "\'", alpha_acids, hop_price)
            flash(hop_name + " has been added")
        else:
            flash("You already have ingredient with this name")

    if request.method == 'POST' and 'yeast_name' in request.form:
        yeast_name = request.form['yeast_name']
        print(yeast_name)

        yeast_attenuation = request.form['yeast_attenuation']
        print(yeast_attenuation)

        yeast_price = request.form['yeast_price']
        print(yeast_price)

        possibility_to_add_yeast = True
        current_yeasts = db.select_from_yeasts("\'" + str(user_id) + "\'")
        for yeast in current_yeasts:
            if yeast_name == yeast[0]:
                possibility_to_add_yeast = False

        if possibility_to_add_yeast:
            db.insert_into_yeasts(user_id, "\'" + yeast_name + "\'", "\'" + yeast_attenuation + "\'", yeast_price)
            flash(yeast_name + " has been added")
        else:
            flash("You already have ingredient with this name")

    if request.method == 'POST' and 'other_name' in request.form:
        other_name = request.form['other_name']
        print(other_name)

        optional_info = request.form['optional_info']
        print(optional_info)

        other_price = request.form['other_price']
        print(other_price)

        possibility_to_add_other = True
        current_others = db.select_from_others("\'" + str(user_id) + "\'")
        for other in current_others:
            print(other)
            if other_name == other[0]:
                possibility_to_add_other = False

        if possibility_to_add_other:
            db.insert_into_others(user_id, "\'" + other_name + "\'", "\'" + optional_info + "\'", other_price)
            flash(other_name + " has been added")
        else:
            flash("You already have ingredient with this name")

    return redirect(url_for("recipes.ingredients"))


@recipes.route('/add_ingredients', methods=['GET'])
def ingredients():
    db = DatabaseConnector()
    user_id = session['id']
    fermentables = db.select_from_fermentables("\'" + str(user_id) + "\'")
    hops = db.select_from_hops("\'" + str(user_id) + "\'")
    yeasts = db.select_from_yeasts("\'" + str(user_id) + "\'")
    others = db.select_from_others("\'" + str(user_id) + "\'")

    return render_template('ingredients_form.html', fermentables=fermentables, hops=hops, yeasts=yeasts, others=others)


@recipes.route('/delete_fermentable/<int:fermentable_id>')
def delete_fermentable(fermentable_id):
    db = DatabaseConnector()
    user_id = session['id']
    fermentables = db.select_from_fermentables("\'" + str(user_id) + "\'")
    possibility_to_delete = False
    for f in fermentables:
        if f[4] == fermentable_id:
            possibility_to_delete = True
    if possibility_to_delete:
        db.delete_from_ingredients('fermentables', "\'" + str(fermentable_id) + "\'")
        flash("Ingredient has been deleted")
    else:
        flash("Error, you cannot delete this ingredient right now")
    return redirect(url_for("recipes.ingredients"))


@recipes.route('/delete_hop/<int:hop_id>')
def delete_hop(hop_id):
    db = DatabaseConnector()
    user_id = session['id']
    hops = db.select_from_hops("\'" + str(user_id) + "\'")
    possibility_to_delete = False
    for h in hops:
        if h[3] == hop_id:
            possibility_to_delete = True
    if possibility_to_delete:
        db.delete_from_ingredients('hops', "\'" + str(hop_id) + "\'")
        flash("Ingredient has been deleted")
    else:
        flash("Error, you cannot delete this ingredient right now")
    return redirect(url_for("recipes.ingredients"))


@recipes.route('/delete_yeast/<int:yeast_id>')
def delete_yeast(yeast_id):
    db = DatabaseConnector()
    user_id = session['id']
    yeasts = db.select_from_yeasts("\'" + str(user_id) + "\'")
    possibility_to_delete = False
    for y in yeasts:
        if y[3] == yeast_id:
            possibility_to_delete = True
    if possibility_to_delete:
        db.delete_from_ingredients('yeasts', "\'" + str(yeast_id) + "\'")
        flash("Ingredient has been deleted")
    else:
        flash("Error, you cannot delete this ingredient right now")
    return redirect(url_for("recipes.ingredients"))


@recipes.route('/delete_other/<int:other_id>')
def delete_other(other_id):
    db = DatabaseConnector()
    user_id = session['id']
    others = db.select_from_others("\'" + str(user_id) + "\'")
    possibility_to_delete = False
    for o in others:
        if o[3] == other_id:
            possibility_to_delete = True
    if possibility_to_delete:
        db.delete_from_ingredients('others', "\'" + str(other_id) + "\'")
        flash("Ingredient has been deleted")
    else:
        flash("Error, you cannot delete this ingredient right now")
    return redirect(url_for("recipes.ingredients"))
