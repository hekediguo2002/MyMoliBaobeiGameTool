"""国王悬赏模块"""

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


def guowangxuanshang(page: Page) -> None:
    """
    执行国王悬赏流程。
    """
    print("开始执行国王悬赏流程...")

    # 1. 点击冒险图标
    print("步骤1：点击冒险图标")
    click_by_image(page, "冒险图标.png", timeout=10000)
    time.sleep(1)

    # 2. 点击国王悬赏
    print("步骤2：点击国王悬赏")
    click_by_image(page, "国王悬赏.png", timeout=10000)
    time.sleep(1)

    # 3. 点击国王悬赏_难度四星
    print("步骤3：点击国王悬赏_难度四星")
    click_by_image(page, "国王悬赏_难度四星.png", timeout=10000)
    time.sleep(0.5)

    # 4. 循环3次：扫荡 -> 点击屏幕中心
    for i in range(3):
        print(f"步骤4：第 {i + 1}/3 轮扫荡")
        click_by_image(page, "扫荡.png", timeout=10000)
        time.sleep(1)
        click_client_center(page)

    time.sleep(1)
    click_by_image(page, "武器试炼关闭按钮.png", timeout=10000)
    click_by_image(page, "冒险图标.png", timeout=10000)
    time.sleep(1)

    print("国王悬赏流程执行完毕")
