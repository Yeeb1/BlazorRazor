import argparse
import requests
import urllib3
import json
import os
from collections import Counter
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REQUEST_TIMEOUT = 10

def fetch_blazor_boot_json(url):
    endpoint = f"{url.rstrip('/')}/_framework/blazor.boot.json"
    try:
        response = requests.get(endpoint, verify=False, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            try:
                return response.json(), endpoint
            except json.JSONDecodeError:
                print(f"[+] Invalid JSON at: {endpoint}")
                return None, None
        else:
            print(f"[+] The file does not exist at: {endpoint}")
            return None, None
    except requests.exceptions.SSLError as e:
        print(f"[+] SSL error occurred while fetching {endpoint}: {e}")
        return None, None
    except requests.exceptions.ConnectionError as e:
        print(f"[+] Connection error occurred while fetching {endpoint}: {e}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"[+] An error occurred while fetching {endpoint}: {e}")
        return None, None

def analyze_ips(ips):
    assembly_counter = Counter()
    stats_dir = os.path.join(os.getcwd(), 'stats')
    os.makedirs(stats_dir, exist_ok=True)

    def process_ip(ip):
        results = []
        print(f"[+] Processing IP: {ip}")
        http_url = f"http://{ip}"
        https_url = f"https://{ip}"

        for url in [http_url, https_url]:
            print(f"[+] Trying URL: {url}")
            data, endpoint = fetch_blazor_boot_json(url)
            if data:
                if "resources" in data and "assembly" in data["resources"]:
                    assemblies = data["resources"]["assembly"]
                    assembly_counter.update(assemblies.keys())
                
                filename = os.path.join(stats_dir, f"{ip.replace('.', '_')}_{urlparse(endpoint).scheme}.json")
                with open(filename, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                print(f"[+] Saved JSON to {filename}")
                results.append((url, filename))
        return results

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_ip, ip) for ip in ips]
        for future in as_completed(futures):
            future.result()

    print("\n[+] Assembly Statistics:")
    for assembly, count in assembly_counter.most_common():
        print(f"[+] {assembly}: {count} occurrences")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and analyze blazor.boot.json from a list of IP addresses.")
    parser.add_argument("ips_file", type=str, help="The file containing the list of IP addresses to analyze.")
    args = parser.parse_args()

    if os.path.isfile(args.ips_file):
        with open(args.ips_file, 'r') as f:
            ips = [line.strip() for line in f.readlines() if line.strip()]
        analyze_ips(ips)
    else:
        print(f"[+] The file {args.ips_file} does not exist.")
