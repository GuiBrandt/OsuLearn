import numpy as np
import math

import osu

from keras.preprocessing.sequence import pad_sequences

def create_training_data(replay_set):
    training_data = []

    for beatmap, _ in replay_set:
        r = []

        for time in range(0, beatmap.length(), 12):
            visible_objects = beatmap.visible_objects(time, count=1)

            if len(visible_objects) > 0:
                obj = visible_objects[0]
                px, py = obj.x, obj.y
                time_left = obj.time - time
                is_slider = obj is osu.hitobjects.Slider
                is_spinner = obj is osu.hitobjects.Spinner
                
            else:
                px = osu.core.SCREEN_WIDTH / 2
                py = osu.core.SCREEN_HEIGHT / 2
                time_left = 1
                is_slider = 0
                is_spinner = 0

            r.append(np.array([
                (max(0, min(px / osu.core.SCREEN_WIDTH, 1)) - 0.5),
                (max(0, min(py / osu.core.SCREEN_HEIGHT, 1)) - 0.5),
                time_left / 1000,
                is_slider,
                is_spinner
            ]))
            
            if len(r) == 2000:
                training_data.append(r)
                r = []
                
        if len(r) > 0:
            training_data.append(r)

        print(beatmap["Title"])            

    return pad_sequences(np.array(training_data), dtype='float', padding='post', value=0)

def create_target_data(replay_set):
    target_data = []
    
    for beatmap, replay in replay_set:
        r = []

        for time in range(0, beatmap.length(), 12):
            x, y, _ = replay.frame(time)

            r.append(np.array([
                max(0, min(x / 512, 1)) - 0.5,
                max(0, min(y / 384, 1)) - 0.5
            ]))

            if len(r) == 2000:
                target_data.append(r)
                r = []

        if len(r) > 0:
            target_data.append(r)

        print(beatmap["Title"])
            
    return pad_sequences(np.array(target_data), dtype='float', padding='post', value=0)