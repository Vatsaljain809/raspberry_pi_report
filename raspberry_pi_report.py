import datetime
import platform
import subprocess

import psutil
import pynmea2
import serial

current_datetime = datetime.datetime.now()

# Get the Raspberry Pi model and serial number
pi_model = platform.machine()
pi_serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | cut -d " " -f 2', shell=True).decode().strip()

# Get the CPU temperature
cpu_temp = subprocess.check_output('vcgencmd measure_temp', shell=True).decode().replace("temp=", "").replace("'C\n",
                                                                                                              "")

# Get the CPU usage percentage
cpu_usage = psutil.cpu_percent()

# Get the available memory
memory = psutil.virtual_memory()
available_memory = memory.available / (1024 ** 2)  # Convert to megabytes

# Get the available disk space
disk = psutil.disk_usage('/')
available_disk_space = disk.free / (1024 ** 3)  # Convert to gigabytes

# GPS testing
serial_port = "/dev/ttyAMA0"  # Adjust the port as per your GPS module connection
with serial.Serial(serial_port, baudrate=9600, timeout=1) as ser:
    gps_data = ser.readline().decode().strip()
    if gps_data.startswith('$GPGGA'):
        try:
            parsed_data = pynmea2.parse(gps_data)
            latitude = parsed_data.latitude
            longitude = parsed_data.longitude
            altitude = parsed_data.altitude
        except pynmea2.ParseError:
            latitude = None
            longitude = None
            altitude = None
    else:
        latitude = None
        longitude = None
        altitude = None
report = f"Raspberry Pi Device Report\n\n"
report += f"Date and Time: {current_datetime}\n"
report += f"Raspberry Pi Model: {pi_model}\n"
report += f"Serial Number: {pi_serial}\n"
report += f"CPU Temperature: {cpu_temp}°C\n"
report += f"CPU Usage: {cpu_usage}%\n"
report += f"Available Memory: {available_memory:.2f} MB\n"
report += f"Available Disk Space: {available_disk_space:.2f} GB\n"

if latitude is not None and longitude is not None and altitude is not None:
    report += f"GPS Data:\n"
    report += f"Latitude: {latitude}\n"
    report += f"Longitude: {longitude}\n"
    report += f"Altitude: {altitude} meters\n"
else:
    report += f"No GPS data available.\n"

# Save the report to a file
with open("raspberry_pi_report.txt", "w") as file:
    file.write(report)
