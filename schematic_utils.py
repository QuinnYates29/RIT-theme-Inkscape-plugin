import inkex
from inkex import Rectangle
from themes import *

# Common Constants
MIN_WIDTH = 80
MIN_HEIGHT = 60


def snap(value, grid=BOX_GRID):
    """Snaps a value to the defined global grid."""
    return round(value / grid) * grid


def min_flow_width(text, font_size_px, width):
    """Calculates minimum width for a flowroot element based on word length."""
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))
    words = text.split()
    if not words: return width
    longest_word = max(words, key=len)
    return max(len(longest_word) * font_size_px * 0.7, width)


def compute_text_height(text, font_size_px, box_width):
    """Calculates necessary height for wrapped text block."""
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))

    usable_width = box_width - 10
    avg_char_width = font_size_px * 0.6
    max_chars_per_line = max(1, usable_width / avg_char_width)

    words = text.split()
    if not words: return 40

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

    line_height = font_size_px * 1.3
    raw_height = (lines * line_height) + 20
    return max(40, snap(raw_height, BOX_GRID))


def create_wrapped_text(x, y, width, height, content, font_size="14px"):
    """Creates a standard FlowRoot element for the schematic."""
    flow = inkex.FlowRoot()
    flow.style = {
        "font-size": font_size,
        "fill": RIT_BLACK,
        "text-align": "center",
        "text-anchor": "middle"
    }
    region = inkex.FlowRegion()
    width = min_flow_width(content, font_size, width)
    rect = Rectangle(x=str(x), y=str(y), width=str(width), height=str(height))
    region.add(rect)
    flow.add(region)
    para = inkex.FlowPara()
    para.style = {"text-align": "center"}
    para.text = content
    flow.add(para)
    return flow


def get_text_v_offset(box_y, box_height, text, font_size_px, box_width):
    """Calculates Y start for vertical centering inside a box."""
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))

    # Re-use logic to find lines
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

    text_block_height = lines * (font_size_px * 1.3)
    return box_y + (box_height - text_block_height) / 2

def create_box(svg, x, y, width, height, fill=LIGHT_GREEN, border=RIT_BLACK) -> inkex.Rectangle:
    snapped_x = snap(x, BOX_GRID)
    snapped_y = snap(y, BOX_GRID)
    snapped_w = snap(width, BOX_GRID)
    snapped_h = snap(height, BOX_GRID)
    rect = inkex.Rectangle(
        x=str(snapped_x),
        y=str(snapped_y),
        width=str(snapped_w),
        height=str(snapped_h),
        rx=str(svg.unittouu("3mm")),
        ry=str(svg.unittouu("3mm"))
    )
    # Assuming a simple style helper; added inline to ensure it runs
    rect.style = get_style(fill, border)
    return rect