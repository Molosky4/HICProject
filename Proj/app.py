from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
import config
import psycopg2 #install: pip install psycopg2

#DB connection from config
app = Flask(__name__)
conn = config.conn

# create a cursor
cur = conn.cursor()


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()