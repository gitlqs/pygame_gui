"""
VirtualKeyboard — touch QWERTY keyboard widget.

Layout strictly follows gui/components/keyboard.py (10-column grid, 4 rows);
styling uses the pg_ui Button look.

Modes:
- letters:  Q..P / A..L / [shift] Z..M [back] / [123][SHIFT][SPACE]
- numbers:  1..0 / symbols_row2 / [empty] symbols_row3 [back] / [ABC][#+=][SPACE]
- symbols:  symbol set 1 (common) vs. set 2 (less common), toggled by #+= key

Dimensions are computed at construction from the target `width`. Each key is a
Button so it reuses pressed-translate and color transitions.

Caller wires two callbacks:
- on_input(ch)     — char(s) to insert
- on_backspace()   — delete char / selection
"""
import pygame
import theme
from button import Button


LETTER_ROW1 = list("QWERTYUIOP")
LETTER_ROW2 = list("ASDFGHJKL")
LETTER_ROW3 = list("ZXCVBNM")

SYMBOL_SET_1 = {
    'row2': ['-', ':', ';', '(', ')', '$', '&', '@', '"'],
    'row3': ['.', ',', '/', '?', '!', "'"],
}
SYMBOL_SET_2 = {
    'row2': ['[', ']', '{', '}', '#', '%', '^', '*', '+'],
    'row3': ['_', '\\', '|', '~', '`', '<', '>'],
}


