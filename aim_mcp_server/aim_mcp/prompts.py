"""
AIM MCP Server - Prompts

封装常用工作流模板，每个 prompt 返回多步骤文本指引（不会直接执行）。
"""

from mcp.types import PromptMessage


def register_all(mcp) -> None:
    """注册全部 prompts。"""

    @mcp.prompt(
        name="search_and_grab_ball",
        description=(
            "返回搜索并抓取 SportsBall 的多步骤操作指引（文本步骤，非直接执行）。"
            "Agent 应按顺序调用工具完成扫描→对准→前进→抓取。"
        ),
    )
    def search_and_grab_ball() -> list:
        """
        搜索并抓取球的步骤指引。

        Returns:
            一组 PromptMessage，描述每一步要调用的工具与参数。
        """
        return [
            PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": (
                        "请按以下步骤完成 '搜索并抓取 SportsBall' 工作流：\n\n"
                        "1. 调用 aim_get_vision_objects(object_type=\"SPORTS_BALL\", count=3)，"
                        "获取最近的球列表。\n"
                        "2. 如果列表为空，调用 aim_turn(direction=\"LEFT\", velocity=30) 让机器人原地旋转，"
                        "再次扫描，直到发现球或达到扫描上限。\n"
                        "3. 取列表第一个球的 centerX、centerY、bearing 字段：\n"
                        "   - 如果 |bearing| > 5，先调用 aim_turn_to(heading=当前朝向 + bearing, wait=True) 对准；\n"
                        "   - 然后调用 aim_move_for(distance=200, direction=0, velocity=50, wait=True) 前进一小段；\n"
                        "   - 重复步骤 1-3 直至球被机器人持住。\n"
                        "4. 调用 aim_has_sports_ball() 确认是否抓到球。\n"
                        "5. 抓到后调用 aim_kick(force=\"MEDIUM\") 将球踢出。\n"
                        "6. 调用 aim_get_battery_capacity() 检查电量，必要时提示用户充电。\n\n"
                        "每一步之间用 aim_print_screen(text=...) 在机器人屏幕显示当前状态，"
                        "便于用户观察进度。"
                    ),
                },
            ),
            PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": (
                        "提示：\n"
                        "- 若 aim_get_vision_objects 返回空，尝试调用 aim_turn(direction=\"RIGHT\") 后再扫描；\n"
                        "- 若出现 DisconnectedException，先调用 aim_disconnect() 再 aim_connect(host=...) 重连；\n"
                        "- 全程使用 aim_get_heading() 记录当前朝向，便于回溯。"
                    ),
                },
            ),
        ]

    @mcp.prompt(
        name="navigate_to_tag",
        description=(
            "返回导航到指定 AprilTag 的多步骤操作指引（文本步骤，非直接执行）。"
            "Agent 应按顺序执行扫描→对准→前进→到达。"
        ),
    )
    def navigate_to_tag(tag_id: int = 0) -> list:
        """
        导航到 AprilTag 的步骤指引。

        Args:
            tag_id: 目标 AprilTag 编号

        Returns:
            一组 PromptMessage
        """
        type_str = f"TAG_{tag_id}"
        return [
            PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": (
                        f"请按以下步骤完成 '导航到 AprilTag {tag_id}' 工作流：\n\n"
                        f"0. 【必须】调用 aim_set_tag_detection(enable=True) 开启 AprilTag 检测，"
                        f"否则 get_data 永远返回空列表（球等其他对象不受影响）；\n"
                        f"1. 调用 aim_get_vision_objects(object_type=\"{type_str}\", count=1) 检测目标 tag；\n"
                        f"2. 若未发现，调用 aim_turn(direction=\"LEFT\", velocity=30) 旋转 360° 持续扫描；\n"
                        f"3. 检测到后读取 bearing 与 centerX：\n"
                        f"   - 计算 heading_offset = 当前朝向 + bearing；\n"
                        f"   - 调用 aim_turn_to(heading=heading_offset, wait=True) 对准；\n"
                        f"   - 调用 aim_move_for(distance=150, direction=0, velocity=40, wait=True) 前进；\n"
                        f"4. 重复 1-3 步骤，每次都重新计算 bearing；\n"
                        f"5. 当 centerY 超过某个阈值（球接近）或 distance 很小时，停止前进并报告到达。\n\n"
                        f"完成后调用 aim_print_screen(text=f\"Reached tag {tag_id}\") 显示结果。"
                    ),
                },
            ),
            PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": (
                        "注意事项：\n"
                        "- 每次前进后用 aim_get_position() 记录位置，便于回退；\n"
                        "- 若连续 3 次 aim_get_vision_objects 都为空，停止任务并提示用户检查 tag 是否在视野内；\n"
                        "- 谨慎使用 aim_turn_to 短距离调整，避免抖动。"
                    ),
                },
            ),
        ]

    @mcp.prompt(
        name="calibrate_and_test",
        description=(
            "返回 IMU 校准和运动测试的多步骤操作指引（文本步骤，非直接执行）。"
            "适合首次调试或长时间运行后的复位场景。"
        ),
    )
    def calibrate_and_test() -> list:
        """IMU 校准和运动测试的步骤指引。"""
        return [
            PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": (
                        "请按以下步骤完成 'IMU 校准 + 运动测试' 工作流：\n\n"
                        "1. 调用 aim_print_screen(text=\"Calibrating IMU...\") 提示用户；\n"
                        "2. 调用 aim_reset_heading() 与 aim_set_xy_position(x=0, y=0) 复位位姿；\n"
                        "3. （IMU 校准）等待 3-5 秒后读取 aim_get_heading()，确认无明显漂移；\n"
                        "4. 调用 aim_set_move_velocity(velocity=40) 设置低速；\n"
                        "5. 调用 aim_move_for(distance=200, direction=0, wait=True) 前进 200mm；\n"
                        "6. 调用 aim_get_position() 检查 x、y 是否符合预期；\n"
                        "7. 调用 aim_turn_for(direction=\"RIGHT\", angle=90, wait=True) 原地右转 90°；\n"
                        "8. 调用 aim_get_heading() 检查朝向变化；\n"
                        "9. 调用 aim_stop() 停止；\n"
                        "10. 报告测试结果：前进距离误差、转向角度误差、电量。\n"
                    ),
                },
            ),
            PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": (
                        "异常处理：\n"
                        "- 若 aim_get_heading() 在静止时仍持续变化，提示用户重启机器人；\n"
                        "- 若 aim_move_for 实际位移与设定值差距 > 20%，提示用户检查轮子或地面；\n"
                        "- 全程使用 aim_get_battery_capacity() 监控电量，低于 20% 时停止测试。"
                    ),
                },
            ),
        ]
