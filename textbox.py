"""
TextBox — display-only text field that opens a full-screen keyboard page
when tapped.

Touch-first design: no caret, no inline editing, no TEXTINPUT handling. All
editing happens in KeyboardInputPage. When the user finishes (Done), the new
text is written back via `set_text` and `on_change` fires.

Construction requires a `manager` reference — TextBox needs to push the
keyboard page when tapped.

Example:
    tb = TextBox(manager, 50, 50, 300, 50,
        label="Part number",         # shown as the keyboard-page title
        placeholder="e.g. 42-B",
        on_change=lambda val: print(val),
    )
"""
import pygame


class TextBox:
    def __init__(self, manager, x, y, width, height, **kwargs):
        self.manager = manager
        self.rect = pygame.Rect(x, y, width, height)

        self.text = str(kwargs.get('text', ''))
        self.label = kwargs.get('label', '')            # title for keyboard page
        self.placeholder = kwargs.get('placeholder', '')
        self.password = bool(kwargs.get('password', False))
        self.mask_char = kwargs.get('mask_char', '\u2022')
        self.max_length = int(kwargs.get('max_length', 0) or 0)
        self.disabled = bool(kwargs.get('disabled', False))

        # Styling — caller passes final (already-scaled) pixel values.
        self.font = kwargs.get('font')                  # required at draw time
        self.bg_color = kwargs.get('bg_color', (255, 255, 255))
        self.pressed_color = kwargs.get('pressed_color', (235, 240, 248))
        self.disabled_bg_color = kwargs.get('disabled_bg_color', (240, 240, 240))
        self.text_color = kwargs.get('text_color', (30, 30, 40))
        self.placeholder_color = kwargs.get('placeholder_color', (180, 180, 180))
        self.border_color = kwargs.get('border_color', (200, 200, 200))
        self.border_width = int(kwargs.get('border_width', 1))
        self.border_radius = int(kwargs.get('border_radius', 6))
        self.padding = self._parse_padding(kwargs.get('padding', (8, 12)))

        self.on_change = kwargs.get('on_change', None)

        self.state = 'normal'   # 'normal' | 'pressed'

    @staticmethod
    def _parse_padding(p):
        if isinstance(p, (int, float)):
            return (p, p, p, p)
        if len(p) == 2:
            return (p[0], p[1], p[0], p[1])
        if len(p) == 4:
            return tuple(p)
        return (0, 0, 0, 0)

    # ── API ──
    def set_text(self, text):
        new = str(text)
        if new != self.text:
            self.text = new
            if self.on_change:
                self.on_change(self.text)

    def set_disabled(self, disabled):
        self.disabled = bool(disabled)
        self.state = 'normal'

    def _display_text(self):
        if self.password:
            return self.mask_char * len(self.text)
        return self.text

    # ── Events ──
    def handle_event(self, event):
        if self.disabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = 'pressed'
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = (self.state == 'pressed')
            inside = self.rect.collidepoint(event.pos)
            self.state = 'normal'
            if was_pressed and inside:
                self._open_keyboard()

    def _open_keyboard(self):
        # Lazy import to avoid circular dep
        from keyboard_input_page import KeyboardInputPage
        page = KeyboardInputPage(self.manager, self)
        self.manager.push(page, transition='fade')

    # ── Draw ──
    def draw(self, surface):
        if self.disabled:
            bg = self.disabled_bg_color
        elif self.state == 'pressed':
            bg = self.pressed_color
        else:
            bg = self.bg_color

        pygame.draw.rect(surface, bg, self.rect, border_radius=self.border_radius)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect,
                             width=self.border_width, border_radius=self.border_radius)

        if not self.font:
            return

        pad_l = self.padding[3]
        disp = self._display_text()
        if disp:
            color = self.text_color if not self.disabled else (150, 150, 150)
            surf = self.font.render(disp, True, color)
        elif self.placeholder:
            surf = self.font.render(self.placeholder, True, self.placeholder_color)
        else:
            return

        ty = self.rect.y + (self.rect.height - surf.get_height()) // 2
        # clip to rect in case text is long
        prev_clip = surface.get_clip()
        surface.set_clip(self.rect)
        surface.blit(surf, (self.rect.x + pad_l, ty))
        surface.set_clip(prev_clip)
