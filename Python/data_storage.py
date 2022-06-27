import sqlite3
import os


def create_connection(db_name):
    # this function requires a name parameter to create the database
    #calling the function with the name of an existing database enables the access to the database

    conn = sqlite3.connect(db_name, check_same_thread=False)

    return conn


if not os.path.exists("./database"):
    os.makedirs("./database")

connection = create_connection("./database/crypto_billionairs.db")