#!/usr/bin/env python3
import inkex
from lxml import etree

class TwoBoxesExtension(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--top_text", type=str, default="Top Box")

    def effect(self):
        layer = self.svg.get_current_layer()

        def rect(x, y, w, h):
            layer.append(
                etree.Element(
                    inkex.addNS("rect", "svg"),
                    {
                        "x": str(x),
                        "y": str(y),
                        "width": str(w),
                        "height": str(h),
                        "style": "fill:white;stroke:black;stroke-width:2"
                    }
                )
            )

        def line(x1, y1, x2, y2):
            layer.append(
                etree.Element(
                    inkex.addNS("line", "svg"),
                    {
                        "x1": str(x1),
                        "y1": str(y1),
                        "x2": str(x2),
                        "y2": str(y2),
                        "style": "stroke:black;stroke-width:2"
                    }
                )
            )

        def text(x, y, content):
            t = etree.Element(
                inkex.addNS("text", "svg"),
                {
                    "x": str(x),
                    "y": str(y),
                    "style": "font-size:14px;text-anchor:middle"
                }
            )
            t.text = content
            layer.append(t)

        # Layout
        box_w = 120
        box_h = 50
        x = 100
        y_top = 50
        y_bot = 170

        rect(x, y_top, box_w, box_h)
        rect(x, y_bot, box_w, box_h)

        line(
            x + box_w / 2,
            y_top + box_h,
            x + box_w / 2,
            y_bot
        )

        text(
            x + box_w / 2,
            y_top + box_h / 2 + 5,
            self.options.top_text
        )

if __name__ == "__main__":
    TwoBoxesExtension().run()
