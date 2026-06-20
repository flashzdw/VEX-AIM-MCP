"""
AIM MCP Server - 踢球器工具

封装 VEX AIM 库的 Kicker 相关 API，共 2 个工具。
"""

import vex as vex_types

from ..connection import robot_manager
from ._decorators import register_tool


@register_tool(
    name="aim_kick",
    description="踢球，可指定力度（SOFT/MEDIUM/HARD）。",
)
def aim_kick(force: str = "MEDIUM") -> str:
    """
    激活踢球器。

    Args:
        force: 力度 "SOFT" / "MEDIUM" / "HARD"

    Returns:
        执行结果描述
    """
    f = force.upper()
    kick_map = {
        "SOFT": vex_types.KickType.SOFT,
        "MEDIUM": vex_types.KickType.MEDIUM,
        "HARD": vex_types.KickType.HARD,
    }
    if f not in kick_map:
        return f"不支持的力度: {force}，应为 SOFT/MEDIUM/HARD"
    robot_manager.get_robot().kicker.kick(kick_map[f])
    return f"已以 {f} 力度踢球"


@register_tool(
    name="aim_place",
    description="轻柔地将前方物体放下。",
)
def aim_place() -> str:
    """放置前方物体。"""
    robot_manager.get_robot().kicker.place()
    return "已放置前方物体"
