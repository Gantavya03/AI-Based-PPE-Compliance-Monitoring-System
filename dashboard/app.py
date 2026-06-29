import sys
import os
import cv2
import threading

from flask import Flask, render_template, Response, redirect 


# ==========================================
# ADD SRC PATH
# ==========================================

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..'
        )
    )
)







# ==========================================
# IMPORT DATABASE ANALYTICS
# ==========================================

from database.analytics import *
from database.database_manager import DatabaseManager

# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)

db = DatabaseManager()



# ==========================================
# DASHBOARD ROUTE
# ==========================================

@app.route("/")

def dashboard():

    total = get_total_violations()

    today = get_today_violations()

    workers = get_unique_workers()

    violation_types = get_violation_types()

    recent = get_recent_violations()

    helmet = 0

    vest = 0

    for item in violation_types:

        violation_name = item[0]

        count = item[1]

        if "helmet" in violation_name.lower():
            helmet += count

        if "vest" in violation_name.lower():
            vest += count

    screenshot_folder = os.path.join(
        app.static_folder,
        'screenshots'
    )

    images = []

    if os.path.exists(screenshot_folder):

        images = sorted(
            os.listdir(screenshot_folder),
            reverse=True
        )[:8]

    return render_template(

        "dashboard.html",

        total=total,
        today=today,
        workers=workers,

        helmet=helmet,
        vest=vest,

        violation_types=violation_types,

        recent=recent,

        rows=recent,

        images=images
    )

# ==========================================
# ACKNOWLEDGE VIOLATION
# ==========================================

@app.route("/ack")

def acknowledge_violation():
    
    print("ACKNOWLEDGE ALL CLICKED")

    query = """
    UPDATE violations
    SET acknowledged = 1,
        alarm_active = 0
    WHERE acknowledged = 0
    """

    db.cursor.execute(query)

    db.conn.commit()

    print("ALL ACTIVE VIOLATIONS ACKNOWLEDGED")

    return redirect("/")



# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=False,
        host="0.0.0.0",
        port=5001,
        threaded=True
    )