import cherrypy
import json
import string
import sys
import datetime
import os
import numpy as np
from dateutil import parser
import uuid
from subscriber import MySubscriber
from deviceTimeChecker import DeviceTimeChecker
from user import User
import socket
from message import Msg

class HomeCatalog(object):
    exposed = True

    filePath = "configuration.json"
    deviceCheckInterval = 2000

    def __init__(self,host,port):
        if not os.path.exists(self.filePath):
            with open("configuration.json", "a+") as outfile:
                json.dump(self.initialContent(host,port), outfile)
                outfile.close()
            print "created configuration.json"

        print "Welcome!"
        # start device checker thread
        # deviceChecker = DeviceTimeChecker("deviceChecker1",self.deviceCheckInterval)
        # deviceChecker.check()
        # MQTT subscriber
        mqttSubscriber = MySubscriber("subscriber1")
        mqttSubscriber.start()

    def initialContent(self,host,port):
        host = socket.gethostbyname(socket.gethostname())
        port = 8080
        return {
            "catalog": {"endpoint": host, "port": port},
            "broker": {"host": "iot.eclipse.org", "port": 1883},
            "devices": [],
            "users": []
        }
    
    def GET(self, *uri,**params):

        if len(uri) == 0:
            return json.dumps({"info": "Smart Home"})
        elif len(uri) == 1:
            if uri[0] == "broker":
                jsonData = open(self.filePath).read()
                address = json.loads(jsonData)["broker"]
                return Msg(address).info()
            elif uri[0] == "devices":
                jsonData = open(self.filePath).read()
                devices = json.loads(jsonData)["devices"]
                return Msg({"devices": devices}).info()
            elif uri[0] == "users":
                jsonData = open(self.filePath).read()
                users = json.loads(jsonData)["users"]
                return Msg({"users": users}).info()
            elif uri[0] == "resources":
                deviceId=str(params["id"])
                jsonData = open(self.filePath).read()
                devices = json.loads(jsonData)["devices"]
                for device in devices:
                    if device["id"] == deviceId:
                        resourcesToPrint=""
                        for resource in device["resources"]:
                            if resourcesToPrint == "":
                                resourcesToPrint+=resource
                            else: resourcesToPrint+=", "+resource
                        return Msg({"resources":"["+resourcesToPrint+"]"}).info()
                return Msg("Resource not available").error()
            elif uri[0] == "device":
                deviceId=params["id"]
                # read from config file
                jsonData = open(self.filePath).read()
                devices = json.loads(jsonData)["devices"]
                for device in devices:
                    if device["id"] == deviceId:
                        return Msg(device).info()
                return Msg("No device with id="+deviceId).error()
            elif uri[0] == "user":
                userId=params["id"]
                # read from config file
                jsonData = open(self.filePath).read()
                users = json.loads(jsonData)["users"]
                for user in users:
                    if user["id"] == userId:
                        return Msg(user).info()
                return Msg("No user with id="+deviceId).error()
            else:
                return Msg("Invalid uri").error()
        else:
            return Msg("Invalid number of uris").error()

    def POST(self, *uri, **params):
        if len(uri) == 1:
            if uri[0] == "addDevice":
                # read body
                body = json.loads(cherrypy.request.body.read())
                endpoint = body["endpoint"]
                resources = body["resources"]
                # create device
                newDevice = Device(endpoint, resources)
                # read from config file
                jsonData = open(self.filePath).read()
                updateData = json.loads(jsonData)
                updateData["devices"].append(newDevice.getInfo())
                # update data
                with open("configuration.json", "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return Msg({"action":"added new device","id":newDevice.getId()}).info()
            if uri[0] == "addUser":
                # read body
                body = json.loads(cherrypy.request.body.read())
                name = body["name"]
                surname = body["surname"]
                email = body["email"]
                # create user
                newUser = User(name, surname, email)
                # read from config file
                jsonData = open(self.filePath).read()
                updateData = json.loads(jsonData)
                updateData["users"].append(newUser.getInfo())
                # update data
                with open("configuration.json", "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return Msg({"action":"added new user","id":newUser.getId()}).info()
        else:
            return Msg("Invalid number of uris").error()

class MessageBroker(object):
    """Message broker class"""

    def __init__(self):
        self.address = 'localhost'
        self.port = 8080

    def getAddress(self):
        return self.address

    def getPort(self):
        return self.port

    def getInfo(self):
        return json.dumps({"ip": self.getAddress(), "port": self.getPort()})


class Device(object):
    def __init__(self, endPoints, resources):
        self.id = self.generateUniqueId()
        self.endPoints = endPoints
        self.resources = resources
        self.timestamp = self.generateTimestamp()

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
        return {"id": self.getId(),
                "endPoints": self.getEndPoints(),
                "resources": self.getResources(),
                "timeStamp": self.generateTimestamp()}


if __name__ == '__main__':
    host = "192.168.1.5"
    port = 8080
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(HomeCatalog(host,port), '/', conf)
    cherrypy.config.update({'server.socket_host': host})
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.engine.start()
    cherrypy.engine.block()
