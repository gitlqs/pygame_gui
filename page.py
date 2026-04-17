"""
Page base class.

A Page owns its widgets and implements three methods:
- handle_event(event)   – touch / mouse events
- update(dt)            – per-frame logic (optional)
- draw(surface)         – render to the given surface

Lifecycle hooks:
- on_enter()  – when the page becomes active (push or pop-return)
- on_leave()  – when the page is hidden (push-under or popped-off)

Pages write coordinates in **design space** (800×800 by default). Use
self.px() / self.rect() to produce scaled screen coordinates.
"""
import theme


class Page:
    def __init__(self, manager):
        self.manager = manager
        self._built = False

    # ── Coordinate helpers (design-px → screen-px) ──
    def px(self, v):
        return theme.px(v)

    def point(self, x, y):
        return theme.point(x, y)

    def rect(self, x, y, w, h):
        return theme.rect(x, y, w, h)

    # ── Lifecycle ──
    def on_enter(self):
        """Called when this page becomes top-of-stack."""
        pass

    def on_leave(self):
        """Called when this page is hidden (pushed-under or popped-off)."""
        pass

    # ── Main loop hooks ──
    def update(self, dt):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):
        raise NotImplementedError(f"{type(self).__name__}.draw() not implemented")
