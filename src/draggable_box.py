import os
import inspect
import gi
gi.require_version("Gdk", "3.0")
from gi.repository import Clutter, Gdk

from . import util
from .resource_prefixes import *


# Bitwise flags to indicate clickable locations
NONE = 0
MIDDLE = 1 << 0
TOP = 1 << 1
BOT = 1 << 2
LEFT = 1 << 3
RIGHT = 1 << 4

# margin represents the hitbox dimension of the corners/sides
MARGIN = 10

# thickness of cropbox border
BORDER_THICKNESS = 2

# How much of the image stage should the crop box take up by default
DEFAULT_PROPORTION = 0.84

# How small the box can be sized
MIN_HEIGHT = 2 * MARGIN
MIN_WIDTH = 2 * MARGIN

# Maps bitwise flags to their Clutter enum values
CLUTTER_EDGES = {
    TOP: Clutter.SnapEdge.TOP,
    BOT: Clutter.SnapEdge.BOTTOM,
    LEFT: Clutter.SnapEdge.LEFT,
    RIGHT: Clutter.SnapEdge.RIGHT
}

# Maps regions to the GdkCursor which should be visible there
CURSOR_DICT = {
    NONE: Gdk.Cursor(Gdk.CursorType.ARROW),
    MIDDLE: Gdk.Cursor(Gdk.CursorType.FLEUR),
    LEFT: Gdk.Cursor(Gdk.CursorType.SB_H_DOUBLE_ARROW),
    RIGHT: Gdk.Cursor(Gdk.CursorType.SB_H_DOUBLE_ARROW),
    TOP: Gdk.Cursor(Gdk.CursorType.SB_V_DOUBLE_ARROW),
    BOT: Gdk.Cursor(Gdk.CursorType.SB_V_DOUBLE_ARROW),
    TOP|LEFT: Gdk.Cursor(Gdk.CursorType.TOP_LEFT_CORNER),
    TOP|RIGHT: Gdk.Cursor(Gdk.CursorType.TOP_RIGHT_CORNER),
    BOT|LEFT: Gdk.Cursor(Gdk.CursorType.BOTTOM_LEFT_CORNER),
    BOT|RIGHT: Gdk.Cursor(Gdk.CursorType.BOTTOM_RIGHT_CORNER)
}

# Color and opacity of the region surrounding the cropbox
BACKGROUND_COLOR = Clutter.Color.from_string("#000000")[1]
BACKGROUND_OPACITY_PCT = 0.6
BACKGROUND_OPACITY = int(255 * BACKGROUND_OPACITY_PCT)

CURRENT_FILE = os.path.abspath(inspect.getfile(inspect.currentframe()))
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
BASE_IMAGE_PATH = os.path.join(CURRENT_DIR, os.pardir) + '/data/images/'

