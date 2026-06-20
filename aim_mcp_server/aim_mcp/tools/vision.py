"""
AIM MCP Server - AI 视觉工具

封装 VEX AIM 库的 AI 视觉相关 API，共 18 个工具。
"""

import os
import time
from typing import Any, Dict, List, Optional

from vex import Robot, VisionObject

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
            out[attr] = val
    return out


# ----------------------------------------------------------------------
# 基础视觉工具
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
    robot = _robot()
    image_bytes = robot.vision.get_camera_image()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    return os.path.abspath(output_path)


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
    _robot().vision.tag_detection(enable)
    state = "已开启" if enable else "已关闭"
    return f"AprilTag 检测{state}"


@register_tool(
    name="aim_set_color_detection",
    description="开启/关闭颜色和颜色码对象检测（默认关闭）。",
)
def aim_set_color_detection(enable: bool = True, merge: bool = False) -> str:
    _robot().vision.color_detection(enable, merge)
    state = "已开启" if enable else "已关闭"
    merge_state = "（已启用相邻合并）" if merge and enable else ""
    return f"颜色检测{state}{merge_state}"


@register_tool(
    name="aim_set_model_detection",
    description="开启/关闭 AI 模型对象检测（球、桶、机器人，默认开启）。",
)
def aim_set_model_detection(enable: bool = True) -> str:
    _robot().vision.model_detection(enable)
    state = "已开启" if enable else "已关闭"
    return f"AI 模型对象检测{state}"


# ----------------------------------------------------------------------
# 高级视觉工具（V1~V7）
# ----------------------------------------------------------------------
@register_tool(
    name="aim_scan_for_object",
    description=(
        "持续原地旋转扫描场地，直到检测到指定类型的对象（球/桶/Tag）。"
        "返回发现时的 found/bearing/centerX/centerY/object。"
    ),
)
def aim_scan_for_object(
    object_type: str,
    count: int = 1,
    scan_velocity: int = 30,
    max_angle: float = 360.0,
) -> Dict[str, Any]:
    """原地旋转扫描直至发现目标。"""
    desc = _resolve_vision_type(object_type)
    robot = _robot()
    try:
        start_heading = robot.heading()
    except Exception:
        start_heading = 0
    rotated = 0.0
    step = 15.0
    found_obj = None
    while rotated < max_angle:
        objs = robot.vision.get_data(desc, count)
        if objs:
            found_obj = _object_to_dict(objs[0])
            break
        try:
            robot.turn_for(angle=step, velocity=scan_velocity, wait=True)
        except Exception:
            break
        rotated += step
        time.sleep(0.05)
    try:
        robot.turn_to(heading=start_heading, wait=True)
    except Exception:
        pass
    return {
        "found": found_obj is not None,
        "scanned_angle": rotated,
        "object": found_obj,
    }


@register_tool(
    name="aim_estimate_distance_to_object",
    description=(
        "根据首个检测对象的像素宽度，启发式估算机器人到目标的距离（毫米）。"
        "公式 distance_mm ≈ calibration_k / width_px（K 默认 35000）。"
        "适合粗略导航；精确距离请自行标定 K 值。"
    ),
    read_only=True,
)
def aim_estimate_distance_to_object(
    object_type: str,
    calibration_k: float = 35000.0,
) -> Dict[str, Any]:
    desc = _resolve_vision_type(object_type)
    objs = _robot().vision.get_data(desc, 1)
    if not objs:
        return {"found": False, "distance_mm": None, "width_px": None}
    width = getattr(objs[0], "width", 0) or 0
    if width <= 0:
        return {"found": True, "distance_mm": None, "width_px": 0, "warning": "width=0 无法估算"}
    return {
        "found": True,
        "distance_mm": round(calibration_k / width, 1),
        "width_px": width,
    }


@register_tool(
    name="aim_capture_with_overlay",
    description=(
        "抓拍当前摄像头画面，并在画面上叠加 AI 检测框 + 标签，"
        "保存为 JPG；返回文件绝对路径。"
    ),
)
def aim_capture_with_overlay(
    output_path: str,
    object_type: str = "ALL_OBJECTS",
    count: int = 8,
) -> str:
    robot = _robot()
    image_bytes = robot.vision.get_camera_image()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    try:
        from PIL import Image, ImageDraw
        import io
    except ImportError:
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        return os.path.abspath(output_path) + " (Pillow 未安装，未叠加框)"
    desc = _resolve_vision_type(object_type)
    objs = robot.vision.get_data(desc, count)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    for o in objs:
        ox = getattr(o, "originX", 0) or 0
        oy = getattr(o, "originY", 0) or 0
        ow = getattr(o, "width", 0) or 0
        oh = getattr(o, "height", 0) or 0
        cx = getattr(o, "centerX", 0) or 0
        cy = getattr(o, "centerY", 0) or 0
        label = f"{getattr(o, 'classname', '') or getattr(o, 'type', 'obj')} {cx},{cy}"
        x0, y0 = int(ox), int(oy)
        x1, y1 = int(ox + ow), int(oy + oh)
        draw.rectangle([x0, y0, x1, y1], outline=(0, 255, 0), width=3)
        draw.text((x0, max(0, y0 - 12)), label, fill=(0, 255, 0))
    img.save(output_path, "JPEG", quality=90)
    return os.path.abspath(output_path)


