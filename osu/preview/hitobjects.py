import pygame

from ..rulesets import hitobjects as hitobjects

def _render_hitcircle(hitcircle, time:int, screen:pygame.Surface, preempt: float, fade_in: float, color:pygame.Color, circle_radius:int, *args):
	surface = pygame.Surface((circle_radius * 2, circle_radius * 2))
	surface.set_colorkey((0, 0, 0))
	pygame.draw.circle(surface, color, (circle_radius, circle_radius), circle_radius)

	alpha = min([1, (time - hitcircle.time + preempt) / fade_in])
	surface.set_alpha(alpha * 127)
	
	pos = (hitcircle.x - circle_radius, hitcircle.y - circle_radius)
	screen.blit(surface, pos)


def _render_slider(slider, time:int, screen:pygame.Surface, preempt: float, fade_in: float,  color:pygame.Color, circle_radius:int, beat_duration:float, multiplier:float=1.0):
	start_pos = (slider.x, slider.y)
	vertices = [start_pos] + slider.curve_points
	pygame.draw.lines(screen, (255, 255, 255), False, vertices)

	_render_hitcircle(slider,  time, screen, preempt, fade_in, color, circle_radius)
	
	pos = slider.target_position(time, beat_duration, multiplier)
	pygame.draw.circle(screen, (255, 255, 255), list(map(int, pos)), circle_radius, 1)


SPINNER_RADIUS = 128


def _render_spinner(spinner, time:int, screen:pygame.Surface,  *args):
	pos = (spinner.x, spinner.y)
	pygame.draw.circle(screen, (255, 255, 255), pos, SPINNER_RADIUS, 2)


def render(obj:hitobjects.HitObject, time:int, screen:pygame.Surface, *args):
	if isinstance(obj, hitobjects.HitCircle):
		_render_hitcircle(obj, time, screen, *args)
	if isinstance(obj, hitobjects.Slider):
		_render_slider(obj, time, screen, *args)
	if isinstance(obj, hitobjects.Spinner):
		_render_spinner(obj, time, screen, *args)