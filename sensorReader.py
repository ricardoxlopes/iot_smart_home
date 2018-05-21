#ThingSpeak
from __future__ import print_function
import psutil
#sensors
import RPi.GPIO as GPIO
import dht11
#others
import time
import datetime
import requests
import paho.mqtt.publish as publish
import sys
import threading

class SensorReader(threading.Thread):

    def __init__(self,threadName,sensorType):
        self.threadName=threadName
        self.sensorType=sensorType
        self.running=True

        print("Init sensor reader thread "+self.threadName)
        threading.Thread.__init__(self,name=self.threadName)
    
    def stop(self):
        self.running=False
        print("Sensor Reader Thread: "+self.threadName+" stopped.")

    def ledAlarm(self):
        GPIO.setwarnings(False)
        GPIO.setup(27,GPIO.OUT)
        print("LED on")
        GPIO.output(27,GPIO.HIGH)
        time.sleep(1)
        print("LED off")
        GPIO.output(27,GPIO.LOW)

    def buttonHandler(self):
            "Push button handler"
            GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while self.running:
                GPIO.setmode(GPIO.BCM)
                input_state = GPIO.input(18)
                if input_state == False:
                    print('Button Pressed')
                    #TODO request to make stereo play
                    time.sleep(0.2)
            print("Sensor Reader Thread: "+self.threadName+" exited.")

    def motionHandler(self):
        "Motion sensor handler"

        GPIO.setmode(GPIO.BCM)
        # Pin 23 on the board
        PIR_PIN = 23
        GPIO.setup(PIR_PIN, GPIO.IN)
        last_motion_time = time.time()

        while self.running:
            if GPIO.input(PIR_PIN):
                last_motion_time = time.time()
                sys.stdout.flush()
                print("Motion time: "+str(last_motion_time))
                # GPIO.setmode(GPIO.BCM)

                #activate led alarm
                self.ledAlarm()

                # build the payload string
                tPayload = "field3=1"

                # attempt to publish this data to the topic 
                try:
                    publish.single(self.topic, payload=tPayload, hostname=self.mqttHost, port=self.tPort, tls=self.tTLS, transport=self.tTransport)
                except (KeyboardInterrupt):
                    break
                except requests.exceptions.RequestException as e:
                    print(e)
                else: 
                    time.sleep(2)
        GPIO.cleanup()
        print("Sensor Reader Thread: "+self.threadName+" exited.")

    def humTempHandler(self):
        "Humidity and temperature sensor handler"

        # initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # read data using pin 17
        instance = dht11.DHT11(pin=17)

        while(self.running):

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
                    publish.single(self.topic, payload=tPayload, hostname=self.mqttHost, port=self.tPort, tls=self.tTLS, transport=self.tTransport)
                except (KeyboardInterrupt):
                    break
                except requests.exceptions.RequestException as e:
                    print(e)
                else: 
                    time.sleep(30)
        print("Sensor Reader Thread: "+self.threadName+" exited.")
        GPIO.cleanup()

    def run(self):
        ###   Start of user configuration   ###   

        #  ThingSpeak Channel Settings

        # The ThingSpeak Channel ID
        channelID = "483274"
        # The Write API Key for the channel
        apiKey = "QHVO77NYFDPHMX2J"
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
        self.mqttHost = "mqtt.thingspeak.com"

        # Set up the connection parameters based on the connection type
        if useUnsecuredTCP:
            self.tTransport = "tcp"
            self.tPort = 1883
            self.tTLS = None

        if useUnsecuredWebsockets:
            self.tTransport = "websockets"
            self.tPort = 80
            self.tTLS = None

        if useSSLWebsockets:
            import ssl
            self.tTransport = "websockets"
            self.tTLS = {'ca_certs':"/etc/ssl/certs/ca-certificates.crt",'tls_version':ssl.PROTOCOL_TLSv1}
            self.tPort = 443

        # Create the topic string
        self.topic = "channels/" + channelID + "/publish/" + apiKey
        
        #handler for raspberrypy sensors
        if self.sensorType == "humidity_temperature_sensor":
            self.humTempHandler()
        elif self.sensorType == "motion_sensor":
            self.motionHandler()
        elif self.sensorType == "button_sensor":
            self.buttonHandler()
        
        