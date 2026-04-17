import pygame

class CSSButton:
    def __init__(self, x, y, width, height, **kwargs):
        """
        HTML/CSS 风格的高级 Pygame 按钮类
        
        支持的 kwargs 样式参数:
        - bg_color: 背景颜色 (R, G, B) 或 (R, G, B, A)
        - hover_color: 鼠标悬停时的颜色
        - pressed_color: 按下时的颜色
        - disabled_color: 禁用时的颜色
        - transition_speed: 颜色过渡速度 (0.01 到 1.0)
        - border_radius: 圆角大小 (px)
        - border_color: 边框颜色
        - border_width: 边框粗细
        - shadow_color: 阴影颜色 (R, G, B, Alpha)
        - shadow_offset: 阴影偏移 (dx, dy)
        - shadow_blur: 阴影模糊层数 (越大越模糊)
        - pressed_translate: 按下时按钮的位移 (dx, dy) 模拟物理按压
        - cursor_hand: 悬停时是否变为小手光标
        - disabled: 是否禁用
        - on_mouse_down: 按下时的回调函数
        - on_mouse_up: 松开时的回调函数
        """
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        
        # 颜色属性
        self.bg_color = kwargs.get('bg_color', (255, 255, 255))
        self.hover_color = kwargs.get('hover_color', (245, 245, 245))
        self.pressed_color = kwargs.get('pressed_color', (230, 230, 230))
        self.disabled_color = kwargs.get('disabled_color', (200, 200, 200))
        
        # 颜色动画过渡
        self.current_color = list(self.bg_color)
        self.transition_speed = kwargs.get('transition_speed', 0.15)
        
        # 边框与圆角
        self.border_radius = kwargs.get('border_radius', 8)
        self.border_color = kwargs.get('border_color', None)
        self.border_width = kwargs.get('border_width', 1)
        
        # 阴影属性 (使用预渲染以保证极高性能)
        self.shadow_color = kwargs.get('shadow_color', (0, 0, 0, 40))
        self.shadow_offset = kwargs.get('shadow_offset', (0, 4))
        self.shadow_blur = kwargs.get('shadow_blur', 4)
        self.shadow_surfaces = []
        self._prerender_shadow()
        
        # 交互反馈
        self.pressed_translate = kwargs.get('pressed_translate', (0, 2))
        self.cursor_hand = kwargs.get('cursor_hand', True)
        self.disabled = kwargs.get('disabled', False)
        
        # 回调与状态
        self.on_mouse_down = kwargs.get('on_mouse_down', None)
        self.on_mouse_up = kwargs.get('on_mouse_up', None)
        self.state = 'normal'
        self._was_hovered = False
        
        # 容器内容 (用于存放多段文本或图层)
        self.elements = []

        # 布局系统内容 (与 elements 二选一，优先 content)
        self._content = None

    def _prerender_shadow(self):
        """预先渲染多层 Alpha 矩形来模拟高斯模糊阴影"""
        if not self.shadow_color: return
        
        color = list(self.shadow_color)
        if len(color) == 3: color.append(100) # 默认 Alpha
        if color[3] == 0: return

        blur_steps = self.shadow_blur
        if blur_steps <= 0:
            surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, surf.get_rect(), border_radius=self.border_radius)
            self.shadow_surfaces.append((surf, 0))
            return
            
        for i in range(blur_steps, 0, -1):
            expansion = i
            alpha = int(color[3] / blur_steps)
            c = (color[0], color[1], color[2], alpha)
            
            surf_w = self.rect.w + expansion * 2
            surf_h = self.rect.h + expansion * 2
            surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            
            draw_rect = pygame.Rect(0, 0, surf_w, surf_h)
            pygame.draw.rect(surf, c, draw_rect, border_radius=self.border_radius + expansion)
            self.shadow_surfaces.append((surf, expansion))

    def add_text(self, text, font, color=(0,0,0), align='center', valign='center', offset=(0,0), antialias=True):
        """
        向按钮添加独立排版的文本层。支持多行 (\n)。
        - align: 水平对齐 ('left', 'center', 'right')
        - valign: 垂直对齐 ('top', 'center', 'bottom')
        - offset: 绝对偏移量 (dx, dy)，相当于 CSS 的 padding/margin 微调
        """
        self.elements.append({
            'type': 'text',
            'text': str(text),
            'font': font,
            'color': color,
            'align': align,
            'valign': valign,
            'offset': offset,
            'antialias': antialias
        })
        return self # 支持链式调用

    def add_image(self, image, size=None, align='center', valign='center', offset=(0,0)):
        """
        向按钮添加独立排版的图片层。
        - image: 可以是文件路径或 pygame.Surface 对象
        - size: (width, height) 缩放大小，None 表示原尺寸
        - align: 水平对齐 ('left', 'center', 'right')
        - valign: 垂直对齐 ('top', 'center', 'bottom')
        - offset: 绝对偏移量 (dx, dy)
        """
        if isinstance(image, str):
            surf = pygame.image.load(image).convert_alpha()
        else:
            surf = image

        if size:
            surf = pygame.transform.smoothscale(surf, size)

        self.elements.append({
            'type': 'image',
            'surface': surf,
            'align': align,
            'valign': valign,
            'offset': offset
        })
        return self # 支持链式调用

    def set_content(self, container):
        """
        使用布局容器来管理按钮内部内容。
        container 可以是 HBox, VBox, Stack 等任何 layout.Container。
        布局会自动限定在按钮的 rect 内，每帧自动重新定位。

        用法:
            btn.set_content(HBox(gap=10, children=[
                Icon('logo.png', size=(32,32)),
                Label("Click Me", font),
            ]))
        """
        self._content = container
        return self

    def _layout_content(self):
        """将内部布局容器对齐到当前按钮 rect"""
        if not self._content:
            return
        c = self._content
        c.rect.x = self.rect.x
        c.rect.y = self.rect.y
        c.rect.width = self.rect.width
        c.rect.height = self.rect.height
        # 保持容器使用按钮的完整尺寸，不自动撑开
        c._auto_width = False
        c._auto_height = False
        c.layout()

    def set_disabled(self, disabled):
        self.disabled = disabled
        if disabled:
            self.state = 'normal'
            self.rect.topleft = self.original_rect.topleft

    def handle_event(self, event):
        if self.disabled:
            if self._was_hovered:
                # 尝试设置光标，如果在没有视频系统的无头环境中可能会失败，这里可以加个 try-except 但不是必须
                try: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                except: pass
                self._was_hovered = False
            return

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEMOTION:
            if self.state != 'pressed':
                self.state = 'hover' if is_hovered else 'normal'

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and is_hovered:
                self.state = 'pressed'
                # 模拟 CSS:active 的 transform: translateY
                self.rect.y = self.original_rect.y + self.pressed_translate[1]
                self.rect.x = self.original_rect.x + self.pressed_translate[0]
                if self.on_mouse_down: self.on_mouse_down()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.state == 'pressed':
                    self.rect.y = self.original_rect.y
                    self.rect.x = self.original_rect.x
                    if is_hovered:
                        self.state = 'hover'
                        if self.on_mouse_up: self.on_mouse_up()
                    else:
                        self.state = 'normal'
        
        # 光标切换 (hover 时变小手)
        if self.cursor_hand:
            if is_hovered and not self._was_hovered:
                try: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                except: pass
                self._was_hovered = True
            elif not is_hovered and self._was_hovered:
                try: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                except: pass
                self._was_hovered = False

    def _lerp_color(self, c1, c2, amount):
        res = []
        for i in range(max(len(c1), len(c2))):
            val1 = c1[i] if i < len(c1) else 255
            val2 = c2[i] if i < len(c2) else 255
            res.append(int(val1 + (val2 - val1) * amount))
        return tuple(res)

    def draw(self, surface):
        # 1. 计算状态颜色并平滑过渡 (Color Transition)
        if self.disabled:
            target_color = self.disabled_color
        elif self.state == 'hover':
            target_color = self.hover_color
        elif self.state == 'pressed':
            target_color = self.pressed_color
        else:
            target_color = self.bg_color

        self.current_color = self._lerp_color(self.current_color, target_color, self.transition_speed)

        # 2. 绘制多层模糊阴影 (Box-shadow)
        if self.shadow_surfaces and not self.disabled:
            # 按下时阴影距离减小，模拟贴近背景的物理效果
            shadow_mult = 0.5 if self.state == 'pressed' else 1.0
            for shadow_surf, expansion in self.shadow_surfaces:
                sx = self.original_rect.x + self.shadow_offset[0] * shadow_mult - expansion
                sy = self.original_rect.y + self.shadow_offset[1] * shadow_mult - expansion
                surface.blit(shadow_surf, (sx, sy))

        # 3. 绘制主按钮体 (Background & Border-radius)
        # 支持绘制带透明度的按钮底色
        if len(self.current_color) == 4 and self.current_color[3] < 255:
            temp_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, self.current_color, temp_surf.get_rect(), border_radius=self.border_radius)
            surface.blit(temp_surf, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.current_color[:3], self.rect, border_radius=self.border_radius)

        # 4. 绘制边框 (Border)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_width, border_radius=self.border_radius)

        # 5. 绘制内容层
        if self._content:
            # 布局系统模式: 用 HBox/VBox/Stack 管理内容
            self._layout_content()
            self._draw_content(surface)
        else:
            # 传统 elements 模式: add_text / add_image
            text_color_mult = 0.5 if self.disabled else 1.0
            for elem in self.elements:
                if elem['type'] == 'text':
                    self._draw_text_element(surface, elem, text_color_mult)
                elif elem['type'] == 'image':
                    self._draw_image_element(surface, elem)

    def _draw_text_element(self, surface, elem, text_color_mult):
        """绘制单个文本元素（支持多行）"""
        lines = elem['text'].split('\n')
        line_height = elem['font'].get_linesize()
        total_height = line_height * len(lines)

        c = elem['color']
        render_color = (int(c[0]*text_color_mult), int(c[1]*text_color_mult), int(c[2]*text_color_mult))

        if elem['valign'] == 'center':
            start_y = self.rect.centery - total_height / 2
        elif elem['valign'] == 'top':
            start_y = self.rect.top
        elif elem['valign'] == 'bottom':
            start_y = self.rect.bottom - total_height

        start_y += elem['offset'][1]

        for i, line in enumerate(lines):
            text_surf = elem['font'].render(line, elem['antialias'], render_color)
            text_rect = text_surf.get_rect()

            if elem['align'] == 'center':
                text_rect.centerx = self.rect.centerx
            elif elem['align'] == 'left':
                text_rect.left = self.rect.left
            elif elem['align'] == 'right':
                text_rect.right = self.rect.right

            text_rect.x += elem['offset'][0]
            text_rect.y = start_y + i * line_height

            surface.blit(text_surf, text_rect)

    def _draw_content(self, surface):
        """递归绘制布局系统内容，支持禁用状态"""
        from layout import Label, Icon, Container

        def draw_node(node):
            if isinstance(node, Label):
                if self.disabled:
                    c = node.color
                    dimmed = (c[0]//2, c[1]//2, c[2]//2)
                    node.draw(surface, color_override=dimmed)
                else:
                    node.draw(surface)
            elif isinstance(node, Icon):
                node.draw(surface, alpha=128 if self.disabled else 255)
            elif isinstance(node, Container):
                for child in node.children:
                    draw_node(child)
            elif hasattr(node, 'draw'):
                node.draw(surface)

        draw_node(self._content)

    def _draw_image_element(self, surface, elem):
        """绘制单个图片元素"""
        img_surf = elem['surface']

        # 禁用时降低图片透明度
        if self.disabled:
            img_surf = img_surf.copy()
            img_surf.set_alpha(128)

        img_rect = img_surf.get_rect()

        # 水平对齐
        if elem['align'] == 'center':
            img_rect.centerx = self.rect.centerx
        elif elem['align'] == 'left':
            img_rect.left = self.rect.left
        elif elem['align'] == 'right':
            img_rect.right = self.rect.right

        # 垂直对齐
        if elem['valign'] == 'center':
            img_rect.centery = self.rect.centery
        elif elem['valign'] == 'top':
            img_rect.top = self.rect.top
        elif elem['valign'] == 'bottom':
            img_rect.bottom = self.rect.bottom

        img_rect.x += elem['offset'][0]
        img_rect.y += elem['offset'][1]

        surface.blit(img_surf, img_rect)
