import requests
import random
import time
import argparse
import os
import sys
from urllib.parse import urljoin

# Predefined User-Agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 Chrome/115.0.0.0 Mobile Safari/537.36",
]

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

def load_wordlist(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Wordlist file not found: {path}")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

def open_output_file(path):
    try:
        return open(path, 'w', encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Could not open output file '{path}': {e}")
        return None

def brute_force(url, wordlist, delay, output_file):
    for word in wordlist:
        full_url = urljoin(url, word)
        headers = {"User-Agent": random.choice(USER_AGENTS)}

        try:
            response = requests.get(full_url, headers=headers, allow_redirects=False, timeout=10)
            status = response.status_code

            if status == 200:
                msg = f"[200] FOUND: {full_url}"
            elif status in [301, 302]:
                loc = response.headers.get('Location', '')
                msg = f"[{status}] REDIRECT: {full_url} -> {loc}"
            elif status == 403:
                msg = f"[403] FORBIDDEN (exists): {full_url}"
            elif status == 401:
                msg = f"[401] AUTH REQUIRED: {full_url}"
            elif status == 429:
                retry_after = response.headers.get('Retry-After')
                wait_time = int(retry_after) if retry_after and retry_after.isdigit() else max(5, delay * 2)
                print(f"[429] TOO MANY REQUESTS. Sleeping {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif status != 404:
                msg = f"[{status}] RESPONSE: {full_url}"
            else:
                # Skip 404 silently
                continue

            print(msg)
            if output_file:
                try:
                    output_file.write(msg + "\n")
                    output_file.flush()
                except Exception as e:
                    print(f"[ERROR] Failed to write to output file: {e}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {full_url}: {e}")

        time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description="Directory Brute Forcer with UA Rotation, Delay, Error Handling")
    parser.add_argument("-u", "--url", required=True, help="Base URL (e.g., http://example.com/)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-d", "--delay", type=float, default=0.0, help="Delay between requests (default: 0)")
    parser.add_argument("-o", "--output", help="Optional output file to log results")
    args = parser.parse_args()

    if not is_valid_url(args.url):
        print("[ERROR] Invalid URL. Please include http:// or https://")
        sys.exit(1)

    try:
        wordlist = load_wordlist(args.wordlist)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    output_file = open_output_file(args.output) if args.output else None

    print(f"[*] Starting brute force on: {args.url}")
    print(f"[*] Words to test: {len(wordlist)}")
    print(f"[*] Delay between requests: {args.delay} sec")
    print(f"[*] Output file: {args.output if args.output else 'None'}\n")

    try:
        brute_force(args.url, wordlist, args.delay, output_file)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting gracefully...")
    finally:
        if output_file:
            output_file.close()

if __name__ == "__main__":
    main()
