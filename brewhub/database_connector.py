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