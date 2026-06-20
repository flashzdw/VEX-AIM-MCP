"""
AIM MCP Server - 工具装饰器工厂

提供 register_tool 装饰器，封装 @mcp.tool(...) 注册，
并自动将 DisconnectedException / AimException 转换为可读错误字符串返回。
"""

import functools
import inspect
import logging
from typing import Any, Callable, Optional

from mcp.server.fastmcp import FastMCP

from ..connection import map_aim_exception, robot_manager
from vex import DisconnectedException, AimException

logger = logging.getLogger(__name__)

# 共享 FastMCP 实例（在 server.py 中创建并被此处引用）
mcp: FastMCP = None  # type: ignore[assignment]


def set_mcp(instance: FastMCP) -> None:
    """由 server.py 在创建 FastMCP 实例后注入，避免循环导入。"""
    global mcp
    mcp = instance


def register_tool(
    name: str,
    description: str,
    read_only: bool = False,
    destructive: bool = False,
    idempotent: bool = False,
    open_world: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    装饰器工厂：注册一个 MCP 工具并自动处理 AIM 异常。

    Args:
        name: 工具名（将作为 MCP 工具的 name）
        description: 工具描述（与函数 docstring 共同构成 MCP 工具的 description）
        read_only: readOnlyHint
        destructive: destructiveHint
        idempotent: idempotentHint
        open_world: openWorldHint

    Returns:
        装饰器函数
    """
    annotations = {
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": open_world,
    }

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # 合并函数 docstring 与传入的 description
        doc = inspect.getdoc(func) or ""
        if description and description.strip() and description.strip() not in doc:
            full_description = f"{description.strip()}\n\n{doc}".strip()
        else:
            full_description = doc or description

        # 用占位注解注册 MCP 工具；@mcp.tool 必须在 mcp 实例存在时调用
        # 因此通过延迟绑定到 mcp 的方式在 import 阶段只做包装，
        # 在 set_mcp() 之后由 _flush_pending_registrations 真正完成注册。
        pending_registrations.append((func, name, full_description, annotations))
        return func

    return decorator


# 缓存待注册的函数；在 set_mcp() 之后一次性注册到 FastMCP
pending_registrations = []  # type: ignore[var-annotated]


def flush_pending_registrations() -> None:
    """将所有延迟注册的工具绑定到当前 mcp 实例。"""
    if mcp is None:
        raise RuntimeError("FastMCP instance not set; call set_mcp() first")

    for func, name, full_description, annotations in pending_registrations:
        wrapped = _wrap_with_error_handling(func)
        # 使用 structured_output=False 让 FastMCP 不做严格的输出类型校验，
        # 便于错误处理包装器统一返回字符串（DisconnectedException 等）
        mcp.tool(
            name=name,
            description=full_description,
            annotations=annotations,
            structured_output=False,
        )(wrapped)
    pending_registrations.clear()


def _wrap_with_error_handling(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    包装工具函数，将 DisconnectedException / AimException 转换为字符串返回值。
    保留原函数签名以便 FastMCP 正确推导参数 schema。
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except (DisconnectedException, AimException) as e:
            return map_aim_exception(e)
        except Exception as e:  # noqa: BLE001
            # 兜底：未预期异常也转为可读字符串
            logger.exception("Unexpected error in tool %s", getattr(func, "__name__", func))
            return map_aim_exception(e)

    return wrapper
