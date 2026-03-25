from enum import Enum

import inkex

# COLORS
BACKGROUND_COLOR = "#dcdcdc"
LIGHT_GREEN = "#b6d7a8"
DARK_BLUE = "#69a4d9"
LIGHT_BLUE = "#cfe2f3"
PURPLE = "#b665a8"
RIT_ORANGE = "#F76902"
RIT_BLACK  = "#000000"
RIT_GRAY   = "#808080"
RIT_WHITE  = "#FFFFFF"

# === Text sizes ===
TITLE_PX = "35px"
SUBTITLE_PX = "20px"

# === Diagram rules ===
BOX_GRID = 20
LINE_GRID = 5

# Enum representing box type in stack - allowing for adding future kinds of boxes in a stack
class BoxType(Enum):
    TITLE = 1
    BODY = 2

# Doubly Linked list Node representing a single box in a stack
class LinkedNode:
    def __init__(self, name, box_type : BoxType, prev_node=None, next_node=None):
        self.name = name
        self.type = box_type
        self.next = next_node
        self.prev = prev_node

    def add_next(self, next_node):
        self.next = next_node
        self.next.prev = self

# Linked list representing a stack of boxes of type LinkedNode
class BoxStack:
    def __init__(self, head : LinkedNode):
        self.head = head

#<--------- Helper Functions -------->#

#Returns the mimimum width for a flowroot element based on the length of the longest word
def min_flow_width(text, font_size_px, width):
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))
    longest_word = max(text.split(), key=len)
    return max(len(longest_word) * font_size_px * 0.7, width)

#Helper to create wrapped text
def create_wrapped_text(x, y, width, height, content, font_size="14px"):
    #print("FLOW:", x, y, width, height, content)

    flow = inkex.FlowRoot()

    flow.style = {
        "font-size": font_size,
        "fill": RIT_BLACK,
        "text-align": "center",
        "text-anchor": "middle"
    }

    region = inkex.FlowRegion()
    #Ensure width is large enough to fit the text
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
    para.style = {
        "text-align": "center",
    }
    para.text = content
    flow.add(para)

    return flow

# Helper to enforce snapping
def snap(value, grid):
    return round(value / grid) * grid

def get_middle_xy(width, height):


#
class BoxStackGenerator(inkex.EffectExtension):
    # Function containing parsing logic for input data, then generates
    # list structure of boxes
    def generate_stack(self, data, title) -> BoxStack:
        # Generate stack
        stack = BoxStack(LinkedNode(title, BoxType.TITLE))

        # Parse data input and generate the rest of the stack
        current = stack.head
        for raw_line in data.splitlines():
            if not raw_line.strip():
                continue
            current.add_next(LinkedNode(raw_line, BoxType.BODY))
            current = current.next
        return stack



    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, help="Title of top box")
        pars.add_argument("--height", type=str, help="Height of the box")
        pars.add_argument("--width", type=str, help="Width of the box")
        pars.add_argument("--stack_data", type=str, default="")

    def effect(self):
        layer = self.svg.get_current_layer()




if __name__ == '__main__':
    BoxStackGenerator().run()