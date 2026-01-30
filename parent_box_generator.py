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


class ParentBox(inkex.EffectExtension):
    def box_style(self, fill):
        return {
            "fill": fill,
            "stroke": RIT_BLACK,
            "stroke-width": str(self.svg.unittouu("1mm"))
        }

    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, help="Title for the top of the box", default="Schematic")
        pars.add_argument("--height", type=str, help="Height of the box - Leave empty for Fit to Page",
                          default=self.svg.get_current_layer().root.attrib.get('height'))
        pars.add_argument("--width", type=str, help="Width of the box - Leave empty for Fit to Page",
                          default=self.svg.get_current_layer().root.attrib.get('width'))
        pars.add_argument("--str_data", type=str, default="")

    def generate_tree(self, title:str) -> TreeNode:
        data = self.options.tree_data.strip()
        head = TreeNode(title)
        if not data:
            return head

        node = head
        for line in data.splitlines():
            node.add_child(TreeNode(line))
            head.depth += 1


    def create_box(self, x, y, width, height, fill = BACKGROUND_COLOR) -> Rectangle:
        rect = Rectangle(
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            rx=str(self.svg.unittouu("3mm")),
            ry=str(self.svg.unittouu("3mm"))
        )
        rect.style = self.box_style(fill)
        return rect

    # Draws initial main box, and then starts recursive generation if necessary
    def draw_structure(self, tree:TreeNode, x, y, width, height, title="Schematic"):
        root_group = inkex.Group()
        rect = self.create_box(x, y, width, height, fill=BACKGROUND_COLOR)
        title = create_text(x + width/2, y, title)
        root_group.add(rect)
        root_group.add(title)

        if len(num_children := tree.children) > 0:
            child_x = x + 10
            child_y = y + 10
            child_width = ((width-20) / (len(num_children)) - 10)
            child_height = height - 20
            for child in tree.children:
                render_node


    def render_node(self, node, x, y, width, height, parent_group, title):
        group = inkex.Group()
        parent_group.add(group)


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
        tree = self.generate_tree(self.options.str_data)




if __name__ == '__main__':
    ParentBox().run()
