import requests
import json
import time

def get_signals():
    try:
        response = requests.get('http://127.0.0.1:8000/signals')
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Fetching signals...")
    get_signals()
