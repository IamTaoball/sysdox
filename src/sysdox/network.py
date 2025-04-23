import psutil
import socket
import subprocess
import platform

import socket  # Add this import

def ips():
    """Retrieve IP addresses for all network interfaces."""
    ip_addresses = {}
    for interface, addrs in psutil.net_if_addrs().items():
        ipv4 = [addr.address for addr in addrs if addr.family == socket.AF_INET]
        ipv6 = [addr.address for addr in addrs if addr.family == socket.AF_INET6]
        if ipv4 or ipv6:
            ip_addresses[interface] = {"ipv4": ipv4, "ipv6": ipv6}
    return ip_addresses


def interface():
    """Fetch network interfaces (ethernet, wifi, etc.) and stats"""
    interfaces = {}
    for interface, addrs in psutil.net_if_addrs().items():
        interfaces[interface] = {
            'ip': None,
            'mac': None
        }
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interfaces[interface]['ip'] = addr.address
            elif addr.family == psutil.AF_LINK:
                interfaces[interface]['mac'] = addr.address
    return interfaces

def interface_stats():
    """Fetch stats for each network interface (bytes sent/received, up/down)"""
    stats = {}
    io_counters = psutil.net_io_counters(pernic=True)
    
    # retrieve interface stats
    for interface, iface_stats in psutil.net_if_stats().items():
        stats[interface] = {
            'is_up': iface_stats.isup,
            'bytes_sent': io_counters.get(interface, {}).bytes_sent if interface in io_counters else None,
            'bytes_recv': io_counters.get(interface, {}).bytes_recv if interface in io_counters else None
        }
    return stats

def dns():
    """Fetch DNS servers"""
    dns_servers = []
    
    try:
        if platform.system() == "Linux":
            with open("/etc/resolv.conf", "r") as f:
                dns_servers = [line.split()[1] for line in f.readlines() if line.startswith("nameserver")]
        elif platform.system() == "Windows":
            dns_servers = subprocess.check_output(["nslookup"], stderr=subprocess.STDOUT).decode().splitlines()
            dns_servers = [line.split(":")[1].strip() for line in dns_servers if "Server" in line]
        elif platform.system() == "Darwin":
            dns_servers = subprocess.check_output("scutil --dns", shell=True).decode().splitlines()
            dns_servers = [line.split(":")[1].strip() for line in dns_servers if "nameserver" in line]
    except Exception as e:
        dns_servers = []
    
    return dns_servers

def speed():
    speeds = {}
    if platform.system() == "Linux":
        for interface in psutil.net_if_addrs():
            try:
                output = subprocess.check_output(
                    f"ethtool {interface} | grep -i speed", 
                    shell=True, 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                speed_line = output.split(':')[-1].strip()
                # if speed is still unknown
                speeds[interface] = speed_line if speed_line.lower() != "unknown!" else "Not Available"
            except subprocess.CalledProcessError:
                speeds[interface] = "Not Available"
    elif platform.system() == "Windows":
        for interface in psutil.net_if_addrs():
            try:
                output = subprocess.check_output(
                    f"netsh interface show interface \"{interface}\"", 
                    shell=True, 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                for line in output.splitlines():
                    if "Link Speed" in line:
                        speed_line = line.split(":")[-1].strip()
                        speeds[interface] = speed_line
            except subprocess.CalledProcessError:
                speeds[interface] = "Not Available"
    elif platform.system() == "Darwin":
        for interface in psutil.net_if_addrs():
            try:
                output = subprocess.check_output(
                    f"networksetup -getInfo {interface}", 
                    shell=True, 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                for line in output.splitlines():
                    if "Link Speed" in line:
                        speed_line = line.split(":")[-1].strip()
                        speeds[interface] = speed_line
            except subprocess.CalledProcessError:
                speeds[interface] = "Not Available"
    else:
        speeds[interface] = "Unsupported OS"
    return speeds

def detect_vpn_tunnels():
    vpn_keywords = {'tun', 'tap', 'ppp', 'wg', 'vpn'}
    tunnels = {}

    for iface in psutil.net_if_addrs():
        if any(iface.lower().startswith(prefix) for prefix in vpn_keywords):
            tunnels[iface] = {
                'ip': None,
                'mac': None
            }
            for addr in psutil.net_if_addrs()[iface]:
                if addr.family == socket.AF_INET:
                    tunnels[iface]['ip'] = addr.address
                elif addr.family == psutil.AF_LINK:
                    tunnels[iface]['mac'] = addr.address
    if not tunnels:
        tunnels = "No VPN tunnels detected"
    return tunnels

def current_connections():
    conns = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status != psutil.CONN_LISTEN:  # skip passive listeners
                conns.append({
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    'status': conn.status,
                    'pid': conn.pid
                })
    except Exception as e:
        conns.append({"error": str(e)})
    return conns


def dump():
    return {
        'ip_address': ips(),
        'interfaces': interface(),
        'interface_stats': interface_stats(),
        'dns_servers': dns(),
        'network_speed': speed(),
        'vpn_tunnels': detect_vpn_tunnels(),
        'connections': current_connections()
    }