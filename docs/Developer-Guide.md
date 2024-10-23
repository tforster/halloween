# Developer Guide <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->

- [References](#references)
- [Tools](#tools)
  - [adafruit-ampy 1.1.0](#adafruit-ampy-110)
  - [MicroPython Remote Control](#micropython-remote-control)

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

See https://docs.micropython.org/en/latest/reference/mpremote.html

```shell
# Connect
/home/tforster/.local/bin/mpremote connect /dev/ttyUSB0
# Disconnect
/home/tforster/.local/bin/mpremote connect /dev/ttyUSB0


```