class VirtualKeyboard:
    """
    Args:
        x, y, width: design-space position & total width.
        on_input(ch):     called when a printable key is pressed.
        on_backspace():   called when ← is pressed.
        gap_design:       gap between keys (design px).

    After construction, read `.height` to know how much vertical space it
    occupies in design space (for positioning above/below).
    """

    def __init__(self, x, y, width, on_input, on_backspace, gap_design=3):
        self.dx, self.dy = x, y
        self.dw = width
        self.on_input = on_input
        self.on_backspace = on_backspace
        self.gap = gap_design

        # state
        self.mode = 'letters'     # 'letters' | 'numbers'
        self.shift = False
        self.symbol_set = 1       # 1 or 2

        # key grid (design px) — 10 cols, 4 rows, square keys
        self.kw = (self.dw - self.gap * 9) / 10
        self.kh = self.kw
        self.height = int(self.kh * 4 + self.gap * 3)

        self.buttons = []
        self._rebuild()

    # ── Public ──────────────────────────────────────────────────────

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, surface):
        for b in self.buttons:
            b.draw(surface)

    # ── Key building ────────────────────────────────────────────────

    def _key(self, label, x, y, w, h, callback, special=False):
        """Create one Button at design coords (x, y, w, h)."""
        sr = theme.rect(x, y, w, h)
        btn = Button(
            sr.x, sr.y, sr.w, sr.h,
            bg_color=(theme.color_primary if special else theme.color_surface),
            pressed_color=(theme.color_primary_pressed if special
                           else theme.color_surface_pressed),
            border_color=(None if special else theme.color_border),
            border_width=theme.px(1),
            border_radius=theme.px(theme.radius_sm),
            shadow_color=(0, 0, 0, 18),
            shadow_offset=(0, theme.px(1)),
            shadow_blur=2,
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=callback,
        )
        text_color = theme.color_text_on_primary if special else theme.color_text
        font_name = 'label' if len(label) > 2 else 'heading'
        btn.add_text(label, theme.font(font_name), color=text_color)
        return btn

    def _rebuild(self):
        self.buttons = []
        x, y, kw, kh, gap = self.dx, self.dy, self.kw, self.kh, self.gap

        if self.mode == 'letters':
            # Row 1: Q..P
            for i, ch in enumerate(LETTER_ROW1):
                c = ch if self.shift else ch.lower()
                self.buttons.append(self._key(c, x + i * (kw + gap), y, kw, kh,
                                              lambda ch=c: self.on_input(ch)))
            # Row 2: A..L (offset by 0.5 key)
            y2 = y + (kh + gap)
            x2 = x + (kw + gap) / 2
            for i, ch in enumerate(LETTER_ROW2):
                c = ch if self.shift else ch.lower()
                self.buttons.append(self._key(c, x2 + i * (kw + gap), y2, kw, kh,
                                              lambda ch=c: self.on_input(ch)))
            # Row 3: [offset 1 key] Z..M [BACK]
            y3 = y + 2 * (kh + gap)
            x3 = x + (kw + gap)
            for i, ch in enumerate(LETTER_ROW3):
                c = ch if self.shift else ch.lower()
                self.buttons.append(self._key(c, x3 + i * (kw + gap), y3, kw, kh,
                                              lambda ch=c: self.on_input(ch)))
            back_x = x3 + len(LETTER_ROW3) * (kw + gap)
            back_w = x + self.dw - back_x
            self.buttons.append(self._key('back', back_x, y3, back_w, kh,
                                          self.on_backspace, special=True))
            # Row 4: [123] [SHIFT 1.5w] [SPACE 3.5w]  (matches gui layout)
            y4 = y + 3 * (kh + gap)
            self.buttons.append(self._key('123', x + 2 * kw, y4, kw, kh,
                                          self._toggle_mode, special=True))
            shift_label = 'SHIFT' if self.shift else 'shift'
            self.buttons.append(self._key(shift_label, x + 3 * kw + gap, y4, kw * 1.5, kh,
                                          self._toggle_shift, special=True))
            self.buttons.append(self._key('space', x + 4.5 * kw + 2 * gap, y4, kw * 3.5, kh,
                                          lambda: self.on_input(' ')))

        else:  # numbers / symbols
            # Row 1: 1..0
            for i, n in enumerate('1234567890'):
                self.buttons.append(self._key(n, x + i * (kw + gap), y, kw, kh,
                                              lambda n=n: self.on_input(n)))
            # Row 2: 9 symbols (offset by 0.5 key)
            y2 = y + (kh + gap)
            x2 = x + (kw + gap) / 2
            syms = (SYMBOL_SET_1 if self.symbol_set == 1 else SYMBOL_SET_2)['row2']
            for i, s in enumerate(syms):
                self.buttons.append(self._key(s, x2 + i * (kw + gap), y2, kw, kh,
                                              lambda s=s: self.on_input(s)))
            # Row 3: offset 1 key, 6 symbols + BACK
            y3 = y + 2 * (kh + gap)
            x3 = x + (kw + gap)
            syms3 = (SYMBOL_SET_1 if self.symbol_set == 1 else SYMBOL_SET_2)['row3']
            for i, s in enumerate(syms3):
                self.buttons.append(self._key(s, x3 + i * (kw + gap), y3, kw, kh,
                                              lambda s=s: self.on_input(s)))
            back_x = x3 + len(syms3) * (kw + gap)
            back_w = x + self.dw - back_x
            self.buttons.append(self._key('back', back_x, y3, back_w, kh,
                                          self.on_backspace, special=True))
            # Row 4: [ABC] [#+= / 123] [SPACE]
            y4 = y + 3 * (kh + gap)
            self.buttons.append(self._key('ABC', x + 2 * kw, y4, kw, kh,
                                          self._toggle_mode, special=True))
            sym_label = '123' if self.symbol_set == 2 else '#+='
            self.buttons.append(self._key(sym_label, x + 3 * kw + gap, y4, kw * 1.5, kh,
                                          self._toggle_symbol, special=True))
            self.buttons.append(self._key('space', x + 4.5 * kw + 2 * gap, y4, kw * 3.5, kh,
                                          lambda: self.on_input(' ')))

    # ── Mode toggles ────────────────────────────────────────────────

    def _toggle_shift(self):
        self.shift = not self.shift
        self._rebuild()

    def _toggle_mode(self):
        self.mode = 'numbers' if self.mode == 'letters' else 'letters'
        self.shift = False
        self.symbol_set = 1
        self._rebuild()

    def _toggle_symbol(self):
        self.symbol_set = 2 if self.symbol_set == 1 else 1
        self._rebuild()
