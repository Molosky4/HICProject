from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
import config
import psycopg2 #install: pip install psycopg2

#DB connection from config
app = Flask(__name__)

# Connect to the database         //replace with your local db name
conn = psycopg2.connect(database="flask_carrental_db", user="postgres",
                        password="JbL_$!760.:?", host="localhost", port="5432")
                        #set to your password

# create a cursor
cur = conn.cursor()

# commit the changes
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

app.secret_key = config.SECRET_KEY

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()