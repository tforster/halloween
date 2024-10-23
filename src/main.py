import machine
import neopixel
import time
from machine import TouchPad
# Configuration
LED_COUNT = 300        # Number of LED pixels
LED_PIN = 25          # GPIO pin connected to the pixels (e.g., 18)
SWITCH_PIN = 14 

# Initialize the NeoPixel strip
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)
switch = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_DOWN)


print("INIT",switch.value()) 

def clear_leds(np):
    """Turn off all LEDs."""
    for i in range(len(np)):
        np[i] = (0, 0, 0)
    np.write()

def light_chaser(np, wait_ms=2, batch_size=1):
    """Light up LEDs in a chaser pattern with batch updates."""
    for i in range(0, len(np), batch_size):
        for j in range(batch_size):
            if i + j < len(np):
                np[i + j] = (240, 248, 255)  # Set color to red
        np.write()
        time.sleep_ms(wait_ms)
        for j in range(batch_size):
            if i + j < len(np):
                np[i + j] = (0, 0, 0)  # Turn off the LED

# # Run the light chaser
clear_leds(np)
# np.fill((0,0,0))
# np.write()
light_chaser(np, wait_ms=2, batch_size=40)
clear_leds(np)
# np.fill((0,0,0))
# np.write()


while True:
    print(switch.value())
    if switch.value() != 0:  # Assuming the switch is active low
        light_chaser(np, wait_ms=2, batch_size=40)
        clear_leds(np)  # Clear LEDs after the effect
        time.sleep(5)
    else:
      print("No touch")
         
    
    time.sleep(.2)  # Add a small delay to avoid excessive readings
