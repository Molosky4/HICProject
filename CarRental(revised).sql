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
CREATE TABLE "Locations"(
    "location_id" INTEGER NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "street" VARCHAR(150) NOT NULL,
    "city" VARCHAR(100) NOT NULL,
    "state" VARCHAR(50) NOT NULL,
    "postal_code" VARCHAR(20) NOT NULL,
    "phone_number" VARCHAR(20) NULL
);
ALTER TABLE
    "Locations" ADD PRIMARY KEY("location_id");
CREATE TABLE "Cars"(
    "car_id" INTEGER NOT NULL,
    "location_id" INTEGER NULL,
    "make" VARCHAR(50) NOT NULL,
    "model" VARCHAR(50) NOT NULL,
    "year" INTEGER NOT NULL,
    "license_plate" VARCHAR(20) NOT NULL,
    "daily_rate" DECIMAL(10, 2) NOT NULL,
    "status" VARCHAR(255) CHECK
        ("status" IN('')) NULL DEFAULT 'available'
);
ALTER TABLE
    "Cars" ADD PRIMARY KEY("car_id");
ALTER TABLE
    "Cars" ADD CONSTRAINT "cars_license_plate_unique" UNIQUE("license_plate");
CREATE TABLE "Reservations"(
    "reservation_id" INTEGER NOT NULL,
    "user_id" INTEGER NULL,
    "car_id" INTEGER NULL,
    "pickup_location" INTEGER NULL,
    "dropoff_location" INTEGER NULL,
    "payment_id" INTEGER NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "total_cost" DECIMAL(10, 2) NOT NULL,
    "status" VARCHAR(255) CHECK
        ("status" IN('')) NULL DEFAULT 'pending'
);

CREATE TABLE "Reviews" (
    "review_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "review" TEXT NOT NULL,
    PRIMARY KEY ("review_id"),
    CONSTRAINT "reviews_user_id_foreign" FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
);


ALTER TABLE
    "Reservations" ADD PRIMARY KEY("reservation_id");
ALTER TABLE
    "Reservations" ADD CONSTRAINT "reservations_pickup_location_foreign" FOREIGN KEY("pickup_location") REFERENCES "Locations"("location_id");
ALTER TABLE
    "Reservations" ADD CONSTRAINT "reservations_payment_id_foreign" FOREIGN KEY("payment_id") REFERENCES "PaymentInfo"("payment_id");
ALTER TABLE
    "Addresses" ADD CONSTRAINT "addresses_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("user_id");
ALTER TABLE
    "PaymentInfo" ADD CONSTRAINT "paymentinfo_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("user_id");
ALTER TABLE
    "Reservations" ADD CONSTRAINT "reservations_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("user_id");
ALTER TABLE
    "Reservations" ADD CONSTRAINT "reservations_car_id_foreign" FOREIGN KEY("car_id") REFERENCES "Cars"("car_id");
ALTER TABLE
    "Cars" ADD CONSTRAINT "cars_location_id_foreign" FOREIGN KEY("location_id") REFERENCES "Locations"("location_id");
ALTER TABLE
    "Reservations" ADD CONSTRAINT "reservations_dropoff_location_foreign" FOREIGN KEY("dropoff_location") REFERENCES "Locations"("location_id");