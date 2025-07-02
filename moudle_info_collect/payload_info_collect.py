import os
import time
import json
from pymetasploit3.msfrpc import MsfRpcClient

def connect_to_msf(password, port=55552):
    """Connect to Metasploit RPC service"""
    try:
        client = MsfRpcClient(password, port=port)
        print("[+] Connected to MSF RPC server.")
        return client
    except Exception as e:
        print(f"[-] Connection failed: {str(e)}")
        return None

def get_all_payloads(client):
    """Get list of all payload modules"""
    try:
        payload_paths = client.modules.payloads
        print(f"[+] Found {len(payload_paths)} payload modules")
        return payload_paths
    except Exception as e:
        print(f"[-] Failed to retrieve payload list: {str(e)}")
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
        time.sleep(0.1)
    return output.strip()

def process_payloads_in_chunks(client, payloads, output_dir, chunk_size=50):
    """
    Process payloads in batches, recreating console after each chunk
    Modified default chunk size to 50 with empty file validation and retry mechanism
    """
    total = len(payloads)
    for i in range(0, total, chunk_size):
        print(f"\n[+] Processing payloads {i+1} to {min(i + chunk_size, total)}...")
        retry_payloads = []
        try:
            console = client.consoles.console()

            for idx, payload_path in enumerate(payloads[i:i + chunk_size], i + 1):
                print(f"\n[+] Processing ({idx}/{total}): {payload_path}")

                try:
                    console.write(f"use {payload_path}")
                    use_output = read_console_output(console)

                    if "Failed to load module" in use_output:
                        print(f"[-] Invalid module: {payload_path}")
                        continue

                    console.write("info")
                    info_output = read_console_output(console)

                    file_name = payload_path.replace("/", "-") + ".txt"
                    save_path = os.path.join(output_dir, file_name)

                    with open(save_path, "w") as f:
                        f.write(info_output)

                    if os.path.getsize(save_path) == 0:
                        print(f"[-] Empty file content, marking for retry: {payload_path}")
                        retry_payloads.append(payload_path)
                        os.remove(save_path)
                        continue

                    print(f"[+] Saved: {file_name}")

                    console.write("back")
                    read_console_output(console)

                except Exception as e:
                    print(f"[-] Error processing {payload_path}: {str(e)}")

            console.destroy()
            print("[+] Current console session destroyed, preparing new session...")

            if retry_payloads:
                print(f"\n[+] Retrying {len(retry_payloads)} payloads with empty files...")
                process_payloads_in_chunks(client, retry_payloads, output_dir, chunk_size=50)

        except Exception as e:
            print(f"[-] Console processing error: {str(e)}")

def main():
    # Configuration parameters
    msf_password = "password"  # Change to your MSFRPC password
    output_directory = "payloads_info"  # Output directory

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

    # Process all payloads in batches
    process_payloads_in_chunks(client, payloads, output_directory, chunk_size=50)

    print("\n[+] All payload information saved to directory:", os.path.abspath(output_directory))

if __name__ == "__main__":
    main()
