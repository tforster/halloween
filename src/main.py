import machine
import _thread
import struct
import time
import neopixel
from machine import TouchPad, Pin


# Configuration
LED_COUNT = 300         # Number of LED pixels
LED_PIN = 14            # GPIO pin connected to the pixels (e.g., 18)
SWITCH_PIN = 5         # GPIO pin connected to the switch (e.g., 14)
DAC_PIN = 26            # GPIO pin connected to the amplifier 
audio_playing = False
light_playing = False


# parse_wav_header: Parse the WAV file header information
# @param header: Header data buffer to parse
# Parse the WAV file header information
# Return: Tuple containing sample rate, bits per sample, data size, and byte rate
def parse_wav_header(header):
    # Parse the header information
    riff, size, fformat = struct.unpack('<4sI4s', header[:12])
    fmt_chunk_marker, fmt_length = struct.unpack('<4sI', header[12:20])
    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', header[20:36])
    data_chunk_header, data_size = struct.unpack('<4sI', header[36:44])

    # Print the parsed header information for debugging
    # print(f"RIFF header: {riff}")
    # print(f"File size: {size}")
    # print(f"Format: {fformat}")
    # print(f"Format chunk marker: {fmt_chunk_marker}")
    # print(f"Format length: {fmt_length}")
    # print(f"Audio format: {audio_format}")
    # print(f"Number of channels: {num_channels}")
    # print(f"Sample rate: {sample_rate}")
    # print(f"Byte rate: {byte_rate}")
    # print(f"Block align: {block_align}")
    # print(f"Bits per sample: {bits_per_sample}")
    # print(f"Data chunk header: {data_chunk_header}")
    # print(f"Data size: {data_size}")
    return sample_rate, bits_per_sample, data_size, byte_rate

# hex_dump: Print the buffer contents in a formatted way
# @param data: Data buffer to print
# @param length: Number of bytes to print per line (default: 16)
# @param offset: Offset value to print (default: 0)
# Print the buffer contents in a formatted way for debugging purposes only
# Return: None
def hex_dump(data, length=16, offset=0):
    # Print the buffer contents in a formatted way
    for i in range(0, len(data), length):
        line = data[i:i+length]
        hex_values = ' '.join(f'{byte:02X}' for byte in line)
        ascii_values = ''.join(chr(byte) if 32 <= byte <= 127 else '.' for byte in line)
        print(f'{offset + i:04X}  {hex_values:<48}  {ascii_values}')

# play_audio: Plays a WAV file using the DAC
# @param wav_file: Open file object for the WAV file
# @param sample_rate: Sample rate of the audio data
# @param data_size: Size of the audio data in bytes
# @param byte_rate: Byte rate of the audio data
# @param volume: Volume multiplier (default: 5.0)
# Play the WAV file using the DAC
# Return: None
def play_audio(wav_file, sample_rate, data_size, byte_rate, volume=5.0):
    # print("play_audio")
    wav_file.seek(44)


    # Buffer size
    buffer_size = 128
    buffer = bytearray(buffer_size)

    # Calculate the duration of the WAV file
    duration = data_size / byte_rate
    sample_interval_us = int(1000000 / sample_rate)  # Interval between samples in microseconds

    # print(f"Playing... Total data size: {data_size} bytes, expected duration: {duration:.2f} seconds")

    # Initialize buffer_index and byte_offset
    buffer_index = 0
    byte_offset = wav_file.readinto(buffer)
    # print("Initial buffer read:")
    # hex_dump(buffer[:byte_offset], offset=44)  # Debugging initial buffer read

    # Read and play the audio data
    file_offset = 0  # Start after the header
    total_bytes_processed = 0

    while True:
        if buffer_index >= byte_offset:
            byte_offset = wav_file.readinto(buffer)
            buffer_index = 0
            file_offset += byte_offset
            if byte_offset == 0:
                # print(f"End of file reached. Total bytes processed: {total_bytes_processed}")
                break
            #print("Buffer read:")
            #hex_dump(buffer[:byte_offset], offset=file_offset + 44)  # Debugging buffer read
        # Handle 8-bit samples
        sample = buffer[buffer_index]
        sample = int((sample - 128) * volume + 128)  # Adjust volume and center around 128
        sample = max(0, min(255, sample))  # Ensure the sample is within 0-255 range
        buffer_index += 1
        dac.write(sample)
        total_bytes_processed += 1  # Increment by 1 byte for 8-bit samples
        #print(f"Sample written to DAC: {sample}, buffer_index: {buffer_index}, byte_offset: {byte_offset}, file position: {file_offset + buffer_index + 44}")  # Debugging sample value
        time.sleep_us(sample_interval_us)  # Delay to match the sample rate
    print(f"Played {duration:.2f} seconds, actual time: {total_bytes_processed / sample_rate:.2f} seconds")
    # print(f"Total bytes processed: {total_bytes_processed}, expected bytes: {data_size}")


