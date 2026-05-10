import psycopg2
import psycopg2.pool
import os

print(os.getenv("DATABASE_URL"))

pool = psycopg2.pool.SimpleConnectionPool(
    1,
    10,
    dsn=os.getenv('DATABASE_URL')
)

def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)