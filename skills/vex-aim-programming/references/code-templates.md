# VEX AIM 代码模板集

---

## 模板 A：AI 视觉搜索与接近（基础）

```python
# 旋转扫描检测运动球，检测到后接近并抓取
from vex import *

robot = Robot()
robot.set_move_velocity(30, PERCENT)
robot.set_turn_velocity(40, PERCENT)

while True:
    vision_data = robot.vision.get_data(SPORTS_BALL)

    if vision_data[0].exists:
        bearing = vision_data[0].bearing
        score = vision_data[0].score
        height = vision_data[0].height

        # 转向对准（bearing ±3° 为死区）
        if abs(bearing) > 3:
            robot.turn(RIGHT if bearing > 0 else LEFT)
        else:
            # 已对准 — 判断距离
            if height < 160:
                robot.move_at(FORWARD)
            else:
                robot.stop_all_movement()
                robot.get_sports_ball()
                robot.sound.play_note(880, 300)
                break
    else:
        robot.turn(RIGHT)  # 旋转搜索

    wait(20, MSEC)
```

---

## 模板 B：AprilTag 多标签排序导航

```python
# 扫描所有 AprilTag，按距离排序后依次导航
from vex import *

robot = Robot()
robot.set_move_velocity(30, PERCENT)
robot.set_turn_velocity(40, PERCENT)

def scan_all_tags():
    """扫描所有标签，返回按距离降序的标签列表"""
    all_tags = robot.vision.get_data(ALL_TAGS, count=10)
    detected = []
    for tag in all_tags:
        if tag.exists:
            detected.append({
                'id': tag.id, 'bearing': tag.bearing,
                'height': tag.height, 'score': tag.score,
            })
    detected.sort(key=lambda t: t['height'], reverse=True)
    return detected

def navigate_to_tag(tag_id):
    """导航到指定标签"""
    # 第一阶段：旋转搜索
    robot.turn(RIGHT)
    start = robot.timer.system()
    while robot.timer.system() - start < 5000:
        sig = globals()[f'TAG_{tag_id}']
        data = robot.vision.get_data(sig)
        if data[0].exists:
            robot.turn_to(robot.inertial.get_heading() + data[0].bearing)
            break
        wait(20, MSEC)

    # 第二阶段：前进直到接近
    robot.move_at(FORWARD)
    while True:
        data = robot.vision.get_data(globals()[f'TAG_{tag_id}'])
        if data[0].exists and data[0].height > 160:
            robot.stop_all_movement()
            break
        elif not data[0].exists:
            robot.stop_all_movement()
            break
        wait(20, MSEC)

    return True

# 主程序
tags = scan_all_tags()
for t in tags:
    navigate_to_tag(t['id'])
    wait(1000, MSEC)

robot.go_home()
robot.celebrate()
```

---

## 模板 C：竞赛自动阶段状态机

```python
from vex import *

robot = Robot()
robot.set_move_velocity(40, PERCENT)
robot.set_turn_velocity(50, PERCENT)

SEARCH, APPROACH, GRAB, SCORE, RETURN = 0, 1, 2, 3, 4
state = SEARCH
balls_scored = 0
MAX_BALLS = 3

while balls_scored < MAX_BALLS:
    if state == SEARCH:
        robot.led.set_color(BLUE)
        robot.turn(RIGHT)
        data = robot.vision.get_data(SPORTS_BALL)
        if data[0].exists and data[0].score > 50:
            robot.turn_to(robot.inertial.get_heading() + data[0].bearing)
            state = APPROACH

    elif state == APPROACH:
        robot.led.set_color(YELLOW)
        robot.move_at(FORWARD)
        data = robot.vision.get_data(SPORTS_BALL)
        if data[0].exists:
            if data[0].height > 170:
                robot.stop_all_movement()
                state = GRAB
            elif abs(data[0].bearing) > 3:
                robot.turn(RIGHT if data[0].bearing > 0 else LEFT)
        else:
            robot.stop_all_movement()
            state = SEARCH

    elif state == GRAB:
        robot.led.set_color(GREEN)
        robot.get_sports_ball()
        state = SCORE

    elif state == SCORE:
        robot.turn(RIGHT)
        for _ in range(100):  # ~2秒搜索
            if robot.vision.get_data(TAG_5)[0].exists:
                robot.turn_to_tag(5)
                robot.drive_to_tag(5)
                break
            wait(20, MSEC)
        robot.drop_sports_ball()
        balls_scored += 1
        state = RETURN if balls_scored >= MAX_BALLS else SEARCH

    elif state == RETURN:
        robot.go_home()
        break

    wait(20, MSEC)

robot.stop_all_movement()
robot.celebrate()
```

