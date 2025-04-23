import subprocess
import platform
import sys
import os
import shutil

def get_pip_packages():
    """List pip packages and versions"""
    try:
        output = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=freeze']).decode().splitlines()
        return dict(line.split('==') for line in output if '==' in line)
    except Exception:
        return {}

def get_apt_packages():
    """List APT packages and versions"""
    try:
        output = subprocess.check_output(['dpkg-query', '-W', '-f=${Package}=${Version}\n']).decode().splitlines()
        return dict(line.split('=') for line in output if '=' in line)
    except Exception:
        return {}

def get_pacman_packages():
    try:
        output = subprocess.check_output(['pacman', '-Q']).decode().splitlines()
        return dict(line.split(' ') for line in output if ' ' in line)
    except Exception:
        return {}

def get_dnf_packages():
    try:
        output = subprocess.check_output(['dnf', 'list', 'installed']).decode().splitlines()[1:]
        return {
            line.split()[0]: line.split()[1]
            for line in output if len(line.split()) >= 2
        }
    except Exception:
        return {}

def get_brew_packages():
    try:
        output = subprocess.check_output(['brew', 'list', '--versions']).decode().splitlines()
        return {
            line.split()[0]: line.split()[1]
            for line in output if len(line.split()) >= 2
        }
    except Exception:
        return {}

def get_choco_packages():
    try:
        output = subprocess.check_output(['choco', 'list', '-lo']).decode().splitlines()[1:]
        return {
            line.split()[0]: line.split()[1]
            for line in output if len(line.split()) >= 2
        }
    except Exception:
        return {}

def all_packages():
    system = platform.system()
    packages = {}

    if system == "Linux":
        if os.path.exists('/usr/bin/apt') or os.path.exists('/bin/apt'):
            packages.update(get_apt_packages())
        elif shutil.which('dnf'):
            packages.update(get_dnf_packages())
        elif shutil.which('pacman'):
            packages.update(get_pacman_packages())
    elif system == "Darwin":
        packages.update(get_brew_packages())
    elif system == "Windows":
        packages.update(get_choco_packages())

    # add pip packages universally
    packages.update(get_pip_packages())

    return packages

def dump():
    return {
        'packages': all_packages()
    }