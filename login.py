"""登录游戏模块"""

import os
import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from config import PHONE_NUMBER, PASSWORD, DEFAULT_TIMEOUT
from image_utils import click_by_image

CDP_PORT_FILE = ".browser_cdp_port"


def connect_to_existing_browser():
    """
    通过 CDP 连接到已启动的浏览器。

    Returns:
        (page, context, browser, playwright) 或 None
    """
    if not os.path.exists(CDP_PORT_FILE):
        return None

    with open(CDP_PORT_FILE, "r") as f:
        port = f.read().strip()

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
        context = browser.contexts[0]
        page = context.pages[0]
        print(f"[CDP] 已连接到已有浏览器，当前页面: {page.url}")
        return page, context, browser, playwright
    except Exception as e:
        print(f"[CDP] 连接已有浏览器失败: {e}")
        return None


def _click_by_dom_or_image(
    page: Page,
    selectors: list[str],
    template_name: str,
    description: str,
    timeout: int = 10000,
) -> bool:
    """
    优先使用 DOM 选择器点击，失败时尝试图片识别点击。

    Args:
        page: Playwright Page 实例
        selectors: DOM 选择器列表，按优先级尝试
        template_name: 图片模板文件名
        description: 元素描述（用于日志）
        timeout: 超时时间（毫秒）

    Returns:
        是否点击成功
    """
    # 策略1：尝试 DOM 选择器
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0 and element.is_visible(timeout=timeout):
                element.click()
                print(f"[DOM] 已点击: {description}")
                return True
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue

    # 策略2：图片识别兜底
    print(f"[Image] 尝试图片识别: {description} (模板: {template_name})")
    try:
        if click_by_image(page, template_name, timeout=timeout):
            print(f"[Image] 已点击: {description}")
            return True
    except FileNotFoundError as e:
        print(f"[Image] 跳过：模板文件不存在 ({e})")

    print(f"[Error] 未找到: {description}")
    return False


def _fill_input(
    page: Page,
    selectors: list[str],
    template_name: str,
    value: str,
    description: str,
    timeout: int = 10000,
) -> bool:
    """
    优先使用 DOM 选择器填充输入框，失败时尝试图片识别定位后输入。

    Args:
        page: Playwright Page 实例
        selectors: DOM 选择器列表
        template_name: 输入框模板图片名
        value: 要输入的值
        description: 元素描述
        timeout: 超时时间（毫秒）

    Returns:
        是否输入成功
    """
    # 策略1：DOM 选择器
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0 and element.is_visible(timeout=timeout):
                element.fill(value)
                print(f"[DOM] 已输入: {description}")
                return True
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue

    # 策略2：图片识别定位后点击 + 输入
    from image_utils import find_template_on_page

    print(f"[Image] 尝试图片识别输入框: {description}")
    try:
        pos = find_template_on_page(page, template_name)
    except FileNotFoundError as e:
        print(f"[Image] 跳过：模板文件不存在 ({e})")
        pos = None

    if pos is not None:
        x, y = pos
        page.mouse.click(x, y)
        time.sleep(0.2)
        page.keyboard.type(value)
        print(f"[Image] 已输入: {description}")
        return True

    print(f"[Error] 未找到输入框: {description}")
    return False

def click_login(page: Page) -> None:
     # c. 等待页面加载，关闭公告界面
    print("等待关闭公告弹窗")
    time.sleep(5)  # 公告弹窗加载较慢，多等一会    
    # 尝试图片识别关闭按钮（阈值放低一点，兼容半透明/动画状态）
    if click_by_image(page, "close_notice_btn.png", timeout=8000, threshold=0.65):
        print("[Image] 已关闭公告弹窗")
    else:
        print("未检测到公告弹窗，继续下一步")

    time.sleep(1)

    # d. 点击开始游戏按钮，等待进入游戏
    print("点击开始游戏按钮")
    start_game_selectors = [
        "text=开始游戏",
        "text=进入游戏",
        "text=立即开始",
        "button:has-text('开始')",
        "button:has-text('进入')",
        "[class*='start-game']",
        "[class*='enter-game']",
    ]
    if not _click_by_dom_or_image(
        page, start_game_selectors, "start_game_btn.png", "开始游戏按钮"
    ):
        raise TimeoutError("未找到开始游戏按钮")

    # 等待进入游戏主界面，通过检测“回城”按钮确认
    print("等待进入游戏主界面...")
    from image_utils import find_template_on_page

    enter_start = time.time() * 1000
    entered = False
    while time.time() * 1000 - enter_start < 30000:
        try:
            pos = find_template_on_page(page, "回城.png", threshold=0.7)
            if pos is not None:
                print("检测到回城按钮，确认已进入游戏主界面")
                entered = True
                break
        except FileNotFoundError:
            print("[Warn] 模板文件不存在: templates/回城.png，跳过主界面检测")
            break
        time.sleep(3)

    if not entered:
        print("未检测到回城按钮，可能仍在加载中或需要其他判断方式")

    time.sleep(0.5)
    print("点击回城")
    click_by_image(page,"回城.png")
    time.sleep(0.5)
    click_by_image(page,"战斗确定.png")
    time.sleep(2)
    print("登录流程执行完毕，已进入游戏")

