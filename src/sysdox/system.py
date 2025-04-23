import platform
import psutil
import socket
import time
import shutil

def os():
    if platform.system() == "Linux":
        try:
            with open('/etc/os-release') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('PRETTY_NAME'):
                    os_name = line.split('=')[1].strip().replace('"', '')
                    break
            else:
                os_name = 'Unknown Linux Distribution'
        except Exception:
            os_name = 'Unknown Linux Distribution'
    elif platform.system() == "Windows":
        os_name = platform.win32_ver()[0]
    elif platform.system() == "Darwin":
        os_name = platform.mac_ver()[0]
    else:
        os_name = 'Unknown OS'
    
    return {
        'os': platform.system(),
        'os_name': os_name,
        'os_version': platform.version(),
        'kernel': platform.release(),
        'architecture': platform.machine(),
        'hostname': socket.gethostname()
    }

def package_manager():
    """Detect the package manager used on the system."""
    if platform.system() == "Linux":
        if shutil.which("apt"):
            return "APT (Advanced Package Tool)"
        elif shutil.which("yum"):
            return "YUM (Yellowdog Updater Modified)"
        elif shutil.which("dnf"):
            return "DNF (Dandified YUM)"
        elif shutil.which("pacman"):
            return "Pacman"
        elif shutil.which("zypper"):
            return "Zypper"
        elif shutil.which("apk"):
            return "APK (Alpine Package Keeper)"
        else:
            return "Unknown Package Manager"
    elif platform.system() == "Darwin":
        if shutil.which("brew"):
            return "Homebrew"
        else:
            return "Unknown Package Manager"
    elif platform.system() == "Windows":
        return "Windows does not use a traditional package manager"
    else:
        return "Unknown Package Manager"

def cpu():
    return {
        'processor': platform.processor(),
        'physical_cores': psutil.cpu_count(logical=False),
        'logical_cores': psutil.cpu_count(logical=True),
        'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
    }

def ram():
    mem = psutil.virtual_memory()
    return {
        'total_ram': f"{mem.total / (1024**3):.2f} GB",
        'available_ram': f"{mem.available / (1024**3):.2f} GB",
        'used_ram': f"{mem.used / (1024**3):.2f} GB",
        'ram_percent': f"{mem.percent} %"
    }

def uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    return {
        'uptime_seconds': int(uptime_seconds),
        'uptime_human': time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    }

def dump():
    return {
        'os_info': os(),
        'package_manager': package_manager(),
        'cpu_info': cpu(),
        'ram_info': ram(),
        'uptime': uptime()
    }