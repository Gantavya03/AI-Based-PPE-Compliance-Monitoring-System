import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def alarm_is_active():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM violations
        WHERE alarm_active = 1
    """)

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count > 0

def acknowledge_all_alarms():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE violations
        SET acknowledged = 1,
            alarm_active = 0
        WHERE alarm_active = 1
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("All alarms acknowledged")
