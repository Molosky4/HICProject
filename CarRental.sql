CREATE TABLE "Users"(
    "user_id" INTEGER NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "phone_number" VARCHAR(20) NULL
);
ALTER TABLE
    "Users" ADD PRIMARY KEY("user_id");
ALTER TABLE
    "Users" ADD CONSTRAINT "users_email_unique" UNIQUE("email");
CREATE TABLE "Addresses"(
    "address_id" INTEGER NOT NULL,
    "user_id" INTEGER NULL,
    "street" VARCHAR(150) NOT NULL,
    "city" VARCHAR(100) NOT NULL,
    "state" VARCHAR(50) NOT NULL,
    "postal_code" VARCHAR(20) NOT NULL,
    "country" VARCHAR(50) NOT NULL
);
ALTER TABLE
    "Addresses" ADD PRIMARY KEY("address_id");
CREATE TABLE "PaymentInfo"(
    "payment_id" INTEGER NOT NULL,
    "user_id" INTEGER NULL,
    "card_number" VARCHAR(20) NOT NULL,
    "card_holder_name" VARCHAR(100) NOT NULL,
    "expiration_date" DATE NOT NULL,
    "billing_address" VARCHAR(150) NULL
);
ALTER TABLE
    "PaymentInfo" ADD PRIMARY KEY("payment_id");

ALTER TABLE "PaymentInfo"
ADD COLUMN "payment_type" VARCHAR(50) NULL;


CREATE TABLE "Reviews" (
    "review_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "review" TEXT NOT NULL,
    PRIMARY KEY ("review_id"),
    CONSTRAINT "reviews_user_id_foreign" FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);


CREATE TABLE "Locations" (
    "location_id" INTEGER PRIMARY KEY,
    "name" VARCHAR(50),
    "street" VARCHAR(50),
    "city" VARCHAR(30),
    "state" VARCHAR(20),
    "zip" VARCHAR(7),
    "phone" VARCHAR(15),
    "image_file" VARCHAR(255), -- store image associated with location
    "days_open" VARCHAR(255),
    "opens" TIME,
    "closes" TIME
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

CREATE TABLE "Specials" (
    special_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    valid_until DATE NOT NULL,
    discount NUMERIC(5,2) NOT NULL,
    image_path VARCHAR(255)
);

ALTER TABLE "Addresses" 
    ADD CONSTRAINT "addresses_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("user_id");

ALTER TABLE "PaymentInfo" 
    ADD CONSTRAINT "paymentinfo_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("user_id");

