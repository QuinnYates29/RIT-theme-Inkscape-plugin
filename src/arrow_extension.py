#!/usr/bin/env python
# coding=utf-8

import inkex
from inkex import PathElement
import math
from schematic_utils import *

def get_point_on_side(bbox, side):
    """Returns the center point of a specific bounding box edge."""
    center = bbox.center
    if side == "top":    return center.x, bbox.top
    if side == "bottom": return center.x, bbox.bottom
    if side == "left":   return bbox.left, center.y
    if side == "right":  return bbox.right, center.y
    return center.x, center.y # Fallback to center

class DrawConnector(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--line_type", type=str, default="orthogonal")
        pars.add_argument("--start_side", type=str, default="auto")
        pars.add_argument("--end_side", type=str, default="auto")

    def get_auto_edge_center(self, source_bbox, target_bbox):
        """Calculates best edge centers based on relative position (Auto Logic)."""
        s_center = source_bbox.center
        t_center = target_bbox.center
        dx = t_center.x - s_center.x
        dy = t_center.y - s_center.y

        if abs(dx) > abs(dy): # Horizontal
            if dx > 0: return (source_bbox.right, s_center.y), (target_bbox.left, t_center.y)
            else:      return (source_bbox.left, s_center.y), (target_bbox.right, t_center.y)
        else: # Vertical
            if dy > 0: return (s_center.x, source_bbox.bottom), (t_center.x, target_bbox.top)
            else:      return (s_center.x, source_bbox.top), (t_center.x, target_bbox.bottom)

    def effect(self):
        selection = self.svg.selection
        if len(selection) != 2:
            inkex.errormsg("Select two boxes.")
            return

        source, target = selection[0], selection[1]
        bbox_s = source.bounding_box()
        bbox_t = target.bounding_box()

        # Get raw points (Source and Target)
        if self.options.start_side == "auto" or self.options.end_side == "auto":
            auto_p1, auto_p2 = self.get_auto_edge_center(bbox_s, bbox_t)

        p1_raw = auto_p1 if self.options.start_side == "auto" else get_point_on_side(bbox_s, self.options.start_side)
        p2_raw = auto_p2 if self.options.end_side == "auto" else get_point_on_side(bbox_t, self.options.end_side)

        # Snap to 5px Grid FIRST
        s_x, s_y = snap_5px(p1_raw[0]), snap_5px(p1_raw[1])
        e_x, e_y = snap_5px(p2_raw[0]), snap_5px(p2_raw[1])

        # Apply 5px Gap (One full grid square away from the box)
        gap = 5

        # Offset Start Point
        if s_y <= bbox_s.top:
            s_y -= gap
        elif s_y >= bbox_s.bottom:
            s_y += gap
        elif s_x <= bbox_s.left:
            s_x -= gap
        else:
            s_x += gap

        # Offset End Point
        if e_y <= bbox_t.top:
            e_y -= gap
        elif e_y >= bbox_t.bottom:
            e_y += gap
        elif e_x <= bbox_t.left:
            e_x -= gap
        else:
            e_x += gap

        # Orthogonal Routing Logic
        dx, dy = abs(e_x - s_x), abs(e_y - s_y)
        if self.options.end_side in ["top", "bottom"] or (self.options.end_side == "auto" and dy > dx):
            mid_y = s_y + (e_y - s_y) / 2
            path_data = f"M {s_x},{s_y} V {mid_y} H {e_x} V {e_y}"
        else:
            mid_x = s_x + (e_x - s_x) / 2
            path_data = f"M {s_x},{s_y} H {mid_x} V {e_y} H {e_x}"

        line = PathElement()
        line.set('d', path_data)

        # This uses the marker ID exactly as it appeared in your successful XML check
        style_str = (
            'fill:none;'
            'stroke:#000000;'
            'stroke-width:1px;'
            'stroke-linecap:butt;'
            'marker-end:url(#ConcaveTriangle);'
        )
        line.set('style', style_str)

        self.svg.get_current_layer().add(line)

if __name__ == '__main__':
    DrawConnector().run()