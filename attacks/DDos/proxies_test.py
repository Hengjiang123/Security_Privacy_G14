import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# === 目标网站 ===
TARGETS = {
    "Digital-bank":"http://flask-env.eba-7mjjpfcw.eu-west-2.elasticbeanstalk.com",
    # "Google": "http://www.google.com",
    # "Baidu": "http://www.baidu.com",
    # "Ngrok": "https://f4f4-140-228-36-171.ngrok-free.app/login"
}

# === 请求头 ===
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

# === 参数配置 ===
PROXY_FILE = "attacks/DDos/Proxy List.txt"
OUTPUT_FILE = "attacks/DDos/proxy_valid.txt"
MAX_THREADS = 50  # threads for testing proxies

# === 读取代理列表 ===
def load_proxies(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# === 测试代理是否可用 ===
def test_proxy(proxy):
    for name, url in TARGETS.items():
        try:
            response = requests.get(
                url,
                proxies={"http": proxy, "https": proxy},
                headers=HEADERS,
                timeout=8
            )
            if response.status_code != 200:
                print(f"❌ {proxy} failed at {name} ({response.status_code})")
                return None
        except requests.RequestException as e:
            print(f"❌ {proxy} error at {name} ({type(e).__name__})")
            return None
    print(f"✅ {proxy} passed all targets.")
    return proxy

# === 主程序 ===
if __name__ == "__main__":
    proxy_list = load_proxies(PROXY_FILE)
    print(f"Loaded {len(proxy_list)} proxies.")
    print(f"Testing with {MAX_THREADS} threads...\n")

    working_proxies = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxy_list}

        for i, future in enumerate(as_completed(future_to_proxy), 1):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                if result:
                    working_proxies.append(result)
            except Exception as e:
                print(f"[{i}] Unexpected error for {proxy}: {e}")

    # 保存可用代理
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for proxy in working_proxies:
            f.write(proxy + "\n")

    print("\nSummary:")
    print(f"   Total proxies tested: {len(proxy_list)}")
    print(f"   Valid proxies     : {len(working_proxies)}")
    print(f"   Saved to          : {OUTPUT_FILE}")
