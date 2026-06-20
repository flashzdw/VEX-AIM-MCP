"""
AIM MCP Server - 声音工具

封装 VEX AIM 库的 Sound 相关 API，共 5 个工具。
"""

import vex as vex_types

from ..connection import robot_manager
from ._decorators import register_tool


# 内置音效名称（vex_types.SoundType 完整列表）
_BUILTIN_SOUNDS = {s.value: s for s in vex_types.SoundType}


@register_tool(
    name="aim_play_sound",
    description="播放内置音效（DOORBELL / TADA / FAIL / SPARKLE 等）。",
)
def aim_play_sound(sound_type: str, volume: int = 50) -> str:
    """
    播放内置音效。

    Args:
        sound_type: 音效名，如 "DOORBELL"、"TADA"、"FAIL"
        volume: 音量 0~100

    Returns:
        执行结果描述
    """
    s = sound_type.upper()
    if s not in _BUILTIN_SOUNDS:
        available = ", ".join(sorted(_BUILTIN_SOUNDS.keys()))
        return f"不支持的音效: {sound_type}。可选: {available}"
    if not 0 <= volume <= 100:
        return f"音量 {volume} 超出 0~100 范围"
    robot_manager.get_robot().sound.play(_BUILTIN_SOUNDS[s], volume)
    return f"已播放音效 {s}（volume={volume}）"


@register_tool(
    name="aim_play_note",
    description="播放单音符（如 C5 / F#6）。",
)
def aim_play_note(note: str, duration: int = 750, volume: int = 50) -> str:
    """
    播放指定音符。

    Args:
        note: 音符字符串，如 "C5"、"F#6"
        duration: 持续时间（毫秒）
        volume: 音量 0~100

    Returns:
        执行结果描述
    """
    if not 0 <= volume <= 100:
        return f"音量 {volume} 超出 0~100 范围"
    robot_manager.get_robot().sound.play_note(note, duration, volume)
    return f"已播放音符 {note}（{duration}ms，volume={volume}）"


@register_tool(
    name="aim_play_sound_file",
    description="播放本地 wav/mp3 文件（最大 255KB）。",
)
def aim_play_sound_file(filepath: str, volume: int = 100) -> str:
    """
    播放本地音频文件。

    Args:
        filepath: 本地音频文件路径
        volume: 音量 0~100

    Returns:
        执行结果描述
    """
    if not 0 <= volume <= 100:
        return f"音量 {volume} 超出 0~100 范围"
    robot_manager.get_robot().sound.play_local_file(filepath, volume)
    return f"已播放音频文件 {filepath}（volume={volume}）"


@register_tool(
    name="aim_stop_sound",
    description="停止当前正在播放的声音。",
)
def aim_stop_sound() -> str:
    robot_manager.get_robot().sound.stop()
    return "已停止声音"


@register_tool(
    name="aim_is_sound_playing",
    description="检查是否正在播放声音。",
    read_only=True,
)
def aim_is_sound_playing() -> bool:
    return robot_manager.get_robot().sound.is_active()
