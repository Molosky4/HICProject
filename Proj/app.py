import secrets
from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection
import datetime 
import random 
# Restore the actual security functions
from werkzeug.security import generate_password_hash, check_password_hash

# DB connection from config
app = Flask(__name__)
app.secret_key = 'super_secret_key' 

# -------------------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ensure your HTML inputs have name="email" and name="password"
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Check user
        cur.execute('SELECT user_id, full_name, password_hash FROM "Users" WHERE email = %s', (email,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash('Logged in successfully!')
            return redirect(url_for('home')) # Redirect to home page after login
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        full_name = request.form.get('name') 
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the password
        hashed_pw = generate_password_hash(password)
        
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                'INSERT INTO "Users" (full_name, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id',
                (full_name, email, hashed_pw)
            )
            conn.commit()
            flash('Account created! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash('Email already exists or error occurred.', 'error')
            print(e)
        finally:
            cur.close()
            conn.close()
            
    return render_template('create_account.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute('SELECT user_id FROM "Users" WHERE email = %s', (email,))
        user = cur.fetchone()
        
        if user:
            # Generate a fake token for the demo
            token = secrets.token_urlsafe(16)
            cur.execute(
                'INSERT INTO "PasswordResets" (user_id, reset_token, expires_at) VALUES (%s, %s, NOW() + INTERVAL \'1 hour\')',
                (user[0], token)
            )
            conn.commit()
            flash('Recovery link sent (Simulated). Check your email/console.')
            print(f"SIMULATED EMAIL: Reset link for {email} is /reset/{token}")
        else:
            flash('If that email exists, we sent a link.')
            
        cur.close()
        conn.close()
        
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# -------------------------------------------------------------------------
# MAIN ROUTES
# -------------------------------------------------------------------------
# Home Page
# -------------------------------------------------------------------------
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        ac = request.form.get('ac')
        
        if ac == "rev":
            rev = request.form.get('reviewSubmit')
            flash("Review submitted successfully!")
        
        if ac == "sch":
            l = request.form.get('l')
            return redirect(url_for('locations', l = l))

        return render_template('index.html')    

    return render_template('index.html')


# Locations & Cars Pages
# -------------------------------------------------------------------------

@app.route('/locations', methods=['GET'])
def locations():
    l = request.args.get('l')
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    
    locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image":r[4], "opens": r[5], "closes": r[6], "days_open":r[7]}
        for r in rows
    ]

    return render_template('locations.html', locations=locations, l=l)

# Search Locations
# -------------------------------------------------------------------------
@app.route('/search_locations', methods=['GET'])
def search_locations():
    query = request.args.get('q', '').lower()
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    
    all_locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image":r[4], "opens": r[5], "closes": r[6], "days_open":r[7]}
        for r in rows
    ]

    filtered_locations = [
        loc for loc in all_locations
        if query in loc['name'].lower() or query in loc['city'].lower() or query in loc['street'].lower()
    ]

    return render_template('location_results.html', locations=filtered_locations)

# Cars at Location
# -------------------------------------------------------------------------
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
         {
             "id": car[0],      # <--- Added this for car_results.html
             "car_id": car[0],  # <--- Kept this for purchase.html
             "make": car[1], 
             "model": car[2], 
             "year": car[3], 
             "rate": car[4], 
             "transmission": car[5],
             "seats": car[6], 
             "MPG": car[7], 
             "special": car[8], 
             "status": car[9]
         }
        for car in cars
    ]

    return render_template("cars.html", carsAtLocation=carsAtLocation, location_id=location_id)

# Search Cars
# -------------------------------------------------------------------------
@app.route('/search_cars', methods=['GET'])
def search_cars():
    query = request.args.get('q', '').lower()
    location_id = request.args.get('location_id')
    
    conn = get_connection()
    cur = conn.cursor()
    
    if location_id:
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status 
            FROM "Cars"
            WHERE location_id = %s;
        """, (location_id,))
    else:
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status 
            FROM "Cars";
        """)
    
    cars = cur.fetchall()
    cur.close()
    conn.close()
    
    # FIXED: Changed "id" to "car_id" here as well
    cars_list = [
         {
             "car_id": car[0],
             "make": car[1], 
             "model": car[2], 
             "year": car[3], 
             "rate": car[4], 
             "transmission": car[5],
             "seats": car[6], 
             "MPG": car[7], 
             "special": car[8], 
             "status": car[9]
         }
        for car in cars
    ]

    filtered_cars = [
        car for car in cars_list
        if query in car['model'].lower() or query in car['make'].lower()
    ]

    return render_template('car_results.html', carsAtLocation=filtered_cars)

