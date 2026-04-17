"""
Dialog — programmatic modal API with blurred backdrop.

Usage:
    Dialog.alert(manager, "Saved", "Settings have been saved.", on_ok=lambda: ...)
    Dialog.confirm(manager, "Delete?", "This cannot be undone.",
                   on_confirm=fn, on_cancel=fn)

Dialogs are drawn as overlays by PageManager. The page underneath stays
visible (blurred) but does not receive events.

Performance notes:
- The backdrop is blurred **once** when the dialog appears via a downsample-
  upsample trick (~10x cheaper than per-frame Gaussian). The blurred surface
  is cached for the lifetime of the dialog.
- Dialog content is rendered directly each frame (no offscreen). Presentation
  animation uses alpha + backdrop fade only (no scale) to keep hit-testing
  trivial for the inner buttons.
"""
import pygame
import theme
from animation import animator
from button import Button


# ───── Core dialog ────────────────────────────────────────────────

class Dialog:
    """Base class. Subclasses render their box via `_draw_box(surface)`."""

    def __init__(self, manager, title, message=None):
        self.manager = manager
        self.title = title
        self.message = message
        # animated properties
        self.backdrop_alpha = 0.0
        self.content_alpha = 0.0
        self._backdrop_blurred = None
        self._interactive = False   # becomes True once entrance anim completes

    # ── Factory helpers (programmatic API) ──
    @staticmethod
    def alert(manager, title, message, on_ok=None, ok_text="OK"):
        d = _AlertDialog(manager, title, message, on_ok, ok_text)
        manager.present_dialog(d)
        return d

    @staticmethod
    def confirm(manager, title, message, on_confirm=None, on_cancel=None,
                confirm_text="Confirm", cancel_text="Cancel", danger=False):
        d = _ConfirmDialog(manager, title, message, on_confirm, on_cancel,
                           confirm_text, cancel_text, danger)
        manager.present_dialog(d)
        return d

    # ── Lifecycle ──
    def on_enter(self):
        self._snapshot_backdrop()
        animator.tween(self, 'backdrop_alpha', 180.0, duration=theme.anim_med, easing='ease_out')
        animator.tween(self, 'content_alpha', 255.0, duration=theme.anim_med, easing='ease_out',
                       on_complete=self._finish_entrance)
        self._build_buttons()

    def _finish_entrance(self):
        self._interactive = True

    def on_leave(self):
        pass

    def dismiss(self):
        self.manager.dismiss_dialog()

    # ── Rendering ──
    def _snapshot_backdrop(self):
        sw, sh = self.manager.screen.get_size()
        snap = pygame.Surface((sw, sh))
        # Draw whatever is underneath
        if self.manager.stack:
            self.manager.stack[-1].draw(snap)
        # Downsample-upsample blur (fast, cached)
        small = pygame.transform.smoothscale(snap, (max(2, sw // 8), max(2, sh // 8)))
        self._backdrop_blurred = pygame.transform.smoothscale(small, (sw, sh))

    def draw(self, surface):
        sw, sh = surface.get_size()
        # Blurred page
        if self._backdrop_blurred is not None:
            surface.blit(self._backdrop_blurred, (0, 0))
        # Dim overlay
        dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
        dim.fill((0, 0, 0, int(self.backdrop_alpha)))
        surface.blit(dim, (0, 0))
        # Dialog box
        self._draw_box(surface)

    def update(self, dt):
        pass

    def handle_event(self, event):
        if not self._interactive:
            return
        for btn in self._buttons():
            btn.handle_event(event)

    # ── Subclass overrides ──
    def _build_buttons(self):
        pass

    def _buttons(self):
        return []

    def _draw_box(self, surface):
        raise NotImplementedError


# ───── Dialog box geometry helpers ────────────────────────────────

DIALOG_W   = 500
DIALOG_MIN_H = 280
DIALOG_RADIUS = 16
DIALOG_PAD = 30


def _dialog_rect():
    """Centered dialog rect in design space (800×800 baseline)."""
    bw, bh = theme.base_size
    x = (bw - DIALOG_W) // 2
    y = (bh - DIALOG_MIN_H) // 2
    return pygame.Rect(x, y, DIALOG_W, DIALOG_MIN_H)


def _render_multiline(surface, text, font, color, box_rect_screen, padding_px):
    """Render wrapped text centered in box. Returns y-bottom of last line."""
    if not text:
        return box_rect_screen.top
    lines = text.split('\n')
    line_h = font.get_linesize()
    total_h = line_h * len(lines)
    y = box_rect_screen.centery - total_h / 2
    for ln in lines:
        surf = font.render(ln, True, color)
        x = box_rect_screen.centerx - surf.get_width() / 2
        surface.blit(surf, (int(x), int(y)))
        y += line_h
    return y


# ───── Built-in dialog types ──────────────────────────────────────

class _AlertDialog(Dialog):
    def __init__(self, manager, title, message, on_ok, ok_text):
        super().__init__(manager, title, message)
        self.on_ok = on_ok
        self.ok_text = ok_text
        self.ok_btn = None

    def _build_buttons(self):
        # Compute button rect in design space, then scale to screen
        dr = _dialog_rect()
        btn_w, btn_h = 160, 52
        bx = dr.centerx - btn_w // 2
        by = dr.bottom - theme.padding_lg - btn_h
        sr = theme.rect(bx, by, btn_w, btn_h)
        self.ok_btn = Button(
            sr.x, sr.y, sr.w, sr.h,
            bg_color=theme.color_primary,
            pressed_color=theme.color_primary_pressed,
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=self._on_ok,
        )
        self.ok_btn.add_text(self.ok_text, theme.font('label'),
                             color=theme.color_text_on_primary)

    def _buttons(self):
        return [self.ok_btn] if self.ok_btn else []

    def _on_ok(self):
        self.dismiss()
        if self.on_ok:
            self.on_ok()

    def _draw_box(self, surface):
        dr = _dialog_rect()
        box = theme.rect(dr.x, dr.y, dr.w, dr.h)
        # Shadow (light)
        shadow = pygame.Surface((box.w + theme.px(20), box.h + theme.px(20)), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, int(30 * self.content_alpha / 255)),
                         shadow.get_rect(), border_radius=theme.px(DIALOG_RADIUS) + theme.px(10))
        surface.blit(shadow, (box.x - theme.px(10), box.y - theme.px(10) + theme.px(6)))

        # Box
        box_surf = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(box_surf, theme.color_dialog_surface + (int(self.content_alpha),),
                         box_surf.get_rect(), border_radius=theme.px(DIALOG_RADIUS))
        surface.blit(box_surf, box.topleft)

        # Title
        tf = theme.font('heading')
        tsurf = tf.render(self.title, True, theme.color_text)
        tsurf.set_alpha(int(self.content_alpha))
        surface.blit(tsurf, (box.centerx - tsurf.get_width() // 2, box.top + theme.px(DIALOG_PAD)))

        # Message
        if self.message:
            mf = theme.font('body')
            lines = self.message.split('\n')
            line_h = mf.get_linesize()
            y = box.top + theme.px(DIALOG_PAD) + tf.get_linesize() + theme.px(10)
            for ln in lines:
                s = mf.render(ln, True, theme.color_text_muted)
                s.set_alpha(int(self.content_alpha))
                surface.blit(s, (box.centerx - s.get_width() // 2, y))
                y += line_h

        # Button
        if self.ok_btn:
            self.ok_btn.draw(surface)


class _ConfirmDialog(Dialog):
    def __init__(self, manager, title, message, on_confirm, on_cancel,
                 confirm_text, cancel_text, danger):
        super().__init__(manager, title, message)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.danger = danger
        self.cancel_btn = None
        self.confirm_btn = None

    def _build_buttons(self):
        dr = _dialog_rect()
        btn_w, btn_h, gap = 160, 52, 20
        total = btn_w * 2 + gap
        bx = dr.centerx - total // 2
        by = dr.bottom - theme.padding_lg - btn_h

        cr = theme.rect(bx, by, btn_w, btn_h)
        self.cancel_btn = Button(
            cr.x, cr.y, cr.w, cr.h,
            bg_color=theme.color_surface,
            pressed_color=theme.color_surface_pressed,
            border_color=theme.color_border,
            border_width=theme.px(1),
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=self._on_cancel,
        )
        self.cancel_btn.add_text(self.cancel_text, theme.font('label'), color=theme.color_text)

        confirm_bg = theme.color_danger if self.danger else theme.color_primary
        confirm_pressed = tuple(max(0, c - 25) for c in confirm_bg)
        xr = theme.rect(bx + btn_w + gap, by, btn_w, btn_h)
        self.confirm_btn = Button(
            xr.x, xr.y, xr.w, xr.h,
            bg_color=confirm_bg,
            pressed_color=confirm_pressed,
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=self._on_confirm,
        )
        self.confirm_btn.add_text(self.confirm_text, theme.font('label'),
                                  color=theme.color_text_on_primary)

    def _buttons(self):
        return [b for b in (self.cancel_btn, self.confirm_btn) if b]

    def _on_cancel(self):
        self.dismiss()
        if self.on_cancel:
            self.on_cancel()

    def _on_confirm(self):
        self.dismiss()
        if self.on_confirm:
            self.on_confirm()

    def _draw_box(self, surface):
        dr = _dialog_rect()
        box = theme.rect(dr.x, dr.y, dr.w, dr.h)

        # shadow
        shadow = pygame.Surface((box.w + theme.px(20), box.h + theme.px(20)), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, int(30 * self.content_alpha / 255)),
                         shadow.get_rect(), border_radius=theme.px(DIALOG_RADIUS) + theme.px(10))
        surface.blit(shadow, (box.x - theme.px(10), box.y - theme.px(10) + theme.px(6)))

        box_surf = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(box_surf, theme.color_dialog_surface + (int(self.content_alpha),),
                         box_surf.get_rect(), border_radius=theme.px(DIALOG_RADIUS))
        surface.blit(box_surf, box.topleft)

        tf = theme.font('heading')
        tsurf = tf.render(self.title, True, theme.color_text)
        tsurf.set_alpha(int(self.content_alpha))
        surface.blit(tsurf, (box.centerx - tsurf.get_width() // 2, box.top + theme.px(DIALOG_PAD)))

        if self.message:
            mf = theme.font('body')
            lines = self.message.split('\n')
            line_h = mf.get_linesize()
            y = box.top + theme.px(DIALOG_PAD) + tf.get_linesize() + theme.px(10)
            for ln in lines:
                s = mf.render(ln, True, theme.color_text_muted)
                s.set_alpha(int(self.content_alpha))
                surface.blit(s, (box.centerx - s.get_width() // 2, y))
                y += line_h

        if self.cancel_btn:
            self.cancel_btn.draw(surface)
        if self.confirm_btn:
            self.confirm_btn.draw(surface)
