---
name: vex-aim-programming
description: "VEX AIM 机器人编程全功能助手。提供 AI Vision API 参考、Python 代码生成、WebSocket 远程编程、环境配置、竞赛策略等全方位支持。在用户编写 VEX AIM 代码、询问 API 用法、配置开发环境、设计竞赛策略或排查机器人问题时调用。"
---

# VEX AIM Programming Skill

VEX AIM 编程全功能助手，覆盖从零基础按键编程到大学 AI 课程的完整编程路径。

## 触发条件

当用户提及以下任一关键词或场景时，应调用此 Skill：
- "VEX AIM"、"AIM 机器人"、"VEX 机器人"
- "AI Vision Sensor"、"视觉检测"、"AprilTag"
- "VEXcode AIM"、"Blocks 编程"、"Python 机器人"
- "WebSocket 远程编程"、"机器人 Wi-Fi 连接"
- "Message Link"、"机器人间通信"
- "STEM Labs"、"AIM 课程"、"竞赛策略"
- 需要编写 AIM 机器人控制代码
- 需要配置 AIM 开发环境

## 知识体系

### 编程路径（五级渐进）

```
按键编程 ──► Blocks 图形化 ──► Switch 混合 ──► Python 文本 ──► WebSocket 远程
(零基础)      (可视化逻辑)      (过渡桥接)      (代码编程)      (高级AI集成)
```

### 核心概念速查

| 概念 | 说明 |
|------|------|
| **AI Vision Sensor** | 预训练视觉模型：SPORTS_BALL, BLUE_BUCKET, RED_BUCKET, AIM_ROBOT + AprilTag 36h11 (ID 0-36) + 7 个自定义颜色签名 |
| **Macro** | 15+ 预构建视觉行为函数，封装完整视觉-运动闭环 |
| **WebSocket** | 通过 Wi-Fi 将 PC 作为"外脑"，实时流式控制机器人 |
| **Message Link** | 蓝牙机器人间通信，仅 VEXcode 本地模式可用 |
| **8 个程序槽位** | Brain 可存储 8 个独立程序 |

### AI Vision Sensor 规格

| 参数 | 规格 |
|------|------|
| 分辨率 | 320 × 240 像素 |
| 帧率 | ~30 FPS |
| 视场角 | 约 60°（水平）|
| 检测类型 | 物体检测 / AprilTag / 颜色签名 / 颜色码 |
| 标签标准 | AprilTag 36h11 家族 (ID 0-36) |
| 连接接口 | SPI 总线 |

### AI Vision 影响因素

- 环境光线（强光/弱光/不均匀光照降低置信度）
- 物体距离（太远太小，太近超出视野）
- 物体角度（侧向/倾斜降低检测率）
- 背景干扰（复杂背景可能误检）
- 运动模糊（高速运动时帧间模糊）
- 遮挡（部分遮挡降低 score 或无法检测）

## API 使用指南

### 核心检测模式

```python
# 模式1：检查是否存在
vision_data = robot.vision.get_data(SPORTS_BALL)
if vision_data[0].exists:
    print("检测到目标！")

# 模式2：遍历多个检测结果
all_balls = robot.vision.get_data(SPORTS_BALL, count=5)
for i, obj in enumerate(all_balls):
    if obj.exists:
        print(f"球{i}: bearing={obj.bearing}, score={obj.score}")

# 模式3：多类型同时检测
balls = robot.vision.get_data(SPORTS_BALL, count=3)
tags = robot.vision.get_data(ALL_TAGS, count=5)
```

### 利用 bearing 做精确转向

bearing 的正负表示目标在机器人的左侧还是右侧：
- `bearing > 0`：目标在右侧 → `robot.turn(RIGHT)`
- `bearing < 0`：目标在左侧 → `robot.turn(LEFT)`
- `abs(bearing) < 3`：已对准

### 利用 height/width 估算距离

- `height > 200`：非常近，准备抓取
- `height > 100`：中等距离，继续接近
- `height < 100`：较远，先转向对准

### VisionData 属性全集（12个）

