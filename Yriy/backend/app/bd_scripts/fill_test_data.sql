
INSERT INTO Users (user_id, user_name) VALUES
(1, 'ivan_ivanov'),
(2, 'petr_petrov');

COMMIT;

INSERT INTO Passport (passport_number, serial_number, birth_date, user_id) VALUES
('123456', '1234', '1990-05-15', 1),
('654321', '4321', '1985-10-20', 2);

COMMIT;


INSERT INTO Driver_license (date_of_issue, expiration_date, user_id) VALUES
('2015-06-10', '2025-06-10', 1),
('2018-03-15', '2028-03-15', 2);

COMMIT;


INSERT INTO Models (brand, model_name, power) VALUES
('Toyota', 'Camry', 180),
('Honda', 'Accord', 190);

COMMIT;


INSERT INTO Cars (mileage, licence, serial_number, buying_date, city, coordinates, model_id) VALUES
(50000, 'A123BC777', 'XTA21099912345678', '2018-01-10', 'Москва', 55.7558, 1),
(30000, 'B456DE999', 'JH4KA7660MC123456', '2020-05-15', 'Санкт-Петербург', 59.9343, 2);

COMMIT;

INSERT INTO Tariffs (price_per_minute, start_time, end_time, model_id) VALUES
(30, '2023-01-01 00:00:00', '2026-12-31 23:59:59', 1),
(10, '2023-01-01 00:00:00', '2026-12-31 23:59:59', 2);