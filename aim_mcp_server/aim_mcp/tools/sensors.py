"""
AIM MCP Server - 传感器工具

封装 VEX AIM 库的 Inertial / 屏幕触摸 / 电池等传感器 API，共 9 个工具。
"""

import vex as vex_types

from ..connection import robot_manager
from ._decorators import register_tool


_AXIS_MAP = {
    "X": vex_types.AxisType.X_AXIS,
    "Y": vex_types.AxisType.Y_AXIS,
    "Z": vex_types.AxisType.Z_AXIS,
}


def _inertial():
    return robot_manager.get_robot().inertial


def _screen():
    return robot_manager.get_robot().screen


@register_tool(
    name="aim_get_battery_capacity",
    description="获取电池剩余容量百分比（0~100）。",
    read_only=True,
)
def aim_get_battery_capacity() -> int:
    return robot_manager.get_robot().get_battery_capacity()


@register_tool(
    name="aim_get_acceleration",
    description="获取 IMU 在指定轴上的加速度（X/Y/Z）。",
    read_only=True,
)
def aim_get_acceleration(axis: str) -> float:
    a = axis.upper()
    if a not in _AXIS_MAP:
        return f"不支持的轴: {axis}，应为 X/Y/Z"
    return _inertial().get_acceleration(_AXIS_MAP[a])


@register_tool(
    name="aim_get_turn_rate",
    description="获取陀螺仪在指定轴上的角速度（DPS），X/Y/Z。",
    read_only=True,
)
def aim_get_turn_rate(axis: str) -> float:
    a = axis.upper()
    if a not in _AXIS_MAP:
        return f"不支持的轴: {axis}，应为 X/Y/Z"
    return _inertial().get_turn_rate(_AXIS_MAP[a])


@register_tool(
    name="aim_get_roll",
    description="获取 IMU 的 roll 角（度）。",
    read_only=True,
)
def aim_get_roll() -> float:
    return _inertial().get_roll()


@register_tool(
    name="aim_get_pitch",
    description="获取 IMU 的 pitch 角（度）。",
    read_only=True,
)
def aim_get_pitch() -> float:
    return _inertial().get_pitch()


@register_tool(
    name="aim_get_yaw",
    description="获取 IMU 的 yaw 角（度）。",
    read_only=True,
)
def aim_get_yaw() -> float:
    return _inertial().get_yaw()


@register_tool(
    name="aim_is_screen_pressed",
    description="检查机器人屏幕是否被触摸。",
    read_only=True,
)
def aim_is_screen_pressed() -> bool:
    return _screen().pressing()


@register_tool(
    name="aim_get_touch_x",
    description="获取最近一次屏幕触摸的 X 坐标。",
    read_only=True,
)
def aim_get_touch_x() -> float:
    return _screen().x_position()


@register_tool(
    name="aim_get_touch_y",
    description="获取最近一次屏幕触摸的 Y 坐标。",
    read_only=True,
)
def aim_get_touch_y() -> float:
    return _screen().y_position()
