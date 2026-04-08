import inkex
from inkex import PathElement, Marker


def snap(value, base=5):
    return round(value / base) * base


class DrawConnector(inkex.EffectExtension):
    def add_arguments(self, pars):
        # You can add options here for line style (straight vs orthogonal)
        pars.add_argument("--line_type", type=str, default="straight")

    def effect(self):
        # 1. Check selection (Need exactly 2 boxes)
        selection = self.svg.selection
        if len(selection) != 2:
            inkex.errormsg("Please select exactly two boxes (Source then Target).")
            return

        source = selection[0]
        target = selection[1]

        # 2. Get Bounding Boxes
        bbox_s = source.bounding_box()
        bbox_t = target.bounding_box()

        # 3. Calculate Start and End Points (Center to Center)
        # We snap these to the 5px grid immediately
        start_x = snap(bbox_s.center.x, 5)
        start_y = snap(bbox_s.center.y, 5)
        end_x = snap(bbox_t.center.x, 5)
        end_y = snap(bbox_t.center.y, 5)

        # 4. Pull Back Logic (Account for 2px arrow size)
        # We calculate the vector to pull the end point back slightly
        import math
        dx = end_x - start_x
        dy = end_y - start_y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < 18:
            inkex.errormsg("Line too short! Minimum length is 18px.")
            return

        # Pull back the end point by 2px
        pullback = 2
        ratio = (dist - pullback) / dist
        adj_end_x = start_x + dx * ratio
        adj_end_y = start_y + dy * ratio

        # 5. Create the Path
        path_data = f"M {start_x},{start_y} L {adj_end_x},{adj_end_y}"

        attribs = {
            'style': 'stroke:#000000;stroke-width:1px;fill:none;',
            'd': path_data,
            'marker-end': 'url(#Arrow1Mend)'
        }

        line = PathElement(**attribs)
        self.svg.get_current_layer().add(line)


if __name__ == '__main__':
    DrawConnector().run()