import paho.mqtt.client as PahoMQTT

class MySubscriber():
    def __init__(self, clientID, host, port, topic):
        self.clientID = clientID
        self.host = host
        self.port = port
        self.topic = topic

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False) 

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def start (self):
        #manage connection to broker
        self._paho_mqtt.connect(self.host, self.port)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop (self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
    
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print "Connected to message broker with result code: "+str(rc)

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        print "Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'"
