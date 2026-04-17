"""
实际工作风格 Dashboard Demo — 项目管理面板
800x800 窗口，全部使用 Layout 系统，零 hardcoded 坐标
"""
import sys
import pygame
from button import Button
from layout import HBox, VBox, Stack, Spacer, Text, Icon


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Project Dashboard")
    clock = pygame.time.Clock()

    # --- 字体 ---
    try:
        font_brand = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 20, bold=True)
        font_h1 = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 26, bold=True)
        font_h2 = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 18, bold=True)
        font_body = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 16)
        font_small = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 13)
        font_tiny = pygame.font.SysFont(['microsoftyahei', 'simhei', 'arial'], 11)
    except:
        font_brand = pygame.font.Font(None, 26)
        font_h1 = pygame.font.Font(None, 32)
        font_h2 = pygame.font.Font(None, 22)
        font_body = pygame.font.Font(None, 20)
        font_small = pygame.font.Font(None, 16)
        font_tiny = pygame.font.Font(None, 14)

    # =============================================
    # 颜色常量
    # =============================================
    BG = (246, 248, 252)
    SIDEBAR_BG = (24, 28, 40)
    WHITE = (255, 255, 255)
    GRAY_100 = (240, 242, 248)
    GRAY_300 = (200, 205, 215)
    GRAY_500 = (130, 140, 155)
    GRAY_700 = (60, 65, 80)
    BLUE = (59, 130, 246)
    BLUE_LIGHT = (80, 150, 255)
    BLUE_DARK = (37, 99, 205)
    GREEN = (34, 197, 94)
    ORANGE = (249, 115, 22)
    RED = (239, 68, 68)
    PURPLE = (139, 92, 246)
    SIDEBAR_HOVER = (38, 44, 62)
    SIDEBAR_ACTIVE = (49, 56, 78)

    # =============================================
    # 侧边栏
    # =============================================

    # Logo 区
    logo_label = Text("Dashboard", font_brand, color=(150, 160, 255))

    # 导航按钮工厂
    def make_nav_btn(icon_text, label, active=False):
        btn = Button(0, 0, 180, 42,
            bg_color=SIDEBAR_ACTIVE if active else (0, 0, 0, 0),
            hover_color=SIDEBAR_HOVER,
            pressed_color=SIDEBAR_ACTIVE,
            border_radius=8,
            shadow_color=(0, 0, 0, 0),
            pressed_translate=(0, 0),
        )
        btn.set_content(HBox(gap=12, align='start', valign='center', padding=(0, 14, 0, 14), children=[
            Text(icon_text, font_body, color=BLUE_LIGHT if active else GRAY_500),
            Text(label, font_body, color=WHITE if active else GRAY_500),
        ]))
        return btn

    nav_overview = make_nav_btn(">>", "Overview", active=True)
    nav_projects = make_nav_btn("[]", "Projects")
    nav_tasks = make_nav_btn("//", "Tasks")
    nav_team = make_nav_btn("@@", "Team")
    nav_reports = make_nav_btn("##", "Reports")
    nav_settings = make_nav_btn("**", "Settings")

    sidebar_nav = VBox(gap=4, children=[
        nav_overview, nav_projects, nav_tasks, nav_team, nav_reports,
    ])

    # 用户信息区域
    user_btn = Button(0, 0, 180, 50,
        bg_color=(0, 0, 0, 0),
        hover_color=SIDEBAR_HOVER,
        pressed_color=SIDEBAR_ACTIVE,
        border_radius=8,
        shadow_color=(0, 0, 0, 0),
        pressed_translate=(0, 0),
    )
    user_btn.set_content(HBox(gap=10, align='start', valign='center', padding=(0, 14, 0, 14), children=[
        Text("QS", font_small, color=WHITE),
        VBox(gap=1, children=[
            Text("Qiushi", font_small, color=WHITE),
            Text("Admin", font_tiny, color=GRAY_500),
        ]),
    ]))

    sidebar = VBox(x=0, y=0, width=210, height=800, padding=(24, 15, 20, 15), children=[
        logo_label,
        Spacer(height=28),
        sidebar_nav,
        Spacer(height=280),
        nav_settings,
        Spacer(height=10),
        user_btn,
    ])

    # =============================================
    # 主内容区 — 顶部 Header
    # =============================================

    header_title = Text("Overview", font_h1, color=GRAY_700)
    header_subtitle = Text("Thursday, April 16, 2026", font_small, color=GRAY_500)

    btn_new_project = Button(0, 0, 140, 40,
        bg_color=BLUE, hover_color=BLUE_LIGHT, pressed_color=BLUE_DARK,
        border_radius=8,
        shadow_color=(59, 130, 246, 35), shadow_blur=5, shadow_offset=(0, 3),
        pressed_translate=(0, 1),
    )
    btn_new_project.set_content(HBox(gap=6, align='center', valign='center', children=[
        Text("+", font_h2, color=WHITE),
        Text("New Project", font_small, color=WHITE),
    ]))

    header = HBox(width=560, align='space-between', valign='center', children=[
        VBox(gap=4, children=[header_title, header_subtitle]),
        btn_new_project,
    ])

    # =============================================
    # 统计卡片行
    # =============================================

    def make_stat_card(title, value, change, change_color, accent_color):
        btn = Button(0, 0, 128, 95,
            bg_color=WHITE,
            hover_color=GRAY_100,
            pressed_color=(230, 235, 245),
            border_radius=14,
            border_color=(235, 238, 245),
            border_width=1,
            shadow_color=(0, 0, 0, 8), shadow_blur=6, shadow_offset=(0, 3),
            pressed_translate=(0, 1),
        )
        btn.set_content(VBox(gap=6, align='start', padding=(14, 16, 14, 16), children=[
            Text(title, font_tiny, color=GRAY_500),
            Text(value, font_h1, color=GRAY_700),
            Text(change, font_tiny, color=change_color),
        ]))
        return btn

    stat_projects = make_stat_card("Active Projects", "12", "+2 this week", GREEN, BLUE)
    stat_tasks = make_stat_card("Open Tasks", "48", "5 due today", ORANGE, PURPLE)
    stat_completed = make_stat_card("Completed", "156", "+23 this month", GREEN, GREEN)
    stat_team = make_stat_card("Team Members", "8", "2 online now", BLUE, BLUE)

    stats_row = HBox(gap=14, children=[stat_projects, stat_tasks, stat_completed, stat_team])

    # =============================================
    # 项目列表
    # =============================================

    projects_title = Text("Recent Projects", font_h2, color=GRAY_700)
    btn_view_all = Button(0, 0, 72, 30,
        bg_color=(0, 0, 0, 0), hover_color=(240, 244, 255), pressed_color=(230, 237, 255),
        border_radius=6, shadow_color=(0, 0, 0, 0), pressed_translate=(0, 0),
    )
    btn_view_all.add_text("View All", font_small, color=BLUE)

    projects_header = HBox(width=560, align='space-between', valign='center', children=[
        projects_title, btn_view_all,
    ])

    def make_project_row(name, status, status_color, progress_text, members, deadline):
        btn = Button(0, 0, 560, 58,
            bg_color=WHITE,
            hover_color=(250, 251, 255),
            pressed_color=GRAY_100,
            border_radius=12,
            border_color=(238, 240, 248),
            border_width=1,
            shadow_color=(0, 0, 0, 5), shadow_blur=3, shadow_offset=(0, 2),
            pressed_translate=(0, 1),
        )
        # 状态标签
        status_label = Text(status, font_tiny, color=status_color)

        btn.set_content(HBox(align='space-between', valign='center', padding=(0, 18, 0, 18), children=[
            HBox(gap=14, valign='center', children=[
                VBox(gap=3, children=[
                    Text(name, font_h2, color=GRAY_700),
                    Text(progress_text, font_tiny, color=GRAY_500),
                ]),
            ]),
            HBox(gap=20, valign='center', children=[
                Text(members, font_small, color=GRAY_500),
                Text(deadline, font_small, color=GRAY_500),
                status_label,
            ]),
        ]))
        return btn

    proj_1 = make_project_row(
        "pg_ui Component Library", "Active", GREEN,
        "78% complete  |  18/23 tasks done", "3 members", "Apr 30",
    )
    proj_2 = make_project_row(
        "Backend API v2.0", "In Review", ORANGE,
        "95% complete  |  38/40 tasks done", "5 members", "Apr 20",
    )
    proj_3 = make_project_row(
        "Mobile App Redesign", "Active", GREEN,
        "42% complete  |  21/50 tasks done", "4 members", "May 15",
    )
    proj_4 = make_project_row(
        "Data Pipeline Migration", "Blocked", RED,
        "60% complete  |  12/20 tasks done", "2 members", "Apr 25",
    )

    projects_list = VBox(gap=10, children=[proj_1, proj_2, proj_3, proj_4])

    # =============================================
    # 底部操作栏
    # =============================================

    def make_action_btn(label, color, hover, pressed):
        btn = Button(0, 0, 130, 40,
            bg_color=color, hover_color=hover, pressed_color=pressed,
            border_radius=8,
            shadow_color=(*color[:3], 30), shadow_blur=4, shadow_offset=(0, 3),
            pressed_translate=(0, 1),
        )
        btn.add_text(label, font_small, color=WHITE)
        return btn

    btn_export = make_action_btn("Export Report", (100, 116, 139), (120, 136, 159), (80, 96, 119))
    btn_archive = make_action_btn("Archive Done", PURPLE, (159, 122, 255), (119, 72, 226))

    quick_actions_title = Text("Quick Actions", font_h2, color=GRAY_700)
    actions_row = HBox(gap=12, children=[btn_export, btn_archive])
    actions_section = VBox(gap=10, children=[quick_actions_title, actions_row])

    # =============================================
    # 主内容区组合
    # =============================================

    main_content = VBox(x=235, y=28, gap=22, children=[
        header,
        stats_row,
        projects_header,
        projects_list,
        actions_section,
    ])

    # =============================================
    # 执行布局
    # =============================================
    sidebar.layout()
    main_content.layout()

    all_containers = [sidebar, main_content]

    # =============================================
    # 主循环
    # =============================================
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for c in all_containers:
                c.handle_event(event)

        # 绘制背景
        screen.fill(BG)

        # 侧边栏背景
        sidebar_bg_rect = pygame.Rect(0, 0, 210, 800)
        pygame.draw.rect(screen, SIDEBAR_BG, sidebar_bg_rect)

        # 绘制所有元素
        for c in all_containers:
            c.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
