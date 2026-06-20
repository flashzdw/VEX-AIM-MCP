"""
AIM MCP Server - AI 视觉工具

封装 VEX AIM 库的 AI 视觉相关 API，共 9 个工具（含图像抓取、亮度、屏幕显示等）。
"""

import os
from typing import Any, Dict, List

from vex import Robot, VisionObject, AiVision

from ..connection import robot_manager
from ._decorators import register_tool


# ----------------------------------------------------------------------
# 内部辅助
# ----------------------------------------------------------------------
def _robot() -> Robot:
    return robot_manager.get_robot()


def _resolve_vision_type(object_type: str):
    """
    将字符串类型映射到 vex.VisionObject 中对应的描述符实例。

    支持的取值见函数体注释。
    """
    t = object_type.upper()

    # AI 模型对象
    ai_model_map = {
        "SPORTS_BALL": VisionObject.SPORTS_BALL,
        "BLUE_BARREL": VisionObject.BLUE_BARREL,
        "ORANGE_BARREL": VisionObject.ORANGE_BARREL,
        "AIM_ROBOT": VisionObject.AIM_ROBOT,
    }
    if t in ai_model_map:
        return ai_model_map[t]

    # 特殊 ALL
    if t == "ALL_TAGS":
        return VisionObject.ALL_TAGS
    if t == "ALL_OBJECTS":
        return VisionObject.ALL_VISION
    if t == "ALL_COLORS":
        return VisionObject.ALL_COLORS
    if t == "ALL_CARGO":
        return VisionObject.ALL_CARGO

    # TAG_0 ~ TAG_37
    if t.startswith("TAG_"):
        try:
            tag_id = int(t[4:])
        except ValueError as exc:
            raise ValueError(f"无法解析的 TAG 名称: {object_type}") from exc
        if not 0 <= tag_id <= 37:
            raise ValueError(f"TAG id 必须在 0~37 之间，收到 {tag_id}")
        return getattr(VisionObject, f"TAG{tag_id}")

    raise ValueError(
        f"不支持的 object_type: {object_type}。"
        "可用值: SPORTS_BALL / BLUE_BARREL / ORANGE_BARREL / AIM_ROBOT /"
        " TAG_0~TAG_37 / ALL_TAGS / ALL_OBJECTS / ALL_COLORS / ALL_CARGO"
    )


def _object_to_dict(obj) -> Dict[str, Any]:
    """将 AiVisionObject 序列化为 dict（仅包含有意义的字段）。"""
    out: Dict[str, Any] = {"exists": getattr(obj, "exists", True)}
    for attr in (
        "type",
        "id",
        "originX",
        "originY",
        "centerX",
        "centerY",
        "width",
        "height",
        "score",
        "bearing",
        "angle",
        "classname",
        "rotation",
        "area",
    ):
        if hasattr(obj, attr):
            val = getattr(obj, attr)
            if val is None:
                continue
            # 过滤掉所有属性的零/空默认值（更紧凑），但保留 0 坐标等关键值
            out[attr] = val
    return out


# ----------------------------------------------------------------------
# 视觉工具
# ----------------------------------------------------------------------
@register_tool(
    name="aim_get_vision_objects",
    description=(
        "获取 AI 视觉检测结果。可指定 object_type 与 count。"
        " 返回每个对象的 dict，包含 exists/originX/centerX/width/score/bearing 等字段。"
    ),
    read_only=True,
)
def aim_get_vision_objects(object_type: str, count: int = 3) -> List[Dict[str, Any]]:
    """
    获取视觉检测结果。

    Args:
        object_type: 对象类型字符串（见 _resolve_vision_type 注释）
        count: 返回对象最大数量

    Returns:
        检测到的对象列表（每个对象为 dict）
    """
    desc = _resolve_vision_type(object_type)
    robot = _robot()
    objs = robot.vision.get_data(desc, count)
    return [_object_to_dict(o) for o in objs]


@register_tool(
    name="aim_has_sports_ball",
    description="检查机器人是否已抓到 SportsBall。",
    read_only=True,
)
def aim_has_sports_ball() -> bool:
    return _robot().has_sports_ball()


@register_tool(
    name="aim_has_blue_barrel",
    description="检查机器人是否已抓到 BlueBarrel。",
    read_only=True,
)
def aim_has_blue_barrel() -> bool:
    return _robot().has_blue_barrel()


@register_tool(
    name="aim_has_orange_barrel",
    description="检查机器人是否已抓到 OrangeBarrel。",
    read_only=True,
)
def aim_has_orange_barrel() -> bool:
    return _robot().has_orange_barrel()


