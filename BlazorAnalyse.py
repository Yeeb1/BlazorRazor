import os
import json
from collections import Counter

def analyze_stats_directory(stats_dir):
    wasm_assembly_counter = Counter()
    dll_assembly_counter = Counter()
    total_files_wasm = 0
    total_files_dll = 0
    
    for filename in os.listdir(stats_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(stats_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if "resources" in data:
                        if "wasmNative" in data["resources"]:
                            total_files_wasm += 1
                            if "assembly" in data["resources"]:
                                assemblies = data["resources"]["assembly"]
                                wasm_assembly_counter.update(assemblies.keys())
                        elif "assembly" in data["resources"]:
                            total_files_dll += 1
                            assemblies = data["resources"]["assembly"]
                            dll_assembly_counter.update(assemblies.keys())
            except (json.JSONDecodeError, IOError) as e:
                print(f"[+] An error occurred while processing {filename}: {e}")

    common_wasm_assemblies = {assembly for assembly, count in wasm_assembly_counter.items() if count / total_files_wasm >= 0.7}
    common_dll_assemblies = {assembly for assembly, count in dll_assembly_counter.items() if count / total_files_dll >= 0.7}
    
    print("\n[+] WASM Assembly Statistics:")
    for assembly in sorted(common_wasm_assemblies):
        print(f"[+] {assembly}")

    print("\n[+] DLL Assembly Statistics:")
    for assembly in sorted(common_dll_assemblies):
        print(f"[+] {assembly}")
    
    with open("common_wasm_assemblies.txt", "w") as wasm_file:
        for assembly in sorted(common_wasm_assemblies):
            wasm_file.write(f"{assembly}\n")

    with open("common_dll_assemblies.txt", "w") as dll_file:
        for assembly in sorted(common_dll_assemblies):
            dll_file.write(f"{assembly}\n")

if __name__ == "__main__":
    stats_dir = os.path.join(os.getcwd(), 'stats')
    if os.path.isdir(stats_dir):
        analyze_stats_directory(stats_dir)
    else:
        print(f"[+] The directory {stats_dir} does not exist.")
