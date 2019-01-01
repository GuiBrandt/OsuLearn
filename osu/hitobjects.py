import pygame

from . import core

from .util import bezier

from abc import ABC, abstractmethod
from enum import Enum, IntEnum, IntFlag

class HitObjectType(IntFlag):
	CIRCLE          = 0b00000001
	SLIDER          = 0b00000010
	NEW_COMBO       = 0b00000100
	SPINNER         = 0b00001000
	COMBO_SKIP      = 0b01110000
	MANIA_HOLD      = 0b10000000

class HitSounds(IntFlag):
	NORMAL  = 0b0001
	WHISTLE = 0b0010
	FINISH  = 0b0100
	CLAP    = 0b1000

class SampleSet(IntEnum):
	AUTO    = 0
	NORMAL  = 1
	SOFT    = 2
	DRUM    = 3

class HitSoundExtras:
	def __init__(self, *args):
		self.sample_set = SampleSet(int(args[0]))
		self.addition_set = SampleSet(int(args[1]))
		self.customIndex = int(args[2])
		self.sampleVolume = int(args[3])
		self.filename = args[4]

class HitObject(ABC):
	def __init__(self, *args):
		self.x = int(args[0])
		self.y = int(args[1])
		self.time = int(args[2])
		self.new_combo = bool(int(args[3]) & HitObjectType.NEW_COMBO)
		self.combo_skip = int(args[3] & HitObjectType.COMBO_SKIP) >> 4
		self.hitsounds = HitSounds(int(args[4]))
		#self.extras = HitSoundExtras(*args[-1].split(":"))

	@abstractmethod
	def duration(self, beatmap):
		pass

	@abstractmethod
	def render(self, beatmap, screen: pygame.Surface, time: int):
		pass

class HitCircle(HitObject):
	def __init__(self, *args):
		super().__init__(*args)

	def duration(self, beatmap):
		return 0

	def render(self, beatmap, screen: pygame.Surface, time: int):
		pos = (self.x, self.y)
		color = beatmap.combo_color(self.new_combo, self.combo_skip)
		radius = beatmap.circle_radius()

		pygame.draw.circle(screen, color, pos, int(radius))

class SliderType(Enum):
	LINEAR  = "L"
	BEZIER  = "B"
	PERFECT = "P"
	CATMUL  = "C"

class Slider(HitCircle):
	def __init__(self, *args):
		super().__init__(*args)

		slider_info = args[5].split("|")
		self.slider_type = SliderType(slider_info.pop(0))

		coordinates = [t.split(':') for t in slider_info]
		self.curve_points = [(int(x), int(y)) for x, y in coordinates]

		self.repeat = int(args[6])
		self.pixel_length = int(args[7])
		#self.edge_hitsounds = [HitSounds(int(h)) for h in args[8].split('|')]

		#additions = [e.split(":") for e in args[9].split('|')]
		#self.edge_additions = [(SampleSet(int(s)), SampleSet(int(a))) for s, a in additions]

	def duration(self, beatmap):
		bpm, timing_point = beatmap.timing(self.time)
		beat_duration = timing_point.bpm

		if beat_duration < 0:
			beat_duration = bpm * -beat_duration / 100

		return beat_duration * self.pixel_length / (100 * beatmap["SliderMultiplier"])

	def render(self, beatmap, screen: pygame.Surface, time: int):

		vertices = [(self.x, self.y)] + self.curve_points
		pygame.draw.lines(screen, (255, 255, 255), False, vertices)

		super().render(beatmap, screen, time)
		
		end_pos = self.curve_points[-1]
		radius = beatmap.circle_radius()
		pygame.draw.circle(screen, (255, 255, 255), end_pos, int(radius), 1)

class Spinner(HitObject):
	RADIUS = 256

	def __init__(self, *args):
		super().__init__(*args)
		self.end_time = int(args[5])
		
	def duration(self, beatmap):
		return self.end_time - self.time

	def render(self, beatmap, screen: pygame.Surface, time: int):
		pos = (self.x, self.y)
		pygame.draw.circle(screen, (255, 255, 255), pos, Spinner.RADIUS, 2)

def create(obj):
	if obj[3] & HitObjectType.CIRCLE:
		return HitCircle(*obj)
	elif obj[3] & HitObjectType.SLIDER:
		return Slider(*obj)
	elif obj[3] & HitObjectType.SPINNER:
		return Spinner(*obj)