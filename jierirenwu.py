"""节日任务模块"""

import time
from playwright.sync_api import Page

from image_utils import (
    click_by_image,
    waitforfight,
    waitforfighttoend,
    click_client_center,
    image_exists,
)


def jierirenwu(page: Page) -> None:
    """
    执行节日任务挑战流程。

    流程：
        1. 点击节日引导1
        2. 点击节日引导2
        3. 循环点击节日挑战BOSS → 等待战斗结束
           若检测到进入图标则提前结束
    """
    print("开始执行节日任务流程...")

    # 1. 查找并点击节日引导1
    if image_exists(page, "节日_引导_1.png"):
        print("找到节日入口，点击进入")
        click_by_image(page, "节日_引导_1.png", timeout=10000)        
        time.sleep(2)
    else:
        print("未找到节日入口，可能活动已经结束")
        return    

    # 2. 查找并点击节日引导2
    click_by_image(page, "节日_引导_2.png", timeout=10000) 
    print("已点击节日_引导_2.png")
    time.sleep(1)

    # 3. 循环挑战BOSS
    loop_count = 0
    while True:
        loop_count += 1

        # 先检查是否没有挑战次数了
        if image_exists(page, "节日_挑战次数_没有了.png", 1.0):
            print(f"第 {loop_count} 轮：检测到没有挑战次数了，流程结束")            
            break

        # 先检查是否出现进入图标（提前结束标志）        
        if image_exists(page, "取消图标.png"):
            print(f"第 {loop_count} 轮：检测到取消图标，流程结束")
            click_by_image(page, "取消图标.png", timeout=10000) 
            time.sleep(1)
            break
        

        # 点击节日挑战BOSS
        if click_by_image(page, "节日_挑战_boss_1.png", timeout=10000):
            time.sleep(1)
            if image_exists(page, "取消图标.png"):
                print(f"第 {loop_count} 轮：检测到取消图标，流程结束")
                click_by_image(page, "取消图标.png", timeout=10000) 
                time.sleep(1)
                break
            # 等待战斗开始和结束
            waitforfight(page)
            waitforfighttoend(page)
            click_client_center(page)  
        else:
            print(f"第 {loop_count} 轮：未找到节日挑战BOSS图标，等待继续")
                  
        time.sleep(1)

    
    click_by_image(page, "节日_引导_关闭_1.png", timeout=10000)
    time.sleep(1)
    click_by_image(page, "节日_引导_关闭_1.png", timeout=10000)
    time.sleep(1)
    print("节日任务流程执行完毕")
