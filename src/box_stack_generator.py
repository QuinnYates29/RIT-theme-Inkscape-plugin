from enum import Enum
import inkex
from themes import *
from schematic_utils import * # Helper functions


# Enum representing box type in stack
class BoxType(Enum):
    TITLE = 1
    BODY = 2

# Simple class to hold box data
class BoxData:
    def __init__(self, name, box_type: BoxType):
        self.name = name
        self.type = box_type

# Gets middle of rectangle given width, height
def get_middle_xy(width, height):
    return width / 2, height / 2


# === Extension Class ===
class BoxStackGenerator(inkex.EffectExtension):

    def generate_stack(self, data, title) -> list:
        # Create a list and add first box
        box_list = [BoxData(title, BoxType.TITLE)]

        # Parse data input and append to the list
        for raw_line in data.splitlines():
            line = raw_line.strip()
            if line:
                box_list.append(BoxData(line, BoxType.BODY))
        return box_list

    def draw_stack(self, stack, x, y, width, height, parent_group=None):
        current_y = snap(y, BOX_GRID)
        current_x = snap(x, BOX_GRID)
        current_w = snap(width, BOX_GRID)

        stack_group = inkex.Group()
        stack_group.set('inkscape:label', 'Stack: ' + stack[0].name)

        if parent_group:
            parent_group.add(stack_group)
        else:
            self.svg.get_current_layer().add(stack_group)

        for box_item in stack:
            # DEFINE THEME VALUES FIRST
            if box_item.type == BoxType.TITLE:
                fill_color = DARK_BLUE
                font_size_str = SUB_GROUP_PX  # From themes.py (e.g., "16px")
            else:
                fill_color = LIGHT_GREEN
                font_size_str = BOX_TEXT_PX  # From themes.py (e.g., "14px")
            font_size_px = float(font_size_str.replace("px", ""))

            # CALCULATE GEOMETRY
            needed_height = compute_text_height(box_item.name, font_size_px, width)
            box_h = snap(needed_height, BOX_GRID)
            centered_y = get_text_v_offset(current_y, box_h, box_item.name, font_size_px, current_w)

            current_group = inkex.Group()
            current_group.set('inkscape:label', 'Box: ' + box_item.name)
            stack_group.add(current_group)

            rect = create_box(self, current_x, current_y, current_w, box_h, fill=fill_color, border=RIT_BLACK)
            current_group.add(rect)

            text = create_wrapped_text(
                current_x,
                centered_y,
                current_w,
                box_h,
                box_item.name,
                font_size=font_size_str
            )
            # Optional: Override text style using helper
            text.style.update(get_text_style(font_size=font_size_str))

            current_group.add(text)
            current_y += box_h


    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, default="Title")
        pars.add_argument("--height", type=float, default=50.0)
        pars.add_argument("--width", type=float, default=150.0)
        pars.add_argument("--stack_data", type=str, default="")
        pars.add_argument("--x", type=int, default=-1)
        pars.add_argument("--y", type=int, default=-1)

    def effect(self):
        # Generate stack as a Python list
        stack_data = self.options.stack_data
        title = self.options.title
        x = self.options.x
        y = self.options.y

        if "\\n" in stack_data:
            stack_data = stack_data.encode().decode("unicode_escape")
        box_list = self.generate_stack(stack_data, title)

        width_int = self.svg.unittouu(self.svg.get('width', '500px'))
        height_int = self.svg.unittouu(self.svg.get('height', '500px'))

        if x == -1:
            x = (width_int / 2) - (self.options.width / 2)
        if y == -1:
            y = 50

        self.draw_stack(box_list, x, y, self.options.width, self.options.height)


if __name__ == '__main__':
    BoxStackGenerator().run()