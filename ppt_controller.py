import pyautogui
import time


class PPTController:
    """
    PPT控制模块
    功能：接收指令并模拟键盘按键，实现PPT翻页
    """

    @staticmethod
    def next_slide():
        """翻到下一页"""
        try:
            pyautogui.press('right')
            print("👉 下一页")
            # logging.info("Triggered: Next Slide")  # 注释日志
        except Exception as e:
            # logging.error(f"Failed to next_slide: {e}")  # 注释日志
            PPTController.recover()

    @staticmethod
    def prev_slide():
        """翻到上一页"""
        try:
            pyautogui.press('left')
            print("👈 上一页")
            # logging.info("Triggered: Prev Slide")  # 注释日志
        except Exception as e:
            # logging.error(f"Failed to prev_slide: {e}")  # 注释日志
            PPTController.recover()

    @staticmethod
    def recover():
        """异常恢复机制"""
        print("⚠️ 控制失败，尝试重新连接...")
        time.sleep(1)
        # logging.warning("System recovery triggered")  # 注释日志

# 测试代码
if __name__ == "__main__":
    print("正在测试 PPTController...")
    print("请在 3 秒内切换到一个 PPT 窗口...")
    time.sleep(3)

    print("尝试翻下一页...")
    PPTController.next_slide()

    time.sleep(2)

    print("尝试翻上一页...")
    PPTController.prev_slide()

    print("测试结束。")