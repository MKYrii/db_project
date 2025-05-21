from .database import engine
from sqlalchemy import text
from fastapi import APIRouter
from .services import get_tables

router = APIRouter()


@router.get('/fill_test_data')
async def fill_test_data():
    try:
        with open('app/bd_scripts/fill_test_data.sql', 'r') as file:
            sql_script = text(file.read())
            try:
                with engine.connect() as connection:
                    check_data = connection.execute(text("SELECT * FROM Users")).fetchall()
                    if 'ivan_ivanov' == check_data[0][1]:
                        return {'message': 'Data already exists'}
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
async def push(sql_query: str):
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
