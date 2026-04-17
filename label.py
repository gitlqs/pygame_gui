import pygame


class Label:
    """
    CSS 风格的样式化标签 (Badge / Tag / Status)

    与 layout.Text 的区别:
    - layout.Text 是纯文本叶子节点 (无背景、无边框)
    - Label 拥有完整的容器样式 (背景、边框、圆角、padding)，适合做徽章/标签/状态块

    参数:
    - text: 文本内容 (支持 \\n 多行)
    - font: pygame.font.Font
    - color: 文本颜色
    - bg_color: 背景颜色 (默认透明 (0,0,0,0))
    - border_color / border_width / border_radius
    - padding: 内边距 (int / (v,h) / (t,r,b,l))
    - align: 水平对齐 ('left', 'center', 'right')
    - valign: 垂直对齐 ('top', 'center', 'bottom')
    - width / height: 固定尺寸 (0 = 根据文字+padding 自动撑开)
    - x, y: 位置
    """

    def __init__(self, text, font, **kwargs):
        self.text = str(text)
        self.font = font
        self.color = kwargs.get('color', (30, 30, 30))
        self.bg_color = kwargs.get('bg_color', (0, 0, 0, 0))
        self.border_color = kwargs.get('border_color', None)
        self.border_width = kwargs.get('border_width', 1)
        self.border_radius = kwargs.get('border_radius', 0)
        self.padding = self._parse_padding(kwargs.get('padding', 0))
        self.align = kwargs.get('align', 'center')
        self.valign = kwargs.get('valign', 'center')
        self.antialias = kwargs.get('antialias', True)

        x = kwargs.get('x', 0)
        y = kwargs.get('y', 0)
        self._fixed_w = kwargs.get('width', 0)
        self._fixed_h = kwargs.get('height', 0)

        self.rect = pygame.Rect(x, y, 0, 0)
        self._surfaces = []
        self._render()

    @staticmethod
    def _parse_padding(p):
        if isinstance(p, (int, float)):
            return (p, p, p, p)
        if len(p) == 2:
            return (p[0], p[1], p[0], p[1])
        if len(p) == 4:
            return tuple(p)
        return (0, 0, 0, 0)

    def _render(self):
        """预渲染文本并根据 fixed / auto 尺寸计算 rect"""
        lines = self.text.split('\n')
        self._surfaces = [self.font.render(l, self.antialias, self.color) for l in lines]
        line_h = self.font.get_linesize()
        text_w = max((s.get_width() for s in self._surfaces), default=0)
        text_h = line_h * len(lines)

        pos = (self.rect.x, self.rect.y)
        if self._fixed_w > 0:
            w = self._fixed_w
        else:
            w = text_w + self.padding[1] + self.padding[3]
        if self._fixed_h > 0:
            h = self._fixed_h
        else:
            h = text_h + self.padding[0] + self.padding[2]
        self.rect = pygame.Rect(pos[0], pos[1], w, h)

    def set_text(self, text):
        self.text = str(text)
        self._render()

    def set_color(self, color):
        self.color = color
        self._render()

    def set_bg_color(self, color):
        self.bg_color = color

    def handle_event(self, event):
        pass

    def draw(self, surface):
        # 背景 (支持 RGBA)
        if len(self.bg_color) == 4 and self.bg_color[3] < 255:
            if self.bg_color[3] > 0:
                tmp = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(tmp, self.bg_color, tmp.get_rect(), border_radius=self.border_radius)
                surface.blit(tmp, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.bg_color[:3], self.rect, border_radius=self.border_radius)

        # 边框
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect,
                             width=self.border_width, border_radius=self.border_radius)

        # 文本
        line_h = self.font.get_linesize()
        total_h = line_h * len(self._surfaces)
        inner_top = self.rect.top + self.padding[0]
        inner_bottom = self.rect.bottom - self.padding[2]
        inner_left = self.rect.left + self.padding[3]
        inner_right = self.rect.right - self.padding[1]

        if self.valign == 'top':
            y = inner_top
        elif self.valign == 'bottom':
            y = inner_bottom - total_h
        else:
            y = (inner_top + inner_bottom) / 2 - total_h / 2

        for surf in self._surfaces:
            if self.align == 'left':
                x = inner_left
            elif self.align == 'right':
                x = inner_right - surf.get_width()
            else:
                x = (inner_left + inner_right) / 2 - surf.get_width() / 2
            surface.blit(surf, (int(x), int(y)))
            y += line_h
