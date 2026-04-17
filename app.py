"""
App — one-line runner for a pg_ui application.

    from pg_ui.app import App
    from pg_ui.page import Page

    class HomePage(Page):
        def draw(self, surface):
            surface.fill((240, 240, 240))

    App(initial_page=HomePage, size=(800, 800)).run()

The App owns the pygame window, clock, event loop, animator tick, and
PageManager lifecycle. The initial_page factory receives the manager as its
only argument (same as Page.__init__).
"""
import pygame
import theme
from animation import animator
from page_manager import PageManager


class App:
    def __init__(self, initial_page, size=(800, 800), base_size=(800, 800),
                 title="pg_ui", bg=None, fps=60,
                 font_path=None, font_path_mono=None,
                 flags=0):
        """
        Args:
            initial_page: a Page subclass (callable taking `manager`).
            size:         actual window size (w, h).
            base_size:    logical design canvas (default 800×800). scale is
                          computed as min(screen/base).
            title:        window title.
            bg:           frame-fill color. Defaults to theme.color_bg.
            fps:          target frame rate.
            font_path:    path to default TTF (None → pygame default).
            font_path_mono: path to monospace TTF (None → pygame default).
            flags:        extra pygame.display.set_mode flags (e.g. FULLSCREEN).
        """
        self._initial_page_cls = initial_page
        self.size = size
        self.base_size = base_size
        self.title = title
        self._bg_override = bg
        self.fps = fps
        self.font_path = font_path
        self.font_path_mono = font_path_mono
        self.flags = flags

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode(self.size, self.flags)
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()

        theme.configure(
            screen_size_=screen.get_size(),
            base_size_=self.base_size,
            font_path_=self.font_path,
            font_path_mono_=self.font_path_mono,
        )
        bg_color = self._bg_override if self._bg_override is not None else theme.color_bg

        manager = PageManager(screen)
        initial = self._initial_page_cls(manager)
        manager.push(initial)

        running = True
        while running:
            dt = clock.tick(self.fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    manager.handle_event(event)

            animator.update(dt)
            manager.update(dt)

            screen.fill(bg_color)
            manager.draw()
            pygame.display.flip()

        pygame.quit()
