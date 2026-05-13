"""图片识别工具模块"""

import os
from typing import Tuple, Optional
import cv2
import numpy as np
import time

from config import IMAGE_MATCH_THRESHOLD, TEMPLATES_DIR,VIEWPORT_WIDTH,VIEWPORT_HEIGHT


def take_screenshot(page, path: str = "screenshot.png") -> str:
    """
    截取当前页面屏幕并保存。

    Args:
        page: Playwright Page 实例
        path: 截图保存路径

    Returns:
        截图文件的绝对路径
    """
    # 短暂等待让 Canvas 动画/渲染稳定，减少闪动导致的匹配失败
    import time
    time.sleep(0.3)
    page.screenshot(path=path, full_page=False)
    return os.path.abspath(path)


def find_image_position(
    screenshot_path: str,
    template_path: str,
    threshold: float = IMAGE_MATCH_THRESHOLD,
) -> Optional[Tuple[int, int]]:
    """
    在截图中查找模板图片的中心坐标。

    Args:
        screenshot_path: 截图文件路径
        template_path: 模板图片路径
        threshold: 匹配阈值，0~1，越高要求越严格

    Returns:
        (x, y) 中心坐标，未匹配到返回 None
    """
    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"截图文件不存在: {screenshot_path}")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    # 读取图片
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screenshot is None or template is None:
        return None

    # 多尺度模板匹配：解决 Canvas 缩放导致分辨率不一致的问题
    best_val = -1.0
    best_loc = None
    best_w, best_h = 0, 0

    scales = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5]
    for scale in scales:
        resized = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        t_h, t_w = resized.shape[:2]

        # 跳过比截图还大的模板
        if t_h > screenshot.shape[0] or t_w > screenshot.shape[1]:
            continue

        result = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_val:            
            best_val = max_val
            best_loc = max_loc
            best_w, best_h = t_w, t_h

    if best_val < threshold:
        print(f"[Debug] 多尺度最佳匹配值: {best_val:.3f} (阈值: {threshold})")
        return None

    # 计算中心坐标
    center_x = best_loc[0] + best_w // 2
    center_y = best_loc[1] + best_h // 2
    print(f"[Debug] 匹配成功: 尺度倍率约 {best_w / template.shape[1]:.2f}x, 置信度={best_val:.3f} 图片:{template_path}")

    return center_x, center_y


