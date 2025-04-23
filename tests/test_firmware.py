import pytest
from unittest.mock import patch, mock_open
from sysdox.firmware import get_file_content, run_command, get_linux_firmware, get_windows_firmware, get_darwin_firmware, dump
import subprocess

def test_get_file_content():
    # Test reading a valid file
    with patch("builtins.open", mock_open(read_data="test content")):
        assert get_file_content("/path/to/file") == "test content"

    # Test reading a file with no permissions
    with patch("builtins.open", side_effect=PermissionError):
        assert get_file_content("/path/to/file") == "Permission denied"

    # Test reading a non-existent file
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert get_file_content("/path/to/file") is None


def test_run_command():
    # Test running a valid command
    with patch("subprocess.check_output", return_value=b"command output"):
        assert run_command("echo test") == "command output"

    # Test running a command that times out
    with patch("subprocess.check_output", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=3)):
        assert run_command("sleep 5", timeout=3) == "Timed out"

    # Test running an invalid command
    with patch("subprocess.check_output", side_effect=Exception):
        assert run_command("invalid_command") is None


@patch("sysdox.firmware.get_file_content")
@patch("sysdox.firmware.run_command")
def test_get_linux_firmware(mock_run_command, mock_get_file_content):
    # Mock file content
    mock_get_file_content.side_effect = lambda path: {
        "/sys/class/dmi/id/bios_version": "1.0.0",
        "/sys/class/dmi/id/bios_date": "2025-01-01",
        "/sys/class/dmi/id/sys_vendor": "TestVendor",
        "/sys/class/dmi/id/board_name": "TestBoard",
        "/proc/cpuinfo": "microcode : 0x1"
    }.get(path, None)

    # Mock command output
    mock_run_command.side_effect = lambda cmd, timeout=None: {
        "fwupdmgr get-devices": "Device1\nDevice2",
        "lsblk -dno NAME": "sda\nsdb",
        "smartctl -i /dev/sda": "Firmware Version: 1.23",
        "smartctl -i /dev/sdb": "Firmware Version: 4.56"
    }.get(cmd, None)

    result = get_linux_firmware()
    assert result["bios_version"] == "1.0.0"
    assert result["bios_date"] == "2025-01-01"
    assert result["vendor"] == "TestVendor"
    assert result["motherboard"] == "TestBoard"
    assert result["cpu_microcode"] == "0x1"
    assert result["fwupd_devices"] == ["Device1", "Device2"]
    assert result["storage_firmware"]["/dev/sda"] == "1.23"
    assert result["storage_firmware"]["/dev/sdb"] == "4.56"


@patch("sysdox.firmware.run_command")
def test_get_windows_firmware(mock_run_command):
    # Mock command output
    mock_run_command.side_effect = lambda cmd: {
        "wmic bios get SMBIOSBIOSVersion,ReleaseDate /format:list": "SMBIOSBIOSVersion=1.0.0\nReleaseDate=20250101",
        "wmic baseboard get Product,Manufacturer /format:list": "Manufacturer=TestVendor\nProduct=TestBoard",
        'powershell -Command "Confirm-SecureBootUEFI"': "True"
    }.get(cmd, None)

    result = get_windows_firmware()
    assert result["bios_version"] == "1.0.0"
    assert result["bios_date"] == "20250101"
    assert result["vendor"] == "TestVendor"
    assert result["motherboard"] == "TestBoard"
    assert result["uefi"] is True


@patch("sysdox.firmware.run_command")
def test_get_darwin_firmware(mock_run_command):
    # Mock command output
    mock_run_command.return_value = (
        "Model Name: MacBook Pro\n"
        "Boot ROM Version: 1.0.0\n"
        "SMC Version: 2.3f35"
    )

    result = get_darwin_firmware()
    assert result["model"] == "MacBook Pro"
    assert result["bios_version"] == "1.0.0"
    assert result["smc_version"] == "2.3f35"
    assert result["uefi"] is True


@patch("sysdox.firmware.platform.system")
@patch("sysdox.firmware.get_linux_firmware")
@patch("sysdox.firmware.get_windows_firmware")
@patch("sysdox.firmware.get_darwin_firmware")
def test_dump(mock_darwin, mock_windows, mock_linux, mock_platform):
    # Test Linux
    mock_platform.return_value = "Linux"
    mock_linux.return_value = {"bios_version": "1.0.0"}
    assert dump() == {"bios_version": "1.0.0"}

    # Test Windows
    mock_platform.return_value = "Windows"
    mock_windows.return_value = {"bios_version": "1.0.0"}
    assert dump() == {"bios_version": "1.0.0"}

    # Test Darwin
    mock_platform.return_value = "Darwin"
    mock_darwin.return_value = {"bios_version": "1.0.0"}
    assert dump() == {"bios_version": "1.0.0"}

    # Test Unsupported Platform
    mock_platform.return_value = "Unsupported"
    assert dump() == {"firmware": "Unsupported platform"}