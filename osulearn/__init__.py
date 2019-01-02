import math

import numpy as np
from keras.preprocessing.sequence import pad_sequences

import osu.rulesets
import random

from osu.rulesets import hitobjects

SAMPLE_RATE = 16
LENGTH = 1024

def create_training_data(replay_set):
    training_data = []
    _cache = {}

    for beatmap, _ in replay_set:
        if beatmap in _cache:
            training_data += _cache[beatmap]
            continue

        if len(beatmap.hit_objects) == 0:
            continue

        _cache[beatmap] = []

        r = []
        preempt, _ = beatmap.approach_rate()

        for time in range(beatmap.start_offset(), beatmap.length(), SAMPLE_RATE):
            visible_objects = beatmap.visible_objects(time, count=1)

            if len(visible_objects) > 0:
                obj = visible_objects[0]
                beat_duration = beatmap.beat_duration(obj.time)
                px, py = obj.target_position(time, beat_duration, beatmap['SliderMultiplier'])

                time_left = obj.time - time
                is_slider = int(isinstance(obj, hitobjects.Slider))
                is_spinner = int(isinstance(obj, hitobjects.Spinner))

            else:
                px, py = osu.rulesets.core.SCREEN_WIDTH / 2, osu.rulesets.core.SCREEN_HEIGHT / 2

                time_left = float("inf")
                is_slider = 0
                is_spinner = 0

            px = max(0, min(px / osu.rulesets.core.SCREEN_WIDTH, 1))
            py = max(0, min(py / osu.rulesets.core.SCREEN_HEIGHT, 1))

            r.append(np.array([
                px - 0.5,
                py - 0.5,
                time_left < preempt,
                is_slider,
                is_spinner
            ]))
            
            if len(r) == LENGTH:
                training_data.append(r)
                _cache[beatmap].append(r)
                r = []
                
        if len(r) > 0:
            _cache[beatmap].append(r)
            training_data.append(r)        

        print(beatmap['Title'])

    return pad_sequences(np.array(training_data), dtype='float', padding='post', value=0)

def create_target_data(replay_set):
    target_data = []
    
    for beatmap, replay in replay_set:
        if len(beatmap.hit_objects) == 0:
            continue
        r = []

        for time in range(beatmap.start_offset(), beatmap.length(), SAMPLE_RATE):
            visible_objects = beatmap.visible_objects(time, count=1)
            
            if len(visible_objects) > 0:
                obj = visible_objects[0]
                if isinstance(obj, hitobjects.Spinner):
                    x, y = obj.x, obj.y
                else:
                    x, y, _ = replay.frame(time)
            else:
                x, y = osu.rulesets.core.SCREEN_WIDTH / 2, osu.rulesets.core.SCREEN_HEIGHT / 2

            x = max(0, min(x / osu.rulesets.core.SCREEN_WIDTH, 1))
            y = max(0, min(y / osu.rulesets.core.SCREEN_HEIGHT, 1))

            r.append(np.array([
                x - 0.5,
                y - 0.5
            ]))

            if len(r) == LENGTH:
                target_data.append(r)
                r = []

        if len(r) > 0:
            target_data.append(r)

        print(beatmap["Title"])
            
    return pad_sequences(np.array(target_data), dtype='float', padding='post', value=0)