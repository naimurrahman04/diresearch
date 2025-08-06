import requests
import random
import time
import argparse
import os
import sys
from urllib.parse import urljoin
from colorama import Fore, Style, init

init(autoreset=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 Chrome/115.0.0.0 Mobile Safari/537.36",
]

STEALTH_HEADERS = [
    {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"Accept-Encoding": "gzip, deflate"},
    {"Accept-Language": "en-US,en;q=0.5"},
    {"Cache-Control": "no-cache"},
    {"Connection": "keep-alive"},
    {"Upgrade-Insecure-Requests": "1"},
]

BYPASS_SUFFIXES = ['/', '/.', '/..;/', '/%2e%2e/', '?', '??', '???', '/./', '/%2e/']
BYPASS_HEADERS = [
    {"X-Original-URL": "/"},
    {"X-Rewrite-URL": "/"},
    {"X-Custom-IP-Authorization": "127.0.0.1"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Host": "127.0.0.1"},
    {"X-Forwarded-Host": "127.0.0.1"},
    {"X-Remote-IP": "127.0.0.1"},
    {"X-Originating-IP": "127.0.0.1"},
    {"X-Remote-Addr": "127.0.0.1"},
    {"X-Client-IP": "127.0.0.1"}
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

def color_status(status, text):
    if status == 200:
        return Fore.GREEN + text + Style.RESET_ALL
    elif status in [301, 302]:
        return Fore.CYAN + text + Style.RESET_ALL
    elif status == 403:
        return Fore.YELLOW + text + Style.RESET_ALL
    elif status == 401:
        return Fore.MAGENTA + text + Style.RESET_ALL
    elif status == 429 or status >= 500:
        return Fore.RED + text + Style.RESET_ALL
    else:
        return text

def build_headers():
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    for hdr in STEALTH_HEADERS:
        headers.update(hdr)
    return headers

def try_bypass(base_url, word, original_status, output_file, proxies, verify, exclude_sizes):
    bypassed = []
    full_url = urljoin(base_url, word)

    for suffix in BYPASS_SUFFIXES:
        bypass_url = full_url + suffix
        headers = build_headers()
        try:
            resp = requests.get(bypass_url, headers=headers, allow_redirects=False, timeout=10, proxies=proxies, verify=verify)
            size = len(resp.content)
            if exclude_sizes and size in exclude_sizes:
                continue
            if resp.status_code != original_status and resp.status_code != 404:
                msg = f"[{resp.status_code} | {size}B] BYPASS via SUFFIX '{suffix}': {bypass_url}"
                print(color_status(resp.status_code, msg))
                bypassed.append((resp.status_code, msg))
                if output_file:
                    output_file.write(msg + "\n")
        except:
            continue

    for hdr in BYPASS_HEADERS:
        headers = build_headers()
        headers.update(hdr)
        try:
            resp = requests.get(full_url, headers=headers, allow_redirects=False, timeout=10, proxies=proxies, verify=verify)
            size = len(resp.content)
            if exclude_sizes and size in exclude_sizes:
                continue
            if resp.status_code != original_status and resp.status_code != 404:
                header_name = list(hdr.keys())[0]
                msg = f"[{resp.status_code} | {size}B] BYPASS via HEADER '{header_name}': {full_url}"
                print(color_status(resp.status_code, msg))
                bypassed.append((resp.status_code, msg))
                if output_file:
                    output_file.write(msg + "\n")
        except:
            continue

    return bypassed

def brute_force(url, wordlist, delay, output_file, do_bypass, proxies, verify, exclude_sizes):
    results = []

    for word in wordlist:
        full_url = urljoin(url, word)
        headers = build_headers()

        try:
            response = requests.get(full_url, headers=headers, allow_redirects=False, timeout=10, proxies=proxies, verify=verify)
            status = response.status_code
            size = len(response.content)

            if exclude_sizes and size in exclude_sizes:
                continue

            banner = f"[{status} | {size}B]"
            if status == 200:
                msg = f"{banner} FOUND: {full_url}"
            elif status in [301, 302]:
                loc = response.headers.get('Location', '')
                msg = f"{banner} REDIRECT: {full_url} -> {loc}"
            elif status == 403:
                msg = f"{banner} FORBIDDEN: {full_url}"
            elif status == 401:
                msg = f"{banner} AUTH REQUIRED: {full_url}"
            elif status == 429:
                retry_after = response.headers.get('Retry-After')
                wait_time = int(retry_after) if retry_after and retry_after.isdigit() else max(5, delay * 2)
                print(color_status(429, f"[429] TOO MANY REQUESTS. Sleeping {wait_time}s..."))
                time.sleep(wait_time)
                continue
            elif status != 404:
                msg = f"{banner} RESPONSE: {full_url}"
            else:
                continue

            print(color_status(status, msg))
            results.append((status, msg))
            if output_file:
                output_file.write(msg + "\n")

            if do_bypass and status == 403:
                bypass_results = try_bypass(url, word, status, output_file, proxies, verify, exclude_sizes)
                results.extend(bypass_results)

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {full_url}: {e}")

        time.sleep(delay)

    print("\n\n[+] Scan Complete. Sorted Results:\n")
    for status, msg in sorted(results, key=lambda x: x[0]):
        print(color_status(status, msg))

def main():
    parser = argparse.ArgumentParser(description="Dir Brute Forcer with proxy, CA cert, UA rotation, bypass, and size filtering")
    parser.add_argument("-u", "--url", required=True, help="Base URL (e.g., https://target.com/)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-d", "--delay", type=float, default=0.0, help="Delay between requests (default: 0)")
    parser.add_argument("-o", "--output", help="Optional output file to log results")
    parser.add_argument("--4bypass", action="store_true", help="Enable 403 bypass techniques")
    parser.add_argument("--proxy", help="HTTP/HTTPS proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--verify", help="Path to Burp/ZAP CA cert (e.g., cacert.pem)")
    parser.add_argument("--exclude-size", help="Comma-separated response sizes to exclude (e.g. 0,1234)")
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
    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    verify = args.verify if args.verify else True

    exclude_sizes = set()
    if args.exclude_size:
        try:
            exclude_sizes = set(int(size.strip()) for size in args.exclude_size.split(',') if size.strip().isdigit())
        except ValueError:
            print("[ERROR] Invalid format in --exclude-size. Use comma-separated integers.")
            sys.exit(1)

    print(f"[*] Starting brute force on: {args.url}")
    print(f"[*] Words to test: {len(wordlist)}")
    print(f"[*] Delay between requests: {args.delay} sec")
    print(f"[*] 403 Bypass Mode: {'ON' if args.__dict__.get('4bypass') else 'OFF'}")
    print(f"[*] Proxy: {args.proxy if args.proxy else 'None'}")
    print(f"[*] Cert: {args.verify if args.verify else 'Default'}")
    print(f"[*] Exclude Sizes: {', '.join(map(str, exclude_sizes)) if exclude_sizes else 'None'}")
    print(f"[*] Output file: {args.output if args.output else 'None'}\n")

    try:
        brute_force(args.url, wordlist, args.delay, output_file, args.__dict__.get("4bypass"), proxies, verify, exclude_sizes)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting gracefully...")
    finally:
        if output_file:
            output_file.close()

if __name__ == "__main__":
    main()
