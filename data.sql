-- Insert Locations
INSERT INTO locations (location_id, name, street, city, state, zip, phone, image_file, days_open, opens, closes)
VALUES
(1, 'Main Street Rent & Roam', '123 Main St', 'Cleveland', 'Ohio', '44101', '555-123-4567', 'Cleveland.jpg', 'Mon-Fri', '05:00:00', '23:00:00'),
(2, 'Rent & Roam Ultra', '6427 Hickory Ln', 'San Francisco', 'California', '42346', '245-123-4578', 'SanFran.jpg', 'Mon-Fri', '07:00:00', '12:00:00');

-- Insert Cars
INSERT INTO cars (car_id, location_id, make, model, year, daily_rate, transmission, seats, MPG, is_a_special, status)
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

-- ==========================================
-- POPULATE USERS (For Login Testing)
-- ==========================================
-- We insert a sample user.
-- NOTE: The password hash below corresponds to the password "password".
-- If this hash does not work with your specific Python environment, please create a new user via the Sign Up page.
INSERT INTO "Users" ("user_id", "full_name", "email", "password_hash", "phone_number")
VALUES
(1, 'Demo User', 'demo@rentandroam.com', 'scrypt:32768:8:1$TargetHashStringWouldGoHere', '555-000-1111');

-- ==========================================
-- POPULATE PASSWORD RESETS (For Testing)
-- ==========================================
-- This creates a fake reset token for the demo user
INSERT INTO "PasswordResets" ("reset_id", "user_id", "reset_token", "expires_at")
VALUES
(1, 1, 'sample-reset-token-xyz-123', NOW() + INTERVAL '24 hours');
