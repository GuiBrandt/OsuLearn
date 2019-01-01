import numpy as np
import math
import random

import osu

from keras.preprocessing.sequence import pad_sequences

SAMPLE_RATE = 16
LENGTH = 1024

def create_training_data(replay_set):
    training_data = []

    for beatmap, _ in replay_set:
        if len(beatmap.hit_objects) == 0:
            continue
        r = []
        preempt, _ = beatmap.approach_rate()

        last_visible_object = None
        for time in range(int(beatmap.hit_objects[0].time - preempt), beatmap.length(), SAMPLE_RATE):
            visible_objects = beatmap.visible_objects(time, count=1)

            if len(visible_objects) > 0:
                obj = visible_objects[0]
                last_visible_object = obj
                px, py = obj.target_position(beatmap, time)
                time_left = obj.time - time
                is_slider = obj is osu.hitobjects.Slider
                is_spinner = obj is osu.hitobjects.Spinner
                
            else:
                if last_visible_object is None:
                    px = osu.core.SCREEN_WIDTH / 2
                    py = osu.core.SCREEN_HEIGHT / 2
                else:
                    px, py = last_visible_object.target_position(beatmap, time)

                time_left = float("inf")
                is_slider = 0
                is_spinner = 0

            px = max(0, min(px / osu.core.SCREEN_WIDTH, 1))
            py = max(0, min(py / osu.core.SCREEN_HEIGHT, 1))

            r.append(np.array([
                px,
                py,
                time_left < preempt,
                is_slider,
                is_spinner
            ]))
            
            if len(r) == LENGTH:
                training_data.append(r)
                r = []
                
        if len(r) > 0:
            training_data.append(r)        

        print(beatmap['Title'])

    return pad_sequences(np.array(training_data), dtype='float', padding='post', value=0)

def create_target_data(replay_set):
    target_data = []
    
    for beatmap, replay in replay_set:
        if len(beatmap.hit_objects) == 0:
            continue
        r = []
        preempt, _ = beatmap.approach_rate()

        for time in range(int(beatmap.hit_objects[0].time - preempt), beatmap.length(), SAMPLE_RATE):
            x, y, _ = replay.frame(time)

            x = max(0, min(x / osu.core.SCREEN_WIDTH, 1))
            y = max(0, min(y / osu.core.SCREEN_HEIGHT, 1))

            r.append(np.array([
                x,
                y
            ]))

            if len(r) == LENGTH:
                target_data.append(r)
                r = []

        if len(r) > 0:
            target_data.append(r)

        print(beatmap["Title"])
            
    return pad_sequences(np.array(target_data), dtype='float', padding='post', value=0)