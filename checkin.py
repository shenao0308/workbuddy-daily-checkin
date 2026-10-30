# -*- coding: utf-8 -*-
import json
import os
import sys
import urllib.request
import urllib.error

TOKEN = os.environ.get("WB_TOKEN", "").strip()
UID = os.environ.get("WB_UID", "").strip()

BASE_URL = "https://www.codebuddy.cn/v2/billing/meter"
CHECKIN_URL = f"{BASE_URL}/daily-checkin"
STATUS_URL = f"{BASE_URL}/checkin-activity-status"

def post_json(url, data_dict):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "WorkBuddy/1.0.0 (Windows NT 10.0; Win64; x64)"
    }
    if UID:
        headers["X-User-Id"] = str(UID)

    req = urllib.request.Request(
        url=url,
        data=json.dumps(data_dict).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            return json.loads(error_msg)
        except Exception:
            return {"code": e.code, "message": error_msg}
    except Exception as e:
        return {"code": -1, "message": str(e)}

def main():
    if not TOKEN:
        print("[!] 错误: 未检测到 WB_TOKEN 环境变量，请先配置！")
        sys.exit(1)

    print("[*] 正在查询签到活动状态...")
    status_res = post_json(STATUS_URL, {})
    print(f"[*] 当前状态: {status_res.get('message', status_res)}")

    print("[*] 正在执行每日签到...")
    res = post_json(CHECKIN_URL, {})
    code = res.get("code")

    if code == 0:
        print(f"[+] 签到成功！响应数据: {res.get('data')}")
    elif code == 10001:
        print("[+] 今日已经签过到（幂等成功，无需重复签到）。")
    else:
        print(f"[-] 签到失败: {res}")
        sys.exit(1)

if __name__ == "__main__":
    main()
