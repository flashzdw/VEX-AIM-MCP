# VEX AIM 环境配置指南

> 适用平台：macOS | 最后更新：2026年6月

---

## 一、WebSocket 开发环境（已配置）

本项目已预配置 WebSocket 开发环境：

```
Test_26.6.13/
├── websocket/
│   ├── AIM_Websocket_Library/   # vex 库源码 (GitHub: VEX-Robotics/AIM_Websocket_Library)
│   ├── venv/                    # Python 虚拟环境（已激活可用）
│   └── src/                     # 用户代码目录（在此编写.py文件）
└── vexcode-projects/            # VEXcode 项目目录
```

### 激活环境

```bash
cd /Users/DONGZ/Desktop/VEXRobots/AIM/Test_26.6.13
source websocket/venv/bin/activate
```

### 已安装的包

| 包 | 版本 | 用途 |
|----|------|------|
| vex | 1.0.1 | WebSocket 机器人控制库 |
| opencv-python | 4.13.0 | 计算机视觉 |
| numpy | 2.0.2 | 数值计算 |
| websocket-client | 1.9.0 | WebSocket 通信 |

### 编写和运行代码

```bash
# 在 websocket/src/ 下创建 Python 文件
# 例如：my_robot.py

# 运行（需确保机器人已连接同一 Wi-Fi）
python my_robot.py
```

---

## 二、VEXcode AIM

### Web IDE（推荐入门）
- 地址：https://codeaim.vex.com
- 无需安装，浏览器打开即用
- 支持 Blocks + Python + Switch 混合编程

### 桌面版
- 下载：https://www.vexrobotics.com/aim
- 最新版本：VEXcode AIM 4.61（2025年9月发布）
- 支持离线使用、固件更新、自定义资源上传

---

## 三、VS Code Extension

### 需要安装的扩展（共 4 个）

1. **VEX Robotics** — 核心扩展（搜索 "VEX Robotics"）
2. **VEX Robotics Feedback** — 反馈扩展（自动安装）
3. **C/C++ (Microsoft)** — C++ IntelliSense
4. **Python (Microsoft)** — Python IntelliSense

### 关键设置

在 VS Code 设置中搜索 "VEX"：
- `Websocket Server Enable`：启用 WebSocket
- `Websocket Server Host Address`：IP 地址
- `Websocket Server Port`：端口
- `Run After Download`：下载后自动运行

---

## 四、机器人 Wi-Fi 连接

### AP 模式（机器人自建热点）
1. AIM 开机 → Settings → Wi-Fi → Access Point
2. PC 连接 AIM 的 Wi-Fi 热点
3. 代码中使用 `Robot("192.168.1.100")`（查看 AIM 屏幕 IP）

### Station 模式（连接同一路由器）
1. AIM → Settings → Wi-Fi → Station → 选择网络
2. PC 连接同一 Wi-Fi
3. 代码中使用 AIM 在路由器上的 IP

### 模式切换
参考：https://api.vex.com/aim/home/websocket/wifi_setup/switch_modes.html

---

## 五、pyaudio 音频支持（可选）

pyaudio 用于音频录制功能，当前未安装（因 macOS Xcode CLT 版本兼容问题）。

如需安装：
```bash
# 1. 安装 portaudio
brew install portaudio

# 2. 安装 pyaudio
source websocket/venv/bin/activate
pip install pyaudio
```

> 注：不影响核心机器人控制功能，仅影响语音识别等高级特性。

---

## 六、官方资源索引

| 资源 | 链接 |
|------|------|
| API 文档首页 | https://api.vex.com/aim/ |
| Python API | https://api.vex.com/aim/home/python/index.html |
| WebSocket 文档 | https://api.vex.com/aim/home/websocket/index.html |
| WebSocket 库 | https://github.com/VEX-Robotics/AIM_Websocket_Library |
| VEXcode AIM Web | https://codeaim.vex.com |
| STEM Labs | https://education.vex.com/stemlabs/aim |
| VS Code 安装 | https://kb.vex.com/hc/en-us/articles/31173783521428 |
| VEX 知识库 | https://kb.vex.com/ |
| CMU Calypso | https://github.com/touretzkyds/calypso |
| VEX 中国 | https://www.vex.com.cn/ |
| 中文社区 | https://vexrobot.cn/ |