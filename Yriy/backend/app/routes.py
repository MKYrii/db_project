from datetime import datetime
from typing import Optional

from .database import engine
from sqlalchemy import text
from fastapi import APIRouter, Body
from .services import get_tables
from datetime import datetime
from typing import List, Optional
from math import ceil
from datetime import date, timedelta

router = APIRouter()


@router.get('/fill_test_data')
async def fill_test_data():
    try:
        with open('app/bd_scripts/fill_test_data.sql', 'r') as file:
            sql_script = text(file.read())
            try:
                with engine.connect() as connection:
                    connection.execute(sql_script)
                    test_data = connection.execute(text("SELECT * from models")).fetchall()
                    if 'Toyota' == test_data[0][1]:
                        connection.commit()
                        return {'message': 'Completed'}
                    else:
                        return {'message': 'Something went wrong'}
            except Exception as e:
                return {'message': 'ошибка при работе с бд: {}'.format(e)}
    except Exception as e:
        return {'message': 'ошибка при работе с файлом: {}'.format(e)}


@router.get('/clear_all_tables')
async def clear_all_tables():
    try:
        with engine.connect() as conn:
            tables = get_tables(conn)
            for table in tables:
                conn.execute(text(f'TRUNCATE TABLE {table[0]} RESTART IDENTITY CASCADE'))

            conn.commit()
            return {"message": f"All tables cleared successfully ({len(tables)} tables)"}
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.get('/get_all_data')
async def get_all_data():
    try:
        with engine.connect() as conn:
            tables = get_tables(conn)
            ans = {}
            for table in tables:
                ans[table[0]] = str(conn.execute(text(f'SELECT * FROM {table[0]}')).fetchall())
            return ans
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.post('/post_sql')
async def post_sql(sql_query: str):
    try:
        with engine.connect() as conn:
            conn.execute(text(sql_query))
            conn.commit()
            return {'message': 'Successfully'}
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.get('/get_sql')
async def get_sql(sql_query: str):
    try:
        with engine.connect() as conn:
            res = str(conn.execute(text(sql_query)).fetchall())
            return res
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


     
@router.get('/install_triggers')
async def install_triggers():
    """Установка триггерных функций"""
    try:
        with engine.connect() as conn:
            existing = conn.execute(text("""
                    SELECT tgname FROM pg_trigger 
                    WHERE tgname IN (
                        'trg_validate_car_date',
                        'trg_check_driver_license',
                        'trg_validate_trip_end_time')
                """)).fetchall()
            if existing:
                return {
                    "message": "Некоторые триггеры уже существуют",
                    "existing": [row[0] for row in existing]
                }
        with open('app/bd_scripts/triggers.sql', 'r') as file:
            sql_script = text(file.read())
            with engine.connect() as conn:
                conn.execute(sql_script)
                conn.commit()
        return {"message": "Триггерные функции успешно установлены"}
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.get("/remove_triggers")
async def remove_triggers():
    """Удаление триггерных функций"""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                DROP TRIGGER IF EXISTS trg_validate_car_date ON cars;
                DROP TRIGGER IF EXISTS trg_check_driver_license ON trip;
                DROP TRIGGER IF EXISTS trg_validate_trip_end_time ON trip;
            """))

            conn.execute(text("""
                DROP FUNCTION IF EXISTS validate_car_date();
                DROP FUNCTION IF EXISTS check_driver_license();
                DROP FUNCTION IF EXISTS validate_trip_end_time();
            """))

        return {"message": "Триггерные функции успешно удалены"}

    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.post("/add_trip")
async def add_trip(
        car_id: int,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        end_coords: Optional[str] = None,
        problems: Optional[str] = None,
        comments: Optional[str] = None,
        end_city: Optional[str] = None,
):
    """
    Добавляет новую поездку в базу данных и обновляет местоположение автомобиля.

    Параметры:
    - car_id: ID автомобиля
    - user_id: ID пользователя
    - problems: Описание проблем (если были)
    - comments: Комментарии к поездке
    - start_time: Время начала поездки
    - end_time: Время окончания поездки
    - end_coords: Координаты, где закончилась поездка

    Возвращает:
    - Сообщение об успешном добавлении или ошибку
    """
    coords_query = text(f"SELECT coordinates FROM cars WHERE car_id = {car_id}")

    trip_query = text("""
        INSERT INTO Trip (start_time, end_time, problems, comments, car_id, user_id)
        VALUES (:start_time, :end_time, :problems, :comments, :car_id, :user_id)
    """)

    car_query = text("""
        UPDATE Cars 
        SET coordinates = :coordinates, mileage = mileage + :distance 
        WHERE car_id = :car_id
    """)
    end_coords = list(map(float, end_coords.split(',')))
    if end_city:
        car_query = text("""
                UPDATE Cars 
                SET coordinates = :coordinates, city = :end_city, mileage = mileage + :distance
                WHERE car_id = :car_id
            """)

    payment_query = text("""
        INSERT INTO Payment (description, value, date, deadline, type, user_id)
        VALUES (
            'оплата поездки',
            (
                SELECT t.price_per_minute * EXTRACT(EPOCH FROM (:end_time - :start_time)) / 60
                FROM Cars c
                JOIN Tariffs t ON t.model_id = c.model_id
                WHERE c.car_id = :car_id
                  AND t.start_time <= :start_time
                  AND t.end_time >= :end_time
                LIMIT 1
            ),
            :date,
            :deadline,
            'trip',
            :user_id
        )
    """)

    try:
        with engine.begin() as conn:
            conn.execute(
                trip_query,
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "problems": problems,
                    "comments": comments,
                    "car_id": car_id,
                    "user_id": user_id
                }
            )
            prev_coords = float(conn.execute(coords_query).fetchall()[0][0])

            coordinates = float(end_coords[0])
            dist = int(ceil(abs(prev_coords - coordinates) * 111))
            conn.execute(
                car_query,
                {
                    "coordinates": coordinates,
                    "car_id": car_id,
                    "end_city": end_city,
                    "distance": dist
                }
            )

            conn.execute(
                payment_query,
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "car_id": car_id,
                    "date": date.today(),
                    "deadline": date.today() + timedelta(days=3),
                    "user_id": user_id
                }
            )
            conn.commit()

        return {"message": "Поездка успешно добавлена"}

    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.get('/show_user_trips')
async def show_user_trips(user_id: int):
    try:
        with engine.begin() as conn:
            query = text("""
            SELECT trip_id, start_time, end_time, problems, comments, car_id, user_id FROM Trip
            WHERE user_id = :user_id;
            """)
            return str(conn.execute(query, {"user_id": user_id}).fetchall())
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.get('/show_user_payments')
async def show_user_payments(user_id: int):
    try:
        with engine.begin() as conn:
            query = text("""
            SELECT pay_id, description, "value", "date", deadline, type, user_id FROM Payment
            WHERE user_id = :user_id;
            """)
            return str(conn.execute(query, {"user_id": user_id}).fetchall())
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


@router.get('/show_car_repairs')
async def show_car_repairs(car_id: int):
    try:
        with engine.begin() as conn:
            query = text("""
            SELECT repair_id, description, datetime, car_id FROM Repairs
            WHERE car_id = :car_id;
            """)
            return str(conn.execute(query, {"car_id": car_id}).fetchall())
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}


from datetime import datetime
from sqlalchemy import text  # Добавьте этот импорт


@router.post('/add_repair')
async def add_repair(car_id: int, description: str, date_time: datetime):
    try:
        with engine.begin() as conn:
            query = text("""
                INSERT INTO Repairs (car_id, description, datetime)
                VALUES (:car_id, :description, :date_time)
            """)
            conn.execute(query, {
                "car_id": car_id,
                "description": description,
                "date_time": date_time
            })
            conn.commit()
        return {'message': 'Repair added successfully'}
    except Exception as e:
        return {'message': f'Something went wrong: {str(e)}'}