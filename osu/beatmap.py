import re
import math
	
CIRCLE_FADEOUT = 50
SLIDER_FADEOUT = 100

class Beatmap:
	
	SECTION_TYPES = {
		'General':      'a',
		'Editor':       'a',
		'Metadata':     'a',
		'Difficulty':   'a',
		'Events':       'b',
		'TimingPoints': 'b',
		'Colours':      'a',
		'HitObjects':   'b'
	}
	
	def _read_section_header(file):
		header = file.readline()
		while header != '' and re.match(r"[^\n\r\s]", header) == None:
			header = file.readline()
			
		m = re.match(r"^\s*\[(\S+)\]\s*$", header)

		if m is None:
			return None
		
		return m[1]
	
	def _parse_value(v):
		if v.isdigit():
			return int(v)
		elif v.replace('.', '', 1).isdigit():
			return float(v)
		else:
			return v
		
	# Seção do tipo Chave: Valor
	def _read_type_a_section(file):
		d = dict()

		line = file.readline()
		while line != '' and re.match(r"[^\n\r\s]", line) != None:
			m = re.match(r"^\s*(\S+)\s*:\s*(.*)\s*\r?\n$", line)
			if m is None:
				raise RuntimeError("Invalid file")
			else:
				d[m[1]] = Beatmap._parse_value(m[2])

			line = file.readline()

		return d

	# Seção do tipo a,b,c,...,d
	def _read_type_b_section(file):
		l = list()

		line = file.readline()
		while line != '' and re.match(r"[^\n\r\s]", line) != None:
			l.append(list(map(Beatmap._parse_value, line.rstrip("\r\n").split(','))))
			line = file.readline()

		return l
	
	def __init__(self, file):

		# Versão do formato
		self.format_version = file.readline()

		# Seções de informações do mapa
		self.sections = {}

		section = Beatmap._read_section_header(file)
		while section != None:
			func = "_read_type_%s_section" % Beatmap.SECTION_TYPES[section]
			section_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', section).lower()

			self.sections[section_name] = getattr(Beatmap, func)(file)

			section = Beatmap._read_section_header(file)
			
	def __getattr__(self, key):
		return self.sections[key]
		
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
	
	def timing_at(self, time):
		bpm = 0
		timing_point = self.timing_points[0]

		for tp in self.timing_points:
			if tp[0] > time:
				break
			d = float(tp[1])
			if d > 0:
				bpm = d
			timing_point = tp

		return bpm, timing_point

	def slider_duration(self, obj):
		bpm, timing_point = self.timing_at(obj[2])
		beat_duration = float(timing_point[1])

		if beat_duration < 0:
			beat_duration = bpm * -beat_duration / 100

		return beat_duration * obj[7] / (100 * self["SliderMultiplier"])

	# Pega os objetos visíveis na tela em dado momento
	def visible_objects(self, time):
		i = 0
		r = []
		
		preempt, fade = self.approach_rate()
		
		# Busca binária no tempo ideal
		beg, end = 0, len(self.hit_objects)
		while end < beg:
			i = (end + beg) // 2
			obj_time = self.hit_objects[i][2]

			if obj_time > time:
				end = i
			elif obj_time < time:
				beg = i
			else:
				break

		for obj in self.hit_objects[i:]:
			obj_time, obj_type = obj[2], obj[3]

			if time < obj_time:
				break
				
			if obj_type & 8 and time < obj[5]:
				r.append(obj)
			elif obj_type & 2:
				if time < obj_time + preempt + self.slider_duration(obj) + SLIDER_FADEOUT:
					r.append(obj)
			elif time < obj_time + preempt + CIRCLE_FADEOUT:
				r.append(obj)
			
		return r

def load(filename):
	with open(filename, 'r', encoding='utf8') as file:
		return Beatmap(file)