import inkex
from inkex import PathElement, Marker


def snap(value, base=5):
    return round(value / base) * base


class DrawConnector(inkex.EffectExtension):
    def add_arguments(self, pars):
        # You can add options here for line style (straight vs orthogonal)
        pars.add_argument("--line_type", type=str, default="straight")

if __name__ == '__main__':
    DrawConnector().run()