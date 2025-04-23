from . import system, network, extra, firmware, specs

def dump():
    """Main API entry point to get all sys info."""
    return {
        "system": system.dump(),
        "network": network.dump(),
        "extra": extra.dump(),
        "firmware": firmware.dump(),
        "specs": specs.dump()
    }