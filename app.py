from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error

DATABASE = "C:/Users/maxmo/PycharmProjects/TeReoDictonary-Assesment/TeReo"

app = Flask(__name__)

def create_connection(db_file):
    """
    create a connection with a database
    :parameter name of the database
    :return a connection to the file
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_homepage():  # put application's code here
    return render_template('home.html')

@app.route('/category')
def render_category():  # put application's code here
    con = create_connection(DATABASE)
    query = "SELECT maori, english, category, definition, level FROM Dictionary"
    cur = con.cursor()
    cur.execute(query)
    definition_list = cur.fetchall()
    con.close()
    print(definition_list)
    return render_template('category.html', definitions=definition_list)

@app.route('/login')
def render_login():  # put application's code here
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
