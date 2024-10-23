import machine
import neopixel
import time

# Constants
LED_PIN = 14  # Change to another GPIO pin if necessary
LED_COUNT = 300

# Initialize the NeoPixel strip
print("Initializing NeoPixel strip...")
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

# Light up the 4th LED (index 3)
print("Setting LED color...")
np[299] = (255,255 , 255)
np.write()

# Confirm the LED is set
print("LED should be lit now.")

# Keep the LED on for a while
time.sleep(10)
print("Test complete.")

