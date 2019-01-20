import math
import os

import numpy as np
import pygame
import mutagen.mp3

from ..rulesets import beatmap as _beatmap, hitobjects as _hitobjects, \
                        replay as _replay
from ..rulesets.core import SCREEN_HEIGHT, SCREEN_WIDTH

from glob import glob
from osu.preview import beatmap as beatmap_preview

BEATMAPS_FOLDER = "C:/Users/guigb/AppData/Local/osu!/Songs"
BEATMAP = glob(BEATMAPS_FOLDER + "\\**\\*Itazura Fiction*Akitoshi*Chaos*.osu")[0]
beatmap = _beatmap.load(BEATMAP)

AUDIO = os.path.dirname(BEATMAP) + "\\" + beatmap["AudioFilename"]

mp3 = mutagen.mp3.MP3(AUDIO)
pygame.mixer.init(frequency=mp3.info.sample_rate)
pygame.mixer.music.load(AUDIO)
pygame.mixer.music.play(start=beatmap['AudioLeadIn'] / 1000)

REPLAY_DATA = 'osu\\replay.npy'
REPLAY_SAMPLING_RATE = 32

ia_replay = np.load(REPLAY_DATA)

pygame.init()

time = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FRAME_RATE = 1000

cx = 0
cy = 0

preview = beatmap_preview.from_beatmap(beatmap)

while True:
    time = pygame.mixer.music.get_pos()

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

    preview.render(screen, time)

    visible_objects = beatmap.visible_objects(time)

    if len(visible_objects) > 0:
        delta = visible_objects[0].time - time
        ox, oy = visible_objects[0].target_position(time, beatmap.beat_duration(time), beatmap['SliderMultiplier'])

        if delta > 0:
            cx += (ox - cx) / delta
            cy += (oy - cy) / delta
        else:
            cx = ox
            cy = oy

    #cx, cy, z = my_replay.frame(time)
    #pygame.draw.circle(screen, (255, 0, 0), (int(cx), int(cy)), 8)

    frame = (time - beatmap.start_offset()) // REPLAY_SAMPLING_RATE
    if frame > 0 and frame < len(ia_replay):
        x, y = ia_replay[frame]
        x += 0.5
        y += 0.5
        x *= SCREEN_WIDTH
        y *= SCREEN_HEIGHT
        pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 8)

    pygame.display.flip()

    clock.tick(FRAME_RATE)