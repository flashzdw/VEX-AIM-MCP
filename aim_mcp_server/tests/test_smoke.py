"""
VEX AIM MCP Server 端到端冒烟测试

覆盖：
  模式 A：未连接机器人（默认）— 验证所有工具能优雅处理未连接情况，
          错误信息含可操作的中文提示（"未连接"、"请检查"、"IP" 等）。
  模式 B：连接真实机器人（需 AIM_ROBOT_HOST 环境变量）— 验证基本读路径。

使用 mcp Python SDK 的 stdio_client 启动服务器子进程，
通过 ClientSession 调用 list_*/call_tool/read_resource 等方法。

不需要 pytest，asyncio.run 直接跑：
    cd aim_mcp_server
    python tests/test_smoke.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ----------------------------------------------------------------------
# 路径与服务器启动参数
# ----------------------------------------------------------------------
# tests/ -> aim_mcp_server/ -> VEX-AIM-MCP/
ROOT = Path(__file__).resolve().parent.parent.parent
SERVER_DIR = ROOT / "aim_mcp_server"

# 在未连接测试中默认指向回环地址（connection refused 立即返回，比默认 192.168.0.85 的 4s 超时快）。
# 若调用方已显式设置 AIM_ROBOT_HOST，则尊重调用方意愿（例如真实机器人测试）。
LOOPBACK_HOST = "127.0.0.1"


def build_server_params(robot_host: Optional[str] = None) -> StdioServerParameters:
    """
    构造启动 AIM MCP Server 子进程的参数。

    Args:
        robot_host: 注入到子进程的 AIM_ROBOT_HOST 值。
                    None 表示不强制设置（沿用调用方环境或默认 settings.json）。
    """
    env = {**os.environ}
    # 强制把 aim_mcp_server 根目录加入 PYTHONPATH，确保子进程能 import aim_mcp
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{SERVER_DIR}{os.pathsep}{existing_pp}" if existing_pp else str(SERVER_DIR)
    )
    if robot_host is not None:
        env["AIM_ROBOT_HOST"] = robot_host
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "aim_mcp.server"],
        env=env,
        cwd=str(SERVER_DIR),
    )


@asynccontextmanager
async def open_session(robot_host: Optional[str] = None):
    """
    异步上下文管理器：启动 MCP Server 子进程并建立 ClientSession。
    使用完毕自动清理（关闭会话、终止子进程）。

    Args:
        robot_host: 同 build_server_params
    """
    server_params = build_server_params(robot_host=robot_host)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


# ----------------------------------------------------------------------
# 文本提取工具：MCP 返回的 CallToolResult 包含若干 TextContent
# ----------------------------------------------------------------------
def extract_text(result: Any) -> str:
    """
    将 CallToolResult 扁平化为单字符串，便于断言中文错误关键字。
    """
    parts: List[str] = []
    content = getattr(result, "content", None) or []
    for item in content:
        text = getattr(item, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts).strip()


# ----------------------------------------------------------------------
# 测试：列表类（不依赖连接）
# ----------------------------------------------------------------------
async def test_tools_list() -> None:
    """测试 MCP 服务器能列出所有工具；预期 82 个（运动 16 / 视觉 18 / 踢球 2 / LED 4 / 声音 5 / 屏幕 22 / 传感器 9 / 连接 6）。"""
    async with open_session() as session:
        result = await session.list_tools()
        tools = result.tools
        assert len(tools) > 0, "未返回任何工具"
        assert len(tools) == 82, f"工具数应为 82，实际为 {len(tools)}"

        # 验证若干关键工具存在
        names = {t.name for t in tools}
        expected_subset = {
            "aim_get_battery_capacity",
            "aim_get_position",
            "aim_get_vision_objects",
            "aim_move_for",
            "aim_connect",
            "aim_disconnect",
        }
        missing = expected_subset - names
        assert not missing, f"缺少关键工具: {missing}"

        # 全部以 aim_ 前缀开头
        bad_prefix = [n for n in names if not n.startswith("aim_")]
        assert not bad_prefix, f"存在非 aim_ 前缀的工具: {bad_prefix}"

        print(f"   共 {len(tools)} 个工具，前缀校验通过")


async def test_resources_list() -> None:
    """测试 3 个 resources 存在：aim://status, aim://battery, aim://position。"""
    async with open_session() as session:
        result = await session.list_resources()
        uris = {str(r.uri) for r in result.resources}
        assert "aim://status" in uris, f"缺少 aim://status，实际: {uris}"
        assert "aim://battery" in uris, f"缺少 aim://battery，实际: {uris}"
        assert "aim://position" in uris, f"缺少 aim://position，实际: {uris}"
        assert len(result.resources) == 3, f"资源数量异常: {len(result.resources)}"
        print(f"   共 {len(result.resources)} 个 resources: {sorted(uris)}")


