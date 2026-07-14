"""
Keep-Alive Script for Discord Bot Hosting
This script sends periodic requests to keep the application alive.
It can be used with external cron jobs or scheduled tasks.
"""

import requests
import time
import sys

def keep_alive(url='http://localhost:5000', interval=30):
    """
    Send periodic requests to keep the application alive.
    
    Args:
        url: The URL to ping
        interval: Time between requests in seconds (default: 30)
    """
    print(f"Keep-Alive started. Pinging {url} every {interval} seconds.")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            response = requests.get(url, timeout=10)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping successful: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping failed: {e}")
        
        time.sleep(interval)

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    try:
        keep_alive(url, interval)
    except KeyboardInterrupt:
        print("\nKeep-Alive stopped.")