# My Account Page
# -------------------------------------------------------------------------
@app.route('/my_account', methods=['GET', 'POST'])
def my_account():
    # 1. Check Login
    if 'user_id' not in session:
        flash("Please log in to view your account.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()

    # 2. Get User Details
    cur.execute('SELECT full_name, email, phone_number FROM "Users" WHERE user_id = %s', (user_id,))
    user_data = cur.fetchone() # We name this 'user_data'
    
    user_formatted = {}
    
    # FIX: Changed 'user_row' to 'user_data' to match the variable above
    if user_data:
        full_name_text = user_data[0] if user_data[0] else " "
        names = full_name_text.split(' ', 1)
        
        user_formatted = {
            'first_name': names[0],
            'last_name': names[1] if len(names) > 1 else '',
            'email': user_data[1],
            'phone': user_data[2]
        }

    # 3. Get History
    # FIX: Assign the string to a variable first, then execute
    history_query = """
        SELECT r.reservation_id, r.pick_up_date, c.year, c.make, c.model, r.total_cost, r.status
        FROM "Reservations" r
        JOIN "Cars" c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.pick_up_date DESC
    """
    
    # FIX: Use 'user_id' (from session), not 'CURRENT_USER_ID'
    cur.execute(history_query, (user_id,))
    history_rows = cur.fetchall()

    cur.close()
    conn.close()

    # FIX: Convert rows to dictionaries so HTML doesn't break
    history = []
    for row in history_rows:
        history.append({
            "reservation_id": row[0],
            "pick_up_date": row[1],
            "car_name": f"{row[2]} {row[3]} {row[4]}",
            "total_cost": row[5],
            "status": row[6]
        })

    # FIX: Pass 'user_formatted', not 'user' (which didn't exist)
    return render_template('my_account.html', user=user_formatted, history=history)


# Purchase Page
# -------------------------------------------------------------------------
@app.route('/purchase/<int:car_id>', methods=['GET', 'POST'])
def purchase(car_id):
    if 'user_id' not in session:
        flash("Please log in to reserve a car.")
        return redirect(url_for('login'))

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
                # FIX: Changed "id" to "car_id" to match your HTML
                "car_id": car_data[0], 
                "make": car_data[1], 
                "model": car_data[2],
                "year": car_data[3], 
                "rate": car_data[4], 
                "transmission": car_data[5], 
                "mpg": car_data[6], 
                "location_id": car_data[7]
            }
            return render_template('purchase.html', car=car)
        else:
            return "Car not found", 404

    if request.method == 'POST':
        # ... (Your POST logic is fine, keep it as is) ...
        user_id = session['user_id']
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        total_cost = request.form.get('total_cost')
        location_id = request.form.get('location_id')
        
        res_id = random.randint(10000, 99999) 
        payment_id = 1 

        try:
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

# Cancel Reservation
# -------------------------------------------------------------------------
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    # 1. Check if user is logged in
    if 'user_id' not in session:
        flash("Please log in.")
        return redirect(url_for('login'))

    # 2. Get the real user ID from the session
    user_id = session['user_id']

    conn = get_connection()
    cur = conn.cursor()
    
    # 3. Use user_id instead of CURRENT_USER_ID
    cur.execute("""
        UPDATE "Reservations" 
        SET status = 'cancelled' 
        WHERE reservation_id = %s AND user_id = %s
    """, (reservation_id, user_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    flash("Reservation cancelled.")
    return redirect(url_for('my_account'))

# Special Offers Page
@app.route('/specials', methods=['GET'])
def specials():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT title, description, valid_until, discount, image_path FROM "Specials"')
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

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