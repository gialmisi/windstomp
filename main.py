import pyaudio
import numpy as np
import pygame
import pygame.midi

class AudioController:
    def __init__(self, callback, audio_device_name="jack", channels=1, audio_format=pyaudio.paFloat32, rate=48_000, buffer_size=256):
        self.callback = callback
        self.p = pyaudio.PyAudio()

        def find_device_index_by_name(device_name, p=self.p):
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info["name"] == device_name:
                    return device_info["index"]
            raise ValueError(f"No device with name '{device_name}' found")
        
        self.stream = self.p.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=find_device_index_by_name(audio_device_name),
            frames_per_buffer=buffer_size,
            stream_callback=self.callback,
        )

    def start(self):
        self.stream.start_stream()
    
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class Oscillator:
    def __init__(self, sample_rate=48_000):
        self.on = False
        self.frequency = 440.0
        self.sample_rate = sample_rate
        self.output = None
        self.generator = None
        self.phase = 0.0
    
    def setup(self):
        self.output = self.sine_wave()
        self.generator = self.create_generator()

    def update(self):
        self.output = self.sine_wave()
        self.generator = self.create_generator()

    def sine_wave(self):
        # Calculate the phase increment
        phase_increment = 2.0 * np.pi * self.frequency / self.sample_rate

        # Use the phase accumulator to generate the waveform
        waveform = np.sin(self.phase + np.arange(self.sample_rate) * phase_increment)
        
        # Update the phase accumulator for the next batch
        self.phase += self.sample_rate * phase_increment
        self.phase %= 2.0 * np.pi  # Keep the phase within [0, 2*pi]
        
        return waveform.astype(np.float32)

    def create_generator(self):
        while True:
            waveform = self.sine_wave()
            for value in waveform:
                yield value
        
    def callback(self, in_data, frame_count, time_info, status):
        if self.on:
            data = np.array([next(self.generator) for _ in range(frame_count)], dtype=np.float32)
            return (data.tobytes(), pyaudio.paContinue)
        else:
            return (b'\0' * frame_count * 4, pyaudio.paContinue)


oscillator = Oscillator()
oscillator.setup()

audio_controller = AudioController(oscillator.callback)

audio_controller.start()

## MIDI
pygame.init()
pygame.midi.init()

midi_device_name = "LPK25 MIDI 1"

def find_midi_input_device_by_name(device_name):
    for i in range(pygame.midi.get_count()):
        device_info = pygame.midi.get_device_info(i)
        # Decode device name from bytes to string
        device_info_name = device_info[1].decode()
        # device_info[2] is a boolean indicating whether it's an input device
        if device_info[2] and device_info_name == device_name:
            return i
    raise ValueError(f"No input device with name '{device_name}' found")

midi_input_device_id = find_midi_input_device_by_name(midi_device_name)

midi_input = pygame.midi.Input(midi_input_device_id)

def midi_to_frequency(midi_note):
    return 2**((midi_note - 69) / 12) * 440

import time

while True:
    if midi_input.poll():
        midi_events = midi_input.read(10)
        for event in midi_events:
            if event[0][0] == 144:
                print("Note on")
                oscillator.on = True
                oscillator.frequency = midi_to_frequency(event[0][1])
                oscillator.update()

            elif event[0][0] == 128:
                oscillator.on = False
                oscillator.update()
            else:
                pass

            time.sleep(0.1)
audio_controller.stop()

"""
# Generate array with time points
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)

# Generate a 440 Hz sine wave
note = np.sin(FREQUENCY * t * 2 * np.pi)

# Convert to 32-bit data
audio = note.astype(np.float32)

def sine_wave_generator(audio):
    index = 0
    while True:
        if index < len(audio):
            yield audio[index]
            index += 1
        else:
            index = 0  # loop back to the beginning
            print("looping!")

# Create a generator for our sine wave audio data
sine_wave = sine_wave_generator(audio)

# Start playback
p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    print(device_info)


# Open stream using callback
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=128,
                stream_callback=callback)
"""

"""
# Start the stream
stream.start_stream()

while True:
    if midi_input.poll():
        midi_events = midi_input.read(10)
        for event in midi_events:
            if event[0][0] == 144:
                print("Note on")
                key_pressed = True
            elif event[0][0] == 128:
                print("note off")
                key_pressed = False
            else:
                pass

# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
pygame.midi.quit()
p.terminate()

pygame.init()
pygame.midi.init()

midi_device_name = "LPK25 MIDI 1"

def find_midi_input_device_by_name(device_name):
    for i in range(pygame.midi.get_count()):
        device_info = pygame.midi.get_device_info(i)
        # Decode device name from bytes to string
        device_info_name = device_info[1].decode()
        # device_info[2] is a boolean indicating whether it's an input device
        if device_info[2] and device_info_name == device_name:
            return i
    raise ValueError(f"No input device with name '{device_name}' found")

midi_input_device_id = find_midi_input_device_by_name(midi_device_name)

midi_input = pygame.midi.Input(midi_input_device_id)
"""