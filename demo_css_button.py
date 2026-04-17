import sys
import pygame
from button import Button

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Button Rich Demo Showcase")
    clock = pygame.time.Clock()

    # 准备字体支持
    try:
        font_xl = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 32, bold=True)
        font_l = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 24, bold=True)
        font_m = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 18)
        font_s = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 14)
    except:
        font_xl = pygame.font.Font(None, 42)
        font_l = pygame.font.Font(None, 32)
        font_m = pygame.font.Font(None, 24)
        font_s = pygame.font.Font(None, 18)

    # =========================================================
    # 1. Primary Button (核心主要按钮，带有柔和高斯模糊发光阴影)
    # =========================================================
    btn_primary = Button(
        50, 50, 220, 60,
        bg_color=(24, 144, 255),
        hover_color=(64, 169, 255),
        pressed_color=(9, 88, 217),
        border_radius=12,
        shadow_color=(24, 144, 255, 60), # 蓝色发光阴影
        shadow_blur=8,
        shadow_offset=(0, 6),
        pressed_translate=(0, 3)
    ).add_text("Primary Action", font_l, color=(255, 255, 255))

    # =========================================================
    # 2. Ghost / Outline Button (幽灵边框按钮)
    # =========================================================
    btn_ghost = Button(
        300, 50, 220, 60,
        bg_color=(255, 255, 255, 0),     # 完全透明背景
        hover_color=(24, 144, 255, 20),  # 悬停时稍微有一点底色
        pressed_color=(24, 144, 255, 50),
        border_radius=12,
        border_color=(24, 144, 255),
        border_width=2,
        shadow_color=(0, 0, 0, 0)        # 无阴影
    ).add_text("Outline Button", font_l, color=(24, 144, 255))

    # =========================================================
    # 3. Danger / Error Button (危险操作按钮)
    # =========================================================
    btn_danger = Button(
        550, 50, 220, 60,
        bg_color=(255, 77, 79),
        hover_color=(255, 120, 117),
        pressed_color=(217, 54, 62),
        border_radius=12,
        shadow_color=(255, 77, 79, 60),
        shadow_blur=6
    ).add_text("Delete Account", font_l, color=(255, 255, 255))

    # =========================================================
    # 4. Complex Pro Card (极度复杂的网页级别信息卡片作为按钮)
    # =========================================================
    btn_card = Button(
        50, 150, 350, 140,
        bg_color=(255, 255, 255),
        hover_color=(248, 250, 255),
        pressed_color=(240, 245, 255),
        border_radius=20,
        border_color=(220, 220, 230),
        border_width=1,
        shadow_color=(0, 0, 0, 15),
        shadow_blur=10,
        shadow_offset=(0, 8),
        pressed_translate=(0, 4)
    )
    # 利用链式排版构建多元素：
    (btn_card
        .add_text("PRO PLAN", font_m, color=(100, 100, 255), align='left', valign='top', offset=(25, 20))
        .add_text("$19.99", font_xl, color=(30, 30, 30), align='left', valign='center', offset=(25, 10))
        .add_text("/ month", font_s, color=(150, 150, 150), align='left', valign='center', offset=(130, 15))
        .add_text("Unlimited access\n24/7 Support\nPriority updates", font_s, color=(100, 100, 100), align='right', valign='center', offset=(-25, 10))
    )

    # =========================================================
    # 5. Disabled Button (禁用状态)
    # =========================================================
    btn_disabled = Button(
        450, 150, 220, 60,
        disabled=True,
        bg_color=(255, 255, 255),  # 禁用时会覆盖成 disabled_color
        disabled_color=(240, 240, 240),
        border_radius=8,
        border_color=(200, 200, 200),
        border_width=1
    ).add_text("Not Available", font_l, color=(160, 160, 160))

    # =========================================================
    # 6. Pill / Round Action Button (全圆角胶囊按钮)
    # =========================================================
    btn_pill = Button(
        450, 230, 320, 60,
        bg_color=(50, 50, 50),
        hover_color=(70, 70, 70),
        pressed_color=(30, 30, 30),
        border_radius=30, # 圆角为其高度的一半，形成胶囊型
        shadow_color=(0, 0, 0, 80),
        shadow_blur=12,
        shadow_offset=(0, 10)
    ).add_text("Subscribe to Newsletter", font_l, color=(255, 220, 100))

    buttons = [btn_primary, btn_ghost, btn_danger, btn_card, btn_disabled, btn_pill]

    running = True
    while running:
        screen.fill((240, 242, 245)) # 类似现代网页的背景灰

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 统一分发事件
            for btn in buttons:
                btn.handle_event(event)

        # 统一绘制
        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