class DraggableBox(Clutter.Actor):

    def __init__(self, stage, **kw):
        kw["opacity"] = 0
        kw["reactive"] = True
        super(DraggableBox, self).__init__(**kw)

        drag_action = Clutter.DragAction()
        self.add_action(drag_action)

        self._last_region = 0

        self.stage = stage
        self.surrounding_squares = self.init_surrounding_squares()
        self.draggable_handles = self.init_draggable_handles()
        self.draggable_borders = self.init_draggable_borders()
        self.reset_dimensions()

        self.stage.add_child(self)
        for square in self.surrounding_squares:
            square.connect("enter-event", self.mouse_leave_handler)
            self.stage.add_child(square)

        for border in self.draggable_borders:
            self.stage.add_child(border)

        for handle in self.draggable_handles:
            self.stage.add_child(handle)

        drag_action.connect("drag-progress", self.drag_progress_handler)
        self.connect("enter-event", self.mouse_enter_handler)
        self.get_parent().connect("leave-event", self.mouse_leave_handler)

    # Given the width/height of the total image stage, position
    # the cropbox in the middle of the screen and size its width/height
    # to be a DEFAULT_PROPORTION of the total
    def resize(self, stage_width, stage_height):
        new_width = self.width_as_pct * stage_width
        new_height = self.height_as_pct * stage_height
        new_x = self.x_pos_as_pct * stage_width
        new_y = self.y_pos_as_pct * stage_height

        self.set_x(new_x)
        self.set_y(new_y)
        self.set_width(new_width)
        self.set_height(new_height)

    def set_crop_selection_coordinates(self, coordinates, real_width, real_height):
        # Coordinates are in the same format output by get_crop_selection_coordinates
        # i.e. left_coord is the dist from the stage's left side to the box's left side,
        # right_coord is the dist from the stage's left side to the box's right side, etc.
        if coordinates is None:
            self.reset_dimensions()
        else:
            left_coord, top_coord, right_coord, bot_coord = list(map(float, coordinates))
            stage_width, stage_height = self.stage.get_width(), self.stage.get_height()

            self.x_pos_as_pct = left_coord / real_width
            self.y_pos_as_pct = top_coord / real_height
            self.width_as_pct = right_coord / real_width - self.x_pos_as_pct
            self.height_as_pct = bot_coord / real_height - self.y_pos_as_pct

    def reset_dimensions(self):
        # The box will store its position/dimensions as percentages of the total stage,
        # (values between 0 and 1) so that upon stage resizing/rotation, its dimensions
        # can be reconstructed faithfully
        self.x_pos_as_pct = (1 - DEFAULT_PROPORTION) / 2
        self.y_pos_as_pct = (1 - DEFAULT_PROPORTION) / 2
        self.width_as_pct = DEFAULT_PROPORTION
        self.height_as_pct = DEFAULT_PROPORTION

    def rotate_dimensions(self):
        # rotates the box's dimensions 90 degrees clockwise
        new_x_pct = 1 - self.y_pos_as_pct - self.height_as_pct
        new_y_pct = self.x_pos_as_pct

        self.x_pos_as_pct, self.y_pos_as_pct = new_x_pct, new_y_pct
        self.width_as_pct, self.height_as_pct = self.height_as_pct, self.width_as_pct

    def get_crop_selection_coordinates(self, real_width, real_height):
        # Dimensions of the crop box need to be scaled to the actual height
        # and width of the image, rather than the scaled version shown
        # in the canvas stage
        x, y = self.get_x(), self.get_y()
        width, height = self.get_width(), self.get_height()
        stage_width, stage_height = self.stage.get_width(), self.stage.get_height()

        left_coord = (x / stage_width) * real_width
        top_coord = (y / stage_height) * real_height
        right_coord = ((x + width) / stage_width) * real_width
        bot_coord = ((y + height) / stage_height) * real_height

        return list(map(int, (left_coord, top_coord, right_coord, bot_coord)))

    def opposing_side(self, side):
        if side & TOP or side & BOT:
            return side ^ (TOP | BOT)
        elif side & MIDDLE:
            return side
        else:
            return side ^ (LEFT | RIGHT)

    def init_draggable_borders(self):
        # Setup the borders which lay between the draggable handles
        borders = []
        coordinates = [TOP, BOT, LEFT, RIGHT]

        for coordinate in coordinates:
            border_wrapper = DraggableBorder(self, coordinate)
            border = border_wrapper.line
            border_hitbox = border_wrapper.hitbox

            # Each border has four constraints:
            #   cropbox_edge_constraint: binds the border's x/y position to the respective edge
            #       of the cropbox
            #   thickness_constraint: binds the height/width of the border to the same edge, in
            #       order to maintain a constant thickness
            #   length_constraint (1 & 2): these two bind the two loose ends of the border to the
            #       cropbox's corners
            # Its hitbox is constrained in the same fashion as its length_constraints, but also has
            # a positional constraint to the border
            cropbox_edge_constraint = Clutter.SnapConstraint()
            cropbox_edge_constraint.set_source(self)
            thickness_constraint = Clutter.SnapConstraint()
            thickness_constraint.set_source(self)

            wrapper_constraint_1 = Clutter.SnapConstraint()
            wrapper_constraint_1.set_source(self)
            wrapper_constraint_2 = Clutter.SnapConstraint()
            wrapper_constraint_2.set_source(self)
            wrapper_pos_constraint = Clutter.BindConstraint()
            wrapper_pos_constraint.set_source(border)
            length_constraint_1 = Clutter.SnapConstraint()
            length_constraint_1.set_source(self)
            length_constraint_2 = Clutter.SnapConstraint()
            length_constraint_2.set_source(self)

            if coordinate & TOP or coordinate & LEFT:
                thickness_offset = border_wrapper.get_offset()
            else:
                thickness_offset = -border_wrapper.get_offset()

            cropbox_edge_constraint.set_edges(
                CLUTTER_EDGES[coordinate], CLUTTER_EDGES[coordinate])

            thickness_constraint.set_edges(
                CLUTTER_EDGES[self.opposing_side(coordinate)], CLUTTER_EDGES[coordinate])
            thickness_constraint.set_offset(thickness_offset)

            wrapper_pos_constraint.set_coordinate(Clutter.BindCoordinate.POSITION)
            wrapper_pos_constraint.set_offset(-MARGIN / 2)

            if coordinate & TOP or coordinate & BOT:
                length_constraint_1.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[LEFT])
                length_constraint_2.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[RIGHT])
                wrapper_constraint_1.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[LEFT])
                wrapper_constraint_2.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[RIGHT])
                border_hitbox.set_height(MARGIN)
            else:
                length_constraint_1.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])
                length_constraint_2.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])
                wrapper_constraint_1.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])
                wrapper_constraint_2.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])
                border_hitbox.set_width(MARGIN)

            border.add_constraint(cropbox_edge_constraint)
            border.add_constraint(thickness_constraint)
            border.add_constraint(length_constraint_1)
            border.add_constraint(length_constraint_2)
            border_hitbox.add_constraint(wrapper_constraint_1)
            border_hitbox.add_constraint(wrapper_constraint_2)
            border_hitbox.add_constraint(wrapper_pos_constraint)

            borders.append(border_wrapper)

        return borders

    def init_draggable_handles(self):
        # Setup the four handles on the cropbox's corners. These are inset into the corners
        # of the cropbox, and don't actually spill over onto the image stage; the illusion
        # of their outward-facing corners overlapping the stage is made by offsetting the
        # opaque squares slightly onto the cropbox
        handles = []
        coordinates = [TOP|LEFT, TOP|RIGHT, BOT|LEFT, BOT|RIGHT]

        for coordinate in coordinates:
            handle = DraggableHandle(self, coordinate)

            # Each handle has four constraints:
            #   horiz_constraint: binds the handle to the cropbox's top/bottom sides
            #   vert_constraint: binds the handle to the cropbox's left/right sides
            #   width_constraint: binds the handle such that its width stays constant
            #   height_constraint: binds the handle such that its height stays constant
            #
            # The height/width constraints are set by binding the opposite side of the handle
            # that horiz/vert constraints bind (respectively) to the same edge of the cropbox,
            # and setting an offset equal to the desired height/width. The handle's hitbox is
            # constrainted by position to the handle image

            horiz_constraint = Clutter.SnapConstraint()
            horiz_constraint.set_source(self)
            vert_constraint = Clutter.SnapConstraint()
            vert_constraint.set_source(self)

            height_constraint = Clutter.SnapConstraint()
            height_constraint.set_source(self)
            width_constraint = Clutter.SnapConstraint()
            width_constraint.set_source(self)

            hitbox_pos_constraint = Clutter.BindConstraint()
            hitbox_pos_constraint.set_source(handle.current_knob)
            hitbox_pos_constraint.set_offset(4)
            hitbox_pos_constraint.set_coordinate(Clutter.BindCoordinate.POSITION)

            offset = handle.get_offset()
            if coordinate & TOP:
                horiz_constraint.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])
                height_constraint.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[TOP])
                horiz_constraint.set_offset(BORDER_THICKNESS/2 - offset)
                height_constraint.set_offset(BORDER_THICKNESS/2 - offset)
            else:
                horiz_constraint.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])
                height_constraint.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[BOT])
                horiz_constraint.set_offset(-(BORDER_THICKNESS/2 + offset))
                height_constraint.set_offset(-(BORDER_THICKNESS/2 + offset))

            if coordinate & LEFT:
                vert_constraint.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[LEFT])
                width_constraint.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[LEFT])
                vert_constraint.set_offset(BORDER_THICKNESS/2 - offset)
                width_constraint.set_offset(BORDER_THICKNESS/2 - offset)
            else:
                vert_constraint.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[RIGHT])
                width_constraint.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[RIGHT])
                vert_constraint.set_offset(-(BORDER_THICKNESS/2 + offset))
                width_constraint.set_offset(-(BORDER_THICKNESS/2 + offset))

            handle.add_constraint(height_constraint)
            handle.add_constraint(width_constraint)
            handle.add_constraint(horiz_constraint)
            handle.add_constraint(vert_constraint)
            handle.hitbox.add_constraint(hitbox_pos_constraint)

            handles.append(handle)

        return handles

    def init_surrounding_squares(self):
        # Setup the four opaque squares which cover the part
        # of the photo which isn't in the crop box
        squares = []
        coordinates = [TOP, BOT, LEFT, RIGHT]

        # Roughly, the stage looks like this:
        # +---------------------+
        # |         TOP         |
        # |---------------------|
        # | LEFT | CROP | RIGHT |
        # |---------------------|
        # |         BOT         |
        # +---------------------+
        # Each box (except for CROP) is bound by their respective
        # edge of the CROP box (i.e. RIGHT's left side is bound to
        # CROP's right side), as well as adjacent sides of the clutter
        # stage

        for coordinate in coordinates:
            square = Clutter.Actor()
            square.set_reactive(True)
            square.set_background_color(BACKGROUND_COLOR)
            square.set_opacity(BACKGROUND_OPACITY)

            if coordinate & TOP or coordinate & BOT:
                # Both the TOP and BOT squares are bound on their right
                # side to the right side of the stage; likewise for left
                right_constraint = Clutter.SnapConstraint()
                right_constraint.set_source(self.stage)
                right_constraint.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[RIGHT])

                left_constraint = Clutter.SnapConstraint()
                left_constraint.set_source(self.stage)
                left_constraint.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[LEFT])

                square.add_constraint(left_constraint)
                square.add_constraint(right_constraint)

            if coordinate & LEFT or coordinate & RIGHT:
                # The LEFT and RIGHT squares have their top and bottom edges
                # bound to the top and bottom edges of the CROP box
                top_constraint = Clutter.SnapConstraint()
                top_constraint.set_source(self)
                top_constraint.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])

                bot_constraint = Clutter.SnapConstraint()
                bot_constraint.set_source(self)
                bot_constraint.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])

                square.add_constraint(top_constraint)
                square.add_constraint(bot_constraint)

            # All the boxes have their namesake's edge bound to the same
            # named edge of the stage, and have the opposite side bound to their
            # namesake's edge of CROP.
            #
            # For example, LEFT's left side is bound to the left edge of
            # the stage, and LEFT's right side is bound to the left side of CROP

            cropbox_constraint = Clutter.SnapConstraint()
            cropbox_constraint.set_source(self)
            cropbox_constraint.set_edges(CLUTTER_EDGES[self.opposing_side(coordinate)], CLUTTER_EDGES[coordinate])

            stage_constraint = Clutter.SnapConstraint()
            stage_constraint.set_source(self.stage)
            stage_constraint.set_edges(CLUTTER_EDGES[coordinate], CLUTTER_EDGES[coordinate])

            square.add_constraint(cropbox_constraint)
            square.add_constraint(stage_constraint)

            squares.append(square)

        return squares

    def set_view(self, view):
        self._view = view

    # Called whenever an actor detects that the mouse has entered its region
    def mouse_changed_region(self, region):
        if region is not self._last_region:
            self._last_region = region

            # Set the cursor based on the pointer's location
            self._view.set_cursor(CURSOR_DICT[region])

            # Metrics for whether a handle or border should be highlighted. An ornament is
            # highlighted if it or an adjacent ornament is moused over, or if the mouse is
            # over the middle section of the cropbox
            is_middle = (region == MIDDLE)
            isnt_handle = not (region == NONE or region & (region - 1))
            border_is_selected = \
                lambda b: b.coordinate & region or is_middle
            handle_is_selected = \
                lambda h: (isnt_handle and h.coordinate & region) \
                            or (h.coordinate == region) or is_middle

            selected_borders = [b for b in self.draggable_borders if border_is_selected(b)]
            unselected_borders = [b for b in self.draggable_borders if b not in selected_borders]
            selected_handles = [h for h in self.draggable_handles if handle_is_selected(h)]
            unselected_handles = [h for h in self.draggable_handles if h not in selected_handles]

            # highlight the relevant handles and edges
            for border in selected_borders:
                border.highlight()
            for border in unselected_borders:
                border.darken()
            for handle in selected_handles:
                handle.highlight()
            for handle in unselected_handles:
                handle.normalize() if region == NONE else handle.darken()

    def mouse_enter_handler(self, actor, event):
        self.mouse_changed_region(MIDDLE)

    def mouse_leave_handler(self, actor, event):
        self.mouse_changed_region(NONE)

    def drag_progress_handler(self, action, actor, dx, dy):
        self.update_box_geometry(MIDDLE, dx, dy)

    # Return a value of dx such that the crop box's width will never
    # be lower than the MIN_WIDTH, and so that the crop box's left/right
    # sides will never move outside the bounds of the image stage
    def validate_dx(self, dx, clicked_region):
        # If the user is dragging either the left/right side, check if
        # the width of the box would be reduced to less than MIN_WIDTH
        # given dx. If so, return a value for dx which would reduce the width
        # to exactly MIN_WIDTH
        if clicked_region & LEFT:
            if self.get_width() - dx < MIN_WIDTH:
                return self.get_width() - MIN_WIDTH
        if clicked_region & RIGHT:
            if self.get_width() + dx < MIN_WIDTH:
                return MIN_WIDTH - self.get_width()

        # If the user is moving the left/right sides (either by dragging the
        # respective side, or by dragging the whole box), trim dx if it'd cause
        # the current x coordinate to be less than 0 or greater than the width
        # of the image stage
        if clicked_region & (LEFT | MIDDLE):
            if self.get_x() + dx < 0:
                return -self.get_x()
        if clicked_region & (RIGHT | MIDDLE):
            if self.get_x() + self.get_width() + dx > self.get_parent().get_width():
                return self.get_parent().get_width() - (self.get_x() + self.get_width())
        return dx

    # Nearly exactly as in validate_dy, trim the value of dy if it'd result
    # in the height of the box being too small, or if dy would place either
    # the top or bottom edges outside the bounds of the image stage
    def validate_dy(self, dy, clicked_region):
        if clicked_region & TOP:
            if self.get_height() - dy < MIN_HEIGHT:
                return self.get_height() - MIN_HEIGHT
        if clicked_region & BOT:
            if self.get_height() + dy < MIN_HEIGHT:
                return MIN_HEIGHT - self.get_height()

        if clicked_region & (TOP | MIDDLE):
            if self.get_y() + dy < 0:
                return -self.get_y()
        if clicked_region & (BOT | MIDDLE):
            if self.get_y() + self.get_height() + dy > self.get_parent().get_height():
                return self.get_parent().get_height() - (self.get_y() + self.get_height())
        return dy

    def update_box_geometry(self, clicked_region, dx, dy):
        # Ensure dx and dy would adjust the crop box's geometry within
        # the minimum size and bounded region constraints
        dx = self.validate_dx(dx, clicked_region)
        dy = self.validate_dy(dy, clicked_region)

        if not clicked_region & MIDDLE:
            # If the click was on the left side, we need to both
            # add the inverse of the dragged distance and simultaneously
            # move the position of the box (to simulate the manipulation
            # of the left side). If it was on the right, just add the
            # dragged distance to the size of the pre-dragged dimensions
            if clicked_region & LEFT:
                self.set_width(self.get_width() - dx)
                self.set_x(self.get_x() + dx)
            elif clicked_region & RIGHT:
                self.set_width(self.get_width() + dx)

            if clicked_region & TOP:
                self.set_height(self.get_height() - dy)
                self.set_y(self.get_y() + dy)
            elif clicked_region & BOT:
                self.set_height(self.get_height() + dy)
        else:
            # If the click happened away from either horizontal or
            # vertical edges, just drag the box around
            self.set_x(self.get_x() + dx)
            self.set_y(self.get_y() + dy)

