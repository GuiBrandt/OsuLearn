import math
from datetime import time

from . import core, hitobjects, timing_points
from .util.bsearch import bsearch

import re


_SECTION_TYPES = {
	'General':      'a',
	'Editor':       'a',
	'Metadata':     'a',
	'Difficulty':   'a',
	'Events':       'b',
	'TimingPoints': 'b',
	'Colours':      'a',
	'HitObjects':   'b'
}

class _BeatmapFile:
	def __init__(self, file):
		self.file = file
		self.format_version = self.file.readline()

	def read_all_sections(self):
		sections = {}
		section = self._read_section_header()
		while section != None:
			func = "_read_type_%s_section" % _SECTION_TYPES[section]
			section_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', section).lower()

			sections[section_name] = getattr(self, func)()
			section = self._read_section_header()

		return sections

	def _read_section_header(self):
		header = self.file.readline()
		while header != '' and re.match(r"[^\n\r\s]", header) == None:
			header = self.file.readline()
			
		m = re.match(r"^\s*\[(\S+)\]\s*$", header)

		if m is None:
			return None
		
		return m[1]

	def _parse_value(self, v):
		if v.isdigit():
			return int(v)
		elif v.replace('.', '', 1).isdigit():
			return float(v)
		else:
			return v
		
	# Seção do tipo Chave: Valor
	def _read_type_a_section(self):
		d = dict()

		line = self.file.readline()
		while line != '' and re.match(r"[^\n\r\s]", line) != None:
			m = re.match(r"^\s*(\S+)\s*:\s*(.*)\s*\r?\n$", line)
			if m is None:
				raise RuntimeError("Invalid file")
			else:
				d[m[1]] = self._parse_value(m[2])

			line = self.file.readline()

		return d

	# Seção do tipo a,b,c,...,d
	def _read_type_b_section(self):
		l = list()

		line = self.file.readline()
		while line != '' and re.match(r"[^\n\r\s]", line) != None:
			l.append(list(map(self._parse_value, line.rstrip("\r\n").split(','))))
			line = self.file.readline()

		return l

class Beatmap:	
	def __init__(self, file):
		file = _BeatmapFile(file)

		self.format_version = file.format_version
		self.sections = file.read_all_sections()

		if 'timing_points' in self.sections:
			self.timing_points = list(map(timing_points.create, self.sections['timing_points']))
			del self.sections['timing_points']

		if 'hit_objects' in self.sections:
			self.hit_objects = list(map(hitobjects.create, self.sections['hit_objects']))
			del self.sections['hit_objects']

	def combo_color(self, new_combo, combo_skip):
		return (255, 0, 0)

	def __getattr__(self, key):
		if key in self.sections:
			return self.sections[key]
		else:
			return []
		
	def __getitem__(self, key):
		for section in self.sections.values():
			if key in section:
				return section[key]
		return None
	
	def approach_rate(self):
		ar = self["ApproachRate"]
		if ar <= 5:
			preempt = 1200 + 600 * (5 - ar) / 5
			fade_in = 800 + 400 * (5 - ar) / 5
		else:
			preempt = 1200 - 750 * (ar - 5) / 5
			fade_in = 800 - 500 * (ar - 5) / 5
		return preempt, fade_in

	def circle_radius(self):
		return 27.2 - 2.24 * self['CircleSize']

	def length(self):
		if len(self.hit_objects) == 0:
			return 0
		return int(self.hit_objects[-1].time + self.hit_objects[-1].duration(self))

	def timing(self, time):
		bpm = None
		i = bsearch(self.timing_point, time, lambda tp: tp.time)
		timing_point = self.timing_points[i - 1]

		for tp in self.timing_points[i:]:
			if tp.offset > time:
				break
			if tp.bpm > 0:
				bpm = tp.bpm
			timing_point = tp

		while i >= 0 and bpm is None:
			i -= 1
			if self.timing_points[i].bpm > 0:
				bpm = self.timing_points[i]

		return bpm or 120, timing_point

	# Pega os objetos visíveis na tela em dado momento
	def visible_objects(self, time, count=None):
		r = []
		preempt, _ = self.approach_rate()

		i = bsearch(self.hit_objects, time, lambda obj: obj.time - preempt)
		i -= 10
		i = max([0, i])
		
		n = 0

		for obj in self.hit_objects[i:]:
			if time > obj.time + obj.duration(self):
				continue

			if time < obj.time - preempt:
				break
				
			if time < obj.time + obj.duration(self):
				r.append(obj)

			n += 1

			if not count is None and n >= count:
				return r
			
		return r

def load(filename):
	with open(filename, 'r', encoding='utf8') as file:
		return Beatmap(file)