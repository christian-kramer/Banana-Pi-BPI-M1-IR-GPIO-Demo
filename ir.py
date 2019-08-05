import RPi.GPIO as GPIO
from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/input/event1')

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
                print(event)
                if event.code == 1:
                        GPIO.output(12, GPIO.HIGH)
                if event.code == 255:
                        GPIO.output(12, GPIO.LOW)
