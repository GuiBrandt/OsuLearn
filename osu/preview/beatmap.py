from ..rulesets.beatmap import Beatmap as BeatmapRuleset
from . import hitobjects

COLOR_PALLETE = [
    #( 255,   0,   0 ),
    ( 255, 0,   255 ),
    ( 255, 255,   0 ),
    #(   0, 255,   0 ),
    (   0, 255, 255 ),
    (   0,   0, 255 ),
]

class Beatmap:
    def __init__(self, beatmap: BeatmapRuleset):
        self.beatmap = beatmap
        self.last_new_combo = 0
        self.color_index = -1

    def render(self, screen, time):
        visible_objects = self.beatmap.visible_objects(time)

        if len(visible_objects) == 0:
            return

        preempt, fade_in = self.beatmap.approach_rate()

        if visible_objects[0].new_combo and visible_objects[0].time > self.last_new_combo:
            self.color_index += visible_objects[0].combo_skip + 1
            self.color_index %= len(COLOR_PALLETE)
            self.last_new_combo = visible_objects[0].time

        color_index = self.color_index

        circle_radius = int(self.beatmap.circle_radius())
        beat_duration = self.beatmap.beat_duration(time)

        for i in range(len(visible_objects)):
            obj = visible_objects[i]

            if obj.new_combo and obj.time > self.last_new_combo:
                color_index += obj.combo_skip + 1
                color_index %= len(COLOR_PALLETE)

            hitobjects.render(
                obj, time, screen,
                preempt, fade_in,
                COLOR_PALLETE[color_index],
                circle_radius,
                beat_duration,
                self.beatmap['SliderMultiplier']
            )

def from_beatmap(beatmap):
    return Beatmap(beatmap)