---
name: aim-mcp-controller
description: "VEX AIM 机器人 MCP 远程控制助手。提供 MCP 协议下的 AIM 机器人工具调用指引、配置示例、错误处理与常用工作流。在用户提到 MCP / AIM / VEX / 机器人 / 控制机器人 / 远程控制 / 让机器人 / 调用机器人 / 用 AI 控制机器人 / 机器人自然语言 等场景时触发；也适用于 Claude Desktop / Cursor / Cline 等 MCP 客户端接入 VEX AIM 机器人。"
---

# AIM MCP Controller Skill

帮助 AI Agent 在支持 MCP 的客户端（Claude Desktop、Cursor、Cline 等）中**通过自然语言控制 VEX AIM 机器人**。本 Skill 不写代码，而是指导 Agent 选用正确的 MCP 工具与参数完成用户指令。

## 触发条件

满足以下**任一**条件时应启用本 Skill：

- 关键词：**MCP**、**Model Context Protocol**、**AIM**、**VEX**、**机器人**、**Robot**、**vex aim**
- 意图：**控制机器人**、**远程控制**、**让机器人**、**调用机器人**、**用 AI 控制机器人**、**机器人自然语言**、**让 AI 操作机器人**
- 客户端：用户在 **Claude Desktop**、**Cursor**、**Cline** 等 MCP 客户端中
- 工具：工具列表中出现了 `aim_*` 前缀的 MCP 工具
- 任务：抓球、踢球、走到 AprilTag、显示表情、播放声音、读电池、读位置等
- 错误：用户反馈"机器人没反应"、"MCP 连不上"、"工具调用失败"

## MCP 是什么（1 段简介）

**MCP（Model Context Protocol）** 是一个让 LLM 客户端通过统一协议调用工具的标准。本项目把 VEX AIM 机器人的 Python API 包装为 82 个 MCP 工具，Agent 通过 stdio 启动 `aim-mcp-server` 即可"看见"这些工具，并按用户自然语言指令自动选择、组合、调用——无需编写任何 Python 代码。

## 工具总览

按模块分组的 82 个工具，Agent 应**按需选用**而不是一次性塞给用户。

### Motion 运动（16）

| 工具 | 用途 |
| --- | --- |
| `aim_move_at` | 持续朝某方向移动（不自动停） |
| `aim_move_for` | 沿方向移动指定距离（毫米），可阻塞 |
| `aim_move_with_vectors` | 全向向量运动（前进+横向+旋转） |
| `aim_turn` | 持续旋转（LEFT/RIGHT） |
| `aim_turn_for` | 旋转指定角度 |
| `aim_turn_to` | 转向绝对朝向 |
| `aim_stop` | 立即停止 |
| `aim_spin_wheels` | 单独控制三个轮子 |
| `aim_set_move_velocity` / `aim_set_turn_velocity` | 设置默认速度 |
| `aim_set_xy_position` | 设定位姿原点 |
| `aim_get_position` / `aim_get_heading` / `aim_get_rotation` | 读位姿 |
| `aim_set_heading` / `aim_reset_heading` | 写朝向 |

### Vision 视觉（18）

| 工具 | 用途 |
| --- | --- |
| `aim_get_vision_objects` | 关键工具：检测球/桶/Tag，返回带 `centerX`/`bearing` 的列表 |
| `aim_has_sports_ball` / `aim_has_blue_barrel` / `aim_has_orange_barrel` / `aim_has_any_barrel` | 持物判断 |
| `aim_get_camera_image` | 抓帧保存为 JPG |
| `aim_show_vision_on_screen` / `aim_hide_vision_on_screen` | 屏幕显示/隐藏视觉画面 |
| **`aim_set_tag_detection(enable)`** | ⚠️ 开启/关闭 AprilTag 检测。**机器人出厂默认关闭**，使用 `TAG_0~TAG_37` 前必须先 `enable=True` |
| `aim_set_color_detection(enable, merge?)` | 开启/关闭颜色和颜色码对象检测（默认关闭） |
| `aim_set_model_detection(enable)` | 开启/关闭 AI 模型对象检测（球/桶/机器人，默认开启） |
| `aim_scan_for_object` | V1：持续原地旋转扫描直到发现指定类型对象 |
| `aim_estimate_distance_to_object` | V2：启发式测距（`distance_mm ≈ K / width_px`，K 默认 35000） |
| `aim_capture_with_overlay` | V3：抓拍并叠加 AI 检测框 + 标签为 JPG（需 Pillow） |
| `aim_define_color_signature` | V4：定义 1~7 号颜色签名槽位（先于此开 `aim_set_color_detection`） |
| `aim_count_objects` | V5：快速统计各类型对象数量，不返回坐标详情 |
| `aim_get_object_bearing` | V6：轻量版取首个对象的 `bearing`/`centerX`（省 token） |
| `aim_define_color_code` | V7：定义 1~5 号颜色码槽位（由 2~5 个颜色签名组合） |

