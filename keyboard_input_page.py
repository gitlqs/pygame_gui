"""
KeyboardInputPage — full-screen text input page with virtual keyboard.

Flow:
  user taps TextBox → TextBox.manager.push(KeyboardInputPage(manager, textbox))
  user edits text → Done pops page, writes text back to textbox
  Cancel pops without saving.

The input field uses a monospace font, so caret / selection / hit-testing use
`char_w = font.size(' ')[0]` (every character is the same width).

Gesture model (handled inside _InputField):
- 1st tap                 : move caret to nearest char boundary
- 2nd tap same spot <400ms : select word around position
- 3rd tap same spot <400ms : select all
- 4th+ tap                 : resets to single-tap
"""
import time
import re
import pygame

import theme
from page import Page
from button import Button
from virtual_keyboard import VirtualKeyboard


# ───── Internal input field (mono font) ──────────────────────────

class _InputField:
    """Single-line text editor used inside KeyboardInputPage only."""

    TAP_TIME_WINDOW = 0.4
    TAP_DIST_PX = 20

    def __init__(self, rect, font, text=''):
        self.rect = rect                        # screen coords
        self.font = font                        # monospace
        self.text = str(text)
        self.caret = len(self.text)
        self.sel_anchor = None                  # selection anchor (None = no selection)
        self.scroll_x = 0
        self._padding = theme.px(12)
        self._blink_timer = 0.0
        self._caret_visible = True
        self._last_tap_time = 0.0
        self._last_tap_pos = (-1000, -1000)
        self._tap_count = 0

    # ── Properties ──
    @property
    def char_w(self):
        return self.font.size(' ')[0]

    def has_selection(self):
        return self.sel_anchor is not None and self.sel_anchor != self.caret

    def _sel_range(self):
        if not self.has_selection():
            return None
        a, b = sorted((self.sel_anchor, self.caret))
        return a, b

    def clear_selection(self):
        self.sel_anchor = None

    # ── Input ops ──
    def insert(self, s):
        if self.has_selection():
            a, b = self._sel_range()
            self.text = self.text[:a] + s + self.text[b:]
            self.caret = a + len(s)
        else:
            self.text = self.text[:self.caret] + s + self.text[self.caret:]
            self.caret += len(s)
        self.clear_selection()
        self._reset_blink()

    def backspace(self):
        if self.has_selection():
            a, b = self._sel_range()
            self.text = self.text[:a] + self.text[b:]
            self.caret = a
            self.clear_selection()
        elif self.caret > 0:
            self.text = self.text[:self.caret - 1] + self.text[self.caret:]
            self.caret -= 1
        self._reset_blink()

    def _reset_blink(self):
        self._caret_visible = True
        self._blink_timer = 0

    # ── Tap / gesture ──
    def on_tap(self, pos, now):
        idx = self._pos_to_index(pos[0])
        dx = pos[0] - self._last_tap_pos[0]
        dy = pos[1] - self._last_tap_pos[1]
        near = (dx * dx + dy * dy) < (self.TAP_DIST_PX * self.TAP_DIST_PX)
        fast = (now - self._last_tap_time) < self.TAP_TIME_WINDOW

        if near and fast:
            self._tap_count += 1
        else:
            self._tap_count = 1
        self._last_tap_time = now
        self._last_tap_pos = pos

        if self._tap_count == 1:
            self.caret = idx
            self.clear_selection()
        elif self._tap_count == 2:
            self._select_word(idx)
        elif self._tap_count >= 3:
            self._select_all()
            # prevent a 4th tap from becoming tap#4
            self._tap_count = 0
            self._last_tap_time = 0
        self._reset_blink()

    def _select_word(self, idx):
        """Select the word containing idx (or whitespace run if idx is blank)."""
        if not self.text:
            return
        idx = max(0, min(idx, len(self.text) - 1 if idx >= len(self.text) else idx))
        # look for non-whitespace word; if on whitespace, select whitespace run
        if idx < len(self.text) and self.text[idx].isspace():
            pattern = r'\s+'
        else:
            pattern = r'\S+'
        for m in re.finditer(pattern, self.text):
            if m.start() <= idx < m.end():
                self.sel_anchor = m.start()
                self.caret = m.end()
                return
        # fallback: nearest
        self.sel_anchor = None

    def _select_all(self):
        self.sel_anchor = 0
        self.caret = len(self.text)

    # ── Geometry ──
    def _pos_to_index(self, x_screen):
        cw = self.char_w
        if cw <= 0:
            return 0
        rel = x_screen - self.rect.x - self._padding + self.scroll_x
        # round to nearest boundary
        idx = int(round(rel / cw))
        return max(0, min(len(self.text), idx))

    def _update_scroll(self):
        cw = self.char_w
        caret_px = self.caret * cw
        inner_w = self.rect.width - 2 * self._padding
        if caret_px < self.scroll_x:
            self.scroll_x = caret_px
        elif caret_px > self.scroll_x + inner_w:
            self.scroll_x = caret_px - inner_w
        self.scroll_x = max(0, self.scroll_x)

    # ── Per-frame ──
    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer > 0.5:
            self._caret_visible = not self._caret_visible
            self._blink_timer = 0

    def draw(self, surface, bg, fg, sel_color, caret_color, border):
        self._update_scroll()
        r = self.rect
        radius = theme.px(theme.radius_md)
        pygame.draw.rect(surface, bg, r, border_radius=radius)
        if border:
            pygame.draw.rect(surface, border, r, theme.px(2), border_radius=radius)

        inner = pygame.Rect(r.x + self._padding, r.y + self._padding,
                            r.width - 2 * self._padding, r.height - 2 * self._padding)

        prev_clip = surface.get_clip()
        surface.set_clip(inner)

        cw = self.char_w
        # selection rect
        if self.has_selection():
            a, b = self._sel_range()
            sel_x = inner.x + a * cw - self.scroll_x
            sel_w = (b - a) * cw
            pygame.draw.rect(surface, sel_color,
                             (sel_x, inner.y, sel_w, inner.height),
                             border_radius=theme.px(3))

        # text
        if self.text:
            ts = self.font.render(self.text, True, fg)
            ty = inner.y + (inner.height - ts.get_height()) // 2
            surface.blit(ts, (inner.x - self.scroll_x, ty))

        # caret
        if not self.has_selection() and self._caret_visible:
            cx = inner.x + self.caret * cw - self.scroll_x
            pygame.draw.line(surface, caret_color,
                             (cx, inner.y + theme.px(4)),
                             (cx, inner.y + inner.height - theme.px(4)),
                             theme.px(2))

        surface.set_clip(prev_clip)


