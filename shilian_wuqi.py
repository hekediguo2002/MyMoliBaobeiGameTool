"""武器试炼模块"""

import os
import time
from playwright.sync_api import Page

from image_utils import (
    click_by_image,
    find_all_image_positions,
    take_screenshot,
    click_client_center,
)
from config import TEMPLATES_DIR, VIEWPORT_WIDTH, VIEWPORT_HEIGHT


def shilian_wuqi(page: Page) -> None:
    """
    执行武器试炼扫荡流程。

    流程：
        1. 点击冒险图标
        2. 点击试炼
        3. 点击进入图标
        4. 循环点击中间的扫荡按钮 → 检测结束标志 / 点击正中央
    """
    print("开始执行武器试炼流程...")

    screenshot_path = "temp_shilian_wuqi.png"

    # 1. 查找并点击冒险图标
    try:
        if not click_by_image(page, "冒险图标.png", timeout=10000):
            print("未找到冒险图标，流程结束")
            return
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/冒险图标.png")
        return
    print("已点击冒险图标")
    time.sleep(1)

    # 2. 查找并点击试炼
    try:
        if not click_by_image(page, "试炼.png", timeout=10000):
            print("未找到试炼，流程结束")
            return
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/试炼.png")
        return
    print("已点击试炼")
    time.sleep(3)

    # 3. 查找并点击进入图标（找正中间的那个）
    enter_path = os.path.join(TEMPLATES_DIR, "进入图标.png")
    try:
        take_screenshot(page, screenshot_path)
        enter_matches = find_all_image_positions(
            screenshot_path, enter_path, threshold=0.8
        )
        if not enter_matches:
            print("未找到进入图标，流程结束")
            return
        # 取正中间的
        enter_sorted = sorted(enter_matches, key=lambda m: m[0])
        middle = enter_sorted[len(enter_sorted) // 2]
        x, y, confidence = middle
        print(f"点击正中间的进入图标: ({x}, {y}), 置信度={confidence:.3f}")
        page.mouse.click(x, y)
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/进入图标.png")
        return
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
    print("已进入图标")

    # 4. 循环扫荡
    saodang_path = os.path.join(TEMPLATES_DIR, "扫荡.png")
    end_path = os.path.join(TEMPLATES_DIR, "武器试炼结束.png")    
    loop_count = 0

    while True:
        loop_count += 1
        try:
            # 截图找扫荡按钮
            take_screenshot(page, screenshot_path)
            matches = find_all_image_positions(
                screenshot_path, saodang_path, threshold=0.8
            )

            if not matches:
                print(f"第 {loop_count} 轮：未找到扫荡按钮，流程结束")
                break

            # 取中间的（按 x 坐标排序后取中间位置）
            matches_sorted = sorted(matches, key=lambda m: m[0])
            middle = matches_sorted[len(matches_sorted) // 2]
            x, y, confidence = middle
            print(f"第 {loop_count} 轮：点击中间的扫荡按钮: ({x}, {y}), 置信度={confidence:.3f}")
            page.mouse.click(x, y)

            time.sleep(3)

            # 重新截图检查是否结束
            take_screenshot(page, screenshot_path)
            end_matches = find_all_image_positions(
                screenshot_path, end_path, threshold=0.8
            )
            if end_matches:
                print(f"第 {loop_count} 轮：检测到武器试炼结束")
                # 点击取消图标关闭结算弹窗
                try:
                    if click_by_image(page, "取消图标.png", timeout=5000):
                        print("已点击取消图标")
                    else:
                        print("未找到取消图标")

                    time.sleep(1)
                    if click_by_image(page, "武器试炼关闭按钮.png", timeout=5000):
                        print("已点击武器试炼关闭按钮")
                    else:
                        print("未找到武器试炼关闭按钮")

                    time.sleep(1)
                    if click_by_image(page, "武器试炼关闭按钮.png", timeout=5000):
                        print("已点击武器试炼关闭按钮")
                    else:
                        print("未找到武器试炼关闭按钮")
                except FileNotFoundError:
                    print("[Error] 模板文件不存在: templates/取消图标.png")
                break

            # 未结束，点击屏幕正中央            
            print(f"第 {loop_count} 轮：点击屏幕正中央空白处")
            click_client_center(page)
            time.sleep(1)
        except FileNotFoundError as e:
            print(f"[Error] 模板文件不存在: {e}")
            break
        finally:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

    # 最后一步关闭武器试炼
    time.sleep(1)
    try:
        if not click_by_image(page, "冒险图标.png", timeout=10000):
            print("未找到冒险图标，流程结束")
            return
    except FileNotFoundError:
        print("[Error] 模板文件不存在: templates/冒险图标.png")
        return       
    print("武器试炼流程执行完毕")
