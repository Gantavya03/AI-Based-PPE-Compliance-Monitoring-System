import mysql.connector
import os

from database.db_config import DB_CONFIG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_connection():

    return mysql.connector.connect(
        **DB_CONFIG
    )


def get_total_violations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM violations")

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_today_violations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM violations
        WHERE DATE(timestamp) = DATE('now')
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_unique_workers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT track_id)
        FROM violations
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_violation_types():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT violation_type, COUNT(*)
        FROM violations
        GROUP BY violation_type
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def get_recent_violations(limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,
           violation_type,
           timestamp,
           screenshot,
           acknowledged,
           reset_done,
           alarm_active
                         
    FROM violations
    ORDER BY id DESC
                   
    LIMIT %s
""", (limit,))

    data = cursor.fetchall()

    conn.close()

    return data