# ───── Page ──────────────────────────────────────────────────────

class KeyboardInputPage(Page):
    def __init__(self, manager, textbox):
        super().__init__(manager)
        self.textbox = textbox
        self.title_text = getattr(textbox, 'label', '') or "Enter text"
        self.is_password = bool(getattr(textbox, 'password', False))
        self.max_length = int(getattr(textbox, 'max_length', 0) or 0)

        # Cancel / Done buttons (design coords: 800×800)
        cr = theme.rect(30, 24, 110, 52)
        self.cancel_btn = Button(
            cr.x, cr.y, cr.w, cr.h,
            bg_color=theme.color_surface,
            pressed_color=theme.color_surface_pressed,
            border_color=theme.color_border,
            border_width=theme.px(1),
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=self._cancel,
        )
        self.cancel_btn.add_text("Cancel", theme.font('label'), color=theme.color_text)

        dr = theme.rect(800 - 30 - 110, 24, 110, 52)
        self.done_btn = Button(
            dr.x, dr.y, dr.w, dr.h,
            bg_color=theme.color_primary,
            pressed_color=theme.color_primary_pressed,
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=self._done,
        )
        self.done_btn.add_text("Done", theme.font('label'), color=theme.color_text_on_primary)

        # Input field
        ir = theme.rect(40, 120, 720, 80)
        mono_font = theme.font('subheading', mono=True)
        self.input_field = _InputField(ir, mono_font, text=textbox.text)

        # Virtual keyboard (bottom 4 rows, key size auto from width)
        self.keyboard = VirtualKeyboard(
            x=20, y=470, width=760,
            on_input=self._on_key,
            on_backspace=self._on_backspace,
        )

    # ── Callbacks ──

    def _on_key(self, ch):
        if self.max_length > 0:
            pending_len = len(self.input_field.text) + len(ch)
            if self.input_field.has_selection():
                a, b = self.input_field._sel_range()
                pending_len -= (b - a)
            if pending_len > self.max_length:
                return
        self.input_field.insert(ch)

    def _on_backspace(self):
        self.input_field.backspace()

    def _done(self):
        self.textbox.set_text(self.input_field.text)
        self.manager.pop(transition='fade')

    def _cancel(self):
        self.manager.pop(transition='fade')

    # ── Page overrides ──

    def handle_event(self, event):
        self.cancel_btn.handle_event(event)
        self.done_btn.handle_event(event)
        # Input field tap gesture
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.input_field.rect.collidepoint(event.pos):
                self.input_field.on_tap(event.pos, time.time())
        # Keyboard keys
        self.keyboard.handle_event(event)

    def update(self, dt):
        self.input_field.update(dt)

    def draw(self, surface):
        surface.fill(theme.color_bg)

        # Title (centered top)
        title_font = theme.font('heading')
        display_title = self.title_text
        if self.is_password:
            display_title = self.title_text  # don't prefix; password masking only affects display
        ts = title_font.render(display_title, True, theme.color_text)
        cx, cy = theme.point(400, 60)
        surface.blit(ts, (cx - ts.get_width() // 2, cy - ts.get_height() // 2))

        # Buttons
        self.cancel_btn.draw(surface)
        self.done_btn.draw(surface)

        # Input field (optionally render masked text)
        if self.is_password:
            # Temporarily swap to mask for rendering
            real_text = self.input_field.text
            self.input_field.text = '\u2022' * len(real_text)
            real_caret = self.input_field.caret
            self.input_field.draw(surface,
                bg=theme.color_surface,
                fg=theme.color_text,
                sel_color=theme.color_selection,
                caret_color=theme.color_caret,
                border=theme.color_border_active,
            )
            self.input_field.text = real_text
        else:
            self.input_field.draw(surface,
                bg=theme.color_surface,
                fg=theme.color_text,
                sel_color=theme.color_selection,
                caret_color=theme.color_caret,
                border=theme.color_border_active,
            )

        # Keyboard
        self.keyboard.draw(surface)
