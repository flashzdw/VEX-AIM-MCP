"""
AIM MCP Server - 入口模块

构造 FastMCP 实例，注册所有 tools / resources / prompts，
并通过 mcp.run() 启动 stdio 传输。
"""

from mcp.server.fastmcp import FastMCP

from .tools._decorators import set_mcp, flush_pending_registrations
from . import resources, prompts

# 1. 创建 FastMCP 实例
mcp = FastMCP("aim-mcp-server")

# 2. 注入到装饰器工厂，供工具模块使用
set_mcp(mcp)

# 3. 导入 tools 包（触发所有 @register_tool 装饰器，将函数加入待注册队列）
from . import tools  # noqa: E402, F401

# 4. 将待注册工具真正绑定到 mcp
flush_pending_registrations()

# 5. 注册 resources 和 prompts（其装饰器在导入时立即执行）
resources.register_all(mcp)
prompts.register_all(mcp)


def main() -> None:
    """Console script 入口：使用 stdio 传输启动 MCP 服务器。"""
    mcp.run()


if __name__ == "__main__":
    main()
