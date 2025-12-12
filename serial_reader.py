# serial_reader.py
import serial
import time
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def parse_block(block):
    out = {}
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("TDS:"):
            nums = re.findall(r"[-+]?\d*\.?\d+|\d+", line)
            if nums:
                out["tds"] = float(nums[0])
        elif line.startswith("pH:"):
            nums = re.findall(r"[-+]?\d*\.?\d+|\d+", line)
            if nums:
                out["ph"] = float(nums[0])
        elif line.startswith("Water Level:"):
            nums = re.findall(r"-?\d+", line)
            if nums:
                out["water_level"] = int(nums[0])
        elif line.startswith("Light:"):
            nums = re.findall(r"[-+]?\d*\.?\d+|\d+", line)
            if nums:
                out["light"] = int(nums[0])
        elif line.startswith("Temperature:"):
            nums = re.findall(r"[-+]?\d*\.?\d+|\d+", line)
            if nums:
                out["temperature"] = float(nums[0])
    return out

def read_serial(port="COM3", baud=9600, timeout=1):
    """
    Generator yielding dicts of parsed data blocks.
    """
    try:
        ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(1)  # give Arduino reset time
    except Exception as e:
        raise RuntimeError(f"Could not open serial port {port}: {e}")

    buffer = ""
    while True:
        try:
            line = ser.readline().decode(errors="ignore")
            if not line:
                time.sleep(0.05)
                continue
            buffer += line
            if "------" in buffer:
                data = parse_block(buffer)
                buffer = ""
                yield data
        except Exception as e:
            # if serial fails, break generator
            break
    ser.close()
