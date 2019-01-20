import math

from abc import ABC, abstractmethod
from enum import Enum, IntEnum, IntFlag

from . import core
from ._util import bezier

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
	def duration(self, beat_duration:float, multiplier:float=1.0):
		pass

	def target_position(self, time:int, beat_duration:float, multiplier:float=1.0):
		return (self.x, self.y)

class HitCircle(HitObject):
	def __init__(self, *args):
		super().__init__(*args)

	def duration(self, *args):
		return 0

class SliderType(Enum):
	LINEAR  = "L"
	BEZIER  = "B"
	PERFECT = "P"
	CATMUL  = "C"

class Slider(HitCircle):
	def __init__(self, *args):
		super().__init__(*args)

		slider_info = args[5].split("|")
		self.slider_type = SliderType(slider_info[0])
		self.curve_points = list(map(lambda p: tuple(map(int, p)), [p.split(':') for p in slider_info[1:]]))

		self.repeat = int(args[6])
		self.pixel_length = int(args[7])
		#self.edge_hitsounds = [HitSounds(int(h)) for h in args[8].split('|')]

		#additions = [e.split(":") for e in args[9].split('|')]
		#self.edge_additions = [(SampleSet(int(s)), SampleSet(int(a))) for s, a in additions]

	def duration(self, beat_duration:float, multiplier:float=1.0):
		return beat_duration * self.pixel_length / (100 * multiplier) * self.repeat

	def real_curve_points(self):
		points = []
		for i in range(1, self.repeat + 1):
			l = ([(self.x, self.y)] + self.curve_points)
			if i % 2 == 0:
				l = list(reversed(l))
			points += l
		return points

	class _Patch:
		def __init__(self, start_position, length:float=0.0, angle:float=0.0):
			self.x, self.y = start_position
			self.length = length
			self.angle = angle

	@staticmethod
	def _get_patches(curve_points):
		processed = []
		for i in range(len(curve_points) - 1):
			x, y = curve_points[i]
			next_x, next_y = curve_points[i + 1]

			dx = next_x - x
			dy = next_y - y
			distance = math.hypot(dx, dy)
			angle = math.atan2(dy, dx)

			processed.append(Slider._Patch((x, y), distance, angle))

		processed.append(Slider._Patch(curve_points[-1], 0, 0))
		return processed

	@staticmethod
	def _traverse_patches(elapsed, step, slider_track):
		while elapsed > 0:
			slider_track[0].length -= step
			if slider_track[0].length <= 0:
				if len(slider_track) > 2:
					slider_track.pop(0)
				else:
					break
			elapsed -= 1

	def current_curve_point(self, time:int, beat_duration:float, multiplier:float=1.0):
		elapsed = time - self.time
		if elapsed <= 0 or len(self.curve_points) == 0:
			return (self.x, self.y)

		duration = self.duration(beat_duration, multiplier)
		if elapsed >= duration:
			return self.curve_points[-1]

		curve_points = self.real_curve_points()
		slider_track = Slider._get_patches(curve_points)

		step = self.pixel_length / duration * self.repeat
		self._traverse_patches(elapsed, step, slider_track)

		if len(slider_track) < 2:
			return self.curve_points[-1]

		x = slider_track[1].x - math.cos(slider_track[0].angle) * slider_track[0].length
		y = slider_track[1].y - math.sin(slider_track[0].angle) * slider_track[0].length
		return (x, y)

	def target_position(self, time:int, beat_duration:float, multiplier:float=1.0):
		return self.current_curve_point(time, beat_duration, multiplier)

class Spinner(HitObject):
	def __init__(self, *args):
		super().__init__(*args)
		self.end_time = int(args[5])
		
	def duration(self, *args):
		return self.end_time - self.time

def create(obj):
	if obj[3] & HitObjectType.CIRCLE:
		return HitCircle(*obj)
	elif obj[3] & HitObjectType.SLIDER:
		return Slider(*obj)
	elif obj[3] & HitObjectType.SPINNER:
		return Spinner(*obj)