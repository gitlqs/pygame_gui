import unittest
import pygame
from unittest.mock import patch, MagicMock
from css_button import CSSButton

class TestCSSButton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # 初始化一个隐藏的窗口，用于测试中涉及的 surface 操作
        pygame.display.set_mode((100, 100), pygame.HIDDEN)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_initialization(self):
        """测试按钮是否能够以默认及自定义参数正确初始化"""
        btn = CSSButton(10, 20, 100, 50)
        self.assertEqual(btn.rect.x, 10)
        self.assertEqual(btn.rect.y, 20)
        self.assertEqual(btn.rect.width, 100)
        self.assertEqual(btn.rect.height, 50)
        self.assertEqual(btn.state, 'normal')
        self.assertFalse(btn.disabled)
        self.assertEqual(btn.bg_color, (255, 255, 255))
        
        # 测试自定义颜色
        btn2 = CSSButton(0, 0, 50, 50, bg_color=(255, 0, 0), disabled=True)
        self.assertEqual(btn2.bg_color, (255, 0, 0))
        self.assertTrue(btn2.disabled)

    def test_add_text_chaining(self):
        """测试文本添加及链式调用"""
        btn = CSSButton(0, 0, 100, 50)
        font_mock = MagicMock()
        font_mock.get_linesize.return_value = 20
        
        # 测试链式调用
        result = btn.add_text("Line 1", font_mock).add_text("Line 2", font_mock, align='left')
        
        self.assertIs(result, btn) # 确保返回 self
        self.assertEqual(len(btn.elements), 2)
        self.assertEqual(btn.elements[0]['text'], "Line 1")
        self.assertEqual(btn.elements[0]['align'], "center")
        self.assertEqual(btn.elements[1]['text'], "Line 2")
        self.assertEqual(btn.elements[1]['align'], "left")

    @patch('pygame.mouse.get_pos')
    def test_hover_event(self, mock_get_pos):
        """测试鼠标悬浮事件"""
        btn = CSSButton(0, 0, 100, 50)
        
        # 鼠标在外面
        mock_get_pos.return_value = (200, 200)
        event = pygame.event.Event(pygame.MOUSEMOTION)
        btn.handle_event(event)
        self.assertEqual(btn.state, 'normal')
        
        # 鼠标移入
        mock_get_pos.return_value = (50, 25)
        btn.handle_event(event)
        self.assertEqual(btn.state, 'hover')
        
        # 鼠标移出
        mock_get_pos.return_value = (200, 200)
        btn.handle_event(event)
        self.assertEqual(btn.state, 'normal')

    @patch('pygame.mouse.get_pos')
    def test_click_event_callbacks(self, mock_get_pos):
        """测试点击状态的变更与回调函数触发"""
        callback_down_mock = MagicMock()
        callback_up_mock = MagicMock()
        
        btn = CSSButton(10, 10, 100, 50, 
                        on_mouse_down=callback_down_mock,
                        on_mouse_up=callback_up_mock,
                        pressed_translate=(0, 5))
        
        # 将鼠标置于按钮之上
        mock_get_pos.return_value = (50, 30)
        
        # 模拟鼠标按下
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
        btn.handle_event(event_down)
        
        self.assertEqual(btn.state, 'pressed')
        self.assertEqual(btn.rect.y, 15) # 测试 pressed_translate (10 + 5)
        callback_down_mock.assert_called_once()
        callback_up_mock.assert_not_called()
        
        # 模拟鼠标松开
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1)
        btn.handle_event(event_up)
        
        self.assertEqual(btn.state, 'hover') # 仍然在上方，所以恢复到 hover
        self.assertEqual(btn.rect.y, 10) # 坐标恢复
        callback_up_mock.assert_called_once()

    @patch('pygame.mouse.get_pos')
    def test_disabled_state(self, mock_get_pos):
        """测试禁用状态是否阻止事件"""
        callback_down_mock = MagicMock()
        btn = CSSButton(0, 0, 100, 50, on_mouse_down=callback_down_mock, disabled=True)
        
        mock_get_pos.return_value = (50, 25)
        
        # 鼠标移动不会导致悬停
        event_motion = pygame.event.Event(pygame.MOUSEMOTION)
        btn.handle_event(event_motion)
        self.assertEqual(btn.state, 'normal')
        
        # 鼠标点击不会触发回调和按压效果
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
        btn.handle_event(event_down)
        self.assertEqual(btn.state, 'normal')
        callback_down_mock.assert_not_called()

        # 动态解除禁用
        btn.set_disabled(False)
        self.assertFalse(btn.disabled)
        btn.handle_event(event_down)
        self.assertEqual(btn.state, 'pressed')

    def test_lerp_color(self):
        """测试颜色的插值计算方法"""
        btn = CSSButton(0, 0, 10, 10)
        color_a = (0, 0, 0)
        color_b = (100, 200, 255)
        
        result_50 = btn._lerp_color(color_a, color_b, 0.5)
        self.assertEqual(result_50, (50, 100, 127))
        
        result_100 = btn._lerp_color(color_a, color_b, 1.0)
        self.assertEqual(result_100, color_b)

    def test_draw_execution(self):
        """测试绘制方法执行不抛出异常"""
        btn = CSSButton(0, 0, 100, 50)
        font = pygame.font.Font(None, 24)
        btn.add_text("Test", font)
        
        surf = pygame.Surface((200, 200))
        try:
            btn.draw(surf)
            # 切换状态再测
            btn.state = 'pressed'
            btn.draw(surf)
            btn.set_disabled(True)
            btn.draw(surf)
            success = True
        except Exception as e:
            success = False
            self.fail(f"Draw method failed with exception: {e}")
            
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
