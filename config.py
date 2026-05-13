"""全局配置模块"""

import json
import os

# 浏览器配置
BROWSER_EXECUTABLE_PATH: str = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 游戏配置
GAME_URL: str = "https://h5.hywan.com/game/index?id=2118"

# 视口配置
VIEWPORT_WIDTH: int = 800
VIEWPORT_HEIGHT: int = 500

# 账号配置：从 settings.json 读取，禁止在代码中硬编码账号密码
_settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
if not os.path.exists(_settings_path):
    raise FileNotFoundError(
        f"账号配置文件不存在: {_settings_path}\n"
        "请创建 settings.json 并填入账号信息，格式: "
        '{"accout": "手机号", "password": "密码"}'
    )

with open(_settings_path, "r", encoding="utf-8") as _f:
    _settings = json.load(_f)

PHONE_NUMBER: str = _settings.get("accout", "")
PASSWORD: str = _settings.get("password", "")

if not PHONE_NUMBER or not PASSWORD:
    raise ValueError(
        f"settings.json 中账号或密码为空，请检查文件内容: {_settings_path}"
    )

# 超时配置（毫秒）
DEFAULT_TIMEOUT: int = 30000
DEFAULT_NAVIGATION_TIMEOUT: int = 60000

# 图片匹配阈值
IMAGE_MATCH_THRESHOLD: float = 0.8

# 模板图片目录
TEMPLATES_DIR: str = "templates"
