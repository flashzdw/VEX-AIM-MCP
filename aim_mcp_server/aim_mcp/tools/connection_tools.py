"""
AIM MCP Server - 连接管理工具

提供以下工具：
- aim_connect：连接 / 切换到指定 host（可指定端口）
- aim_disconnect：断开当前连接
- aim_is_connected：检查连接状态
- aim_set_port：仅修改端口（不立即重连）
- aim_get_port：查询当前端口设置
- aim_get_effective_port：查询实际生效的端口（考虑环境变量和默认）
"""

from ..connection import robot_manager
from ._decorators import register_tool


@register_tool(
    name="aim_connect",
    description="连接（或切换）到指定 host 的 AIM 机器人；可同时指定 WebSocket 端口。",
)
def aim_connect(host: str, port: int | None = None) -> str:
    """
    连接（或切换）到指定 host 的 VEX AIM 机器人。

    Args:
        host: 机器人 IP / 主机名（AP 模式下默认 192.168.4.1）
        port: WebSocket 端口，1-65535 之间的整数；为 None 时使用默认 80
               （也可通过 `AIM_ROBOT_PORT` 环境变量设置）

    Returns:
        成功或失败描述
    """
    try:
        return robot_manager.connect(host, port=port)
    except Exception as e:
        from ..connection import map_aim_exception
        return map_aim_exception(e)


@register_tool(
    name="aim_disconnect",
    description="断开当前与 AIM 机器人的连接。",
)
def aim_disconnect() -> str:
    """断开当前 Robot 实例。"""
    return robot_manager.disconnect()


@register_tool(
    name="aim_is_connected",
    description="检查当前是否已建立与 AIM 机器人的连接。",
    read_only=True,
)
def aim_is_connected() -> bool:
    """返回当前是否已连接。"""
    return robot_manager.is_connected()


@register_tool(
    name="aim_set_port",
    description="设置 WebSocket 端口（不立即重连），传入 None 恢复默认 80。",
)
def aim_set_port(port: int | None = None) -> str:
    """
    修改 WebSocket 端口设置。若当前已连接，会先断开。

    Args:
        port: 新的端口号（1-65535），传入 None 恢复默认 80

    Returns:
        操作结果描述
    """
    try:
        return robot_manager.set_port(port)
    except ValueError as e:
        return f"端口无效: {e}"
    except Exception as e:
        from ..connection import map_aim_exception
        return map_aim_exception(e)


@register_tool(
    name="aim_get_port",
    description="查询当前显式设置的 WebSocket 端口（None 表示使用默认 80）。",
    read_only=True,
)
def aim_get_port() -> int | None:
    """返回当前设置的端口；未设置时返回 None。"""
    return robot_manager.get_port()


@register_tool(
    name="aim_get_effective_port",
    description="查询实际生效的 WebSocket 端口（考虑设置、环境变量和默认值）。",
    read_only=True,
)
def aim_get_effective_port() -> int:
    """返回实际生效的端口（80 或显式设置的端口）。"""
    return robot_manager.get_effective_port()
