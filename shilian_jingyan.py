"""节日任务模块"""

import time
import os
from playwright.sync_api import Page

from image_utils import (
    click_by_image,
    waitforfight,
    waitforfighttoend,
    click_client_center,
    image_exists,
    find_all_image_positions,
    take_screenshot,
    click_client_left
)
from config import TEMPLATES_DIR,VIEWPORT_WIDTH, VIEWPORT_HEIGHT

def shilian_jingyan(page: Page) -> None:
    
    print("开始经验试炼任务流程...")

    screenshot_path = "temp_wuqishilian.png"
    click_by_image(page, "冒险图标.png", timeout=10000)
    print("已点击冒险")
    time.sleep(2)

    click_by_image(page, "试炼.png", timeout=10000) 
    print("已点击试炼")
    time.sleep(2)

     # 3. 查找并点击进入图标（找最右边的那个）
    enter_path = os.path.join(TEMPLATES_DIR, "进入图标.png")
    try:
        take_screenshot(page, screenshot_path)
        enter_matches = find_all_image_positions(
            screenshot_path, enter_path, threshold=0.8
        )
        if not enter_matches:
            print("未找到进入图标，流程结束")
            return
        # 取最右边的（x 坐标最大）
        rightmost = max(enter_matches, key=lambda m: m[0])
        x, y, confidence = rightmost
        print(f"点击最右边的进入图标: ({x}, {y}), 置信度={confidence:.3f}")
        page.mouse.click(x, y)
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/进入图标.png")
        return
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
    print("已进入图标")

    # 3. 循环挑战BOSS
    click_by_image(page, "一键重置.png", timeout=10000)
    time.sleep(1)

    if image_exists(page, "确定.png"):
        print("检测到有确定按钮，点击确定")
        click_by_image(page, "确定.png", timeout=10000) 
        time.sleep(1)

    if image_exists(page, "一键扫荡.png"):
        print("点击一键扫荡.png")
        click_by_image(page, "一键扫荡.png", timeout=10000) 
        time.sleep(1)
        if image_exists(page, "确定.png"):
            print("点击确定.png")
            click_by_image(page, "确定.png", timeout=5000) 
            time.sleep(1)    
            print("一键扫荡点击确定完毕，点击屏幕左侧关闭弹出框")   
            click_client_left(page)
        time.sleep(1)
        click_client_left(page)
    else:
        print("未找到一键扫荡图标，流程结束") 
    
    
    click_by_image(page, "武器试炼关闭按钮.png", timeout=10000)
    time.sleep(1)

    click_by_image(page, "冒险图标.png", timeout=10000)
    print("已点击冒险")
   
    print("节日任务流程执行完毕")
