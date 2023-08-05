"""
import pygame
import pygame.midi
import time
import pyaudio
import numpy as np
import scipy.signal as sg

pygame.init()
pygame.midi.init()
default_id = pygame.midi.get_default_input_id() 

print(default_id)
in_midi = pygame.midi.Input(3)

sample_rate = 48000 # 48kHz

duration = 1
frequency = 440.0 # A4


def create_sine(frequency, duration=duration, sample_rate=sample_rate) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sine_wave = np.sin(2 * np.pi * frequency * t)

    return sine_wave.astype(np.float32)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True, frames_per_buffer=128)

wave_A = 0.2*create_sine(440.0, duration=0.5)
wave_B = 0.2*create_sine(493.88, duration=0.5)
wave_C = 0.2*create_sine(523.25, duration=0.5)

stream.write(wave_A.tobytes())
stream.write(wave_B.tobytes())
stream.write(wave_C.tobytes())

stream.close()

p.terminate()

# stream.write(blended_wave.tobytes())


while True:
    if in_midi.poll():
        res = in_midi.read(128)
        py_res = pygame.midi.midis2events(res, default_id)
        
        output = []
        for e in py_res:
            output.append(pygame.midi.midi_to_ansi_note(e.data1))
            print(py_res)
        print(output)

    time.sleep(0.1)

"""

import pyaudio
import numpy as np

# Define constants
SAMPLE_RATE = 48000  # Hertz
DURATION = 5  # The duration of the wave
FREQUENCY = 440.0  # Frequency of the wave in Hz

# Generate array with time points
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)

# Generate a 440 Hz sine wave
note = np.sin(FREQUENCY * t * 2 * np.pi)

# Convert to 32-bit data
audio = note.astype(np.float32)

# Start playback
p = pyaudio.PyAudio()

# Define callback for PyAudio to pull data from
def callback(in_data, frame_count, time_info, status):
    data = audio[:frame_count]
    return (data.tobytes(), pyaudio.paContinue)

# Open stream using callback
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                output=True,
                frames_per_buffer=1028,
                stream_callback=callback)

# Start the stream
stream.start_stream()

# Keep the stream active for 5 seconds by sleeping here
import time
time.sleep(DURATION)

# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
