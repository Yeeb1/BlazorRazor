# Tools Suite to Dump Blazor Applications

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

### Usage

#### Prerequisites

- Python 3.x
- `requests` library

Install the required libraries using pip:
```sh
pip install requests
```

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
