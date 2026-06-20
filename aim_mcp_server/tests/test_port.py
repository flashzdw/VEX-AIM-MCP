"""
AIM MCP Server - 端口处理单元测试

覆盖：
1. _validate_port：端口校验（None / 合法 / 越界 / 类型错误）
2. _build_host_string：host 与 port 拼接
3. RobotManager：port 字段读写、get_effective_port
4. AIM_ROBOT_PORT 环境变量支持
5. aim_connect / aim_set_port / aim_get_port 工具签名
"""

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "aim_mcp"))


class TestValidatePort(unittest.TestCase):
    """_validate_port 函数测试"""

    def setUp(self):
        from connection import _validate_port
        self.fn = _validate_port

    def test_none_is_valid(self):
        """None 应该透传（表示使用默认）"""
        self.assertIsNone(self.fn(None))

    def test_valid_ports(self):
        """合法端口 1-65535 都应通过"""
        for port in [1, 80, 443, 8080, 65535]:
            self.assertEqual(self.fn(port), port)

    def test_below_range(self):
        """端口 0 或负数应抛 ValueError"""
        for port in [0, -1, -100]:
            with self.assertRaises(ValueError):
                self.fn(port)

    def test_above_range(self):
        """端口 > 65535 应抛 ValueError"""
        for port in [65536, 100000]:
            with self.assertRaises(ValueError):
                self.fn(port)

    def test_wrong_type(self):
        """非整数应抛 ValueError（bool 也是 int 实例，需排除）"""
        for port in ["80", 80.5, [80], None]:
            if port is None:
                continue
            with self.assertRaises(ValueError):
                self.fn(port)

    def test_bool_rejected(self):
        """Python 中 bool 是 int 的子类，必须显式排除"""
        with self.assertRaises(ValueError):
            self.fn(True)
        with self.assertRaises(ValueError):
            self.fn(False)


class TestBuildHostString(unittest.TestCase):
    """_build_host_string 函数测试"""

    def setUp(self):
        from connection import _build_host_string
        self.fn = _build_host_string

    def test_default_port(self):
        """默认端口（None 或 80）保持 host 原样"""
        self.assertEqual(self.fn("192.168.1.100", None), "192.168.1.100")
        self.assertEqual(self.fn("192.168.1.100", 80), "192.168.1.100")

    def test_custom_port(self):
        """非默认端口应拼接"""
        self.assertEqual(self.fn("192.168.1.100", 8080), "192.168.1.100:8080")
        self.assertEqual(self.fn("aim.local", 443), "aim.local:443")

    def test_host_already_has_port(self):
        """host 自身已包含端口时不再拼接"""
        self.assertEqual(self.fn("192.168.1.100:8080", 443), "192.168.1.100:8080")
        self.assertEqual(self.fn("192.168.1.100:8080", None), "192.168.1.100:8080")


