"""
AIM MCP Server - 屏幕工具

封装 VEX AIM 库的 Screen 相关 API，共 22 个工具。
"""

import threading
from typing import List, Optional

import vex as vex_types

from ..connection import robot_manager
from ._decorators import register_tool


_COLOR_MAP = {
    "RED": vex_types.Color.RED,
    "GREEN": vex_types.Color.GREEN,
    "BLUE": vex_types.Color.BLUE,
    "WHITE": vex_types.Color.WHITE,
    "YELLOW": vex_types.Color.YELLOW,
    "ORANGE": vex_types.Color.ORANGE,
    "PURPLE": vex_types.Color.PURPLE,
    "CYAN": vex_types.Color.CYAN,
    "BLACK": vex_types.Color.BLACK,
    "TRANSPARENT": vex_types.Color.TRANSPARENT,
}


_EMOJI_MAP = {e.name: e for e in vex_types.EmojiType}
_LOOK_MAP = {l.name: l for l in vex_types.EmojiLookType}


def _parse_color(color: str):
    c = color.upper()
    if c not in _COLOR_MAP:
        raise ValueError(
            f"不支持的颜色: {color}，可选: {', '.join(sorted(_COLOR_MAP.keys()))}"
        )
    return _COLOR_MAP[c]


def _screen():
    return robot_manager.get_robot().screen


def _robot():
    return robot_manager.get_robot()


# ----------------------------------------------------------------------
# 基础屏幕工具
# ----------------------------------------------------------------------
@register_tool(
    name="aim_print_screen",
    description="在屏幕当前光标位置打印文本。",
)
def aim_print_screen(text: str) -> str:
    _screen().print(text)
    return f"已打印: {text}"


@register_tool(
    name="aim_print_at",
    description="在屏幕指定 (x, y) 坐标打印文本。",
)
def aim_print_at(text: str, x: int, y: int) -> str:
    _screen().print_at(text, x=x, y=y)
    return f"已在 ({x},{y}) 打印: {text}"


@register_tool(
    name="aim_clear_screen",
    description="清空屏幕，可指定背景颜色。",
)
def aim_clear_screen(color: str = "BLUE") -> str:
    try:
        _screen().clear_screen(_parse_color(color))
    except ValueError as e:
        return str(e)
    return f"已清屏（背景色 {color.upper()}）"


@register_tool(
    name="aim_set_cursor",
    description="设置屏幕光标位置（row, column）。",
)
def aim_set_cursor(row: int, column: int) -> str:
    _screen().set_cursor(row, column)
    return f"光标已设到 ({row}, {column})"


@register_tool(
    name="aim_set_pen_color",
    description="设置画笔颜色。",
)
def aim_set_pen_color(color: str) -> str:
    try:
        _screen().set_pen_color(_parse_color(color))
    except ValueError as e:
        return str(e)
    return f"画笔颜色已设为 {color.upper()}"


@register_tool(
    name="aim_set_fill_color",
    description="设置填充颜色。",
)
def aim_set_fill_color(color: str) -> str:
    try:
        _screen().set_fill_color(_parse_color(color))
    except ValueError as e:
        return str(e)
    return f"填充颜色已设为 {color.upper()}"


@register_tool(
    name="aim_set_pen_width",
    description="设置画笔宽度（像素）。",
)
def aim_set_pen_width(width: int) -> str:
    _screen().set_pen_width(width)
    return f"画笔宽度已设为 {width}"


@register_tool(
    name="aim_draw_pixel",
    description="在指定坐标画一个像素。",
)
def aim_draw_pixel(x: int, y: int) -> str:
    _screen().draw_pixel(x, y)
    return f"已在 ({x},{y}) 画点"


@register_tool(
    name="aim_draw_line",
    description="画一条直线。",
)
def aim_draw_line(x1: int, y1: int, x2: int, y2: int) -> str:
    _screen().draw_line(x1, y1, x2, y2)
    return f"已画线 ({x1},{y1}) -> ({x2},{y2})"