| 属性 | 类型 | 说明 |
|------|------|------|
| `exists` | bool | 是否检测到目标 |
| `bearing` | float | 目标水平角度（度），左负右正 |
| `centerX` | int | 图像 X 坐标（0-320）|
| `centerY` | int | 图像 Y 坐标（0-240）|
| `width` | int | 边界框宽度（像素）|
| `height` | int | 边界框高度（像素）|
| `id` | int | AprilTag ID |
| `score` | int | 置信度（0-100）|
| `rotation` | float | 标签旋转角度（官方名，也写作 angle）|
| `decision_margin` | float | 决策边界值 |
| `hamming` | int | 汉明距离 |
| `tag_family` | string | 标签家族（"36h11"）|

### Signature 常量全集

```python
# 预训练物体检测
SPORTS_BALL, BLUE_BUCKET, RED_BUCKET, AIM_ROBOT

# AprilTag (ID 0-36)
TAG_0 ~ TAG_36, ALL_TAGS

# 自定义颜色签名 (7个)
SIGNATURE_1 ~ SIGNATURE_7

# 自定义颜色码 (7个)
COLOR_CODE_1 ~ COLOR_CODE_7
```

> **注意**：官方 API 中 BLUE_BUCKET/RED_BUCKET 可能也以 BLUE_BARREL/ORANGE_BARREL 形式出现，两者等价。

## Python API 模块速查（14个模块）

### 1. Motion（运动控制）
```python
robot.move_at(direction)          # FORWARD / REVERSE
robot.move_for(direction, dist, MM)
robot.move_with_vectors(x, y)      # 全向移动
robot.turn(direction)              # LEFT / RIGHT
robot.turn_for(direction, angle, DEGREES)
robot.turn_to(heading)
robot.set_move_velocity(50, PERCENT)
robot.set_turn_velocity(40, PERCENT)
robot.stop_all_movement()
robot.get_x_position() / robot.get_y_position()
robot.set_xy_position(x, y)
robot.is_move_active() / robot.is_turn_active() / robot.is_stopped()
```

> **注意**：旧版 API 中 `drive()`/`drive_for()` 等价于 `move_at()`/`move_for()`。

### 2. AI_Vision（AI 视觉）
```python
robot.vision.get_data(signature, count=3)
robot.vision.has_sports_ball()      # 便捷布尔查询 ⭐ 新增
robot.vision.has_any_barrel()
robot.vision.has_blue_barrel()
robot.vision.has_orange_barrel()
robot.vision.show_aivision()        # 屏幕显示视觉画面
robot.vision.hide_aivision()
robot.vision.get_camera_image()     # 仅 WebSocket
robot.vision.set_brightness(50)
robot.vision.set_led_brightness(50)
```

### 3. Kicker（踢球器）
```python
robot.kicker.kick()
robot.kicker.retract()
robot.kicker.is_kicked()
```

### 4. LED
```python
robot.led.set_color(RED)     # RED/GREEN/BLUE/WHITE/OFF
robot.led.set_brightness(50)
robot.led.blink(color, 500)  # interval 单位 MSEC
```

### 5. Sound
```python
robot.sound.play_note(440, 500)           # 频率Hz, 时长MSEC
robot.sound.play_local_file("sound.mp3")  # 仅 WebSocket
```

### 6. Screen
```python
robot.screen.print("Hello")
robot.screen.clear()
robot.screen.draw_rectangle(x, y, w, h)
robot.screen.draw_circle(x, y, r)
robot.screen.set_cursor(row, col)
```

### 7-14. 其他模块
- **Message**：`robot.link.send_message()`, `robot.link.get_message()`, 事件回调
- **Controller**：仅 VEXcode 本地模式，`get_axis()`, `get_button()`
- **Inertial**：`get_heading()`, `get_rotation()`, `set_heading()`
- **Macro**：15+ 预构建行为函数（见下方 Macro 章节）
- **Console**：`console.log()`, `console.print()`
- **Robot**：`robot.battery.capacity()`, `robot.timer.system()`, `robot.reset()`
- **Emoji**：`robot.emoji.show_emoji(HAPPY)`, 36种表情 + 3方向
- **Logic**：`wait(1000, MSEC)`, `timer.value()`

## Macro 预构建行为

### 运动球相关
- `turn_right_until_sports_ball()` / `turn_left_until_sports_ball()`
- `drive_to_sports_ball()` / `get_sports_ball()` / `drop_sports_ball()`
- `find_next_ball()`

### 桶相关
- `turn_right_until_blue_barrel()` / `turn_left_until_blue_barrel()`
- `get_blue_barrel()` / `get_red_barrel()`

