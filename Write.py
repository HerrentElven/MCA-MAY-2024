import serial
import time

# Open the serial port for the Nucleo board
nucleo_serial = serial.Serial('COM4', 115200, timeout=1)

while True:
    # Read data from the Nucleo board
    if nucleo_serial.in_waiting > 0:
        data = nucleo_serial.readline().decode('utf-8').strip()
        print(f"Received from Nucleo: {data}")

        # Check if the data contains temperature or wind speed
        if 'T:' in data:
            # Write the temperature data to a file
            with open('temperature.txt', 'w') as f:
                f.write(data)
            print(f"Written temperature to file: {data}")
        elif 'W:' in data:
            # Write the wind speed data to a file
            with open('windspeed.txt', 'w') as f:
                f.write(data)
            print(f"Written wind speed to file: {data}")

    time.sleep(0.5)  # Add a delay to reduce CPU usage