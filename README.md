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


---

Let me know if you’d like to turn this into a GitHub project with additional improvements like:

- `requirements.txt`
- Multi-threading support
- WAF bypass techniques (headers, encodings)
- JSON output
- API fuzzing variant

I'll be happy to help.
