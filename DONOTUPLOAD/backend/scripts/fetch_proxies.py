import re
import sys

import httpx

URL = "https://www.proxynova.com/proxy-server-list/"
MAX_RESULTS = 10


def extract_ip(ip_expr: str) -> str | None:
    cleaned = re.sub(r"[\s\+\'\"]", "", ip_expr)
    cleaned = cleaned.replace("document.write(", "").replace(")", "")
    if cleaned.endswith("."):
        cleaned = cleaned[:-1]
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", cleaned):
        return cleaned
    return None


def fetch_proxies() -> list[str]:
    proxies: list[str] = []
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
            resp = client.get(URL)
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return proxies

    pattern = re.compile(r"document\.write\(([^)]*)\).*?<td[^>]*>(\d+)</td>", re.DOTALL)
    for ip_expr, port in pattern.findall(html):
        ip = extract_ip(ip_expr)
        if not ip:
            continue
        proxies.append(f"http://{ip}:{port}")
        if len(proxies) >= MAX_RESULTS:
            break
    return proxies


def main() -> int:
    proxies = fetch_proxies()
    if not proxies:
        return 1
    print(",".join(proxies[:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
