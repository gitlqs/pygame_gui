import sys
import pygame
from button import Button

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Button Image + Text Demo")
    clock = pygame.time.Clock()

    try:
        font_xl = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 28, bold=True)
        font_l = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 22, bold=True)
        font_m = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 18)
        font_s = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 14)
        font_title = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 13)
    except:
        font_xl = pygame.font.Font(None, 36)
        font_l = pygame.font.Font(None, 28)
        font_m = pygame.font.Font(None, 24)
        font_s = pygame.font.Font(None, 18)
        font_title = pygame.font.Font(None, 16)

    # =========================================================
    # 1. PNG 图标 + 文字按钮 (Pygame Logo)
    # =========================================================
    btn_png = Button(
        50, 80, 280, 70,
        bg_color=(50, 180, 50),
        hover_color=(70, 200, 70),
        pressed_color=(30, 150, 30),
        border_radius=14,
        shadow_color=(50, 180, 50, 50),
        shadow_blur=6,
        shadow_offset=(0, 5),
    )
    (btn_png
        .add_image('demo_pygame_logo.png', size=(50, 14), align='left', offset=(20, 0))
        .add_text("Pygame Powered", font_l, color=(255, 255, 255), align='left', offset=(80, 0))
    )

    # =========================================================
    # 2. SVG 图标 + 文字按钮 (TypeScript Logo)
    # =========================================================
    btn_svg = Button(
        50, 180, 280, 70,
        bg_color=(49, 120, 198),
        hover_color=(70, 140, 220),
        pressed_color=(30, 90, 170),
        border_radius=14,
        shadow_color=(49, 120, 198, 50),
        shadow_blur=6,
        shadow_offset=(0, 5),
    )
    (btn_svg
        .add_image('test_svg.svg', size=(40, 40), align='left', offset=(20, 0))
        .add_text("TypeScript", font_xl, color=(255, 255, 255), align='left', offset=(75, 0))
    )

    # =========================================================
    # 3. JPG 图标 + 文字按钮 (Fire Icon)
    # =========================================================
    btn_jpg = Button(
        50, 280, 280, 70,
        bg_color=(255, 87, 34),
        hover_color=(255, 120, 70),
        pressed_color=(220, 60, 20),
        border_radius=14,
        shadow_color=(255, 87, 34, 50),
        shadow_blur=6,
        shadow_offset=(0, 5),
    )
    (btn_jpg
        .add_image('demo_fire_icon.jpg', size=(40, 40), align='left', offset=(20, 0))
        .add_text("Hot Deals!", font_xl, color=(255, 255, 255), align='left', offset=(75, 0))
    )

    # =========================================================
    # 4. SVG 大图标 + 多行文字卡片 (Python Logo)
    # =========================================================
    btn_card = Button(
        380, 80, 350, 130,
        bg_color=(255, 255, 255),
        hover_color=(248, 250, 255),
        pressed_color=(240, 245, 255),
        border_radius=20,
        border_color=(220, 220, 230),
        border_width=1,
        shadow_color=(0, 0, 0, 15),
        shadow_blur=10,
        shadow_offset=(0, 8),
        pressed_translate=(0, 4),
    )
    (btn_card
        .add_image('demo_python_logo.svg', size=(120, 36), align='left', valign='top', offset=(20, 15))
        .add_text("Official Language", font_s, color=(100, 100, 100), align='left', valign='top', offset=(150, 32))
        .add_text("v3.12", font_xl, color=(55, 118, 171), align='right', valign='top', offset=(-15, 50))
        .add_text("Batteries Included\nCross-platform\nOpen Source", font_s, color=(120, 120, 120), align='left', valign='bottom', offset=(20, -8))
    )

    # =========================================================
    # 5. 纯图标按钮 (Icon-only，类似 Toolbar 按钮)
    # =========================================================
    btn_icon_only = Button(
        380, 240, 60, 60,
        bg_color=(240, 240, 245),
        hover_color=(220, 225, 240),
        pressed_color=(200, 210, 230),
        border_radius=12,
        shadow_color=(0, 0, 0, 20),
        shadow_blur=4,
        shadow_offset=(0, 3),
    )
    btn_icon_only.add_image('test_svg.svg', size=(32, 32))

    btn_icon_only2 = Button(
        455, 240, 60, 60,
        bg_color=(240, 240, 245),
        hover_color=(220, 225, 240),
        pressed_color=(200, 210, 230),
        border_radius=12,
        shadow_color=(0, 0, 0, 20),
        shadow_blur=4,
        shadow_offset=(0, 3),
    )
    btn_icon_only2.add_image('demo_fire_icon.jpg', size=(32, 32))

    btn_icon_only3 = Button(
        530, 240, 60, 60,
        bg_color=(240, 240, 245),
        hover_color=(220, 225, 240),
        pressed_color=(200, 210, 230),
        border_radius=12,
        shadow_color=(0, 0, 0, 20),
        shadow_blur=4,
        shadow_offset=(0, 3),
    )
    btn_icon_only3.add_image('demo_pygame_logo.png', size=(40, 11))

    # =========================================================
    # 6. 图片居中 + 底部文字 (App 图标风格)
    # =========================================================
    btn_app1 = Button(
        380, 330, 90, 100,
        bg_color=(255, 255, 255),
        hover_color=(245, 248, 255),
        pressed_color=(235, 240, 250),
        border_radius=16,
        border_color=(230, 230, 235),
        border_width=1,
        shadow_color=(0, 0, 0, 12),
        shadow_blur=6,
        shadow_offset=(0, 4),
    )
    (btn_app1
        .add_image('test_svg.svg', size=(40, 40), valign='top', offset=(0, 15))
        .add_text("TypeScript", font_s, color=(80, 80, 80), valign='bottom', offset=(0, -12))
    )

    btn_app2 = Button(
        485, 330, 90, 100,
        bg_color=(255, 255, 255),
        hover_color=(245, 248, 255),
        pressed_color=(235, 240, 250),
        border_radius=16,
        border_color=(230, 230, 235),
        border_width=1,
        shadow_color=(0, 0, 0, 12),
        shadow_blur=6,
        shadow_offset=(0, 4),
    )
    (btn_app2
        .add_image('demo_fire_icon.jpg', size=(40, 40), valign='top', offset=(0, 15))
        .add_text("Hot", font_s, color=(80, 80, 80), valign='bottom', offset=(0, -12))
    )

    btn_app3 = Button(
        590, 330, 90, 100,
        bg_color=(255, 255, 255),
        hover_color=(245, 248, 255),
        pressed_color=(235, 240, 250),
        border_radius=16,
        border_color=(230, 230, 235),
        border_width=1,
        shadow_color=(0, 0, 0, 12),
        shadow_blur=6,
        shadow_offset=(0, 4),
    )
    (btn_app3
        .add_image('demo_pygame_logo.png', size=(60, 17), valign='top', offset=(0, 20))
        .add_text("Pygame", font_s, color=(80, 80, 80), valign='bottom', offset=(0, -12))
    )

    # =========================================================
    # 7. 禁用状态的图片按钮
    # =========================================================
    btn_disabled_img = Button(
        50, 380, 280, 70,
        bg_color=(255, 255, 255),
        disabled=True,
        disabled_color=(240, 240, 240),
        border_radius=14,
        border_color=(200, 200, 200),
        border_width=1,
    )
    (btn_disabled_img
        .add_image('demo_python_logo.svg', size=(90, 27), align='left', offset=(15, 0))
        .add_text("Not Available", font_m, color=(160, 160, 160), align='left', offset=(115, 0))
    )

    # =========================================================
    # 8. Ghost 图标按钮 (Outline + 图片 + 文字)
    # =========================================================
    btn_ghost_img = Button(
        50, 480, 280, 70,
        bg_color=(255, 255, 255, 0),
        hover_color=(49, 120, 198, 15),
        pressed_color=(49, 120, 198, 40),
        border_radius=14,
        border_color=(49, 120, 198),
        border_width=2,
        shadow_color=(0, 0, 0, 0),
    )
    (btn_ghost_img
        .add_image('test_svg.svg', size=(36, 36), align='left', offset=(20, 0))
        .add_text("Open Project", font_l, color=(49, 120, 198), align='left', offset=(70, 0))
    )

    # =========================================================
    # 9. 多图片叠加按钮 (头像堆叠风格)
    # =========================================================
    btn_multi_img = Button(
        380, 460, 300, 80,
        bg_color=(255, 255, 255),
        hover_color=(248, 250, 255),
        pressed_color=(240, 245, 255),
        border_radius=16,
        border_color=(220, 220, 230),
        border_width=1,
        shadow_color=(0, 0, 0, 15),
        shadow_blur=8,
        shadow_offset=(0, 5),
    )
    (btn_multi_img
        .add_image('test_svg.svg', size=(36, 36), align='left', offset=(15, 0))
        .add_image('demo_fire_icon.jpg', size=(36, 36), align='left', offset=(45, 0))
        .add_image('demo_pygame_logo.png', size=(50, 14), align='left', offset=(88, 0))
        .add_text("3 Projects", font_l, color=(60, 60, 60), align='right', offset=(-20, -8))
        .add_text("Active now", font_s, color=(100, 200, 100), align='right', offset=(-20, 12))
    )

    buttons = [
        btn_png, btn_svg, btn_jpg, btn_card,
        btn_icon_only, btn_icon_only2, btn_icon_only3,
        btn_app1, btn_app2, btn_app3,
        btn_disabled_img, btn_ghost_img, btn_multi_img,
    ]

    # 区域标签
    labels = [
        ("PNG + Text", font_title, (50, 58)),
        ("SVG + Text", font_title, (50, 158)),
        ("JPG + Text", font_title, (50, 258)),
        ("SVG Card (image + multi-text)", font_title, (380, 58)),
        ("Icon-only Buttons (toolbar style)", font_title, (380, 220)),
        ("App Icon Style (image + label)", font_title, (380, 310)),
        ("Disabled (image dimmed)", font_title, (50, 358)),
        ("Ghost / Outline + Image", font_title, (50, 458)),
        ("Multi-image + Multi-text", font_title, (380, 440)),
    ]

    running = True
    while running:
        screen.fill((240, 242, 245))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons:
                btn.handle_event(event)

        # 绘制区域标签
        for text, font, pos in labels:
            surf = font.render(text, True, (130, 130, 140))
            screen.blit(surf, pos)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
