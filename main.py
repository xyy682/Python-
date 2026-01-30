import flet as ft
import threading
import cv2
import sys
import os
from gesture_recognition import GestureRecognizer
from motion_detection import MotionDetector
from ppt_controller import PPTController


# 打包的资源路径问题
def resource_path(relative_path):
    """获取打包后文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境的路径
    return os.path.join(os.path.abspath("."), relative_path)


class GestureSlideCore:
    def __init__(self):
        self.gesture_recognizer = GestureRecognizer()
        self.motion_detector = MotionDetector(
            min_distance=60,  # 优化阈值，减少误触
            debounce_time=1.8
        )
        self.is_running = False
        self.cap = None

    def run_pipeline(self):
        # ========== 修复：指定摄像头索引+分辨率 ==========
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 用CAP_DSHOW避免Windows摄像头卡顿
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cap.isOpened():
            return False

        self.is_running = True
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            x, y, is_right_hand = self.gesture_recognizer.get_index_finger_tip(frame)
            frame = self.gesture_recognizer.draw_hand(frame)

            if x is not None and y is not None:
                cv2.circle(frame, (x, y), 8, (0, 200, 255), -1)
                swipe_dir = self.motion_detector.detect_swipe(x, is_right_hand)
                if swipe_dir == "right":
                    PPTController.next_slide()
                elif swipe_dir == "left":
                    PPTController.prev_slide()

            cv2.imshow("GestureSlide • Real-time Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        return True


def main(page: ft.Page):
    core = GestureSlideCore()

    # 页面设置
    page.title = "GestureSlide"
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30
    page.bgcolor = "#0f172a"

    # 状态指示器
    status_dot = ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor="#f87171",
    )
    status_text = ft.Text("Ready to start", color="#9ca3af", size=14)

    def on_start(e):
        if core.is_running:
            return

        def run():
            success = core.run_pipeline()
            if not success:
                page.snack_bar = ft.SnackBar(ft.Text("❌ 摄像头打开失败，请检查摄像头是否被占用"), open=True)
                page.update()

        status_dot.bgcolor = "#4ade80"
        status_text.value = "Running • Show your index finger"
        start_btn.disabled = True
        stop_btn.disabled = False
        page.update()

        # 线程设为非守护线程，避免闪退
        threading.Thread(target=run, daemon=False).start()

    def on_stop(e):
        core.is_running = False
        status_dot.bgcolor = "#f87171"
        status_text.value = "Stopped"
        start_btn.disabled = False
        stop_btn.disabled = True
        page.update()

    # 按钮
    start_btn = ft.ElevatedButton(
        "▶ Start Recognition",
        width=220,
        height=50,
        style=ft.ButtonStyle(
            color="black",
            bgcolor="#5eead4",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=on_start,
    )

    stop_btn = ft.ElevatedButton(
        "⏹ Stop",
        width=220,
        height=50,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="#374151",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        on_click=on_stop,
        disabled=True,
    )

    # 布局
    page.add(
        ft.Column(
            [
                ft.Text("GestureSlide", size=48, weight=ft.FontWeight.BOLD, color="#4FD1C5"),
                ft.Text("Control PowerPoint with Hand Gestures", size=18, color="#9ca3af"),
                ft.Divider(height=30, color="transparent"),
                ft.Row([status_dot, status_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=40, color="transparent"),
                ft.Row([start_btn, stop_btn], spacing=20),
                ft.Divider(height=50, color="transparent"),
                ft.Text("💡 Ensure good lighting and clear hand visibility", size=12, color="#6b7280"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )


if __name__ == "__main__":
    ft.app(target=main, assets_dir=resource_path("assets"))