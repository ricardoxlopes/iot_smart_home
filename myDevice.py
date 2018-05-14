import paho.mqtt.client as PahoMQTT
import requests
import json
from thingspeak import SensorReader
import cherrypy

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

class MyDevice(object):
	exposed=True
	
	def __init__(self,endpoint):
		self.smartHomeEndpoint='http://192.168.1.3:8080/'
		self.endpoint=endpoint
		self.broker=self.getBroker
		self.myDevice=self.registerDevice
		res=json.dumps({"msg":"started"})
		
	def GET(self,*uri):
		if len(uri) == 0:
			return json.dumps({"info":"Raspberry device"})
		elif len(uri) == 1:
			if uri[0] == "startResource":
				res=self.startResource
				return res
			else: return Msg("Invalid uri").error()
		else: return Msg("Invalid number of uris").error()

	def POST(self,*uri,**params):
		if len(uri) == 1:
			if uri[0] == "startResource":
                #read body
				body=json.loads(cherrypy.request.body.read())
				endpoint=body["resource"]
				self.startResource(resource)

	def getBroker(self):
		r = requests.get(endpoint+'broker')
		print r.text
		return r.text
	
	def registerDevice(self):
		user=json.dumps({"endpoint":self.add,"resources":["humidity_temperature_sensor"]})
		r=requests.post(self.smartHomeEndpoint+'addDevice',data = user)
		update.message.reply_text("New device added! Your smart home said:")
		update.message.reply_text(r.text)
		return r.text
	
	def startResource(self):
		mySensor=SensorReader()
		return json.dumps({"msg":"started"})

if __name__=='__main__':
	host='192.168.1.4'
	port=8080

	conf={
		'/':{
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}

	cherrypy.tree.mount(MyDevice("http://"+host+":"+str(port)+"/"),'/',conf)
	# cherrypy.config.update({'server.socket_host': '192.168.1.4'})
	cherrypy.config.update({'server.socket_host': host})
	cherrypy.config.update({'server.socket_port': port})
	cherrypy.engine.start()
	cherrypy.engine.block()

	# send=json.dumps({"name":"name1","surname":"1","surname1":"email@email."})
	# r= requests.post('http://localhost:8080/addUser',data = send )
	# print(r.text)
    
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