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
from homeConfigurator import HomeConfigurator

"""
CONFIGURATIONS
webservice
-host
-port
-filePath: name or path of configuration file
-deviceCheckInterval: time interval to check devices
"""

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, HEAD, PUT, DELETE, OPTIONS"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "Cache-Control, X-Proxy-Authorization, X-Requested-With"

class HomeCatalog(object):
    exposed = True

    def __init__(self, host, port, filePath, deviceCheckInterval, homeConfig):
        self.host = host
        self.port = port
        self.filePath = filePath
        self.homeConfig = homeConfig
        self.deviceCheckInterval = deviceCheckInterval

        if not os.path.exists(self.filePath):
            with open(self.filePath, "a+") as outfile:
                json.dump(self.initialContent(self.host, self.port), outfile)
                outfile.close()
            print "created configuration.json"

        print "Welcome!"
        # start device checker thread
        # deviceChecker = DeviceTimeChecker("deviceChecker1",self.deviceCheckInterval,self.filePath)
        # deviceChecker.check()
        # MQTT subscriber
        mqttSubscriber = MySubscriber("subscriber1")
        mqttSubscriber.start()

    def initialContent(self, host, port):
        host = socket.gethostbyname(socket.gethostname())
        port = 8080
        return {
            "catalog": {"endpoint": host, "port": port},
            "broker": {"host": "iot.eclipse.org", "port": 1883},
            "devices": [],
            "users": []
        }

    def GET(self, *uri, **params):

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
                deviceId = str(params["id"])
                jsonData = open(self.filePath).read()
                devices = json.loads(jsonData)["devices"]
                for device in devices:
                    if device["id"] == deviceId:
                        resourcesToPrint = ""
                        for resource in device["resources"]:
                            if resourcesToPrint == "":
                                resourcesToPrint += resource
                            else:
                                resourcesToPrint += ", "+resource
                        return Msg({"resources": "["+resourcesToPrint+"]"}).info()
                return Msg("Resource not available").error()
            # elif uri[0] == "device":
            #     deviceId = params["id"]
            #     # read from config file
            #     jsonData = open(self.filePath).read()
            #     devices = json.loads(jsonData)["devices"]
            #     for device in devices:
            #         if device["id"] == deviceId:
            #             return Msg(device).info()
            #     return Msg("No device with id="+deviceId).error()
            elif uri[0] == "user":
                userId = params["id"]
                # read from config file
                jsonData = open(self.filePath).read()
                users = json.loads(jsonData)["users"]
                for user in users:
                    if user["id"] == userId:
                        return Msg(user).info()
                return Msg("No user with id="+deviceId).error()
            elif uri[0] == "home":
                jsonData = open(self.homeConfig).read()
                return jsonData
            elif uri[0] == "beacons":
                jsonData = open(self.homeConfig).read()
                beacons = json.loads(jsonData)["beacons"]
                return json.dumps(beacons)
            else:
                return Msg("Invalid uri").error()
        else:
            return Msg("Invalid number of uris").error()

    def POST(self, *uri, **params):
        if len(uri) == 1:
            if uri[0] == "addDevice":
                # read body
                body = json.loads(cherrypy.request.body.read())
                endpoint = body["endPoints"]
                resources = body["resources"]
                timestamp = body["timeStamp"]
                # check device's first occorrence
                if "id" in body:
                    newDevice = Device(endpoint, resources, body["id"])
                else:
                    newDevice = Device(endpoint, resources)

                # read from config file
                jsonData = open(self.filePath).read()
                updateData = json.loads(jsonData)
                devices = updateData["devices"]
                for device in devices:
                    if device["id"] == body["id"]:
                        devices.remove(device)
                updateData["devices"].append(newDevice.getInfo())
                # update data
                with open(self.filePath, "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return Msg({"action": "added new device", "device": newDevice.getInfo()}).info()
            elif uri[0] == "addUser":
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
                with open(self.filePath, "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return Msg({"action": "added new user", "id": newUser.getId()}).info()
            elif uri[0] == "addDivision":
                # read body
                divisionName = cherrypy.request.body.read()
                hc = HomeConfigurator(self.homeConfig)
                hc.newDivision(divisionName)
                return Msg("Added "+divisionName+" division").info()
            elif uri[0] == "addLight":
                body = json.loads(cherrypy.request.body.read())
                divisionName = body["divisionName"]
                lightName = body["lightName"]
                hc = HomeConfigurator(self.homeConfig)
                hc.newLight(divisionName, lightName)
                return Msg("Added "+lightName+" light to "+divisionName+" division").info()
            elif uri[0] == "updateLightState":
                body = json.loads(cherrypy.request.body.read())
                divisionName = body["divisionName"]
                lightName = body["lightName"]
                hc = HomeConfigurator(self.homeConfig)
                status = hc.updateLightState(divisionName, lightName)
                if status:
                    return Msg("Updated "+lightName+" light state from "+divisionName+" division").info()
                else:
                    return Msg("Could not update light state").error()
            elif uri[0] == "removeDivision":
                body = json.loads(cherrypy.request.body.read())
                divisionName = body["divisionName"]
                hc = HomeConfigurator(self.homeConfig)
                status = hc.removeDivision(divisionName)
                if status:
                    return Msg("Removed "+divisionName+" division").info()
                else:
                    return Msg("Could not remove divisison").error()
            elif uri[0] == "removeLight":
                body = json.loads(cherrypy.request.body.read())
                divisionName = body["divisionName"]
                lightName = body["lightName"]
                hc = HomeConfigurator(self.homeConfig)
                status = hc.removeLight(divisionName, lightName)
                if status:
                    return Msg("Removed "+lightName+" light from "+divisionName+" division").info()
                else:
                    return Msg("Could not remove light").error()
            else:
                return Msg("Invalid uri").error()
        else:
            return Msg("Invalid number of uris").error()

    def PUT(self, *uri, **params):
        if len(uri) == 1:
            if uri[0] == "updateLightState":
                body = json.loads(cherrypy.request.body.read())
                divisionName = body["divisionName"]
                lightName = body["lightName"]
                hc = HomeConfigurator(self.homeConfig)
                status = hc.updateLightState(divisionName, lightName)
                if status:
                    return Msg("Updated "+lightName+" light state from "+divisionName+" division").info()
                else:
                    return Msg("Could not update light state").error()
            else:
                return Msg("Invalid uri").error()
        else:
            return Msg("Invalid number of uris").error()

    def DELETE(self, *uri, **params):
        if len(uri) == 1:
            if uri[0] == "removeDivision":
                divisionName = params["divisionName"]
                hc = HomeConfigurator(self.homeConfig)
                status = hc.removeDivision(divisionName)
                if status:
                    return Msg("Removed "+divisionName+" division").info()
                else:
                    return Msg("Could not remove divisison").error()
            elif uri[0] == "removeLight":
                divisionName = params["divisionName"]
                lightName = params["lightName"]
                hc = HomeConfigurator(self.homeConfig)
                status = hc.removeLight(divisionName, lightName)
                if status:
                    return Msg("Removed "+lightName+" light from "+divisionName+" division").info()
                else:
                    return Msg("Could not remove light").error()
            else:
                return Msg("Invalid uri").error()
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
    def __init__(self, endPoints, resources, deviceId=None):
        # check device's first occorrence
        if deviceId is None:
            self.id = self.generateUniqueId()
        else:
            self.id = deviceId
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
    # Catalog configurations
    host = "192.168.1.3"
    port = 8080
    filePath = "Configuration/catalogConfiguration.json"
    homeConfig = "Configuration/homeConfiguration.json"
    deviceCheckInterval = 2000

    cherrypy.tools.CORS = cherrypy.Tool("before_handler", CORS) # This MUST run before every request sent

    # cherrypy webservice configuration
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.CORS.on': True
        }
    }
    cherrypy.tree.mount(HomeCatalog(host, port, filePath,
                                    deviceCheckInterval, homeConfig), '/', conf)
    cherrypy.config.update({'server.socket_host': host})
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.engine.start()
    cherrypy.engine.block()