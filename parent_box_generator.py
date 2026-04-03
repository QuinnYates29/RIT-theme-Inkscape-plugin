#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2026 Quinn Yates, qry3977@rit.edu
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
This extension is intended for automatically generating a nested structure of boxes for a schematic.
It is intended for the main "structure" of a schematic.
"""

import inkex
from inkex import Rectangle
from themes import *

BOX_EDGE_MARGIN = 20
LINE_EDGE_MARGIN = 10

STROKE_WIDTH = "1px"

# === Padding & spacing ===
UNIT = BOX_GRID  # 20px

OUTER_PADDING = UNIT            # 20px – page to main box
BOX_PADDING = UNIT              # 20px – inside a box
TITLE_PADDING = UNIT            # 20px – top text offset
SIBLING_GAP = UNIT // 2         # 10px – space between child boxes
LEVEL_GAP = UNIT                # 20px – vertical separation (if used)
MIN_WIDTH = 80
MIN_HEIGHT = 60

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

#Safely returns the weight of parameter node
# Returns 1 if error occurs
def get_weight(node):
    try:
        return float(node.meta.get("weight", 1.0))
    except (TypeError, ValueError):
        return 1.0

# Returns the mimimum width for a flowroot element based on the length of the longest word
def min_flow_width(text, font_size_px, width):
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))
    longest_word = max(text.split(), key=len)
    return max(len(longest_word) * font_size_px * 0.7, width)

def compute_title_height(text, font_size_px, box_width):
    if isinstance(font_size_px, str):
        font_size_px = float(font_size_px.replace("px", ""))

    words = text.split()
    avg_char_width = font_size_px * 0.6
    max_chars_per_line = box_width / avg_char_width

    lines = 1
    current_len = 0

    for w in words:
        word_len = len(w)
        if current_len + word_len > max_chars_per_line:
            lines += 1
            current_len = word_len
        else:
            current_len += word_len + 1  # + space

    line_height = font_size_px * 1.2
    return lines * line_height + 5

def compute_child_layout(children, inner_width, font_px):

    n = len(children)
    if n == 0:
        return [], 0, 0

    if isinstance(font_px, str):
        font_px = float(font_px.replace("px", ""))
    # --- Step 1: Minimum widths (text safety) ---
    min_widths = []
    for child in children:
        longest_word = max(child.name.split(), key=len)
        text_min = len(longest_word) * font_px * 0.6 + 2 * BOX_PADDING
        min_widths.append(max(text_min, MIN_WIDTH))

    total_min = sum(min_widths)
    # --- Step 2: Reserve spacing region (15%) ---
    spacing_ratio = 0.15
    total_spacing_width = inner_width * spacing_ratio

    if n > 1:
        spacing = total_spacing_width / (n - 1)
        spacing = snap(spacing, BOX_GRID)
    else:
        spacing = 0

    box_region_width = inner_width - total_spacing_width
    # --- Step 3: If minimums exceed box region, scale them down ---
    if total_min > box_region_width:
        scale = box_region_width / total_min
        widths = [w * scale for w in min_widths]
    else:
        # --- Step 4: Apply weights inside box region ---
        weights = [get_weight(c) for c in children]
        total_weight = sum(weights)

        widths = [
            box_region_width * (w / total_weight)
            for w in weights
        ]

        # Enforce minimums
        widths = [
            max(min_w, w)
            for min_w, w in zip(min_widths, widths)
        ]
    widths = [snap(w, BOX_GRID) for w in widths]
    # --- Step 5: Final centering ---
    total_width = sum(widths)
    total_layout = total_width + spacing * (n - 1)

    start_offset = (inner_width - total_layout) / 2

    return widths, spacing, start_offset

#Helper to create wrapped text
def create_wrapped_text(x, y, width, height, content, font_size="14px"):
    print("FLOW:", x, y, width, height, content)

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
    rect = Rectangle(
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

            node = TreeNode(label, depth=depth + 1, meta={"weight": 1})

            if depth >= len(stack):
                raise ValueError(f"Invalid indentation jump:\n{raw_line}")

            parent = stack[depth]
            parent.add_child(node)

            # reset stack to current depth and append node
            stack = stack[: depth + 1]
            stack.append(node)

        return root

    def create_box(self, x, y, width, height, fill = GREY) -> Rectangle:
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

    def render_node(self, node, x, y, width, height, parent_group=None, fill=WHITE, px="14px"):
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return

        if node.depth == 0:
            current_fill = WHITE
            current_px = PRIMARY_TITLE_PX
        elif node.depth == 1:
            current_fill = GREY
            current_px = GROUP_HEADER_PX
        else:
            current_fill = RIT_GRAY
            current_px = BOX_TEXT_PX

        group = inkex.Group()
        if parent_group is None:
            self.svg.get_current_layer().add(group)
        else:
            parent_group.add(group)

        # Use the determined fill
        rect = self.create_box(x, y, width, height, fill=current_fill)
        group.add(rect)

        title_width = width - 2 * BOX_PADDING
        title_height = compute_title_height(node.name, current_px, title_width)

        title = create_wrapped_text(
            x + (width - title_width) / 2,
            y + BOX_PADDING,
            title_width,
            title_height,
            node.name,
            font_size=current_px
        )
        group.add(title)

        if not node.children:
            return

        # --- Child Layout Logic ---
        inner_x = snap(x + BOX_PADDING, BOX_GRID)
        inner_width = snap(width - 2 * BOX_PADDING, BOX_GRID)

        widths, spacing, offset = compute_child_layout(node.children, inner_width, current_px)

        cbox_x = inner_x + offset
        child_y = y + title_height + BOX_PADDING
        ch = height - title_height - 2 * BOX_PADDING

        for child, cw in zip(node.children, widths):
            self.render_node(
                child,
                snap(cbox_x, BOX_GRID),
                child_y,
                cw,
                ch,
                parent_group=group
            )
            cbox_x += cw + spacing


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

        self.render_node(tree, x, y, width, height, fill=WHITE, px=PRIMARY_TITLE_PX)

if __name__ == '__main__':
    ParentBox().run()