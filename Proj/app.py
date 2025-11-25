from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection

#DB connection from config
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():

    if request.method == 'POST':

        ac = request.form.get('ac')
        
        if ac == "rev":
            rev = request.form.get('reviewSubmit')
        
        if ac == "sch":
            l = request.form.get('l')
            return redirect(url_for('locations', l = l))

        return render_template('index.html')    

    return render_template('index.html')


@app.route('/locations', methods=['GET'])
def locations():
    l = request.args.get('l')
    
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all locations
    cur.execute("SELECT location_id, location_name, street, city, location_image, open_time, close_time, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    
    locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image":r[4], "opens": r[5], "closes": r[6], "days_open":r[7]}
        for r in rows
    ]

    return render_template('locations.html', locations=locations, l=l)

@app.route('/search_locations', methods=['GET'])
def search_locations():
    # 1. Get the search term from the AJAX request
    query = request.args.get('q', '').lower()
    
    conn = get_connection()
    cur = conn.cursor()
    
    # 2. Fetch all data (or just the necessary data for the query)
    cur.execute("SELECT location_id, location_name, street, city, location_image, open_time, close_time, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    
    all_locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image":r[4], "opens": r[5], "closes": r[6], "days_open":r[7]}
        for r in rows
    ]

    # 3. Filter the data based on the query (case-insensitive)
    filtered_locations = [
        loc for loc in all_locations
        if query in loc['name'].lower() or query in loc['city'].lower() or query in loc['street'].lower()
    ]

    # 4. Render only the partial HTML template with the filtered results
    # You MUST create a separate template file named 'location_results_partial.html'
    return render_template('location_results.html', locations=filtered_locations)


@app.route('/locations/<int:location_id>')
def cars_at_location(location_id):
    conn = get_connection()
    cur = conn.cursor()

    # adjust column/table names to your DB
    cur.execute("""
        SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status 
        FROM "Cars"
        WHERE location_id = %s;
    """, (location_id,))

    cars = cur.fetchall()

    cur.close()
    conn.close()

    carsAtLocation = [
         {"id": car[0], "make": car[1], "model": car[2], "year": car[3], "rate":car[4], "transmission": car[5],
           "seats": car[6], "MPG":car[7], "special": car[8], "status": car[9]}
        for car in cars
    ]

    return render_template("cars.html", carsAtLocation=carsAtLocation, location_id=location_id) 

@app.route('/search_cars', methods=['GET'])
def search_cars():
    # 1. Get the search term from the AJAX request
    query = request.args.get('q', '').lower()
    location_id = request.args.get('location_id')
    
    conn = get_connection()
    cur = conn.cursor()
    
    # 2. Fetch all data (or just the necessary data for the query)
    cur.execute("""
        SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status 
        FROM "Cars"
        WHERE location_id = %s;
    """, (location_id,))
    
    cars = cur.fetchall()

    cur.close()
    conn.close()
    
    cars = [
         {"id": car[0], "make": car[1], "model": car[2], "year": car[3], "rate":car[4], "transmission": car[5],
           "seats": car[6], "MPG":car[7], "special": car[8], "status": car[9]}
        for car in cars
    ]

    # 3. Filter the data based on the query (case-insensitive)
    filtered_cars = [
        car for car in cars
        if query in car['model'].lower()
    ]

    # 4. Render only the partial HTML template with the filtered results
    # You MUST create a separate template file named 'location_results_partial.html'
    return render_template('car_results.html', carsAtLocation=filtered_cars)                

if __name__ == '__main__':
    app.run()