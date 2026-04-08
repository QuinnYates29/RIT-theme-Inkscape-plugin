import inkex
from themes import *
from schematic_utils import *

class BoxGenerator(inkex.EffectExtension):
    def draw_box(self, title, x, y, width, height, fill_color, border_color):
        group = inkex.Group()
        group.set('inkscape:label', 'Box: ' + title)

        box = create_box(self, x, y, width, height, fill_color, border_color)
        box.style = get_style(fill_color, border_color)
        group.add(box)

        text = create_wrapped_text(x, y, width, height, title)
        text.style = get_text_style()
        group.add(text)

        self.svg.get_current_layer().add(group)

    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, default="Title")
        pars.add_argument("--height", type=float, default=50.0)
        pars.add_argument("--width", type=float, default=150.0)
        pars.add_argument("--theme", type=str, default="grn_blk", help="Box theme selection")
        pars.add_argument("--x", type=int, default = -1)
        pars.add_argument("--y", type=int, default = -1)

    def effect(self):
        title = self.options.title
        height = self.options.height
        width = self.options.width
        theme = self.options.theme

        p_width = self.svg.unittouu(self.svg.get("width"))
        p_height = self.svg.unittouu(self.svg.get("height"))
        x = self.options.x
        y = self.options.y

        if x == -1:
            x = p_width // 2
        if y == -1:
            y = p_height // 2

        match theme:
            case "grn_wht":
                fill_color = LIGHT_GREEN
                border_color = WHITE
            case "purp_blk":
                fill_color = PURPLE
                border_color = RIT_BLACK
            case "purp_wht":
                fill_color = PURPLE
                border_color = WHITE
            case "blu_blk":
                fill_color = LIGHT_BLUE
                border_color = RIT_BLACK
            case "blu_wht":
                fill_color = LIGHT_BLUE
                border_color = WHITE
            case "dk_blu_blk":
                fill_color = DARK_BLUE
                border_color = RIT_BLACK
            case "dk_blu_wht":
                fill_color = DARK_BLUE
                border_color = WHITE
            case _:
                fill_color = LIGHT_GREEN
                border_color = RIT_BLACK

        self.draw_box(title, x, y, width, height, fill_color, border_color)

if __name__ == "__main__":
    BoxGenerator().run()