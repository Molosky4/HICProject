from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection
import datetime

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

# --- MY ACCOUNT PAGE ROUTE ---
@app.route('/my_account', methods=['GET'])
def my_account():
    # Since "no login is required" for the project, we simulate User ID 1 is logged in
    user_id = 1 
    
    conn = get_connection()
    cur = conn.cursor()

    # 1. Fetch User Information
    cur.execute('SELECT first_name, last_name, email, phone FROM "Users" WHERE user_id = %s', (user_id,))
    user_data = cur.fetchone()
    
    if user_data:
        user = {
            "first_name": user_data[0],
            "last_name": user_data[1],
            "email": user_data[2],
            "phone": user_data[3]
        }
    else:
        user = None

    # 2. Fetch Rental History (Joins Rentals with Cars to show what they rented)
    cur.execute("""
        SELECT r.rental_date, c.make, c.model, r.total_cost 
        FROM "Rentals" r
        JOIN "Cars" c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.rental_date DESC
    """, (user_id,))
    
    history_rows = cur.fetchall()
    
    history = [
        {"date": row[0], "car": f"{row[1]} {row[2]}", "cost": row[3]} 
        for row in history_rows
    ]

    cur.close()
    conn.close()

    return render_template('my_account.html', user=user, history=history)


# --- PURCHASE PAGE ROUTE ---
@app.route('/purchase/<int:car_id>', methods=['GET', 'POST'])
def purchase(car_id):
    conn = get_connection()
    cur = conn.cursor()

    # GET: Display the car details and the purchase form
    if request.method == 'GET':
        cur.execute('SELECT car_id, make, model, year, daily_rate, transmission, "MPG" FROM "Cars" WHERE car_id = %s', (car_id,))
        car_data = cur.fetchone()
        
        cur.close()
        conn.close()

        if car_data:
            car = {
                "id": car_data[0], "make": car_data[1], "model": car_data[2],
                "year": car_data[3], "rate": car_data[4], "transmission": car_data[5], "mpg": car_data[6]
            }
            return render_template('purchase.html', car=car)
        else:
            return "Car not found", 404

    # POST: Process the "Payment"
    if request.method == 'POST':
        user_id = 1  # Simulated logged-in user
        total_cost = request.form.get('total_cost')
        
        # Insert the rental record
        try:
            cur.execute("""
                INSERT INTO "Rentals" (user_id, car_id, total_cost)
                VALUES (%s, %s, %s)
            """, (user_id, car_id, total_cost))
            conn.commit()
            flash("Booking confirmed! Thank you for your purchase.")
        except Exception as e:
            conn.rollback()
            flash("An error occurred during processing.")
            print(e)
        finally:
            cur.close()
            conn.close()

        # Redirect to My Account to show the Golden Rule: "Design dialogue to yield closure"
        return redirect(url_for('my_account'))             

if __name__ == '__main__':
    app.run()