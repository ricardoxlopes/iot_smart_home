import paho.mqtt.client as PahoMQTT

class MyPublisher:
    def __init__(self, clientID, host, port, topic):
        self.clientID = clientID
        self.host = host
        self.port = port
        self.topic = topic

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.host, self.port)  # 'iot.eclipse.org', 1883)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        # publish a message with a certain topic
        self. _paho_mqtt.publish(topic, message, 2)

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: "+str(rc))
