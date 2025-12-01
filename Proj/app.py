from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection
import datetime # For handling dates
import random # For generating random reservation IDs

# DB connection from config
app = Flask(__name__)
app.secret_key = 'super_secret_key' # Needed for flash messages

CURRENT_USER_ID = 3 # Hardcoded user ID for demo purposes, should chage once login logic is implemented
# -------------------------------------------------------------------------


# Home Page
# -------------------------------------------------------------------------
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

# Purchase Page
# -------------------------------------------------------------------------
@app.route('/purchase/<int:car_id>', methods=['GET', 'POST'])
def purchase(car_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_cost = request.form['total_cost']
        location_id = request.form['location_id']
        
        insert_query = """
            INSERT INTO "Reservations" 
            (user_id, car_id, pickup_location, dropoff_location, payment_id, pick_up_date, drop_off_date, total_cost, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'confirmed')
        """
        cur.execute(insert_query, (
            CURRENT_USER_ID, 
            car_id, 
            location_id, 
            location_id, 
            1, # Hardcoded Payment ID
            start_date, 
            end_date, 
            total_cost
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Reservation confirmed successfully!")
        return redirect(url_for('my_account'))

    # --- GET Request: Fetch Car Details ---
    cur.execute("""
        SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status, location_id 
        FROM "Cars" 
        WHERE car_id = %s
    """, (car_id,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        # FIX: Changed "id" to "car_id" to match your HTML template
        car = {
            "car_id": row[0], 
            "make": row[1],
            "model": row[2],
            "year": row[3],
            "daily_rate": row[4],
            "transmission": row[5],
            "seats": row[6],
            "MPG": row[7],
            "special": row[8],
            "status": row[9],
            "location_id": row[10]
        }
    else:
        return "Car not found", 404
    
    return render_template('purchase.html', car=car)

# My Account Page
# -------------------------------------------------------------------------
@app.route('/my_account', methods=['GET', 'POST'])
def my_account():
    conn = get_connection()
    cur = conn.cursor()

    # POST: Update Personal Details
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        full_name = f"{first_name} {last_name}"
        
        cur.execute("""
            UPDATE "Users" 
            SET full_name = %s, email = %s, phone_number = %s
            WHERE user_id = %s
        """, (full_name, email, phone, CURRENT_USER_ID))
        
        conn.commit()
        flash("Account details updated.")
        return redirect(url_for('my_account'))

    # GET: Fetch User & History
    
    # 1. Get User Details (Select specific columns so we know the order)
    cur.execute('SELECT full_name, email, phone_number FROM "Users" WHERE user_id = %s', (CURRENT_USER_ID,))
    user_row = cur.fetchone()
    
    user_formatted = {}
    
    if user_row:
        # FIX: Access tuple by index (0, 1, 2) instead of string keys
        # user_row[0] is full_name, user_row[1] is email, etc.
        full_name_text = user_row[0] if user_row[0] else " "
        names = full_name_text.split(' ', 1)
        
        user_formatted = {
            'first_name': names[0],
            'last_name': names[1] if len(names) > 1 else '',
            'email': user_row[1],
            'phone': user_row[2]
        }

    # 2. Get Reservation History
    history_query = """
        SELECT r.reservation_id, 
               CONCAT(c.year, ' ', c.make, ' ', c.model),
               r.pick_up_date,
               r.total_cost,
               r.status
        FROM "Reservations" r
        JOIN "Cars" c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.pick_up_date DESC
    """
    cur.execute(history_query, (CURRENT_USER_ID,))
    history_rows = cur.fetchall()

    cur.close()
    conn.close()

    # FIX: Convert the tuple history rows into dictionaries
    # This prevents errors in the HTML when doing {{ reservation.car }}
    history = []
    for row in history_rows:
        history.append({
            "id": row[0],
            "car": row[1],
            "date": row[2],
            "cost": row[3],
            "status": row[4]
        })
    
    return render_template('my_account.html', user=user_formatted, history=history)

# Cancel Reservation
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    
    # Golden Rule: Permit easy reversal of actions 
    cur.execute("""
        UPDATE "Reservations" 
        SET status = 'cancelled' 
        WHERE reservation_id = %s AND user_id = %s
    """, (reservation_id, CURRENT_USER_ID))
    
    conn.commit()
    cur.close()
    conn.close()
    
    flash("Reservation cancelled.")
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