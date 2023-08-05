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

duration = 100
frequency = 440.0 # A4


def create_sine(frequency, duration=duration, sample_rate=sample_rate) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sine_wave = np.sin(2 * np.pi * frequency * t)

    return sine_wave

"""
# Create waveforms
square_wave = sg.square(2 * np.pi * frequency * t)
triangle_wave = sg.sawtooth(2 * np.pi * frequency * t, 0.5)  # 0.5 sets it as a triangle wave
saw_wave = sg.sawtooth(2 * np.pi * frequency * t)

# Set your blend levels (these can be whatever you want)
sine_blend = 0.25
square_blend = 0.9
triangle_blend = 0.25
saw_blend = 0.24

# Now blend your waveforms together
blended_wave = sine_blend * sine_wave + square_blend * square_wave + triangle_blend * triangle_wave + saw_blend * saw_wave
blended_wave *= 0.25
"""

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True, frames_per_buffer=2048)

wave_A = 0.2*create_sine(440, duration=0.5)
wave_B = 0.2*create_sine(493.88, duration=0.5)
wave_C = 0.2*create_sine(523.25, duration=0.5)

stream.write(wave_A.tobytes())
stream.write(np.zeros(1024).tobytes())
stream.write(wave_B.tobytes())
stream.write(np.zeros(1024).tobytes())
stream.write(wave_C.tobytes())
stream.write(np.zeros(1024).tobytes())

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
        print(output)

    time.sleep(0.1)

