"""
AIM MCP Server - 运动控制工具

封装 VEX AIM 库的运动相关 API，共 16 个工具。
"""

from typing import Optional

import vex as vex_types
from vex import Robot

from ..connection import robot_manager
from ._decorators import register_tool


# ----------------------------------------------------------------------
# 内部辅助
# ----------------------------------------------------------------------
def _robot() -> Robot:
    """获取共享 Robot 实例（延迟连接）。"""
    return robot_manager.get_robot()


def _drive_velocity_unit(unit: str) -> vex_types.DriveVelocityUnits:
    """将字符串单位转换为 DriveVelocityUnits 枚举。"""
    u = unit.upper()
    if u == "PERCENT":
        return vex_types.DriveVelocityUnits.PERCENT
    if u == "MMPS":
        return vex_types.DriveVelocityUnits.MMPS
    raise ValueError(f"不支持的移动速度单位: {unit}")


def _turn_velocity_unit(unit: str) -> vex_types.TurnVelocityUnits:
    """将字符串单位转换为 TurnVelocityUnits 枚举。"""
    u = unit.upper()
    if u == "PERCENT":
        return vex_types.TurnVelocityUnits.PERCENT
    if u == "DPS":
        return vex_types.TurnVelocityUnits.DPS
    raise ValueError(f"不支持的转向速度单位: {unit}")


def _turn_direction(direction: str) -> vex_types.TurnType:
    """将字符串方向转换为 TurnType 枚举。"""
    d = direction.upper()
    if d == "LEFT":
        return vex_types.TurnType.LEFT
    if d == "RIGHT":
        return vex_types.TurnType.RIGHT
    raise ValueError(f"不支持的转向方向: {direction}，应为 LEFT 或 RIGHT")


# ----------------------------------------------------------------------
# 运动控制工具
# ----------------------------------------------------------------------
@register_tool(
    name="aim_move_at",
    description="持续以指定方向（-360~360 度）和速度移动，速度为 0~100% 或 MMPS。",
)
def aim_move_at(
    direction: float,
    velocity: Optional[int] = None,
    unit: str = "PERCENT",
) -> str:
    """
    持续以指定角度和速度移动（不会自动停止，需要后续调用 aim_stop）。

    Args:
        direction: 方向角（度），0=前方，90=右方，180=后方，-90=左方
        velocity: 速度（0~100 或具体 MMPS），None 使用默认速度
        unit: 速度单位，"PERCENT" 或 "MMPS"

    Returns:
        执行结果描述
    """
    _robot().move_at(direction, velocity=velocity, units=_drive_velocity_unit(unit))
    return f"已开始以 {velocity if velocity is not None else '默认'} {unit} 沿 {direction}° 方向持续移动"


@register_tool(
    name="aim_move_for",
    description="沿指定方向移动指定距离（毫米），可选择阻塞等待完成。",
)
def aim_move_for(
    distance: float,
    direction: float,
    velocity: Optional[int] = None,
    unit: str = "PERCENT",
    wait: bool = True,
) -> str:
    """
    沿指定方向移动指定距离。

    Args:
        distance: 距离（毫米）
        direction: 方向角（度）
        velocity: 速度（0~100 或 MMPS），None 使用默认速度
        unit: 速度单位
        wait: 是否阻塞等待移动完成

    Returns:
        执行结果描述
    """
    _robot().move_for(
        distance,
        direction,
        velocity=velocity,
        units=_drive_velocity_unit(unit),
        wait=wait,
    )
    return f"已沿 {direction}° 方向移动 {distance}mm（wait={wait}）"


@register_tool(
    name="aim_move_with_vectors",
    description="全向向量移动，同时控制前进/横向/旋转三轴速度（-100~100）。",
)
def aim_move_with_vectors(
    forwards: float,
    rightwards: float,
    rotation: float,
) -> str:
    """
    使用向量方式同时控制三个轴的移动。

    Args:
        forwards: 前进分量（-100~100），正数前进，负数后退
        rightwards: 横向分量（-100~100），正数右移，负数左移
        rotation: 旋转分量（-100~100），正数顺时针，负数逆时针

    Returns:
        执行结果描述
    """
    _robot().move_with_vectors(forwards, rightwards, rotation)
    return f"已应用向量运动 f={forwards} r={rightwards} rot={rotation}"


@register_tool(
    name="aim_turn",
    description="持续以指定方向（LEFT/RIGHT）和速度旋转，需要后续调用 aim_stop 停止。",
)
def aim_turn(
    direction: str,
    velocity: Optional[int] = None,
    unit: str = "PERCENT",
) -> str:
    """
    持续转向。

    Args:
        direction: "LEFT" 或 "RIGHT"
        velocity: 速度（0~100 或 DPS），None 使用默认速度
        unit: 速度单位

    Returns:
        执行结果描述
    """
    _robot().turn(
        _turn_direction(direction),
        velocity=velocity,
        units=_turn_velocity_unit(unit),
    )
    return f"已开始以 {direction} 方向持续旋转"