@register_tool(
    name="aim_define_color_signature",
    description=(
        "定义一个 AIM 视觉颜色签名（1~7 号槽位），"
        "供 aim_set_color_detection(enable=True) 之后使用。"
    ),
)
def aim_define_color_signature(
    slot: int,
    red: int,
    green: int,
    blue: int,
    hue_range: int = 10,
    sat_range: int = 100,
) -> str:
    if not 1 <= slot <= 7:
        return f"颜色签名槽位必须在 1~7 之间，收到 {slot}"
    try:
        from vex import Colordesc
    except ImportError:
        return "当前 vex 库版本不支持 Colordesc，无法定义颜色签名"
    _robot().vision.set_color_signature(
        Colordesc(red, green, blue, hue_range, sat_range, slot)
    )
    return f"颜色签名 #{slot} 已定义（RGB={red},{green},{blue}, hue±{hue_range}）"


@register_tool(
    name="aim_count_objects",
    description=(
        "快速统计视野中各类型对象的数量（不返回坐标详情）。"
        "适用场景：快速判断场上还有几个球/几个 Tag，再决定是否要切换策略。"
    ),
    read_only=True,
)
def aim_count_objects(
    object_types: Optional[List[str]] = None,
    count_per_type: int = 8,
) -> Dict[str, Any]:
    types = object_types or [
        "SPORTS_BALL",
        "BLUE_BARREL",
        "ORANGE_BARREL",
        "AIM_ROBOT",
        "ALL_TAGS",
    ]
    result: Dict[str, Any] = {}
    for t in types:
        try:
            desc = _resolve_vision_type(t)
            objs = _robot().vision.get_data(desc, count_per_type)
            result[t] = len(objs) if objs else 0
        except Exception as e:
            result[t] = f"error: {e}"
    return result


@register_tool(
    name="aim_get_object_bearing",
    description=(
        "取首个指定对象的 bearing / centerX 角度（轻量版 get_vision_objects）。"
        "适用场景：只想知道目标方向、不需要完整字段时用这个更省 token。"
    ),
    read_only=True,
)
def aim_get_object_bearing(
    object_type: str,
    max_count: int = 8,
) -> Dict[str, Any]:
    desc = _resolve_vision_type(object_type)
    objs = _robot().vision.get_data(desc, max_count)
    if not objs:
        return {"found": False, "bearing": None, "centerX": None}
    o = objs[0]
    return {
        "found": True,
        "bearing": getattr(o, "bearing", None),
        "centerX": getattr(o, "centerX", None),
    }


@register_tool(
    name="aim_define_color_code",
    description=(
        "定义一个 AIM 视觉颜色码（1~5 号槽位），由 2~5 个 Colordesc 组合而成。"
        "适用于场地上的复合标记（如双色条纹 / 棋盘格）。"
        "先调 aim_define_color_signature 注册单个颜色，再用本工具组合为颜色码。"
    ),
)
def aim_define_color_code(
    slot: int,
    color_descs: List[Dict[str, Any]],
) -> str:
    if not 1 <= slot <= 5:
        return f"颜色码槽位必须在 1~5 之间，收到 {slot}"
    if not 2 <= len(color_descs) <= 5:
        return f"颜色码需要 2~5 个 Colordesc，收到 {len(color_descs)}"
    try:
        from vex import Colordesc
    except ImportError:
        return "当前 vex 库版本不支持 Colordesc，无法定义颜色码"
    descs = [
        Colordesc(
            d["r"],
            d["g"],
            d["b"],
            d.get("hue", 10),
            d.get("sat", 100),
            d.get("sig", i + 1),
        )
        for i, d in enumerate(color_descs)
    ]
    _robot().vision.set_color_code(slot, descs)
    return f"颜色码 #{slot} 已定义（{len(descs)} 个 Colordesc）"
