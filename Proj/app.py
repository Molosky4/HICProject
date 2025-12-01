from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection
import datetime # For handling dates
import random # For generating random reservation IDs

# DB connection from config
app = Flask(__name__)
app.secret_key = 'super_secret_key' # Needed for flash messages

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        ac = request.form.get('ac')
        
        if ac == "rev":
            rev = request.form.get('reviewSubmit')
            # In a real app, save review here
            flash("Review submitted successfully!")
        
        if ac == "sch":
            l = request.form.get('l')
            return redirect(url_for('locations', l = l))

        return render_template('index.html')    

    return render_template('index.html')

# User Authentication Pages
# -------------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

# Locations & Cars Pages
# -------------------------------------------------------------------------

@app.route('/locations', methods=['GET'])
def locations():
    l = request.args.get('l')
    
    conn = get_connection()
    cur = conn.cursor()

    # FIX: Updated column names to match data.sql (name, street, city, image_file, etc.)
    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
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
    
    # FIX: Updated column names to match data.sql
    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
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
    return render_template('location_results.html', locations=filtered_locations)


@app.route('/locations/<int:location_id>')
def cars_at_location(location_id):
    conn = get_connection()
    cur = conn.cursor()

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

# Search Cars within a Location
@app.route('/search_cars', methods=['GET'])
def search_cars():
    query = request.args.get('q', '').lower()
    location_id = request.args.get('location_id')
    
    conn = get_connection()
    cur = conn.cursor()
    
    # If location_id is provided, filter by it, otherwise search all (optional safety check)
    if location_id:
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status 
            FROM "Cars"
            WHERE location_id = %s;
        """, (location_id,))
    else:
        # Fallback if no location selected (prevents crash)
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status 
            FROM "Cars";
        """)
    
    cars = cur.fetchall()
    cur.close()
    conn.close()
    
    cars_list = [
         {"id": car[0], "make": car[1], "model": car[2], "year": car[3], "rate":car[4], "transmission": car[5],
           "seats": car[6], "MPG":car[7], "special": car[8], "status": car[9]}
        for car in cars
    ]

    filtered_cars = [
        car for car in cars_list
        if query in car['model'].lower() or query in car['make'].lower()
    ]

    return render_template('car_results.html', carsAtLocation=filtered_cars)


# My Account Page
# -------------------------------------------------------------------------

@app.route('/my_account', methods=['GET'])
def my_account():
    # Simulate a logged-in user (User ID 1 based on our SQL setup)
    user_id = 1 
    
    conn = get_connection()
    cur = conn.cursor()

    # 1. Fetch User Information
    cur.execute('SELECT full_name, email, phone_number FROM "Users" WHERE user_id = %s', (user_id,))
    user_data = cur.fetchone()
    
    user = None
    if user_data:
        full_name_split = user_data[0].split(' ', 1)
        first_name = full_name_split[0]
        last_name = full_name_split[1] if len(full_name_split) > 1 else ""
        
        user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": user_data[1],
            "phone": user_data[2]
        }

    # 2. Fetch Reservation History (Added reservation_id to select for cancellation)
    cur.execute("""
        SELECT r.reservation_id, r.pick_up_date, c.year, c.make, c.model, r.total_cost, r.status
        FROM "Reservations" r
        JOIN "Cars" c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.pick_up_date DESC
    """, (user_id,))
    
    rows = cur.fetchall()
    
    history = [
        {
            "id": row[0],
            "date": row[1], 
            "car": f"{row[2]} {row[3]} {row[4]}", 
            "cost": row[5], 
            "status": row[6]
        } 
        for row in rows
    ]

    cur.close()
    conn.close()

    return render_template('my_account.html', user=user, history=history)

# Purchase Page
# -------------------------------------------------------------------------

@app.route('/purchase/<int:car_id>', methods=['GET', 'POST'])
def purchase(car_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, "MPG", location_id 
            FROM "Cars" 
            WHERE car_id = %s
        """, (car_id,))
        car_data = cur.fetchone()
        
        cur.close()
        conn.close()

        if car_data:
            car = {
                "id": car_data[0], "make": car_data[1], "model": car_data[2],
                "year": car_data[3], "rate": car_data[4], "transmission": car_data[5], 
                "mpg": car_data[6], "location_id": car_data[7]
            }
            return render_template('purchase.html', car=car)
        else:
            return "Car not found", 404

    if request.method == 'POST':
        user_id = 1  # Simulated Logged-in User
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        total_cost = request.form.get('total_cost')
        location_id = request.form.get('location_id')
        
        res_id = random.randint(10000, 99999) 
        
        # FIX: Hardcoded payment_id to 1 (Matches John Doe in our data.sql)
        payment_id = 1 

        try:
            # Insert reservation into the database
            cur.execute("""
                INSERT INTO "Reservations" 
                (reservation_id, user_id, car_id, pickup_location, dropoff_location, payment_id, pick_up_date, drop_off_date, total_cost, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmed')
            """, (res_id, user_id, car_id, location_id, location_id, payment_id, start_date, end_date, total_cost))
            
            conn.commit()
            flash("Booking confirmed successfully!")
            return redirect(url_for('my_account'))
            
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return f"An error occurred: {e}"
        finally:
            cur.close()
            conn.close()

# NEW ROUTE: Allow user to cancel reservation (Golden Rule: Easy Reversal of Actions)
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE "Reservations" 
            SET status = 'cancelled' 
            WHERE reservation_id = %s
        """, (reservation_id,))
        conn.commit()
        flash("Reservation cancelled.")
    except Exception as e:
        conn.rollback()
        flash("Error cancelling reservation.")
    finally:
        cur.close()
        conn.close()
        
    return redirect(url_for('my_account'))


@app.route('/specials', methods=['GET'])
def specials():
    conn = get_connection()
    cur = conn.cursor()
    
    # Fetch specials from the database
    cur.execute('SELECT title, description, valid_until, discount, image_path FROM "Specials"')
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    # Create a list of dictionaries for the template
    specials_list = [
        {
            "title": r[0], 
            "description": r[1], 
            "valid_until": r[2], 
            "discount": r[3], 
            "image": r[4]
        } 
        for r in rows
    ]

    return render_template('specials.html', specials=specials_list)

if __name__ == '__main__':
    app.run(debug=True)