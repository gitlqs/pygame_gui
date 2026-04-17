"""
轻量级 Flexbox 风格布局系统 for Pygame

核心容器:
- HBox: 水平排列子元素 (flex-direction: row)
- VBox: 垂直排列子元素 (flex-direction: column)
- Stack: 绝对定位叠放子元素 (position: absolute)

任何拥有 rect 属性 (pygame.Rect) 的对象都可以作为子元素 (Sizable 协议)。
也支持嵌套容器实现复杂布局。
"""

import pygame


class Container:
    """
    布局容器基类。

    所有容器都有:
    - rect: 自身的包围盒 (由 layout() 计算或手动设定)
    - padding: 内边距 (top, right, bottom, left) — 可传单值/二元组/四元组
    - children: 子元素列表
    """

    def __init__(self, x=0, y=0, width=0, height=0, padding=0, children=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.padding = self._parse_padding(padding)
        self.children = list(children) if children else []
        # 自动尺寸: width/height 为 0 时由子元素撑开
        self._auto_width = (width == 0)
        self._auto_height = (height == 0)

    @staticmethod
    def _parse_padding(p):
        """将 padding 统一为 (top, right, bottom, left)"""
        if isinstance(p, (int, float)):
            return (p, p, p, p)
        elif len(p) == 2:
            return (p[0], p[1], p[0], p[1])  # (垂直, 水平)
        elif len(p) == 4:
            return tuple(p)
        return (0, 0, 0, 0)

    @property
    def inner_x(self):
        return self.rect.x + self.padding[3]

    @property
    def inner_y(self):
        return self.rect.y + self.padding[0]

    @property
    def inner_width(self):
        return self.rect.width - self.padding[1] - self.padding[3]

    @property
    def inner_height(self):
        return self.rect.height - self.padding[0] - self.padding[2]

    def add(self, *children):
        """添加子元素，支持链式调用"""
        self.children.extend(children)
        return self

    def layout(self):
        """递归计算所有子元素位置。子类必须实现。"""
        raise NotImplementedError

    def draw(self, surface):
        """递归绘制所有子元素。"""
        for child in self.children:
            if hasattr(child, 'draw'):
                child.draw(surface)

    def handle_event(self, event):
        """递归分发事件给所有子元素。"""
        for child in self.children:
            if hasattr(child, 'handle_event'):
                child.handle_event(event)

    def _measure_children(self):
        """递归预计算所有子容器的尺寸（不设置位置，只算 width/height）"""
        for child in self.children:
            if isinstance(child, Container):
                child._measure_children()
                child._compute_size()

    def _compute_size(self):
        """由子类实现: 根据 children 的 rect 计算自身 auto 尺寸"""
        pass

    def _place_children(self):
        """由子类实现: 仅计算子元素位置（尺寸已在 measure pass 中算好）"""
        pass

    def _child_rect(self, child):
        """获取子元素的 rect (兼容各种对象)"""
        if hasattr(child, 'rect'):
            return child.rect
        return pygame.Rect(0, 0, 0, 0)

    def _set_child_pos(self, child, x, y):
        """设置子元素位置，子容器递归定位（不重新 measure）"""
        # 如果是 CSSButton，还需要同步 original_rect
        if hasattr(child, 'original_rect'):
            child.original_rect.x = x
            child.original_rect.y = y
            child.rect.x = x
            child.rect.y = y
        elif hasattr(child, 'rect'):
            child.rect.x = x
            child.rect.y = y
        # 嵌套容器: 尺寸已在 Pass 1 算好，只需递归定位子元素
        if isinstance(child, Container):
            child._place_children()


class HBox(Container):
    """
    水平弹性布局容器 (flex-direction: row)

    参数:
    - gap: 子元素间距 (px)
    - align: 主轴对齐 ('start', 'center', 'end', 'space-between')
    - valign: 交叉轴对齐 ('start', 'center', 'end')
    """

    def __init__(self, gap=0, align='start', valign='start', **kwargs):
        super().__init__(**kwargs)
        self.gap = gap
        self.align = align
        self.valign = valign

    def _compute_size(self):
        """根据子元素计算自身 auto 尺寸"""
        if not self.children:
            return
        rects = [self._child_rect(c) for c in self.children]
        total_children_w = sum(r.width for r in rects)
        total_gap = self.gap * (len(self.children) - 1)
        max_child_h = max(r.height for r in rects)
        if self._auto_width:
            self.rect.width = total_children_w + total_gap + self.padding[1] + self.padding[3]
        if self._auto_height:
            self.rect.height = max_child_h + self.padding[0] + self.padding[2]

    def _place_children(self):
        """Pass 2: 根据已计算好的尺寸，递归分配位置"""
        if not self.children:
            return

        rects = [self._child_rect(c) for c in self.children]
        total_children_w = sum(r.width for r in rects)
        total_gap_w = self.gap * (len(self.children) - 1)

        if self.align == 'start':
            cursor_x = self.inner_x
        elif self.align == 'center':
            cursor_x = self.inner_x + (self.inner_width - total_children_w - total_gap_w) / 2
        elif self.align == 'end':
            cursor_x = self.inner_x + self.inner_width - total_children_w - total_gap_w
        else:
            cursor_x = self.inner_x

        if self.align == 'space-between' and len(self.children) > 1:
            actual_gap = (self.inner_width - total_children_w) / (len(self.children) - 1)
        else:
            actual_gap = self.gap

        for child, r in zip(self.children, rects):
            if self.valign == 'start':
                child_y = self.inner_y
            elif self.valign == 'center':
                child_y = self.inner_y + (self.inner_height - r.height) / 2
            elif self.valign == 'end':
                child_y = self.inner_y + self.inner_height - r.height
            else:
                child_y = self.inner_y

            self._set_child_pos(child, int(cursor_x), int(child_y))
            cursor_x += r.width + actual_gap

    def layout(self):
        """完整布局入口: measure(bottom-up) → place(top-down)"""
        if not self.children:
            return
        self._measure_children()
        self._compute_size()
        self._place_children()


class VBox(Container):
    """
    垂直弹性布局容器 (flex-direction: column)

    参数:
    - gap: 子元素间距 (px)
    - align: 主轴对齐 ('start', 'center', 'end', 'space-between')
    - halign: 交叉轴对齐 ('start', 'center', 'end')
    """

    def __init__(self, gap=0, align='start', halign='start', **kwargs):
        super().__init__(**kwargs)
        self.gap = gap
        self.align = align
        self.halign = halign

    def _compute_size(self):
        """根据子元素计算自身 auto 尺寸"""
        if not self.children:
            return
        rects = [self._child_rect(c) for c in self.children]
        total_children_h = sum(r.height for r in rects)
        total_gap = self.gap * (len(self.children) - 1)
        max_child_w = max(r.width for r in rects)
        if self._auto_width:
            self.rect.width = max_child_w + self.padding[1] + self.padding[3]
        if self._auto_height:
            self.rect.height = total_children_h + total_gap + self.padding[0] + self.padding[2]

    def _place_children(self):
        if not self.children:
            return

        rects = [self._child_rect(c) for c in self.children]
        total_children_h = sum(r.height for r in rects)
        total_gap_h = self.gap * (len(self.children) - 1)

        if self.align == 'start':
            cursor_y = self.inner_y
        elif self.align == 'center':
            cursor_y = self.inner_y + (self.inner_height - total_children_h - total_gap_h) / 2
        elif self.align == 'end':
            cursor_y = self.inner_y + self.inner_height - total_children_h - total_gap_h
        else:
            cursor_y = self.inner_y

        if self.align == 'space-between' and len(self.children) > 1:
            actual_gap = (self.inner_height - total_children_h) / (len(self.children) - 1)
        else:
            actual_gap = self.gap

        for child, r in zip(self.children, rects):
            if self.halign == 'start':
                child_x = self.inner_x
            elif self.halign == 'center':
                child_x = self.inner_x + (self.inner_width - r.width) / 2
            elif self.halign == 'end':
                child_x = self.inner_x + self.inner_width - r.width
            else:
                child_x = self.inner_x

            self._set_child_pos(child, int(child_x), int(cursor_y))
            cursor_y += r.height + actual_gap

    def layout(self):
        if not self.children:
            return
        self._measure_children()
        self._compute_size()
        self._place_children()


class Stack(Container):
    """
    绝对定位叠放容器 (position: absolute)

    子元素根据各自的 stack_align / stack_valign 在容器内定位。
    可以通过 add_aligned(child, align, valign, offset) 设置。
    不设置时默认放在左上角。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._alignments = {}  # child_id -> (align, valign, offset)

    def add_aligned(self, child, align='start', valign='start', offset=(0, 0)):
        """添加子元素并指定对齐方式"""
        self.children.append(child)
        self._alignments[id(child)] = (align, valign, offset)
        return self

    def _compute_size(self):
        if not self.children:
            return
        rects = [self._child_rect(c) for c in self.children]
        if self._auto_width:
            max_w = max(r.width for r in rects) if rects else 0
            self.rect.width = max_w + self.padding[1] + self.padding[3]
        if self._auto_height:
            max_h = max(r.height for r in rects) if rects else 0
            self.rect.height = max_h + self.padding[0] + self.padding[2]

    def _place_children(self):
        if not self.children:
            return
        rects = [self._child_rect(c) for c in self.children]
        for child, r in zip(self.children, rects):
            align_info = self._alignments.get(id(child), ('start', 'start', (0, 0)))
            h_align, v_align, offset = align_info

            if h_align == 'start':
                cx = self.inner_x
            elif h_align == 'center':
                cx = self.inner_x + (self.inner_width - r.width) / 2
            elif h_align == 'end':
                cx = self.inner_x + self.inner_width - r.width
            else:
                cx = self.inner_x

            if v_align == 'start':
                cy = self.inner_y
            elif v_align == 'center':
                cy = self.inner_y + (self.inner_height - r.height) / 2
            elif v_align == 'end':
                cy = self.inner_y + self.inner_height - r.height
            else:
                cy = self.inner_y

            self._set_child_pos(child, int(cx + offset[0]), int(cy + offset[1]))

    def layout(self):
        if not self.children:
            return
        self._measure_children()
        self._compute_size()
        self._place_children()


class Spacer:
    """
    弹性空白占位符。用于在 HBox/VBox 中撑开空间。

    用法:
    HBox(children=[btn_left, Spacer(width=50), btn_right])
    VBox(children=[header, Spacer(height=20), content])
    """

    def __init__(self, width=0, height=0):
        self.rect = pygame.Rect(0, 0, width, height)


class Text:
    """
    文本叶子元素，可参与布局系统。

    用法:
    txt = Text("Hello", font, color=(0,0,0))
    HBox(children=[icon, txt])
    """

    def __init__(self, text, font, color=(0, 0, 0), antialias=True):
        self.text = str(text)
        self.font = font
        self.color = color
        self.antialias = antialias
        self._surfaces = []  # 预渲染的行 surfaces
        self._render()

    def _render(self):
        """预渲染文本为 surfaces，计算 rect"""
        lines = self.text.split('\n')
        self._surfaces = []
        max_w = 0
        total_h = 0
        line_h = self.font.get_linesize()

        for line in lines:
            surf = self.font.render(line, self.antialias, self.color)
            self._surfaces.append(surf)
            max_w = max(max_w, surf.get_width())
            total_h += line_h

        self.rect = pygame.Rect(0, 0, max_w, total_h)

    def set_text(self, text):
        """动态更新文本内容"""
        self.text = str(text)
        old_pos = (self.rect.x, self.rect.y)
        self._render()
        self.rect.x, self.rect.y = old_pos

    def set_color(self, color):
        """动态更新颜色"""
        self.color = color
        old_pos = (self.rect.x, self.rect.y)
        self._render()
        self.rect.x, self.rect.y = old_pos

    def draw(self, surface, color_override=None):
        """绘制文本"""
        line_h = self.font.get_linesize()
        if color_override and color_override != self.color:
            # 需要临时重新渲染
            for i, line in enumerate(self.text.split('\n')):
                surf = self.font.render(line, self.antialias, color_override)
                surface.blit(surf, (self.rect.x, self.rect.y + i * line_h))
        else:
            for i, surf in enumerate(self._surfaces):
                surface.blit(surf, (self.rect.x, self.rect.y + i * line_h))


class Icon:
    """
    图片叶子元素，可参与布局系统。

    用法:
    icon = Icon('logo.png', size=(32, 32))
    HBox(children=[icon, label])

    支持: png, jpg, svg, 或直接传入 pygame.Surface
    """

    def __init__(self, image, size=None):
        if isinstance(image, str):
            self._surface = pygame.image.load(image).convert_alpha()
        else:
            self._surface = image

        if size:
            self._surface = pygame.transform.smoothscale(self._surface, size)

        w, h = self._surface.get_size()
        self.rect = pygame.Rect(0, 0, w, h)

    def draw(self, surface, alpha=255):
        """绘制图片"""
        if alpha < 255:
            tmp = self._surface.copy()
            tmp.set_alpha(alpha)
            surface.blit(tmp, self.rect.topleft)
        else:
            surface.blit(self._surface, self.rect.topleft)
