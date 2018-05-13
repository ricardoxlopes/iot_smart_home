
import uuid
import string

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