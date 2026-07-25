"""Poll a URL until it responds or a timeout elapses.
Usage: wait_for_url.py <url> <timeout_seconds>
"""
import sys
import time
import urllib.request

url = sys.argv[1]
deadline = time.time() + float(sys.argv[2])
last_err = None

while time.time() < deadline:
    try:
        urllib.request.urlopen(url, timeout=2)
        print(f"[OK] {url} responded")
        sys.exit(0)
    except Exception as e:
        last_err = e
        time.sleep(1)

print(f"[FAIL] {url} did not respond within {sys.argv[2]}s. Last error: {last_err}")
sys.exit(1)