### AprilTag 导航
- `turn_right_until_tag(id)` / `turn_left_until_tag(id)`
- `turn_to_tag(id)` / `drive_to_tag(id)`
- `set_tag_for_alignment(id)` / `move_to_position(x, y)`

### 通用
- `go_home()` / `celebrate()` / `scan_field()`

## WebSocket 远程编程

### 环境要求
- Python 3.8+
- vex 库（`pip install -e .` 从 AIM_Websocket_Library）
- opencv-python, numpy
- 机器人需连接 Wi-Fi（AP 或 Station 模式）

### 连接机器人
```python
from vex import Robot
robot = Robot("192.168.1.100")       # IP 地址
robot = Robot("AIM-1234.local")      # Bonjour/mDNS
robot1, robot2 = Robot("192.168.1.51"), Robot("192.168.1.53")  # 多机器人
```

### API 差异
| 特性 | WebSocket | VEXcode 本地 |
|------|-----------|-------------|
| `play_local_file()` | ✅ | ❌ |
| `get_camera_image()` | ✅ | ❌ |
| 多机器人控制 | ✅ | ❌ |
| Controller / Event | ❌ | ✅ |
| 固件更新 | ❌ | ✅ |
| Message Link | ❌ | ✅ |

### 工作区 WebSocket 环境

本项目已配置好 WebSocket 开发环境：
```bash
# 激活虚拟环境
source websocket/venv/bin/activate
# 库位置：websocket/AIM_Websocket_Library/
# 用户代码：websocket/src/
```

## 编程环境对比

| 特性 | VEXcode AIM Web | 桌面版 | VS Code |
|------|----------------|--------|---------|
| 安装 | 无需 | 需下载 | VS Code + 扩展 |
| 语言 | Blocks+Python | Blocks+Python | Python/C++ |
| WebSocket | 不支持 | 不支持 | 间接支持 |
| 离线 | 否 | 是 | 是 |
| 地址 | codeaim.vex.com | vexrobotics.com/aim | VS Code 扩展商店 |

## Message Link（机器人间通信）

**仅在 VEXcode 本地模式可用**，蓝牙通信，约 10 米范围。

```python
# 发送
robot.link.send_message("ball_found", bearing, score, height)

# 同步接收
msg = robot.link.get_message(timeout=5000)
msg, data = robot.link.get_message_and_data(timeout=5000)

# 事件回调
robot.link.handle_message(my_callback, "ball_found")
robot.link.connected(on_connected)
robot.link.disconnected(on_disconnected)

# 状态
robot.link.is_connected()
robot.link.is_message_available()
```

## 代码生成模板

当用户需要编写 VEX AIM 代码时，根据需求选择以下模板：

### 模板 A：AI 视觉搜索与接近
旋转搜索目标 → 检测到后转向对准 → 根据 height 判断距离 → 前进或抓取

### 模板 B：AprilTag 导航
旋转搜索标签 → 对准 → 前进直到足够近 → 执行操作

### 模板 C：竞赛状态机
SEARCH → APPROACH → GRAB → SCORE → RETURN 五状态循环

### 模板 D：WebSocket 视频流 + OpenCV
获取摄像头帧 → cv2 解码 → 自定义处理 → 显示 + 控制

### 模板 E：多机器人协作
连接多个机器人 → Leader 搜索 → Wings 跟随

## 问题排查指南

### AI Vision 检测不稳定
1. 检查光线条件，调整亮度 `robot.vision.set_brightness()`
2. 降低速度减少运动模糊
3. 检查 bearing 修正阈值（±3° 为建议值）
4. 用 score 过滤低置信度检测（建议 > 50）

### WebSocket 连接失败
1. 确认机器人和 PC 在同一 Wi-Fi
2. 检查防火墙设置
3. 验证 IP 地址正确
4. 尝试 `Robot("AIM-XXXX.local")` Bonjour 方式

### Message Link 配对失败
1. 双方进入 Settings → Link AIM
2. 确保蓝牙范围内（< 10 米）
3. 检查连接状态 `robot.link.is_connected()`

## 参考资源

完整文档和代码示例请查阅：
- API 速查表：`references/api-reference.md`
- 代码模板集：`references/code-templates.md`
- 环境配置指南：`references/env-setup.md`