def find_all_image_positions(
    screenshot_path: str,
    template_path: str,
    threshold: float = IMAGE_MATCH_THRESHOLD,
    nms_threshold: float = 0.3,
) -> list[tuple[int, int, float]]:
    """
    在截图中查找所有匹配模板的位置（支持多目标）。

    Args:
        screenshot_path: 截图文件路径
        template_path: 模板图片路径
        threshold: 匹配阈值
        nms_threshold: 非极大值抑制阈值，0~1，越大越宽松

    Returns:
        [(x, y, confidence), ...] 按置信度降序排列，未匹配到返回空列表
    """
    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"截图文件不存在: {screenshot_path}")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screenshot is None or template is None:
        return []

    matches = []
    scales = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5]

    for scale in scales:
        resized = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        t_h, t_w = resized.shape[:2]

        if t_h > screenshot.shape[0] or t_w > screenshot.shape[1]:
            continue

        result = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)

        for pt in zip(*loc[::-1]):
            confidence = result[pt[1], pt[0]]
            center_x = pt[0] + t_w // 2
            center_y = pt[1] + t_h // 2
            matches.append((center_x, center_y, confidence, t_w, t_h))

    if not matches:
        return []

    # 按置信度降序排列，优先保留高置信度
    matches = sorted(matches, key=lambda x: x[2], reverse=True)

    # 非极大值抑制（NMS）：去除邻近重复框
    def _iou(box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        xi1 = max(x1 - w1 // 2, x2 - w2 // 2)
        yi1 = max(y1 - h1 // 2, y2 - h2 // 2)
        xi2 = min(x1 + w1 // 2, x2 + w2 // 2)
        yi2 = min(y1 + h1 // 2, y2 + h2 // 2)
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area
        return inter_area / union_area if union_area > 0 else 0

    filtered = []
    for cx, cy, conf, tw, th in matches:
        box = (cx, cy, tw, th)
        if all(_iou(box, (fx, fy, fw, fh)) < nms_threshold for fx, fy, _, fw, fh in filtered):
            filtered.append((cx, cy, conf, tw, th))

    return [(int(cx), int(cy), float(conf)) for cx, cy, conf, _, _ in filtered]


def find_template_on_page(
    page,
    template_name: str,
    threshold: float = IMAGE_MATCH_THRESHOLD,
) -> Optional[Tuple[int, int]]:
    """
    在当前页面查找指定模板图片的位置。

    Args:
        page: Playwright Page 实例
        template_name: 模板文件名（相对于 TEMPLATES_DIR）
        threshold: 匹配阈值

    Returns:
        (x, y) 中心坐标，未匹配到返回 None
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    screenshot_path = "temp_screenshot.png"

    try:
        take_screenshot(page, screenshot_path)
        result = find_image_position(screenshot_path, template_path, threshold)

        # 调试：匹配失败时保留截图，方便排查分辨率/缩放问题
        if result is None:
            debug_dir = "debug"
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, f"fail_{template_name}")
            os.replace(screenshot_path, debug_path)
            print(f"[Debug] 匹配失败，截图已保存: {debug_path}")
            # 打印尺寸信息辅助排查
            if os.path.exists(template_path):
                tmpl = cv2.imread(template_path)
                scr = cv2.imread(debug_path)
                if tmpl is not None and scr is not None:
                    print(f"[Debug] 模板尺寸: {tmpl.shape[1]}x{tmpl.shape[0]}, 截图尺寸: {scr.shape[1]}x{scr.shape[0]}")

        return result
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)


def image_exists(
    page,
    template_name: str,
    threshold: float = IMAGE_MATCH_THRESHOLD,
) -> bool:
    """
    判断指定模板图片是否存在于当前页面中。

    Args:
        page: Playwright Page 实例
        template_name: 模板文件名
        threshold: 匹配阈值

    Returns:
        图片是否存在（True/False）
    """
    try:
        return find_template_on_page(page, template_name, threshold) is not None
    except FileNotFoundError:
        return False


def click_by_image(
    page,
    template_name: str,
    threshold: float = IMAGE_MATCH_THRESHOLD,
    timeout: int = 10000,
) -> bool:
    """
    通过图片识别找到目标并点击。

    Args:
        page: Playwright Page 实例
        template_name: 模板文件名
        threshold: 匹配阈值
        timeout: 最大等待时间（毫秒）

    Returns:
        是否点击成功
    """
    

    start_time = time.time() * 1000
    while time.time() * 1000 - start_time < timeout:
        pos = find_template_on_page(page, template_name, threshold)
        if pos is not None:
            x, y = pos
            page.mouse.click(x, y)
            return True
        time.sleep(0.5)

    return False

# 等待战斗开始的函数，默认检测战斗标志出现
def waitforfight(
    page,
    template_name: str = "战斗标志.png",
    threshold: float = IMAGE_MATCH_THRESHOLD,
    timeout: int = 10000,
    check_interval: float = 1.0,
) -> Optional[Tuple[int, int]]:
    """
    循环等待页面中出现指定模板图片。

    Args:
        page: Playwright Page 实例
        template_name: 模板文件名
        threshold: 匹配阈值
        timeout: 最大等待时间（毫秒）
        check_interval: 每次检测间隔（秒）

    Returns:
        (x, y) 中心坐标，超时未找到返回 None
    """
    import time

    start_time = time.time() * 1000
    while time.time() * 1000 - start_time < timeout:
        try:
            pos = find_template_on_page(page, template_name, threshold)
            if pos is not None:
                print(f"[WaitForFight] 检测到 {template_name}，坐标: {pos}")
                time.sleep(0.5)
                return pos
        except FileNotFoundError:
            print(f"[WaitForFight] 模板文件不存在: {template_name}")
            return None
        time.sleep(check_interval)

    print(f"[WaitForFight] 等待超时 ({timeout}ms)，未检测到 {template_name}")
    return None


# 等待战斗结束的函数，默认检测回城按钮出现
def waitforfighttoend(
    page,
    template_name: str = "战斗标志.png",
    threshold: float = IMAGE_MATCH_THRESHOLD,
    timeout: int = 600000,
    check_interval: float = 3.0,
) -> bool:
    

    start_time = time.time() * 1000
    while time.time() * 1000 - start_time < timeout:
        try:
            pos = find_template_on_page(page, template_name, threshold)
            if pos is None:
                print("战斗已经结束")
                time.sleep(2.0)
                return True
        except FileNotFoundError:
            print(f"[WaitForNotFight] 模板文件不存在: {template_name}")
            return None
        time.sleep(check_interval)

    print(f"[WaitForNotFight] 等待超时 ({timeout}ms)，未检测到 {template_name}")
    return False


# 点击屏幕中心空白位置
def click_client_center(page):    
    center_x = VIEWPORT_WIDTH // 2
    center_y = VIEWPORT_HEIGHT // 2
    center_y += 100
    page.mouse.click(center_x, center_y)
    print(f"[ClickCenter] 已点击页面正中央: ({center_x}, {center_y})")
    time.sleep (1)

# 点击屏幕最左边空白区域
def click_client_left(page):    
    center_x = 1
    center_y = VIEWPORT_HEIGHT // 2
    center_y += 100
    page.mouse.click(center_x, center_y)
    print(f"[ClickLeft] 已点击页面最左边: ({center_x}, {center_y})")
    time.sleep (1)
    