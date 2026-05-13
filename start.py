"""浏览器启动模块"""

import os
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright

from config import (
    BROWSER_EXECUTABLE_PATH,
    GAME_URL,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
    DEFAULT_NAVIGATION_TIMEOUT,
)

CDP_PORT = 9222
CDP_PORT_FILE = ".browser_cdp_port"


def launch_browser() -> tuple[Page, BrowserContext, Browser, Playwright]:
    """
    启动浏览器并打开游戏页面。

    Returns:
        page: Playwright Page 实例
        context: BrowserContext 实例
        browser: Browser 实例
        playwright: Playwright 实例

    Raises:
        FileNotFoundError: 浏览器可执行文件不存在
        TimeoutError: 页面加载超时
    """
    # 检查浏览器可执行文件是否存在
    if not os.path.exists(BROWSER_EXECUTABLE_PATH):
        raise FileNotFoundError(
            f"Chrome 可执行文件不存在: {BROWSER_EXECUTABLE_PATH}"
        )

    playwright = sync_playwright().start()

    try:
        browser = playwright.chromium.launch(
            executable_path=BROWSER_EXECUTABLE_PATH,
            headless=False,
            args=[f"--remote-debugging-port={CDP_PORT}"],
        )

        # 如果存在本地 cookies，加载以保持登录态
        storage_state = "cookies.json" if os.path.exists("cookies.json") else None
        context = browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            storage_state=storage_state,
        )

        page = context.new_page()
        page.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)
        page.set_default_timeout(DEFAULT_NAVIGATION_TIMEOUT)

        # 打开游戏页面并等待加载
        page.goto(GAME_URL, wait_until="networkidle")

        # 保存 CDP 端口到文件，供 login.py 分步连接
        with open(CDP_PORT_FILE, "w") as f:
            f.write(str(CDP_PORT))

        return page, context, browser, playwright

    except Exception as e:
        playwright.stop()
        raise e


def main():
    """模块独立运行入口"""
    page, context, browser, playwright = launch_browser()
    print(f"浏览器已启动，当前页面: {page.url}")
    print("按 Enter 键关闭浏览器...")
    try:
        input()
    finally:
        if os.path.exists(CDP_PORT_FILE):
            os.remove(CDP_PORT_FILE)
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()
