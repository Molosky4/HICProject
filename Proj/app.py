import secrets
from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session
from config import get_connection
import datetime # For handling dates
import random # For generating random reservation IDs

#DB connection from config
app = Flask(__name__)
app.secret_key = 'super_secret_key' # Needed for flash messages

def check_password_hash(password_hash, password):
    raise NotImplementedError

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

def generate_password_hash(password):
    raise NotImplementedError

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        full_name = request.form.get('name') # Ensure HTML input has name="name"
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
            # Don't reveal if user exists or not for security, but flash success anyway
            flash('If that email exists, we sent a link.')
            
        cur.close()
        conn.close()
        
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

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
    return render_template('car_results.html', carsAtLocation=filtered_cars)


# My Account & Purchase Page
# -------------------------------------------------------------------------

@app.route('/my_account', methods=['GET'])
def my_account():
    # Simulate a logged-in user (User ID 1 based on your SQL setup)
    user_id = 1 
    
    conn = get_connection()
    cur = conn.cursor()

    # 1. Fetch User Information
    cur.execute('SELECT full_name, email, phone_number FROM "Users" WHERE user_id = %s', (user_id,))
    user_data = cur.fetchone()
    
    user = None
    if user_data:
        # Split full_name into first and last for the template display
        full_name_split = user_data[0].split(' ', 1)
        first_name = full_name_split[0]
        last_name = full_name_split[1] if len(full_name_split) > 1 else ""
        
        user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": user_data[1],
            "phone": user_data[2]
        }

    # 2. Fetch Reservation History
    cur.execute("""
        SELECT r.pick_up_date, c.year, c.make, c.model, r.total_cost, r.status
        FROM "Reservations" r
        JOIN "Cars" c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.pick_up_date DESC
    """, (user_id,))
    
    rows = cur.fetchall()
    
    history = [
        {
            "date": row[0], 
            "car": f"{row[1]} {row[2]} {row[3]}", 
            "cost": row[4], 
            "status": row[5]
        } 
        for row in rows
    ]

    cur.close()
    conn.close()

    return render_template('my_account.html', user=user, history=history)


@app.route('/purchase/<int:car_id>', methods=['GET', 'POST'])
def purchase(car_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'GET':
        # Fetch car details for the "Car Summary" section
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
        
        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        total_cost = request.form.get('total_cost')
        location_id = request.form.get('location_id')
        
        # Generate a random reservation ID
        res_id = random.randint(10000, 99999) 

        try:
            # Insert the reservation
            cur.execute("""
                INSERT INTO "Reservations" 
                (reservation_id, user_id, car_id, pickup_location, dropoff_location, pick_up_date, drop_off_date, total_cost, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'confirmed')
            """, (res_id, user_id, car_id, location_id, location_id, start_date, end_date, total_cost))
            
            conn.commit()
            flash("Booking confirmed!")
            return redirect(url_for('my_account'))
            
        except Exception as e:
            conn.rollback()
            print(e)
            return f"An error occurred: {e}"
        finally:
            cur.close()
            conn.close()


if __name__ == '__main__':
    app.run()