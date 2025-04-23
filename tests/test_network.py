import pytest
from unittest.mock import patch, MagicMock
import platform
import psutil
from sysdox.network import (
    ips, interface, interface_stats, dns, speed, 
    detect_vpn_tunnels, current_connections, dump
)

# Test ips()
@patch("psutil.net_if_addrs") # TODO: fix this
def test_ips(mock_net_if_addrs):
    """Test the ips() function."""
    mock_net_if_addrs.return_value = {
        "eth0": [
            MagicMock(family=psutil.AF_INET, address="192.168.1.1"),
            MagicMock(family=psutil.AF_INET6, address="fe80::1")
        ],
        "wlan0": [
            MagicMock(family=psutil.AF_INET, address="192.168.1.2"),
            MagicMock(family=psutil.AF_INET6, address="fe80::2")
        ]
    }
    
    result = ips()
    
    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert "eth0" in result
    assert "ipv4" in result["eth0"]
    assert result["eth0"]["ipv4"] == ["192.168.1.1"]
    assert result["eth0"]["ipv6"] == ["fe80::1"]
    assert "wlan0" in result
    assert result["wlan0"]["ipv4"] == ["192.168.1.2"]
    assert result["wlan0"]["ipv6"] == ["fe80::2"]

# Test interface()
@patch("psutil.net_if_addrs") # TODO: fix this
def test_interface(mock_net_if_addrs):
    """Test the interface() function."""
    mock_net_if_addrs.return_value = {
        "eth0": [
            MagicMock(family=psutil.AF_INET, address="192.168.1.1"),
            MagicMock(family=psutil.AF_LINK, address="00:11:22:33:44:55")
        ]
    }
    
    result = interface()
    
    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert "eth0" in result
    assert result["eth0"]['ip'] == "192.168.1.1"
    assert result["eth0"]['mac'] == "00:11:22:33:44:55"

# Test interface_stats()
@patch("psutil.net_if_stats")
@patch("psutil.net_io_counters")
def test_interface_stats(mock_net_io_counters, mock_net_if_stats):
    """Test the interface_stats() function."""
    mock_net_if_stats.return_value = {
        "eth0": MagicMock(isup=True),
        "wlan0": MagicMock(isup=False)
    }
    mock_net_io_counters.return_value = {
        "eth0": MagicMock(bytes_sent=1000, bytes_recv=2000),
        "wlan0": MagicMock(bytes_sent=500, bytes_recv=1000)
    }
    
    result = interface_stats()
    
    assert "eth0" in result
    assert result["eth0"]['is_up'] is True
    assert result["eth0"]['bytes_sent'] == 1000
    assert result["eth0"]['bytes_recv'] == 2000
    assert "wlan0" in result
    assert result["wlan0"]['is_up'] is False
    assert result["wlan0"]['bytes_sent'] == 500
    assert result["wlan0"]['bytes_recv'] == 1000

# Test dns()
@patch("platform.system") # TODO: fix this
@patch("subprocess.check_output")
def test_dns(mock_check_output, mock_platform_system):
    """Test the dns() function."""
    mock_platform_system.return_value = "Linux"
    mock_check_output.return_value = b"nameserver 8.8.8.8\nnameserver 8.8.4.4"
    
    result = dns()
    
    assert result == ["8.8.8.8", "8.8.4.4"]

# Test speed()
@patch("platform.system")
@patch("subprocess.check_output")
@patch("psutil.net_if_addrs")
def test_speed(mock_net_if_addrs, mock_check_output, mock_platform_system):
    """Test the speed() function."""
    mock_platform_system.return_value = "Linux"
    mock_net_if_addrs.return_value = {"eth0": []}
    mock_check_output.return_value = b"Speed: 1000Mb/s"
    
    result = speed()
    
    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert "eth0" in result
    assert result["eth0"] == "1000Mb/s"

# Test detect_vpn_tunnels()
@patch("psutil.net_if_addrs") # TODO: fix this
def test_detect_vpn_tunnels(mock_net_if_addrs):
    """Test the detect_vpn_tunnels() function."""
    mock_net_if_addrs.return_value = {
        "tun0": [
            MagicMock(family=psutil.AF_INET, address="10.8.0.1"),
            MagicMock(family=psutil.AF_LINK, address="00:11:22:33:44:66")
        ],
        "eth0": [
            MagicMock(family=psutil.AF_INET, address="192.168.1.1")
        ]
    }
    
    result = detect_vpn_tunnels()
    
    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert "tun0" in result
    assert result["tun0"]['ip'] == "10.8.0.1"
    assert result["tun0"]['mac'] == "00:11:22:33:44:66"
    assert "eth0" not in result  # Regular interface should not be in VPN list

# Test current_connections()
@patch("psutil.net_connections")
def test_current_connections(mock_net_connections):
    """Test the current_connections() function."""
    mock_net_connections.return_value = [
        MagicMock(laddr=MagicMock(ip="192.168.1.1", port=8080), raddr=MagicMock(ip="93.184.216.34", port=80), status="ESTABLISHED", pid=1234)
    ]
    
    result = current_connections()
    
    assert isinstance(result, list), "Expected result to be a list"
    assert len(result) == 1
    assert result[0]['local_address'] == "192.168.1.1:8080"
    assert result[0]['remote_address'] == "93.184.216.34:80"
    assert result[0]['status'] == "ESTABLISHED"
    assert result[0]['pid'] == 1234

# Test dump()
@patch("sysdox.network.ips")
@patch("sysdox.network.interface")
@patch("sysdox.network.interface_stats")
@patch("sysdox.network.dns")
@patch("sysdox.network.speed")
@patch("sysdox.network.detect_vpn_tunnels")
@patch("sysdox.network.current_connections")
def test_dump(mock_current_connections, mock_detect_vpn_tunnels, mock_speed, mock_dns, mock_interface_stats, mock_interface, mock_ips):
    """Test the dump() function."""
    mock_ips.return_value = {"eth0": {"ipv4": ["192.168.1.1"], "ipv6": []}}
    mock_interface.return_value = {"eth0": {"ip": "192.168.1.1", "mac": "00:11:22:33:44:55"}}
    mock_interface_stats.return_value = {"eth0": {"is_up": True, "bytes_sent": 1000, "bytes_recv": 2000}}
    mock_dns.return_value = ["8.8.8.8", "8.8.4.4"]
    mock_speed.return_value = {"eth0": "1000Mb/s"}
    mock_detect_vpn_tunnels.return_value = {"tun0": {"ip": "10.8.0.1", "mac": "00:11:22:33:44:66"}}
    mock_current_connections.return_value = [
        {"local_address": "192.168.1.1:8080", "remote_address": "93.184.216.34:80", "status": "ESTABLISHED", "pid": 1234}
    ]
    
    result = dump()
    
    assert "ip_address" in result
    assert "interfaces" in result
    assert "interface_stats" in result
    assert "dns_servers" in result
    assert "network_speed" in result
    assert "vpn_tunnels" in result
    assert "connections" in result
    assert isinstance(result["ip_address"], dict)
    assert isinstance(result["interfaces"], dict)
    assert isinstance(result["interface_stats"], dict)
    assert isinstance(result["dns_servers"], list)
    assert isinstance(result["network_speed"], dict)
    assert isinstance(result["vpn_tunnels"], dict)
    assert isinstance(result["connections"], list)

