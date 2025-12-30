import mysql.connector
import os

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "vexuser"),
        password=os.getenv("DB_PASS", "vexpass"),
        database=os.getenv("DB_NAME", "vex"),
    )
