import os
import time
import json
import re
import shutil
from pymetasploit3.msfrpc import MsfRpcClient

def connect_to_msf(password, port=55552):
    """Connect to Metasploit RPC service"""
    try:
        client = MsfRpcClient(password, port=port)
        print("[+] Connected to MSF RPC server")
        return client
    except Exception as e:
        print(f"[-] Connection failed: {str(e)}")
        return None

def get_all_payloads(client):
    """Retrieve all payload modules"""
    try:
        payload_paths = client.modules.payloads
        print(f"[+] Found {len(payload_paths)} payload modules")
        return payload_paths
    except Exception as e:
        print(f"[-] Failed to get payload list: {str(e)}")
        return []

def save_payloads_to_file(payloads, file_name="all_payloads.txt"):
    """Save payload list to file"""
    try:
        with open(file_name, "w") as f:
            json.dump(payloads, f, indent=4)
        print(f"[+] Payload list saved to {file_name}")
    except Exception as e:
        print(f"[-] Failed to save list: {str(e)}")

def read_console_output(console):
    """Read console output until command completes"""
    output = ""
    while True:
        result = console.read()
        output += result.get('data', '')
        if not result.get('busy', False):
            break
        time.sleep(0.5)
    return output.strip()

def extract_html_path(console_output):
    """Extract HTML file path from console output"""
    pattern = r"opening\s+(/tmp/.+?\.html)"
    match = re.search(pattern, console_output)
    if match:
        return match.group(1)
    return None

def copy_html_file(html_path, output_path):
    """Copy HTML file to specified location"""
    try:
        if os.path.exists(html_path):
            shutil.copy(html_path, output_path)
            return True
        return False
    except Exception as e:
        print(f"[-] Failed to copy HTML file: {str(e)}")
        return False

def process_payloads_in_chunks(client, payloads, output_dir, chunk_size=30):
    """Process payloads in batches and save HTML documentation"""
    total = len(payloads)
    for i in range(0, total, chunk_size):
        print(f"\n[+] Processing payloads {i+1} to {min(i + chunk_size, total)}...")
        retry_payloads = []
        try:
            console = client.consoles.console()
            time.sleep(1)

            for idx, payload_path in enumerate(payloads[i:i + chunk_size], i + 1):
                print(f"\n[+] Processing ({idx}/{total}): {payload_path}")

                try:
                    # Load module
                    console.write(f"use {payload_path}")
                    use_output = read_console_output(console)
                    
                    if "Failed to load module" in use_output:
                        print(f"[-] Invalid module: {payload_path}")
                        continue
                    
                    # Generate HTML documentation
                    console.write("info -d")
                    time.sleep(0.2)
                    info_output = read_console_output(console)
                    
                    # Extract HTML file path
                    html_path = extract_html_path(info_output)
                    
                    if not html_path:
                        print(f"[-] HTML path not found: {payload_path}")
                        retry_payloads.append(payload_path)
                        continue
                    
                    # Create safe filename
                    safe_name = payload_path.replace("/", "-").replace("\\", "_")
                    output_path = os.path.join(output_dir, f"{safe_name}.html")
                    
                    time.sleep(0.1)
                    
                    # Copy HTML file
                    if copy_html_file(html_path, output_path):
                        print(f"[+] HTML documentation copied: {os.path.basename(output_path)}")
                    else:
                        print(f"[-] Copy failed: {payload_path}")
                        retry_payloads.append(payload_path)
                    
                    # Return to previous menu
                    console.write("back")
                    time.sleep(0.1)
                    read_console_output(console)
                    time.sleep(0.1)
                
                except Exception as e:
                    print(f"[-] Error processing {payload_path}: {str(e)}")
            
            console.destroy()
            print("[+] Console session destroyed, preparing new session...")
            time.sleep(1)
            
            # Retry failed payloads
            if retry_payloads:
                print(f"\n[+] Retrying {len(retry_payloads)} failed payloads...")
                process_payloads_in_chunks(client, retry_payloads, output_dir, chunk_size=10)
        
        except Exception as e:
            print(f"[-] Console processing error: {str(e)}")

def main():
    # Configuration parameters
    msf_password = "your_password"  # Change to your MSFRPC password
    output_directory = "payloads_html_docs"
    
    # Connect to MSF
    client = connect_to_msf(msf_password)
    if not client:
        return
    
    # Get payload list
    payloads = get_all_payloads(client)
    if not payloads:
        return
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    print(f"[+] Output directory: {os.path.abspath(output_directory)}")
    
    # Process all payloads in batches
    process_payloads_in_chunks(client, payloads, output_directory, chunk_size=30)
    
    print("\n[+] All payload HTML documentation saved!")

if __name__ == "__main__":
    main()
