"""
PageManager — stack-based navigation + animated transitions + dialog overlays.

Transitions (opt-in):
- None       : instant (default)
- 'fade'     : alpha crossfade
- 'slide'    : new page slides in from right; old slides left
- 'morph'    : new page expands from source_rect; old fades out

Transitions pre-render both pages to offscreen surfaces and then composite them
over N frames. Widget logic is paused during a transition → cost is constant
regardless of page complexity.

Dialogs are overlay pages drawn above the current page. They don't pop the
page underneath; they live on a parallel stack.
"""
import pygame
import theme
from animation import animator


class PageManager:
    def __init__(self, screen):
        self.screen = screen
        self.stack = []         # page stack
        self.dialogs = []       # dialog overlay stack
        self._transition = None # active transition state

    # ── Stack operations ────────────────────────────────────────────

    def push(self, page, transition=None, source_rect=None):
        """Push a new page. transition: None | 'fade' | 'slide' | 'morph'."""
        if self.stack:
            self.stack[-1].on_leave()
        self.stack.append(page)
        page.on_enter()
        # Stash a COPY of source_rect on the page so the later pop can morph
        # back to the same spot automatically.
        if transition == 'morph' and source_rect is not None:
            page._morph_source_rect = pygame.Rect(source_rect)
        if transition and len(self.stack) >= 2:
            self._start_transition('push', transition, source_rect, self.stack[-2], page)

    def pop(self, transition=None, source_rect=None):
        """
        Pop the top page (keeps at least one on the stack).

        If `transition='morph'` and no `source_rect` is passed, the rect stored
        on the page at push time is reused — so pop automatically morphs back
        to the widget that triggered the push.
        """
        if len(self.stack) <= 1:
            return None
        popped = self.stack.pop()
        popped.on_leave()
        self.stack[-1].on_enter()
        if transition:
            sr = source_rect if source_rect is not None else getattr(popped, '_morph_source_rect', None)
            self._start_transition('pop', transition, sr, popped, self.stack[-1])
        return popped

    def replace(self, page, transition='fade'):
        """Replace top page with a new one."""
        old = self.stack[-1] if self.stack else None
        if old:
            old.on_leave()
            self.stack.pop()
        self.stack.append(page)
        page.on_enter()
        if transition and old:
            self._start_transition('replace', transition, None, old, page)

    def current(self):
        return self.stack[-1] if self.stack else None

    # ── Dialogs ─────────────────────────────────────────────────────

    def present_dialog(self, dialog):
        self.dialogs.append(dialog)
        dialog.on_enter()

    def dismiss_dialog(self):
        if self.dialogs:
            d = self.dialogs.pop()
            d.on_leave()

    # ── Main-loop hooks ─────────────────────────────────────────────

    def handle_event(self, event):
        # Swallow events while transitioning to avoid double-dispatch
        if self._transition is not None:
            return
        if self.dialogs:
            self.dialogs[-1].handle_event(event)
            return
        if self.stack:
            self.stack[-1].handle_event(event)

    def update(self, dt):
        if self._transition is not None:
            self._transition['t'] += dt
            if self._transition['t'] >= self._transition['duration']:
                self._transition = None
        if self.stack:
            self.stack[-1].update(dt)
        for d in self.dialogs:
            d.update(dt)

    def draw(self):
        if not self.stack and not self.dialogs:
            return
        if self._transition is not None:
            self._draw_transition()
        elif self.stack:
            self.stack[-1].draw(self.screen)
        # Dialog overlays always on top
        for d in self.dialogs:
            d.draw(self.screen)

    def is_busy(self):
        return self._transition is not None or animator.is_busy()

    # ── Transition internals ────────────────────────────────────────

    def _start_transition(self, kind, transition, source_rect, from_page, to_page):
        sw, sh = self.screen.get_size()
        before = pygame.Surface((sw, sh), pygame.SRCALPHA)
        after = pygame.Surface((sw, sh), pygame.SRCALPHA)
        from_page.draw(before)
        to_page.draw(after)
        self._transition = {
            'kind': kind,
            'type': transition,
            'source_rect': source_rect,
            'before': before,
            'after': after,
            't': 0.0,
            'duration': self._duration(transition),
        }

    def _duration(self, transition):
        if transition == 'morph':
            return 0.35
        if transition == 'slide':
            return 0.28
        return 0.22  # fade / default

    def _draw_transition(self):
        tr = self._transition
        t = min(1.0, tr['t'] / tr['duration'])
        eased = 1 - (1 - t) ** 3  # ease_out_cubic
        before, after = tr['before'], tr['after']
        sw, sh = self.screen.get_size()
        ttype = tr['type']
        reverse = (tr['kind'] == 'pop')

        if ttype == 'fade':
            # Alpha crossfade. Push: new fades in. Pop: old fades out.
            p = (1 - eased) if reverse else eased
            self.screen.blit(before, (0, 0))
            after.set_alpha(int(255 * p))
            self.screen.blit(after, (0, 0))

        elif ttype == 'slide':
            p = (1 - eased) if reverse else eased
            shift = int(sw * p)
            self.screen.blit(before, (-shift, 0))
            self.screen.blit(after, (sw - shift, 0))

        elif ttype == 'morph':
            sr = tr['source_rect']
            if sr is None:
                # No source rect (e.g. pop without stashed rect) → fall back to fade.
                p = (1 - eased) if reverse else eased
                self.screen.blit(before, (0, 0))
                after.set_alpha(int(255 * p))
                self.screen.blit(after, (0, 0))
                return

            # `mp` = morph progress of the moving page:
            #   mp=0 → size/pos of source_rect (tiny)
            #   mp=1 → size/pos of full screen
            # Push: mp 0→1 (new page grows OUT of source_rect to fill screen).
            # Pop:  mp 1→0 (exiting page shrinks BACK into source_rect).
            if reverse:
                mp = 1 - eased
                # The returning-to page is the static "destination" behind.
                # Fade it in as the exiting page shrinks away.
                after.set_alpha(int(255 * eased))
                self.screen.blit(after, (0, 0))
                moving = before
            else:
                mp = eased
                # The old page stays put, fades out under the growing new page.
                before.set_alpha(int(255 * (1 - mp)))
                self.screen.blit(before, (0, 0))
                moving = after

            tgt_w = max(1, int(sr.w + (sw - sr.w) * mp))
            tgt_h = max(1, int(sr.h + (sh - sr.h) * mp))
            cx = sr.centerx + (sw / 2 - sr.centerx) * mp
            cy = sr.centery + (sh / 2 - sr.centery) * mp
            scaled = pygame.transform.smoothscale(moving, (tgt_w, tgt_h))
            scaled.set_alpha(int(255 * mp))
            self.screen.blit(scaled, (int(cx - tgt_w / 2), int(cy - tgt_h / 2)))
        else:
            # unknown / no-op
            self.screen.blit(after, (0, 0))