---

## 模板 D：WebSocket 视频流 + OpenCV 处理

```python
# stream_video.py — 需要 WebSocket 连接
import cv2
import numpy as np
from vex import Robot

robot = Robot("192.168.1.100")

while True:
    # 获取 JPEG 帧
    image_bytes = robot.vision.get_camera_image()
    nparr = np.frombuffer(image_bytes, dtype='uint8')
    frame = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    # 自定义处理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # 显示
    cv2.imshow('AIM Camera', frame)
    cv2.imshow('Edge Detection', edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
```

---

## 模板 E：多机器人编队协作

```python
# 需要 WebSocket 连接
from vex import Robot

class AIMSwarm:
    def __init__(self):
        self.robots = {
            'leader': Robot("192.168.1.100"),
            'left_wing': Robot("192.168.1.101"),
            'right_wing': Robot("192.168.1.102"),
        }

    def all_drive(self, direction, duration_ms):
        for robot in self.robots.values():
            robot.move_at(direction)
        wait(duration_ms, MSEC)
        for robot in self.robots.values():
            robot.stop_all_movement()

    def leader_search(self):
        leader = self.robots['leader']
        while True:
            data = leader.vision.get_data(SPORTS_BALL)
            if data[0].exists:
                leader.turn_to(
                    leader.inertial.get_heading() + data[0].bearing
                )
                leader.move_at(FORWARD)
                self.robots['left_wing'].move_at(FORWARD)
                self.robots['right_wing'].move_at(FORWARD)
            else:
                leader.turn(RIGHT)
            wait(20, MSEC)

swarm = AIMSwarm()
swarm.leader_search()
```

---

## 模板 F：Message Link 双机器人协作

```python
# 机器人 A：检测后通知 B（仅 VEXcode 本地模式）
from vex import *

robot = Robot()

while True:
    data = robot.vision.get_data(SPORTS_BALL)
    if data[0].exists:
        robot.link.send_message(
            "ball_found",
            data[0].bearing,
            data[0].score,
            data[0].height
        )
        robot.led.set_color(GREEN)
    else:
        robot.link.send_message("searching", 0, 0, 0)
        robot.turn(RIGHT)
    wait(50, MSEC)
```

```python
# 机器人 B：接收通知并响应
from vex import *

robot = Robot()

while True:
    msg, data = robot.link.get_message_and_data(timeout=1000)
    if msg == "ball_found":
        bearing, score, height = data
        robot.turn_to(robot.inertial.get_heading() + bearing)
        robot.move_at(FORWARD)
        wait(2000, MSEC)
        robot.stop_all_movement()
    elif msg == "searching":
        robot.turn(RIGHT)
    wait(20, MSEC)
```

---

## 模板 G：bearing 平滑与距离估算

```python
from collections import deque

class VisionTracker:
    def __init__(self, robot, smooth_window=5):
        self.robot = robot
        self.bearing_history = deque(maxlen=smooth_window)

    def get_smooth_bearing(self):
        """获取平滑后的 bearing 值"""
        data = self.robot.vision.get_data(SPORTS_BALL)
        if data[0].exists:
            self.bearing_history.append(data[0].bearing)
            return sum(self.bearing_history) / len(self.bearing_history)
        return None

    def estimate_distance_cm(self):
        """根据 height 估算距离（粗略）"""
        data = self.robot.vision.get_data(SPORTS_BALL)
        if data[0].exists:
            return int(5000 / (data[0].height + 1))
        return None
```