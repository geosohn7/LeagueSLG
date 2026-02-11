import requests
import time

def test_map():
    base_url = "http://127.0.0.1:5000"
    
    # Wait
    time.sleep(1)

    # 1. Map Data
    print("\n--- 1. Fetching Map Data ---")
    try:
        resp = requests.get(f"{base_url}/api/map/data")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Width: {data['width']}, Height: {data['height']}")
            print(f"✅ Tiles Count: {len(data['tiles']) * len(data['tiles'][0])}")
            print(f"✅ Armies: {len(data['armies'])}")
            if data['armies']:
                 print(f"   First Army: {data['armies'][0]['name']} at ({data['armies'][0]['x']}, {data['armies'][0]['y']})")
        else:
            print(f"❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. Movement
    print("\n--- 2. Moving Army ---")
    try:
        target = {"x": 5, "y": 5}
        resp = requests.post(f"{base_url}/api/map/march", json=target)
        if resp.status_code == 200:
            res = resp.json()
            print(f"✅ {res['message']}")
        else:
            print(f"❌ Move Failed: {resp.json().get('message')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_map()
