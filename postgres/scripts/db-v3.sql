-- Veritabanlarını oluştur
CREATE DATABASE cars;
GRANT ALL PRIVILEGES ON DATABASE cars TO program;

CREATE DATABASE rentals;
GRANT ALL PRIVILEGES ON DATABASE rentals TO program;

CREATE DATABASE payments;
GRANT ALL PRIVILEGES ON DATABASE payments TO program;

-- Cars Veritabanı Tabloları ve İzinler
\connect cars
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    car_uid UUID UNIQUE NOT NULL,
    brand VARCHAR(80) NOT NULL,
    model VARCHAR(80),
    registration_number VARCHAR(20) NOT NULL,
    power INT,
    price INT NOT NULL,
    type VARCHAR(20),
    CHECK (type IN ('SEDAN', 'SUV', 'MINIVAN', 'ROADSTER')),
    availability BOOLEAN NOT NULL
);

INSERT INTO cars (car_uid, brand, model, registration_number, power, price, type, availability)
VALUES 
('109b42f3-198d-4c89-9276-a7520a7120ab', 'Mercedes Benz', 'GLA 250', 'ЛО777Х799', 249, 3500, 'SEDAN', true);

-- Kullanıcıya cars tablosu üzerinde gerekli izinleri ver
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE cars TO program;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO program;

-- Rentals Veritabanı Tabloları ve İzinler
CREATE TABLE IF NOT EXISTS rental (
    id SERIAL PRIMARY KEY,
    rental_uid UUID UNIQUE NOT NULL,
    username VARCHAR(80) NOT NULL,
    payment_uid UUID NOT NULL,
    car_uid UUID NOT NULL,
    date_from TIMESTAMP WITH TIME ZONE NOT NULL,
    date_to TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('IN_PROGRESS', 'FINISHED', 'CANCELED')),
    FOREIGN KEY (car_uid) REFERENCES cars(car_uid) ON DELETE CASCADE,
    FOREIGN KEY (payment_uid) REFERENCES payments(payment_uid) ON DELETE CASCADE
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE rental TO program;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO program;

-- Payments Veritabanı Tabloları ve İzinler
\connect payments
CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    payment_uid UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    CHECK (status IN ('PAID', 'CANCELED')),
    price INT NOT NULL
);

-- Kullanıcıya payment tablosu üzerinde gerekli izinleri ver
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE payment TO program;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO program;
