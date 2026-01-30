import time
from collections import deque
import cv2


class MotionDetector:
    """
    动作识别模块（滑动检测）
    功能：
    - 基于连续帧食指 x 坐标判断左右滑动
    - 最小滑动距离阈值
    - 防抖动机制
    - 左右手方向自动校正
    - 轨迹缓存用于可视化
    """

    def __init__(self,
                 min_distance=66,
                 debounce_time=2.0,
                 max_trajectory_length=30):

        # 参数
        self.min_distance = min_distance
        self.debounce_time = debounce_time

        # 轨迹缓存
        self.trajectory = deque(maxlen=max_trajectory_length)

        # 状态控制
        self.last_trigger_time = 0
        self.state = "READY"

    # --------------------------------
    # 核心接口：检测滑动
    # --------------------------------
    def detect_swipe(self, current_x: int, is_right_hand: bool):
        """
        参数：
            current_x: 食指当前帧x坐标
            is_right_hand: 是否为右手

        返回：
            'left'  -> 上一页
            'right' -> 下一页
            None    -> 无动作
        """

        self.trajectory.append(current_x)

        if len(self.trajectory) < 5:
            return None

        x_start = self.trajectory[0]
        x_end = self.trajectory[-1]
        delta_x = x_end - x_start

        # 未达到阈值
        if abs(delta_x) < self.min_distance:
            return None

        # 防抖检测
        if not self._can_trigger():
            return None

        self._trigger()
        self.trajectory.clear()

        # 判断方向
        if delta_x > 0:
            gesture = "right"
        else:
            gesture = "left"

        # 左手方向反转
        if not is_right_hand:
            gesture = "left" if gesture == "right" else "right"

        return gesture

    # --------------------------------
    # 状态查询接口
    # --------------------------------
    def get_status(self):
        if self.state == "READY":
            return "READY"
        else:
            remain = self.debounce_time - (time.time() - self.last_trigger_time)
            remain = max(0, round(remain, 1))
            return f"Ready in {remain}s"

    # --------------------------------
    # 内部方法
    # --------------------------------
    def _can_trigger(self):
        if self.state == "READY":
            return True

        if time.time() - self.last_trigger_time > self.debounce_time:
            self.state = "READY"
            return True

        return False

    def _trigger(self):
        self.state = "COOLDOWN"
        self.last_trigger_time = time.time()

    # --------------------------------
    # 轨迹绘制（可选）
    # --------------------------------
    def draw_trajectory(self, frame, y_pos=50):
        """
        在画面上绘制水平轨迹线
        y_pos: 绘制高度
        """
        if len(self.trajectory) < 2:
            return

        for i in range(1, len(self.trajectory)):
            pt1 = (self.trajectory[i-1], y_pos)
            pt2 = (self.trajectory[i], y_pos)
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    # --------------------------------
    # 扩展接口（预留）
    # --------------------------------
    def volume_up(self):
        pass

    def volume_down(self):
        pass

    def brightness_up(self):
        pass

    def brightness_down(self):
        pass