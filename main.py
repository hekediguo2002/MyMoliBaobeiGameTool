"""主入口：启动浏览器并执行登录"""

from start import launch_browser
from login import login
from jiaodouchang import jiaodouchang
from shilian_wuqi import shilian_wuqi
from mozuruqin import mozuruqin 
from jierirenwu import jierirenwu
from shilian_jingyan import shilian_jingyan
from shibozhici import shibozhici
from shilian_daochang import shilian_daochang
from guowangxuanshang import guowangxuanshang
from screenshot import screenshot_loop, stop_screenshot


def main():
    page, context, browser, playwright = launch_browser()
    try:
        login(page)
         # 保存登录态，下次启动可直接复用
        try:
            context.storage_state(path="cookies.json")
            print("登录态已保存到 cookies.json")
        except Exception as e:
            print(f"[Warn] 保存登录态失败: {e}")
        print("登录成功，已进入游戏")
        
        # 角斗场
        jiaodouchang(page)
        # 武器试炼
        shilian_wuqi(page)
        # 试炼道场
        shilian_daochang(page)
        # 经验试炼
        shilian_jingyan(page)
        # 时波之祠
        shibozhici(page)
        # 魔族入侵
        mozuruqin(page)
        # 国王悬赏
        guowangxuanshang(page)
        # 节日任务
        jierirenwu(page)       
        # 循环截图 10 张（约 30 秒），完成后自动继续
        # screenshot_loop(page, max_count=0)

    except Exception as e:
        print(f"流程异常: {e}")
        raise
    finally:
        # 停止截图（若仍在运行）
        # stop_screenshot()
        print("按 Enter 键关闭浏览器...")
        input()
        # 保存登录态，下次启动可直接复用
        try:
            context.storage_state(path="cookies.json")
            print("登录态已保存到 cookies.json")
        except Exception as e:
            print(f"[Warn] 保存登录态失败: {e}")
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()
