
CREATE TABLE IF NOT EXISTS Models (
    model_id SERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL CHECK (LENGTH(brand) > 0),
    model_name VARCHAR(50) NOT NULL CHECK (LENGTH(model_name) > 0),
    power INT NOT NULL CHECK (power > 0)
);


CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS Cars (
    car_id SERIAL PRIMARY KEY,
    mileage INT NOT NULL CHECK (mileage >= 0),
    licence VARCHAR(9) NOT NULL UNIQUE,
    serial_number VARCHAR(17),
    buying_date DATE NOT NULL,
    city VARCHAR(50),
    coordinates FLOAT NOT NULL,
    malfunctions TEXT,
    model_id INT NOT NULL REFERENCES Models(model_id)
);


CREATE TABLE IF NOT EXISTS Passport (
    passport_id SERIAL PRIMARY KEY,
    passport_number VARCHAR(6) NOT NULL UNIQUE,
    serial_number VARCHAR(4) NOT NULL,
    birth_date DATE NOT NULL,
    user_id INT NOT NULL REFERENCES Users(user_id)
);


CREATE TABLE IF NOT EXISTS Driver_license (
    license_id SERIAL PRIMARY KEY,
    date_of_issue DATE NOT NULL,
    expiration_date DATE NOT NULL CHECK (expiration_date > date_of_issue),
    user_id INT NOT NULL REFERENCES Users(user_id)
);


CREATE TABLE IF NOT EXISTS Repairs (
    repair_id SERIAL PRIMARY KEY,
    description TEXT,
    datetime TIMESTAMP NOT NULL,
    car_id INT NOT NULL REFERENCES Cars(car_id)
);


CREATE TABLE IF NOT EXISTS Payment (
    pay_id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    value FLOAT CHECK (value > 0),
    date DATE NOT NULL,
    deadline DATE NOT NULL CHECK (deadline > date),
    type VARCHAR(50),
    user_id INT NOT NULL REFERENCES Users(user_id)
);


CREATE TABLE IF NOT EXISTS Tariffs (
    tariff_id SERIAL PRIMARY KEY,
    price_per_minute INT CHECK (price_per_minute > 0),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL CHECK (end_time > start_time),
    model_id INT NOT NULL REFERENCES Models(model_id)
);


CREATE TABLE IF NOT EXISTS Trip (
    trip_id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL CHECK (end_time > start_time),
    problems TEXT,
    comments TEXT,
    car_id INT NOT NULL REFERENCES Cars(car_id),
    user_id INT NOT NULL REFERENCES Users(user_id)
);