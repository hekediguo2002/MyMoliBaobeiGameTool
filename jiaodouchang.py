"""角斗场模块"""

import os
import time
from playwright.sync_api import Page

from image_utils import (
    click_by_image,
    find_all_image_positions,
    take_screenshot,
    waitforfight,
    waitforfighttoend,
    find_image_position,
    click_client_center,
    image_exists,
)
from config import TEMPLATES_DIR


def jiaodouchang(page: Page) -> None:
    """
    执行角斗场挑战流程。

    流程：
        1. 点击竞技图标
        2. 点击角斗场图标
        3. 循环点击最右边的挑战按钮 → 等待战斗开始 → 等待战斗结束
        4. 找不到挑战按钮时结束
    """
    print("开始执行角斗场流程...")

    # 1. 查找并点击竞技图标
    try:
        if not click_by_image(page, "竞技图标.png", timeout=10000):
            print("未找到竞技图标，流程结束")
            return
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/竞技图标.png")
        return
    print("已点击竞技图标")
    time.sleep(1)

    # 2. 查找并点击角斗场图标
    try:
        if not click_by_image(page, "角斗场图标.png", timeout=10000):
            print("未找到角斗场图标，流程结束")
            return
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/角斗场图标.png")
        return
    print("已点击角斗场图标")
    time.sleep(2)
   

    # 3. 循环挑战：找最右边的挑战按钮
    challenge_btn_path = os.path.join(TEMPLATES_DIR, "挑战按钮.png")
    while True:
        screenshot_path = "temp_jiaodouchang.png"
        try:
             # 先检查是否没有挑战次数了
            if image_exists(page, "角斗场_没有挑战次数了.png",1.0):
                print("检测到没有挑战次数了，流程结束,点击关闭按钮")   
                click_by_image(page, "武器试炼关闭按钮.png")         
                break

            take_screenshot(page, screenshot_path)

            matches = find_all_image_positions(
                screenshot_path, challenge_btn_path, threshold=0.8
            )

            if not matches:
                print("未找到挑战按钮，角斗场流程结束")
                break

            # 取最右边的（x 坐标最大）
            rightmost = max(matches, key=lambda m: m[0])
            x, y, confidence = rightmost
            print(f"点击最右边的挑战按钮: ({x}, {y}), 置信度={confidence:.3f}")
            page.mouse.click(x, y)

            time.sleep(1.5)

            # 检测6次挑战次数是否已经结束
            take_screenshot(page, screenshot_path)
            huichengImage = os.path.join(TEMPLATES_DIR, "回城.png")
            ret = find_image_position(screenshot_path,huichengImage)
            if ret is not None:
                print("检测到回城按钮，6次挑战次数可能已经用完")
                break

            # 等待战斗开始
            waitforfight(page)

            # 等待战斗结束
            waitforfighttoend(page)

            # 点击屏幕正中央空白处，继续下一轮挑战
            click_client_center(page)

            time.sleep(1)
        except FileNotFoundError:
            print("[Error] 模板文件不存在: templates/挑战按钮.png")
            break
        finally:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

    print("角斗场流程执行完毕")
