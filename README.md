# sysdox

**sysdox** is a modern Python tool and API for gathering detailed system diagnostics and specifications — like `neofetch`, but focused on structured output, extensibility, and developer integration.

![badge](https://img.shields.io/badge/version-1.0.0-blue.svg)
![badge](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-green.svg)
![badge](https://img.shields.io/badge/license-GNU%20GPLv3-lightgrey.svg)

## Features

- **Modular**: Collects system, CPU, RAM, firmware, and network info via separate modules

- **API**: Importable as a library to use in other Python projects

- **Cross-Platform**: Supports Linux, macOS, and Windows

## Installation

```bash
git clone https://github.com/IamTaoball/sysdox.git
cd sysdox
pip install .
```

## Usage

CLI (Terminal)
```bash
sysdox
```
Optional JSON output
```bash
sysdox --json
```
### Python API
```py
import sysdox

info = sysdox.dump()
print(info["system"]) # Prints system dump
```

## Modules

| Module     | Description                            |
|------------|----------------------------------------|
| `system`   | OS, kernel, CPU, memory, uptime        |
| `network`  | Interfaces, IPs, DNS, bandwidth stats  |
| `firmware` | BIOS version, microcode, UEFI, drives  |
| `extra`    | Package manager, environment details   |
| `specs`    | Combined hardware specs                |
