from gi.repository import Clutter, Gdk

# Bitwise flags to indicate clickable locations
NONE = 0
MIDDLE = 1 << 0
TOP = 1 << 1
BOT = 1 << 2
LEFT = 1 << 3
RIGHT = 1 << 4

# margin represents the hitbox dimension of the corners/sides
MARGIN = 10

# How much of the image stage should the crop box take up by default
DEFAULT_PROPORTION = 0.5

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
BACKGROUND_COLOR = Clutter.Color.from_string("#333333")[1]
BACKGROUND_OPACITY = 200

class DraggableBox(Clutter.Actor):
    
    def __init__(self, stage, **kw):
        kw["opacity"] = 0
        kw["reactive"] = True
        super(DraggableBox, self).__init__(**kw)

        drag_action = Clutter.DragAction()
        self.add_action(drag_action)

        self.drag_begin_dimensions = []
        self.drag_begin_coords = []
        self.clicked_region = 0
        self._last_region = 0

        self.stage = stage
        self.surrounding_squares = self.init_surrounding_squares()
        self.draggable_handles = self.init_draggable_handles()
        self.draggable_borders = self.init_draggable_borders()

        self.stage.add_child(self)
        for square in self.surrounding_squares:
            self.stage.add_child(square)

        for handle in self.draggable_handles:
            self.stage.add_child(handle)

        for border in self.draggable_borders:
            self.stage.add_child(border)

        drag_action.connect("drag-begin", self.drag_begin_handler)
        drag_action.connect("drag-progress", self.drag_progress_handler)
        self.connect("motion-event", self.mouse_motion_handler)
        self.connect("enter-event", self.mouse_motion_handler)
        self.connect("leave-event", self.mouse_leave_handler)

    # Given the width/height of the total image stage, position
    # the cropbox in the middle of the screen and size its width/height
    # to be a DEFAULT_PROPORTION of the total
    def resize(self, stage_width, stage_height):
        new_width = DEFAULT_PROPORTION * stage_width
        new_height = DEFAULT_PROPORTION * stage_height
        new_x = (stage_width - new_width) / 2
        new_y = (stage_height - new_height) / 2

        self.set_x(new_x)
        self.set_y(new_y)
        self.set_width(new_width)
        self.set_height(new_height)

    def get_crop_selection_coordinates(self, real_width, real_height):
        # Dimensions of the crop box need to be scaled to the actual height
        # and width of the image, rather than the scaled version shown
        # in the canvas stage
        x, y = self.get_x(), self.get_y()
        width, height = self.get_width(), self.get_height()
        stage_width, stage_height = self.stage.get_width(), self.stage.get_height()

        left_coord = int((x / stage_width) * real_width)
        top_coord = int((y / stage_height) * real_height)
        right_coord = int(((x + width) / stage_width) * real_width)
        bot_coord = int(((y + height) / stage_height) * real_height)

        return (left_coord, top_coord, right_coord, bot_coord)

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
            border = DraggableBorder()

            # Each border has four constraints:
            #   cropbox_edge_constraint: binds the border's x/y position to the respective edge
            #       of the cropbox
            #   thickness_constraint: binds the height/width of the border to the same edge, in
            #       order to maintain a constant thickness
            #   length_constraint (1 & 2): these two bind the two loose ends of the border to the
            #       cropbox's corners
            cropbox_edge_constraint = Clutter.SnapConstraint()
            cropbox_edge_constraint.set_source(self)
            thickness_constraint = Clutter.SnapConstraint()
            thickness_constraint.set_source(self)

            length_constraint_1 = Clutter.SnapConstraint()
            length_constraint_1.set_source(self)
            length_constraint_2 = Clutter.SnapConstraint()
            length_constraint_2.set_source(self)

            if coordinate & TOP or coordinate & LEFT:
                position_offset = border.get_offset()
                thickness_offset = position_offset + border.get_thickness()
            else:
                position_offset = -border.get_offset()
                thickness_offset = position_offset - border.get_thickness()

            cropbox_edge_constraint.set_edges(
                CLUTTER_EDGES[coordinate], CLUTTER_EDGES[coordinate])
            cropbox_edge_constraint.set_offset(position_offset)

            thickness_constraint.set_edges(
                CLUTTER_EDGES[self.opposing_side(coordinate)], CLUTTER_EDGES[coordinate])
            thickness_constraint.set_offset(thickness_offset)

            if coordinate & TOP or coordinate & BOT:
                length_constraint_1.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[LEFT])
                length_constraint_2.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[RIGHT])
            else:
                length_constraint_1.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])
                length_constraint_2.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])

            border.add_constraint(cropbox_edge_constraint)
            border.add_constraint(thickness_constraint)
            border.add_constraint(length_constraint_1)
            border.add_constraint(length_constraint_2)

            borders.append(border)

        return borders

    def init_draggable_handles(self):
        # Setup the four handles on the cropbox's corners. These are inset into the corners
        # of the cropbox, and don't actually spill over onto the image stage; the illusion
        # of their outward-facing corners overlapping the stage is made by offsetting the
        # opaque squares slightly onto the cropbox
        handles = []
        coordinates = [TOP|LEFT, TOP|RIGHT, BOT|LEFT, BOT|RIGHT]

        for coordinate in coordinates:
            handle = DraggableHandle()

            # Each handle has four constraints:
            #   horiz_constraint: binds the handle to the cropbox's top/bottom sides
            #   vert_constraint: binds the handle to the cropbox's left/right sides
            #   width_constraint: binds the handle such that its width stays constant
            #   height_constraint: binds the handle such that its height stays constant
            #
            # The height/width constraints are set by binding the opposite side of the handle
            # that horiz/vert constraints bind (respectively) to the same edge of the cropbox,
            # and setting an offset equal to the desired height/width

            horiz_constraint = Clutter.SnapConstraint()
            horiz_constraint.set_source(self)
            vert_constraint = Clutter.SnapConstraint()
            vert_constraint.set_source(self)

            height_constraint = Clutter.SnapConstraint()
            height_constraint.set_source(self)
            width_constraint = Clutter.SnapConstraint()
            width_constraint.set_source(self)

            if coordinate & TOP:
                horiz_constraint.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])
                height_constraint.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[TOP])
                height_constraint.set_offset(handle.get_offset())
            else:
                horiz_constraint.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])
                height_constraint.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[BOT])
                height_constraint.set_offset(-handle.get_offset())

            if coordinate & LEFT:
                vert_constraint.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[LEFT])
                width_constraint.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[LEFT])
                width_constraint.set_offset(handle.get_offset())
            else:
                vert_constraint.set_edges(CLUTTER_EDGES[RIGHT], CLUTTER_EDGES[RIGHT])
                width_constraint.set_edges(CLUTTER_EDGES[LEFT], CLUTTER_EDGES[RIGHT])
                width_constraint.set_offset(-handle.get_offset())

            handle.add_constraint(height_constraint)
            handle.add_constraint(width_constraint)
            handle.add_constraint(horiz_constraint)
            handle.add_constraint(vert_constraint)

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
                top_constraint.set_offset(MARGIN / 2)
                top_constraint.set_edges(CLUTTER_EDGES[TOP], CLUTTER_EDGES[TOP])
                bot_constraint = Clutter.SnapConstraint()
                bot_constraint.set_source(self)
                bot_constraint.set_offset(-MARGIN / 2)
                bot_constraint.set_edges(CLUTTER_EDGES[BOT], CLUTTER_EDGES[BOT])

                square.add_constraint(top_constraint)
                square.add_constraint(bot_constraint)

            if coordinate & TOP or coordinate & LEFT:
                offset = MARGIN / 2
            else:
                offset = -MARGIN / 2
            # All the boxes have their namesake's edge bound to the same
            # named edge of the stage, and have the opposite side bound to their
            # namesake's edge of CROP. 
            #
            # For example, LEFT's left side is bound to the left edge of 
            # the stage, and LEFT's right side is bound to the left side of CROP

            cropbox_constraint = Clutter.SnapConstraint()
            cropbox_constraint.set_source(self)
            cropbox_constraint.set_offset(offset)
            cropbox_constraint.set_edges(CLUTTER_EDGES[self.opposing_side(coordinate)], CLUTTER_EDGES[coordinate])

            stage_constraint = Clutter.SnapConstraint()
            stage_constraint.set_source(self.stage)
            stage_constraint.set_edges(CLUTTER_EDGES[coordinate], CLUTTER_EDGES[coordinate])

            square.add_constraint(cropbox_constraint)
            square.add_constraint(stage_constraint)

            squares.append(square)

        return squares

    def box_region_at_coord(self, x, y):
        clicked_region = 0
        mid_vertical = mid_horizontal = False

        # Normalize the click coordinates to be the distance from
        # the box's (x, y) coordinates
        norm_x, norm_y = x - self.get_x(), y - self.get_y()

        # If the click happened within the first MARGIN pixels
        # of the box, it's on the left. If it was in the last
        # MARGIN of pixels, it's on the right
        if norm_x < MARGIN:
            clicked_region |= LEFT
        elif norm_x > self.get_width() - MARGIN:
            clicked_region |= RIGHT
        else:
            mid_horizontal = True

        # Likewise for top/bottom
        if norm_y < MARGIN:
            clicked_region |= TOP
        elif norm_y > self.get_height() - MARGIN:
            clicked_region |= BOT
        else:
            mid_vertical = True

        # If the clicked region isn't in a corner (i.e. has both a
        # top/bot and right/left quality), it's in the middle
        if mid_horizontal and mid_vertical:
            clicked_region = MIDDLE

        return clicked_region

    def set_view(self, view):
        self._view = view

    def mouse_motion_handler(self, actor, event):
        mouse_x, mouse_y = event.x, event.y
        region = self.box_region_at_coord(mouse_x, mouse_y)
        if region is not self._last_region:
            self._last_region = region
            if self._view is not None:
                # set the cursor here based on the region
                self._view.set_cursor(CURSOR_DICT[region])

    def mouse_leave_handler(self, actor, event):
        self._last_region = NONE
        # set the cursor back to normal
        if self._view is not None:
            # set the cursor here based on the region
            self._view.set_cursor(CURSOR_DICT[NONE])

    def drag_begin_handler(self, action, actor, x, y, mod):
        self.clicked_region = self.box_region_at_coord(x, y)
        self.drag_begin_dimensions = [actor.get_width(), actor.get_height()]
        self.drag_begin_coords = [actor.get_x(), actor.get_y()]

    # Return a value of dx such that the crop box's width will never
    # be lower than the MIN_WIDTH, and so that the crop box's left/right
    # sides will never move outside the bounds of the image stage
    def validate_dx(self, dx):
        # If the user is dragging either the left/right side, check if
        # the width of the box would be reduced to less than MIN_WIDTH
        # given dx. If so, return a value for dx which would reduce the width
        # to exactly MIN_WIDTH
        if self.clicked_region & LEFT:
            if self.get_width() - dx < MIN_WIDTH:
                return self.get_width() - MIN_WIDTH
        if self.clicked_region & RIGHT:
            if self.drag_begin_dimensions[0] + dx < MIN_WIDTH:
                return MIN_WIDTH - self.drag_begin_dimensions[0]

        # If the user is moving the left/right sides (either by dragging the
        # respective side, or by dragging the whole box), trim dx if it'd cause
        # the current x coordinate to be less than 0 or greater than the width
        # of the image stage
        if self.clicked_region & (LEFT | MIDDLE):
            if self.get_x() + dx < 0:
                return -self.get_x()
        if self.clicked_region & (RIGHT | MIDDLE):
            if self.get_x() + self.drag_begin_dimensions[0] + dx > self.get_parent().get_width():
                return self.get_parent().get_width() - (self.get_x() + self.drag_begin_dimensions[0])
        return dx

    # Nearly exactly as in validate_dy, trim the value of dy if it'd result
    # in the height of the box being too small, or if dy would place either
    # the top or bottom edges outside the bounds of the image stage
    def validate_dy(self, dy):
        if self.clicked_region & TOP:
            if self.get_height() - dy < MIN_HEIGHT:
                return self.get_height() - MIN_HEIGHT
        if self.clicked_region & BOT:
            if self.drag_begin_dimensions[1] + dy < MIN_HEIGHT:
                return MIN_HEIGHT - self.drag_begin_dimensions[1]

        if self.clicked_region & (TOP | MIDDLE):
            if self.get_y() + dy < 0:
                return -self.get_y()
        if self.clicked_region & (BOT | MIDDLE):
            if self.get_y() + self.drag_begin_dimensions[1] + dy > self.get_parent().get_height():
                return self.get_parent().get_height() - (self.get_y() + self.drag_begin_dimensions[1])
        return dy

    def drag_progress_handler(self, action, actor, dx, dy):
        # Ensure dx and dy would adjust the crop box's geometry within
        # the minimum size and bounded region constraints
        dx = self.validate_dx(dx)
        dy = self.validate_dy(dy)

        if not self.clicked_region & MIDDLE:
            # If the click was on the left side, we need to both
            # add the inverse of the dragged distance and simultaneously
            # move the position of the box (to simulate the manipulation
            # of the left side). If it was on the right, just add the
            # dragged distance to the size of the pre-dragged dimensions
            if self.clicked_region & LEFT:
                actor.set_width(actor.get_width() - dx)
                actor.set_x(actor.get_x() + dx)
            elif self.clicked_region & RIGHT:
                actor.set_width(self.drag_begin_dimensions[0] + dx)

            if self.clicked_region & TOP:
                actor.set_height(actor.get_height() - dy)
                actor.set_y(actor.get_y() + dy)
            elif self.clicked_region & BOT:
                actor.set_height(self.drag_begin_dimensions[1] + dy)
        else:
            # If the click happened away from either horizontal or 
            # vertical edges, just drag the box around
            actor.set_x(actor.get_x() + dx)
            actor.set_y(actor.get_y() + dy)

class DraggableHandle(Clutter.Actor):
    def __init__(self, **kw):
        super(DraggableHandle, self).__init__(**kw)
        self.dimension = MARGIN
        self.set_height(self.dimension)
        self.set_width(self.dimension)
        self.set_background_color(Clutter.Color.from_string("#000000")[1])

    def get_offset(self):
        return self.dimension

class DraggableBorder(Clutter.Actor):
    def __init__(self, **kw):
        super(DraggableBorder, self).__init__(**kw)
        self.thickness = MARGIN / 4
        self.set_background_color(Clutter.Color.from_string("#000000")[1])

    def get_offset(self):
        return MARGIN / 2

    def get_thickness(self):
        return self.thickness