@register_tool(
    name="aim_turn_for",
    description="转向指定角度（度），可阻塞等待完成。",
)
def aim_turn_for(
    direction: str,
    angle: float,
    velocity: Optional[int] = None,
    unit: str = "PERCENT",
    wait: bool = True,
) -> str:
    """
    转向指定角度。

    Args:
        direction: "LEFT" 或 "RIGHT"
        angle: 角度（度）
        velocity: 速度
        unit: 速度单位
        wait: 是否阻塞等待

    Returns:
        执行结果描述
    """
    _robot().turn_for(
        _turn_direction(direction),
        angle,
        velocity=velocity,
        units=_turn_velocity_unit(unit),
        wait=wait,
    )
    return f"已向 {direction} 旋转 {angle}°（wait={wait}）"


@register_tool(
    name="aim_turn_to",
    description="转向绝对朝向（0~359.99 度），可阻塞等待完成。",
)
def aim_turn_to(
    heading: float,
    velocity: Optional[int] = None,
    unit: str = "PERCENT",
    wait: bool = True,
) -> str:
    """
    转向绝对朝向。

    Args:
        heading: 目标朝向（度，-360~360）
        velocity: 速度
        unit: 速度单位
        wait: 是否阻塞等待

    Returns:
        执行结果描述
    """
    _robot().turn_to(
        heading,
        velocity=velocity,
        units=_turn_velocity_unit(unit),
        wait=wait,
    )
    return f"已转向 {heading}°（wait={wait}）"


@register_tool(
    name="aim_stop",
    description="立即停止所有运动（移动 + 转向）。",
)
def aim_stop() -> str:
    """停止所有运动。"""
    _robot().stop_all_movement()
    return "已停止所有运动"


@register_tool(
    name="aim_spin_wheels",
    description="直接控制三个轮子的速度（-100~100）。",
)
def aim_spin_wheels(v1: int, v2: int, v3: int) -> str:
    """
    单独控制每个轮子。

    Args:
        v1: 轮子 1 速度
        v2: 轮子 2 速度
        v3: 轮子 3 速度

    Returns:
        执行结果描述
    """
    _robot().spin_wheels(v1, v2, v3)
    return f"已设置轮速 v1={v1} v2={v2} v3={v3}"


@register_tool(
    name="aim_set_move_velocity",
    description="设置后续移动命令的默认速度（PERCENT 或 MMPS）。",
)
def aim_set_move_velocity(velocity: int, unit: str = "PERCENT") -> str:
    """设置默认移动速度。"""
    _robot().set_move_velocity(velocity, units=_drive_velocity_unit(unit))
    return f"默认移动速度已设为 {velocity} {unit}"


@register_tool(
    name="aim_set_turn_velocity",
    description="设置后续转向命令的默认速度（PERCENT 或 DPS）。",
)
def aim_set_turn_velocity(velocity: int, unit: str = "PERCENT") -> str:
    """设置默认转向速度。"""
    _robot().set_turn_velocity(velocity, units=_turn_velocity_unit(unit))
    return f"默认转向速度已设为 {velocity} {unit}"


@register_tool(
    name="aim_set_xy_position",
    description="设置机器人当前位置坐标（用于位姿原点重置）。",
)
def aim_set_xy_position(x: float, y: float) -> str:
    """设置位置。"""
    _robot().set_xy_position(x, y)
    return f"位置已设为 ({x}, {y})"


@register_tool(
    name="aim_get_position",
    description="获取机器人当前 (x, y) 位置（坐标单位：毫米）。",
    read_only=True,
)
def aim_get_position() -> dict:
    """返回包含 x、y 的字典。"""
    r = _robot()
    return {"x": r.get_x_position(), "y": r.get_y_position()}


@register_tool(
    name="aim_get_heading",
    description="获取机器人当前朝向（0~359.99 度）。",
    read_only=True,
)
def aim_get_heading() -> float:
    """返回当前朝向。"""
    return _robot().inertial.get_heading()


@register_tool(
    name="aim_get_rotation",
    description="获取机器人累计旋转角度（自上次重置起）。",
    read_only=True,
)
def aim_get_rotation() -> float:
    """返回累计旋转角度。"""
    return _robot().inertial.get_rotation()


@register_tool(
    name="aim_set_heading",
    description="设置机器人当前朝向值。",
)
def aim_set_heading(heading: float) -> str:
    """设置朝向。"""
    _robot().inertial.set_heading(heading)
    return f"朝向已设为 {heading}°"


@register_tool(
    name="aim_reset_heading",
    description="将机器人朝向重置为 0。",
)
def aim_reset_heading() -> str:
    """重置朝向。"""
    _robot().inertial.reset_heading()
    return "朝向已重置为 0"
