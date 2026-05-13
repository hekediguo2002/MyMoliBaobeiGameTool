# 网页游戏自动化脚本 PRD

## 1. 项目概述

### 1.1 项目背景
基于 HTML5 Canvas 的网页游戏自动化操作脚本，使用 Python + Playwright 架构实现浏览器自动化控制，支持图片识别定位与模拟点击操作。

### 1.2 游戏信息
- **游戏地址**: `https://h5.hywan.com/game/index?id=2118`
- **技术方案**: HTML5 Canvas 渲染
- **浏览器**: Google Chrome (Mac)
- **浏览器路径**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

### 1.3 技术栈
- Python 3.9+
- Playwright (浏览器自动化)
- Pillow / OpenCV (图片识别，预留)

---

## 2. 目录结构

```
project/
├── start.py          # 浏览器启动模块
├── login.py          # 登录游戏模块
├── game_bot.py       # 游戏主控模块（预留）
├── image_utils.py    # 图片识别工具模块（预留）
├── config.py         # 全局配置
├── templates/        # 图片模板目录（预留）
│   ├── login_btn.png
│   ├── phone_login_btn.png
│   ├── start_game_btn.png
│   └── close_notice_btn.png
└── requirements.txt  # 依赖清单
```

---

## 3. 模块设计

### 3.1 配置模块 (config.py)

集中管理所有全局配置参数，避免硬编码分散在各模块中。

| 配置项 | 类型 | 值 | 说明 |
|--------|------|-----|------|
| BROWSER_EXECUTABLE_PATH | str | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | Chrome 可执行文件路径 |
| GAME_URL | str | `https://h5.hywan.com/game/index?id=2118` | 游戏入口地址 |
| VIEWPORT_WIDTH | int | 800 | 浏览器窗口宽度 |
| VIEWPORT_HEIGHT | int | 600 | 浏览器窗口高度 |
| PHONE_NUMBER | str | `17712426331` | 登录手机号 |
| PASSWORD | str | `123456` | 登录密码 |
| DEFAULT_TIMEOUT | int | 30000 | 默认等待超时（毫秒） |

### 3.2 启动模块 (start.py)

负责初始化 Playwright 浏览器实例并打开游戏页面。

#### 功能职责
1. 启动 Playwright 同步/异步上下文
2. 以指定路径的 Chrome 作为浏览器引擎
3. 设置视口大小为 800x600
4. 打开游戏目标 URL
5. 返回 `page` 对象供后续模块使用

#### 接口定义
```python
def launch_browser() -> tuple[Page, BrowserContext, Browser, Playwright]:
    """
    启动浏览器并打开游戏页面。

    Returns:
        page: Playwright Page 实例
        context: BrowserContext 实例
        browser: Browser 实例
        playwright: Playwright 实例
    """
```

#### 启动流程
```
[启动 Playwright] → [启动 Chrome] → [设置视口 800x600]
      → [打开游戏 URL] → [等待页面加载] → [返回 page 对象]
```

#### 异常处理
- 浏览器可执行文件不存在：抛出 `FileNotFoundError`
- 页面加载超时：抛出 `TimeoutError`
- 网络异常：重试 3 次后抛出异常

### 3.3 登录模块 (login.py)

负责完成从登录页到进入游戏主界面的完整流程。

#### 功能职责
1. 识别并点击"手机登录"按钮
2. 识别并点击手机号输入框，输入手机号
3. 识别并点击密码输入框，输入密码
4. 识别并点击"登录"按钮
5. 等待页面加载完毕，识别并关闭公告弹窗
6. 识别并点击"开始游戏"按钮
7. 等待进入游戏主界面

#### 接口定义
```python
def login(page: Page) -> None:
    """
    执行完整的登录并进入游戏流程。

    Args:
        page: Playwright Page 实例

    Raises:
        TimeoutError: 任一元素等待超时
        RuntimeError: 登录失败（如账号密码错误）
    """
```

#### 登录流程
```
[点击手机登录按钮]
      ↓
[点击手机号输入框] → [输入 17712426331]
      ↓
[点击密码输入框] → [输入 123456]
      ↓
[点击登录按钮]
      ↓
[等待页面加载] → [关闭公告界面]
      ↓
[点击开始游戏按钮]
      ↓
[等待进入游戏主界面] → [完成]
```

#### 交互方式策略
由于目标游戏使用 HTML Canvas 渲染，常规 DOM 选择器可能无法直接定位元素。本模块支持两种交互方式（按优先级执行）：

1. **DOM 选择器优先**：尝试使用 Playwright 的 `page.locator()` / `page.get_by_text()` 等方式定位按钮/输入框
2. **图片识别兜底**：当 DOM 方式失败时，通过 Canvas 截图 + 模板匹配计算坐标，再使用 `page.mouse.click()` 模拟点击

#### 异常处理
- 任一按钮/输入框 10 秒内未出现：抛出 `TimeoutError`
- 登录后检测到"账号或密码错误"提示：抛出 `RuntimeError`
- 公告弹窗不存在（已自动关闭或本期无公告）：跳过该步骤，不抛异常

---

## 4. 图片识别方案

### 4.1 适用场景
Canvas 游戏无法通过 DOM 选择器定位元素时，使用截图 + 模板匹配的方式定位目标按钮/图标。

### 4.2 技术实现
- **截图**: Playwright `page.screenshot()` 截取全屏或指定区域
- **模板匹配**: OpenCV `cv2.matchTemplate()` 多尺度匹配
- **点击**: Playwright `page.mouse.click(x, y)` 根据识别到的坐标模拟点击

