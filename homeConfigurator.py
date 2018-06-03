import os
import json
import string


class HomeConfigurator(object):
    """Home Configurator"""

    def __init__(self, homeConfig):
        self.homeConfig = homeConfig

    def newDivision(self, divisionName):
        jsonData = open(self.homeConfig).read()
        updateData = json.loads(jsonData)
        divisionsNames = updateData["divisionsName"]
        divisionsNames.append(divisionName)
        divisions = updateData["divisions"]
        divisions[divisionName] = {
            "lights": []
        }
        with open(self.homeConfig, "w") as outfile:
            json.dump(updateData, outfile)
            outfile.close()

    def newLight(self, divisionName, lightName):
        jsonData = open(self.homeConfig).read()
        updateData = json.loads(jsonData)
        divisions = updateData["divisions"]
        division = divisions[divisionName]
        lights = division["lights"]
        lights.append({
            "state": False,
            "name": lightName
        })
        with open(self.homeConfig, "w") as outfile:
            json.dump(updateData, outfile)
            outfile.close()

    def removeDivision(self, divisionName):
        jsonData = open(self.homeConfig).read()
        updateData = json.loads(jsonData)
        devisionsNames = updateData["divisionsName"]
        for name in devisionsNames:
            if name == divisionName:
                index = devisionsNames.index(divisionName)
                del devisionsNames[index]
                divisions = updateData["divisions"]
                # delete division
                if divisionName in divisions:
                    del divisions[divisionName]
                else:
                    return False
                with open(self.homeConfig, "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return True
        return False

    def removeLight(self, divisionName, lightName):
        jsonData = open(self.homeConfig).read()
        updateData = json.loads(jsonData)
        divisions = updateData["divisions"]
        if divisionName in divisions:
            division = divisions[divisionName]
        else:
            return False

        lights = division["lights"]

        for light in lights:
            if light["name"] == lightName:
                index = lights.index(light)
                del lights[index]
                with open(self.homeConfig, "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return True
        else:
            return False

    def updateLightState(self, divisionName, lightName):
        jsonData = open(self.homeConfig).read()
        updateData = json.loads(jsonData)
        divisions = updateData["divisions"]
        if divisionName in divisions:
            division = divisions[divisionName]
        else:
            return False

        lights = division["lights"]

        for light in lights:
            if light["name"] == lightName:
                if light["state"]:
                    light["state"] = False
                else:
                    light["state"] = True
                with open(self.homeConfig, "w") as outfile:
                    json.dump(updateData, outfile)
                    outfile.close()
                return True
        else:
            return False
        return True