class TestRobotManagerPort(unittest.TestCase):
    """RobotManager 端口相关方法测试（不连真实机器人）"""

    def setUp(self):
        # 避免污染全局单例，新建一个 manager
        from connection import RobotManager, DEFAULT_AIM_PORT
        self.mgr = RobotManager()
        self.default_port = DEFAULT_AIM_PORT

    def test_initial_port_is_none(self):
        """初始状态 port 应为 None（使用默认）"""
        self.assertIsNone(self.mgr.port)
        self.assertIsNone(self.mgr.get_port())

    def test_get_effective_port_default(self):
        """未设置时 effective port 应为默认值 80"""
        # 确保没有 AIM_ROBOT_PORT 环境变量
        env_orig = os.environ.pop("AIM_ROBOT_PORT", None)
        try:
            self.assertEqual(self.mgr.get_effective_port(), self.default_port)
        finally:
            if env_orig is not None:
                os.environ["AIM_ROBOT_PORT"] = env_orig

    def test_set_port_valid(self):
        """set_port 应正确更新 port 字段"""
        result = self.mgr.set_port(8080)
        self.assertEqual(self.mgr.port, 8080)
        self.assertEqual(self.mgr.get_port(), 8080)
        self.assertEqual(self.mgr.get_effective_port(), 8080)
        self.assertIn("8080", result)

    def test_set_port_none_resets_to_default(self):
        """set_port(None) 应恢复默认"""
        self.mgr.set_port(8080)
        self.mgr.set_port(None)
        self.assertIsNone(self.mgr.port)
        self.assertEqual(self.mgr.get_effective_port(), self.default_port)

    def test_set_port_invalid_raises(self):
        """set_port 越界值应抛 ValueError"""
        with self.assertRaises(ValueError):
            self.mgr.set_port(0)
        with self.assertRaises(ValueError):
            self.mgr.set_port(70000)
        with self.assertRaises(ValueError):
            self.mgr.set_port("not_a_number")

    def test_env_var_used_when_no_explicit_port(self):
        """AIM_ROBOT_PORT 环境变量在未显式设置 port 时生效"""
        env_orig = os.environ.get("AIM_ROBOT_PORT")
        os.environ["AIM_ROBOT_PORT"] = "9090"
        try:
            mgr = self.__class__.setUp.__self__(None) if False else None
            # 简单方式：直接建新 manager
            from connection import RobotManager
            mgr = RobotManager()
            self.assertEqual(mgr.get_effective_port(), 9090)
        finally:
            if env_orig is None:
                os.environ.pop("AIM_ROBOT_PORT", None)
            else:
                os.environ["AIM_ROBOT_PORT"] = env_orig

    def test_explicit_port_overrides_env(self):
        """显式设置的 port 优先于环境变量"""
        env_orig = os.environ.get("AIM_ROBOT_PORT")
        os.environ["AIM_ROBOT_PORT"] = "9090"
        try:
            from connection import RobotManager
            mgr = RobotManager()
            mgr.set_port(1234)
            self.assertEqual(mgr.get_effective_port(), 1234)
        finally:
            if env_orig is None:
                os.environ.pop("AIM_ROBOT_PORT", None)
            else:
                os.environ["AIM_ROBOT_PORT"] = env_orig

    def test_invalid_env_var_ignored(self):
        """AIM_ROBOT_PORT 取值非法时回退到默认"""
        env_orig = os.environ.get("AIM_ROBOT_PORT")
        os.environ["AIM_ROBOT_PORT"] = "not_a_number"
        try:
            from connection import RobotManager
            mgr = RobotManager()
            self.assertEqual(mgr.get_effective_port(), self.default_port)
        finally:
            if env_orig is None:
                os.environ.pop("AIM_ROBOT_PORT", None)
            else:
                os.environ["AIM_ROBOT_PORT"] = env_orig


class TestConnectionToolSignatures(unittest.TestCase):
    """aim_connect / aim_set_port / aim_get_port 工具签名测试"""

    def test_aim_connect_accepts_port(self):
        """aim_connect 签名应接受可选 port 参数"""
        from aim_mcp.tools.connection_tools import aim_connect
        import inspect
        sig = inspect.signature(aim_connect)
        params = sig.parameters
        self.assertIn("host", params)
        self.assertIn("port", params)
        # port 应有默认值 None
        self.assertIsNone(params["port"].default)

    def test_aim_set_port_signature(self):
        from aim_mcp.tools.connection_tools import aim_set_port
        import inspect
        sig = inspect.signature(aim_set_port)
        self.assertIn("port", sig.parameters)
        self.assertIsNone(sig.parameters["port"].default)

    def test_aim_get_port_signature(self):
        from aim_mcp.tools.connection_tools import aim_get_port
        import inspect
        sig = inspect.signature(aim_get_port)
        self.assertEqual(len(sig.parameters), 0)


if __name__ == "__main__":
    # 确保当前目录是 tests/ 父目录，使 `import connection` 可用
    os.chdir(ROOT)
    unittest.main(verbosity=2)
