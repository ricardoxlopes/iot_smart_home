import paho.mqtt.client as PahoMQTT
import requests

class MyPublisher:
	def __init__(self, clientID):
		self.clientID = clientID

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect('iot.eclipse.org', 1883)
		self._paho_mqtt.loop_start()

	def stop (self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, topic, message):
		# publish a message with a certain topic
		self. _paho_mqtt.publish(topic, message, 2)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to message broker with result code: "+str(rc))

if __name__=='__main__':
    # publisher=MyPublisher("publisher1")
    # publisher.start()
    # iterator=0
    # while(iterator < 10):
    #     publisher.myPublish("this/is/my/topic","msg")
    #     iterator+=1
    #     print(iterator)
    # publisher.stop()
    # r = requests.post('http://httpbin.org/post', data = {'key':'value'})

    r = requests.get('https://api.thingspeak.com/channels/483274/feeds.json?api_key=XR3KAGSY5OFN0N18&results=2')
    print(r.text)