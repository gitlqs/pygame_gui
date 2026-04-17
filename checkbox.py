import pygame


class Checkbox:
    """
    CSS 风格的复选框。

    - 点击切换 checked
    - 可带文本标签 (固定显示在右侧)
    - 支持 hover / pressed / disabled 状态
    - 颜色平滑过渡

    参数:
    - checked: 初始状态 (bool)
    - box_size: 复选框边长 (px)
    - box_color: 未选中背景
    - checked_color: 选中背景
    - hover_color: 悬停 (未选中时) 的背景提示色
    - disabled_color: 禁用背景
    - border_color / checked_border_color / border_width / border_radius
    - check_color: 对勾颜色
    - check_width: 对勾线宽
    - label: 文本 (None 则不显示)
    - font, text_color: 标签字体 / 颜色
    - label_gap: box 与 label 间距
    - transition_speed: 颜色 / 尺寸过渡速度
    - on_change(checked): 状态变化回调
    """

    def __init__(self, x, y, **kwargs):
        self.box_size = kwargs.get('box_size', 20)
        self.checked = kwargs.get('checked', False)

        self.box_color = kwargs.get('box_color', (255, 255, 255))
        self.checked_color = kwargs.get('checked_color', (24, 144, 255))
        self.hover_color = kwargs.get('hover_color', (245, 250, 255))
        self.disabled_color = kwargs.get('disabled_color', (230, 230, 230))

        self.border_color = kwargs.get('border_color', (200, 200, 200))
        self.checked_border_color = kwargs.get('checked_border_color', self.checked_color)
        self.border_width = kwargs.get('border_width', 2)
        self.border_radius = kwargs.get('border_radius', 4)

        self.check_color = kwargs.get('check_color', (255, 255, 255))
        self.check_width = kwargs.get('check_width', 2)

        self.label = kwargs.get('label', None)
        self.font = kwargs.get('font', None)
        self.text_color = kwargs.get('text_color', (30, 30, 30))
        self.label_gap = kwargs.get('label_gap', 8)

        self.transition_speed = kwargs.get('transition_speed', 0.2)
        self.cursor_hand = kwargs.get('cursor_hand', True)
        self.disabled = kwargs.get('disabled', False)
        self.on_change = kwargs.get('on_change', None)

        # 计算总 rect (含 label)
        w, h = self.box_size, self.box_size
        if self.label and self.font:
            lbl_w, lbl_h = self.font.size(self.label)
            w += self.label_gap + lbl_w
            h = max(h, lbl_h)
        self.rect = pygame.Rect(x, y, w, h)

        self.state = 'normal'
        self._was_hovered = False
        self._current_bg = list(self.checked_color if self.checked else self.box_color)
        self._check_anim = 1.0 if self.checked else 0.0

    def _box_rect(self):
        bx = self.rect.x
        by = self.rect.centery - self.box_size // 2
        return pygame.Rect(bx, by, self.box_size, self.box_size)

    def set_checked(self, checked):
        if self.checked != bool(checked):
            self.checked = bool(checked)
            if self.on_change:
                self.on_change(self.checked)

    def toggle(self):
        self.set_checked(not self.checked)

    def set_disabled(self, disabled):
        self.disabled = disabled

    def handle_event(self, event):
        # Touch-first: no hover, no cursor switching.
        if self.disabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = 'pressed'
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == 'pressed' and self.rect.collidepoint(event.pos):
                self.toggle()
            self.state = 'normal'

    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def _lerp_color(self, c1, c2, t):
        return [int(self._lerp(a, b, t)) for a, b in zip(c1, c2)]

    def draw(self, surface):
        box = self._box_rect()

        # 目标背景色
        if self.disabled:
            target = self.disabled_color
        elif self.checked:
            target = self.checked_color
        else:
            target = self.box_color
        self._current_bg = self._lerp_color(self._current_bg, target, self.transition_speed)

        pygame.draw.rect(surface, self._current_bg, box, border_radius=self.border_radius)

        # 边框
        bc = self.checked_border_color if (self.checked and not self.disabled) else self.border_color
        if bc and self.border_width > 0:
            pygame.draw.rect(surface, bc, box, width=self.border_width, border_radius=self.border_radius)

        # 对勾动画
        target_anim = 1.0 if self.checked else 0.0
        self._check_anim = self._lerp(self._check_anim, target_anim, self.transition_speed)

        if self._check_anim > 0.05:
            color = self.check_color if not self.disabled else (150, 150, 150)
            # V 形三点 (从左下 -> 中下 -> 右上)
            p1 = (box.x + box.width * 0.22, box.y + box.height * 0.52)
            p2 = (box.x + box.width * 0.44, box.y + box.height * 0.72)
            p3 = (box.x + box.width * 0.78, box.y + box.height * 0.30)

            # 根据动画进度绘制部分对勾
            if self._check_anim >= 0.999:
                pygame.draw.lines(surface, color, False, [p1, p2, p3], self.check_width)
            else:
                t = self._check_anim
                # 第一段 p1→p2 占 0.5, 第二段 p2→p3 占 0.5
                if t <= 0.5:
                    sub = t / 0.5
                    end = (p1[0] + (p2[0] - p1[0]) * sub, p1[1] + (p2[1] - p1[1]) * sub)
                    pygame.draw.lines(surface, color, False, [p1, end], self.check_width)
                else:
                    sub = (t - 0.5) / 0.5
                    end = (p2[0] + (p3[0] - p2[0]) * sub, p2[1] + (p3[1] - p2[1]) * sub)
                    pygame.draw.lines(surface, color, False, [p1, p2, end], self.check_width)

        # 标签
        if self.label and self.font:
            color = self.text_color if not self.disabled else (150, 150, 150)
            surf = self.font.render(self.label, True, color)
            tx = box.right + self.label_gap
            ty = self.rect.centery - surf.get_height() // 2
            surface.blit(surf, (tx, ty))
