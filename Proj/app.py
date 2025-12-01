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
    cur = get_connection().cursor()

    if request.method == 'GET':
        sql = "SELECT review_id, user_id, full_name, review FROM \"Reviews\" LIMIT 5"
        cur.execute(sql)
        rev = cur.fetchall()

    if request.method == 'POST':
        ac = request.form.get('ac')
        
        if ac == "rev":
            rev = request.form.get('reviewSubmit')
            sql = "INSERT INTO Reviews(user_id, full_name, review) VALUES (%s, %s, %s)"
            cur.execute(sql, (session.get('user_id'), session.get('user_name'), rev,))

        
        if ac == "sch":
            l = request.form.get('l')
            return redirect(url_for('locations', l = l))

        return render_template('index.html', rev=rev)    

    return render_template('index.html', rev=rev)


# Locations & Cars Pages
# -------------------------------------------------------------------------

@app.route('/locations', methods=['GET'])
def locations():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image": r[4], "opens": r[5], "closes": r[6], "days_open": r[7]}
        for r in rows
    ]

    return render_template('locations.html', locations=locations)

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
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image": r[4], "opens": r[5], "closes": r[6], "days_open": r[7]}
        for r in rows
    ]

    filtered_locations = [
        loc for loc in all_locations
        if query in (loc['name'] or '').lower() or query in (loc['city'] or '').lower() or query in (loc['street'] or '').lower()
    ]

    return render_template('location_results.html', locations=filtered_locations)

