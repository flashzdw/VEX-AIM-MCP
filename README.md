# VEX AIM 测试项目

VEX AIM 机器人开发与 AI Agent 集成工作区。

## 子项目

| 目录 | 用途 | 文档 |
|------|------|------|
| [`src/`](./src) | VEXcode USB 模式代码（运行在 Brain 上） | — |
| [`websocket/`](./websocket) | WebSocket 远程编程工作区（运行在 PC 上） | [README](./websocket/README.md) |
| [`aim_mcp_server/`](./aim_mcp_server) | **MCP 服务器**：让 AI Agent 通过 MCP 控制 AIM 机器人（61 工具 + 3 资源 + 3 工作流） | [README](./aim_mcp_server/README.md) |

## AI Agent 集成

通过 [aim-mcp-server](./aim_mcp_server) 任何支持 MCP 的 AI Agent（Claude Desktop、Cursor、Cline 等）都能直接控制 AIM 机器人：

```bash
# 安装
source aim_mcp_venv/bin/activate
pip install -e websocket/AIM_Websocket_Library
pip install -e aim_mcp_server

# 运行 MCP 服务器
aim-mcp-server
```

配置示例见 [aim_mcp_server/claude_desktop_config.json](./aim_mcp_server/claude_desktop_config.json)。

## 配套 Skill

- [`.TRAE/skills/aim-mcp-controller/SKILL.md`](./.TRAE/skills/aim-mcp-controller/SKILL.md) — AI Agent 使用指南
- [`.TRAE/skills/vex-aim-programming/SKILL.md`](./.TRAE/skills/vex-aim-programming/SKILL.md) — VEX AIM 编程参考

## 架构文档

- [`.TRAE/documents/aim-mcp-architecture.md`](./.TRAE/documents/aim-mcp-architecture.md) — MCP 服务器架构（Mermaid 图）
- [`.TRAE/documents/voice-chat-architecture.md`](./.TRAE/documents/voice-chat-architecture.md) — 语音对话架构