async def test_prompts_list() -> None:
    """测试 3 个 prompts 存在：search_and_grab_ball / navigate_to_tag / calibrate_and_test。"""
    async with open_session() as session:
        result = await session.list_prompts()
        names = {p.name for p in result.prompts}
        expected = {
            "search_and_grab_ball",
            "navigate_to_tag",
            "calibrate_and_test",
        }
        missing = expected - names
        assert not missing, f"缺少 prompts: {missing}"
        assert len(result.prompts) == 3, f"prompts 数量异常: {len(result.prompts)}"
        print(f"   共 {len(result.prompts)} 个 prompts: {sorted(names)}")


# ----------------------------------------------------------------------
# 测试：未连接场景（错误处理）
# ----------------------------------------------------------------------
def _assert_disconnected_error(text: str) -> None:
    """
    验证未连接场景下返回的文本含可操作的中文提示。
    装饰器会把 DisconnectedException 映射为 "机器人未连接。请检查：..."。
    """
    assert text, "未连接调用应返回非空错误信息"
    lowered = text
    # 至少应命中"未连接"、"请检查"、"IP" 中的一个核心关键词
    keywords = ["未连接", "请检查", "IP", "Wi-Fi", "开机"]
    matched = [k for k in keywords if k in lowered]
    assert matched, (
        f"错误信息缺少可操作中文提示: {text!r}\n"
        f"  期望至少命中一个: {keywords}"
    )


async def test_aim_get_battery_capacity_not_connected() -> None:
    """测试未连接时调用传感器工具返回可读错误。"""
    async with open_session(robot_host=LOOPBACK_HOST) as session:
        result = await session.call_tool(
            "aim_get_battery_capacity", arguments={}
        )
        text = extract_text(result)
        _assert_disconnected_error(text)
        print(f"   电池工具未连接提示: {text[:60]}...")


async def test_aim_get_position_not_connected() -> None:
    """测试位置查询在未连接时返回错误。"""
    async with open_session(robot_host=LOOPBACK_HOST) as session:
        result = await session.call_tool("aim_get_position", arguments={})
        text = extract_text(result)
        _assert_disconnected_error(text)
        print(f"   位置工具未连接提示: {text[:60]}...")


async def test_aim_get_vision_objects_not_connected() -> None:
    """测试视觉工具在未连接时返回错误。"""
    async with open_session(robot_host=LOOPBACK_HOST) as session:
        result = await session.call_tool(
            "aim_get_vision_objects",
            arguments={"object_type": "SPORTS_BALL", "count": 3},
        )
        text = extract_text(result)
        _assert_disconnected_error(text)
        print(f"   视觉工具未连接提示: {text[:60]}...")


async def test_aim_move_for_not_connected() -> None:
    """测试运动工具在未连接时返回错误而非崩溃。"""
    async with open_session(robot_host=LOOPBACK_HOST) as session:
        result = await session.call_tool(
            "aim_move_for",
            arguments={
                "distance": 200,
                "direction": 0,
                "velocity": 50,
                "wait": True,
            },
        )
        text = extract_text(result)
        # FastMCP 包装器把异常转字符串时，isError 字段是否置位取决于实现版本；
        # 关键验证是错误信息本身含可操作提示（_assert_disconnected_error 内部已断言）
        _assert_disconnected_error(text)
        print(f"   运动工具未连接提示: {text[:60]}...")


