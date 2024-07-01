import argparse
import requests
import urllib3
import json
import os
import subprocess
import re
from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WASM_DECOMPILE = os.path.join(os.getcwd(), 'bin', 'wasm-decompile') # maybe modify this to use $PATH or whatever
WASM2WAT = os.path.join(os.getcwd(), 'bin', 'wasm2wat')

SECRET_PATTERNS = [
    re.compile(r'password\s*[:=]\s*["\']?(\w+)["\']?', re.IGNORECASE),
    re.compile(r'api[-_]?key\s*[:=]\s*["\']?(\w+)["\']?', re.IGNORECASE),
    re.compile(r'secret\s*[:=]\s*["\']?(\w+)["\']?', re.IGNORECASE),
    re.compile(r'aws[-_]?access[-_]?key\s*[:=]\s*["\']?(\w+)["\']?', re.IGNORECASE),
    re.compile(r'aws[-_]?secret[-_]?key\s*[:=]\s*["\']?(\w+)["\']?', re.IGNORECASE),
    re.compile(r'session[-_]?token\s*[:=]\s*["\']?(\w+)["\']?', re.IGNORECASE)
]

def run_strings(file_path):
    try:
        result = subprocess.run(['strings', file_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"[+] An error occurred while running strings on {file_path}: {e}")
        return ""

def search_secrets(text):
    secrets = []
    for pattern in SECRET_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            for match in matches:
                secrets.append((match, text.find(match)))
    return secrets

def decompile_wasm(file_path):
    try:
        result = subprocess.run([WASM_DECOMPILE, file_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"[+] An error occurred while decompiling WASM file {file_path}: {e}")
        return ""

def convert_wasm_to_wat(file_path):
    try:
        result = subprocess.run([WASM2WAT, file_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"[+] An error occurred while converting WASM to WAT for file {file_path}: {e}")
        return ""

def save_output(output, file_path):
    try:
        with open(file_path, 'w') as f:
            f.write(output)
        print(f"[+] Saved output to {file_path}")
    except Exception as e:
        print(f"[+] An error occurred while saving output to {file_path}: {e}")

def process_file(file_path, output_dir):
    if file_path.endswith('.wasm'):
        print(f"[+] Decompiling WASM file: {file_path}")
        wasm_content = decompile_wasm(file_path)
        if wasm_content:
            decompiled_path = os.path.join(output_dir, os.path.basename(file_path) + '.decompiled.c')
            save_output(wasm_content, decompiled_path)

        print(f"[+] Converting WASM to WAT: {file_path}")
        wat_content = convert_wasm_to_wat(file_path)
        if wat_content:
            wat_path = os.path.join(output_dir, os.path.basename(file_path) + '.wat')
            save_output(wat_content, wat_path)
            
        secrets = search_secrets(wasm_content)
    else:
        print(f"[+] Running strings on file: {file_path}")
        strings_output = run_strings(file_path)
        if strings_output:
            strings_path = os.path.join(output_dir, os.path.basename(file_path) + '.strings.txt')
            save_output(strings_output, strings_path)

        secrets = search_secrets(strings_output)

    if secrets:
        print(f"[+] Potential secrets found in {file_path}:")
        for secret, index in secrets:
            print(f"    - {secret}")
            save_strings_around(secret, strings_output, index, file_path, output_dir)

def save_strings_around(secret, strings_output, index, file_path, output_dir, context=10):
    start = max(index - context, 0)
    end = index + len(secret) + context
    snippet = strings_output[start:end]
    snippet_path = os.path.join(output_dir, os.path.basename(file_path) + '.snippet.txt')
    try:
        with open(snippet_path, 'a') as f:
            f.write(f"Secret: {secret}\n")
            f.write(snippet + '\n\n')
        print(f"[+] Saved snippet around secret to {snippet_path}")
    except Exception as e:
        print(f"[+] An error occurred while saving snippet to {snippet_path}: {e}")

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            output_dir = os.path.join(root, 'out')
            os.makedirs(output_dir, exist_ok=True)
            process_file(file_path, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify potential secrets in files within a folder.")
    parser.add_argument("folder", type=str, help="The folder to process.")
    args = parser.parse_args()

    if os.path.isdir(args.folder):
        process_folder(args.folder)
    else:
        print(f"[+] The folder {args.folder} does not exist.")
