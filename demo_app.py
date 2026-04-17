"""
Demo: full v2 framework — theme + pages + animated transitions + dialogs +
tap-to-edit textbox (virtual keyboard page).

Run:
    python demo_app.py

Tap each row in the Settings page to edit it. Tap the Save button to see a
confirmation dialog. Tap "About" to push a page with a morph transition.
"""
import pygame
import theme
from app import App
from page import Page
from button import Button
from label import Label
from checkbox import Checkbox
from progress import Progress
from pagecontrol import PageControl
from textbox import TextBox
from dialog import Dialog
from animation import animator


# ───────────────────────────────────────────────────────────────────
# Settings page — tap rows to edit via keyboard page
# ───────────────────────────────────────────────────────────────────

class SettingsPage(Page):
    def __init__(self, manager):
        super().__init__(manager)

        # Fade-in animation state (applied at draw time)
        self.content_alpha = 0.0

        # TextBox rows — each opens the keyboard page when tapped
        font_body = theme.font('body')
        tb_style = dict(
            font=font_body,
            border_radius=theme.px(theme.radius_md),
            border_color=theme.color_border,
            border_width=theme.px(1),
            padding=(theme.px(theme.padding_sm), theme.px(theme.padding_md)),
        )

        r1 = theme.rect(60, 130, 680, 60)
        self.tb_name = TextBox(manager, r1.x, r1.y, r1.w, r1.h,
            label="Part Name", placeholder="Tap to enter name...", **tb_style)

        r2 = theme.rect(60, 210, 680, 60)
        self.tb_number = TextBox(manager, r2.x, r2.y, r2.w, r2.h,
            label="Serial Number", placeholder="Tap to enter serial...", **tb_style)

        r3 = theme.rect(60, 290, 680, 60)
        self.tb_pwd = TextBox(manager, r3.x, r3.y, r3.w, r3.h,
            label="Admin Password", placeholder="Tap to set password...",
            password=True, **tb_style)

        # Checkboxes
        self.cb_autostart = Checkbox(
            theme.px(60), theme.px(400),
            box_size=theme.px(28), label="Auto-start on boot", font=font_body,
            checked=True,
        )
        self.cb_telemetry = Checkbox(
            theme.px(60), theme.px(450),
            box_size=theme.px(28), label="Send usage telemetry", font=font_body,
        )

        # Progress bar (animated)
        pr = theme.rect(60, 520, 680, 14)
        self.progress = Progress(pr.x, pr.y, pr.w, pr.h, value=0.35)

        # Pagecontrol + buttons
        pc = theme.rect(360, 570, 80, 20)
        self.pagectrl = PageControl(pc.x, pc.y, count=3, current=0,
            dot_size=theme.px(8), active_size=theme.px(14), gap=theme.px(10))

        # Save / About / Delete buttons
        self.btn_about = self._pill_btn(60, 640, 200, 70,
            label="About", color=theme.color_surface,
            text_color=theme.color_text, border=True,
            on_click=self._on_about)
        self.btn_save = self._pill_btn(300, 640, 200, 70,
            label="Save", color=theme.color_primary,
            text_color=theme.color_text_on_primary,
            on_click=self._on_save)
        self.btn_delete = self._pill_btn(540, 640, 200, 70,
            label="Reset", color=theme.color_danger,
            text_color=theme.color_text_on_primary,
            on_click=self._on_delete)

        self.widgets = [
            self.tb_name, self.tb_number, self.tb_pwd,
            self.cb_autostart, self.cb_telemetry,
            self.pagectrl,
            self.btn_about, self.btn_save, self.btn_delete,
        ]

    def _pill_btn(self, x, y, w, h, label, color, text_color, border=False, on_click=None):
        r = theme.rect(x, y, w, h)
        kwargs = dict(
            bg_color=color,
            pressed_color=tuple(max(0, c - 25) for c in color[:3]),
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 25),
            shadow_offset=(0, theme.px(3)),
            shadow_blur=3,
            pressed_translate=(0, theme.px(2)),
            on_mouse_up=on_click,
        )
        if border:
            kwargs['border_color'] = theme.color_border
            kwargs['border_width'] = theme.px(1)
            kwargs['shadow_color'] = (0, 0, 0, 0)
        btn = Button(r.x, r.y, r.w, r.h, **kwargs)
        btn.add_text(label, theme.font('label'), color=text_color)
        return btn

    # ── Lifecycle ──
    def on_enter(self):
        self.content_alpha = 0.0
        animator.tween(self, 'content_alpha', 255.0, duration=theme.anim_med, easing='ease_out')
        # Simulate progress increments over time
        self._sim_progress(0)

    def _sim_progress(self, step):
        if step < 6:
            animator.tween(self.progress, 'value',
                           min(1.0, 0.35 + step * 0.1),
                           duration=0.4,
                           on_complete=lambda s=step: self._sim_progress(s + 1))

    # ── Callbacks ──
    def _on_save(self):
        Dialog.alert(self.manager,
            "Saved",
            f"Name: {self.tb_name.text or '(none)'}\nSerial: {self.tb_number.text or '(none)'}",
            on_ok=None)

    def _on_delete(self):
        Dialog.confirm(self.manager,
            "Reset settings?",
            "This will clear all fields.\nThis action cannot be undone.",
            on_confirm=self._do_reset,
            danger=True)

    def _do_reset(self):
        self.tb_name.set_text("")
        self.tb_number.set_text("")
        self.tb_pwd.set_text("")

    def _on_about(self):
        # Morph transition from the tapped button's rect
        page = AboutPage(self.manager)
        self.manager.push(page, transition='morph', source_rect=self.btn_about.rect)

    # ── Page overrides ──
    def handle_event(self, event):
        for w in self.widgets:
            w.handle_event(event)

    def draw(self, surface):
        surface.fill(theme.color_bg)
        # Title
        tf = theme.font('title')
        ts = tf.render("Settings", True, theme.color_text)
        ts.set_alpha(int(self.content_alpha))
        cx, cy = theme.point(400, 70)
        surface.blit(ts, (cx - ts.get_width() // 2, cy - ts.get_height() // 2))

        # Section labels
        small = theme.font('small')
        for txt, dy in [("PROFILE", 105), ("PREFERENCES", 380), ("STATUS", 500)]:
            s = small.render(txt, True, theme.color_text_muted)
            s.set_alpha(int(self.content_alpha))
            px_, py_ = theme.point(60, dy)
            surface.blit(s, (px_, py_))

        # Widgets
        for w in self.widgets:
            w.draw(surface)
        self.progress.draw(surface)


# ───────────────────────────────────────────────────────────────────
# About page — pushed with morph transition
# ───────────────────────────────────────────────────────────────────

class AboutPage(Page):
    def __init__(self, manager):
        super().__init__(manager)
        br = theme.rect(60, 680, 200, 60)
        self.back_btn = Button(br.x, br.y, br.w, br.h,
            bg_color=theme.color_surface,
            pressed_color=theme.color_surface_pressed,
            border_color=theme.color_border, border_width=theme.px(1),
            border_radius=theme.px(theme.radius_md),
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, theme.px(1)),
            on_mouse_up=self._back)
        self.back_btn.add_text("Back", theme.font('label'), color=theme.color_text)

        # Badges row
        self.badges = [
            Label("v2.0", theme.font('small'),
                color=theme.color_primary, bg_color=(230, 244, 255),
                padding=(theme.px(5), theme.px(14)),
                border_radius=theme.px(theme.radius_lg)),
            Label("TOUCH", theme.font('small'),
                color=theme.color_success, bg_color=(220, 252, 231),
                padding=(theme.px(5), theme.px(14)),
                border_radius=theme.px(theme.radius_lg)),
            Label("QWERTY", theme.font('small'),
                color=theme.color_info, bg_color=(238, 242, 255),
                padding=(theme.px(5), theme.px(14)),
                border_radius=theme.px(theme.radius_lg)),
        ]
        # Place badges horizontally
        x = theme.px(60)
        y = theme.px(380)
        for b in self.badges:
            b.rect.x = x
            b.rect.y = y
            x += b.rect.width + theme.px(10)

    def _back(self):
        self.manager.pop(transition='morph')

    def handle_event(self, event):
        self.back_btn.handle_event(event)

    def draw(self, surface):
        surface.fill(theme.color_bg)
        tf = theme.font('title')
        ts = tf.render("About pg_ui", True, theme.color_text)
        cx, cy = theme.point(400, 140)
        surface.blit(ts, (cx - ts.get_width() // 2, cy - ts.get_height() // 2))

        body = theme.font('body')
        lines = [
            "A lightweight Pygame CSS-style UI toolkit.",
            "Touch-first, fully self-contained.",
            "",
            "Theme • Animation • PageManager • Dialog",
            "Virtual Keyboard • Responsive Scaling",
        ]
        y = theme.px(220)
        for ln in lines:
            s = body.render(ln, True, theme.color_text_muted)
            cx2, _ = theme.point(400, 0)
            surface.blit(s, (cx2 - s.get_width() // 2, y))
            y += body.get_linesize()

        for b in self.badges:
            b.draw(surface)
        self.back_btn.draw(surface)


# ───────────────────────────────────────────────────────────────────
# Run
# ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App(initial_page=SettingsPage, size=(800, 800), title="pg_ui v2").run()
