from .database import engine
from sqlalchemy import text
from fastapi import APIRouter, Body
from .services import get_tables
from datetime import datetime
from typing import List, Optional
from math import ceil


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
                SET coordinates = :coordinates, city = :end_city
                WHERE car_id = :car_id
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

            coordinates = float(end_coords[0])
            conn.execute(
                car_query,
                {
                    "coordinates": coordinates,
                    "car_id": car_id,
                    "end_city": end_city,
                    "distance": 25
                }
            )
            conn.commit()

        return {"message": "Поездка успешно добавлена"}

    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(e)}