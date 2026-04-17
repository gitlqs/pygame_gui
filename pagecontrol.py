import pygame


class PageControl:
    """
    分页指示器 (iOS 风格小圆点)。

    - N 个圆点代表 N 页；当前页放大并变色
    - 点击圆点可跳转
    - 支持水平 / 垂直排列
    - 颜色与尺寸平滑过渡

    参数:
    - count: 页数
    - current: 初始激活页索引 (0-based)
    - dot_size: 未激活圆点直径
    - active_size: 激活圆点直径 (默认 dot_size * 1.5)
    - gap: 圆点间距
    - dot_color: 未激活颜色
    - active_color: 激活颜色
    - hover_color: 悬停颜色
    - orientation: 'horizontal' | 'vertical'
    - transition_speed: 过渡速度
    - cursor_hand: 悬停时是否变手型
    - disabled: 禁用
    - on_change(index): 页面切换回调
    """

    def __init__(self, x, y, count, **kwargs):
        self.count = max(1, int(count))
        self.current = max(0, min(kwargs.get('current', 0), self.count - 1))

        self.dot_size = kwargs.get('dot_size', 8)
        self.active_size = kwargs.get('active_size', int(self.dot_size * 1.5))
        self.gap = kwargs.get('gap', 10)

        self.dot_color = kwargs.get('dot_color', (200, 200, 200))
        self.active_color = kwargs.get('active_color', (24, 144, 255))
        self.hover_color = kwargs.get('hover_color', (150, 150, 150))

        self.orientation = kwargs.get('orientation', 'horizontal')
        self.transition_speed = kwargs.get('transition_speed', 0.2)
        self.cursor_hand = kwargs.get('cursor_hand', True)
        self.disabled = kwargs.get('disabled', False)
        self.on_change = kwargs.get('on_change', None)

        # 动画状态 (每个点独立)
        self._dot_scales = [1.0] * self.count
        self._dot_colors = [list(self.dot_color) for _ in range(self.count)]
        self._dot_scales[self.current] = self.active_size / self.dot_size
        self._dot_colors[self.current] = list(self.active_color)

        self._hover_index = -1
        self._was_hovered = False

        # 总 rect (点击区按 active_size 计算，保证布局稳定)
        step = self.active_size + self.gap
        if self.orientation == 'horizontal':
            w = self.count * self.active_size + (self.count - 1) * self.gap
            h = self.active_size
        else:
            w = self.active_size
            h = self.count * self.active_size + (self.count - 1) * self.gap
        self.rect = pygame.Rect(x, y, w, h)

    def _dot_center(self, i):
        step = self.active_size + self.gap
        if self.orientation == 'horizontal':
            cx = self.rect.x + i * step + self.active_size // 2
            cy = self.rect.centery
        else:
            cx = self.rect.centerx
            cy = self.rect.y + i * step + self.active_size // 2
        return cx, cy

    def _dot_hitbox(self, i):
        cx, cy = self._dot_center(i)
        s = self.active_size
        return pygame.Rect(cx - s // 2, cy - s // 2, s, s)

    def set_current(self, index):
        index = max(0, min(int(index), self.count - 1))
        if self.current != index:
            self.current = index
            if self.on_change:
                self.on_change(index)

    def next(self):
        if self.current < self.count - 1:
            self.set_current(self.current + 1)

    def prev(self):
        if self.current > 0:
            self.set_current(self.current - 1)

    def set_disabled(self, disabled):
        self.disabled = disabled

    def handle_event(self, event):
        # Touch-first: no hover, no cursor switching.
        if self.disabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(self.count):
                if self._dot_hitbox(i).collidepoint(event.pos):
                    self.set_current(i)
                    return

    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def _lerp_color(self, c1, c2, t):
        return [int(self._lerp(a, b, t)) for a, b in zip(c1, c2)]

    def draw(self, surface):
        active_scale = self.active_size / self.dot_size
        for i in range(self.count):
            if i == self.current:
                target_color = self.active_color
                target_scale = active_scale
            else:
                target_color = self.dot_color
                target_scale = 1.0

            self._dot_colors[i] = self._lerp_color(self._dot_colors[i], target_color, self.transition_speed)
            self._dot_scales[i] = self._lerp(self._dot_scales[i], target_scale, self.transition_speed)

            cx, cy = self._dot_center(i)
            radius = max(1, int(self.dot_size * self._dot_scales[i] / 2))
            pygame.draw.circle(surface, self._dot_colors[i], (cx, cy), radius)
