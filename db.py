import os
import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "user":     os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "db":       os.getenv("MYSQL_DB", "mcp_demo"),
    "charset":  "utf8mb4",
    "cursorclass": DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)