# Cars at Location
# -------------------------------------------------------------------------
@app.route('/locations/<int:location_id>')
def cars_at_location(location_id):
    conn = get_connection()
    cur = conn.cursor()

    if location_id == 0:
        # Fetch all cars (no filter on location)
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status
            FROM "Cars";
        """)
    else:
        # Otherwise, filter by location_id
        cur.execute("""
            SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status
            FROM "Cars"
            WHERE location_id = %s;
        """, (location_id,))


    cars = cur.fetchall()

    cur.close()
    conn.close()

    carsAtLocation = [
         {"id": car[0], "make": car[1], "model": car[2], "year": car[3], "rate": car[4], "transmission": car[5],
           "seats": car[6], "MPG": car[7], "special": car[8], "status": car[9]}
        for car in cars
    ]

    return render_template("cars.html", carsAtLocation=carsAtLocation, location_id=location_id)

# Search Cars
# -------------------------------------------------------------------------
@app.route('/search_cars', methods=['GET'])
def search_cars():
    query = request.args.get('q', '').lower()
    location_id = request.args.get('location_id')

    # Get database connection
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
    
    cars_list = [
         {
              "id": car[0],      # <--- Added this for car_results.html
             "car_id": car[0], # <--- Kept this for purchase.html
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
    # cur.execute(history_query, (CURRENT_USER_ID,))
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
                "id": car_data[0], "make": car_data[1], "model": car_data[2],
                "year": car_data[3], "rate": car_data[4], "transmission": car_data[5], 
                "mpg": car_data[6], "location_id": car_data[7]
            }
            return render_template('purchase.html', car=car)
        else:
            return "Car not found", 404

    if request.method == 'POST':
        user_id = session['user_id']
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        total_cost = request.form.get('total_cost')
        location_id = request.form.get('location_id')
        
        res_id = random.randint(10000, 99999) 
        payment_id = 1 # Placeholder for payment ID

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

@app.route('/reservation/modify/<int:reservation_id>', methods=['GET', 'POST'])
def modify_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        try:
            # Get form data
            car_id = int(request.form.get('car_id'))
            pick_up_date = request.form.get('pick_up_date')
            drop_off_date = request.form.get('drop_off_date')
            pickup_location = int(request.form.get('pickup_location'))
            dropoff_location = int(request.form.get('dropoff_location'))
            payment_id_raw = request.form.get('payment_id')
            payment_id = int(payment_id_raw) if payment_id_raw else None

            # Validate dates
            if not pick_up_date or not drop_off_date:
                flash('Pick-up and drop-off dates are required.', 'danger')
                return redirect(url_for('modify_reservation', reservation_id=reservation_id))

            d1 = datetime.fromisoformat(pick_up_date)
            d2 = datetime.fromisoformat(drop_off_date)
            days = (d2 - d1).days
            
            if days < 0:
                flash('Drop-off must be after pick-up date.', 'danger')
                return redirect(url_for('modify_reservation', reservation_id=reservation_id))
            if days == 0:
                days = 1

            # Get car's daily rate to recalculate cost
            cur.execute("SELECT daily_rate, status FROM \"Cars\" WHERE car_id = %s", (car_id,))
            car_row = cur.fetchone()
            if not car_row:
                flash('Selected car not found.', 'danger')
                return redirect(url_for('modify_reservation', reservation_id=reservation_id))
            
            daily_rate, status = car_row
            total_cost = float(daily_rate) * days

            # Update reservation
            cur.execute("""
                UPDATE reservations 
                SET car_id = %s, 
                    pick_up_date = %s, 
                    drop_off_date = %s, 
                    pickup_location = %s, 
                    dropoff_location = %s, 
                    payment_id = %s, 
                    total_cost = %s
                WHERE reservation_id = %s;
            """, (car_id, pick_up_date, drop_off_date, pickup_location, dropoff_location, payment_id, total_cost, reservation_id))
            
            conn.commit()
            flash(f'Reservation updated successfully! New total: ${total_cost:.2f}', 'success')
            return redirect(url_for('manage_reservations'))
            
        except Exception as e:
            conn.rollback()
            print('Error updating reservation:', e)
            flash('There was an error updating your reservation. Please try again.', 'danger')
            return redirect(url_for('modify_reservation', reservation_id=reservation_id))
        finally:
            cur.close()
            conn.close()
    
    else:  # GET request
        # Fetch the reservation details
        cur.execute("""
            SELECT reservation_id, pick_up_date, drop_off_date, pickup_location, 
                   dropoff_location, car_id, payment_id, total_cost, status
            FROM reservations 
            WHERE reservation_id = %s;
        """, (reservation_id,))
        row = cur.fetchone()
        
        if not row:
            cur.close()
            conn.close()
            abort(404)
        
        res = {
            "id": row[0],
            "code": row[0],  # Using reservation_id as code
            "pick_up_date": row[1],
            "drop_off_date": row[2],
            "pickup_location": row[3],
            "dropoff_location": row[4],
            "car_id": row[5],
            "payment_id": row[6],
            "total_cost": row[7],
            "status": row[8]
        }
        
        # Fetch all cars for dropdown
        cur.execute("SELECT car_id, make, model, year, daily_rate FROM \"Cars\" ORDER BY car_id;")
        cars = cur.fetchall()
        
        # Fetch all locations for dropdown
        cur.execute("SELECT location_id, name FROM \"Locations\" ORDER BY location_id;")
        locations = cur.fetchall()
        
        # Fetch all payment methods for dropdown
        cur.execute("SELECT payment_id, payment_type FROM \"PaymentInfo\" ORDER BY payment_id;")
        payments = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('modify_reservation.html', 
                             res=res, 
                             cars=cars, 
                             locations=locations, 
                             payments=payments)



@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    conn = get_connection()
    cur = conn.cursor()

    try:
        if request.method == 'POST':
            try:
                # Parse inputs
                user_id = int(request.form.get('user_id'))
                car_id = int(request.form.get('car_id'))
                pickup_location = int(request.form.get('pickup_location'))
                dropoff_location = int(request.form.get('dropoff_location'))
                payment_id_raw = request.form.get('payment_id')
                payment_id = int(payment_id_raw) if payment_id_raw else None
                pick_up_date = request.form.get('pick_up_date')
                drop_off_date = request.form.get('drop_off_date')

                # Basic validation
                if not pick_up_date or not drop_off_date:
                    flash('Pick-up and drop-off dates are required.', 'danger')
                    return redirect(url_for('reserve'))

                d1 = datetime.fromisoformat(pick_up_date)
                d2 = datetime.fromisoformat(drop_off_date)
                days = (d2 - d1).days
                if days < 0:
                    flash('Drop-off must be after pick-up date.', 'danger')
                    return redirect(url_for('reserve'))
                if days == 0:
                    days = 1

                # Check car exists and is available
                cur.execute("SELECT daily_rate, status FROM cars WHERE car_id = %s", (car_id,))
                car_row = cur.fetchone()
                if not car_row:
                    flash('Selected car not found.', 'danger')
                    return redirect(url_for('reserve'))
                daily_rate, status = car_row
                if status != 'available':
                    flash('Selected car is not available.', 'danger')
                    return redirect(url_for('reserve'))

                total_cost = float(daily_rate) * days

                # Insert reservation
                cur.execute("""
                    INSERT INTO reservations (user_id, car_id, pickup_location, dropoff_location, payment_id, pick_up_date, drop_off_date, total_cost, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING reservation_id;
                """, (user_id, car_id, pickup_location, dropoff_location, payment_id, pick_up_date, drop_off_date, total_cost, 'pending'))
                res_id = cur.fetchone()[0]

                # Optional: mark car unavailable
                cur.execute("UPDATE cars SET status = %s WHERE car_id = %s", ('unavailable', car_id))

                conn.commit()
                flash(f'Reservation {res_id} created. Total: ${total_cost:.2f}', 'success')
                return redirect(url_for('manage_reservations'))

            except Exception as e:
                conn.rollback()
                print('Error creating reservation:', e)
                flash('There was an error creating your reservation. Please try again.', 'danger')
                return redirect(url_for('reserve'))

        # GET request: show the reservation form
        return render_template('reserve.html')  # ✅ Must return something

    except Exception as e:
        conn.rollback()
        print('Unexpected error in reserve:', e)
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('reserve'))

    finally:
        # Close cursor and connection
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

    

# Cancel Reservation
# -------------------------------------------------------------------------
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

@app.route('/manage_reservations', methods=['GET'])
def manage_reservations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT reservation_id, reservation_id as reservation_code, pick_up_date, drop_off_date, pickup_location, dropoff_location, car_id, total_cost, status
        FROM \"Reservations\"
        ORDER BY reservation_id DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    reservations = [{
        "id": r[0],
        "code": r[1],
        "pick_up_date": r[2],
        "drop_off_date": r[3],
        "pickup_location": r[4],
        "dropoff_location": r[5],
        "car_id": r[6],
        "total_cost": r[7],
        "status": r[8]
    } for r in rows]

    return render_template('manage_reservations.html', reservations=reservations)

if __name__ == '__main__':
    app.run(debug=True)
