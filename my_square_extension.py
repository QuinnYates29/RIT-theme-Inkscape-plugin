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
    name: str
    children: list[TreeNode]


class ParentBox(inkex.EffectExtension):
    def box_style(self, fill):
        return {
            "fill": fill,
            "stroke": RIT_BLACK,
            "stroke-width": str(self.svg.unittouu("1mm"))
        }

    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, help="Title for the top of the box", default="Schematic")
        pars.add_argument("--height", type=str, help="Height of the box", default="500mm")
        pars.add_argument("--width", type=str, help="Width of the box", default="500mm")
        pars.add_argument("--str_data", type=str, default="")

    def generate_tree(self, data, head):


    def draw_box(self, x, y, width, height, fill = BACKGROUND_COLOR):
        rect = Rectangle(
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            rx=str(self.svg.unittouu("3mm")),
            ry=str(self.svg.unittouu("3mm"))
        )
        rect.style = self.box_style(fill)
        self.svg.get_current_layer().add(rect)

    def text(self, x, y, content):
        t = inkex.TextElement(
            x=str(x),
            y=str(y)
        )
        t.style = {
            "font-size": "12px",
            "text-anchor": "middle",
            "dominant-baseline": "middle"
        }
        t.text = content
        self.svg.get_current_layer().add(t)

    def effect(self):
        layer = self.svg.get_current_layer()

        x = 100
        y = 100
        width = self.svg.unittouu(self.options.width)
        height = self.svg.unittouu(self.options.height)

        self.draw_box(x, y, width, height)
        self.text(x + width/3, y + width/3, self.options.top_text)

if __name__ == '__main__':
    Box().run()
