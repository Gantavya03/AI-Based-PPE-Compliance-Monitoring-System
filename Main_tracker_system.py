# ==========================================
# FILE: src/Main_tracker_system.py
# ==========================================

from ultralytics import YOLO
import supervision as sv
import cv2
import time
import os
import numpy as np

from violations.alert_manager import AlertManager
from association.smart_association import PPEAssociator
from database.database_manager import DatabaseManager




# ==========================================
# LOAD MODEL
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

model = YOLO(MODEL_PATH)

# ==========================================
# INITIALIZE TRACKER
# ==========================================

tracker = sv.ByteTrack(

    track_activation_threshold=0.2,

    lost_track_buffer=600,

    minimum_matching_threshold=0.85,

    frame_rate=30
)

# ==========================================
# INITIALIZE ASSOCIATOR
# ==========================================

associator = PPEAssociator()

# ==========================================
# OPEN CAMERA
# ==========================================

cap = cv2.VideoCapture(0)

# ==========================================
# CREATE SCREENSHOT FOLDER
# ==========================================

save_dir = "dashboard/static/screenshots"

os.makedirs(save_dir, exist_ok=True)

# ==========================================
# CLEAR OLD SCREENSHOTS
# ==========================================

for file in os.listdir(save_dir):

    file_path = os.path.join(save_dir, file)

    try:
        os.remove(file_path)

    except:
        pass

# ==========================================
# ALERT MANAGER
# ==========================================

alert_manager = AlertManager()

# ==========================================
# DATABASE
# ==========================================

db = DatabaseManager()

db.clear_all_violations()

already_logged = set()

# ==========================================
# MAIN TRACKER FUNCTION
# ==========================================

