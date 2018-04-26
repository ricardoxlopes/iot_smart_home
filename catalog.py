import cherrypy
import json
import string
import sys
import uuid
import datetime
import os
import threading
import numpy as np
from dateutil import parser

import paho.mqtt.client as PahoMQTT

class MySubscriber:
		def __init__(self, clientID):
			self.clientID = clientID
			# create an instance of paho.mqtt.client
			self._paho_mqtt = PahoMQTT.Client(clientID, False) 

			# register the callback
			self._paho_mqtt.on_connect = self.myOnConnect
			self._paho_mqtt.on_message = self.myOnMessageReceived

			self.topic = '/this/is/my/topic'


		def start (self):
			#manage connection to broker
			self._paho_mqtt.connect('iot.eclipse.org', 1883)
			self._paho_mqtt.loop_start()
			# subscribe for a topic
			self._paho_mqtt.subscribe(self.topic, 2)

		def stop (self):
			self._paho_mqtt.unsubscribe(self.topic)
			self._paho_mqtt.loop_stop()
			self._paho_mqtt.disconnect()

		def myOnConnect (self, paho_mqtt, userdata, flags, rc):
			print ("Connected to message broker with result code: "+str(rc))

		def myOnMessageReceived (self, paho_mqtt , userdata, msg):
			# A new message is received
			print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")

class deviceTimeChecker(object):

    def __init__(self,name,interval):
        self.name=name
        self.interval=interval
        self.lifetime=120

    def check(self):
        print("Device checker ",self.getName()," working...")
        #read devices
        jsonData=open("configuration.json").read()
        updateData = json.loads(jsonData)
        for device in updateData["devices"]:
            actualTime=self.generateTimestamp()
            deviceTime= parser.parse(device["timeStamp"])
            #check lifetime
            delta=actualTime-deviceTime
            if delta.seconds > self.lifetime:
                #remove device
                updateData["devices"].remove(device)
                print("Device checker ",self.getName," deleted device with id: ",device["id"])
                #update data
                with open("configuration.json","w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
        threading.Timer(self.getInterval(), self.check).start()

    def generateTimestamp(self):
         return datetime.datetime.now()

    def getInterval(self):
        return self.interval

    def getName(self):
        return self.name

class HomeCatalog(object):
    exposed=True
    filePath="configuration.json"
    deviceCheckInterval=60
    initialContent={
        "broker":{"ip":"","port":""},
        "devices":[],
        "users":[]
    }

    def __init__(self):
        if not os.path.exists(self.filePath):
            with open("configuration.json","a+") as outfile:
                json.dump(self.initialContent, outfile)
                outfile.close()
            print("created configuration.json")
        print("Welcome!")
        #start thread
        deviceChecker = deviceTimeChecker("deviceChecker1",self.deviceCheckInterval)
        deviceChecker.check()
        #MQTT subscriber
        mqttSubscriber=MySubscriber("subscriber1")
        mqttSubscriber.start()

    def GET(self,*uri):

        if len(uri) == 0:
            return json.dumps({"info":"Smart Home"})
        elif len(uri) == 1:
            if uri[0] == "broker":
                jsonData=open(self.filePath).read()
                address = json.loads(jsonData)["broker"]
                res=json.dumps(address)
                return res
            elif uri[0] == "devices":
                jsonData=open(self.filePath).read()
                devices = json.loads(jsonData)["devices"]
                res=json.dumps({"devices":devices})
                return res
            elif uri[0] == "users":
                jsonData=open(self.filePath).read()
                users = json.loads(jsonData)["users"]
                res=json.dumps({"users":users})
                return res
            else: return Msg("Invalid uri").error()
        else: return Msg("Invalid number of uris").error()
            
    def POST(self,*uri,**params):
        if len(uri) == 1:
            if uri[0] == "addDevice":
                #read body
                body=json.loads(cherrypy.request.body.read())
                endpoint=body["endpoint"]
                resources=body["resources"]
                #create device
                newDevice=Device(endpoint,resources)
                #read from config file
                jsonData=open(self.filePath).read()
                updateData = json.loads(jsonData)
                updateData["devices"].append(newDevice.getInfo())
                #update data
                with open("configuration.json","w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return Msg("Added new device "+newDevice.getId()).info()
            if uri[0] == "addUser":
                #read body
                body=json.loads(cherrypy.request.body.read())
                name=body["name"]
                surname=body["surname"]
                email=body["email"]
                #create user
                newUser=User(name,surname,email)
                #read from config file
                jsonData=open(self.filePath).read()
                updateData = json.loads(jsonData)
                updateData["users"].append(newUser.getInfo())
                #update data
                with open("configuration.json","w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return Msg("Added new user "+newUser.getId()).info()
            if uri[0] == "device":
                body=json.loads(cherrypy.request.body.read())
                deviceId=body["id"]
                #read from config file
                jsonData=open(self.filePath).read()
                devices = json.loads(jsonData)["devices"]
                for device in devices:
                    if device["id"] == deviceId:
                        return json.dumps(device)
                return Msg("No device with id="+deviceId).error()
            if uri[0] == "user":
                body=json.loads(cherrypy.request.body.read())
                userId=body["id"]
                #read from config file
                jsonData=open(self.filePath).read()
                users = json.loads(jsonData)["users"]
                for user in users:
                    if user["id"] == userId:
                        return json.dumps(user)
                return Msg("No user with id="+deviceId).error()
        else: return Msg("Invalid number of uris").error()

class Msg(object):

    def __init__(self,msg):
        self.msg=msg
    
    def error(self):
        return json.dumps({"error": self.getMsg()})
    
    def info(self):
        return json.dumps({"info": self.getMsg()})
    
    def getMsg(self):
        return self.msg
 
class MessageBroker(object):
    """Message broker class"""

    def __init__(self):
        self.address='localhost'
        self.port=8080
    
    def getAddress(self):
        return self.address
    
    def getPort(self):
        return self.port
    
    def getInfo(self):
        return json.dumps({"ip":self.getAddress(),"port":self.getPort()})

class User(object):

    def __init__(self,name,surname,email):
        self.id=self.generateUniqueId()
        self.name=name
        self.surname=surname
        self.email=email
    
    def generateUniqueId(self):
        return str(uuid.uuid4())
    def getId(self):
        return self.id
    def getName(self):
        return self.name
    def getSurname(self):
        return self.surname
    def getEmail(self):
        return self.email
    def getInfo(self):
        return {"id":self.getId(),
                            "name":self.getName(),
                            "surname":self.getSurname(),
                            "email":self.getEmail()}

class Device(object):

    def __init__(self,endPoints,resources):
        self.id=self.generateUniqueId()
        self.endPoints=endPoints
        self.resources=resources
        self.timestamp=self.generateTimestamp()

    def generateTimestamp(self):
        return str(datetime.datetime.now())
    def generateUniqueId(self):
        return str(uuid.uuid4())
    def getId(self):
        return self.id
    def getEndPoints(self):
        return self.endPoints
    def getResources(self):
        return self.resources
    def getTimestamp(self):
        return self.timestamp
    def getInfo(self):
        return {"id":self.getId(),
                            "endPoints":self.getEndPoints(),
                            "resources":self.getResources(),
                            "timeStamp":self.generateTimestamp()}

if __name__=='__main__':
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    cherrypy.tree.mount(HomeCatalog(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
