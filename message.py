import json

class Msg(object):
    "Messaging class, available error and info types"
    
    def __init__(self, msg):
        self.msg = msg

    def error(self):
        return json.dumps({"error": self.getMsg()})

    def info(self):
        return json.dumps({"info": self.getMsg()})

    def getMsg(self):
        return self.msg