# VEX AIM API 速查表

> 基于官方 API 文档 + 实际调研更新 | 适用 VEXcode AIM 4.61+ / WebSocket v1.0.1

---

## 一、AI Vision API

### get_data(signature, count=3)
```python
vision_data = robot.vision.get_data(SPORTS_BALL, count=3)
# 返回 VisionData[] 数组，按置信度降序，最多 count 个
# count: 最大 10
```

### 便捷布尔检测（⭐ 新增方法）
```python
robot.vision.has_sports_ball()   # → bool
robot.vision.has_any_barrel()    # → bool
robot.vision.has_blue_barrel()   # → bool
robot.vision.has_orange_barrel() # → bool
```

### VisionData 属性
```
.exists            bool   是否检测到
.bearing           float  水平角度(°)，左负右正
.centerX           int    X坐标(0-320)
.centerY           int    Y坐标(0-240)
.width             int    宽度(px)
.height            int    高度(px)
.id                int    AprilTag ID
.score             int    置信度(0-100)
.rotation          float  旋转角度(官方名，=angle)
.decision_margin   float  决策边界
.hamming           int    汉明距离
.tag_family        str    标签家族("36h11")
.originX           int    框原点X(⭐新增)
.originY           int    框原点Y(⭐新增)
```

### 其他视觉函数
```python
robot.vision.get_object_count(signature)      # → int
robot.vision.take_snapshot(signature, count)  # 含时间戳快照
robot.vision.detect_all_tags()                # 所有标签
robot.vision.get_tag_pose(id)                 # 3D姿态
robot.vision.get_camera_image()               # JPEG bytes (仅WebSocket)
robot.vision.show_aivision()                  # 屏幕显示AI画面
robot.vision.hide_aivision()
robot.vision.set_brightness(0-100)
robot.vision.set_white_balance(mode)          # 0=auto, 1=manual
robot.vision.set_led_brightness(0-100)
```

---

## 二、Motion API

```python
# 基本运动
robot.move_at(FORWARD)          # FORWARD / REVERSE
robot.turn(RIGHT)               # RIGHT / LEFT
robot.stop_all_movement()

# 参数化运动
robot.move_for(direction, 300, MM)       # MM / INCHES
robot.turn_for(direction, 90, DEGREES)
robot.turn_to(180)                       # 转到指定航向(°)
robot.move_with_vectors(x, y)            # ⭐ 全向移动

# 速度设置
robot.set_move_velocity(50, PERCENT)     # PERCENT / RPM
robot.set_turn_velocity(40, PERCENT)

# 坐标追踪 ⭐
robot.set_xy_position(x, y)
robot.get_x_position()
robot.get_y_position()

# 状态查询 ⭐
robot.is_move_active()     # → bool
robot.is_turn_active()     # → bool
robot.is_stopped()         # → bool

# 兼容旧API（等价的旧名称）
robot.drive(FORWARD)       # = move_at(FORWARD)
robot.drive_for(FORWARD, 300, MM)  # = move_for(...)
```

---

## 三、其他模块速查

### Kicker
```python
robot.kicker.kick()
robot.kicker.retract()
robot.kicker.is_kicked()    # → bool
```

### LED
```python
robot.led.set_color(RED)        # RED/GREEN/BLUE/WHITE/OFF
robot.led.set_brightness(50)    # 0-100
robot.led.blink(GREEN, 500)     # ms间隔
```

### Sound
```python
robot.sound.play_note(440, 500)               # Hz, MSEC
robot.sound.play_effect(effect)               # 预设音效
robot.sound.play_local_file("file.wav", 80)   # 仅WebSocket
```

### Screen
```python
robot.screen.print("text")
robot.screen.clear()
robot.screen.set_cursor(row, col)
robot.screen.draw_rectangle(x, y, w, h)
robot.screen.draw_circle(x, y, r)
robot.screen.draw_line(x1, y1, x2, y2)
robot.screen.set_pen_color(color)
robot.screen.set_fill_color(color)
robot.screen.is_pressed()    # → bool
```

### Inertial
```python
robot.inertial.get_heading()      # 0-359.9°
robot.inertial.get_rotation()     # 累计旋转
robot.inertial.set_heading(0)     # 重置
robot.inertial.is_calibrating()   # → bool
```

### Message (仅VEXcode本地)
```python
robot.link.send_message("msg", arg1, arg2, arg3)
robot.link.get_message(timeout=5000)       # → str
robot.link.get_message_and_data(timeout)   # → (str, tuple)
robot.link.is_connected()                  # → bool
robot.link.is_message_available()          # → bool
robot.link.get_name()                      # → str
robot.link.handle_message(callback, "msg")  # 事件回调
robot.link.connected(callback)
robot.link.disconnected(callback)
```

### Robot 全局
```python
robot.battery.capacity()    # 电量%
robot.timer.system()        # 系统运行时间(ms)
robot.timer.clear()         # 清零计时器
robot.reset()               # 重置状态
```

### Emoji
```python
robot.emoji.show_emoji(HAPPY)   # 36种: EXCITED,HAPPY,SAD,ANGRY,COOL...
robot.emoji.hide_emoji()
robot.emoji.set_direction(LOOK_FORWARD)  # LOOK_LEFT/FORWARD/RIGHT
```

### Logic
```python
wait(1000, MSEC)      # MSEC / SECONDS
timer.value()          # → int
```

---

## 四、WebSocket 特有 API

```python
# 多机器人
Robot("192.168.1.100")           # IP地址
Robot("AIM-1234.local")          # Bonjour/mDNS
robot1 = Robot("192.168.1.51")
robot2 = Robot("192.168.1.53")   # 同时控制多台

# 摄像头流
image_bytes = robot.vision.get_camera_image()  # JPEG bytes

# 本地音频
robot.sound.play_local_file("path/to/file.wav", volume=80)
```

---

## 五、Macro 函数

```python
# 运动球
turn_right_until_sports_ball(), turn_left_until_sports_ball()
drive_to_sports_ball(), get_sports_ball(), drop_sports_ball()
find_next_ball()

# 桶
turn_right_until_blue_barrel(), turn_left_until_blue_barrel()
get_blue_barrel(), turn_right_until_red_barrel(), get_red_barrel()

# AprilTag
turn_right_until_tag(id), turn_left_until_tag(id)
turn_to_tag(id), drive_to_tag(id)
set_tag_for_alignment(id), move_to_position(x, y)

# 通用
go_home(), celebrate(), scan_field()
```