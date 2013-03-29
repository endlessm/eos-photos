import cairo
import math

from gi.repository import Gtk,Gdk

class DropShadowAlignment(Gtk.Alignment):
	DROP_SHADOW_WIDTH = 8

	def __init__(self, shadowed_widget=None, **kw):
		super(DropShadowAlignment, self).__init__(**kw)
		self._shadowed_widget = shadowed_widget
		self.set_app_paintable(True)
		self.connect('draw', self._image_border_gradient_draw)

	def _image_border_gradient_draw(self, w, cr):
		shadowed_widget_allocation = self._shadowed_widget.get_allocation()

		image_x, image_y = shadowed_widget_allocation.x, shadowed_widget_allocation.y
		image_width, image_height = shadowed_widget_allocation.width, shadowed_widget_allocation.height
		horizontal_offset = image_x - self.get_allocation().x
		vertical_offset = image_y - self.get_allocation().y # Minus 1 pixel due to offset error, possibly due to resizing.

		# Top drop shadow.
		linear_pattern = cairo.LinearGradient(horizontal_offset, vertical_offset, horizontal_offset,
		vertical_offset - DropShadowAlignment.DROP_SHADOW_WIDTH)
		linear_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.5)
		linear_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(linear_pattern)
		cr.move_to(horizontal_offset, vertical_offset)
		cr.line_to(horizontal_offset + image_width, vertical_offset)
		cr.line_to(horizontal_offset + image_width, vertical_offset - DropShadowAlignment.DROP_SHADOW_WIDTH)
		cr.line_to(horizontal_offset, vertical_offset - DropShadowAlignment.DROP_SHADOW_WIDTH)
		cr.fill()

		# Left drop shadow.
		linear_pattern = cairo.LinearGradient(horizontal_offset, vertical_offset, horizontal_offset - DropShadowAlignment.DROP_SHADOW_WIDTH,
		vertical_offset)
		linear_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.5)
		linear_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(linear_pattern)
		cr.move_to(horizontal_offset, vertical_offset)
		cr.line_to(horizontal_offset - DropShadowAlignment.DROP_SHADOW_WIDTH, vertical_offset)
		cr.line_to(horizontal_offset - DropShadowAlignment.DROP_SHADOW_WIDTH, vertical_offset + image_height)
		cr.line_to(horizontal_offset, vertical_offset + image_height)
		cr.fill()

		# Right drop shadow.
		linear_pattern = cairo.LinearGradient(horizontal_offset + image_width, vertical_offset, horizontal_offset + image_width + DropShadowAlignment.DROP_SHADOW_WIDTH,
		vertical_offset)
		linear_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.5)
		linear_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(linear_pattern)
		cr.move_to(horizontal_offset + image_width, vertical_offset)
		cr.line_to(horizontal_offset + image_width + DropShadowAlignment.DROP_SHADOW_WIDTH, vertical_offset)
		cr.line_to(horizontal_offset + image_width + DropShadowAlignment.DROP_SHADOW_WIDTH, vertical_offset + image_height)
		cr.line_to(horizontal_offset + image_width, vertical_offset + image_height)
		cr.fill()

		# Bottom drop shadow.
		linear_pattern = cairo.LinearGradient(horizontal_offset, vertical_offset + image_height, horizontal_offset,
		vertical_offset + image_height + DropShadowAlignment.DROP_SHADOW_WIDTH)
		linear_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.5)
		linear_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(linear_pattern)
		cr.move_to(horizontal_offset, vertical_offset + image_height)
		cr.line_to(horizontal_offset + image_width, vertical_offset + image_height)
		cr.line_to(horizontal_offset + image_width, vertical_offset + image_height + DropShadowAlignment.DROP_SHADOW_WIDTH)
		cr.line_to(horizontal_offset, vertical_offset + image_height + DropShadowAlignment.DROP_SHADOW_WIDTH)
		cr.fill()

		# Top left corner drop shadow.
		CORNER_SHADOW_RADIUS = DropShadowAlignment.DROP_SHADOW_WIDTH
		radial_pattern = cairo.RadialGradient(horizontal_offset, vertical_offset, 0,
		horizontal_offset, vertical_offset, CORNER_SHADOW_RADIUS)
		radial_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.3)
		radial_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(radial_pattern)
		cr.move_to(horizontal_offset, vertical_offset)
		cr.line_to(horizontal_offset - CORNER_SHADOW_RADIUS, vertical_offset)
		cr.arc(horizontal_offset, vertical_offset, CORNER_SHADOW_RADIUS, math.pi, (math.pi * 3) / 2)
		cr.fill()

		# Top right corner drop shadow.
		CORNER_SHADOW_RADIUS = DropShadowAlignment.DROP_SHADOW_WIDTH
		radial_pattern = cairo.RadialGradient(horizontal_offset + image_width, vertical_offset, 0,
		horizontal_offset + image_width, vertical_offset, CORNER_SHADOW_RADIUS)
		radial_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.3)
		radial_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(radial_pattern)
		cr.move_to(horizontal_offset + image_width, vertical_offset)
		cr.line_to(horizontal_offset + image_width, vertical_offset - CORNER_SHADOW_RADIUS)
		cr.arc(horizontal_offset + image_width, vertical_offset, CORNER_SHADOW_RADIUS, (math.pi * 3) / 2, 0)
		cr.fill()

		# Bottom right corner drop shadow.
		CORNER_SHADOW_RADIUS = DropShadowAlignment.DROP_SHADOW_WIDTH
		radial_pattern = cairo.RadialGradient(horizontal_offset + image_width, vertical_offset + image_height, 0,
		horizontal_offset + image_width, vertical_offset + image_height, CORNER_SHADOW_RADIUS)
		radial_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.3)
		radial_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(radial_pattern)
		cr.move_to(horizontal_offset + image_width, vertical_offset + image_height)
		cr.line_to(horizontal_offset + image_width + CORNER_SHADOW_RADIUS, vertical_offset + image_height)
		cr.arc(horizontal_offset + image_width, vertical_offset + image_height, CORNER_SHADOW_RADIUS, 0, math.pi / 2)
		cr.fill()

		# Bottom left corner drop shadow.
		CORNER_SHADOW_RADIUS = DropShadowAlignment.DROP_SHADOW_WIDTH
		radial_pattern = cairo.RadialGradient(horizontal_offset, vertical_offset + image_height, 0,
		horizontal_offset, vertical_offset + image_height, CORNER_SHADOW_RADIUS)
		radial_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.3)
		radial_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.0)

		cr.set_source(radial_pattern)
		cr.move_to(horizontal_offset, vertical_offset + image_height)
		cr.line_to(horizontal_offset, vertical_offset + image_height + CORNER_SHADOW_RADIUS)
		cr.arc(horizontal_offset, vertical_offset + image_height, CORNER_SHADOW_RADIUS, math.pi / 2, math.pi)
		cr.fill()
