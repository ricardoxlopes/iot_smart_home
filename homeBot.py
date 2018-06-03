#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
This Bot uses the Updater class to handle the bot.

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from user import User
from message import Msg
import string
import requests
import json
import os

class MyBot(object):
    """
        TELEGRAM BOT

        Configuration:
        It is necessary to configure the catalog endpoint as address and port

        BOT COMMAND LIST:

        info - Catalog Webservice Info
        setid - Command: /setId deviceId | Ex: /setId 11-12-33-33 | Persist most used device id
        reboot - Command: /reboot deviceId | Ex: /reboot 11-12-33-33 | Update catalog's device's register
        device - Command: /device host port resources | Ex: /device localhost 8080 ["humidity"] | Add new device
        res - Command: /resource deviceId resourceId | Ex: /resouce 11-12-33-33 | Start/stop device's resource
        devices - Get list of devices
        resources - Command: /resources deviceId | Ex: /resources 11-12-33-33 | Get list of resources for a device
        adddivision - Command: /adddivision divisionName | Ex: /adddivision division1 | Create new division
        removedivision - Command: /removedivision divisionName | Ex: /removedivision division1 | Delete division
        addlight - Command: /addlight divisionName lightName | Ex: /addlight division1 light1 | Create new light
        removelight - Command: /removelight divisionName lightName | Ex: /removelight division1 light1 | Delete light
        updatelightstate - Command: /updatelightstate divisionName lightName | Ex: /updateLightState division1 light1 | Turn on/off light
        help - commands list

        UPDATE bot list:
        BOTFATHER:
        1. /setcommands
        2. choose @iotSmartHomeBot
        3. copy list
    """

    # user - Command: /user name surname email | Ex: /user name1 surname1 email1 | Add new user
    # users - Get list of users

    def __init__(self, endpoint, filePath):
        print "Bot started..."
        self.endpoint = endpoint
        self.filePath = filePath
        self.getId()
        self.tempId = None

    def updateLightState(self, bot, update,args):
        sendData=json.dumps({"divisionName":args[0],"lightName":args[1]})
        r = requests.put(self.endpoint+'/updateLightState', data=sendData)
        update.message.reply_text(r.text)

    def removeLight(self, bot, update,args):
        r = requests.delete(self.endpoint+'/removeLight?divisionName='+args[0]+'&lightName='+args[1])
        update.message.reply_text(r.text)

    def removeDivision(self, bot, update):
        r = requests.delete(self.endpoint+'/removeDivision?divisionName='+args[0])
        update.message.reply_text(r.text)

    def addLight(self, bot, update,args):
        sendData=json.dumps({"divisionName":args[0],"lightName":args[1]})
        r = requests.post(self.endpoint+'/addLight', data=sendData)
        update.message.reply_text(r.text)
    
    def addDivison(self, bot, update,args):
        r = requests.post(self.endpoint+'/addDivision', data=args[0])
        update.message.reply_text(r.text)

    def getId(self):
        if os.path.exists(self.filePath):
            jsonData = open(self.filePath).read()
            jsonData = json.loads(jsonData)
            self.tempId = jsonData["id"]
            print "Reading device id setted..."

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        print error

    def getInfo(self, bot, update):
        try:
            r = requests.get(self.endpoint+"/home")
        except requests.exceptions.RequestException as e:
            error = Msg("Unable to get info").error()
            print e
            print error
        else:
            update.message.reply_text(r.text)

    # def getUsers(self, bot, update):
    #     try:
    #         r = requests.get(self.endpoint+'/users')
    #     except requests.exceptions.RequestException as e:
    #         error=Msg("Unable to get users").error()
    #         print e
    #         print error
    #     else: update.message.reply_text(r.text)

    def getDevices(self, bot, update):
        try:
            r = requests.get(self.endpoint+'/devices')
        except requests.exceptions.RequestException as e:
            error = Msg("Unable to get devices").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getResources(self, bot, update, args):
        try:
            if self.tempId is not None:
                r = requests.get(self.endpoint+'/resources?id='+self.tempId)
            else: r = requests.get(self.endpoint+'/resources?id='+args[0])
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get resources").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    # def newUser(self, bot, update, args):
    #     user = json.dumps(
    #         {"name": args[0], "surname": args[1], "email": args[2]})
    #     try:
    #         r = requests.post(self.endpoint+'/addUser', data=user)
    #     except requests.exceptions.RequestException as e:
    #         error=Msg("Unable to create new user").error()
    #         print e
    #         print error
    #     else:
    #         update.message.reply_text("New user added! Your smart home said:")
    #         update.message.reply_text(r.text)

    def newDevice(self, bot, update, args):
        device = json.dumps({"endpoint": args[0], "resources": args[1]})
        try:
            r = requests.post(self.endpoint+'/addDevice', data=device)
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to create new device").error()
            print e
            print error
        else:
            update.message.reply_text("New device added! Your smart home said:")
            update.message.reply_text(r.text)

    def handleResource(self, bot, update,args):
        try:
            if self.tempId is not None:
                r = requests.get(self.endpoint+'/device?id='+self.tempId)
            else: r = requests.get(self.endpoint+'/device?id='+args[0])
            update.message.reply_text("DEVICE:")
            update.message.reply_text(r.text)
            device=json.loads(r.text)["info"]
            if self.tempId is not None:
                r = requests.get(device["endPoints"]+'/resource?id='+args[0])
            else: r = requests.get(device["endPoints"]+'/resource?id='+args[1])
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to start resource").error()
            print e
            print error
        else: update.message.reply_text(r.text)
    
    def rebootDevice(self, bot, update,args):
        try:
            if self.tempId is not None:
                r = requests.get(self.endpoint+'/device?id='+self.tempId)
            else: r = requests.get(self.endpoint+'/device?id='+args[0])
            device=json.loads(r.text)["info"]
            r = requests.get(device["endPoints"]+'/reboot')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to reboot device").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def setId(self, bot, update,args):
        try:
            if not os.path.exists(self.filePath):
                with open(self.filePath, "a+") as outfile:
                    json.dump({"id":args[0]}, outfile)
                    outfile.close()
                update.message.reply_text("created botConfiguration.json")
            else:
                jsonData = open(self.filePath).read()
                updateData = json.loads(jsonData)
                updateData["id"]=args[0]
            self.getId()
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to set device id").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getHelp(self, bot, update):
        commandsList="""BOT COMMAND LIST:

        info - Catalog Webservice Info

        info - Catalog Webservice Info
        setid - Command: /setId deviceId | Ex: /setId 11-12-33-33 | Persist most used device id
        reboot - Command: /reboot deviceId | Ex: /reboot 11-12-33-33 | Update catalog's device's register
        device - Command: /device host port resources | Ex: /device localhost 8080 ["humidity"] | Add new device
        res - Command: /resource deviceId resourceId | Ex: /resouce 11-12-33-33 | Start/Stop device's resource
        devices - Get list of devices
        resources - Command: /resources deviceId | Ex: /resources 11-12-33-33 | Get list of resources for a device
        adddivision - Command: /adddivision divisionName | Ex: /adddivision division1 | Create new division
        removedivision - Command: /removedivision divisionName | Ex: /removedivision division1 | Delete division
        addlight - Command: /addlight divisionName lightName | Ex: /addlight division1 light1 | Create new light
        removelight - Command: /removelight divisionName lightName | Ex: /removelight division1 light1 | Delete light
        updatelightstate - Command: /updatelightstate divisionName lightName | Ex: /updateLightState division1 light1 | Turn on/off light
        
        """
        
        update.message.reply_text(commandsList)
  #      user - Command: /user name surname email | Ex: /user name1 surname1 email1 | Add new user