### 4.3 核心实现 (image_utils.py)
```python
def find_image_position(
    screenshot_path: str,
    template_path: str,
    threshold: float = 0.8
) -> tuple[int, int] | None:
    """
    在截图中查找模板图片的中心坐标。
    内部采用多尺度模板匹配，自动兼容 Canvas 缩放。

    Returns:
        (x, y) 中心坐标，未匹配到返回 None
    """
```

### 4.4 图片识别注意事项

#### 4.4.1 模板图片截取规范
- **分辨率一致**：模板图必须在浏览器视口 `800x600` 下截取，确保与 Playwright 截图分辨率相同
- **尺寸精简**：模板只截取按钮/图标本身，建议控制在 `100x100` 像素以内，背景越少越好
- **格式统一**：统一使用 `.png` 格式，保存到 `templates/` 目录

#### 4.4.2 Canvas 缩放与多尺度匹配
- **问题**：HTML5 Canvas 游戏在不同设备像素比（DPR）或缩放设置下，实际渲染尺寸可能与设计稿不一致，导致模板和截图像素对不上
- **解决**：`image_utils.py` 内置**多尺度模板匹配**，会自动将模板缩放到 `0.5x ~ 1.5x` 之间的 16 个尺寸逐一尝试，返回匹配度最高的结果。无需手动调整模板大小

#### 4.4.3 截图稳帧
- **问题**：Canvas 动画或弹窗出现时，画面可能在短时间内闪动/渐变，直接截图会导致画面内容不稳定
- **解决**：`take_screenshot()` 函数在截图前强制等待 `0.3` 秒，让 Canvas 渲染稳定后再截取

#### 4.4.4 匹配阈值调整
- **默认值**：`IMAGE_MATCH_THRESHOLD = 0.8`（config.py 中配置）
- **半透明/动画元素**：如公告弹窗的关闭按钮可能处于渐变或半透状态，可适当降低阈值（如 `0.65`）提高容错
- **调试输出**：匹配失败时控制台会打印 `最佳匹配值` 和 `截图/模板尺寸`，方便判断是时机问题还是模板精度问题

#### 4.4.5 调试机制
- **自动保存**：当模板匹配失败时，当时的页面截图会自动保存到 `debug/fail_<模板名>.png`
- **排查步骤**：
  1. 打开 `debug/` 目录下的截图，确认目标元素是否清晰可见
  2. 对比模板图和 debug 截图中目标元素的尺寸、颜色是否一致
  3. 若尺寸不一致 → 属于缩放问题，多尺度匹配会自动处理
  4. 若颜色/外观不一致 → 重新截取模板图，确保与游戏中实际状态一致

---

## 5. 测试用例

### 5.1 启动模块测试
```python
def test_launch_browser():
    page, context, browser, playwright = launch_browser()
    assert page is not None
    assert page.url == GAME_URL
    browser.close()
    playwright.stop()
```

### 5.2 登录模块测试
```python
def test_login(page):
    login(page)
    # 断言：进入游戏后页面标题或特定 Canvas 内容发生变化
    # 具体断言条件需根据游戏实际加载后的特征补充
```

---

## 6. 依赖清单 (requirements.txt)

```
pytest-playwright>=0.4.0
pillow>=10.0.0
opencv-python>=4.8.0
```

> Playwright 浏览器安装命令：`playwright install chromium`

---

## 7. 运行方式

### 7.1 启动浏览器
```bash
python start.py
```

### 7.2 执行登录
```python
from start import launch_browser
from login import login

page, context, browser, playwright = launch_browser()
try:
    login(page)
    print("登录成功，已进入游戏")
except Exception as e:
    print(f"登录失败: {e}")
finally:
    browser.close()
    playwright.stop()
```

---

## 8. 风险与注意事项

| 风险点 | 影响 | 应对措施 |
|--------|------|----------|
| Canvas 元素无法通过 DOM 定位 | 高 | 引入截图 + 模板匹配方案 |
| 游戏 UI 更新导致模板图片失效 | 中 | 定期维护 `templates/` 目录中的模板图 |
| 登录验证码/人机验证 | 高 | PRD 暂不覆盖，需人工介入或接入打码平台 |
| 多分辨率/缩放导致坐标偏移 | 中 | 固定视口 800x600，模板图在此分辨率下截取 |

---

## 9. 后续扩展（预留）

1. **game_bot.py**: 游戏主循环，实现具体的自动化任务（刷副本、挂机、领取奖励等）
2. **日志模块**: 引入 `logging` 记录操作流水与异常信息
3. **配置热加载**: 支持从 JSON/YAML 读取配置，避免修改源码
4. **验证码处理**: 接入第三方打码平台或本地 OCR
5. **异常重试与恢复**: 网络抖动或游戏掉线后自动重连

---

## 10. 待确认事项

以下事项需在脚本开发前与需求方确认或实地调研：

1. **DOM 可访问性**: 登录按钮、输入框是否为标准 DOM 元素，还是完全绘制在 Canvas 内部？
2. **公告弹窗特征**: 公告界面是否有固定关闭按钮，还是点击任意区域关闭？
3. **登录方式**: 除手机号+密码外，是否支持快捷登录（如微信扫码），是否会弹出额外授权窗口？
4. **游戏加载标识**: 进入游戏主界面后，是否有明确的标题、角色信息或其他可用于断言加载成功的特征？
5. **反作弊机制**: 游戏是否有针对自动化脚本的检测机制（如频繁点击封禁）？
