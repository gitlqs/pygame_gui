# pg_ui — Pygame CSS-Style UI Toolkit

一套轻量的 Pygame UI 组件库，零外部依赖（仅需 `pygame`）。

**组件：**
- **CSSButton** — HTML/CSS 风格按钮（阴影、圆角、过渡）
- **CSSLabel** — 样式化文本标签/徽章
- **CSSTextBox** — 文本输入框（单行 / 多行 / 密码）
- **CSSCheckbox** — 复选框
- **CSSProgress** — 进度条（确定 / 不确定）
- **CSSPageControl** — 分页指示小圆点
- **Layout** — Flexbox 风格布局系统（HBox / VBox / Stack）

---

## 目录

- [快速开始](#快速开始)
- [CSSButton](#cssbutton)
  - [基础按钮](#1-基础按钮)
  - [颜色与状态](#2-颜色与状态)
  - [圆角](#3-圆角-border-radius)
  - [边框](#4-边框-border)
  - [阴影](#5-阴影-box-shadow)
  - [按压位移](#6-按压位移-pressed-translate)
  - [颜色过渡动画](#7-颜色过渡动画-transition)
  - [光标切换](#8-光标切换-cursor)
  - [禁用状态](#9-禁用状态-disabled)
  - [事件回调](#10-事件回调-callbacks)
  - [文本内容](#11-文本内容-add_text)
  - [图片内容](#12-图片内容-add_image)
  - [链式调用](#13-链式调用)
  - [布局系统内容](#14-布局系统内容-set_content)
- [CSSLabel](#csslabel)
- [CSSTextBox](#csstextbox)
- [CSSCheckbox](#csscheckbox)
- [CSSProgress](#cssprogress)
- [CSSPageControl](#csspagecontrol)
- [Layout 布局系统](#layout-布局系统)
  - [HBox 水平布局](#hbox-水平布局)
  - [VBox 垂直布局](#vbox-垂直布局)
  - [Stack 叠放布局](#stack-叠放布局)
  - [Spacer 空白占位](#spacer-空白占位)
  - [Label 文本元素](#label-文本元素)
  - [Icon 图片元素](#icon-图片元素)
  - [嵌套布局](#嵌套布局)
  - [页面级布局](#页面级布局)
- [完整示例](#完整示例)
- [文件结构](#文件结构)

---

## 快速开始

```python
import pygame
from css_button import CSSButton

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 20)

btn = CSSButton(100, 100, 200, 60,
    bg_color=(24, 144, 255),
    hover_color=(64, 169, 255),
    pressed_color=(9, 88, 217),
    border_radius=12,
    on_mouse_up=lambda: print("Clicked!")
)
btn.add_text("Click Me", font, color=(255, 255, 255))

running = True
while running:
    screen.fill((240, 242, 245))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        btn.handle_event(event)
    btn.draw(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
```

---

## CSSButton

```python
from css_button import CSSButton
```

### 1. 基础按钮

最简形式，只需位置和尺寸：

```python
btn = CSSButton(x=50, y=50, width=200, height=60)
```

默认白色背景、8px 圆角、灰色阴影。

### 2. 颜色与状态

按钮有四种颜色状态，支持 RGB 和 RGBA：

```python
btn = CSSButton(50, 50, 200, 60,
    bg_color=(24, 144, 255),         # 默认蓝色
    hover_color=(64, 169, 255),      # 悬停时变亮
    pressed_color=(9, 88, 217),      # 按下时变深
    disabled_color=(200, 200, 200),  # 禁用时灰色
)
```

**透明背景（Ghost 按钮）：**

```python
btn_ghost = CSSButton(50, 50, 200, 60,
    bg_color=(255, 255, 255, 0),       # 完全透明
    hover_color=(24, 144, 255, 20),    # 悬停微微有色
    pressed_color=(24, 144, 255, 50),  # 按下更明显
)
```

### 3. 圆角 (border-radius)

```python
# 小圆角
btn_subtle = CSSButton(50, 50, 200, 60, border_radius=4)

# 大圆角
btn_round = CSSButton(50, 50, 200, 60, border_radius=20)

# 胶囊型 (圆角 = 高度的一半)
btn_pill = CSSButton(50, 50, 200, 60, border_radius=30)
```

### 4. 边框 (border)

```python
# Outline / Ghost 风格
btn = CSSButton(50, 50, 200, 60,
    bg_color=(255, 255, 255, 0),
    border_color=(24, 144, 255),  # 蓝色边框
    border_width=2,               # 2px 粗细
    border_radius=12,
    shadow_color=(0, 0, 0, 0),   # 去掉阴影
)
```

### 5. 阴影 (box-shadow)

使用多层预渲染 Alpha 矩形模拟高斯模糊阴影，性能极高：

```python
# 柔和投影
btn = CSSButton(50, 50, 200, 60,
    shadow_color=(0, 0, 0, 40),   # (R, G, B, Alpha), Alpha 控制浓度
    shadow_offset=(0, 4),          # (dx, dy) 偏移方向
    shadow_blur=4,                 # 模糊层数，越大越散
)

# 彩色发光阴影 (品牌色)
btn_glow = CSSButton(50, 50, 200, 60,
    bg_color=(24, 144, 255),
    shadow_color=(24, 144, 255, 60),  # 蓝色发光
    shadow_blur=8,
    shadow_offset=(0, 6),
)

# 无阴影
btn_flat = CSSButton(50, 50, 200, 60,
    shadow_color=(0, 0, 0, 0),
)
```

> 按下时阴影自动减半偏移，模拟物理上"贴近表面"的效果。

### 6. 按压位移 (pressed-translate)

模拟 CSS `:active { transform: translateY(2px) }` 的物理按压感：

```python
# 默认轻微下沉
btn = CSSButton(50, 50, 200, 60,
    pressed_translate=(0, 2),   # 按下时向下移 2px
)

# 更强的物理感
btn_deep = CSSButton(50, 50, 200, 60,
    pressed_translate=(0, 5),   # 按下时向下移 5px
    shadow_offset=(0, 10),      # 配合更远的阴影效果更好
)

# 无位移
btn_flat = CSSButton(50, 50, 200, 60,
    pressed_translate=(0, 0),
)
```

### 7. 颜色过渡动画 (transition)

状态切换时颜色不会突变，而是平滑过渡：

```python
# 慢速柔和过渡
btn = CSSButton(50, 50, 200, 60,
    transition_speed=0.05,   # 值越小越慢 (0.01 ~ 1.0)
)

# 快速响应过渡
btn_fast = CSSButton(50, 50, 200, 60,
    transition_speed=0.3,
)

# 瞬间切换（无动画）
btn_instant = CSSButton(50, 50, 200, 60,
    transition_speed=1.0,
)
```

> 内部使用 `_lerp_color()` 线性插值，每帧自动计算。

### 8. 光标切换 (cursor)

默认悬停时自动切换为手型光标：

```python
# 默认开启
btn = CSSButton(50, 50, 200, 60, cursor_hand=True)

# 关闭光标切换
btn = CSSButton(50, 50, 200, 60, cursor_hand=False)
```

### 9. 禁用状态 (disabled)

禁用后不响应事件，颜色变灰，文字/图片自动变淡：

```python
# 初始化时禁用
btn = CSSButton(50, 50, 200, 60, disabled=True)

# 动态切换
btn.set_disabled(True)   # 禁用
btn.set_disabled(False)  # 启用
```

禁用时的视觉效果（自动处理）：
- 背景色切换为 `disabled_color`
- 文本颜色减半
- 图片透明度降至 50%
- 阴影不绘制
- 不触发回调、不切换光标

### 10. 事件回调 (callbacks)

```python
def on_press():
    print("Button pressed down!")

def on_release():
    print("Button released (clicked)!")

btn = CSSButton(50, 50, 200, 60,
    on_mouse_down=on_press,   # 鼠标按下时触发
    on_mouse_up=on_release,   # 鼠标松开时触发（仅在按钮上松开）
)
```

> `on_mouse_up` 仅在鼠标按下 **且** 松开时仍在按钮上才触发，等价于 "click" 事件。

**事件分发：** 在主循环中传递事件：

```python
for event in pygame.event.get():
    btn.handle_event(event)
```

### 11. 文本内容 (add_text)

向按钮添加文本层，支持多行、多对齐方式：

```python
font_l = pygame.font.SysFont('arial', 22, bold=True)
font_s = pygame.font.SysFont('arial', 14)

# 居中单行文本
btn.add_text("Click Me", font_l, color=(255, 255, 255))

# 左对齐 + 偏移
btn.add_text("Title", font_l, color=(0, 0, 0),
    align='left',      # 'left', 'center', 'right'
    valign='top',       # 'top', 'center', 'bottom'
    offset=(20, 10),    # (dx, dy) 微调位置
)

# 多行文本
btn.add_text("Line 1\nLine 2\nLine 3", font_s, color=(100, 100, 100))
```

**可同时添加多段文本实现复杂排版：**

```python
btn_card = CSSButton(50, 50, 350, 120, border_radius=16)
btn_card.add_text("PRO PLAN", font_s, color=(100, 100, 255),
    align='left', valign='top', offset=(20, 15))
btn_card.add_text("$19.99", font_xl, color=(30, 30, 30),
    align='left', valign='center', offset=(20, 5))
btn_card.add_text("/ month", font_s, color=(150, 150, 150),
    align='left', valign='center', offset=(130, 10))
```

### 12. 图片内容 (add_image)

向按钮添加图片层，支持 PNG、JPG、SVG 和 `pygame.Surface`：

```python
# 从文件加载，缩放到指定尺寸
btn.add_image('logo.png', size=(32, 32))

# 指定对齐和偏移
btn.add_image('icon.svg', size=(40, 40),
    align='left',       # 'left', 'center', 'right'
    valign='center',    # 'top', 'center', 'bottom'
    offset=(15, 0),     # (dx, dy)
)

# 直接传入 Surface
my_surface = pygame.image.load('photo.jpg')
btn.add_image(my_surface, size=(60, 60))

# 原始尺寸（不缩放）
btn.add_image('large_banner.png')  # size=None 时保持原尺寸
```

**图标 + 文字组合（手动 offset 方式）：**

```python
btn = CSSButton(0, 0, 280, 65, bg_color=(49, 120, 198), border_radius=14)
btn.add_image('ts_logo.svg', size=(40, 40), align='left', offset=(20, 0))
btn.add_text("TypeScript", font_xl, color=(255, 255, 255), align='left', offset=(75, 0))
```

### 13. 链式调用

`add_text()`、`add_image()`、`set_content()` 都返回 `self`，支持链式写法：

```python
btn = (CSSButton(50, 50, 300, 80, bg_color=(255, 255, 255), border_radius=16)
    .add_image('avatar1.png', size=(36, 36), align='left', offset=(15, 0))
    .add_image('avatar2.png', size=(36, 36), align='left', offset=(45, 0))
    .add_text("2 Members", font_l, color=(60, 60, 60), align='right', offset=(-20, 0))
)
```

### 14. 布局系统内容 (set_content)

用 `HBox` / `VBox` / `Stack` 管理按钮内部内容，**不需要手动计算 offset**：

```python
from layout import HBox, VBox, Icon, Label

# 图标 + 文字，自动水平居中对齐
btn = CSSButton(0, 0, 280, 65, bg_color=(50, 180, 50), border_radius=14)
btn.set_content(HBox(gap=12, align='center', valign='center', padding=(0, 20, 0, 20), children=[
    Icon('logo.png', size=(32, 32)),
    Label("Download", font_l, color=(255, 255, 255)),
]))
```

**嵌套布局实现复杂卡片：**

```python
btn_card = CSSButton(0, 0, 300, 100, bg_color=(255, 255, 255), border_radius=18)
btn_card.set_content(HBox(gap=15, align='start', valign='center', padding=(0, 20, 0, 20), children=[
    Icon('python.svg', size=(80, 24)),
    VBox(gap=4, children=[
        Label("Python 3.12", font_l, color=(55, 118, 171)),
        Label("Batteries Included", font_s, color=(120, 120, 120)),
    ]),
]))
```

> `set_content()` 和 `add_text()`/`add_image()` 二选一。设置了 `set_content()` 后，旧的 `elements` 不再绘制。

---

## CSSLabel

```python
from css_label import CSSLabel
```

带背景、边框、padding 的样式化文本标签，适合做徽章 / 标签 / 状态提示。
与 `layout.Label`（纯文本叶子）的区别：`CSSLabel` 有完整容器样式，自动根据文本+padding 撑开。

```python
# 彩色徽章
info = CSSLabel("INFO", font_s,
    color=(24, 144, 255),
    bg_color=(230, 244, 255),
    padding=(4, 10),
    border_radius=10,
)

# 描边风格
tag = CSSLabel("Beta", font_s,
    color=(90, 90, 100),
    bg_color=(255, 255, 255),
    border_color=(200, 200, 210),
    border_width=1,
    padding=(4, 10),
    border_radius=6,
)
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text`, `font` | str / Font | — | 必填 |
| `color` | tuple | `(30,30,30)` | 文本颜色 |
| `bg_color` | tuple | `(0,0,0,0)` | 背景 (支持 RGBA) |
| `border_color` | tuple | `None` | 边框颜色 |
| `border_width` | int | 1 | 边框粗细 |
| `border_radius` | int | 0 | 圆角 |
| `padding` | int/tuple | 0 | 同布局 padding 格式 |
| `align` / `valign` | str | `'center'` | 文本对齐 |
| `width` / `height` | int | 0 | 0 = 自动撑开 |

**动态更新：**

```python
status = CSSLabel("OK", font_s, color=(22,163,74), bg_color=(220,252,231),
    padding=(4,10), border_radius=10)
status.set_text("FAILED")
status.set_color((220, 38, 38))
status.set_bg_color((254, 226, 226))
```

---

## CSSTextBox

```python
from css_textbox import CSSTextBox
```

功能完整的文本输入框，支持 **单行 / 多行 / 密码** 三种模式。

### 基础单行输入

```python
tb = CSSTextBox(50, 50, 300, 36, font,
    placeholder='Enter your name...',
    border_radius=8,
    on_change=lambda txt: print(f"changed: {txt}"),
    on_submit=lambda txt: print(f"submitted: {txt}"),  # Enter 触发
)
```

### 密码框

```python
tb_pwd = CSSTextBox(50, 100, 300, 36, font,
    mode='password',
    placeholder='Password',
    mask_char='•',     # 默认就是 •
    max_length=20,
)
```

### 多行文本

```python
tb_multi = CSSTextBox(50, 160, 500, 120, font,
    mode='multi',
    placeholder='Write a note...\nPress Enter for new line.',
)
```
多行模式下 Enter 换行，Ctrl+Enter 触发 `on_submit`。

### 支持的按键

| 按键 | 行为 |
|------|------|
| 方向键 ←/→ | 移动光标 |
| 方向键 ↑/↓ | 上下行（仅多行模式） |
| Home / End | 行首 / 行尾 |
| Backspace / Delete | 删除字符 |
| Enter | 单行/密码 → 提交；多行 → 换行 |
| Ctrl+Enter | 多行模式下提交 |

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mode` | `'single'` | `'single'` / `'multi'` / `'password'` |
| `text` | `''` | 初始文本 |
| `placeholder` | `''` | 占位符 |
| `mask_char` | `'•'` | 密码模式替代字符 |
| `max_length` | 0 | 最大字符数 (0 = 无限制) |
| `read_only` | False | 只读 |
| `disabled` | False | 禁用 |
| `bg_color` / `focus_bg_color` / `disabled_bg_color` | — | 三态背景 |
| `text_color` / `placeholder_color` / `caret_color` | — | 文本/占位/光标色 |
| `border_color` / `focus_border_color` | — | 焦点自动切换边框色 |
| `border_width` / `border_radius` | 1 / 6 | |
| `padding` | `(6, 10)` | 内边距 |
| `on_change(text)` | None | 文本变化回调 |
| `on_submit(text)` | None | 提交回调 |

### 方法

```python
tb.set_text("Hello")
tb.set_focus(True)        # 程序触发聚焦
tb.set_disabled(True)     # 动态禁用
```

> 文本超出宽度时自动滚动（单行横向 / 多行纵向）。

---

## CSSCheckbox

```python
from css_checkbox import CSSCheckbox
```

带文本标签的复选框，支持 hover / disabled / 颜色过渡。

```python
cb = CSSCheckbox(50, 50,
    checked=False,
    label='Accept terms and conditions',
    font=font,
    on_change=lambda checked: print(f"checked={checked}"),
)

# 自定义颜色
cb_green = CSSCheckbox(50, 100,
    label='Subscribe', font=font,
    checked_color=(34, 197, 94),
    checked_border_color=(34, 197, 94),
)

# 无文字版
cb_plain = CSSCheckbox(50, 150, box_size=24)
```

**参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `checked` | False | 初始状态 |
| `box_size` | 20 | 复选框边长 |
| `box_color` / `checked_color` / `hover_color` / `disabled_color` | — | 四态背景 |
| `border_color` / `checked_border_color` | — | 选中时自动切换 |
| `border_width` / `border_radius` | 2 / 4 | |
| `check_color` | `(255,255,255)` | 对勾颜色 |
| `check_width` | 2 | 对勾线宽 |
| `label` | None | 文字（None 则无标签） |
| `font` / `text_color` | — | 标签字体/颜色 |
| `label_gap` | 8 | box 与文字间距 |
| `transition_speed` | 0.2 | 颜色/尺寸过渡 |
| `disabled` | False | 禁用 |
| `on_change(checked)` | None | 回调 |

**方法：**

```python
cb.toggle()           # 反转
cb.set_checked(True)  # 设定
cb.set_disabled(True) # 禁用
```

---

## CSSProgress

```python
from css_progress import CSSProgress
```

进度条，支持确定进度与不确定（循环动画）两种模式。

### 确定进度

```python
pg = CSSProgress(50, 50, 300, 10,
    value=0.35,                  # 0.0 ~ 1.0
    bar_color=(24, 144, 255),
    track_color=(230, 230, 230),
)

# 每帧或定时更新
pg.set_value(0.8)
```

### 带百分比文字

```python
pg = CSSProgress(50, 100, 300, 22,
    value=0.65,
    show_text=True,
    font=font_s,
    text_color=(255, 255, 255),
    bar_color=(34, 197, 94),
    text_format='{percent}%',   # 可自定义，支持 {percent} {value}
)
```

### 不确定进度（加载中）

```python
pg_loading = CSSProgress(50, 150, 300, 10,
    indeterminate=True,
    bar_color=(168, 85, 247),
    indeterminate_speed=0.015,
)
```

一段亮条会在轨道内左右循环移动，表达"处理中、进度未知"。

**参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `value` | 0.0 | 进度 (0~1) |
| `track_color` / `bar_color` | — | 背景 / 进度条色 |
| `border_radius` | `height//2` | 默认胶囊形 |
| `border_color` / `border_width` | None / 0 | |
| `show_text` / `font` / `text_color` | — | 文字显示 |
| `text_format` | `'{percent}%'` | 文字模板 |
| `indeterminate` | False | 不确定模式 |
| `indeterminate_speed` | 0.015 | 动画速度 |
| `animated` | True | 值变化平滑过渡 |
| `transition_speed` | 0.15 | 平滑过渡速度 |

---

## CSSPageControl

```python
from css_pagecontrol import CSSPageControl
```

iOS 风格的分页指示小圆点：N 个点代表 N 页，当前页放大变色，点击跳转。

```python
pc = CSSPageControl(100, 200, count=5,
    current=0,
    dot_size=8,
    active_size=14,
    gap=10,
    dot_color=(200, 200, 200),
    active_color=(24, 144, 255),
    on_change=lambda idx: print(f"page {idx}"),
)
```

### 垂直方向

```python
pc_v = CSSPageControl(20, 100, count=4,
    orientation='vertical',
    dot_size=10, active_size=20,
)
```

**参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `count` | — | 页数 |
| `current` | 0 | 当前页 (0-based) |
| `dot_size` | 8 | 未激活直径 |
| `active_size` | `dot_size * 1.5` | 激活直径 |
| `gap` | 10 | 间距 |
| `dot_color` / `active_color` / `hover_color` | — | 三态色 |
| `orientation` | `'horizontal'` | `'horizontal'` / `'vertical'` |
| `transition_speed` | 0.2 | 过渡速度 |
| `on_change(index)` | None | 回调 |

**方法：**

```python
pc.next()             # 下一页
pc.prev()             # 上一页
pc.set_current(3)     # 跳转
```

---

## Layout 布局系统

```python
from layout import HBox, VBox, Stack, Spacer, Label, Icon
```

布局系统独立于 CSSButton，可用于任何拥有 `rect` 属性的 Pygame 对象。

### HBox 水平布局

子元素从左到右排列，类似 CSS `flex-direction: row`。

```python
row = HBox(x=50, y=50, gap=20, children=[btn_a, btn_b, btn_c])
row.layout()  # 计算坐标
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `gap` | int | 0 | 子元素之间的间距 (px) |
| `align` | str | `'start'` | 主轴 (水平) 对齐: `'start'`, `'center'`, `'end'`, `'space-between'` |
| `valign` | str | `'start'` | 交叉轴 (垂直) 对齐: `'start'`, `'center'`, `'end'` |
| `padding` | int/tuple | 0 | 内边距，支持 `10` / `(10, 20)` / `(10, 20, 10, 20)` |
| `x, y` | int | 0 | 容器位置 |
| `width, height` | int | 0 | 容器尺寸，0 表示自动撑开 |

**居中对齐：**

```python
toolbar = HBox(x=0, y=0, width=800, gap=10, align='center', valign='center', children=[
    btn_bold, btn_italic, btn_underline,
])
toolbar.layout()
```

**两端对齐 (space-between)：**

```python
footer = HBox(x=0, y=500, width=800, height=60, align='space-between', valign='center',
    padding=(0, 20, 0, 20),
    children=[btn_cancel, btn_save],
)
footer.layout()
```

### VBox 垂直布局

子元素从上到下排列，类似 CSS `flex-direction: column`。

```python
sidebar = VBox(x=20, y=20, gap=15, children=[btn_home, btn_settings, btn_profile])
sidebar.layout()
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `gap` | int | 0 | 子元素之间的间距 (px) |
| `align` | str | `'start'` | 主轴 (垂直) 对齐: `'start'`, `'center'`, `'end'`, `'space-between'` |
| `halign` | str | `'start'` | 交叉轴 (水平) 对齐: `'start'`, `'center'`, `'end'` |
| `padding` | int/tuple | 0 | 内边距 |
| `x, y` | int | 0 | 容器位置 |
| `width, height` | int | 0 | 容器尺寸，0 表示自动撑开 |

**水平居中的垂直列表：**

```python
menu = VBox(x=100, y=50, width=300, gap=10, halign='center', children=[
    btn_option_a, btn_option_b, btn_option_c,
])
menu.layout()
```

### Stack 叠放布局

子元素在同一区域内叠放，各自独立定位，类似 CSS `position: absolute`。

```python
overlay = Stack(x=100, y=100, width=400, height=300)
overlay.add_aligned(background_panel, align='start', valign='start')
overlay.add_aligned(close_button, align='end', valign='start', offset=(-10, 10))
overlay.add_aligned(title_label, align='center', valign='center')
overlay.layout()
```

**参数 (add_aligned)：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `align` | str | `'start'` | 水平对齐: `'start'`, `'center'`, `'end'` |
| `valign` | str | `'start'` | 垂直对齐: `'start'`, `'center'`, `'end'` |
| `offset` | tuple | `(0, 0)` | 额外偏移 `(dx, dy)` |

### Spacer 空白占位

在 HBox/VBox 中插入固定大小的空白区域：

```python
# 水平间距
row = HBox(children=[btn_a, Spacer(width=50), btn_b])

# 垂直间距
col = VBox(children=[header, Spacer(height=30), content])
```

### Label 文本元素

可参与布局的文本叶子元素，支持多行：

```python
title = Label("Hello World", font_l, color=(0, 0, 0))
subtitle = Label("Line 1\nLine 2", font_s, color=(100, 100, 100))
```

**动态更新：**

```python
score_label = Label("Score: 0", font_m, color=(0, 0, 0))

# 游戏循环中更新
score_label.set_text(f"Score: {score}")
score_label.set_color((255, 0, 0))  # 变红
```

### Icon 图片元素

可参与布局的图片叶子元素，支持 PNG、JPG、SVG、Surface：

```python
logo = Icon('logo.png', size=(48, 48))
flag = Icon('flag.svg', size=(24, 16))
avatar = Icon(some_surface, size=(32, 32))   # 直接传入 Surface
raw = Icon('banner.png')                      # 不缩放，保持原尺寸
```

### 嵌套布局

容器可以互相嵌套，`layout()` 会递归计算所有子元素坐标：

```python
# 工具栏: 左侧 logo + 右侧按钮组
toolbar = HBox(x=0, y=0, width=800, height=60, align='space-between', valign='center',
    padding=(0, 20, 0, 20),
    children=[
        # 左侧
        HBox(gap=10, valign='center', children=[
            Icon('logo.svg', size=(32, 32)),
            Label("My App", font_l, color=(30, 30, 30)),
        ]),
        # 右侧
        HBox(gap=8, valign='center', children=[
            btn_settings,
            btn_profile,
            btn_logout,
        ]),
    ],
)
toolbar.layout()  # 一次调用，递归计算全部
```

### 页面级布局

组合 HBox + VBox 构建完整页面布局：

```python
# 侧边栏
sidebar = VBox(x=0, y=0, gap=10, padding=20, children=[
    btn_home, btn_explore, btn_library,
])

# 主内容区
main = VBox(x=0, y=0, gap=20, padding=20, children=[
    title_label,
    HBox(gap=15, children=[card_a, card_b, card_c]),  # 卡片行
    HBox(gap=15, children=[card_d, card_e, card_f]),
])

# 根布局
root = HBox(x=20, y=80, gap=30, children=[sidebar, main])
root.layout()

# 主循环
while running:
    screen.fill((240, 242, 245))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        root.handle_event(event)    # 递归分发事件
    root.draw(screen)               # 递归绘制
    pygame.display.flip()
```

**Padding 格式：**

```python
padding=10              # 四边各 10px
padding=(10, 20)        # 上下 10px，左右 20px
padding=(10, 20, 30, 40)  # 上 10, 右 20, 下 30, 左 40 (CSS 顺序)
```

**自动尺寸 vs 固定尺寸：**

```python
# 自动撑开 (width/height=0 或不传)
auto_box = HBox(x=50, y=50, gap=10, children=[btn_a, btn_b])
# 布局后 auto_box.rect.width == btn_a 宽 + btn_b 宽 + gap

# 固定尺寸
fixed_box = HBox(x=50, y=50, width=600, height=80, gap=10, children=[btn_a, btn_b])
# align='center' 时子元素会在 600px 内居中
```

---

## 完整示例

### 示例 1: 图标按钮 (set_content 方式)

```python
import pygame
from css_button import CSSButton
from layout import HBox, VBox, Icon, Label

pygame.init()
screen = pygame.display.set_mode((500, 300))
font = pygame.font.SysFont('arial', 20, bold=True)

btn = CSSButton(0, 0, 250, 60,
    bg_color=(24, 144, 255),
    hover_color=(64, 169, 255),
    pressed_color=(9, 88, 217),
    border_radius=12,
    shadow_color=(24, 144, 255, 50),
    shadow_blur=6,
)
btn.set_content(HBox(gap=10, align='center', valign='center', children=[
    Icon('download.svg', size=(24, 24)),
    Label("Download", font, color=(255, 255, 255)),
]))

layout = VBox(x=125, y=120, children=[btn])
layout.layout()

running = True
while running:
    screen.fill((240, 242, 245))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        layout.handle_event(event)
    layout.draw(screen)
    pygame.display.flip()
pygame.quit()
```

### 示例 2: 完整页面布局

```python
import pygame
from css_button import CSSButton
from layout import HBox, VBox, Spacer

pygame.init()
screen = pygame.display.set_mode((800, 500))
font = pygame.font.SysFont('arial', 18)

def make_btn(text, color):
    btn = CSSButton(0, 0, 200, 50, bg_color=color, border_radius=10)
    btn.add_text(text, font, color=(255, 255, 255))
    return btn

# 侧边栏
sidebar = VBox(gap=12, padding=15, children=[
    make_btn("Home",     (52, 152, 219)),
    make_btn("Explore",  (46, 204, 113)),
    make_btn("Settings", (155, 89, 182)),
])

# 主内容区按钮网格
grid = VBox(gap=12, children=[
    HBox(gap=12, children=[make_btn("Card A", (231, 76, 60)), make_btn("Card B", (230, 126, 34))]),
    HBox(gap=12, children=[make_btn("Card C", (241, 196, 15)), make_btn("Card D", (26, 188, 156))]),
])

# 根布局
root = HBox(x=30, y=30, gap=30, children=[sidebar, grid])
root.layout()

running = True
while running:
    screen.fill((240, 242, 245))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        root.handle_event(event)
    root.draw(screen)
    pygame.display.flip()
pygame.quit()
```

---

## 文件结构

```
pg_ui/
├── css_button.py         # CSSButton 按钮组件
├── css_label.py          # CSSLabel 样式化标签/徽章
├── css_textbox.py        # CSSTextBox 文本输入框 (single/multi/password)
├── css_checkbox.py       # CSSCheckbox 复选框
├── css_progress.py       # CSSProgress 进度条
├── css_pagecontrol.py    # CSSPageControl 分页圆点
├── layout.py             # 布局系统 (HBox, VBox, Stack, Spacer, Label, Icon)
├── test_css_button.py    # 单元测试
├── demo_css_button.py    # CSSButton 基础样式 Demo
├── demo_image_button.py  # 图片 + 文字混合 Demo
├── demo_layout.py        # 布局系统 Demo
├── demo_dashboard.py     # 综合 Dashboard Demo
└── demo_widgets.py       # 新组件综合 Demo (Label/TextBox/Checkbox/Progress/PageControl)
```
