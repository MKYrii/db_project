
CREATE OR REPLACE FUNCTION validate_car_date()
RETURNS TRIGGER AS $psql$
BEGIN
    IF NEW.buying_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Дата покупки не может быть в будущем';
    ELSIF NEW.buying_date < '2010-01-01' THEN
        RAISE NOTICE 'Машина слишком старая (старше 2010 года)';
    END IF;
    RETURN NEW;
END;
$psql$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION check_driver_license()
RETURNS TRIGGER AS $psql$
DECLARE
    license_valid boolean;
BEGIN
    SELECT expiration_date > CURRENT_DATE INTO license_valid
    FROM driver_license
    WHERE user_id = NEW.user_id;

    IF NOT license_valid THEN
        RAISE EXCEPTION 'Срок действия водительских прав истек';
    END IF;
    RETURN NEW;
END;
$psql$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION validate_trip_end_time()
RETURNS TRIGGER AS $psql$
BEGIN
    IF NEW.end_time > CURRENT_TIMESTAMP THEN
        RAISE EXCEPTION 'Дата окончания поездки не может быть в будущем';
    END IF;
    RETURN NEW;
END;
$psql$ LANGUAGE plpgsql;


DO $$
BEGIN

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_validate_car_date') THEN
        CREATE TRIGGER trg_validate_car_date
        BEFORE INSERT OR UPDATE ON cars
        FOR EACH ROW EXECUTE FUNCTION validate_car_date();
    END IF;


    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_check_driver_license') THEN
        CREATE TRIGGER trg_check_driver_license
        BEFORE INSERT ON trip
        FOR EACH ROW EXECUTE FUNCTION check_driver_license();
    END IF;


    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_validate_trip_end_time') THEN
        CREATE TRIGGER trg_validate_trip_end_time
        BEFORE INSERT OR UPDATE ON trip
        FOR EACH ROW EXECUTE FUNCTION validate_trip_end_time();
    END IF;
END $$;


CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_car_id ON trips(car_id);

CREATE INDEX idx_payments_payment_time ON payments(payment_time);