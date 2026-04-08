#!/usr/bin/env python
# coding=utf-8

import inkex
from inkex import PathElement
import math

def snap(value, base=5):
    return round(value / base) * base

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
            inkex.errormsg("Please select exactly two boxes.")
            return

        source, target = selection[0], selection[1]
        bbox_s = source.bounding_box()
        bbox_t = target.bounding_box()

        # Determine Start/End points based on Auto or User Input
        if self.options.start_side == "auto" or self.options.end_side == "auto":
            auto_p1, auto_p2 = self.get_auto_edge_center(bbox_s, bbox_t)

        p1 = auto_p1 if self.options.start_side == "auto" else get_point_on_side(bbox_s, self.options.start_side)
        p2 = auto_p2 if self.options.end_side == "auto" else get_point_on_side(bbox_t, self.options.end_side)

        # Geometry check
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 18:
            inkex.errormsg("Boxes too close.")
            return

        # Unit vectors for the 2px gap offset
        ux, uy = dx/dist, dy/dist
        start_x, start_y = snap(p1[0] + (ux * 2), 5), snap(p1[1] + (uy * 2), 5)
        end_x, end_y = snap(p2[0] - (ux * 2), 5), snap(p2[1] - (uy * 2), 5)

        # Path Generation
        if self.options.line_type == "orthogonal":
            # Determine mid-point for elbow
            mid_x = snap(start_x + (end_x - start_x) / 2, 5)
            path_data = f"M {start_x},{start_y} H {mid_x} V {end_y} H {end_x}"
        else:
            path_data = f"M {start_x},{start_y} L {end_x},{end_y}"

        # Create Path with Standard Arrow
        line = PathElement()
        line.set('d', path_data)
        line.style = {
            'stroke': '#000000',
            'stroke-width': '1px',
            'fill': 'none',
            'marker-end': 'url(#Arrow1Mend)'
        }
        self.svg.get_current_layer().add(line)

if __name__ == '__main__':
    DrawConnector().run()