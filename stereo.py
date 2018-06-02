import pygame
import os
import time
from os import listdir
from os.path import isfile, join
from random import shuffle

defaultDirectory="Music/"
running = True

if not os.path.exists(defaultDirectory):
    os.makedirs(defaultDirectory)
    print("Empty folder...")
    exit()

pygame.mixer.init()
#files names
playlist = [f for f in listdir(defaultDirectory) if isfile(join(defaultDirectory, f))]
#shuffle playlist
shuffle(playlist)
music=defaultDirectory+playlist.pop()
print music
pygame.mixer.music.load(music) 
pygame.mixer.music.play()

while pygame.mixer.music.get_busy() or running:
    if len(playlist) > 0:
        music=defaultDirectory+playlist.pop()
        print music
        pygame.mixer.music.queue(music)
    else: continue
