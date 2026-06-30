import time
import RPi.GPIO as GPIO

from config import POLL_INTERVAL
from db_handler import alarm_is_active, acknowledge_all_alarms
from gpio_handler import alarm_on, alarm_off

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)

GPIO.setup(
    BUTTON_PIN,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
)

alarm_state = None

print("PPE Alarm Controller Started")

try:

    while True:

        # ACK BUTTON

        if GPIO.input(BUTTON_PIN) == GPIO.LOW:

            print("ACK BUTTON PRESSED")

            acknowledge_all_alarms()

            alarm_off()
            alarm_state= False

            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.1)

        # ALARM CHECK

        current_state = alarm_is_active()

        if current_state != alarm_state:

            if current_state:
                alarm_on()
            else:
                alarm_off()

            alarm_state = current_state

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:

    GPIO.cleanup()

except Exception as e:

    print("ERROR:", e)
