"""
AIM MCP Server - Resources

只读状态资源，供 Agent 主动查询当前机器人状态。
"""

import json

from mcp.types import Annotations

from .connection import robot_manager


def _robot():
    return robot_manager.get_robot()


def get_status_resource(mcp):
    """注册 aim://status 资源。"""

    @mcp.resource(
        "aim://status",
        name="aim_status",
        description="AIM 机器人完整状态 JSON（位置、朝向、电池、视觉、屏幕、触摸等）",
        mime_type="application/json",
        annotations=Annotations(readOnlyHint=True, audience=["user", "assistant"]),
    )
    def aim_status() -> str:
        """返回当前完整 status dict 的 JSON 字符串。"""
        try:
            return json.dumps(_robot().status, ensure_ascii=False, indent=2)
        except Exception as e:
            from .connection import map_aim_exception
            return json.dumps({"error": map_aim_exception(e)}, ensure_ascii=False)

    return aim_status


def get_battery_resource(mcp):
    """注册 aim://battery 资源。"""

    @mcp.resource(
        "aim://battery",
        name="aim_battery",
        description="AIM 机器人电池剩余容量百分比（纯文本，0~100）",
        mime_type="text/plain",
        annotations=Annotations(readOnlyHint=True, audience=["user", "assistant"]),
    )
    def aim_battery() -> str:
        """返回电池剩余百分比字符串。"""
        try:
            return str(_robot().get_battery_capacity())
        except Exception as e:
            from .connection import map_aim_exception
            return map_aim_exception(e)

    return aim_battery


def get_position_resource(mcp):
    """注册 aim://position 资源。"""

    @mcp.resource(
        "aim://position",
        name="aim_position",
        description='AIM 机器人当前位姿 JSON，格式 {"x": float, "y": float, "heading": float}',
        mime_type="application/json",
        annotations=Annotations(readOnlyHint=True, audience=["user", "assistant"]),
    )
    def aim_position() -> str:
        """返回位置 + 朝向的 JSON。"""
        try:
            r = _robot()
            payload = {
                "x": r.get_x_position(),
                "y": r.get_y_position(),
                "heading": r.inertial.get_heading(),
            }
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            from .connection import map_aim_exception
            return json.dumps({"error": map_aim_exception(e)}, ensure_ascii=False)

    return aim_position


def register_all(mcp) -> None:
    """注册全部 resources。"""
    get_status_resource(mcp)
    get_battery_resource(mcp)
    get_position_resource(mcp)