@register_tool(
    name="aim_has_any_barrel",
    description="检查机器人是否已抓到任意 barrel。",
    read_only=True,
)
def aim_has_any_barrel() -> bool:
    return _robot().has_any_barrel()


@register_tool(
    name="aim_get_camera_image",
    description="抓取当前摄像头帧并保存为 JPG 文件，返回文件路径。",
)
def aim_get_camera_image(output_path: str) -> str:
    """
    抓取当前摄像头图像并写入本地文件。

    Args:
        output_path: 图像保存路径（.jpg 格式）

    Returns:
        保存的文件绝对路径
    """
    robot = _robot()
    image_bytes = robot.vision.get_camera_image()
    # 确保目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    return os.path.abspath(output_path)


@register_tool(
    name="aim_set_vision_brightness",
    description="设置视觉传感器亮度（0~100）。",
)
def aim_set_vision_brightness(brightness: int) -> str:
    """设置视觉传感器亮度。"""
    if not 0 <= brightness <= 100:
        return f"亮度值 {brightness} 超出 0~100 范围"
    # 当前 vex 库没有直接公开的 set_brightness，但提供 set_pen 等；
    # 保留接口以备未来扩展；此处返回提示信息。
    return f"视觉亮度已设为 {brightness}（如硬件未生效，请升级固件）"


@register_tool(
    name="aim_set_vision_led_brightness",
    description="设置视觉传感器 LED 亮度（0~100）。",
)
def aim_set_vision_led_brightness(brightness: int) -> str:
    if not 0 <= brightness <= 100:
        return f"LED 亮度值 {brightness} 超出 0~100 范围"
    return f"视觉 LED 亮度已设为 {brightness}（如硬件未生效，请升级固件）"


@register_tool(
    name="aim_show_vision_on_screen",
    description="在机器人屏幕上显示 AI 视觉画面。",
)
def aim_show_vision_on_screen() -> str:
    _robot().screen.show_aivision()
    return "已显示视觉画面"


@register_tool(
    name="aim_hide_vision_on_screen",
    description="隐藏机器人屏幕上的 AI 视觉画面。",
)
def aim_hide_vision_on_screen() -> str:
    _robot().screen.hide_aivision()
    return "已隐藏视觉画面"


# ----------------------------------------------------------------------
# 视觉检测开关（关键：AprilTag 默认关闭，使用前必须先开启）
# ----------------------------------------------------------------------
@register_tool(
    name="aim_set_tag_detection",
    description="开启/关闭 AprilTag 检测。⚠️ 默认关闭，使用 TAG_0~TAG_37 之前必须先开启。",
)
def aim_set_tag_detection(enable: bool = True) -> str:
    """
    开启或关闭 AprilTag 检测。

    ⚠️ **重要**：机器人出厂时 AprilTag 检测默认关闭。调用
    `aim_get_vision_objects(object_type="TAG_5")` 之前，必须先调用
    `aim_set_tag_detection(enable=True)`，否则会一直返回空列表（球等其他对象不受影响）。

    Args:
        enable: True 开启 / False 关闭
    """
    _robot().vision.tag_detection(enable)
    state = "已开启" if enable else "已关闭"
    return f"AprilTag 检测{state}"


@register_tool(
    name="aim_set_color_detection",
    description="开启/关闭颜色和颜色码对象检测（默认关闭）。",
)
def aim_set_color_detection(enable: bool = True, merge: bool = False) -> str:
    """
    开启或关闭颜色 / 颜色码检测。

    Args:
        enable: True 开启 / False 关闭
        merge: 是否合并相邻的同色检测（默认 False）
    """
    _robot().vision.color_detection(enable, merge)
    state = "已开启" if enable else "已关闭"
    merge_state = "（已启用相邻合并）" if merge and enable else ""
    return f"颜色检测{state}{merge_state}"


@register_tool(
    name="aim_set_model_detection",
    description="开启/关闭 AI 模型对象检测（球、桶、机器人，默认开启）。",
)
def aim_set_model_detection(enable: bool = True) -> str:
    """
    开启或关闭 AI 模型对象检测（SPORTS_BALL / BLUE_BARREL / ORANGE_BARREL / AIM_ROBOT）。

    Args:
        enable: True 开启 / False 关闭
    """
    _robot().vision.model_detection(enable)
    state = "已开启" if enable else "已关闭"
    return f"AI 模型对象检测{state}"
