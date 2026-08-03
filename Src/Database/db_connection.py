import psycopg2
from sqlalchemy import create_engine
from decouple import config
from urllib.parse import quote_plus
from contextlib import contextmanager





DB_NAME = "earthquake_db"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database_if_not_exists():

    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=config("DB_PASSWORD"),
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True 
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"Database '{DB_NAME}' created.")
    else:
        print(f"Database '{DB_NAME}' already exists.")

    cur.close()
    conn.close()


def get_connection():

    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=config("DB_PASSWORD"),
        host=DB_HOST,
        port=DB_PORT
    )


def get_engine():

    db_password = quote_plus(config("DB_PASSWORD"))
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{db_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


@contextmanager
def db_cursor():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()



if __name__ == '__main__':
    create_database_if_not_exists()

    with db_cursor() as cur:
        cur.execute("SELECT 1")
        print("psycopg2 connection: OK")

    engine = get_engine()
    with engine.connect() as test_conn:
        print("sqlalchemy engine: OK")