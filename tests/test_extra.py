import pytest
from unittest.mock import patch, MagicMock
import sys
import platform
from sysdox.extra import (
    get_pip_packages, get_apt_packages, get_pacman_packages, 
    get_dnf_packages, get_brew_packages, get_choco_packages, all_packages, dump
)

# Test get_pip_packages()
@patch("sysdox.extra.subprocess.check_output")
def test_get_pip_packages(mock_check_output):
    """Test pip package retrieval."""
    mock_check_output.return_value = b"package1==1.0.0\npackage2==2.0.0"
    
    packages = get_pip_packages()
    
    assert isinstance(packages, dict), "Expected a dictionary"
    assert packages == {"package1": "1.0.0", "package2": "2.0.0"}, "Mismatch in pip packages"

@patch("sysdox.extra.subprocess.check_output", side_effect=Exception("Command failed"))
def test_get_pip_packages_failure(mock_check_output):
    """Test pip package retrieval failure."""
    packages = get_pip_packages()
    assert packages == {}, "Expected empty dictionary when subprocess fails"

# Test get_apt_packages()
@patch("sysdox.extra.subprocess.check_output")
def test_get_apt_packages(mock_check_output):
    """Test APT package retrieval."""
    mock_check_output.return_value = b"apt-package1=1.0.0\napt-package2=2.0.0"
    
    packages = get_apt_packages()
    
    assert isinstance(packages, dict), "Expected a dictionary"
    assert packages == {"apt-package1": "1.0.0", "apt-package2": "2.0.0"}, "Mismatch in APT packages"

@patch("sysdox.extra.subprocess.check_output", side_effect=Exception("Command failed"))
def test_get_apt_packages_failure(mock_check_output):
    """Test APT package retrieval failure."""
    packages = get_apt_packages()
    assert packages == {}, "Expected empty dictionary when subprocess fails"

# Test get_pacman_packages()
@patch("sysdox.extra.subprocess.check_output")
def test_get_pacman_packages(mock_check_output):
    """Test Pacman package retrieval."""
    mock_check_output.return_value = b"pacman-package1 1.0.0\npacman-package2 2.0.0"
    
    packages = get_pacman_packages()
    
    assert isinstance(packages, dict), "Expected a dictionary"
    assert packages == {"pacman-package1": "1.0.0", "pacman-package2": "2.0.0"}, "Mismatch in Pacman packages"

@patch("sysdox.extra.subprocess.check_output", side_effect=Exception("Command failed"))
def test_get_pacman_packages_failure(mock_check_output):
    """Test Pacman package retrieval failure."""
    packages = get_pacman_packages()
    assert packages == {}, "Expected empty dictionary when subprocess fails"

# Test get_dnf_packages()
@patch("sysdox.extra.subprocess.check_output") # TODO: fix this
def test_get_dnf_packages(mock_check_output):
    """Test DNF package retrieval."""
    mock_check_output.return_value = b"dnf-package1 1.0.0\ndnf-package2 2.0.0"
    
    packages = get_dnf_packages()
    
    assert isinstance(packages, dict), "Expected a dictionary"
    assert packages == {"dnf-package1": "1.0.0", "dnf-package2": "2.0.0"}, "Mismatch in DNF packages"

@patch("sysdox.extra.subprocess.check_output", side_effect=Exception("Command failed"))
def test_get_dnf_packages_failure(mock_check_output):
    """Test DNF package retrieval failure."""
    packages = get_dnf_packages()
    assert packages == {}, "Expected empty dictionary when subprocess fails"

# Test get_brew_packages()
@patch("sysdox.extra.subprocess.check_output")
def test_get_brew_packages(mock_check_output):
    """Test Brew package retrieval."""
    mock_check_output.return_value = b"brew-package1 1.0.0\nbrew-package2 2.0.0"
    
    packages = get_brew_packages()
    
    assert isinstance(packages, dict), "Expected a dictionary"
    assert packages == {"brew-package1": "1.0.0", "brew-package2": "2.0.0"}, "Mismatch in Brew packages"

@patch("sysdox.extra.subprocess.check_output", side_effect=Exception("Command failed"))
def test_get_brew_packages_failure(mock_check_output):
    """Test Brew package retrieval failure."""
    packages = get_brew_packages()
    assert packages == {}, "Expected empty dictionary when subprocess fails"

# Test get_choco_packages()
@patch("sysdox.extra.subprocess.check_output") # TODO: fix this
def test_get_choco_packages(mock_check_output):
    """Test Choco package retrieval."""
    mock_check_output.return_value = b"choco-package1 1.0.0\nchoco-package2 2.0.0"
    
    packages = get_choco_packages()
    
    assert isinstance(packages, dict), "Expected a dictionary"
    assert packages == {"choco-package1": "1.0.0", "choco-package2": "2.0.0"}, "Mismatch in Choco packages"

@patch("sysdox.extra.subprocess.check_output", side_effect=Exception("Command failed"))
def test_get_choco_packages_failure(mock_check_output):
    """Test Choco package retrieval failure."""
    packages = get_choco_packages()
    assert packages == {}, "Expected empty dictionary when subprocess fails"

# Test all_packages()
@patch("sysdox.extra.platform.system") # TODO: fix this
@patch("sysdox.extra.shutil.which")
def test_all_packages_linux(mock_system, mock_which):
    """Test all packages retrieval on Linux."""
    mock_system.return_value = "Linux"
    mock_which.return_value = "/usr/bin/apt"  # Simulating APT packages

    # Mock subprocess to return some APT packages
    with patch("sysdox.extra.subprocess.check_output") as mock_check:
        mock_check.return_value = b"apt-package1=1.0.0\napt-package2=2.0.0"
        
        packages = all_packages()
        assert packages == {"apt-package1": "1.0.0", "apt-package2": "2.0.0"}, "Mismatch in all packages for Linux"

@patch("sysdox.extra.platform.system")
def test_all_packages_darwin(mock_system):
    """Test all packages retrieval on macOS."""
    mock_system.return_value = "Darwin"
    
    with patch("sysdox.extra.subprocess.check_output") as mock_check:
        mock_check.return_value = b"brew-package1 1.0.0\nbrew-package2 2.0.0"
        
        packages = all_packages()
        assert packages == {"brew-package1": "1.0.0", "brew-package2": "2.0.0"}, "Mismatch in all packages for macOS"

@patch("sysdox.extra.platform.system") # TODO: fix this
def test_all_packages_windows(mock_system):
    """Test all packages retrieval on Windows."""
    mock_system.return_value = "Windows"
    
    with patch("sysdox.extra.subprocess.check_output") as mock_check:
        mock_check.return_value = b"choco-package1 1.0.0\nchoco-package2 2.0.0"
        
        packages = all_packages()
        assert packages == {"choco-package1": "1.0.0", "choco-package2": "2.0.0"}, "Mismatch in all packages for Windows"

# Test dump()
def test_dump():
    """Test dump function."""
    with patch("sysdox.extra.all_packages") as mock_all_packages:
        mock_all_packages.return_value = {"package1": "1.0.0", "package2": "2.0.0"}
        data = dump()
        assert "packages" in data, "'packages' key is missing in dump() output"
        assert data["packages"] == {"package1": "1.0.0", "package2": "2.0.0"}, "Mismatch in dump() output"