class DraggableOrnament(Clutter.Group):
    """
    Base class for an object which forwards mouse events to the crop box. The hitbox actor is kept
    separate from any other visual actors so that the ornament can receieve events over a wider
    region than what is actually visible to the user
    """
    def __init__(self, box, coordinate, **kw):
        kw["reactive"] = True
        super(DraggableOrnament, self).__init__(**kw)

        self.draggable_box = box
        self.coordinate = coordinate

        self.hitbox = Clutter.Actor()
        self.hitbox.set_reactive(True)

        drag_action = Clutter.DragAction()
        drag_action.connect("drag-progress", self.drag_progress_handler)

        self.hitbox.add_action(drag_action)
        self.hitbox.connect("enter-event", self.mouse_enter_handler)

    def drag_progress_handler(self, actor, action, dx, dy):
        self.draggable_box.update_box_geometry(self.coordinate, dx, dy)

    def mouse_enter_handler(self, x, y):
        self.draggable_box.mouse_changed_region(self.coordinate)


class DraggableHandle(DraggableOrnament):
    def __init__(self, *args):
        super(DraggableHandle, self).__init__(*args)
        self.dimension = MARGIN
        self.current_knob = None

        self.hitbox.set_height(self.dimension)
        self.hitbox.set_width(self.dimension)

        self.NORMAL_KNOB = util.load_clutter_image_from_resource(IMAGES_RESOURCE_PREFIX + "crop_knob_normal.png")
        self.LIGHT_KNOB = util.load_clutter_image_from_resource(IMAGES_RESOURCE_PREFIX + "crop_knob_hover.png")
        self.DARK_KNOB = util.load_clutter_image_from_resource(IMAGES_RESOURCE_PREFIX + "crop_knob_dark.png")

        dummy, knob_width, knob_height = self.NORMAL_KNOB.get_preferred_size()
        self.current_knob = Clutter.Actor(width=knob_width, height=knob_height, content=self.NORMAL_KNOB)
        self.add_child(self.current_knob)
        self.add_child(self.hitbox)

    def highlight(self):
        self.current_knob.set_content(self.LIGHT_KNOB)

    def darken(self):
        self.current_knob.set_content(self.DARK_KNOB)

    def normalize(self):
        self.current_knob.set_content(self.NORMAL_KNOB)

    def get_offset(self):
        return (self.get_width() / 2)

class DraggableBorder(DraggableOrnament):
    def __init__(self, *args):
        super(DraggableBorder, self).__init__(*args)

        self.line = Clutter.Actor()
        self.add_child(self.line)
        self.add_child(self.hitbox)

        self.thickness = BORDER_THICKNESS
        self.NORMAL_COLOR = Clutter.Color.from_string("#000000")[1]
        self.HIGHLIGHT_COLOR = Clutter.Color.from_string("#FFFFFF")[1]
        self.darken()

    def highlight(self):
        self.line.set_background_color(self.HIGHLIGHT_COLOR)

    def darken(self):
        self.line.set_background_color(self.NORMAL_COLOR)

    def get_offset(self):
        return self.thickness
