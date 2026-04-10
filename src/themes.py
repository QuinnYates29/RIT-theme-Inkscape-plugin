# All themes (colors, fonts, etc) for RIT Formula Inkscape plugins

# === Schematic Colors (RITRacing Palette) ===
GREY         = "#DCDCDC" # Background / Containers
LIGHT_GREEN  = "#B6D7A8" # Logic / Process Body (e.g., "A lrr", "Convert to %")
DARK_BLUE    = "#69A4D9" # Header / Logic Titles (e.g., "Accelerator Pedal")
LIGHT_BLUE   = "#CFE2F3" # I/O / Sensor Body (e.g., "A ADC", "Accel Pos")
PURPLE       = "#B665A8" # State Change / Alert Body (e.g., "NORMAL", "HARD")

# === RIT Branding Colors ===
RIT_ORANGE   = "#F76902"
RIT_BLACK    = "#000000"
RIT_GRAY     = "#808080"
WHITE    = "#FFFFFF"

# === Font sizes ===
PRIMARY_TITLE_PX = "35px" # Main Page Title
GROUP_HEADER_PX  = "22px" # Large boundary boxes (e.g. "Driver Inputs")
SUB_GROUP_PX     = "16px" # Nested boundary boxes
BOX_TEXT_PX      = "14px" # Standard text inside boxes
ANNOTATION_PX    = "10px" # Text on arrows or small notes

# === Diagram rules ===
BOX_GRID  = 20
LINE_GRID = 5
STROKE_WIDTH = "1px"

# === Arrow Styles ===
ARROW_START    = "Arrow1Mstart"
ARROW_END      = "Arrow1Mend"
ARROW_PULLBACK = 2
MIN_ARROW_SEG  = 18

# === Styles (Dictionaries for .style = {}) ===

def get_style(fill_color, stroke_color=RIT_BLACK, stroke_width=STROKE_WIDTH):
    """Returns a standard dictionary for shape styles."""
    return {
        "fill": fill_color,
        "stroke": stroke_color,
        "stroke-width": stroke_width,
        "stroke-linejoin": "round",
        "stroke-linecap": "round"
    }

def get_text_style(font_size=BOX_TEXT_PX, color=RIT_BLACK, weight="normal"):
    """Returns a standard dictionary for text styles."""
    return {
        "font-size": font_size,
        "font-family": "sans-serif",
        "fill": color,
        "font-weight": weight,
        "text-align": "center",
        "text-anchor": "middle"
    }

# Pre-defined Theme Styles based on the Diagram
THEMES = {
    "purp_blk": {"fill": "#b665a8", "stroke": "#000000"},
    "purp_wht": {"fill": "#b665a8", "stroke": "#FFFFFF"},
    "grn_blk":  {"fill": "#b6d7a8", "stroke": "#000000"},
    "grn_wht":  {"fill": "#b6d7a8", "stroke": "#FFFFFF"},
    "dk_blu_blk": {"fill": "#69a4d9", "stroke": "#000000"},
    "dk_blu_wht": {"fill": "#69a4d9", "stroke": "#FFFFFF"},
    "blu_blk": {"fill": "#cfe2f3", "stroke": "#000000"},
    "blu_wht": {"fill": "#cfe2f3", "stroke": "#FFFFFF"},
}