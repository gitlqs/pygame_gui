import pygame


class Progress:
    """
    CSS 风格的进度条。

    两种模式:
    - 确定进度: value 为 0.0 ~ 1.0，进度条宽度按比例填充
    - 不确定进度 (indeterminate=True): 一段亮条在轨道中循环移动，表达"进行中"

    特性:
    - 胶囊形默认圆角 (height/2)，可自定义
    - 进度变化可选平滑过渡 (animated)
    - 可显示百分比文字 (show_text + font)

    参数:
    - value: 进度 (0.0 ~ 1.0)
    - track_color: 轨道背景色
    - bar_color: 进度条颜色
    - border_radius: 圆角 (None → height//2)
    - border_color / border_width
    - show_text: 是否显示文字
    - font: 文字字体
    - text_color: 文字颜色
    - text_format: 文字格式化字符串，占位符 {percent} {value}，默认 '{percent}%'
    - indeterminate: 不确定模式
    - indeterminate_speed: 不确定动画速度
    - animated: 进度变化是否平滑过渡
    - transition_speed: 平滑过渡速度
    """

    def __init__(self, x, y, width, height, **kwargs):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = max(0.0, min(1.0, kwargs.get('value', 0.0)))
        self._display_value = self.value

        self.track_color = kwargs.get('track_color', (230, 230, 230))
        self.bar_color = kwargs.get('bar_color', (24, 144, 255))
        self.border_radius = kwargs.get('border_radius', height // 2)
        self.border_color = kwargs.get('border_color', None)
        self.border_width = kwargs.get('border_width', 0)

        self.show_text = kwargs.get('show_text', False)
        self.font = kwargs.get('font', None)
        self.text_color = kwargs.get('text_color', (30, 30, 30))
        self.text_format = kwargs.get('text_format', '{percent}%')

        self.indeterminate = kwargs.get('indeterminate', False)
        self.indeterminate_speed = kwargs.get('indeterminate_speed', 0.015)
        self.animated = kwargs.get('animated', True)
        self.transition_speed = kwargs.get('transition_speed', 0.15)

        self._anim_phase = 0.0

    def set_value(self, value):
        self.value = max(0.0, min(1.0, float(value)))

    def set_indeterminate(self, indeterminate):
        self.indeterminate = indeterminate

    def handle_event(self, event):
        pass

    def draw(self, surface):
        # 轨道
        pygame.draw.rect(surface, self.track_color, self.rect, border_radius=self.border_radius)

        if self.indeterminate:
            self._anim_phase = (self._anim_phase + self.indeterminate_speed) % 1.0
            segment_w = max(int(self.rect.width * 0.3), 1)
            # 从 -segment 走到 rect.width
            pos = -segment_w + (self.rect.width + segment_w) * self._anim_phase
            bar_rect = pygame.Rect(self.rect.x + int(pos), self.rect.y, segment_w, self.rect.height)
            clip = bar_rect.clip(self.rect)
            if clip.width > 0:
                # 为了圆角好看，绘制进度条时基于原始 bar_rect 再做 clip
                tmp = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                rel = pygame.Rect(bar_rect.x - self.rect.x, 0, segment_w, self.rect.height)
                pygame.draw.rect(tmp, self.bar_color, rel, border_radius=self.border_radius)
                mask = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=self.border_radius)
                tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                surface.blit(tmp, self.rect.topleft)
        else:
            if self.animated:
                self._display_value += (self.value - self._display_value) * self.transition_speed
            else:
                self._display_value = self.value

            bar_w = int(self.rect.width * self._display_value)
            if bar_w > 0:
                bar = pygame.Rect(self.rect.x, self.rect.y, bar_w, self.rect.height)
                # 使用裁剪 + 圆角绘制，保持轨道圆角一致
                tmp = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(tmp, self.bar_color, pygame.Rect(0, 0, bar_w, self.rect.height),
                                 border_radius=self.border_radius)
                mask = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=self.border_radius)
                tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                surface.blit(tmp, self.rect.topleft)

        # 边框
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect,
                             width=self.border_width, border_radius=self.border_radius)

        # 文字
        if self.show_text and self.font:
            if self.indeterminate:
                text = '...'
            else:
                text = self.text_format.format(percent=int(self.value * 100), value=self.value)
            surf = self.font.render(text, True, self.text_color)
            tx = self.rect.centerx - surf.get_width() // 2
            ty = self.rect.centery - surf.get_height() // 2
            surface.blit(surf, (tx, ty))
