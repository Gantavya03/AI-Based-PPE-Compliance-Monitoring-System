import mysql.connector 
import os

from datetime import datetime

from database.db_config import DB_CONFIG

class DatabaseManager:

    def __init__(self):

    

        # -----------------------------
        # CONNECT DATABASE
        # -----------------------------

        self.conn = mysql.connector.connect(
            **DB_CONFIG
        ) 

        self.cursor = self.conn.cursor()

        # create table
        self.create_table()

    # -----------------------------
    # CREATE TABLE
    # -----------------------------

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (

            id INT AUTO_INCREMENT PRIMARY KEY,

            track_id INT,

            violation_type VARCHAR(255),

            timestamp DATETIME,

            screenshot TEXT,
                            
            acknowledged INT DEFAULT 0,

            reset_done INT DEFAULT 0,

            alarm_active INT DEFAULT 1
        )
        """)

        self.conn.commit()

    # -----------------------------
    # INSERT VIOLATION
    # -----------------------------

    def insert_violation(
        self,
        track_id,
        violation_type,
        screenshot
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.cursor.execute("""
        INSERT INTO violations (

            track_id,
            violation_type,
            timestamp,
            screenshot,
            acknowledged,
            reset_done,
            alarm_active

        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (

            track_id,
            violation_type,
            timestamp,
            screenshot,
            0,
            0,
            1

        ))

        self.conn.commit()

        print(
            f"[DB] Inserted: "
            f"{track_id} | "
            f"{violation_type}"
        )
    
    def clear_all_violations(self):
        
        query = "DELETE FROM violations"
        
        self.cursor.execute(query)
        
        self.conn.commit()

    # -----------------------------
    # CLOSE DATABASE
    # -----------------------------

    def close(self):

        self.conn.close()