### Kicker 踢球（2）

| 工具 | 用途 |
| --- | --- |
| `aim_kick` | 踢球，力度 SOFT/MEDIUM/HARD |
| `aim_place` | 轻柔放置前方物体 |

### LED 灯（4）

| 工具 | 用途 |
| --- | --- |
| `aim_set_led` | 颜色或 RGB 数值（受全局亮度倍率缩放） |
| `aim_set_led_brightness` | 设置全局 LED 亮度倍率（0~100） |
| `aim_blink_led` | 闪烁（线程实现） |
| `aim_stop_blink_led` | 停止闪烁线程 |

### Sound 声音（5）

| 工具 | 用途 |
| --- | --- |
| `aim_play_sound` | 内置音效（DOORBELL/TADA/FAIL/SPARKLE 等） |
| `aim_play_note` | 音符（C5、F#6 等） |
| `aim_play_sound_file` | 播放本地 wav/mp3 |
| `aim_stop_sound` | 停止声音 |
| `aim_is_sound_playing` | 是否在播 |

### Screen 屏幕（22）

| 工具 | 用途 |
| --- | --- |
| `aim_print_screen` / `aim_print_at` | 打印文本 |
| `aim_clear_screen` | 清屏 + 背景色 |
| `aim_set_cursor` / `aim_set_pen_color` / `aim_set_fill_color` / `aim_set_pen_width` | 画笔设置 |
| `aim_draw_pixel` / `aim_draw_line` / `aim_draw_rectangle` / `aim_draw_circle` | 基础绘图 |
| `aim_show_emoji` / `aim_hide_emoji` | 表情 |
| `aim_show_battery_gauge` | S1：画电池图标 + 百分比（颜色随电量） |
| `aim_show_emotion_sequence` / `aim_stop_emotion_sequence` | S2：后台线程循环显示表情（可停止） |
| `aim_show_image_file` | S3：从本地加载 bmp/png 并显示 |
| `aim_set_screen_font` | S4：切换字体（`MONO12/15/20/24/30/36/40/60` / `PROP20/24/30/36/40/60`） |
| `aim_clear_row` | S4：清除指定行（可指定背景色） |
| `aim_set_screen_origin` | S5：重新定义屏幕坐标系原点 |
| `aim_set_screen_clip` | S6：限制后续绘图区域（分屏/对话框） |
| `aim_draw_progress_bar` | S7：画水平进度条 + 百分比数字 |

### Sensor 传感器（9）

| 工具 | 用途 |
| --- | --- |
| `aim_get_battery_capacity` | 电池百分比 |
| `aim_get_acceleration` / `aim_get_turn_rate` | IMU 加速度/角速度（X/Y/Z） |
| `aim_get_roll` / `aim_get_pitch` / `aim_get_yaw` | IMU 姿态角 |
| `aim_is_screen_pressed` / `aim_get_touch_x` / `aim_get_touch_y` | 屏幕触摸 |

### Connection 连接（3）

| 工具 | 用途 |
| --- | --- |
| `aim_connect` | 连接到 host（自动断开旧连接） |
| `aim_disconnect` | 断开 |
| `aim_is_connected` | 查询连接状态 |

## 常用工作流

### 1. 简单运动

> 用户：前进 1 米后停下。

```text
1. aim_move_for(distance=1000, direction=0, velocity=50, wait=True)
2. （可选）aim_print_screen(text="done")
```

### 2. 找球并抓取

> 用户：找到球然后抓住。

```text
1. aim_get_vision_objects(object_type="SPORTS_BALL", count=3)
2. 若列表空：aim_turn(direction="LEFT", velocity=30) 旋转扫描，回到步骤 1
3. 取第一个球的 bearing：aim_turn_to(heading=current_heading + bearing, wait=True)
4. aim_move_for(distance=200, direction=0, velocity=40, wait=True)
5. 跳回步骤 1 直到 aim_has_sports_ball() == true
6. （可选）aim_kick(force="MEDIUM")
```

### 3. AprilTag 导航

> 用户：走到 AprilTag 5 旁边。

