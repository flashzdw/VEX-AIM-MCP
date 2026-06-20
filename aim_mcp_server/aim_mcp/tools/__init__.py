"""
AIM MCP Server - tools 包

通过集中导入触发所有工具模块的注册（@mcp.tool 装饰器在 import 时立即执行）。
"""

from . import motion  # noqa: F401
from . import vision  # noqa: F401
from . import kicker  # noqa: F401
from . import led  # noqa: F401
from . import sound  # noqa: F401
from . import screen_tools  # noqa: F401
from . import sensors  # noqa: F401
from . import connection_tools  # noqa: F401
