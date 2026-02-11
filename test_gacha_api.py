import requests
import time

def test_api():
    base_url = "http://127.0.0.1:5000"
    
    # Wait for server to be up
    print("Checking server status...")
    try:
        resp = requests.get(base_url)
        if resp.status_code == 200:
            print("✅ Server is UP")
        else:
            print(f"❌ Server returned {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return

    # 1. Get User Info
    print("\n--- 1. User Info ---")
    resp = requests.get(f"{base_url}/api/user/info")
    if resp.status_code == 200:
        data = resp.json()
        print(f"User: {data['username']}, Gold: {data['resources']['gold']}, Silver: {data['resources']['silver']}")
    else:
        print("❌ Failed to get user info")

    # 2. Mine Silver
    print("\n--- 2. Mining Silver ---")
    resp = requests.post(f"{base_url}/api/mine/collect")
    if resp.status_code == 200:
        print(f"✅ {resp.json()['message']}")
    else:
        print("❌ Mining failed")

    # 3. Pull Silver Gacha
    print("\n--- 3. Silver Gacha ---")
    resp = requests.post(f"{base_url}/api/gacha/pull", json={"gacha_type": "silver_gacha"})
    if resp.status_code == 200:
        res = resp.json()
        print(f"✅ Success: {res['message']}")
        print(f"   Pulled: {res['result']['name']}, Rem Silver: {res['result']['remaining_currency']}")
    else:
        print(f"❌ Failed: {resp.json().get('message')}")

if __name__ == "__main__":
    test_api()
