import platform
import subprocess
import os

def get_file_content(path):
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except PermissionError:
        return "Permission denied"
    except Exception:
        return None

def run_command(cmd, timeout=3):
    try:
        return subprocess.check_output(cmd, shell=True, timeout=timeout).decode()
    except subprocess.TimeoutExpired:
        return "Timed out"
    except Exception:
        return None

def get_linux_firmware():
    info = {
        "bios_version": get_file_content("/sys/class/dmi/id/bios_version"),
        "bios_date": get_file_content("/sys/class/dmi/id/bios_date"),
        "vendor": get_file_content("/sys/class/dmi/id/sys_vendor"),
        "motherboard": get_file_content("/sys/class/dmi/id/board_name"),
        "uefi": os.path.exists("/sys/firmware/efi"),
    }

    cpuinfo = get_file_content("/proc/cpuinfo")
    if cpuinfo and "microcode" in cpuinfo:
        try:
            info["cpu_microcode"] = cpuinfo.split("microcode")[-1].strip().split()[1]
        except:
            info["cpu_microcode"] = "Unknown"
    else:
        info["cpu_microcode"] = "Unknown"

    # Firmware update devices
    fwupd_output = run_command("fwupdmgr get-devices", timeout=4)
    if fwupd_output and fwupd_output != "Timed out":
        info["fwupd_devices"] = [
            line.strip() for line in fwupd_output.splitlines()
            if line.strip() and not line.startswith("Devices")
        ]
    else:
        info["fwupd_devices"] = "Unavailable"

    # Storage firmware info
    info["storage_firmware"] = {}
    lsblk_output = run_command("lsblk -dno NAME")
    if lsblk_output:
        for disk in lsblk_output.strip().splitlines():
            device = f"/dev/{disk.strip()}"
            smart_info = run_command(f"smartctl -i {device}", timeout=3)
            if smart_info:
                for line in smart_info.splitlines():
                    if "Firmware Version" in line:
                        info["storage_firmware"][device] = line.split(":")[1].strip()
                        break
                else:
                    info["storage_firmware"][device] = "Unknown"
            else:
                info["storage_firmware"][device] = "Unavailable"
    else:
        info["storage_firmware"] = "Unavailable"

    return info

def get_windows_firmware():
    info = {}
    try:
        output = run_command("wmic bios get SMBIOSBIOSVersion,ReleaseDate /format:list")
        if output:
            for line in output.strip().splitlines():
                if "SMBIOSBIOSVersion" in line:
                    info["bios_version"] = line.split("=")[1].strip()
                elif "ReleaseDate" in line:
                    info["bios_date"] = line.split("=")[1].strip()

        output = run_command("wmic baseboard get Product,Manufacturer /format:list")
        if output:
            for line in output.strip().splitlines():
                if "Manufacturer" in line:
                    info["vendor"] = line.split("=")[1].strip()
                elif "Product" in line:
                    info["motherboard"] = line.split("=")[1].strip()

        output = run_command('powershell -Command "Confirm-SecureBootUEFI"')
        info["uefi"] = "True" in output if output else "Unknown"

    except Exception:
        info["bios_version"] = "Unavailable"
        info["uefi"] = "Unknown"

    return info

def get_darwin_firmware():
    info = {}
    try:
        output = run_command("system_profiler SPHardwareDataType")
        for line in output.splitlines():
            if "Model Name" in line:
                info["model"] = line.split(":")[1].strip()
            elif "Boot ROM Version" in line:
                info["bios_version"] = line.split(":")[1].strip()
            elif "SMC Version" in line:
                info["smc_version"] = line.split(":")[1].strip()
    except:
        info["bios_version"] = "Unavailable"
    info["uefi"] = True
    return info

def dump():
    system = platform.system()
    if system == "Linux":
        return get_linux_firmware()
    elif system == "Windows":
        return get_windows_firmware()
    elif system == "Darwin":
        return get_darwin_firmware()
    else:
        return {"firmware": "Unsupported platform"}