```text
1. aim_get_vision_objects(object_type="TAG_5", count=1)
2. 若空：aim_turn(direction="LEFT", velocity=30) 旋转 360° 持续扫描
3. aim_turn_to(heading=current_heading + tag[0]["bearing"], wait=True)
4. aim_move_for(distance=150, direction=0, velocity=40, wait=True)
5. 跳回步骤 1，连续 3 次空则停止并提示用户
6. aim_print_screen(text="Reached tag 5")
```

### 4. 屏幕表情

> 用户：显示一个向前看的开心表情。

```text
aim_show_emoji(emoji="HAPPY", look="LOOK_FORWARD")
```

### 5. 播放音符

> 用户：播放 1 秒的 C5 音符。

```text
aim_play_note(note="C5", duration=1000, volume=60)
```

## 错误处理指引

| 工具返回 | 含义 | 建议处理 |
| --- | --- | --- |
| `"机器人未连接。请检查：1) IP 是否正确 2) 是否在同一 Wi-Fi 3) 是否已开机"` | `DisconnectedException` | 调用 `aim_is_connected()` 确认；如未连接则 `aim_connect(host=192.168.x.x)`，提示用户确认机器人电源与 Wi-Fi |
| `"未预期错误: ..."` | 未捕获异常 | 提示用户检查终端 MCP Server 日志（`~/Library/Logs/Claude/`），可能需要重启 MCP |
| `"亮度值 X 超出 0~100 范围"` / `"RGB 分量必须都在 0~255 范围"` | 参数越界 | Agent 应自动修正参数（如截断到 0~100），再次调用 |
| `"不支持的 object_type: ..."` | vision 类型拼写错误 | 改成 `SPORTS_BALL` / `BLUE_BARREL` / `ORANGE_BARREL` / `AIM_ROBOT` / `TAG_0`~`TAG_37` / `ALL_TAGS` / `ALL_OBJECTS` / `ALL_COLORS` / `ALL_CARGO` |
| 运动命令长时间无返回 | 阻塞等待中（`wait=True`） | 正常行为；如想异步执行可改 `wait=False` |
| `aim_get_vision_objects(object_type="TAG_5")` 持续返回 `[]` 而球能识别 | ⚠️ **AprilTag 检测未开启**（机器人出厂默认关闭） | **必须**先调用 `aim_set_tag_detection(enable=True)`，再重新检测。球/桶走的是 AI 模型检测（默认开），Tag 走的是独立的 tag 处理（默认关） |
| 视觉连续多次返回空 | 光线/距离/角度问题 | 提示用户：1) 开灯（提高环境光）；2) 调整机器人角度；3) 确认目标在画面中 |
| `aim_kick` 报错 | Kicker 状态异常 | 调用 `aim_stop_sound()` 复位后重试，或提示用户重启机器人 |
| `aim_get_battery_capacity` < 20 | 电池低 | 立即停止危险操作（踢球、长时间前进），提示用户充电 |
| `"端口无效: 端口号超出合法范围 [1, 65535], 收到: 0"` | `aim_set_port` 或 `aim_connect` 端口越界 | 改用 1-65535 之间的合法端口；如不确定用 `aim_get_effective_port()` 查询默认值 |

## MCP 配置示例（Claude Desktop）

`~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "aim": {
      "command": "<repo-root>/.venv/bin/aim-mcp-server",
      "env": {
        "AIM_ROBOT_HOST": "192.168.1.100",
        "AIM_ROBOT_PORT": "80"
      }
    }
  }
}
```

Cursor 项目级配置（`.cursor/mcp.json`）格式相同。

## 决策原则

1. **优先只读探测**：拿到一个任务时，先用 `aim_get_position` / `aim_get_heading` / `aim_get_vision_objects` / `aim_get_battery_capacity` 探查当前状态，再决定动作。
2. **小步快跑**：运动类任务建议拆成多次短距移动（≤300mm）+ 重新视觉检测，避免一次性下达大距离导致丢失目标。
3. **安全第一**：每次动作前确认 `aim_get_battery_capacity()` 充足；任何写操作（kick / set_xy / reset_heading）前打印提示到屏幕（`aim_print_screen`）。
4. **失败可恢复**：所有写操作失败时，调用 `aim_stop` + `aim_disconnect` + `aim_connect` 重建一次连接，再重试一次。
5. **不超范围**：参数校验类错误由 Agent 自动修正（如颜色名、坐标范围），不要把错误原文原样回给用户。

## 相关资源

- [MCP 协议规范](https://modelcontextprotocol.io/)
- `aim_mcp_server/README.md` — 安装、运行、配置详解
- `docs/aim-mcp-architecture.md` — 架构设计文档
- `skills/vex-aim-programming/SKILL.md` — 编写 AIM Python 代码的辅助 Skill（互补关系）
