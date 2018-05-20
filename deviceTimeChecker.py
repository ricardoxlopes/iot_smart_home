import json
import threading

class DeviceTimeChecker(object):
    """Device lifetime checker"""

    def __init__(self,name,interval):
        self.name=name
        self.interval=interval
        #device lifetime checker
        self.lifetime=180

    def check(self):
        print "Device checker ",self.getName()," working..."
        #read devices
        jsonData=open("configuration.json").read()
        updateData = json.loads(jsonData)
        for device in updateData["devices"]:
            actualTime=self.generateTimestamp()
            deviceTime=parser.parse(device["timeStamp"])
            #check lifetime
            delta=actualTime-deviceTime
            if delta.seconds > self.lifetime:
                #remove device
                updateData["devices"].remove(device)
                print "Device checker ",self.getName," deleted device with id: ",device["id"]
                #update data
                with open("configuration.json","w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
        #launch new thread
        threading.Timer(self.getInterval(), self.check).start()

    def generateTimestamp(self):
         return datetime.datetime.now()

    def getInterval(self):
        return self.interval

    def getName(self):
        return self.name