def run_tracker():

    

    while True:

        ret, frame = cap.read()

        frame = cv2.resize(frame, (640, 480))

        if not ret:
            break

        current_time = time.time()

        # ==========================================
        # RUN YOLO MODEL
        # ==========================================

        results = model(
            frame,
            conf=0.5,
            imgsz=416
        )[0]

        # ==========================================
        # CONVERT DETECTIONS
        # ==========================================

        detections = sv.Detections.from_ultralytics(results)

        # ==========================================
        # STORE DETECTIONS
        # ==========================================

        person_detections = []

        ppe_detections = []

        # ==========================================
        # PROCESS DETECTIONS
        # ==========================================

        for i in range(len(detections)):

            class_id = detections.class_id[i]

            class_name = model.names[class_id]

            box = detections.xyxy[i]

            confidence = detections.confidence[i]

            x1, y1, x2, y2 = map(int, box)

            # ==========================================
            # PERSON DETECTION
            # ==========================================

            if class_name == "Person":

                width = x2 - x1

                height = y2 - y1

                # ignore tiny detections
                if width < 150 or height < 250:
                    continue

                person_detections.append({

                    "box": [x1, y1, x2, y2],

                    "confidence": confidence
                })

            # ==========================================
            # PPE VIOLATIONS
            # ==========================================

            elif class_name == "NO-Hardhat":

                ppe_detections.append({

                    "class": "no_helmet",

                    "box": [x1, y1, x2, y2]
                })

            elif class_name == "NO-Safety Vest":

                ppe_detections.append({

                    "class": "no_vest",

                    "box": [x1, y1, x2, y2]
                })

        # ==========================================
        # CREATE PERSON DETECTIONS
        # ==========================================

        if len(person_detections) > 0:

            person_boxes = []

            person_confidences = []

            person_class_ids = []

            for person in person_detections:

                person_boxes.append(person["box"])

                person_confidences.append(person["confidence"])

                person_class_ids.append(0)

            person_sv_detections = sv.Detections(

                xyxy=np.array(person_boxes),

                confidence=np.array(person_confidences),

                class_id=np.array(person_class_ids)
            )

        else:

            person_sv_detections = sv.Detections.empty()

        # ==========================================
        # TRACK PERSONS
        # ==========================================

        person_sv_detections = tracker.update_with_detections(
            person_sv_detections
        )

        # ==========================================
        # PREPARE TRACKED PERSONS
        # ==========================================

        tracked_persons = []

        for i in range(len(person_sv_detections)):

            tracker_id = int(
                person_sv_detections.tracker_id[i]
            )

            box = person_sv_detections.xyxy[i]

            x1, y1, x2, y2 = map(int, box)

            tracked_persons.append({

                "id": tracker_id,

                "box": [x1, y1, x2, y2]
            })

        # ==========================================
        # SMART ASSOCIATION
        # ==========================================

        association_results = associator.associate(

            tracked_persons,

            ppe_detections
        )

        # ==========================================
        # PROCESS EACH TRACKED PERSON
        # ==========================================

        for person in tracked_persons:

            tracker_id = person["id"]

            x1, y1, x2, y2 = person["box"]

            # ==========================================
            # GET ASSOCIATION RESULTS
            # ==========================================

            result = association_results[tracker_id]

            no_helmet = result["no_helmet"]

            no_vest = result["no_vest"]

            # ==========================================
            # STATUS TEXT
            # ==========================================

            status = []

            if no_helmet:
                status.append("No Helmet")

            if no_vest:
                status.append("No Vest")

            # ==========================================
            # COLORS
            # ==========================================

            if len(status) == 0:

                status_text = "PPE OK"

                color = (0, 255, 0)

            else:

                status_text = " | ".join(status)

                color = (0, 0, 255)

            # ==========================================
            # ALERT MANAGER
            # ==========================================

            trigger_alert, confirmed_alerts = (

                alert_manager.update(

                    tracker_id,

                    no_helmet,

                    no_vest
                )
            )

            # ==========================================
            # CONFIRMED ALERT
            # ==========================================

            if no_helmet or no_vest:

                print(
                    f"CONFIRMED ALERT : "
                    f"Person {tracker_id} : "
                    f"{confirmed_alerts}"
                )


                # ==========================================
                # SAVE TO DATABASE
                # ==========================================

                for violation in confirmed_alerts:
                    key = f"{tracker_id}_{violation}"

                    if key not in already_logged:
                        
                        
                        # ==========================================
                        # SAVE SCREENSHOT
                        # ==========================================
                     
                        filename = (
                            f"person_"
                        
                            f"{tracker_id}_"
                        
                            f"{int(current_time)}.jpg"
                        )
                    
                        full_path = os.path.join(
                            save_dir,
                            filename
                        )
                    
                        cv2.imwrite(full_path, frame)
                    
                        print(
                            f"Screenshot Saved : "
                            f"{full_path}"
                        )

                        # ==========================================
                        # LOG ONLY ONCE PER PERSON
                        # ==========================================

                    
                        db.insert_violation(
                            tracker_id,
                            violation,
                            full_path
                        )
                        
                        already_logged.add(key)
                        
                        print(
                            f"Violation Logged Once : "
                            f"{key}"
                        )

            # ==========================================
            # DRAW PERSON BOX
            # ==========================================

            cv2.rectangle(

                frame,

                (x1, y1),

                (x2, y2),

                color,

                2
            )

            # ==========================================
            # LABEL
            # ==========================================

            label = (

                f"Person {tracker_id} : "

                f"{status_text}"
            )

            cv2.putText(

                frame,

                label,

                (x1, y1 - 10),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                color,

                2
            )

        

     

        
        # ==========================================
        # SHOW LIVE WINDOW
        # ==========================================

        cv2.imshow(
            "Tracked PPE System",
            frame
        )

        # ==========================================
        # PRESS Q TO EXIT
        # ==========================================

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

    # ==========================================
    # CLEANUP
    # ==========================================

    cap.release()

    cv2.destroyAllWindows()

    db.close()

# ==========================================
# RUN DIRECTLY
# ==========================================

if __name__ == "__main__":

    run_tracker()