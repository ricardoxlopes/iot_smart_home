import cherrypy
import json
import string
import sys
import uuid
import datetime

class HomeCatalog(object):
    exposed=True
    devices=[]
    users=[]

    def GET(self,*uri):

        if len(uri) == 0:
            return json.dumps({"info":"Smart Home"})
        elif len(uri) == 1:
            if uri[0] == "broker":
                res=MessageBroker().getInfo()
                return res
            elif uri[0] == "devices":
                devices=[]
                for device in self.devices:
                    devices.append(device.getInfo())
                return json.dumps({"devices":devices})
            elif uri[0] == "users":
                users=[]
                for user in self.users:
                    users.append(user.getInfo())
                return json.dumps({"users":users})
            else: return Msg("Invalid uri").error()
        else: return Msg("Invalid number of uris").error()
            
    def POST(self,*uri,**params):
        if len(uri) == 1:
            if uri[0] == "addDevice":
                body=json.loads(cherrypy.request.body.read())
                endpoint=body["endpoint"]
                resources=body["resources"]
                newDevice=Device(endpoint,resources)
                self.devices.append(newDevice)
                return Msg("Added new device "+newDevice.getId()).info()
            if uri[0] == "device":
                body=json.loads(cherrypy.request.body.read())
                deviceId=body["id"]
                for device in self.devices:
                    if device.getId() == deviceId:
                        return json.dumps(device.getInfo())
                return Msg("No device with id="+deviceId).error()
            if uri[0] == "user":
                body=json.loads(cherrypy.request.body.read())
                userId=body["id"]
                for user in self.users:
                    if user.getId() == userId:
                        return json.dumps(user.getInfo())
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
        return datetime.datetime.now().isoformat()
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
                            "timestamp":self.generateTimestamp()}

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
