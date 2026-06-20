"""
AIM MCP Server - LED 控制工具

封装 VEX AIM 库的 Led 相关 API，共 4 个工具。
"""

import threading
import time
from typing import Optional

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
    "OFF": None,
}


# ----------------------------------------------------------------------
# 全局 LED 状态：亮度倍率 + 闪烁控制
# ----------------------------------------------------------------------
_led_brightness: int = 100
_state_lock = threading.Lock()
_blink_stop = threading.Event()
_blink_thread: Optional[threading.Thread] = None


def _scale_rgb(r: int, g: int, b: int) -> tuple:
    """根据全局亮度倍率缩放 RGB。"""
    with _state_lock:
        scale = _led_brightness / 100.0
    return int(r * scale), int(g * scale), int(b * scale)


def _parse_led_index(target: str):
    """将 'ALL'/'0'..'5' 转换为 vex.LightType 或 int。"""
    t = target.strip().upper()
    if t == "ALL":
        return vex_types.LightType.ALL_LEDS
    if t.isdigit() and 0 <= int(t) <= 5:
        return int(t)
    raise ValueError(f"不支持的 LED target: {target}，应为 ALL 或 0~5")


@register_tool(
    name="aim_set_led",
    description="设置 LED 颜色，可按名称或 RGB 数值。RGB 会按全局亮度倍率自动缩放。",
)
def aim_set_led(
    target: str,
    color: Optional[str] = None,
    r: Optional[int] = None,
    g: Optional[int] = None,
    b: Optional[int] = None,
) -> str:
    """
    设置 LED 颜色。

    Args:
        target: "ALL" 或 "0"~"5"
        color: 颜色名（RED/GREEN/BLUE/WHITE/YELLOW/ORANGE/PURPLE/CYAN/BLACK/OFF），与 r,g,b 互斥
        r: 红色分量 0~255（与 color 互斥）
        g: 绿色分量 0~255
        b: 蓝色分量 0~255

    Returns:
        执行结果描述
    """
    if color is not None and (r is not None or g is not None or b is not None):
        return "color 与 r/g/b 不能同时指定"

    led = robot_manager.get_robot().led
    led_index = _parse_led_index(target)

    if color is not None:
        c = color.upper()
        if c not in _COLOR_MAP:
            return f"不支持的颜色: {color}"
        rgb = _COLOR_MAP[c]
        if rgb is None:
            led.on(led_index, 0, 0, 0)
            return f"已关闭 LED {target}"
        # vex.Color 通常有 .value / 可解包为 (r,g,b)
        try:
            rr, gg, bb = rgb.red, rgb.green, rgb.blue
        except AttributeError:
            rr, gg, bb = 0, 0, 0
        rr, gg, bb = _scale_rgb(rr, gg, bb)
        led.on(led_index, rr, gg, bb)
        return f"已将 LED {target} 设为 {c}（已按全局亮度缩放）"
    # RGB 模式
    if r is None or g is None or b is None:
        return "必须同时提供 r, g, b 三个分量"
    if not all(0 <= v <= 255 for v in (r, g, b)):
        return f"RGB 分量必须都在 0~255 范围，收到 r={r} g={g} b={b}"
    rr, gg, bb = _scale_rgb(r, g, b)
    led.on(led_index, rr, gg, bb)
    return f"已将 LED {target} 设为 RGB({r},{g},{b})（缩放后 {rr},{gg},{bb}）"


@register_tool(
    name="aim_set_led_brightness",
    description=(
        "设置全局 LED 亮度倍率（0~100）。"
        "100=原色不缩放，50=半亮度。后续 aim_set_led 的 RGB 分量会按此倍率缩放。"
    ),
)
def aim_set_led_brightness(brightness: int) -> str:
    if not 0 <= brightness <= 100:
        return f"亮度值 {brightness} 超出 0~100 范围"
    with _state_lock:
        global _led_brightness
        _led_brightness = brightness
    return f"全局 LED 亮度已设为 {brightness}%，后续 aim_set_led 会按此倍率自动缩放"


@register_tool(
    name="aim_blink_led",
    description="LED 按指定颜色和间隔（毫秒）闪烁。再次调用会替换前一次的闪烁线程。",
)
def aim_blink_led(color: str, interval_ms: int) -> str:
    """
    启动 LED 闪烁（后台线程）。

    Args:
        color: 颜色名
        interval_ms: 闪烁间隔（毫秒）

    Returns:
        执行结果描述
    """
    c = color.upper()
    if c not in _COLOR_MAP or _COLOR_MAP[c] is None:
        return f"不支持的颜色: {color}"

    led = robot_manager.get_robot().led
    rgb = _COLOR_MAP[c]
    try:
        base_r, base_g, base_b = rgb.red, rgb.green, rgb.blue
    except AttributeError:
        base_r, base_g, base_b = 0, 0, 0

    # 重置旧线程的 stop 信号
    global _blink_thread
    _blink_stop.set()
    _blink_stop.clear()

    def _blink():
        on = False
        while not _blink_stop.is_set():
            if on:
                rr, gg, bb = _scale_rgb(base_r, base_g, base_b)
                led.on(vex_types.LightType.ALL_LEDS, rr, gg, bb)
            else:
                led.on(vex_types.LightType.ALL_LEDS, 0, 0, 0)
            on = not on
            # 等待 stop 信号或 interval_ms
            _blink_stop.wait(timeout=max(0.05, interval_ms / 1000.0))

    _blink_thread = threading.Thread(target=_blink, daemon=True)
    _blink_thread.start()
    return f"已启动 LED 闪烁（color={c}，间隔={interval_ms}ms）"


@register_tool(
    name="aim_stop_blink_led",
    description="停止由 aim_blink_led 启动的 LED 闪烁。",
)
def aim_stop_blink_led() -> str:
    _blink_stop.set()
    return "已请求停止 LED 闪烁"
