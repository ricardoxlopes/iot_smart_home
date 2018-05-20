#ThingSpeak
from __future__ import print_function
import psutil
#dht11 sensor
import RPi.GPIO as GPIO
import dht11
#others
import time
import datetime
import requests
import paho.mqtt.publish as publish

class SensorReader(object):

    def __init__(self,channelID,apiKey):
        # print "init"
        ###   Start of user configuration   ###   
        #  MQTT Connection Methods

        # Set useUnsecuredTCP to True to use the default MQTT port of 1883
        # This type of unsecured MQTT connection uses the least amount of system resources.
        useUnsecuredTCP = False

        # Set useUnsecuredWebSockets to True to use MQTT over an unsecured websocket on port 80.
        # Try this if port 1883 is blocked on your network.
        useUnsecuredWebsockets = True

        # Set useSSLWebsockets to True to use MQTT over a secure websocket on port 443.
        # This type of connection will use slightly more system resources, but the connection
        # will be secured by SSL.
        useSSLWebsockets = False

        ###   End of user configuration   ###

        # The Hostname of the ThinSpeak MQTT service
        mqttHost = "mqtt.thingspeak.com"

        # Set up the connection parameters based on the connection type
        if useUnsecuredTCP:
            tTransport = "tcp"
            tPort = 1883
            tTLS = None

        if useUnsecuredWebsockets:
            tTransport = "websockets"
            tPort = 80
            tTLS = None

        if useSSLWebsockets:
            import ssl
            tTransport = "websockets"
            tTLS = {'ca_certs':"/etc/ssl/certs/ca-certificates.crt",'tls_version':ssl.PROTOCOL_TLSv1}
            tPort = 443
                
        # Create the topic string
        topic = "channels/" + channelID + "/publish/" + apiKey
        # initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()

        # read data using pin 17
        instance = dht11.DHT11(pin=17)

        while(True):

            result = instance.read()
            if result.is_valid():
                temperature=str(result.temperature)
                humidity=str(result.humidity)
                #print data
                print("Last valid input: " + str(datetime.datetime.now()))
                print("Temperature: ",temperature)
                print("Humidity: ",humidity)

                # build the payload string
                tPayload = "field1=" + temperature + "&field2=" + humidity

                # attempt to publish this data to the topic 
                try:
                    # a=publish.single(topic, payload=tPayload, hostname=mqttHost, port=tPort, tls=tTLS, transport=tTransport)
                    # print(a)
                    r=requests.get("https://api.thingspeak.com/update?api_key=QHVO77NYFDPHMX2J&field1=500")
                    # r=requests.get("https://api.thingspeak.com/update?api_key=QHVO77NYFDPHMX2J&field2="+humidity)
                except (KeyboardInterrupt):
                    break
                except requests.exceptions.RequestException as e:
                    print(e)
                else: 
                    time.sleep(5)

if __name__=='__main__':
    # The ThingSpeak Channel ID
    # Replace this with your Channel ID
    channelID = "483274"

    # The Write API Key for the channel
    # Replace this with your Write API key
    apiKey = "QHVO77NYFDPHMX2J"

    newSensor=SensorReader(channelID,apiKey)