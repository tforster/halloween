import machine
import uos
import struct
import time

def parse_wav_header(header):
    # Parse the header information
    riff, size, fformat = struct.unpack('<4sI4s', header[:12])
    fmt_chunk_marker, fmt_length = struct.unpack('<4sI', header[12:20])
    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', header[20:36])
    data_chunk_header, data_size = struct.unpack('<4sI', header[36:44])

    # Print the parsed header information for debugging
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

def hex_dump(data, length=16, offset=0):
    # Print the buffer contents in a formatted way
    for i in range(0, len(data), length):
        line = data[i:i+length]
        hex_values = ' '.join(f'{byte:02X}' for byte in line)
        ascii_values = ''.join(chr(byte) if 32 <= byte <= 127 else '.' for byte in line)
        print(f'{offset + i:04X}  {hex_values:<48}  {ascii_values}')

def play_wav(wav_file, sample_rate, data_size, byte_rate, volume=5.0):
    # Initialize DAC
    dac = machine.DAC(machine.Pin(25))  # Use GPIO25 (DAC1)

    # Buffer size
    buffer_size = 128
    buffer = bytearray(buffer_size)

    # Calculate the duration of the WAV file
    duration = data_size / byte_rate
    sample_interval_us = int(1000000 / sample_rate)  # Interval between samples in microseconds

    print(f"Playing... Total data size: {data_size} bytes, expected duration: {duration:.2f} seconds")

    # Initialize buffer_index and byte_offset
    buffer_index = 0
    byte_offset = wav_file.readinto(buffer)
    print("Initial buffer read:")
    hex_dump(buffer[:byte_offset], offset=44)  # Debugging initial buffer read

    # Read and play the audio data
    file_offset = 0  # Start after the header
    total_bytes_processed = 0

    while True:
        if buffer_index >= byte_offset:
            byte_offset = wav_file.readinto(buffer)
            buffer_index = 0
            file_offset += byte_offset
            if byte_offset == 0:
                print(f"End of file reached. Total bytes processed: {total_bytes_processed}")
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
    print(f"Total bytes processed: {total_bytes_processed}, expected bytes: {data_size}")

def init():
    # Open the WAV file
    wav_file = open('/audio/Storm_exclamation.wav', 'rb')
    
    # Read the first 44 bytes (header)
    header = wav_file.read(44)
    sample_rate, bits_per_sample, data_size, byte_rate = parse_wav_header(header)
    
    # Play the WAV file with volume control
    play_wav(wav_file, sample_rate, data_size, byte_rate, volume=2.0)  # Adjust volume here

# Run the initialization function
init()