@register_tool(
    name="aim_draw_rectangle",
    description="画一个矩形。",
)
def aim_draw_rectangle(x: int, y: int, width: int, height: int) -> str:
    _screen().draw_rectangle(x, y, width, height)
    return f"已画矩形 ({x},{y}) {width}x{height}"


@register_tool(
    name="aim_draw_circle",
    description="画一个圆。",
)
def aim_draw_circle(x: int, y: int, radius: int) -> str:
    _screen().draw_circle(x, y, radius)
    return f"已画圆 ({x},{y}) 半径 {radius}"


@register_tool(
    name="aim_show_emoji",
    description="显示一个表情，可指定朝向。",
)
def aim_show_emoji(emoji: str, look: str = "LOOK_FORWARD") -> str:
    e = emoji.upper()
    lk = look.upper()
    if e not in _EMOJI_MAP:
        return f"不支持的 emoji: {emoji}"
    if lk not in _LOOK_MAP:
        return f"不支持的 look: {look}，可选: {', '.join(sorted(_LOOK_MAP.keys()))}"
    _screen().show_emoji(_EMOJI_MAP[e], _LOOK_MAP[lk])
    return f"已显示 emoji {e}（{lk}）"


@register_tool(
    name="aim_hide_emoji",
    description="隐藏屏幕上的表情。",
)
def aim_hide_emoji() -> str:
    _screen().hide_emoji()
    return "已隐藏 emoji"


# ----------------------------------------------------------------------
# 高级屏幕工具（S1~S9）
# ----------------------------------------------------------------------
_EMOJI_STOP = threading.Event()
_EMOJI_THREAD: Optional[threading.Thread] = None


