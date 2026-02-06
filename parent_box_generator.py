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
from idlelib.tree import TreeNode

import inkex
from inkex import Rectangle
from lxml import etree
from rich.markdown import TextElement

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
BOX_PADDING = UNIT // 2         # 10px – inside a box
TITLE_PADDING = UNIT // 2       # 10px – top text offset
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


def create_text(x, y, content, font_size="12px") -> TextElement:
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

# Helper to enforce snapping
def snap(value, grid):
    return round(value / grid) * grid


class ParentBox(inkex.EffectExtension):
    def box_style(self, fill):
        return {
            "fill": fill,
            "stroke": RIT_BLACK,
            "stroke-width": STROKE_WIDTH
        }

    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, help="Title for the top of the box", default="Schematic")
        pars.add_argument("--height", type=str, help="Height of the box - Leave empty for Fit to Page",
                          default=self.svg.get_current_layer().root.attrib.get('height'))
        pars.add_argument("--width", type=str, help="Width of the box - Leave empty for Fit to Page",
                          default=self.svg.get_current_layer().root.attrib.get('width'))
        pars.add_argument("--str_data", type=str, default="")

    # Parse data from the input string and generate a tree structure
    # Format should be:
    # Parent
    # ---Child
    # ------ChildofChild
    #, Where - is a space
    def generate_tree(self, input, root_title) -> TreeNode:
        root = TreeNode(root_title)
        stack = {0: root}
        for raw_line in input.splitlines():
            if not raw_line.strip():
                continue
            dash_count = 0
            for char in raw_line:
                if char == '-':
                    dash_count += 1
                else:
                    break
            depth = dash_count // 3
            value = raw_line[dash_count:].strip()
            node = TreeNode(value)

            # Attach node
            parent = stack[depth]
            parent.add_child(node)
            # Store for children
            stack[depth + 1] = node
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


    def render_node(self, node, x, y, width, height, parent_group=None):
        group = inkex.Group()
        if parent_group is None:
            self.svg.get_current_layer().add(group)
        else:
            parent_group.add(group)
        parent_group.add(group)
        rect = self.create_box(x, y, width, height, fill=BACKGROUND_COLOR)
        title = create_text(x + width/2, y + 12, node.name)
        group.add(rect)
        group.add(title)

        if not node.children:
            return

        n = len(node.children)
        tot_inner_width = width - 2 * BOX_PADDING
        cbox_width = (tot_inner_width - (n - 1) * SIBLING_GAP) / n
        cbox_x = x + BOX_PADDING
        inner_y = y + BOX_PADDING
        ch = height - 2 * BOX_PADDING

        for child in node.children:
            self.render_node(child, cbox_x, inner_y, cbox_width, ch, group)
            cbox_x += cbox_width + SIBLING_GAP


    def effect(self):
        layer = self.svg.get_current_layer()

        # Width and height of the entire "page"
        root = self.svg.getroot()
        width = root.attrib.get('width')
        height = root.attrib.get('height')

        x = 0
        y = 0
        width = self.svg.unittouu(self.options.width)
        height = self.svg.unittouu(self.options.height)

        # Generate tree (Main box is not in tree and children = [] if empty)
        tree_data = self.options.tree_data.strip()
        tree = self.generate_tree(tree_data, self.options.title)
        self.render_node(tree, x, y, width, height)

if __name__ == '__main__':
    ParentBox().run()