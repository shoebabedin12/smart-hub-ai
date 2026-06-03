import os
import pymysql
from pymysql.cursors import DictCursor
from urllib.parse import urlparse

# DATABASE_URL পার্স করা (mysql+pymysql://user:password@host:port/db)
url_str = os.getenv('DATABASE_URL')
# 'mysql+pymysql' কে স্ট্যান্ডার্ড 'mysql' দিয়ে রিপ্লেস করা পার্স করার সুবিধার জন্য
if url_str.startswith("mysql+pymysql://"):
    url_str = url_str.replace("mysql+pymysql://", "mysql://")

url = urlparse(url_str)

DB_CONFIG = {
    'host': url.hostname or 'localhost',
    'port': url.port or 3306,
    'user': url.username or 'root',
    'password': url.password or '',
    'database': url.path.lstrip('/'),
    'cursorclass': DictCursor, # এর ফলে ডেটাবেজের রেজাল্ট ডিকশনারি/অবজেক্ট আকারে আসবে
    'autocommit': True
}

def get_conn():
    """নতুন একটি MySQL কানেকশন তৈরি করে রিটার্ন করবে"""
    return pymysql.connect(**DB_CONFIG)

def release_conn(conn):
    """কানেকশন বন্ধ করার জন্য"""
    if conn:
        conn.close()