CREATE TABLE "Users" (
    "user_id" INTEGER PRIMARY KEY,
    "full_name" VARCHAR(50),
    "email" VARCHAR(50) UNIQUE,
    "password" VARCHAR(20)
);

CREATE TABLE "Addresses" (
    "address_id" INTEGER PRIMARY KEY,
    "user_id" INTEGER,
    "street" VARCHAR(50),
    "city" VARCHAR(20),
    "state" VARCHAR(15),
    "postal_code" VARCHAR(7),
    "country" VARCHAR(30),
    FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE "PaymentInfo" (
    "payment_id" INTEGER PRIMARY KEY,
    "user_id" INTEGER,
    "card_number" VARCHAR(20),
    "expiration_date" DATE,
    "cvv" INTEGER,
    FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);

CREATE TABLE "Locations" (
    "location_id" INTEGER PRIMARY KEY,
    "location_name" VARCHAR(50),
    "street" VARCHAR(50),
    "city" VARCHAR(30),
    "state" VARCHAR(20),
    "postal_code" VARCHAR(7),
    "phone_number" VARCHAR(15),
    "location_image" VARCHAR(255), -- store image associated with location
    "days_open" VARCHAR(255),
    "open_time" TIME,
    "close_time" TIME
);

CREATE TABLE "Cars" (
    "car_id" INTEGER PRIMARY KEY,
    "location_id" INTEGER,
    "make" VARCHAR(20),
    "model" VARCHAR(20),
    "year" INTEGER,
    "daily_rate" DECIMAL(10, 2), -- daily rate can include 10 digits. only 2 digits after decimal point
    "transmission" VARCHAR(20),
    "seats" INTEGER,
    "MPG" INTEGER,
    "is_a_special" BOOLEAN DEFAULT FALSE,
    "status" VARCHAR(15) DEFAULT 'available'
        CHECK ("status" IN ('available','unavailable')),
    FOREIGN KEY ("location_id") REFERENCES "Locations"("location_id")
);

CREATE TABLE "Reservations" (
    "reservation_id" INTEGER PRIMARY KEY,
    "user_id" INTEGER,
    "car_id" INTEGER,
    "pickup_location" INTEGER,
    "dropoff_location" INTEGER,
    "payment_id" INTEGER,
    "pick_up_date" DATE,
    "drop_off_date" DATE,
    "total_cost" DECIMAL(100, 2),
    "status" VARCHAR(255) DEFAULT 'pending'
        CHECK ("status" IN ('pending','confirmed','cancelled')),
    FOREIGN KEY ("user_id") REFERENCES "Users"("user_id"),
    FOREIGN KEY ("car_id") REFERENCES "Cars"("car_id"),
    FOREIGN KEY ("pickup_location") REFERENCES "Locations"("location_id"),
    FOREIGN KEY ("dropoff_location") REFERENCES "Locations"("location_id"),
    FOREIGN KEY ("payment_id") REFERENCES "PaymentInfo"("payment_id")
);
