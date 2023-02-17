from uModBusSerial import uModBusSerial
import time
import machine
from machine import Pin, ADC
from time import sleep
import network
from network import WLAN
from umqtt.simple import MQTTClient
ADC.width(ADC.WIDTH_10BIT)

sensor_1 = ADC(Pin(35))
sensor_1.atten(ADC.ATTN_11DB) #Full range: 3.3v

sensor_2 = ADC(Pin(33))
sensor_2.atten(ADC.ATTN_11DB) #Full range: 3.3v

WiFi_SSID = "INTELBRAS"  # Enter Wifi SSID
WiFi_PASS = "12345678"  # Enter Wifi Pasword

# ThingSpeak Credentials:

SERVER = "mqtt3.thingspeak.com"
PORT = 1883
CHANNEL_ID_1 = "1560902"
CHANNEL_ID_2 = "1578255"
PUB_TIME_SEC = 30
SERVER = "mqtt3.thingspeak.com"

# Enter Mqtt Broker Name

USER = "Cxc9AwcgIiYmBw8nCyoWKhw"  # Enter User Id here
CLIENT_ID = "Cxc9AwcgIiYmBw8nCyoWKhw" #Enter Client Id here
PASSWORD = "0fSLNz7pL3o54mkcs52R0OEa" #Enter Password here

#create topic to publish the message

topic_1 = "channels/" + CHANNEL_ID_1 + "/publish" 
topic_2 = "channels/" + CHANNEL_ID_2 + "/publish" 

G15 = Pin(15, Pin.OUT)
G16 = Pin(16, Pin.OUT)
G17 = Pin(17, Pin.OUT)

# define pin 2 (LED) as output
led = Pin(2, Pin.OUT)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WiFi_SSID, WiFi_PASS)
        while not wlan.isconnected():
            pass
    print("Connected to Wifi Router")

uart_id = 0x02
modbus_obj=uModBusSerial(uart_id,pins=(17,16),ctrl_pin=15)
slave_addr_1=0x15
slave_addr_2=0x6
starting_address=0x114
register_quantity=20
signed=False

def main():
    while(1):
        try:
            wifi_connect()
            led.on()
            media_1 = 0
            media_2 = 0
            for j in range(1000):
                temp_1 = (sensor_1.read()*(0.0032258)*25)
                media_1 = media_1 + temp_1
                temp_2 = (sensor_2.read()*(0.0032258)*25)
                media_2 = media_2 + temp_2
            temp_1 = media_1/1000
            temp_2 = media_2/1000
            
            a = modbus_obj.read_holding_registers(slave_addr_1, starting_address, register_quantity, signed)
            
            payload_1 = "field1="+str(a[15]/1000.0)+"&field2="+str(a[17]/1000.0)+"&field3="+str(a[1])+"&field4="+str(a[7])+"&field5="+str(temp_1)

            time.sleep(1)
            
            b = modbus_obj.read_holding_registers(slave_addr_2, starting_address, register_quantity, signed)
            
            payload_2 = "field1="+str(b[15]/1000.0)+"&field2="+str(b[17]/1000.0)+"&field3="+str(b[1])+"&field4="+str(b[7])+"&field5="+str(temp_2)

            #create a client, connect to the mqtt broker...

            client = MQTTClient(CLIENT_ID, SERVER, PORT, USER, PASSWORD)

            client.connect()
            
            client.publish(topic_1, payload_1)
            
            client.publish(topic_2, payload_2)
            
            client.disconnect()
            
            led.off()
            
            time.sleep(PUB_TIME_SEC)
            
        except:
            
            machine.reset()

main()
