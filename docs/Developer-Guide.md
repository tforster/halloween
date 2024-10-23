# Developer Guide <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->

- [References](#references)
- [Tools](#tools)
  - [adafruit-ampy 1.1.0](#adafruit-ampy-110)
  - [MicroPython Remote Control](#micropython-remote-control)
  - [Use PIP to instal ESPtool](#use-pip-to-instal-esptool)

## References

<https://learn.microsoft.com/en-us/windows/wsl/connect-usb>

## Tools

### adafruit-ampy 1.1.0

See <https://pypi.org/project/adafruit-ampy/>

```shell
# List files on the device

/home/tforster/.local/bin/ampy --port /dev/ttyUSB0 ls
```

### MicroPython Remote Control

See <https://docs.micropython.org/en/latest/reference/mpremote.html>

```shell
# Connect
/home/tforster/.local/bin/mpremote connect /dev/ttyUSB0
# Disconnect
/home/tforster/.local/bin/mpremote connect /dev/ttyUSB0


```

Pre req
sudo apt-get install build-essential autoconf libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev

1. Install Python
   wget <https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz>
2. Uncompress tar xf Python-3.13.0.tgz
3. cd Python-3.13.0
4. ./configure --enable-optimizations
5. make -j $(nproc)
6. sudo make altinstall
7. python3.13 --version

cd /path/to/your/project
python3.13 -m venv myenv
source myenv/bin/activate

Select the Python interpreter in VS Code:

Open the Command Palette (Ctrl+Shift+P).
Type and select Python: Select Interpreter.
Choose the interpreter from the virtual environment (myenv).

### Use PIP to instal ESPtool

pip3.13 install esptool
pip install setuptools
confirm w python -m esptool

reset with esptool.py --port /dev/ttyUSB0 erase_flash

download latest firmware from [<https://micropython.org/download/esp32/>](https://micropython.org/download/ESP32_GENERIC/)

flash with python -m esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 /mnt/chromeos/MyFiles/temp/ESP32_GENERIC-20240602-v1.23.0.bin
