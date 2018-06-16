import paho.mqtt.client as PahoMQTT
import requests
import json
from sensorReader import SensorReader
import cherrypy
import socket
from message import Msg
import os
import datetime

"""
CONFIGURATIONS
webservice
device host port
catalog endpoint: host port

Modular device, can be modified to be reused.
To be set 3 options: [host port,catalog endpoint, available resources]
Has a MQTT publisher to send messages
Handles and makes REST requests
Initialy it registers to the catalog

Raspberrypy 3 breadboard connections:
GPIO17 - dht11 sensor
GPIO18 - push button
GPIO23 - motion sensor
GPIO27 - red LED

Ground
pin 6- dht11
pin 14- push button
pin 9- motion sensor
pin 20- red LED

Power
pin 1 3v3-dht11
pin 2 5v- motion

"""

class MyDevice(object):
    exposed = True

    def __init__(self, endpoint, catalogEndpoint, resources, filePath):
        print "Init device"
        self.endpoint = endpoint
        self.catalogEndpoint = catalogEndpoint
        self.resources = resources
        self.filePath = filePath
        self.runningResources = {}
        self.broker = self.getBroker()
        self.myDevice = self.registerDevice()

    def GET(self, *uri, **params):
        if len(uri) == 0:
            return Msg("Raspberry device").info()
        elif len(uri) == 1:
            if uri[0] == "resource":
                resourceId = params["id"]
                if resourceId in self.resources:
                    if "info" in self.myDevice:
                        if resourceId in self.runningResources:
                            return self.stopResource(resourceId)
                        else:
                            return self.startResource(resourceId)
                    else:
                        return Msg("Not registered").error()
                else:
                    return Msg("Resource not available").error()
            elif uri[0] == "reboot":
                self.myDevice = self.registerDevice()
                return Msg("Device rebooted").info()
            else:
                return Msg("Invalid uri").error()
        else:
            return Msg("Invalid number of uris").error()

    def getBroker(self):
        "Get broker from catalog"
        try:
            r = requests.get(self.catalogEndpoint+'/broker')
        except requests.exceptions.RequestException as e:
            error = Msg("Unable to get broket").error()
            print e
            print error
            return error
        else:
            print "Requested broker, received: "+r.text
            return r.text

    def registerDevice(self):
        "Register device to catalog"

        print "Registering device..."
        device=None

        if os.path.exists(self.filePath):
            print "Read device from persistence..."
            jsonData = open(self.filePath).read()
            jsonData = json.loads(jsonData)
            device = jsonData["device"]
            device["timeStamp"]=str(datetime.datetime.now())
            device = json.dumps(device)
        else: device = json.dumps({"endPoints": self.endpoint,
                             "resources": self.resources})
        try:
            r = requests.post(self.catalogEndpoint +
                              '/addDevice', data=device)
        except requests.exceptions.RequestException as e:
            error = Msg("unable to register").error()
            print e
            print error
            return error
        else:
            info = json.loads(r.text)["info"]
            deviceInfo = info["device"]
            if not os.path.exists(self.filePath):
                with open(self.filePath, "a+") as outfile:
                    json.dump(deviceInfo, outfile)
                    outfile.close()
                print "created deviceConfiguration.json"
                return Msg("New device registered.").info()
            else:
                return Msg("Device already registered.").info()

    def startResource(self, resourceId):
        "Start resources by id. Possible to add new handlers for new resources such as sensors"

        if resourceId == "humidity_temperature_sensor":
            name = "humidity_temperature_sensor1"
            mySensor = SensorReader(name, "humidity_temperature_sensor")
            mySensor.start()
            self.runningResources[resourceId] = mySensor
            return Msg("Resource "+name+" started").info()
        elif resourceId == "motion_sensor":
            name = "motion_sensor1"
            mySensor = SensorReader(name, "motion_sensor")
            mySensor.start()
            self.runningResources[resourceId] = mySensor
            return Msg("Resource "+name+" started").info()
        elif resourceId == "button_sensor":
            name = "button_sensor1"
            mySensor = SensorReader(name, "button_sensor")
            mySensor.start()
            self.runningResources[resourceId] = mySensor
            return Msg("Resource "+name+" started").info()
        elif resourceId == "stereo":
            name = "stereo1"
            mySensor = SensorReader(name, "stereo")
            mySensor.start()
            self.runningResources[resourceId] = mySensor
            return Msg("Resource "+name+" started").info()
        else:
            Msg("Resource "+name+" not available").error()

    def stopResource(self, resourceId):
        "Stop resource by id"
        # stop thread
        self.runningResources[resourceId].stop()
        # delete element from dictionary
        del self.runningResources[resourceId]
        return Msg("Stopped resource "+resourceId).info()

if __name__ == '__main__':
    filePath = "Configuration/deviceConfiguration.json"

    if os.path.exists(filePath):
        jsonData = open(filePath).read()
        jsonData = json.loads(jsonData)
        device = jsonData["device"]
        endpoint = device["endPoints"]
        resources = device["resources"]
        catalogEndpoint = jsonData["catalogEndpoint"]
        newstr = endpoint.replace("/","")
        newstr=newstr.split(":")
        host = newstr[1]
        port = int(newstr[2])
        print "Reading device config..."
    else: print "ERROR: Missing "+filePath+"!"

    # Catalog endpoint
    #  catalogEndpoint = "http://192.168.1.6:8080"
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(
        MyDevice(endpoint, catalogEndpoint, resources, filePath), '/', conf)
    cherrypy.config.update({'server.socket_host': host})
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.engine.start()
    cherrypy.engine.block()