"""
AIM MCP Server - 屏幕工具

封装 VEX AIM 库的 Screen 相关 API，共 13 个工具。
"""

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


# ----------------------------------------------------------------------
# 屏幕工具
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
