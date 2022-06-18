import mysql.connector
import logging
import sys
from brewhub.database_config import HOST, USER, PASSWORD, DATABASE


class DatabaseConnector:
    # establishing connection to database
    try:
        database = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE,
                                           auth_plugin='mysql_native_password')
        print('DUPA')
    except mysql.connector.Error as e:
        logging.critical('Connection to database has not been established: ' + str(e))
        sys.exit()

    @staticmethod
    def test():
        query = 'SELECT username, email FROM users'
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)

            for element in cursor:
                print(element)
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def insert_into_users(name, username, email, password, age, bio):
        query = 'INSERT INTO %s (username, email, password, age, bio) VALUES (%s, %s, %s, %s, %s)' % (name, username, email, password, age, bio)
        print(query)

        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def select_from_registration(name):
        query = 'SELECT username FROM %s' % name
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            data = []
            for element in cursor:
                # tuple unpacking
                (username) = element
                line = username[0]
                print(line)
                data.append(line)
            return data
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def select_from_users(name, username, password):
        query = 'SELECT * FROM %s WHERE username=%s AND password=%s' % (name, username, password)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            data = []
            for element in cursor:
                data.append(element)
            return data
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def update_users(name, username, new_username, new_email, new_bio):
        query = 'UPDATE %s SET username=%s, email=%s, bio=%s WHERE username=%s' %(name, new_username, new_email, new_bio, username)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def insert_into_fermentables(user_id, name, color, contribution, price):
        query = 'INSERT INTO fermentables (user_id, name, color, contribution, price) VALUES (%s, %s, %s, %s, %s)' % (user_id, name, color, contribution, price)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def select_from_fermentables(user_id):
        query = 'SELECT name, color, contribution, price FROM fermentables WHERE user_id=%s' % (user_id)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            fermentables = []
            for element in cursor:
                fermentables.append(element)
            return fermentables
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def insert_into_hops(user_id, name, alpha_acids, price):
        query = 'INSERT INTO hops (user_id, name, alpha_acids, price) VALUES (%s, %s, %s, %s)' % (
        user_id, name, alpha_acids, price)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def select_from_hops(user_id):
        query = 'SELECT name, alpha_acids, price FROM hops WHERE user_id=%s' % (user_id)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            hops = []
            for element in cursor:
                hops.append(element)
            return hops
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def insert_into_others(user_id, name, info, price):
        query = 'INSERT INTO others (user_id, name, info, price) VALUES (%s, %s, %s, %s)' % (
            user_id, name, info, price)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def select_from_others(user_id):
        query = 'SELECT name, info, price FROM others WHERE user_id=%s' % (user_id)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            others = []
            for element in cursor:
                others.append(element)
            return others
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def insert_into_yeasts(user_id, name, attenuation, price):
        query = 'INSERT INTO yeasts (user_id, name, attenuation, price) VALUES (%s, %s, %s, %s)' % (
            user_id, name, attenuation, price)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

    @staticmethod
    def select_from_yeasts(user_id):
        query = 'SELECT name, attenuation, price FROM yeasts WHERE user_id=%s' % (user_id)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            yeasts = []
            for element in cursor:
                yeasts.append(element)
            return yeasts
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))

