"""图片匹配测试脚本

用于分析模板匹配失败的原因。
用法: python test.py
"""

import os
import cv2
import numpy as np

from config import TEMPLATES_DIR, IMAGE_MATCH_THRESHOLD


def test_match(screenshot_path: str, template_name: str):
    """测试单张截图与模板的匹配情况。"""
    template_path = os.path.join(TEMPLATES_DIR, template_name)

    print(f"\n{'='*60}")
    print(f"测试: {template_name}")
    print(f"{'='*60}")

    if not os.path.exists(screenshot_path):
        print(f"[错误] 截图不存在: {screenshot_path}")
        return
    if not os.path.exists(template_path):
        print(f"[错误] 模板不存在: {template_path}")
        return

    scr = cv2.imread(screenshot_path)
    tmpl = cv2.imread(template_path)

    if scr is None or tmpl is None:
        print("[错误] 图片读取失败")
        return

    print(f"截图尺寸 : {scr.shape[1]} x {scr.shape[0]} (宽 x 高)")
    print(f"模板尺寸 : {tmpl.shape[1]} x {tmpl.shape[0]} (宽 x 高)")
    print(f"宽比     : {scr.shape[1] / tmpl.shape[1]:.2f}")
    print(f"高比     : {scr.shape[0] / tmpl.shape[0]:.2f}")
    print(f"匹配阈值 : {IMAGE_MATCH_THRESHOLD}")

    # 1. 直接匹配（不缩放）
    if tmpl.shape[0] <= scr.shape[0] and tmpl.shape[1] <= scr.shape[1]:
        result = cv2.matchTemplate(scr, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        print(f"\n[直接匹配] 最佳值: {max_val:.4f} @ {max_loc}")
    else:
        print("\n[直接匹配] 模板比截图大，跳过")

    # 2. 多尺度匹配（与 image_utils.find_image_position 完全一致）
    scales = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0,
              1.05, 1.1, 1.15, 1.2, 1.3, 1.4, 1.5]
    best_val = -1.0
    best_loc = None
    best_scale = 1.0
    best_w, best_h = 0, 0

    for scale in scales:
        resized = cv2.resize(tmpl, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        t_h, t_w = resized.shape[:2]
        if t_h > scr.shape[0] or t_w > scr.shape[1]:
            continue
        result = cv2.matchTemplate(scr, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > best_val:
            best_val = max_val
            best_loc = max_loc
            best_scale = scale
            best_w, best_h = t_w, t_h

    print(f"\n[多尺度匹配] 最佳值: {best_val:.4f}")
    print(f"             最佳尺度: {best_scale:.2f}x")
    print(f"             最佳位置: {best_loc}")
    print(f"             中心坐标: ({best_loc[0] + best_w // 2}, {best_loc[1] + best_h // 2})")

    if best_val >= IMAGE_MATCH_THRESHOLD:
        print(f"\n[结果] ✅ 匹配成功 (超过阈值 {IMAGE_MATCH_THRESHOLD})")
    else:
        print(f"\n[结果] ❌ 匹配失败 (未达到阈值 {IMAGE_MATCH_THRESHOLD})")

    # 3. 可视化：在截图上标注匹配位置
    vis = scr.copy()
    if best_loc is not None:
        top_left = best_loc
        bottom_right = (top_left[0] + best_w, top_left[1] + best_h)
        color = (0, 255, 0) if best_val >= IMAGE_MATCH_THRESHOLD else (0, 0, 255)
        cv2.rectangle(vis, top_left, bottom_right, color, 2)
        cv2.putText(vis, f"{best_val:.3f} @ {best_scale}x",
                    (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    debug_dir = "debug"
    os.makedirs(debug_dir, exist_ok=True)
    out_path = os.path.join(debug_dir, f"test_vis_{template_name}")
    cv2.imwrite(out_path, vis)
    print(f"\n[可视化] 已保存到: {out_path}")


def test_all_templates(screenshot_path: str):
    """用同一张截图测试所有模板。"""
    print(f"\n{'#'*60}")
    print(f"批量测试所有模板")
    print(f"截图: {screenshot_path}")
    print(f"{'#'*60}")

    if not os.path.exists(TEMPLATES_DIR):
        print(f"[错误] 模板目录不存在: {TEMPLATES_DIR}")
        return

    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".png")]
    print(f"发现 {len(templates)} 个模板:\n  " + "\n  ".join(sorted(templates)))

    for tmpl_name in sorted(templates):
        test_match(screenshot_path, tmpl_name)


if __name__ == "__main__":
    # 测试指定截图与指定模板
    screenshot = "debug/fail_角斗场_没有挑战次数了.png"
    template = "魔族入侵_没有挑战次数了.png"

    test_match(screenshot, template)

    # 如果想测试所有模板，取消下面注释
    # test_all_templates(screenshot)
