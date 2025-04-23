import pytest
from sysdox import system, verbose, network, firmware, extra, specs


@pytest.mark.parametrize("module_func", [
    system.dump,
    network.dump,
    firmware.dump,
    extra.dump,
    specs.dump,
])
def test_module_dump_runs(module_func):
    """Test that all dump functions return valid data."""
    result = module_func()
    assert result is not None, f"{module_func.__name__} returned None"
    assert isinstance(result, dict) or isinstance(result, list), f"{module_func.__name__} did not return a dict or list"


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4])
def test_verbose_sendLog(level):
    """Test verbose logging at different levels."""
    result = verbose.sendLog("Test message", level)
    assert result is not None, f"sendLog failed at log level {level}"
    assert isinstance(result, str), f"sendLog did not return a string at log level {level}"


def test_system_dump():
    """Test the structure and content of system.dump()."""
    data = system.dump()
    assert isinstance(data, dict), "system.dump() should return a dictionary"
    assert "os_info" in data, "'os_info' key is missing in system.dump() output"
    assert "cpu_info" in data, "'cpu_info' key is missing in system.dump() output"
    assert "ram_info" in data, "'ram_info' key is missing in system.dump() output"


def test_specs_dump():
    """Test the structure and content of specs.dump()."""
    data = specs.dump()
    assert isinstance(data, dict), "specs.dump() should return a dictionary"
    assert "cpu_info" in data, "'cpu_info' key is missing in specs.dump() output"
    assert "ram_info" in data, "'ram_info' key is missing in specs.dump() output"
    assert "storage_info" in data, "'storage_info' key is missing in specs.dump() output"


def test_network_dump():
    """Test the structure and content of network.dump()."""
    data = network.dump()
    assert isinstance(data, dict), "network.dump() should return a dictionary"
    assert "connections" in data, "'connections' key is missing in network.dump() output"
    assert isinstance(data["connections"], list), "'interfaces' should be a list in network.dump() output"


def test_firmware_dump():
    """Test the structure and content of firmware.dump()."""
    data = firmware.dump()
    assert isinstance(data, dict), "firmware.dump() should return a dictionary"
    assert "bios_version" in data, "'bios_version' key is missing in firmware.dump() output"
    assert "uefi" in data, "'uefi' key is missing in firmware.dump() output"


def test_extra_dump():
    """Test the structure and content of extra.dump()."""
    data = extra.dump()
    assert isinstance(data, dict), "extra.dump() should return a dictionary"
    assert "packages" in data, "'packages' key is missing in extra.dump() output"