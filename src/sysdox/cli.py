import argparse
import json
from pprint import pformat
from . import system, network, extra, firmware, specs
import atexit
import socket
import os
import sys

open_sockets = []

def cleanup():
    """closes open sockets"""
    for sock in open_sockets:
        try:
            sock.close()
        except Exception as e:
            print(f"Error closing socket: {e}")


atexit.register(cleanup)

def format_key(key):
    acronyms = {"os", "ip", "ram", "cpu", "dns", "mac", "vpn", "tcp", "udp", "http", "https", "ftp", "ssh", "smtp", "pop3", "imap", "ipv4", "ipv6", "usb", "gpu", "ssd", "hdd", "bios", "uefi"}
    words = key.split('_')
    return ' '.join(
        word.upper() if word.lower() in acronyms else word.capitalize()
        for word in words
    )

def print_pretty(data, indent="⤷ ", sub_indent="   ↳ "):
    """Pretty print function"""
    for section, content in data.items():
        section_title = format_key(section)
        print(f"\n{section_title}")
        
        if isinstance(content, dict):  # Handle nested dictionaries (ts pmo)
            for key, value in content.items():
                key_name = format_key(key)
                if isinstance(value, dict):  # Handle deep nested dicts (ts too)
                    print(f"{indent}{key_name}:")
                    for sub_key, sub_val in value.items():
                        sub_key_name = format_key(sub_key)
                        if isinstance(sub_val, list):  # Handle lists in nested dicts (absolute acheron)
                            print(f"{sub_indent}{sub_key_name}: {', '.join(map(str, sub_val))}")
                        else:
                            print(f"{sub_indent}{sub_key_name}: {sub_val}")
                elif isinstance(value, list):  # Handle lists directly under a key 
                    print(f"{indent}{key_name}: {', '.join(map(str, value))}")
                else:
                    print(f"{indent}{key_name}: {value}")
        elif isinstance(content, list):  # Handle lists at this point
            if all(isinstance(i, dict) for i in content):  # Handle list of dictionaries
                for item in content:
                    line = None
                    if 'local_address' in item and 'remote_address' in item:
                        line = f"{indent}{item['local_address']} → {item['remote_address']}"
                    else:
                        line = f"{indent}{pformat(item)}"
                    print(line)
                    for k, v in item.items():
                        if k not in {'local_address', 'remote_address'}:
                            print(f"{sub_indent}{format_key(k)}: {v}")
            else:  # Handle simple lists
                print(f"{indent}{', '.join(map(str, content))}")
        else:  # Handle other types of shit
            print(f"{indent}{content}")

def main():
    if os.geteuid() != 0:
        print("This command must be run as root. Please use 'sudo'.")
        sys.exit(1)
    parser = argparse.ArgumentParser(description="System Info Dumper")
    parser.add_argument('--json', action='store_true', help='Output in raw JSON format')
    parser.add_argument('-c', '--command', choices=['network', 'system', 'extra', 'firmware', 'specs'], help='Run a specific command and output its data')
    args = parser.parse_args()

    if args.command:
        if args.command == 'network':
            data = network.dump()
        elif args.command == 'system':
            data = system.dump()
        elif args.command == 'extra':
            data = extra.dump()
        elif args.command == 'firmware':
            data = firmware.dump()
        elif args.command == 'specs':
            data = specs.dump()

        if args.json:
            print(json.dumps(data, indent=4))
        else:
            print_pretty(data)
        return

    # Here are all of them dumps in case you want to mod it
    data = {**system.dump(), **network.dump(), **extra.dump(), **firmware.dump(), **specs.dump()}

    if args.json:
        print(json.dumps(data, indent=4))
    else:
        print_pretty(data)

if __name__ == "__main__":
    main()