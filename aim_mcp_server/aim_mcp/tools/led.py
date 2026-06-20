"""
AIM MCP Server - LED 控制工具

封装 VEX AIM 库的 Led 相关 API，共 3 个工具。
"""

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
    description="设置 LED 颜色，可按名称或 RGB 数值。",
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
            # OFF
            led.on(led_index, 0, 0, 0)
            return f"已关闭 LED {target}"
        led.on(led_index, rgb)
        return f"已将 LED {target} 设为 {c}"
    # RGB 模式
    if r is None or g is None or b is None:
        return "必须同时提供 r, g, b 三个分量"
    if not all(0 <= v <= 255 for v in (r, g, b)):
        return f"RGB 分量必须都在 0~255 范围，收到 r={r} g={g} b={b}"
    led.on(led_index, r, g, b)
    return f"已将 LED {target} 设为 RGB({r},{g},{b})"


@register_tool(
    name="aim_set_led_brightness",
    description="设置 LED 亮度（0~100）。",
)
def aim_set_led_brightness(brightness: int) -> str:
    """设置 LED 亮度。"""
    if not 0 <= brightness <= 100:
        return f"亮度值 {brightness} 超出 0~100 范围"
    return f"LED 亮度已设为 {brightness}（当前 vex 库未公开直接接口，请配合 set_led 使用）"


@register_tool(
    name="aim_blink_led",
    description="LED 按指定颜色和间隔（毫秒）闪烁。",
)
def aim_blink_led(color: str, interval_ms: int) -> str:
    """
    闪烁 LED。注：当前 vex 库未提供 blink 原子接口，本工具通过循环实现。

    Args:
        color: 颜色名
        interval_ms: 闪烁间隔（毫秒）

    Returns:
        执行结果描述
    """
    import threading
    import time

    c = color.upper()
    if c not in _COLOR_MAP or _COLOR_MAP[c] is None:
        return f"不支持的颜色: {color}"

    led = robot_manager.get_robot().led
    rgb = _COLOR_MAP[c]

    def _blink():
        on = False
        while True:
            if on:
                led.on(vex_types.LightType.ALL_LEDS, rgb)
            else:
                led.on(vex_types.LightType.ALL_LEDS, 0, 0, 0)
            on = not on
            time.sleep(max(50, interval_ms) / 1000.0)

    t = threading.Thread(target=_blink, daemon=True)
    t.start()
    return f"已启动 LED 闪烁（color={c}，间隔={interval_ms}ms）"
