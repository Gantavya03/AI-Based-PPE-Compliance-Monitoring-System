import threading
import time
import RPi.GPIO as GPIO
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone

# LED Pin
LED_PIN = 18

# Buzzer Pin
BUZZER_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


buzzer = TonalBuzzer(BUZZER_PIN)

blinking = False


def blink_alarm():

    while blinking:

        GPIO.output(LED_PIN, GPIO.HIGH)

        buzzer.tone = Tone(440)

        time.sleep(0.5)

        GPIO.output(LED_PIN, GPIO.LOW)

        buzzer.stop()

        time.sleep(0.5)


def alarm_on():

    global blinking

    if not blinking:

        blinking = True

        threading.Thread(
            target=blink_alarm,
            daemon=True
        ).start()

    print("ALARM ACTIVE")


def alarm_off():

    global blinking

    blinking = False

    GPIO.output(LED_PIN, GPIO.LOW)
    buzzer.stop()

    print("ALARM CLEARED")
