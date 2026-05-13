"""时波之祠模块"""

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
    find_all_image_positions,
    find_image_position,
    find_template_on_page,
    image_exists,
    take_screenshot,
    waitforfight,
    waitforfighttoend,
)


def shibozhici(page: Page) -> None:
    """
    执行时波之祠扫荡流程。
    """
    print("开始执行时波之祠流程...")

    # 1. 点击冒险图标
    if click_by_image(page, "冒险图标.png", timeout=10000):
        print("已点击冒险图标")
    else:
        print("未找到冒险图标")
    time.sleep(1)

    # 2. 点击时波之祠
    if click_by_image(page, "时波之祠.png", timeout=10000):
        print("已点击时波之祠")
    else:
        print("未找到时波之祠")
    time.sleep(1)

    # 3. 点击扫荡
    if click_by_image(page, "扫荡.png", timeout=10000):
        print("已点击扫荡")
    else:
        print("未找到扫荡")
    time.sleep(3)

    # 4. 点击屏幕正中央
    click_client_center(page)
    print("已点击屏幕正中央")
    time.sleep(1)

    # 5. 点击时波之祠_海神祭坛
    if click_by_image(page, "时波之祠_海神祭坛.png", timeout=10000):
        print("已点击时波之祠_海神祭坛")
    else:
        print("未找到时波之祠_海神祭坛")
    time.sleep(1)

    # 6. 点击扫荡
    if click_by_image(page, "扫荡.png", timeout=10000):
        print("已点击扫荡")
    else:
        print("未找到扫荡")
    time.sleep(3)

    # 7. 点击屏幕正中央  
    click_client_center(page)
    print("已点击屏幕正中央")
    time.sleep(1)

    # 8. 点击武器试炼关闭按钮，关闭界面
    if click_by_image(page, "武器试炼关闭按钮.png", timeout=10000):
        print("已点击武器试炼关闭按钮，界面已关闭")
    else:
        print("未找到武器试炼关闭按钮")
    time.sleep(1)

    if click_by_image(page, "冒险图标.png", timeout=10000):
        print("已点击冒险图标")
    else:
        print("未找到冒险图标")
    time.sleep(0.5)

    print("时波之祠流程执行完毕")
