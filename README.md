# diresearch

# 🔍 Python Directory Brute Force Tool

A lightweight and extensible Python script to perform directory/file brute forcing on web applications. It includes features such as:

- ✅ Custom wordlist support  
- 🎭 User-Agent rotation for evasion  
- 🐢 Configurable rate limiting (delay between requests)  
- 📄 Logging to output file  
- 🔐 Smart handling of HTTP status codes (e.g. 200, 403, 401, 301/302, 429)

> ⚠️ **Use this tool ethically and only against targets you own or have permission to test.**

---

## 🛠 Features

- Rotate User-Agent strings for stealthy requests
- Delay between requests to avoid rate limiting
- Support for redirects, forbidden access, and authentication-required paths
- Output results to terminal and/or file
- Handles `429 Too Many Requests` gracefully

---

## 📦 Requirements

- Python 3.6+
- `requests` library

Install dependencies:

```bash
pip install requests

python dir_bruteforce.py -u <target_url> -w <wordlist_path> [options]

python dir_bruteforce.py -u http://example.com -w ./wordlists/common.txt -d 1.5 -o results.txt




Start
 │
 ├──► Parse CLI Arguments
 │       ├─ URL, Wordlist
 │       ├─ Delay, Proxy, Output
 │       ├─ --4bypass, --exclude-size
 │
 ├──► Validate:
 │       ├─ URL format
 │       ├─ Wordlist file
 │       └─ Parse exclude-size (into set)
 │
 ├──► Open Output File (optional)
 ├──► Setup Proxy (if provided)
 ├──► Loop through each path in wordlist:
 │
 │   ├──► Build Request Headers (User-Agent + Stealth Headers)
 │   ├──► Send GET Request (with headers and proxy)
 │   ├──► Get:
 │   │       ├─ Status Code
 │   │       └─ Response Size
 │   ├──► If size in --exclude-size:
 │   │       └─ Skip to next path
 │   ├──► Log & Print Status (Colored)
 │   ├──► If status == 403 AND --4bypass:
 │   │       ├──► Try Bypass (Suffixes + Headers)
 │   │       ├──► For Each Bypass:
 │   │       │       ├── Send Request
 │   │       │       ├── Get Status + Size
 │   │       │       ├── If status not 403/404 and size not excluded:
 │   │       │       │     └── Log & Print
 │   │       │       └── End
 │   │       └── End
 │   └──► Sleep for delay (if set)
 │
 └──► After loop:
         ├── Sort all results by status code
         ├── Print final colored summary
         └── Close output file (if open)
         └── Exit


I'll be happy to help.