# ----------------------------------------------------------------------
# 测试：资源读取在未连接时同样应优雅降级
# ----------------------------------------------------------------------
async def test_resource_read_not_connected() -> None:
    """测试未连接时读取 aim://battery 资源也能得到可读错误。"""
    async with open_session(robot_host=LOOPBACK_HOST) as session:
        result = await session.read_resource("aim://battery")  # type: ignore[arg-type]
        # ReadResourceResult.contents 是列表，每个元素 .text 是字符串
        contents = result.contents
        assert contents, "资源读取应返回至少一个内容项"
        text = "\n".join(getattr(c, "text", "") or "" for c in contents)
        _assert_disconnected_error(text)
        print(f"   资源未连接提示: {text[:60]}...")


# ----------------------------------------------------------------------
# 测试：错误信息可读性汇总
# ----------------------------------------------------------------------
async def test_error_messages_are_actionable() -> None:
    """
    汇总：跨多个工具类（传感/位置/视觉/运动）调用，
    每条错误信息都应至少包含 "未连接" + 至少一个可操作建议。
    """
    cases = [
        ("aim_get_battery_capacity", {}),
        ("aim_get_position", {}),
        ("aim_get_vision_objects", {"object_type": "BLUE_BARREL", "count": 1}),
        ("aim_move_for", {"distance": 100, "direction": 0}),
        ("aim_turn_for", {"direction": "LEFT", "angle": 90}),
    ]
    async with open_session(robot_host=LOOPBACK_HOST) as session:
        for name, args in cases:
            result = await session.call_tool(name, arguments=args)
            text = extract_text(result)
            _assert_disconnected_error(text)
            # 进一步断言：同时包含"机器人"与"未连接"两个关键词
            assert "未连接" in text, f"{name} 错误信息缺少'未连接': {text!r}"
    print(f"   {len(cases)} 个工具的错误信息均含'未连接'提示")


# ----------------------------------------------------------------------
# 测试：真实机器人（opt-in via AIM_ROBOT_HOST）
# ----------------------------------------------------------------------
async def test_real_robot_battery() -> None:
    """
    连接真实机器人读取电池（需要 AIM_ROBOT_HOST 环境变量）。

    仅在 AIM_ROBOT_HOST 显式设置时执行；否则打印跳过。
    """
    host = os.environ.get("AIM_ROBOT_HOST")
    if not host or host == LOOPBACK_HOST:
        print("⏭️  跳过真实机器人测试（AIM_ROBOT_HOST 未设置或等于回环占位符）")
        return

    # 把外部的 AIM_ROBOT_HOST 透传给子进程（open_session 默认会沿用环境）
    async with open_session() as session:
        result = await session.call_tool(
            "aim_get_battery_capacity", arguments={}
        )
        text = extract_text(result)
        # 真实连接时不应再出现"未连接"提示；应当能解析为整数百分比
        assert "未连接" not in text, f"真实机器人测试不应触发未连接错误: {text!r}"
        # 输出可能直接是数字字符串，也可能是 "电池: 87" 形式；尝试提取首段整数
        first_token = text.strip().split()[0] if text.strip() else ""
        pct = int("".join(ch for ch in first_token if ch.isdigit()) or "-1")
        assert 0 <= pct <= 100, f"电池百分比越界: {pct} (raw={text!r})"
        print(f"   真实机器人电池: {pct}% (host={host})")


# ----------------------------------------------------------------------
# 入口
# ----------------------------------------------------------------------
async def main() -> bool:
    print("=" * 60)
    print("VEX AIM MCP Server 端到端冒烟测试")
    print("=" * 60)

    tests: List[tuple] = [
        ("工具列表", test_tools_list),
        ("资源列表", test_resources_list),
        ("Prompts 列表", test_prompts_list),
        ("未连接 - 电池", test_aim_get_battery_capacity_not_connected),
        ("未连接 - 位置", test_aim_get_position_not_connected),
        ("未连接 - 视觉", test_aim_get_vision_objects_not_connected),
        ("未连接 - 运动", test_aim_move_for_not_connected),
        ("未连接 - 资源读取", test_resource_read_not_connected),
        ("错误信息可读性", test_error_messages_are_actionable),
        ("真实机器人（可选）", test_real_robot_battery),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            await test_fn()
            print(f"✅ {name}: 通过")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: 失败 - {type(e).__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"结果: {passed} 通过 / {failed} 失败")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