def login(page: Page) -> None:
    """
    执行完整的登录并进入游戏流程。

    流程：
        1. 点击手机登录按钮
        2. 输入手机号和密码
        3. 点击登录按钮
        4. 关闭公告弹窗（如有）
        5. 点击开始游戏按钮
        6. 等待进入游戏主界面

    Args:
        page: Playwright Page 实例

    Raises:
        TimeoutError: 任一关键步骤等待超时
        RuntimeError: 登录失败（如账号密码错误）
    """
    print("开始执行登录流程...")

    # a. 点击手机登录按钮
    print("步骤 1/6: 点击手机登录按钮")
    phone_login_selectors = [
        "text=手机登录",
        "text=手机号登录",
        "text=账号登录",
        "button:has-text('手机')",
        "button:has-text('登录')",
        "[class*='phone']",
        "[class*='login']",
    ]
    if not _click_by_dom_or_image(
        page, phone_login_selectors, "phone_login_btn.png", "手机登录按钮"
    ):
        print("未找到手机登录按钮,尝试直接登录")        
        return click_login(page)

    time.sleep(1)

    # b. 输入手机号
    print("步骤 2/6: 输入手机号")
    phone_selectors = [
        "input[type='tel']",
        "input[placeholder*='手机']",
        "input[placeholder*='手机号']",
        "input[name='phone']",
        "input[name='mobile']",
        "input[id*='phone']",
        "input[id*='mobile']",
        "[class*='phone'] input",
    ]
    if not _fill_input(
        page, phone_selectors, "phone_input.png", PHONE_NUMBER, "手机号输入框"
    ):
        raise TimeoutError("未找到手机号输入框")

    time.sleep(0.5)

    # 输入密码
    print("步骤 3/6: 输入密码")
    password_selectors = [
        "xpath=//*[@id='phonelogin']/div/form/div/ul[2]/li[2]/input",
        "input[type='password']",
        "input[placeholder*='密码']",
        "input[name='password']",
        "input[id*='password']",
        "[class*='password'] input",
    ]
    if not _fill_input(
        page, password_selectors, "password_input.png", PASSWORD, "密码输入框"
    ):
        raise TimeoutError("未找到密码输入框")

    time.sleep(0.5)

    # 点击登录按钮
    print("步骤 4/6: 点击登录按钮")
    login_btn_selectors = [
        "xpath=//*[@id='phonelogin']/div/form/div/button",
        "button:has-text('登录')",
        "text=登录",
        "[class*='login-btn']",
        "[class*='submit']",
        "button[type='submit']",
    ]
    if not _click_by_dom_or_image(
        page, login_btn_selectors, "login_btn.png", "登录按钮"
    ):
        raise TimeoutError("未找到登录按钮")

    # 等待登录响应，检查是否有错误提示
    time.sleep(2)
    error_selectors = [
        "text=账号或密码错误",
        "text=密码错误",
        "text=手机号格式错误",
        "text=用户不存在",
        "[class*='error']",
        "[class*='toast']",
    ]
    for selector in error_selectors:
        try:
            if page.locator(selector).first.is_visible(timeout=3000):
                raise RuntimeError(f"登录失败，检测到错误提示")
        except PlaywrightTimeoutError:
            continue

    # 关闭公告弹窗（如有）
    return click_login(page)


def main():
    """模块独立测试入口，优先连接已有浏览器，否则自行启动。"""
    result = connect_to_existing_browser()
    own_browser = False

    if result is not None:
        page, context, browser, playwright = result
    else:
        print("未检测到已有浏览器，自行启动...")
        from start import launch_browser

        page, context, browser, playwright = launch_browser()
        own_browser = True

    try:
        login(page)
        if own_browser:
            print("按 Enter 键关闭浏览器...")
            input()
        else:
            print("登录完成，浏览器保持运行")
    except Exception as e:
        print(f"登录失败: {e}")
        raise
    finally:
        if own_browser:
            browser.close()
            playwright.stop()


if __name__ == "__main__":
    main()