# clear_leds: Called during init to ensure any LEDs that were on are turned off
# @param np: NeoPixel object
# Turn off all LEDs

# Return: None
def clear_leds(np):
    np.fill((0, 0, 0))
    np.write()

# lightning: Simulates a lightning effect by turning on a batch of LEDs
# @param np: NeoPixel object
# @param wait_ms: Delay in milliseconds between each batch update
# @param batch_size: Number of LEDs to update in each batch
# Turn on a batch of LEDs to simulate lightning
# Return: None
def play_lightning(np, wait_ms=2, batch_size=1):
  # print("lightning")
  num_pixels = len(np)
  
  for i in range(num_pixels - 1, -1, -batch_size):
      # Calculate the red component based on the position
      red_intensity = int(255 * (num_pixels - 1 - i) / (num_pixels - 1))
      
      for j in range(batch_size):
          if i - j >= 0:
              np[i - j] = (240 + red_intensity, 248 - red_intensity, 255 - red_intensity)  # Adjust color
      np.write()
      time.sleep_ms(wait_ms)
      
      for j in range(batch_size):
          if i - j >= 0:
              np[i - j] = (0, 0, 0)  # Turn off the LED
      np.write()
      
  time.sleep_ms(wait_ms*100)  

  np.fill((240, 248, 255))
  np.write()
  time.sleep_ms(wait_ms*100)  
  clear_leds(np)

  np.fill((240, 248, 255))
  np.write()
  time.sleep_ms(wait_ms*100) 
  clear_leds(np)
  light_playing = False



# Initialize the wav and NeoPixel strip
# This function is called when the device starts up
# Return: None
def init():
    # Open the WAV file
    wav_file = open('/audio/Storm_exclamation.wav', 'rb')
    header = wav_file.read(44)
    sample_rate, bits_per_sample, data_size, byte_rate = parse_wav_header(header)
    return wav_file, sample_rate, data_size, byte_rate

print("see this once")
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)
dac = machine.DAC(machine.Pin(DAC_PIN))  # Use GPIO25 (DAC1)
wav_file, sample_rate, data_size, byte_rate  = init()

clear_leds(np)
print("X")
while True:
    switch = machine.Pin(SWITCH_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

    ## Get the switch value
    switch_value = switch.value()
    
    # Invert with XOR (e.g., 0 -> 1, 1 -> 0)  
    switch_value^= 1
    # Check if the switch was pressed
    if switch_value == 1 and audio_playing == False and light_playing == False:
        audio_playing = True
        light_playing = True

        # Start threads for audio and lightning
        _thread.start_new_thread(play_audio, (wav_file, sample_rate, data_size, byte_rate))
        _thread.start_new_thread(play_lightning, (np, 2, 90))

        time.sleep(10)
        audio_playing = False
        light_playing = False
        print("reset")
        switch_value = 1