# users - Get list of users
        
    def main(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater("589534581:AAEjVfLTNkPFycdscg_XaVQJEcUP0eFgPec")

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("info", self.getInfo))
        dp.add_handler(CommandHandler("help", self.getHelp))

        # dp.add_handler(CommandHandler("users", self.getUsers))
        dp.add_handler(CommandHandler("devices", self.getDevices))
        dp.add_handler(CommandHandler("resources", self.getResources,pass_args=True))

        dp.add_handler(CommandHandler("res", self.handleResource,pass_args=True))
        # dp.add_handler(CommandHandler("user", self.newUser,pass_args=True))
        dp.add_handler(CommandHandler("device", self.newDevice,pass_args=True))
        dp.add_handler(CommandHandler("reboot", self.rebootDevice,pass_args=True))
        dp.add_handler(CommandHandler("setid", self.setId,pass_args=True))
        
        dp.add_handler(CommandHandler("adddivision", self.addDivison,pass_args=True))
        dp.add_handler(CommandHandler("removedivision", self.removeDivision,pass_args=True))
        dp.add_handler(CommandHandler("addlight", self.addLight,pass_args=True))
        dp.add_handler(CommandHandler("removelight", self.removeLight,pass_args=True))
        dp.add_handler(CommandHandler("updatelightstate", self.updateLightState,pass_args=True))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

if __name__ == '__main__':
    # catalog address
    address = '192.168.1.7'
    # catalog port
    port = 8080
    # catalog endpoint
    endpoint = 'http://'+address+':'+str(port)
    # homebot config
    filePath="Configuration/botConfiguration.json"
    bot = MyBot(endpoint,filePath)
    bot.main()
