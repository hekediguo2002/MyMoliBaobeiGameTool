"""自动截图模块

每3秒截取一次屏幕，保存到 resource 目录。
用法:
    from screenshot import screenshot_loop, stop_screenshot
    # 启动循环（阻塞式）
    screenshot_loop(page)
    # 从外部调用 stop_screenshot() 可停止循环
"""

import os
import time
from datetime import datetime

from playwright.sync_api import Page

# 截图保存目录
RESOURCE_DIR = "resource"
# 截图间隔（秒）
INTERVAL = 3

_running = False


def screenshot_loop(page: Page, max_count: int = 0) -> None:
    """
    循环截图。阻塞式运行，直到调用 stop_screenshot() 或达到 max_count。

    Args:
        page: Playwright Page 实例
        max_count: 最大截图次数，0 表示无限循环
    """
    global _running
    os.makedirs(RESOURCE_DIR, exist_ok=True)
    _running = True
    count = 0

    print(f"[Screenshot] 截图循环已启动，每 {INTERVAL} 秒保存到 {RESOURCE_DIR}/")

    while _running:
        if max_count > 0 and count >= max_count:
            break

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(RESOURCE_DIR, filename)
            page.screenshot(path=filepath, full_page=False)
            print(f"[Screenshot] 已保存: {filepath}")
        except Exception as e:
            print(f"[Screenshot] 截图失败: {e}")

        count += 1
        time.sleep(INTERVAL)

    print("[Screenshot] 截图循环已结束")


def stop_screenshot() -> None:
    """停止截图循环。"""
    global _running
    _running = False
    print("[Screenshot] 已发送停止信号")
