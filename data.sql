-- Insert Locations
INSERT INTO "Locations" (location_id, name, street, city, state, zip, phone, image_file, days_open, opens, closes)
VALUES
(1, 'Main Street Rent & Roam', '123 Main St', 'Cleveland', 'Ohio', '44101', '555-123-4567', 'Cleveland.jpg', 'Mon-Fri', '05:00:00', '23:00:00'),
(2, 'Rent & Roam Ultra', '6427 Hickory Ln', 'San Francisco', 'California', '42346', '245-123-4578', 'SanFran.jpg', 'Mon-Fri', '07:00:00', '12:00:00');

-- Insert Cars
INSERT INTO "Cars" (car_id, location_id, make, model, year, daily_rate, transmission, seats, "MPG", is_a_special, status)
VALUES
(101, 1, 'Toyota', 'Corolla', 2023, 50.00, 'Automatic', 5, 35, FALSE, 'available'),
(102, 1, 'Toyota', 'Corolla', 2022, 45.00, 'Automatic', 5, 36, FALSE, 'available'),
(103, 2, 'Ford', 'Mustang', 2023, 89.99, 'Manual', 4, 22, TRUE, 'available'),
(104, 1, 'Ford', 'Mustang', 2023, 95.00, 'Automatic', 4, 22, TRUE, 'available'),
(105, 2, 'Chevrolet', 'Tahoe', 2022, 110.00, 'Automatic', 7, 18, FALSE, 'unavailable'),
(106, 1, 'Chevrolet', 'Tahoe', 2021, 95.50, 'Automatic', 7, 18, FALSE, 'unavailable'),
(107, 2, 'Ford', 'Mustang', 2023, 85.00, 'Automatic', 4, 25, TRUE, 'available'),
(108, 2, 'Toyota', 'Corolla', 2020, 40.00, 'Automatic', 5, 34, FALSE, 'available'),
(109, 1, 'Chevrolet', 'Tahoe', 2022, 100.00, 'Automatic', 7, 18, FALSE, 'available'),
(110, 1, 'Ford', 'Mustang', 2023, 120.00, 'Manual', 4, 20, TRUE, 'available');


-- Insert Users
INSERT INTO "Users" ("user_id", "full_name", "email", "password_hash", "phone_number")
VALUES
(1, 'John Doe', 'john@example.com', 'hashedpassword1', '555-111-2222'),
(2, 'Jane Smith', 'jane@example.com', 'hashedpassword2', '555-333-4444');

INSERT INTO "Reviews" (user_id, full_name, review)
VALUES
(1, 'John Doe', '10/10, greatest thing yet'),
(2, 'Jane Smith', 'Im with John');

-- Insert Addresses
INSERT INTO "Addresses" ("address_id", "user_id", "street", "city", "state", "postal_code", "country")
VALUES
(1, 1, '123 Main St', 'Cleveland', 'Ohio', '44101', 'USA'),
(2, 2, '6427 Hickory Ln', 'San Francisco', 'California', '42346', 'USA');

-- Insert Paymentinfo
INSERT INTO "PaymentInfo" ("payment_id", "user_id", "card_number", "card_holder_name", "expiration_date", "billing_address", "payment_type") 
VALUES 
(1, 1, '1111222233334444', 'John Doe', '2025-12-31', '123 Main St, Cleveland', 'Credit Card'),
(2, 2, '5555666677778888', 'Jane Smith', '2025-12-31', '6427 Hickory Ln, San Francisco', 'Debit Card');



-- Insert Reservations (after Users, Cars, Locations, PaymentInfo)
INSERT INTO "Reservations" ("reservation_id", "user_id", "car_id", "pickup_location", "dropoff_location", "payment_id", "pick_up_date", "drop_off_date", "total_cost", "status")
VALUES
(1, 1, 101, 1, 2, 1, '2025-11-28', '2025-11-30', 100.00, 'confirmed'),
(2, 2, 103, 2, 2, 2, '2025-12-01', '2025-12-03', 180.00, 'pending'),
(3, 1, 104, 1, 1, 1, '2025-12-05', '2025-12-07', 190.00, 'cancelled');

-- Insert Specials
INSERT INTO "Specials" ("title", "description", "valid_until", "discount", "image_path")
VALUES
('Holiday Special', '20% off all cars during holidays', '2025-12-31', 20.0, 'specials_holiday.jpg'),
('Weekend Special', '15% off SUVs on weekends', '2025-12-13', 15.0, 'specials_weekend.jpg'),
('Student Special', '10% off for students with valid ID', '2025-12-31', 10.0, 'specials_student.jpg');