@register_tool(
    name="aim_show_battery_gauge",
    description=(
        "读取当前电池电量，在屏幕上画一个电池图标 + 百分比数字。"
        "配色：>30% 绿、>15% 黄、≤15% 红。"
    ),
)
def aim_show_battery_gauge(x: int = 20, y: int = 20, width: int = 80, height: int = 30) -> str:
    pct = _robot().battery.capacity()
    if pct > 30:
        fill = "GREEN"
    elif pct > 15:
        fill = "YELLOW"
    else:
        fill = "RED"
    sc = _screen()
    sc.set_fill_color(_parse_color(fill))
    sc.set_pen_color(_parse_color("WHITE"))
    bar_w = int(width * pct / 100)
    sc.draw_rectangle(x, y, bar_w, height)
    sc.set_fill_color(_parse_color("TRANSPARENT"))
    sc.set_pen_color(_parse_color("WHITE"))
    sc.draw_rectangle(x, y, width, height)
    sc.print_at(f"{pct}%", x + width + 4, y + height // 2 - 8)
    return f"已绘制电池仪表盘 {pct}%"


@register_tool(
    name="aim_show_emotion_sequence",
    description=(
        "按 JSON 数组顺序循环显示表情（后台线程）。"
        "再次调用会替换前一次的轮播；用 aim_stop_emotion_sequence 停止。"
    ),
)
def aim_show_emotion_sequence(
    emotions: List[str],
    interval_ms: int = 1000,
    loop: bool = True,
    look: str = "LOOK_FORWARD",
) -> str:
    global _EMOJI_THREAD
    lk = look.upper()
    if lk not in _LOOK_MAP:
        return f"不支持的 look: {look}"
    normalized = [e.upper() for e in emotions]
    bad = [e for e in normalized if e not in _EMOJI_MAP]
    if bad:
        return f"不支持的 emoji: {bad}"

    _EMOJI_STOP.set()
    _EMOJI_STOP.clear()

    def _run():
        sc = _screen()
        while not _EMOJI_STOP.is_set():
            for e in normalized:
                if _EMOJI_STOP.is_set():
                    break
                try:
                    sc.show_emoji(_EMOJI_MAP[e], _LOOK_MAP[lk])
                except Exception:
                    pass
                _EMOJI_STOP.wait(timeout=max(0.1, interval_ms / 1000.0))
            if not loop:
                break

    _EMOJI_THREAD = threading.Thread(target=_run, daemon=True)
    _EMOJI_THREAD.start()
    return f"已启动表情轮播：{emotions}（间隔 {interval_ms}ms, loop={loop}）"


@register_tool(
    name="aim_stop_emotion_sequence",
    description="停止由 aim_show_emotion_sequence 启动的表情轮播。",
)
def aim_stop_emotion_sequence() -> str:
    _EMOJI_STOP.set()
    return "已请求停止表情轮播"


@register_tool(
    name="aim_show_image_file",
    description=(
        "从本地文件加载 bmp/png 图片并显示在屏幕指定坐标。"
        "文件需先通过 VEX 文件管理上传到机器人。"
    ),
)
def aim_show_image_file(path: str, x: int = 0, y: int = 0) -> str:
    import os
    if not os.path.isfile(path):
        return f"文件不存在: {path}"
    try:
        _screen().show_image(path, x, y)
    except Exception as e:
        return f"显示图片失败: {e}"
    return f"已显示图片 {path} @ ({x},{y})"


@register_tool(
    name="aim_set_screen_font",
    description=(
        "切换屏幕字体。"
        "可选：MONO12/15/20/24/30/36/40/60 或 PROP20/24/30/36/40/60。"
    ),
)
def aim_set_screen_font(font: str) -> str:
    try:
        font_type = getattr(vex_types.FontType, font.upper())
    except AttributeError:
        names = [a for a in dir(vex_types.FontType) if not a.startswith("_")]
        return f"不支持的字体: {font}，可选: {names}"
    _screen().set_font(font_type)
    return f"字体已设为 {font.upper()}"


@register_tool(
    name="aim_clear_row",
    description="清除屏幕的某一行，可指定背景色。",
)
def aim_clear_row(row: int, color: str = "BLUE") -> str:
    try:
        c = _parse_color(color)
    except ValueError as e:
        return str(e)
    _screen().clear_row(row, c)
    return f"已清除第 {row} 行（背景 {color.upper()}）"


@register_tool(
    name="aim_set_screen_origin",
    description="重新定义屏幕坐标系的原点 (0, 0)；后续 print_at / draw_* 都会相对新原点。",
)
def aim_set_screen_origin(x: int = 0, y: int = 0) -> str:
    _screen().set_origin(x, y)
    return f"屏幕原点已设为 ({x}, {y})"


@register_tool(
    name="aim_set_screen_clip",
    description="限制后续绘图只在 (x, y, width, height) 矩形区域内。便于做分屏/对话框效果。",
)
def aim_set_screen_clip(x: int, y: int, width: int, height: int) -> str:
    _screen().set_clip_region(x, y, width, height)
    return f"屏幕裁剪区域已设为 ({x},{y}) {width}x{height}"


@register_tool(
    name="aim_draw_progress_bar",
    description=(
        "在屏幕指定位置画一个水平进度条 + 百分比数字。"
        "颜色逻辑：>=30% GREEN / >=10% YELLOW / <10% RED。color=AUTO 自动按阈值选色。"
    ),
)
def aim_draw_progress_bar(
    x: int = 20,
    y: int = 20,
    width: int = 120,
    height: int = 20,
    percent: int = 50,
    color: str = "AUTO",
) -> str:
    if color.upper() == "AUTO":
        if percent >= 30:
            color = "GREEN"
        elif percent >= 10:
            color = "YELLOW"
        else:
            color = "RED"
    try:
        c = _parse_color(color)
    except ValueError as e:
        return str(e)
    sc = _screen()
    sc.set_fill_color(c)
    sc.draw_rectangle(x, y, int(width * percent / 100), height)
    sc.set_pen_color(_parse_color("WHITE"))
    sc.draw_rectangle(x, y, width, height)
    sc.print_at(f"{percent}%", x + width + 4, y + height // 2 - 8)
    return f"已绘制进度条 {percent}%（color={color.upper()}）"
