# Tools Suite to Dump Microsoft .NET Blazor Applications


<p align="center">
  <img src="/img/blazorrazor.png" width="200">
</p>


## BlazorRazor.py - Blazor Application Dumper

This tool is designed to identify and dump Blazor applications by accessing the `/_framework/blazor.boot.json` endpoint on a given URL. It can determine the deployment method (WASM or DLL), fetch appsettings references, and optionally download all related assemblies based on user input.

### Features

- **Endpoint Check**: Verifies the existence of the `/_framework/blazor.boot.json` file at the specified URL.
- **Deployment Method Identification**: Determines whether the application uses WebAssembly (WASM) or DLL-based deployment.
- **Appsettings Fetching**: Retrieves and saves appsettings files referenced in the Blazor boot JSON.
- **Selective Assembly Dumping**: 
  - Asks the user if Microsoft and System assemblies should be dumped.
  - Allows the user to choose whether to dump all assemblies (common and uncommon) or just the uncommon ones.
  - Logs any assemblies that could not be downloaded.

#### Running the Tool

- Save the common assemblies in the following files:
  - common_wasm_assemblies.txt
  - common_dll_assemblies.txt
- Run the script with the URL to check:
```sh
python3 BlazorRazor.py http://example.com
```


#### Example Output
```sh
[+] The file has been identified at: http://example.com/_framework/blazor.boot.json and will be parsed.
[+] Deployment method: WASM
[+] Retrieved appsettings.json content:
{
  "Setting1": "Value1",
  "Setting2": "Value2"
}
[+] Saved appsettings.json to /path/to/output/appsettings.json
[+] Do you want to dump Microsoft and System assemblies? (y/N): n
[+] Do you want to dump all assemblies (common and uncommon)? (Y/n): y
[+] Saved assembly to /path/to/output/assembly.dll
```
## BlazorSecrets.py - Directory Secret Scanner for Blazor Dumps

`BlazorSecrets.py` is designed to process directories dumped by `BlazorRazor.py`, decompiling or extracting strings from files to identify potential secrets like passwords and API keys.

### Features

- **String Extraction**: Extracts readable text from files using the `strings` command.
- **Secret Pattern Matching**: Identifies common secret patterns (e.g., passwords, API keys).
- **WASM Decompilation**: Decompiles WebAssembly (WASM) files to C code and WebAssembly Text (WAT).
- **Contextual Snippets**: Saves text snippets around identified secrets for easier analysis.

#### Running the Tool

1. Ensure WASM decompilation tools (`wasm-decompile`, `wasm2wat`) are available.
2. Run the script with the directory to process:

```sh
python3 BlazorSecrets.py /path/to/directory
```

#### Example Output

```sh
[+] Decompiling WASM file: example.wasm
[+] Converting WASM to WAT: example.wasm
[+] Running strings on file: example.dll
[+] Potential secrets found in example.dll:
    - gomuGomuNoPassword
    - API_KEY_1234567890
[+] Saved output to /path/to/output
```

## BlazorBootDump.py - Blazor Boot JSON Dumper

`BlazorBootDump.py` scans a list of IP addresses to identify HTTP or HTTPS services running Blazor applications and dumps the `blazor.boot.json` file for further analysis.

### Features

- **Service Detection**: Identifies HTTP and HTTPS services running Blazor applications.
- **Boot JSON Dumping**: Fetches and saves the `blazor.boot.json` file from identified services.
- **Assembly Analysis**: Aggregates and reports occurrences of assemblies found in the boot JSON files.

### Running the Tool

1. Create a file containing a list of IP addresses or domains, one per line.
2. Run the script with the path to the IP address file:

#### Example Output

```sh
[+] Processing IP: 192.168.1.1
[+] Trying URL: http://192.168.1.1
[+] Trying URL: https://192.168.1.1
[+] Processing IP: 192.168.1.2
[+] Trying URL: http://192.168.1.2
[+] The file does not exist at: http://192.168.1.2/_framework/blazor.boot.json
[+] Trying URL: https://192.168.1.2
[+] SSL error occurred while fetching https://192.168.1.2/_framework/blazor.boot.json: ...
[+] Saved JSON to /path/to/output/192_168_1_1_http.json

[+] Assembly Statistics:
[+] mscorlib.dll: 2 occurrences
[+] System.dll: 1 occurrences
```

## BlazorAnalyse.py - Blazor Assembly Statistics Analyzer

`BlazorAnalyse.py` processes directories dumped by `BlazorBootDump.py` to analyze and generate statistics on commonly found assemblies.

### Features

- **Assembly Analysis**: Counts occurrences of assemblies in `blazor.boot.json` files.
- **Common Assemblies Identification**: Identifies assemblies that appear in at least 70% of the analyzed files.
- **Report Generation**: Generates text files listing common WebAssembly (WASM) and DLL assemblies.

#### Running the Tool

1. Ensure the `stats` directory contains JSON files dumped by `BlazorBootDump.py`.
2. Run the script to analyze the assemblies:

```sh
python3 BlazorAnalyse.py
```

#### Example Output

```sh
[+] WASM Assembly Statistics:
[+] mscorlib.dll
[+] System.dll

[+] DLL Assembly Statistics:
[+] mscorlib.dll
[+] System.Core.dll
```
