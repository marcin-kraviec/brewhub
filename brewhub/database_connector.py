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
    def insert_into(name, username, email, password, age, bio):
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
    def select_from(name, username, password):
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
    def update(name, username, new_username, new_email, new_bio):
        query = 'UPDATE %s SET username=%s, email=%s, bio=%s WHERE username=%s' %(name, new_username, new_email, new_bio, username)
        print(query)
        try:
            cursor = DatabaseConnector.database.cursor()
            cursor.execute(query)
            DatabaseConnector.database.commit()
        except (mysql.connector.Error, AttributeError) as e:
            logging.error('Query has not been executed: ' + str(e))
