import numpy as np
import pygame
import os

from glob import glob
from . import beatmap as _beatmap
from . import replay as _replay

from .core import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()

BEATMAPS_FOLDER = 'C:\\Program Files (x86)\\Jogos\\osu!\\Songs\\'
BEATMAP = glob(BEATMAPS_FOLDER + "\\**\\*Daybreak*Horizon[]]*.osu")[0]
#BEATMAP = glob(BEATMAPS_FOLDER + "\\**\\*Kami no Kotoba (byfar) [[]Voice of God[]]*.osu")[0]
#BEATMAP = glob(BEATMAPS_FOLDER + "\\**\\*Imprinting*9.5*.osu")[0]
beatmap = _beatmap.load(BEATMAP)

AUDIO = os.path.dirname(BEATMAP) + "\\" + beatmap["AudioFilename"]

#REPLAY = 'C:\\Program Files (x86)\\Jogos\\osu!\\Replays\\BzMasked - Imperial Circus Dead Decadence - Uta [Himei] (2018-04-29) Osu.osr'
REPLAY_DATA = 'osu\\replay.npy'
REPLAY_SAMPLING_RATE = 16

#my_replay = _replay.load(REPLAY)

ia_replay = np.load(REPLAY_DATA)

time = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.mixer.music.load(AUDIO)
pygame.mixer.music.play()

cx = 0
cy = 0

preempt, _ = beatmap.approach_rate()

while True:
    time = pygame.mixer.music.get_pos()

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

    visible_objects = beatmap.visible_objects(time)

    for obj in visible_objects:
        obj.render(beatmap, screen, time)

    if len(visible_objects) > 0:
        delta = visible_objects[0].time - time
        if delta > 0:
            cx += (visible_objects[0].x - cx) / delta
            cy += (visible_objects[0].y - cy) / delta

    #x, y, z = my_replay.frame(time)
    pygame.draw.circle(screen, (0, 0, 255), (int(cx), int(cy)), 4)

    frame = (time - int(beatmap.hit_objects[0].time - preempt)) // REPLAY_SAMPLING_RATE
    if frame > 0 and frame < len(ia_replay):
        x, y = ia_replay[frame]
        x *= SCREEN_WIDTH
        x += SCREEN_WIDTH / 2
        y *= SCREEN_HEIGHT
        y += SCREEN_HEIGHT / 2
        pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 8)

    pygame.display.flip()

    clock.tick(1000)