"""魔族入侵模块"""

import os
import time
from playwright.sync_api import Page

import image_utils
from config import TEMPLATES_DIR,VIEWPORT_WIDTH, VIEWPORT_HEIGHT


def mozuruqin(page: Page) -> None:
    """
    执行魔族入侵挑战流程。

    流程：
        1. 点击家族图标
        2. 点击魔族入侵图标
        3. 循环点击魔族入侵出战图标 → 检测结束标志 / 等待战斗并继续
    """
    print("开始执行魔族入侵流程...")

    # 1. 查找并点击家族图标
    if not image_utils.click_by_image(page, "家族图标.png", timeout=10000):
        print("未找到家族图标，流程结束")
        return
    print("已点击家族图标")
    time.sleep(4)    

    # if image_utils.image_exists(page, "魔族入侵_没有挑战次数了.png", 1.0):
    #     print("魔族入侵没有挑战次数了，流程结束")
    #     return
    
    # 2. 查找并点击魔族入侵图标
    if not image_utils.click_by_image(page, "魔族入侵图标.png", timeout=10000):
        print("未找到魔族入侵图标，流程结束")
        return
    print("已点击魔族入侵图标")
    time.sleep(1)

    # 3. 循环出战
    chuzhan_path = os.path.join(TEMPLATES_DIR, "魔族入侵出战图标.png")
    end_path = os.path.join(TEMPLATES_DIR, "魔族入侵结束图标.png")
    screenshot_path = "temp_mozuruqin.png"
    loop_count = 0

    while True:
        loop_count += 1

        # 检查还有没有挑战次数了
        # if image_utils.image_exists(page, "魔族入侵_挑战次数没有了2.png", 1.0):
        #     print(f"第 {loop_count} 轮：检测到没有挑战次数了，流程结束")           
        #     break

        # 点击魔族入侵出战图标
        image_utils.click_by_image(page, "魔族入侵出战图标.png", timeout=10000)
        print(f"第 {loop_count} 轮：已点击魔族入侵出战图标")
        time.sleep(1)

        # 点击出战后可能没有挑战次数了
        if image_utils.image_exists(page, "取消图标.png"):
            print(f"第 {loop_count} 轮：检查到取消图标，没有挑战次数了，流程结束")
            image_utils.click_by_image(page, "取消图标.png", timeout=3000)
            time.sleep(1)
            break

        # 未结束，等待战斗开始
        image_utils.waitforfight(page)

        # 等待战斗结束
        image_utils.waitforfighttoend(page)

        # 点击空白区域
        image_utils.click_client_center(page)

        # 等待战斗结束后继续下一轮
        print(f"第 {loop_count} 轮：战斗结束，继续下一轮")

        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    print("准备关闭按钮")
    if image_utils.image_exists(page, "武器试炼关闭按钮.png"):           
        image_utils.click_by_image(page, "武器试炼关闭按钮.png", timeout=3000)
        time.sleep(1)
    
    if image_utils.image_exists(page, "武器试炼关闭按钮.png"):           
        image_utils.click_by_image(page, "武器试炼关闭按钮.png", timeout=3000)
        time.sleep(1)            

    print("魔族入侵流程执行完毕")
