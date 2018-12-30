import numpy as np
import math

from keras.preprocessing.sequence import pad_sequences

def create_training_data(replay_set):
    training_data = []

    for beatmap, replay in replay_set:
        time = 0
        r = []
        for w, x, y, z in replay.data:
            if w < 0:
                continue

            visible_objects = beatmap.visible_objects(time, count=1)

            if len(visible_objects) > 0:
                obj = visible_objects[0]

                px = obj[0]
                py = obj[1]

                dx = obj[0] - x
                dy = obj[1] - y
                dist = dx ** 2 + dy ** 2

                angle = math.atan2(dy, dx)
                if angle < 0:
                    angle += 2 * math.pi

                time_left = obj[2] - time

                is_slider = obj[3] & 2
                is_spinner = obj[3] & 8

                if is_spinner:
                    duration = obj[5]
                else:
                    duration = 0
            else:
                px = 0
                py = 0
                dx = 0
                dy = 0
                dist = 0
                angle = 0
                time_left = 5000
                is_slider = 0
                is_spinner = 0
                duration = 0

            r.append(np.array([
                max(0, min(px / 512, 1)),
                max(0, min(py / 384, 1)),
                time_left,
                # is_slider,
                # is_spinner,
                # duration
            ]))

            time += w

        training_data.append(np.array(r))

    return pad_sequences(np.array(training_data), dtype='float', padding='post')

def create_target_data(replay_set):
    target_data = []
    
    for _, replay in replay_set:
        time = 0

        last_x = None
        last_y = None

        r = []
        for i in range(len(replay.data)):
            w, x, y, z = replay.data[i]

            if w < 0:
                continue

            if not last_x is None:
                dx = x - last_x
                dy = y - last_y

                dist = dx ** 2 + dy ** 2

                angle = math.atan2(dy, dx)
                if angle < 0:
                    angle += 2 * math.pi
            else:
                dist = 0
                angle = 0

            r.append(np.array([
                max(0, min(x / 512, 1)),
                max(0, min(y / 384, 1)),
                # z & 0x01 == 1,
                # z & 0x02 == 2
            ]))

            if x > 0 and y > 0:
                last_x = x
                last_y = y

            time += w

        target_data.append(np.array(r))
            
    return pad_sequences(np.array(target_data), dtype='float', padding='post')