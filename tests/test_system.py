import pytest
from unittest.mock import patch
from sysdox.system import dump


@patch("sysdox.system.platform.system") # TODO: fix this
@patch("sysdox.system.platform.version")
@patch("sysdox.system.platform.architecture")
@patch("sysdox.system.platform.machine")
def test_dump(mock_machine, mock_architecture, mock_version, mock_system):
    """Test dump function."""
    
    # Mock system info
    mock_system.return_value = "Linux"
    mock_version.return_value = "5.4.0-80-generic"
    mock_architecture.return_value = ("64bit", "ELF")
    mock_machine.return_value = "x86_64"
    
    # Call the function
    data = dump()

    # Debugging output to check the returned data
    print("System Info:", data)

    # Validate structure
    assert isinstance(data, dict), "dump() should return a dictionary"
    assert "os_info" in data, "'os' key is missing in dump() output"
    assert "uptime" in data, "'os_version' key is missing in dump() output"
    assert "cpu_info" in data, "'architecture' key is missing in dump() output"
    assert "ram_info" in data, "'machine' key is missing in dump() output"
    assert "package_manager" in data, "'processor' key is missing in dump() output"

    # Validate content
    assert data["os_info"]["os"] == "Linux", "OS mismatch in dump() output"
    assert data["os_version"] == "5.4.0-80-generic", "OS version mismatch in dump() output"
    assert data["os_info"]["architecture"] == ("64bit", "ELF"), "Architecture mismatch in dump() output"
    assert data["os_info"]["architecture"] == "x86_64", "Machine mismatch in dump() output"
    assert data["cpu_info"]["processor"] == "Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz", "Processor mismatch in dump() output"


@patch("sysdox.system.platform.system", return_value="Windows") # TODO: fix this
@patch("sysdox.system.platform.version", return_value="10.0.19042")
@patch("sysdox.system.platform.architecture", return_value=("64bit", "WindowsPE"))
@patch("sysdox.system.platform.machine", return_value="AMD64")
@patch("sysdox.system.platform.processor", return_value="AMD Ryzen 7 3700X 8-Core Processor")
def test_dump_windows(mock_processor, mock_machine, mock_architecture, mock_version, mock_system):
    """Test dump for Windows."""
    
    # Call the function
    data = dump()

    # Debugging output to check the returned data
    print("System Info (Windows):", data)

    # Validate content for Windows
    assert data["os_info"]["os"] == "Windows", "OS mismatch in dump() output"
    assert data["os_version"] == "10.0.19042", "OS version mismatch in dump() output"
    assert data["architecture"] == ("64bit", "WindowsPE"), "Architecture mismatch in dump() output"
    assert data["machine"] == "AMD64", "Machine mismatch in dump() output"
    assert data["processor"] == "AMD Ryzen 7 3700X 8-Core Processor", "Processor mismatch in dump() output"


@patch("sysdox.system.platform.system", return_value="Darwin") # TODO: fix this
@patch("sysdox.system.platform.version", return_value="19.6.0")
@patch("sysdox.system.platform.architecture", return_value=("64bit", "Mach-O"))
@patch("sysdox.system.platform.machine", return_value="x86_64")
@patch("sysdox.system.platform.processor", return_value="Intel Core i9")
def test_dump_darwin(mock_processor, mock_machine, mock_architecture, mock_version, mock_system):
    """Test dump for macOS."""
    
    # Call the function
    data = dump()

    # Debugging output to check the returned data
    print("System Info (Darwin):", data)

    # Validate content for macOS
    assert data["os_info"]["os"] == "Darwin", "OS mismatch in dump() output"
    assert data["os_version"] == "19.6.0", "OS version mismatch in dump() output"
    assert data["architecture"] == ("64bit", "Mach-O"), "Architecture mismatch in dump() output"
    assert data["os_info"]["architecture"] == "x86_64", "Machine mismatch in dump() output"
    assert data["processor"] == "Intel Core i9", "Processor mismatch in dump() output"
