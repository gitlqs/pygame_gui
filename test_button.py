import unittest
import pygame
from unittest.mock import MagicMock
from button import Button


class TestButton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((100, 100), pygame.HIDDEN)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_initialization(self):
        btn = Button(10, 20, 100, 50)
        self.assertEqual(btn.rect.x, 10)
        self.assertEqual(btn.rect.y, 20)
        self.assertEqual(btn.rect.width, 100)
        self.assertEqual(btn.rect.height, 50)
        self.assertEqual(btn.state, 'normal')
        self.assertFalse(btn.disabled)
        self.assertEqual(btn.bg_color, (255, 255, 255))

        btn2 = Button(0, 0, 50, 50, bg_color=(255, 0, 0), disabled=True)
        self.assertEqual(btn2.bg_color, (255, 0, 0))
        self.assertTrue(btn2.disabled)

    def test_add_text_chaining(self):
        btn = Button(0, 0, 100, 50)
        font_mock = MagicMock()
        font_mock.get_linesize.return_value = 20
        result = btn.add_text("Line 1", font_mock).add_text("Line 2", font_mock, align='left')
        self.assertIs(result, btn)
        self.assertEqual(len(btn.elements), 2)
        self.assertEqual(btn.elements[0]['text'], "Line 1")
        self.assertEqual(btn.elements[0]['align'], "center")
        self.assertEqual(btn.elements[1]['text'], "Line 2")
        self.assertEqual(btn.elements[1]['align'], "left")

    def test_no_hover_on_touch(self):
        """Touch-first: MOUSEMOTION does not enter a 'hover' state."""
        btn = Button(0, 0, 100, 50)
        event = pygame.event.Event(pygame.MOUSEMOTION, pos=(50, 25))
        btn.handle_event(event)
        self.assertEqual(btn.state, 'normal')

    def test_click_event_callbacks(self):
        """Press / release fires callbacks; state returns to 'normal' after release."""
        down = MagicMock()
        up = MagicMock()
        btn = Button(10, 10, 100, 50,
                     on_mouse_down=down, on_mouse_up=up,
                     pressed_translate=(0, 5))

        btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 30)))
        self.assertEqual(btn.state, 'pressed')
        self.assertEqual(btn.rect.y, 15)
        down.assert_called_once()
        up.assert_not_called()

        btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(50, 30)))
        self.assertEqual(btn.state, 'normal')
        self.assertEqual(btn.rect.y, 10)
        up.assert_called_once()

    def test_click_release_outside(self):
        """Release outside the button: on_mouse_up must NOT fire (drag-off cancels)."""
        up = MagicMock()
        btn = Button(10, 10, 100, 50, on_mouse_up=up)
        btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 30)))
        btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(500, 500)))
        self.assertEqual(btn.state, 'normal')
        up.assert_not_called()

    def test_disabled_state(self):
        down = MagicMock()
        btn = Button(0, 0, 100, 50, on_mouse_down=down, disabled=True)
        btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 25)))
        self.assertEqual(btn.state, 'normal')
        down.assert_not_called()
        btn.set_disabled(False)
        btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 25)))
        self.assertEqual(btn.state, 'pressed')

    def test_lerp_color(self):
        btn = Button(0, 0, 10, 10)
        self.assertEqual(btn._lerp_color((0, 0, 0), (100, 200, 255), 0.5), (50, 100, 127))
        self.assertEqual(btn._lerp_color((0, 0, 0), (100, 200, 255), 1.0), (100, 200, 255))

    def test_draw_execution(self):
        btn = Button(0, 0, 100, 50)
        font = pygame.font.Font(None, 24)
        btn.add_text("Test", font)
        surf = pygame.Surface((200, 200))
        btn.draw(surf)
        btn.state = 'pressed'
        btn.draw(surf)
        btn.set_disabled(True)
        btn.draw(surf)


if __name__ == '__main__':
    unittest.main()
