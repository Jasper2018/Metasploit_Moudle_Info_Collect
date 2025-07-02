import os
import time
import json
from pymetasploit3.msfrpc import MsfRpcClient

def connect_to_msf(password, port=55552):
    """Connect to Metasploit RPC service"""
    try:
        client = MsfRpcClient(password, port=port)
        print("[+] Successfully connected to MSF RPC server")
        return client
    except Exception as e:
        print(f"[-] Connection failed: {str(e)}")
        return None

def get_auxiliary_scanners(client):
    """Get all auxiliary/scanner modules"""
    try:
        # Get all auxiliary modules with enhanced debug output
        auxiliary_modules = client.modules.auxiliary
        print(f"[DEBUG] Found {len(auxiliary_modules)} auxiliary modules")
        print(f"[DEBUG] Sample modules (first 5): {auxiliary_modules[:5]}")

        # Use looser path filtering
        scanner_modules = [
            m for m in auxiliary_modules 
            if 'scanner' in m.lower()  # Match if path contains fragment
        ]
        
        print(f"[+] Found {len(scanner_modules)} scanner modules")
        return scanner_modules
    except Exception as e:
        print(f"[-] Failed to get modules: {str(e)}")
        return []

def save_modules_to_file(modules, file_name="all_scanners.txt"):
    """Save module list to file"""
    try:
        with open(file_name, "w") as f:
            json.dump(modules, f, indent=4)
        print(f"[+] Module list saved to {file_name}")
    except Exception as e:
        print(f"[-] Save failed: {str(e)}")

def read_console_output(console):
    """Read console output"""
    output = ""
    while True:
        result = console.read()
        output += result.get('data', '')
        if not result.get('busy', False):
            break
        time.sleep(0.1)
    return output.strip()

def process_scanners_in_chunks(client, scanners, output_dir, chunk_size=30):
    """Process scanner modules in batches"""
    total = len(scanners)
    for i in range(0, total, chunk_size):
        print(f"\n[+] Processing {i+1} to {min(i+chunk_size, total)} modules...")
        retry_modules = []
        try:
            console = client.consoles.console()
            
            for idx, module_path in enumerate(scanners[i:i+chunk_size], i+1):
                print(f"\n[+] Processing ({idx}/{total}): {module_path}")
                
                try:
                    # Module loading verification
                    console.write(f"use {module_path}")
                    use_output = read_console_output(console)
                    
                    if "Failed to load module" in use_output:
                        print(f"[-] Invalid module: {module_path}")
                        continue
                        
                    # Get detailed information
                    console.write("info")
                    info_output = read_console_output(console)
                    
                    # File saving verification
                    safe_name = module_path.replace("/", "-") + ".txt"  # Using safer naming convention
                    save_path = os.path.join(output_dir, safe_name)
                    
                    with open(save_path, "w") as f:
                        f.write(info_output)
                    
                    # Empty file detection
                    if os.path.getsize(save_path) < 100:  # Normal info output usually exceeds 100 bytes
                        print(f"[-] File content too short, marking for retry: {module_path}")
                        retry_modules.append(module_path)
                        os.remove(save_path)
                        continue
                    
                    # New: Detect Name: field occurrences
                    with open(save_path, "r") as f:
                        content = f.read()
                        name_count = content.count("Name:")
                    
                    if name_count > 1:
                        print(f"[-] Error: File {safe_name} has {name_count} 'Name:' entries, exceeding 1!")
                        os.remove(save_path)  # Remove invalid file
                        retry_modules.append(module_path)
                        continue
                    
                    print(f"[+] Saved: {safe_name}")
                    
                    console.write("back")
                    read_console_output(console)
                    
                except Exception as e:
                    print(f"[-] Processing error: {module_path} - {str(e)}")
            
            console.destroy()
            print("[+] Console session reset")
            
            # Retry mechanism
            if retry_modules:
                print(f"[!] Need to retry {len(retry_modules)} modules")
                process_scanners_in_chunks(client, retry_modules, output_dir, chunk_size=5)  # Reduce batch size for retry
            
        except Exception as e:
            print(f"[-] Console error: {str(e)}")

def main():
    # Configuration parameters
    msf_password = "JC04T8GJ"  # Change to actual password
    output_directory = "scanners_info"  # Output directory
    
    # Connection verification
    client = connect_to_msf(msf_password)
    if not client:
        return
    
    # Module acquisition
    scanners = get_auxiliary_scanners(client)
    if not scanners:
        print("[-] No scanner modules found, please check:")
        print("1. Is MSFRPC service started with -m parameter?")
        print("2. Is Metasploit installation complete?")
        print("3. Does module path contain '/scanner/'?")
        return
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    # Execute processing
    process_scanners_in_chunks(client, scanners, output_directory)
    
    print("\n[+] All scanner module information saved to:", os.path.abspath(output_directory))

if __name__ == "__main__":
    main()
