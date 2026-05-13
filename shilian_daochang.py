"""试炼道场模块"""

import os
import time
from playwright.sync_api import Page

from config import (
    BROWSER_EXECUTABLE_PATH,
    DEFAULT_NAVIGATION_TIMEOUT,
    DEFAULT_TIMEOUT,
    GAME_URL,
    IMAGE_MATCH_THRESHOLD,
    PHONE_NUMBER,
    PASSWORD,
    TEMPLATES_DIR,
    VIEWPORT_HEIGHT,
    VIEWPORT_WIDTH,
)
from image_utils import (
    click_by_image,
    click_client_center,
    click_client_left,
    find_all_image_positions,
    find_image_position,
    find_template_on_page,
    image_exists,
    take_screenshot,
    waitforfight,
    waitforfighttoend,
)


def shilian_daochang(page: Page) -> None:
    """
    执行试炼道场流程。
    """
    print("开始执行试炼道场流程...")

    # 1. 点击冒险图标
    print("步骤1：点击冒险图标")
    click_by_image(page, "冒险图标.png", timeout=10000)
    time.sleep(1)

    # 2. 点击试炼
    print("步骤2：点击试炼")
    click_by_image(page, "试炼.png", timeout=10000)
    time.sleep(1)

    # 3. 点击最左侧的进入图标
    print("步骤3：点击最左侧的进入图标")
    enter_path = os.path.join(TEMPLATES_DIR, "进入图标.png")
    screenshot_path = "temp_shilian_daochang.png"
    take_screenshot(page, screenshot_path)
    enter_matches = find_all_image_positions(screenshot_path, enter_path, threshold=0.8)
    if enter_matches:
        leftmost = min(enter_matches, key=lambda m: m[0])
        x, y, confidence = leftmost
        print(f"点击最左侧的进入图标: ({x}, {y}), 置信度={confidence:.3f}")
        page.mouse.click(x, y)
    else:
        print("未找到进入图标")
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    time.sleep(1)

    # 4. 如果有重置进度，则重置
    print("步骤4：检查是否需要重置进度")
    if image_exists(page, "重置进度.png"):
        print("检测到重置进度，开始重置")
        click_by_image(page, "重置进度.png", timeout=10000)
        time.sleep(0.5)
        print("点击确定按钮")
        click_by_image(page, "道场试炼_确定按钮.png", timeout=10000)
        time.sleep(1)
    else:
        print("无需重置进度")

    # 5. 如果有一键扫荡，则扫荡
    print("步骤5：检查是否有一键扫荡")
    if image_exists(page, "道场试炼_一键扫荡按钮.png"):
        print("检测到一键扫荡，开始扫荡")
        click_by_image(page, "道场试炼_一键扫荡按钮.png", timeout=10000)
        time.sleep(0.5)
        click_by_image(page, "道场试炼_确定按钮.png", timeout=10000)
        time.sleep(3)
        click_client_center(page)
        time.sleep(1)
        click_client_left(page)
    else:
        print("未找到一键扫荡")
        click_client_left(page)

    # 6. 点击武器试炼关闭按钮
    print("步骤6：点击武器试炼关闭按钮")
    time.sleep(1)
    click_by_image(page, "武器试炼关闭按钮.png", timeout=10000)
    time.sleep(1)   
    click_by_image(page, "冒险图标.png", timeout=10000)
    time.sleep(1)

    print("试炼道场流程执行完毕")
