#!/usr/bin/env python
# coding=utf-8

import inkex
from inkex import PathElement
import math


def snap(value, base=5):
    return round(value / base) * base

def get_point_on_side(bbox, side):
    """Helper to return the center point of a specific bounding box edge."""
    center = bbox.center
    if side == "top":    return center.x, bbox.top
    if side == "bottom": return center.x, bbox.bottom
    if side == "left":   return bbox.left, center.y
    if side == "right":  return bbox.right, center.y
    return center


class DrawConnector(inkex.EffectExtension):
    def add_arguments(self, pars):
        # This matches the 'name' attribute in the .inx file
        pars.add_argument("--line_type", type=str, default="orthogonal", help="Style of the connector")

    def get_edge_center(self, source_bbox, target_bbox):
        """Calculates the best edge centers to connect based on relative position."""
        s_center = source_bbox.center
        t_center = target_bbox.center

        dx = t_center.x - s_center.x
        dy = t_center.y - s_center.y

        # Determine if boxes are more horizontal or vertical relative to each other
        if abs(dx) > abs(dy):
            # Horizontal connection
            if dx > 0:  # Target is to the right
                start = (source_bbox.right, s_center.y)
                end = (target_bbox.left, t_center.y)
            else:  # Target is to the left
                start = (source_bbox.left, s_center.y)
                end = (target_bbox.right, t_center.y)
        else:
            # Vertical connection
            if dy > 0:  # Target is below
                start = (s_center.x, source_bbox.bottom)
                end = (t_center.x, target_bbox.top)
            else:  # Target is above
                start = (s_center.x, source_bbox.top)
                end = (t_center.x, target_bbox.bottom)

        return start, end

    def effect(self):
        selection = self.svg.selection
        if len(selection) != 2:
            inkex.errormsg("Please select exactly two boxes.")
            return

        source, target = selection[0], selection[1]
        bbox_s = source.bounding_box()
        bbox_t = target.bounding_box()

        # Determine Start Point
        if self.options.start_side == "auto":
            # logic from previous response to find best exit
            p1, _ = self.get_auto_edge_center(bbox_s, bbox_t)
        else:
            p1 = get_point_on_side(bbox_s, self.options.start_side)

        # Determine End Point
        if self.options.end_side == "auto":
            _, p2 = self.get_auto_edge_center(bbox_s, bbox_t)
        else:
            p2 = get_point_on_side(bbox_t, self.options.end_side)

        # Apply 2px gap and 5px grid snap
        dist = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        if dist < 18:
            inkex.errormsg("Boxes are too close for a valid arrow.")
            return

        ux, uy = (p2[0] - p1[0]) / dist, (p2[1] - p1[1]) / dist

        start_x = snap(p1[0] + (ux * 2), 5)
        start_y = snap(p1[1] + (uy * 2), 5)
        # End point pulled back 2px from the edge center
        end_x = snap(p2[0] - (ux * 2), 5)
        end_y = snap(p2[1] - (uy * 2), 5)

        # Path Generation
        if self.options.line_type == "orthogonal":
            # Simple elbow: Move halfway horizontally, then vertically
            mid_x = snap(start_x + (end_x - start_x) / 2, 5)
            path_data = f"M {start_x},{start_y} H {mid_x} V {end_y} H {end_x}"
        else:
            path_data = f"M {start_x},{start_y} L {end_x},{end_y}"

        # Create Element with Marker
        attribs = {
            'style': 'stroke:#000000;stroke-width:1px;fill:none;',
            'd': path_data,
            'marker-end': 'url(#Arrow1Mend)'
        }

        line = PathElement(**attribs)
        self.svg.get_current_layer().add(line)


if __name__ == '__main__':
    DrawConnector().run()