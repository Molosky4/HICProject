from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
import config
import psycopg2 #install: pip install psycopg2

#DB connection from config
app = Flask(__name__)
app.secret_key = "secret_key_here"
conn = config.conn

# Connect to the database         //replace with your local db name
conn = psycopg2.connect(database="flask_carrental_db", user="postgres",
                        password="NewPasswordHere", host="localhost", port="5432")

# create a cursor
cur = conn.cursor()
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/locations')
def locations():
    return 'locations'

if __name__ == '__main__':
    app.run()