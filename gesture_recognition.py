      
"""
gesture_recognition.py - 手势识别模块

符合 GestureSlide 系统接口文档规范
提供手部关键点检测和食指尖坐标获取功能

类路径: from gesture_recognition import GestureRecognizer

依赖: pip install mediapipe opencv-python numpy
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple


class GestureRecognizer:
    """
    手势识别模块
    
    功能说明:
        使用 MediaPipe Hands 模型检测手部关键点，
        获取食指尖位置，并判断手的左右。
    
    使用示例:
        recognizer = GestureRecognizer()
        
        while True:
            frame = camera.read()
            x, y, is_right_hand = recognizer.get_index_finger_tip(frame)
            if x is not None:
                print(f"食指尖位置: ({x}, {y}), 右手: {is_right_hand}")
    """
    
    # 手部关键点索引常量
    WRIST = 0
    THUMB_TIP = 4
    INDEX_FINGER_TIP = 8
    
    def __init__(self):
        """
        初始化 MediaPipe Hands 模型
        
        内部配置:
            - static_image_mode=False  # 视频模式
            - max_num_hands=1          # 最多检测一只手
            - min_detection_confidence=0.5
            - min_tracking_confidence=0.5
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,      # 视频模式
            max_num_hands=1,              # 最多检测一只手
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 存储最新的检测结果供 draw_hand 使用
        self._last_results = None
        self._last_image_shape = None
    
    def get_index_finger_tip(self, image: np.ndarray) -> Tuple[Optional[int], Optional[int], Optional[bool]]:
        """
        从图像帧中检测食指尖位置，并判断是否为右手
        
        功能说明:
            检测图像中手部的食指尖位置，并根据拇指尖与手腕的 x 坐标
            关系判断是否为右手。
        
        Args:
            image (np.ndarray): OpenCV 读取的 BGR 格式图像帧
        
        Returns:
            成功时: (x: int, y: int, is_right_hand: bool)
                - x: 食指尖的像素 x 坐标
                - y: 食指尖的像素 y 坐标  
                - is_right_hand: True 表示右手，False 表示左手
            未检测到手时: (None, None, None)
        
        坐标系说明:
            原点位于图像左上角；x 向右递增，y 向下递增。
        
        手别判断逻辑:
            比较拇指尖（landmark 4）与手腕（landmark 0）的 x 坐标；
            若 thumb.x > wrist.x，判定为右手。
        
        示例:
            >>> recognizer = GestureRecognizer()
            >>> x, y, is_right = recognizer.get_index_finger_tip(frame)
            >>> if x is not None:
            ...     print(f"位置: ({x}, {y}), 右手: {is_right}")
            位置: (320, 240), 右手: True
        """
        if image is None:
            return None, None, None
        
        h, w = image.shape[:2]
        
        # 转换为 RGB 格式（MediaPipe 需要 RGB）
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 进行手部检测
        results = self.hands.process(image_rgb)
        
        # 存储结果供 draw_hand 使用
        self._last_results = results
        self._last_image_shape = (h, w)
        
        # 检查是否检测到手
        if not results.multi_hand_landmarks:
            return None, None, None
        
        # 获取第一只手的关键点
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # 获取食指尖坐标（转换为像素坐标）
        index_tip = hand_landmarks.landmark[self.INDEX_FINGER_TIP]
        x = int(index_tip.x * w)
        y = int(index_tip.y * h)
        
        # 判断左右手：比较拇指尖与手腕的 x 坐标
        thumb_tip = hand_landmarks.landmark[self.THUMB_TIP]
        wrist = hand_landmarks.landmark[self.WRIST]
        
        # 若 thumb.x > wrist.x，判定为右手
        is_right_hand = thumb_tip.x > wrist.x
        
        return x, y, is_right_hand
    
    def draw_hand(self, image: np.ndarray) -> np.ndarray:
        """
        在图像上绘制所有手部关键点及其连接线
        
        功能说明:
            绘制手部骨架，便于调试和可视化。
            需要先调用 get_index_finger_tip() 进行检测。
        
        应用场景:
            开发阶段开启以验证识别准确性；
            发布版本可关闭以提升性能。
        
        Args:
            image (np.ndarray): OpenCV 读取的 BGR 格式图像帧
        
        Returns:
            np.ndarray: 标注后的图像
        """
        output_image = image.copy()
        
        if self._last_results is None or not self._last_results.multi_hand_landmarks:
            return output_image
        
        # 绘制所有检测到的手
        for hand_landmarks in self._last_results.multi_hand_landmarks:
            # 绘制骨架
            self.mp_drawing.draw_landmarks(
                output_image,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # 高亮食指尖
            if self._last_image_shape:
                h, w = self._last_image_shape
                index_tip = hand_landmarks.landmark[self.INDEX_FINGER_TIP]
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)
                cv2.circle(output_image, (x, y), 10, (0, 255, 0), -1)
        
        return output_image
    
    def release(self):
        """释放资源"""
        self.hands.close()


# ==================== 测试代码 ====================

def main():
    """
    测试模块 - 手势识别演示
    """
    print("=" * 60)
    print(" " * 15 + "手势识别模块测试")
    print("=" * 60)
    print("\n功能说明:")
    print("  - 检测食指尖坐标")
    print("  - 判断左右手")
    print("  - 绘制手部骨架")
    print("\n操作说明:")
    print("  - 按 'q' 退出")
    print("=" * 60)
    
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 错误: 无法打开摄像头!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("\n摄像头已启动...\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 镜像翻转
        frame = cv2.flip(frame, 1)
        
        # 检测食指尖
        x, y, is_right_hand = recognizer.get_index_finger_tip(frame)
        
        # 绘制手部骨架
        display_img = recognizer.draw_hand(frame)
        
        # 显示检测信息
        if x is not None:
            hand_str = "右手" if is_right_hand else "左手"
            info_text = f"食指尖: ({x}, {y}) - {hand_str}"
            cv2.putText(display_img, info_text, (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        else:
            cv2.putText(display_img, "未检测到手", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        
        cv2.imshow('GestureRecognizer Test', display_img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    recognizer.release()
    
    print("\n测试结束")


if __name__ == "__main__":
    main()

    