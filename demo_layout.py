"""
Layout 系统 Demo — 用 HBox / VBox / Stack 替代所有 hardcoded 坐标

左侧: set_content() 新方式 (Icon + Label 由 HBox 自动排列，无 offset)
右侧: add_text/add_image 旧方式 (保留对比)
"""
import sys
import pygame
from css_button import CSSButton
from layout import HBox, VBox, Stack, Spacer, Label, Icon


def main():
    pygame.init()
    screen = pygame.display.set_mode((1050, 750))
    pygame.display.set_caption("Layout System Demo")
    clock = pygame.time.Clock()

    try:
        font_xl = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 28, bold=True)
        font_l = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 22, bold=True)
        font_m = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 18)
        font_s = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 14)
    except:
        font_xl = pygame.font.Font(None, 36)
        font_l = pygame.font.Font(None, 28)
        font_m = pygame.font.Font(None, 24)
        font_s = pygame.font.Font(None, 18)

    # =========================================================
    # 左侧栏: 用 set_content() 新方式构建按钮内容
    # 不需要任何手动 offset！HBox 自动处理间距和对齐
    # =========================================================
    btn_png = CSSButton(0, 0, 280, 65,
        bg_color=(50, 180, 50), hover_color=(70, 200, 70), pressed_color=(30, 150, 30),
        border_radius=14, shadow_color=(50, 180, 50, 50), shadow_blur=6, shadow_offset=(0, 5),
    )
    btn_png.set_content(HBox(gap=12, align='center', valign='center', padding=(0, 20, 0, 20), children=[
        Icon('demo_pygame_logo.png', size=(50, 14)),
        Label("Pygame Powered", font_l, color=(255, 255, 255)),
    ]))

    btn_svg = CSSButton(0, 0, 280, 65,
        bg_color=(49, 120, 198), hover_color=(70, 140, 220), pressed_color=(30, 90, 170),
        border_radius=14, shadow_color=(49, 120, 198, 50), shadow_blur=6, shadow_offset=(0, 5),
    )
    btn_svg.set_content(HBox(gap=14, align='center', valign='center', padding=(0, 20, 0, 20), children=[
        Icon('test_svg.svg', size=(40, 40)),
        Label("TypeScript", font_xl, color=(255, 255, 255)),
    ]))

    btn_jpg = CSSButton(0, 0, 280, 65,
        bg_color=(255, 87, 34), hover_color=(255, 120, 70), pressed_color=(220, 60, 20),
        border_radius=14, shadow_color=(255, 87, 34, 50), shadow_blur=6, shadow_offset=(0, 5),
    )
    btn_jpg.set_content(HBox(gap=14, align='center', valign='center', padding=(0, 20, 0, 20), children=[
        Icon('demo_fire_icon.jpg', size=(40, 40)),
        Label("Hot Deals!", font_xl, color=(255, 255, 255)),
    ]))

    btn_disabled = CSSButton(0, 0, 280, 65,
        bg_color=(255, 255, 255), disabled=True, disabled_color=(240, 240, 240),
        border_radius=14, border_color=(200, 200, 200), border_width=1,
    )
    btn_disabled.set_content(HBox(gap=10, align='center', valign='center', padding=(0, 15, 0, 15), children=[
        Icon('demo_python_logo.svg', size=(90, 27)),
        Label("Not Available", font_m, color=(160, 160, 160)),
    ]))

    btn_ghost = CSSButton(0, 0, 280, 65,
        bg_color=(255, 255, 255, 0), hover_color=(49, 120, 198, 15), pressed_color=(49, 120, 198, 40),
        border_radius=14, border_color=(49, 120, 198), border_width=2, shadow_color=(0, 0, 0, 0),
    )
    btn_ghost.set_content(HBox(gap=12, align='center', valign='center', padding=(0, 20, 0, 20), children=[
        Icon('test_svg.svg', size=(36, 36)),
        Label("Open Project", font_l, color=(49, 120, 198)),
    ]))

    sidebar = VBox(x=40, y=40, gap=18, children=[
        btn_png, btn_svg, btn_jpg, btn_disabled, btn_ghost,
    ])

    # =========================================================
    # 右上: HBox 水平排列三个 icon-only 工具栏按钮
    # =========================================================
    def make_icon_btn(image_path, size):
        btn = CSSButton(0, 0, 60, 60,
            bg_color=(240, 240, 245), hover_color=(220, 225, 240), pressed_color=(200, 210, 230),
            border_radius=12, shadow_color=(0, 0, 0, 20), shadow_blur=4, shadow_offset=(0, 3),
        )
        btn.add_image(image_path, size=size)
        return btn

    toolbar = HBox(x=380, y=40, gap=12, valign='center', children=[
        make_icon_btn('test_svg.svg', (32, 32)),
        make_icon_btn('demo_fire_icon.jpg', (32, 32)),
        make_icon_btn('demo_pygame_logo.png', (40, 11)),
    ])

    # =========================================================
    # 右中: HBox 水平排列三个 App 图标风格按钮
    # =========================================================
    def make_app_btn(image_path, img_size, label):
        btn = CSSButton(0, 0, 90, 100,
            bg_color=(255, 255, 255), hover_color=(245, 248, 255), pressed_color=(235, 240, 250),
            border_radius=16, border_color=(230, 230, 235), border_width=1,
            shadow_color=(0, 0, 0, 12), shadow_blur=6, shadow_offset=(0, 4),
        )
        btn.add_image(image_path, size=img_size, valign='top', offset=(0, 15))
        btn.add_text(label, font_s, color=(80, 80, 80), valign='bottom', offset=(0, -12))
        return btn

    app_icons = HBox(x=380, y=130, gap=16, valign='center', children=[
        make_app_btn('test_svg.svg', (40, 40), "TypeScript"),
        make_app_btn('demo_fire_icon.jpg', (40, 40), "Hot"),
        make_app_btn('demo_pygame_logo.png', (60, 17), "Pygame"),
    ])

    # =========================================================
    # 右下: 多图叠加按钮
    # =========================================================
    btn_multi = CSSButton(0, 0, 300, 80,
        bg_color=(255, 255, 255), hover_color=(248, 250, 255), pressed_color=(240, 245, 255),
        border_radius=16, border_color=(220, 220, 230), border_width=1,
        shadow_color=(0, 0, 0, 15), shadow_blur=8, shadow_offset=(0, 5),
    )
    (btn_multi
        .add_image('test_svg.svg', size=(36, 36), align='left', offset=(15, 0))
        .add_image('demo_fire_icon.jpg', size=(36, 36), align='left', offset=(45, 0))
        .add_image('demo_pygame_logo.png', size=(50, 14), align='left', offset=(88, 0))
        .add_text("3 Projects", font_l, color=(60, 60, 60), align='right', offset=(-20, -8))
        .add_text("Active now", font_s, color=(100, 200, 100), align='right', offset=(-20, 12))
    )

    # =========================================================
    # 右下方: set_content + 嵌套布局的 Card 按钮
    # HBox 里嵌套 VBox，实现复杂卡片内容
    # =========================================================
    btn_card = CSSButton(0, 0, 300, 100,
        bg_color=(255, 255, 255), hover_color=(248, 250, 255), pressed_color=(240, 245, 255),
        border_radius=18, border_color=(220, 220, 230), border_width=1,
        shadow_color=(0, 0, 0, 15), shadow_blur=8, shadow_offset=(0, 5),
    )
    btn_card.set_content(HBox(gap=15, align='start', valign='center', padding=(0, 20, 0, 20), children=[
        Icon('demo_python_logo.svg', size=(80, 24)),
        VBox(gap=4, children=[
            Label("Python 3.12", font_l, color=(55, 118, 171)),
            Label("Batteries Included", font_s, color=(120, 120, 120)),
        ]),
    ]))

    # =========================================================
    # 底部: HBox + space-between 演示
    # =========================================================
    btn_cancel = CSSButton(0, 0, 140, 50,
        bg_color=(240, 240, 240), hover_color=(230, 230, 230), pressed_color=(220, 220, 220),
        border_radius=10, border_color=(200, 200, 200), border_width=1, shadow_color=(0,0,0,0),
    )
    btn_cancel.add_text("Cancel", font_m, color=(80, 80, 80))

    btn_save = CSSButton(0, 0, 140, 50,
        bg_color=(24, 144, 255), hover_color=(64, 169, 255), pressed_color=(9, 88, 217),
        border_radius=10, shadow_color=(24, 144, 255, 40), shadow_blur=4, shadow_offset=(0, 3),
    )
    btn_save.add_text("Save", font_m, color=(255, 255, 255))

    btn_delete = CSSButton(0, 0, 140, 50,
        bg_color=(255, 77, 79), hover_color=(255, 120, 117), pressed_color=(217, 54, 62),
        border_radius=10, shadow_color=(255, 77, 79, 40), shadow_blur=4, shadow_offset=(0, 3),
    )
    btn_delete.add_text("Delete", font_m, color=(255, 255, 255))

    footer_bar = HBox(
        x=40, y=580, width=700, height=70,
        gap=0, align='space-between', valign='center',
        padding=(10, 20, 10, 20),
        children=[btn_cancel, btn_save, btn_delete],
    )

    # =========================================================
    # 右侧面板: VBox 嵌套, 把 toolbar + app_icons + multi 竖向排列
    # =========================================================
    right_panel = VBox(x=380, y=40, gap=25, children=[
        toolbar,
        app_icons,
        btn_multi,
        btn_card,
    ])

    # =========================================================
    # 全局根布局: HBox 包裹 sidebar + right_panel
    # =========================================================
    root = HBox(x=40, y=40, gap=50, children=[
        sidebar,
        right_panel,
    ])

    # 执行布局计算 — 一次 layout() 递归搞定所有坐标
    root.layout()
    footer_bar.layout()

    # 收集所有需要绘制/交互的容器
    all_containers = [root, footer_bar]

    # 用于绘制区域标签
    label_font = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 12)

    running = True
    while running:
        screen.fill((240, 242, 245))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for container in all_containers:
                container.handle_event(event)

        # 绘制区域标示 (可视化容器边界，方便调试)
        for container in all_containers:
            pygame.draw.rect(screen, (210, 215, 220), container.rect, 1, border_radius=4)

        for container in all_containers:
            container.draw(screen)

        # 标签
        labels = [
            (f"root: HBox (sidebar + right_panel)", (root.rect.x, root.rect.y - 16)),
            (f"footer: HBox space-between", (footer_bar.rect.x, footer_bar.rect.y - 16)),
        ]
        for text, pos in labels:
            surf = label_font.render(text, True, (150, 150, 160))
            screen.blit(surf, pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
