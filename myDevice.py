import paho.mqtt.client as PahoMQTT
import requests
import json
from sensorReader import SensorReader
import cherrypy
import socket
from message import Msg

"""

Modular device, can be modified to be reused.
To be set 3 options: [host port,catalog endpoint, available resources]
Has a MQTT publisher to send messages
Handles and makes REST requests
Initialy it registers to the catalog

"""

class MyPublisher:
	def __init__(self, clientID,host,port,topic):
		self.clientID = clientID
		self.host=host
		self.port=port
		self.topic=topic

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(host,port) #'iot.eclipse.org', 1883)
		self._paho_mqtt.loop_start()

	def stop (self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, topic, message):
		# publish a message with a certain topic
		self. _paho_mqtt.publish(topic, message, 2)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to message broker with result code: "+str(rc))

class MyDevice(object):
	exposed=True
	
	def __init__(self,endpoint,catalogEndpoint,resources):
		print "Init device"
		self.endpoint=endpoint
		self.catalogEndpoint=catalogEndpoint
		self.resources=resources
		self.broker=self.getBroker()
		self.myDevice=self.registerDevice()
		
	def GET(self,*uri,**params):
		if len(uri) == 0:
			return Msg("Raspberry device").info()
		elif len(uri) == 1:
			if uri[0] == "resource":
				if params["id"] in self.resources:
					if "info" in self.myDevice:
						res=self.startResource()
						return res
					else: Msg("Not registered").error()
				else: Msg("Resource not available").error()
		else: return Msg("Invalid number of uris").error()

	def getBroker(self):
		try:
			print self.catalogEndpoint+'/broker'
			r = requests.get(self.catalogEndpoint+'/broker')
		except requests.exceptions.RequestException as e:
			error=Msg("Unable to get broket").error()
			print e
			print error
			return error
		else:
			print "Requested broker, received: "+r.text
			return r.text

	def registerDevice(self):
		print "Registering device..."
		user=json.dumps({"endpoint":self.endpoint,"resources":self.resources})
		try:
			r=requests.post(self.catalogEndpoint+'/addDevice',data = user)
		except requests.exceptions.RequestException as e:
			error=Msg("unable to register").error()
			print e
			print error
			return error
		else:
			info=json.loads(r.text)["info"]
			deviceId=info["id"]
			return Msg({"id":deviceId}).info()
	
	def startResource(self,resourceId):
		"Possible to add new handlers for new resources such as sensors"
		if resourceId == "humidity_temperature_sensor":
			mySensor=SensorReader()
			return Msg("Resource started").info()
		elif resourceId == "anotherResource":
			print "add handler"
		else: Msg("Resource not available").error()

if __name__=='__main__':
	#My Device settings
	host = "192.168.1.4"
	port = 8080
	endpoint="http://"+host+":"+str(port)+"/"
	resources=["humidity_temperature_sensor"]
	#Catalog endpoint
	catalogEndpoint="http://192.168.1.5:8080"
	conf={
		'/':{
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}
	cherrypy.tree.mount(MyDevice(endpoint,catalogEndpoint,resources),'/',conf)
	cherrypy.config.update({'server.socket_host': host})
	cherrypy.config.update({'server.socket_port': port})
	cherrypy.engine.start()
	cherrypy.engine.block()

	#TODO read broker info and start sending messages

	# publisher=MyPublisher("publisher1")
    # publisher.start()
    # iterator=0
    # while(iterator < 10):
    #     publisher.myPublish("this/is/my/topic","msg")
    #     iterator+=1
    #     print(iterator)
    # publisher.stop()
    # r = requests.post('http://httpbin.org/post', data = {'key':'value'})

    # r = requests.get('https://api.thingspeak.com/channels/483274/feeds.json?api_key=XR3KAGSY5OFN0N18&results=2')
    # print(r.text)