from machine import Pin, SoftI2C, RTC, PWM
import ssd1306
import time
import utime
import machine
import _thread
import network
import urequests

led = Pin(4, Pin.OUT)

SW1 = Pin(20, Pin.IN, Pin.PULL_UP)

switch_state = False

# Create I2C object
i2c = SoftI2C(scl=Pin(3), sda=Pin(2))

# Create OLED object
oled = ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)

# Create RTC object
rtc = RTC()

# Create Ultrasonic object
trigger = Pin(10, Pin.OUT)
echo = Pin(8, Pin.IN)
distance = 0

# Create Buzzer object
buzzer = PWM(Pin(9), freq=2000, duty=512)

# Network settings
station = network.WLAN(network.STA_IF)
station.active(True)
wifi_ssid = "MSI 6182"
wifi_password = "burn01hahaha"
url = "http://wifitest.adafruit.com/testwifi/index.html"

# Define ThingSpeak API settings
THINGSPEAK_API_KEY = 'HLJG3ZCW94G3435O'  
THINGSPEAK_API_URL = 'https://api.thingspeak.com/update'

def connect_to_wifi():
    oled.fill(0)
    oled.text('Connecting to WiFi...', 0, 0)
    oled.show()
    station.connect(wifi_ssid, wifi_password)
    while not station.isconnected():
        pass
    oled.fill(0)
    oled.text('Connected!', 0, 0)
    oled.text('IP: ' + station.ifconfig()[0], 0, 10)
    oled.show()
    time.sleep(1)
    
def measure_distance():
    trigger.value(1)
    utime.sleep_us(10)
    trigger.value(0)
    while echo.value() == 0:
        pass
    start = utime.ticks_us()
    while echo.value() == 1:
        pass
    finish = utime.ticks_us()
    distance = ((finish - start) * 0.0343) / 2
    return distance

def beep_buzzer():
    buzzer.duty(512)
    time.sleep(0.1)  # Short beep
    buzzer.duty(0)
    
def display_time():
    current_datetime = rtc.datetime()
    oled.fill(0)
    oled.text('{:02d}:{:02d}:{:02d}'.format(current_datetime[4], current_datetime[5], current_datetime[6]), 0, 10)
    oled.show()
    
def display_data():
    distance = measure_distance()
    data = fetch_data_from_server()
    windspeed = data['windspeed']
    temperature = data['temperature']
    oled.fill(0)
    oled.text('Dist: {:.2f} cm'.format(distance), 0, 0)
    oled.text('Wind: {:.2f} mph'.format(windspeed), 0, 10)
    oled.text('Temp: {:.2f} C'.format(temperature), 0, 20)
    oled.show()
    return distance

def fetch_data_from_server():
    response = urequests.get('http://172.16.85.206:5000/data')
    data = response.json()
    return data

def send_to_thingspeak(field1, field2, field3):
    # Prepare data payload
    data = 'api_key={}&field1={}&field2={}&field3={}'.format(THINGSPEAK_API_KEY, field1, field2, field3)

    # Send data to ThingSpeak
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = urequests.post(THINGSPEAK_API_URL, data=data.encode(), headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        print('Data sent to ThingSpeak successfully.')
        led.value(1)  
        time.sleep(0.5)  
        led.value(0)  
    else:
        print('Failed to send data to ThingSpeak.')

    # Close the response
    response.close()
    
def buzzer_thread():
    global switch_state
    while True:
        if SW1.value() == 0:  # If switch is pressed
            switch_state = not switch_state  # Toggle the switch state
            time.sleep(2)  # Debounce delay
        if switch_state:
            display_time()
        else:
            distance = display_data()
            if distance < 30 and distance > 15:
                beep_buzzer()
                time.sleep(1)
            elif distance < 15 and distance > 5:
                beep_buzzer()
                time.sleep(0.5)
            elif distance < 5:
                beep_buzzer()
                time.sleep(0.1)
            else:
                buzzer.duty(0)  # Keep the buzzer on
            time.sleep(0)  # Add a delay of 1 second
        
def send_to_thingspeak_thread():
    while True:
        distance = measure_distance()
        data = fetch_data_from_server()
        windspeed = data['windspeed']
        temperature = data['temperature']
        send_to_thingspeak(distance, windspeed, temperature)  # Send distance, wind speed, and temperature to ThingSpeak
        time.sleep(1)  # Send data every 60 seconds
        time.sleep(0)
    
# Start by connecting to WiFi
connect_to_wifi()

# Then start the buzzer thread
_thread.start_new_thread(buzzer_thread, ())
_thread.start_new_thread(send_to_thingspeak_thread, ())
