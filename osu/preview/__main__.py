import math
import os
import re

import numpy as np
import pygame
import mutagen.mp3

from osu.rulesets import beatmap as _beatmap, hitobjects as _hitobjects, \
						replay as _replay
from osu.rulesets.core import SCREEN_HEIGHT, SCREEN_WIDTH
from osulearn import dataset

from glob import glob
from osu.preview import beatmap as beatmap_preview

# Replay selection
replays = glob(os.path.join(".generated", "* (*) [[]*[]].npy"))

if len(replays) == 0:
	raise "No replays found"
elif len(replays) == 1:
	replay_file = replays[0]
else:
	for i, file in enumerate(replays):
		print(i, '-', os.path.basename(file))

	replay_file = None
	while replay_file == None:
		print()
		print("Choose replay (0-{}):".format(len(replays) - 1), end='')
		n = input()

		if not n.isnumeric():
			print("Invalid replay Id -", n)
			continue
		else:
			n = int(n)

			if n >= len(replays):
				print("Invalid replay Id -", n)
				continue

			replay_file = replays[n]

replay_file = os.path.basename(replay_file)
m = re.search(r"(.+)\s*\((.+)\)\s*\[(.+)\]", replay_file)
assert not (m is None), "Invalid replay file"
beatmap_pattern = "*{}*{}*{}*.osu".format(m[1], m[2], m[3])

# osu! Beatmap directory
BEATMAPS_FOLDER = os.path.join(os.getenv('LocalAppData'), "osu!", "Songs")

# Find beatmap
beatmap_glob = glob(os.path.join(BEATMAPS_FOLDER, "**", beatmap_pattern))
assert len(beatmap_glob) > 0, "Beatmap not found"
beatmap = _beatmap.load(beatmap_glob[0])

# Setup audio
AUDIO = os.path.join(os.path.dirname(beatmap_glob[0]), beatmap["AudioFilename"])
mp3 = mutagen.mp3.MP3(AUDIO)
pygame.mixer.init(frequency=mp3.info.sample_rate)
pygame.mixer.music.load(AUDIO)

# Load generated replay data
REPLAY_DATA = os.path.join('.generated', replay_file)
REPLAY_SAMPLING_RATE = dataset.FRAME_RATE

ia_replay = np.load(REPLAY_DATA)

pygame.init()

time = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FRAME_RATE = 1000

cx = 0
cy = 0

preview = beatmap_preview.from_beatmap(beatmap)

trail = []

pygame.mixer.music.play(start=beatmap['AudioLeadIn'] / 1000)

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

		trail_surface = pygame.Surface((screen.get_width(), screen.get_height()))
		trail_surface.set_colorkey((0, 0, 0))
		for tx, ty in trail:
			pygame.draw.circle(trail_surface, (0, 255, 0), (int(tx), int(ty)), 6)
		trail_surface.set_alpha(127)
		screen.blit(trail_surface, (0, 0))
		trail.append((x, y))
		if len(trail) > 64:
			trail.pop(0)

	pygame.display.flip()

	clock.tick(FRAME_RATE)