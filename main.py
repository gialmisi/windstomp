import pygame
import pygame.midi
import time

pygame.init()
pygame.midi.init()
default_id = pygame.midi.get_default_input_id() 

print(default_id)
in_midi = pygame.midi.Input(3)


while True:
    if in_midi.poll():
        res = in_midi.read(128)
        py_res = pygame.midi.midis2events(res, default_id)
        
        output = []
        for e in py_res:
            output.append(pygame.midi.midi_to_ansi_note(e.data1))
        print(output)

    time.sleep(0.1)
