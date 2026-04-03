from enum import Enum
import inkex
from themes import *


# Enum representing box type in stack
class BoxType(Enum):
    TITLE = 1
    BODY = 2

# Simple class to hold box data
class BoxData:
    def __init__(self, name, box_type: BoxType):
        self.name = name
        self.type = box_type


# <--------- Helper Functions -------->#

def min_flow_width(text, font_size_px, width):
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))
    words = text.split()
    if not words: return width
    longest_word = max(words, key=len)
    return max(len(longest_word) * font_size_px * 0.7, width)


def create_wrapped_text(x, y, width, height, content, font_size="14px"):
    flow = inkex.FlowRoot()
    flow.style = {
        "font-size": font_size,
        "fill": RIT_BLACK,
        "text-align": "center",
        "text-anchor": "middle"
    }

    region = inkex.FlowRegion()
    width = min_flow_width(content, font_size, width)
    rect = inkex.Rectangle(
        x=str(x),
        y=str(y),
        width=str(width),
        height=str(height)
    )

    region.add(rect)
    flow.add(region)

    para = inkex.FlowPara()
    para.style = {"text-align": "center"}
    para.text = content
    flow.add(para)

    return flow

# Helper which calculates necessary height for wrapped text
def compute_text_height(text, font_size_px, box_width):
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))

    # Account for some internal padding so text doesn't touch the 1px border
    usable_width = box_width - 10
    avg_char_width = font_size_px * 0.6
    max_chars_per_line = max(1, usable_width / avg_char_width)

    words = text.split()
    if not words:
        return 40  # Minimum box height

    lines = 1
    current_line_chars = 0

    for w in words:
        word_len = len(w)

        # If this isn't the first word on the line, add 1 for the space
        space = 1 if current_line_chars > 0 else 0

        if current_line_chars + space + word_len > max_chars_per_line:
            lines += 1
            current_line_chars = word_len  # Start new line with this word
        else:
            current_line_chars += space + word_len

    # Standard line height is usually 1.2 to 1.4 times font size
    line_height = font_size_px * 1.3
    raw_height = (lines * line_height) + 20  # Add vertical padding

    # RULE: Snap to your 20px grid
    return max(40, snap(raw_height, 20))

# Helper that gets the offset for wrapped text to align vertically inside a box
def get_text_v_offset(box_y, box_height, text, font_size_px, box_width):
    """
    Calculates the starting Y coordinate for a FlowRoot by finding the
    difference between the box height and the actual text block height.
    """
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))

    # Calculate lines to find the height of the "text block" itself
    usable_width = box_width - 10
    avg_char_width = font_size_px * 0.6
    max_chars_per_line = max(1, usable_width / avg_char_width)

    words = text.split()
    lines = 1
    current_line_chars = 0
    for w in words:
        word_len = len(w)
        space = 1 if current_line_chars > 0 else 0
        if current_line_chars + space + word_len > max_chars_per_line:
            lines += 1
            current_line_chars = word_len
        else:
            current_line_chars += space + word_len

    # The actual height the text occupies
    line_height = font_size_px * 1.3
    text_block_height = lines * line_height

    # Center the block within the box height
    v_padding = (box_height - text_block_height) / 2

    return box_y + v_padding

def snap(value, grid):
    return round(value / grid) * grid


def get_middle_xy(width, height):
    return width / 2, height / 2


# === Extension Class ===
class BoxStackGenerator(inkex.EffectExtension):

    def create_box(self, x, y, width, height, fill=LIGHT_GREEN) -> inkex.Rectangle:
        snapped_x = snap(x, BOX_GRID)
        snapped_y = snap(y, BOX_GRID)
        snapped_w = snap(width, BOX_GRID)
        snapped_h = snap(height, BOX_GRID)
        rect = inkex.Rectangle(
            x=str(snapped_x),
            y=str(snapped_y),
            width=str(snapped_w),
            height=str(snapped_h),
            rx=str(self.svg.unittouu("3mm")),
            ry=str(self.svg.unittouu("3mm"))
        )
        # Assuming a simple style helper; added inline to ensure it runs
        rect.style = {'fill': fill, 'stroke': RIT_BLACK, 'stroke-width': '1px'}
        return rect

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
            # 1. DEFINE THEME VALUES FIRST
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

            rect = self.create_box(current_x, current_y, current_w, box_h, fill_color)
            rect.style = get_style(fill_color)
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

    def effect(self):
        # Generate stack as a Python list
        stack_data = self.options.stack_data
        title = self.options.title

        if "\\n" in stack_data:
            stack_data = stack_data.encode().decode("unicode_escape")
        box_list = self.generate_stack(stack_data, title)

        # Get dimensions
        # Note: Added fallback values in case SVG width/height are percent-based
        width_int = self.svg.unittouu(self.svg.get('width', '500px'))
        height_int = self.svg.unittouu(self.svg.get('height', '500px'))

        # Center the stack horizontally, start near top
        x = (width_int / 2) - (self.options.width / 2)
        y = 50

        self.draw_stack(box_list, x, y, self.options.width, self.options.height)


if __name__ == '__main__':
    BoxStackGenerator().run()