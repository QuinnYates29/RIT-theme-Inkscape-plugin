#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [YEAR] [YOUR NAME], [YOUR EMAIL]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Description of this extension
"""

import inkex
from inkex import Rectangle

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

BOX_EDGE_MARGIN = 20
LINE_EDGE_MARGIN = 10

STROKE_WIDTH = "1px"

ARROW_PULLBACK = 2
MIN_ARROW_SEGMENT = 18

ARROW_START = "Arrow1Mstart"
ARROW_END = "Arrow1Mend"

# === Padding & spacing ===
UNIT = BOX_GRID  # 20px

OUTER_PADDING = UNIT            # 20px – page to main box
BOX_PADDING = UNIT              # 20px – inside a box
TITLE_PADDING = UNIT            # 20px – top text offset
SIBLING_GAP = UNIT // 2         # 10px – space between child boxes
LEVEL_GAP = UNIT                # 20px – vertical separation (if used)

class TreeNode:
    def __init__(self, name, depth=0, meta=None):
        self.name = name        # string
        self.depth = depth      # integer
        self.children = []      # list of TreeNode objects
        self.meta = meta or {}  # dictionary

    def add_child(self, node):
        self.children.append(node)


def create_text(x, y, content, font_size="12px") -> inkex.TextElement:
    t = inkex.TextElement(
        x=str(x),
        y=str(y)
    )
    t.style = {
        "font-size": font_size,
        "text-anchor": "middle",
        "dominant-baseline": "middle"
    }
    t.text = content
    return t

#Helper to create wrapped text
def create_wrapped_text(x, y, width, height, content, font_size="14px"):
    flow = inkex.FlowRoot()
    flow.style = {
        "font-size": font_size,
        "text-align": "center",
        "white-space": "normal",
        "word-break": "normal",
        #"overflow-wrap": "break-word",  # optional fallback
    }

    # Define wrapping region
    region = inkex.FlowRegion()
    rect = Rectangle(
        x=str(x),
        y=str(y),
        width=str(width),
        height=str(height)
    )
    region.add(rect)
    flow.add(region)

    # Add paragraph
    para = inkex.FlowPara()
    para.text = content
    flow.add(para)

    return flow

# Helper to enforce snapping
def snap(value, grid):
    return round(value / grid) * grid

def debug(node, indent=0):
    print("  " * indent + node.name)
    for c in node.children:
        debug(c, indent + 1)


class ParentBox(inkex.EffectExtension):
    def box_style(self, fill):
        return {
            "fill": fill,
            "stroke": RIT_BLACK,
            "stroke-width": STROKE_WIDTH
        }

    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, help="Title for the top of the box", default="Schematic")
        pars.add_argument("--height", type=str, help="Height of the box - Leave empty for Fit to Page")
        pars.add_argument("--width", type=str, help="Width of the box - Leave empty for Fit to Page")
        pars.add_argument("--tree_data", type=str, default="")

    # Parse data from the input string and generate a tree structure
    # Format should be:
    # Parent
    # ---Child
    # ------ChildofChild
    #, Where - is a space
    def generate_tree(self, text, root_title) -> TreeNode:
        root = TreeNode(root_title)
        stack = [root]  # stack[level] = node at that depth

        for raw_line in text.splitlines():
            if not raw_line.strip():
                continue

            # Count leading dashes
            dash_count = 0
            for ch in raw_line:
                if ch == '-':
                    dash_count += 1
                else:
                    break

            if dash_count % 3 != 0:
                raise ValueError(f"Indentation must be multiples of 3 dashes:\n{raw_line}")

            depth = dash_count // 3
            label = raw_line[dash_count:].strip()

            node = TreeNode(label, depth=depth + 1)

            if depth >= len(stack):
                raise ValueError(f"Invalid indentation jump:\n{raw_line}")

            parent = stack[depth]
            parent.add_child(node)

            # reset stack to current depth and append node
            stack = stack[: depth + 1]
            stack.append(node)

        return root

    def create_box(self, x, y, width, height, fill = BACKGROUND_COLOR) -> Rectangle:
        rect = Rectangle(
            x=str(snap(x, BOX_GRID)),
            y=str(snap(y, BOX_GRID)),
            width=str(snap(width, BOX_GRID)),
            height=str(snap(height, BOX_GRID)),
            rx=str(self.svg.unittouu("3mm")),
            ry=str(self.svg.unittouu("3mm"))
        )
        rect.style = self.box_style(fill)
        return rect


    def render_node(self, node, x, y, width, height, parent_group=None, fill=RIT_WHITE, px="14px"):
        group = inkex.Group()
        if parent_group is None:
            self.svg.get_current_layer().add(group)
        else:
            parent_group.add(group)
        rect = self.create_box(x, y, width, height, fill=fill,)
        title = create_wrapped_text(
            x + BOX_PADDING,  # LEFT edge of inner box
            y + BOX_PADDING,  # TOP padding
            width - 2 * BOX_PADDING,  # inner width
            100,  # inner height
            node.name,
            font_size=px
        )
        group.add(rect)
        group.add(title)

        if not node.children:
            return

        n = len(node.children)

        inner_x = x + BOX_PADDING
        inner_width = width - 2 * BOX_PADDING

        # Snap inner area
        inner_x = snap(inner_x, BOX_GRID)
        inner_width = snap(inner_width, BOX_GRID)

        # Compute child width snapped to grid
        cbox_width = (inner_width - (n - 1) * SIBLING_GAP) / n
        cbox_width = snap(cbox_width, BOX_GRID)

        cbox_x = inner_x
        inner_y = y + TITLE_PADDING + BOX_PADDING
        ch = height - TITLE_PADDING - 2 * BOX_PADDING

        for child in node.children:
            if node.depth == 0:
                new_fill = BACKGROUND_COLOR
                fontsize = TITLE_PX
            elif node.depth == 1:
                new_fill = RIT_GRAY
                fontsize = SUBTITLE_PX
            else:
                new_fill = LIGHT_GREEN

            # TODO remove debug
            print("Child width:", cbox_width)
            print("Child height:", ch)
            self.render_node(child, cbox_x, inner_y, cbox_width, ch, parent_group=group, fill=new_fill, px=fontsize)
            cbox_x += cbox_width + SIBLING_GAP


    def effect(self):
        layer = self.svg.get_current_layer()

        # Width and height of the entire "page"
        svg = self.svg

        width = self.options.width or svg.get('width')
        height = self.options.height or svg.get('height')

        width = svg.unittouu(width)
        height = svg.unittouu(height)

        x = 0
        y = 0

        # Generate tree (Main box is not in tree and children = [] if empty)
        tree_data = self.options.tree_data

        if "\\n" in tree_data:
            tree_data = tree_data.encode().decode("unicode_escape")

        tree = self.generate_tree(tree_data, self.options.title)
        debug(tree)

        self.render_node(tree, x, y, width, height, fill=RIT_WHITE, px=TITLE_PX)

if __name__ == '__main__':
    ParentBox().run()