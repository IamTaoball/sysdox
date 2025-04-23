import platform
import psutil
import socket
import subprocess
import os

def get_cpu_info():
    """Get detailed CPU specs."""
    cpu_info = {}
    
    if platform.system() in ["Linux", "Darwin"]:
        try:
            cpu_info["model"] = subprocess.check_output("lscpu | grep 'Model name'", shell=True).decode().strip().split(":")[-1].strip()
            cpu_info["cores"] = psutil.cpu_count(logical=False)
            cpu_info["threads"] = psutil.cpu_count(logical=True)
            cpu_info["max_freq"] = psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown"
        except Exception as e:
            cpu_info["error"] = f"Error fetching CPU info: {str(e)}"
    
    elif platform.system() == "Windows":
        try:
            cpu_info["model"] = subprocess.check_output("wmic cpu get caption", shell=True).decode().strip().splitlines()[1].strip()
            cpu_info["cores"] = psutil.cpu_count(logical=False)
            cpu_info["threads"] = psutil.cpu_count(logical=True)
            cpu_info["max_freq"] = subprocess.check_output("wmic cpu get maxclockspeed", shell=True).decode().strip().splitlines()[1].strip()
        except Exception as e:
            cpu_info["error"] = f"Error fetching CPU info: {str(e)}"
    
    return cpu_info

def get_ram_info():
    """Get RAM details."""
    mem = psutil.virtual_memory()
    return {
        'total': f"{mem.total / (1024 ** 3):.2f} GB",
        'available': f"{mem.available / (1024 ** 3):.2f} GB",
        'used': f"{mem.used / (1024 ** 3):.2f} GB",
        'percent': f"{mem.percent}%",
        'type': "DDR"  # placeholder bc i dont know how to get this lmfao
    }

def get_storage_info():
    """Get detailed storage info with SMART health check."""
    storage_info = {}
    partitions = psutil.disk_partitions()
    
    for part in partitions:
        device = part.device
        usage = psutil.disk_usage(part.mountpoint)
        health = "Healthy"
        
        # smart check for health
        try:
            if platform.system() == "Linux":
                smart_status = subprocess.check_output(f"smartctl -H {device}", shell=True).decode().strip()
                if "PASSED" not in smart_status:
                    health = "Warning"
            elif platform.system() == "Windows":
                smart_status = subprocess.check_output(f"wmic diskdrive where deviceid='{device}' get status", shell=True).decode().strip()
                if "OK" not in smart_status:
                    health = "Warning"
        except Exception:
            health = "Unable to check"
        
        storage_info[device] = {
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total": f"{usage.total / (1024 ** 3):.2f} GB",
            "used": f"{usage.used / (1024 ** 3):.2f} GB",
            "free": f"{usage.free / (1024 ** 3):.2f} GB",
            "percent": f"{usage.percent}%",
            "health": health
        }
    
    return storage_info

def get_motherboard_info():
    """Get motherboard details."""
    if platform.system() == "Linux":
        try:
            motherboard_info = {
                "manufacturer": subprocess.check_output("cat /sys/class/dmi/id/board_vendor", shell=True).decode().strip(),
                "model": subprocess.check_output("cat /sys/class/dmi/id/board_name", shell=True).decode().strip(),
                "serial": subprocess.check_output("cat /sys/class/dmi/id/board_serial", shell=True).decode().strip(),
            }
        except Exception:
            motherboard_info = {"error": "Unable to retrieve motherboard info on Linux"}
    elif platform.system() == "Windows":
        try:
            motherboard_info = {
                "manufacturer": subprocess.check_output("wmic baseboard get manufacturer", shell=True).decode().strip().splitlines()[1],
                "model": subprocess.check_output("wmic baseboard get product", shell=True).decode().strip().splitlines()[1],
                "serial": subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().strip().splitlines()[1],
            }
        except Exception:
            motherboard_info = {"error": "Unable to retrieve motherboard info on Windows"}
    else:
        motherboard_info = {"error": "Motherboard info is not available on this OS."}
    
    return motherboard_info

def get_gpu_info():
    """Get GPU details."""
    if platform.system() == "Linux":
        try:
            gpu_info = subprocess.check_output("lspci | grep VGA", shell=True).decode().strip()
        except subprocess.CalledProcessError:
            gpu_info = "No GPU information found"
    elif platform.system() == "Windows":
        try:
            gpu_info = subprocess.check_output("wmic path win32_videocontroller get caption", shell=True).decode().strip().splitlines()[1]
        except Exception:
            gpu_info = "No GPU information found"
    else:
        gpu_info = "GPU information is not available"
    
    return gpu_info


def get_sound_info():
    """Get sound card info."""
    sound_info = {}
    if platform.system() == "Linux":
        try:
            sound_info["devices"] = subprocess.check_output("aplay -l", shell=True).decode().strip()
        except subprocess.CalledProcessError:
            sound_info["error"] = "No sound card detected"
    elif platform.system() == "Windows":
        try:
            sound_info["devices"] = subprocess.check_output("wmic sounddev get caption", shell=True).decode().strip().splitlines()[1:]
        except Exception:
            sound_info["error"] = "No sound card detected"
    
    return sound_info

def get_battery_info():
    """Get battery info (if applicable)."""
    battery_info = {}
    if platform.system() == "Linux":
        battery = psutil.sensors_battery()
        if battery:
            battery_info = {
                "percent": f"{battery.percent}%",
                "plugged": battery.power_plugged,
                "time_left": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNKNOWN else "Unknown"
            }
    elif platform.system() == "Windows":
        battery = psutil.sensors_battery()
        if battery:
            battery_info = {
                "percent": f"{battery.percent}%",
                "plugged": battery.power_plugged,
                "time_left": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNKNOWN else "Unknown"
            }
    if not battery_info:
        battery_info = {"error": "No battery information available"}
    elif battery.secsleft == -1:
        battery_info["time_left"] = "indefinite"
    return battery_info

def get_temperature_info():
    """Get temperature sensors info."""
    temperature_info = {}
    if platform.system() == "Linux":
        try:
            temp = psutil.sensors_temperatures()
            if temp:
                temperature_info = {sensor: values[0].current for sensor, values in temp.items()}
        except Exception:
            temperature_info["error"] = "Unable to fetch temperature data"
    if not temperature_info:
        temperature_info = {"error": "No temperature information available"}
    return temperature_info

def get_fan_info():
    """Get fan info (if applicable)."""
    fan_info = {}
    if platform.system() == "Linux":
        try:
            fan = psutil.sensors_fans()
            if fan:
                fan_info = {sensor: values[0] for sensor, values in fan.items()}
        except Exception:
            fan_info["error"] = "Unable to fetch fan data"
    if not fan_info:
        fan_info = {"error": "No fan information available"}
    
    return fan_info

def dump():
    """Compile all system specs."""
    return {
        "cpu_info": get_cpu_info(),
        "ram_info": get_ram_info(),
        "storage_info": get_storage_info(),
        "motherboard_info": get_motherboard_info(),
        "gpu_info": get_gpu_info(),
        "sound_info": get_sound_info(),
        "battery_info": get_battery_info(),
        "temperature_info": get_temperature_info(),
        "fan_info": get_fan_info()
    }
