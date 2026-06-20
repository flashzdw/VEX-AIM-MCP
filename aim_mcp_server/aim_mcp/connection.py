"""
AIM MCP Server - Robot 连接管理器

封装 VEX AIM 库的 Robot 单例，提供延迟初始化、连接/断开、错误映射等能力。

## 端口处理

VEX AIM 库的 `Robot(host)` 内部将 WebSocket URI 硬编码为
`ws://{host}/{ws_name}`（默认端口 80）。本管理器通过将端口拼接到 host 字符串
（`host:port` 形式）来支持自定义端口，无需修改 vex 库本身。

例如：
- `Robot("192.168.1.100")`        → `ws://192.168.1.100/ws_status`（端口 80）
- `Robot("192.168.1.100:8080")`   → `ws://192.168.1.100:8080/ws_status`（端口 8080）
"""

import os
import threading
from typing import Optional

from vex import Robot, DisconnectedException, AimException
from vex.settings import Settings


# WebSocket 默认端口（与 `ws://` URL 一致）
DEFAULT_AIM_PORT = 80

# 端口取值范围
_MIN_PORT = 1
_MAX_PORT = 65535


# ----------------------------------------------------------------------
# 错误映射
# ----------------------------------------------------------------------
def map_aim_exception(e: Exception) -> str:
    """
    将 VEX AIM 库抛出的异常映射为对 AI Agent 友好的中文错误描述。
    """
    if isinstance(e, DisconnectedException):
        return (
            "机器人未连接。请检查："
            "1) 机器人 IP 是否正确 "
            "2) 机器人与本机是否在同一 Wi-Fi 网络 "
            "3) 机器人是否已开机 "
            "4) WebSocket 端口是否正确（默认 80）"
        )
    if isinstance(e, AimException):
        return str(e)
    return f"未预期错误: {type(e).__name__}: {e}"


# ----------------------------------------------------------------------
# 端口工具
# ----------------------------------------------------------------------
def _validate_port(port: Optional[int]) -> Optional[int]:
    """
    校验端口号；通过返回端口值本身，失败抛出 ValueError。
    """
    if port is None:
        return None
    if not isinstance(port, int) or isinstance(port, bool):
        raise ValueError(f"端口必须是整数，收到: {type(port).__name__}")
    if not (_MIN_PORT <= port <= _MAX_PORT):
        raise ValueError(
            f"端口号超出合法范围 [{_MIN_PORT}, {_MAX_PORT}]，收到: {port}"
        )
    return port


def _build_host_string(host: str, port: Optional[int]) -> str:
    """
    根据 host 和 port 构造 Robot 所需的 host 字符串。

    - 若 host 本身已包含端口（形如 `1.2.3.4:8080`），原样使用
    - 若提供了 port 且 host 不含端口，则拼接为 `host:port`
    - 若端口为 80（默认）且 host 不含端口，保持 host 原样以保留旧行为
    """
    # host 本身已含端口（出现 ":" 且不是 IPv6 形式）
    if ":" in host and not host.startswith("["):
        return host
    if port is None or port == DEFAULT_AIM_PORT:
        return host
    return f"{host}:{port}"


# ----------------------------------------------------------------------
# Robot 单例管理器
# ----------------------------------------------------------------------
class RobotManager:
    """
    Robot 单例管理器。

    - **延迟初始化**：首次调用 `get_robot()` 时才创建 Robot 实例；
      若 host 为空则优先使用 `AIM_ROBOT_HOST` 环境变量，否则使用 `settings.json` 默认值。
    - **端口可配置**：通过 `connect(host, port)`、`set_port()` 或环境变量 `AIM_ROBOT_PORT` 设置。
    - **线程安全**：通过自旋锁保证多线程下只创建一个实例。
    """

    def __init__(self) -> None:
        self.host: Optional[str] = None
        self.port: Optional[int] = None  # None 表示使用默认 80
        self._robot: Optional[Robot] = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------
    def _resolve_host(self) -> str:
        """解析最终的 host 字符串（不含端口）。"""
        host = self.host
        if not host:
            host = os.environ.get("AIM_ROBOT_HOST")
        if not host:
            host = Settings().host
        self.host = host
        return host

    def _resolve_port(self) -> Optional[int]:
        """解析最终的端口值（host 字段本身含端口时返回 None）。"""
        if self.port is not None:
            return self.port
        env_port = os.environ.get("AIM_ROBOT_PORT")
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                # 无效值忽略，使用默认
                pass
        return None

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------
    def get_robot(self) -> Robot:
        """
        获取当前 Robot 实例；未初始化时延迟创建。

        Raises:
            DisconnectedException: 创建/连接失败时抛出
        """
        if self._robot is not None:
            return self._robot

        with self._lock:
            if self._robot is not None:
                return self._robot

            host = self._resolve_host()
            port = self._resolve_port()
            full_host = _build_host_string(host, port)

            try:
                self._robot = Robot(full_host)
            except SystemExit as e:
                self._robot = None
                port_info = f":{port}" if port and port != DEFAULT_AIM_PORT else ""
                raise DisconnectedException(
                    f"无法连接到 AIM 机器人 {host}{port_info}：底层连接超时（exit code={e.code}）"
                ) from e
            return self._robot

    def connect(self, host: str, port: Optional[int] = None) -> str:
        """
        断开旧连接，连接到新的 host（可指定端口）。

        Args:
            host: 机器人 IP / 主机名
            port: WebSocket 端口（None 表示使用 80 默认；范围 1-65535）

        Returns:
            成功信息字符串
        """
        # 提前校验端口，失败时不让旧连接被错误断开
        validated = _validate_port(port)
        self.disconnect()
        self.host = host
        self.port = validated
        self.get_robot()  # 触发实际连接
        return self._connection_summary()

    def disconnect(self) -> str:
        """关闭并清理当前 Robot 实例。"""
        if self._robot is None:
            return "机器人未连接，无需断开"
        try:
            try:
                self._robot.exit_handler()
            except Exception:
                pass
        finally:
            self._robot = None
        return "已断开与 AIM 机器人的连接"

    def is_connected(self) -> bool:
        """返回当前是否已建立连接。"""
        return self._robot is not None

    def get_port(self) -> Optional[int]:
        """返回当前显式设置的端口（None 表示使用默认 80）。"""
        return self.port

    def set_port(self, port: Optional[int]) -> str:
        """
        修改端口设置。**不会自动重连**，下次 `get_robot()` 或 `connect()` 时生效。
        若已连接，会先断开。

        Args:
            port: 新的端口号；传入 None 恢复默认（80）
        """
        validated = _validate_port(port)
        was_connected = self._robot is not None
        if was_connected:
            self.disconnect()
        self.port = validated
        if was_connected:
            return f"端口已更新为 {validated or DEFAULT_AIM_PORT}（默认），旧连接已断开，请调用 aim_connect 重新连接"
        return f"端口已更新为 {validated or DEFAULT_AIM_PORT}（默认），将在下次连接时生效"

    def get_effective_port(self) -> int:
        """返回实际生效的端口（考虑了环境变量和默认）。"""
        if self.port is not None:
            return self.port
        env_port = os.environ.get("AIM_ROBOT_PORT")
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                pass
        return DEFAULT_AIM_PORT

    def _connection_summary(self) -> str:
        """生成人类可读的当前连接摘要。"""
        port_str = (
            f":{self.get_effective_port()}"
            if self.get_effective_port() != DEFAULT_AIM_PORT
            else ""
        )
        return f"已连接到 AIM 机器人 {self.host}{port_str}"


# 全局单例
robot_manager = RobotManager()
