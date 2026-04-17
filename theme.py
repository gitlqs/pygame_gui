"""
theme — centralized design tokens & responsive scaling.

Design baseline: 800 x 800 logical canvas. `theme.configure(screen_size=...)`
computes a uniform scale; `theme.px()`, `theme.rect()`, `theme.font()` all
transform design-space values to real screen pixels.

Pages write coordinates in the 800×800 design space. The framework scales
everything at draw time so the same UI runs on any resolution.
"""
import pygame

# ───── Palette ────────────────────────────────────────────────────
color_primary          = (24, 144, 255)
color_primary_pressed  = (9, 88, 217)
color_success          = (34, 197, 94)
color_warning          = (234, 179, 8)
color_danger           = (220, 38, 38)
color_info             = (99, 102, 241)

color_bg               = (245, 247, 250)
color_surface          = (255, 255, 255)
color_surface_pressed  = (230, 230, 235)

color_text             = (30, 30, 40)
color_text_muted       = (120, 125, 140)
color_text_disabled    = (160, 165, 180)
color_text_on_primary  = (255, 255, 255)

color_border           = (210, 215, 225)
color_border_active    = (24, 144, 255)

color_selection        = (180, 210, 255)
color_caret            = (30, 30, 40)

color_dialog_backdrop  = (0, 0, 0)          # overlaid with dynamic alpha
color_dialog_surface   = (255, 255, 255)

# ───── Typography (design px) ─────────────────────────────────────
FONT_SIZES = {
    'tiny':       14,
    'small':      18,
    'body':       22,
    'label':      24,
    'subheading': 28,
    'heading':    36,
    'title':      48,
    'display':    64,
}

font_path       = None   # None → pygame default
font_path_mono  = None   # None → pygame default (monospace fallback)

# ───── Sizing & Animation defaults ────────────────────────────────
radius_sm, radius_md, radius_lg = 6, 10, 16
padding_sm, padding_md, padding_lg = 8, 12, 20
border_width = 2

anim_fast  = 0.15
anim_med   = 0.25
anim_slow  = 0.40

# ───── Scaling state (set by configure()) ─────────────────────────
base_size   = (800, 800)
screen_size = (800, 800)
scale       = 1.0
offset      = (0.0, 0.0)   # letterbox offset when aspect differs

_font_cache = {}


def configure(screen_size_=(800, 800), base_size_=(800, 800),
              font_path_=None, font_path_mono_=None):
    """Set screen/baseline and recompute scale. Called once by App."""
    global base_size, screen_size, scale, offset, font_path, font_path_mono
    base_size = base_size_
    screen_size = screen_size_
    sw, sh = screen_size
    bw, bh = base_size
    scale = min(sw / bw, sh / bh)
    canvas_w = bw * scale
    canvas_h = bh * scale
    offset = ((sw - canvas_w) / 2, (sh - canvas_h) / 2)
    if font_path_ is not None:
        font_path = font_path_
    if font_path_mono_ is not None:
        font_path_mono = font_path_mono_
    _font_cache.clear()


def px(v):
    """Scale a design-px value to actual screen px."""
    return int(v * scale)


def point(x, y):
    """Transform a design-px point to screen coords (with letterbox)."""
    return (int(x * scale + offset[0]),
            int(y * scale + offset[1]))


def rect(x, y, w, h):
    """Build a pygame.Rect from design-px coords."""
    return pygame.Rect(
        int(x * scale + offset[0]),
        int(y * scale + offset[1]),
        int(w * scale),
        int(h * scale),
    )


def font(name_or_size, mono=False):
    """
    Get a cached Font by semantic name ('body', 'heading', …) or design-px size.

    Args:
        name_or_size: one of FONT_SIZES keys or an int design-px size.
        mono: use monospace font (requires `font_path_mono` set).
    """
    if isinstance(name_or_size, str):
        size_design = FONT_SIZES.get(name_or_size, 22)
    else:
        size_design = int(name_or_size)
    size_actual = max(8, int(size_design * scale))
    key = (size_actual, mono)
    if key not in _font_cache:
        path = font_path_mono if mono else font_path
        try:
            _font_cache[key] = pygame.font.Font(path, size_actual)
        except Exception:
            # Fallback to default if custom font fails
            _font_cache[key] = pygame.font.Font(None, size_actual)
    return _font_cache[key]
