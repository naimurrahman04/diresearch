import requests
import random
import time
import argparse

# Predefined list of User-Agent strings for rotation (a sample from various browsers)
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

def main():
    parser = argparse.ArgumentParser(description="Python Directory Brute Force Tool with User-Agent rotation and rate limiting")
    parser.add_argument("-u", "--url", required=True, help="Target base URL (e.g., http://site.com or http://site.com/dir/)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file (one directory/file name per line)")
    parser.add_argument("-d", "--delay", type=float, default=0.0, help="Delay between requests in seconds (rate limiting)")
    parser.add_argument("-o", "--output", help="Output file to write found directories to")
    args = parser.parse_args()

    base_url = args.url
    # Ensure the base URL does not end with a trailing slash to avoid double slashes
    # (We'll handle slash when constructing full URL)
    if base_url.endswith("/"):
        base_url = base_url.rstrip("/")

    delay = args.delay if args.delay >= 0 else 0.0  # negative delay not allowed, set to 0 if so

    # Open wordlist file and read entries
    try:
        with open(args.wordlist, "r") as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] Wordlist file not found: {args.wordlist}")
        return

    # Open output file if specified
    output_file = None
    if args.output:
        try:
            output_file = open(args.output, "w")
        except Exception as e:
            print(f"[ERROR] Could not open output file for writing: {e}")
            # Continue without file logging if file open fails
            output_file = None

    try:
        for word in words:
            # Construct the full URL to test
            # e.g., base_url + "/" + word
            target_url = f"{base_url}/{word}"
            # Pick a random User-Agent for this request
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            try:
                # Send GET request (do not follow redirects to capture 301/302 responses)
                response = requests.get(target_url, headers=headers, allow_redirects=False)
            except requests.RequestException as req_err:
                # Handle network errors (timeout, connection error, etc.)
                print(f"[ERROR] Request to {target_url} failed: {req_err}")
                # Continue to next word
                continue

            status = response.status_code

            # Check response status and act accordingly
            if status == 200:
                print(f"[200] FOUND: {target_url}")
                if output_file:
                    output_file.write(f"200\t{target_url}\n")
                    output_file.flush()
            elif status in (301, 302):
                # Redirect indicates something is there (often adding a slash or redirect to login)
                location = response.headers.get("Location", "")
                print(f"[{status}] FOUND (redirect to {location}): {target_url}")
                if output_file:
                    output_file.write(f"{status}\t{target_url} -> {location}\n")
                    output_file.flush()
            elif status == 403:
                print(f"[403] FOUND (forbidden): {target_url}")
                if output_file:
                    output_file.write(f"403\t{target_url} (Forbidden)\n")
                    output_file.flush()
            elif status == 401:
                print(f"[401] FOUND (auth required): {target_url}")
                if output_file:
                    output_file.write(f"401\t{target_url} (Unauthorized)\n")
                    output_file.flush()
            elif status == 429:
                # Too Many Requests - hit rate limit or got blocked temporarily
                retry_after = response.headers.get("Retry-After")
                wait_time = 0
                if retry_after:
                    try:
                        wait_time = int(retry_after)
                    except ValueError:
                        # If Retry-After is a timestamp or not an integer, default to a safe wait
                        pass
                if not wait_time:
                    # If no Retry-After header or not usable, wait longer than the normal delay
                    wait_time = 5 if delay == 0 else max(5, delay * 2)
                print(f"[429] Rate limit hit. Sleeping for {wait_time} seconds...")
                time.sleep(wait_time)
                # After sleeping, skip logging this as found and continue with next word
                # (We could also retry the same word after sleeping, but to keep things simple, we'll move on)
            else:
                # Other status codes (404, 500, etc.)
                if status != 404:
                    # If it's not 404, it might be something interesting (500 error, 301 followed by a 404, etc.)
                    print(f"[{status}] Note: Received status {status} for {target_url}")
                    if output_file:
                        output_file.write(f"{status}\t{target_url}\n")
                        output_file.flush()
                # For 404 or any uninteresting code, do nothing (not found)

            # Respect the delay between requests
            if delay > 0:
                time.sleep(delay)
    finally:
        if output_file:
            output_file.close()
