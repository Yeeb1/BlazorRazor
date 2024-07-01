import argparse
import requests
import urllib3
import json
import os
from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_common_assemblies(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def check_endpoint(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    output_dir = os.path.join(os.getcwd(), host)
    
    endpoint = f"{url.rstrip('/')}/_framework/blazor.boot.json"
    try:
        response = requests.get(endpoint, verify=False)
        if response.status_code == 200:
            print(f"[+] The file has been identified at: {endpoint} and will be parsed.")
            parse_json(response.text, url, output_dir)
        else:
            print(f"[+] The file does not exist at: {endpoint}")
    except requests.exceptions.RequestException as e:
        print(f"[+] An error occurred: {e}")

def parse_json(json_content, base_url, output_dir):
    try:
        data = json.loads(json_content)
        if "resources" in data:
            resources = data["resources"]
            if "wasmNative" in resources:
                print("[+] Deployment method: WASM")
            elif "assembly" in resources:
                print("[+] Deployment method: DLL")
            else:
                print("[+] Deployment method could not be determined.")
        else:
            print("[+] Invalid JSON format: 'resources' key not found.")
        
        if "config" in data:
            appsettings = data["config"]
            fetch_appsettings(appsettings, base_url, output_dir)
        elif "appsettings" in data:
            appsettings = data["appsettings"]
            fetch_appsettings(appsettings, base_url, output_dir)
        else:
            print("[+] No appsettings references found.")
        
        common_wasm_assemblies = read_common_assemblies("common_wasm_assemblies.txt")
        common_dll_assemblies = read_common_assemblies("common_dll_assemblies.txt")
        
        dump_ms_system = input("[+] Do you want to dump Microsoft and System assemblies? (y/N): ").strip().lower() in ['y', 'yes']
        
        dump_all = input("[+] Do you want to dump all assemblies (common and uncommon)? (Y/n): ").strip().lower() not in ['n', 'no']
        
        fetch_all_resources(resources, base_url, output_dir, dump_ms_system, dump_all, common_wasm_assemblies, common_dll_assemblies)
    except json.JSONDecodeError as e:
        print(f"[+] Error parsing JSON: {e}")

def fetch_appsettings(appsettings, base_url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for config_file in appsettings:
        config_url = f"{base_url.rstrip('/')}/{config_file.lstrip('../')}"
        try:
            response = requests.get(config_url, verify=False)
            if response.status_code == 200:
                print(f"[+] Retrieved {config_file} content:")
                print(response.text)
                output_path = os.path.join(output_dir, os.path.basename(config_file))
                with open(output_path, 'w') as f:
                    f.write(response.text)
                print(f"[+] Saved {config_file} to {output_path}")
            else:
                print(f"[+] Failed to retrieve {config_file}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[+] An error occurred while fetching {config_file}: {e}")

def fetch_all_resources(resources, base_url, output_dir, dump_ms_system, dump_all, common_wasm_assemblies, common_dll_assemblies):
    os.makedirs(output_dir, exist_ok=True)
    failed_resources = []

    for resource_type, resource_files in resources.items():
        if isinstance(resource_files, dict):
            for resource_file in resource_files:
                if not dump_ms_system and (resource_file.startswith('Microsoft.') or resource_file.startswith('System.')):
                    continue
                
                if not dump_all and (resource_file in common_wasm_assemblies or resource_file in common_dll_assemblies):
                    failed_resources.append(resource_file)
                    continue

                resource_url = f"{base_url.rstrip('/')}/_framework/{resource_file}"
                try:
                    response = requests.get(resource_url, verify=False)
                    if response.status_code == 200:
                        output_path = os.path.join(output_dir, os.path.basename(resource_file))
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"[+] Saved {resource_file} to {output_path}")
                    else:
                        failed_resources.append(resource_file)
                        print(f"[+] Failed to retrieve {resource_file}: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    failed_resources.append(resource_file)
                    print(f"[+] An error occurred while fetching {resource_file}: {e}")

    if failed_resources:
        print("[+] The following resources could not be downloaded:")
        for resource in failed_resources:
            print(f"    - {resource}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if a specific endpoint exists, determine the deployment method, and fetch appsettings references.")
    parser.add_argument("url", type=str, help="The base URL to check the endpoint.")
    args = parser.parse_args()
    check_endpoint(args.url)
