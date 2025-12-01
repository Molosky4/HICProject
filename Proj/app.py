
from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session, abort
from config import get_connection
from datetime import datetime

# DB connection from config
app = Flask(__name__)
app.secret_key = 'dev-key-change-this'   # required for flash messages

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        rev = request.form.get('reviewSubmit')
        return render_template('index.html')
    return render_template('index.html')

@app.route('/locations', methods=['GET'])
def locations():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all locations (match lowercase table/column names)
    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image": r[4], "opens": r[5], "closes": r[6], "days_open": r[7]}
        for r in rows
    ]

    return render_template('locations.html', locations=locations)

@app.route('/search_locations', methods=['GET'])
def search_locations():
    # 1. Get the search term from the AJAX request
    query = request.args.get('q', '').lower()

    conn = get_connection()
    cur = conn.cursor()

    # 2. Fetch all necessary data for the query (lowercase columns)
    cur.execute("SELECT location_id, name, street, city, image_file, opens, closes, days_open FROM \"Locations\";")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    all_locations = [
        {"id": r[0], "name": r[1], "street": r[2], "city": r[3], "image": r[4], "opens": r[5], "closes": r[6], "days_open": r[7]}
        for r in rows
    ]

    # 3. Filter the data based on the query (case-insensitive)
    filtered_locations = [
        loc for loc in all_locations
        if query in (loc['name'] or '').lower() or query in (loc['city'] or '').lower() or query in (loc['street'] or '').lower()
    ]

    # 4. Render the partial HTML template with the filtered results
    return render_template('location_results.html', locations=filtered_locations)


@app.route('/locations/<int:location_id>')
def cars_at_location(location_id):
    conn = get_connection()
    cur = conn.cursor()

    # Use lowercase table and column names; mpg and is_a_special are lowercase
    cur.execute("""
        SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status
        FROM \"Cars\"
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


@app.route('/search_cars', methods=['GET'])
def search_cars():
    query = request.args.get('q', '').lower()
    location_id = request.args.get('location_id')

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT car_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status
        FROM \"Cars\"
        WHERE location_id = %s;
    """, (location_id,))

    cars = cur.fetchall()
    cur.close()
    conn.close()

    cars = [
         {"id": car[0], "make": car[1], "model": car[2], "year": car[3], "rate": car[4], "transmission": car[5],
           "seats": car[6], "MPG": car[7], "special": car[8], "status": car[9]}
        for car in cars
    ]

    filtered_cars = [
        car for car in cars
        if query in (car['model'] or '').lower()
    ]

    return render_template('car_results.html', carsAtLocation=filtered_cars)


# --- Manage Reservations & Specials routes ---
@app.route('/manage_reservations', methods=['GET'])
def manage_reservations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT reservation_id, reservation_id as reservation_code, pick_up_date, drop_off_date, pickup_location, dropoff_location, car_id, total_cost, status
        FROM \"Reservations"\
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


@app.route('/reservation/cancel/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE reservations SET status = %s WHERE reservation_id = %s;", ('cancelled', reservation_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('manage_reservations'))


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


@app.route('/specials', methods=['GET'])
def specials():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT special_id, title, description, valid_until, discount, image_path FROM "Specials"  ORDER BY special_id;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    specials = [{
        "id": r[0],
        "title": r[1],
        "description": r[2],
        "valid_until": r[3],
        "discount": r[4],
        "image": r[5]
    } for r in rows]
    return render_template('specials.html', specials=specials)







@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    conn = get_connection()
    cur = conn.cursor()
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

            # Check car exists and is available, and get rate
            cur.execute("SELECT daily_rate, status FROM \"Cars\" WHERE car_id = %s", (car_id,))
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
        finally:
            cur.close()
            conn.close()

    # GET: prepare dropdown data
    cur.execute("SELECT user_id, full_name FROM \"Users\" ORDER BY user_id;")

    users = cur.fetchall()
    cur.execute("SELECT car_id, make, model, year, daily_rate FROM \"Cars\" ORDER BY car_id;")
    cars = cur.fetchall()
    cur.execute("SELECT location_id, name FROM \"Locations\" ORDER BY location_id;")
    locations = cur.fetchall()
    cur.execute("SELECT payment_id, payment_type FROM \"PaymentInfo\" ORDER BY payment_id;")
    payments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('reserve.html', users=users, cars=cars, locations=locations, payments=payments)



if __name__ == '__main__':
    app.run(debug=True)
