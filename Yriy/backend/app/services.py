from sqlalchemy import text
from sqlalchemy import Connection

def get_tables(connection: Connection):
    tables = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                """)).fetchall()
    return tables


