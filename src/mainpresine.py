import machine
import uos
import struct
import time
import math

def print_wav_header(header):
    # Parse the header information
    riff, size, fformat = struct.unpack('<4sI4s', header[:12])
    fmt_chunk_marker, fmt_length = struct.unpack('<4sI', header[12:20])
    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', header[20:36])
    data_chunk_header, data_size = struct.unpack('<4sI', header[36:44])

    # Print the parsed header information
    print(f"RIFF header: {riff}")
    print(f"File size: {size}")
    print(f"Format: {fformat}")
    print(f"Format chunk marker: {fmt_chunk_marker}")
    print(f"Format length: {fmt_length}")
    print(f"Audio format: {audio_format}")
    print(f"Number of channels: {num_channels}")
    print(f"Sample rate: {sample_rate}")
    print(f"Byte rate: {byte_rate}")
    print(f"Block align: {block_align}")
    print(f"Bits per sample: {bits_per_sample}")
    print(f"Data chunk header: {data_chunk_header}")
    print(f"Data size: {data_size}")

    return sample_rate, bits_per_sample, data_size, byte_rate

def playWav(wav_file, sample_rate, bits_per_sample, data_size, byte_rate):
    # Initialize DAC
    dac = machine.DAC(machine.Pin(25))  # Use GPIO25 (DAC1)

    # Buffer to hold audio data
    buffer = bytearray(1024)

    # Calculate the duration of the WAV file
    duration = data_size / byte_rate

    print(f"Playing... Total data size: {data_size} bytes")

    # Flag to indicate playback completion
    playback_complete = [False]  # Use a list to allow modification inside the inner function

    # Read and play the audio data
    def play_sample(timer):
        nonlocal buffer, num_read, buffer_index, wav_file, playback_complete, file_offset
        print(f"Timer callback called, buffer_index: {buffer_index}, num_read: {num_read}, total size: {data_size}, file offset: {file_offset}")
        if buffer_index >= num_read:
            print("Reading more data into buffer")
            num_read = wav_file.readinto(buffer)
            buffer_index = 0
            file_offset += num_read
            if num_read == 0:
                print("End of file reached")
                timer.deinit()
                wav_file.close()
                playback_complete[0] = True  # Modify the content of the list
                print(f"Played {duration:.2f} seconds")
                return
        sample = buffer[buffer_index]
        if bits_per_sample == 16:
            sample = sample // 256  # Convert 16-bit to 8-bit
        dac.write(sample)
        buffer_index += 1

    num_read = wav_file.readinto(buffer)
    buffer_index = 0
    file_offset = 44  # Start after the header

    # Set up a hardware timer to call play_sample at the sample rate
    timer = machine.Timer(0)
    timer.init(period=int(1000000 / sample_rate), mode=machine.Timer.PERIODIC, callback=play_sample)

    # Keep the main thread alive to allow the timer to run
    while not playback_complete[0]:
        time.sleep(0.1)

def test_dac():
    # Initialize DAC
    dac = machine.DAC(machine.Pin(25))  # Use GPIO25 (DAC1)

    # Generate a 5-second sine wave
    sample_rate = 44100
    frequency = 440  # A4 note
    duration = 5  # seconds
    num_samples = sample_rate * duration

    print("Generating sine wave...")

    for i in range(num_samples):
        sample = int((math.sin(2 * math.pi * frequency * i / sample_rate) + 1) * 127.5)
        dac.write(sample)
        time.sleep(1 / sample_rate)

    print("Sine wave generation complete.")

def init():
    # Test the DAC with a sine wave
    test_dac()

    # Open the WAV file
    wav_file = open('/audio/Storm_exclamation.wav', 'rb')
    
    # Read the first 44 bytes (header)
    header = wav_file.read(44)
    sample_rate, bits_per_sample, data_size, byte_rate = print_wav_header(header)
    
    # Play the WAV file
    playWav(wav_file, sample_rate, bits_per_sample, data_size, byte_rate)

# Run the initialization function
init()