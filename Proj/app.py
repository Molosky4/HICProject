from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection

#DB connection from config
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/locations')
def locations():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all locations
    cur.execute("SELECT location_id, location_name, street, city, location_image FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image":r[4]}
        for r in rows
    ]

    return render_template('locations.html', locations=locations)

# @app.route('/locations/<int:location_id>')
# def cars_at_location(location_id):
#     conn = get_connection()
#     cur = conn.cursor()

#     # adjust column/table names to your DB
#     cur.execute("""
#         SELECT car_id, car_make, car_model, car_year
#         FROM "Cars"
#         WHERE location_id = %s;
#     """, (location_id,))

#     cars = cur.fetchall()

#     cur.close()
#     conn.close()

#     return render_template("results.html", cars=cars)

if __name__ == '__main__':
    app.run()