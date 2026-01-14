#!/usr/bin/env python3
"""
binance_connectivity_diagnose.py

Usage:
  python binance_connectivity_diagnose.py
"""

import os
import ssl
import sys
import json
import time
import socket
import textwrap
import urllib.parse
from datetime import datetime

import requests

HOST = "fapi.binance.com"
BASE = f"https://{HOST}"
PUBLIC_URLS = [
    f"{BASE}/fapi/v1/time",
    f"{BASE}/fapi/v1/ping",
    f"{BASE}/fapi/v1/exchangeInfo",
]
# This requires auth in real use, but for diagnosis we expect a quick 4xx.
PRIVATE_URL = f"{BASE}/fapi/v2/account"

TIMEOUT = 15  # seconds


def banner(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def note(msg: str):
    print(f"• {msg}")


def warn(msg: str):
    print(f"⚠️  {msg}")


def good(msg: str):
    print(f"✅ {msg}")


def bad(msg: str):
    print(f"❌ {msg}")


def check_env_proxies():
    banner("1) Proxy / Environment Variables")
    env_keys = ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "NO_PROXY", "no_proxy", "REQUESTS_CA_BUNDLE"]
    found = {k: os.environ.get(k) for k in env_keys if os.environ.get(k)}
    if found:
        warn("Detected proxy / TLS vars in your environment:")
        for k, v in found.items():
            print(f"   {k} = {v}")
        note("Requests may behave differently in your app vs. browser if these are set.")
    else:
        good("No proxy or TLS env vars detected.")


def check_public_ip():
    banner("2) Outbound Public IP (as seen by ipify)")
    try:
        t0 = time.time()
        r = requests.get("https://api64.ipify.org?format=json", timeout=10)
        dt = (time.time() - t0) * 1000
        ip = r.json().get("ip")
        good(f"Public IP (ipify): {ip}  ({dt:.0f} ms)")
        return ip
    except Exception as e:
        bad(f"Failed to get public IP: {e}")
        return None


def check_dns_resolution(host: str):
    banner("3) DNS Resolution")
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        addrs = sorted({info[4][0] for info in infos})
        good(f"{host} resolves to: {', '.join(addrs)}")
        return addrs
    except Exception as e:
        bad(f"DNS lookup failed for {host}: {e}")
        return []


def check_tls_handshake(host: str):
    banner("4) TLS Handshake (raw)")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                proto = ssock.version()
                good(f"TLS handshake OK. Protocol: {proto}")
                subj = dict(x[0] for x in cert.get('subject', []))
                issuer = dict(x[0] for x in cert.get('issuer', []))
                note(f"Cert subject CN: {subj.get('commonName')}, issuer CN: {issuer.get('commonName')}")
    except Exception as e:
        bad(f"TLS handshake failed: {e}")


def http_get(url: str, trust_env: bool):
    """
    Perform a GET with/without env proxies. Return (ok, status, elapsed_ms, body_excerpt or error).
    """
    sess = requests.Session()
    sess.trust_env = trust_env  # True uses system/env proxies; False ignores them
    t0 = time.time()
    try:
        r = sess.get(url, timeout=TIMEOUT)
        dt = (time.time() - t0) * 1000
        excerpt = (r.text or "")[:160].replace("\n", " ")
        return True, r.status_code, dt, excerpt
    except requests.exceptions.Timeout as e:
        return False, None, (time.time() - t0) * 1000, f"Timeout: {e}"
    except requests.exceptions.SSLError as e:
        return False, None, (time.time() - t0) * 1000, f"SSL error: {e}"
    except requests.exceptions.ProxyError as e:
        return False, None, (time.time() - t0) * 1000, f"Proxy error: {e}"
    except requests.exceptions.RequestException as e:
        return False, None, (time.time() - t0) * 1000, f"Request error: {e}"


def test_public_endpoints():
    banner("5) Public Endpoints (with and without proxies)")
    for url in PUBLIC_URLS:
        print(f"\nGET {url}")
        ok1, st1, dt1, ex1 = http_get(url, trust_env=True)
        ok2, st2, dt2, ex2 = http_get(url, trust_env=False)

        if ok1:
            good(f"[trust_env=True ] HTTP {st1} in {dt1:.0f} ms  | Excerpt: {ex1}")
        else:
            bad(f"[trust_env=True ] {ex1} ({dt1:.0f} ms)")

        if ok2:
            good(f"[trust_env=False] HTTP {st2} in {dt2:.0f} ms  | Excerpt: {ex2}")
        else:
            bad(f"[trust_env=False] {ex2} ({dt2:.0f} ms)")

        # Quick verdict
        if ok1 or ok2:
            note("→ Reachable ✔ (public).")
        else:
            warn("→ Not reachable (public); network or proxy is blocking.")


def test_private_connectivity():
    banner("6) Private Endpoint Connectivity (no API key needed for this check)")
    print(f"\nGET {PRIVATE_URL} (we EXPECT a quick 4xx if the path is open)")
    ok1, st1, dt1, ex1 = http_get(PRIVATE_URL, trust_env=True)
    ok2, st2, dt2, ex2 = http_get(PRIVATE_URL, trust_env=False)

    if ok1:
        if 400 <= st1 < 500:
            good(f"[trust_env=True ] HTTP {st1} in {dt1:.0f} ms → Path is OPEN (auth missing, as expected).")
        else:
            note(f"[trust_env=True ] HTTP {st1} in {dt1:.0f} ms | Excerpt: {ex1}")
    else:
        bad(f"[trust_env=True ] {ex1} ({dt1:.0f} ms) → If this is a timeout, something blocks private calls.")

    if ok2:
        if 400 <= st2 < 500:
            good(f"[trust_env=False] HTTP {st2} in {dt2:.0f} ms → Path is OPEN (auth missing, as expected).")
        else:
            note(f"[trust_env=False] HTTP {st2} in {dt2:.0f} ms | Excerpt: {ex2}")
    else:
        bad(f"[trust_env=False] {ex2} ({dt2:.0f} ms) → If this is a timeout, something blocks private calls.")

    verdict = []
    if ok1 and 400 <= st1 < 500: verdict.append("env-proxy path OPEN")
    if ok2 and 400 <= st2 < 500: verdict.append("direct path OPEN")

    if verdict:
        good("Summary: private endpoint is reachable; your auth signing/allow-list will be the next step.")
    else:
        warn("Summary: private endpoint did not return a fast 4xx. If you saw timeouts, it's likely filtering/TLS inspection/proxy issues.")


def main():
    banner("Binance Futures Connectivity Diagnostic")
    note(f"Time: {datetime.utcnow().isoformat()}Z")
    note(f"Target host: {HOST}")
    check_env_proxies()
    check_public_ip()
    check_dns_resolution(HOST)
    check_tls_handshake(HOST)
    test_public_endpoints()
    test_private_connectivity()

    banner("7) What the results mean")
    print(textwrap.dedent("""
      • If public endpoints are fast but the private one TIMEOUTS → something on the path
        (firewall/TLS inspection/proxy) filters private calls. Use VPN/another network or
        adjust those controls.

      • If both with and without proxies work (fast 4xx on the private URL) → your network path
        is fine; next focus on correct request signing, timestamp/recvWindow, and allow-listed IPs.

      • If 'trust_env=True' fails but 'trust_env=False' works → your environment proxies are the issue.

      • If DNS or TLS handshake fails → fix DNS or disable HTTPS scanning that injects certs.
    """).strip())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
