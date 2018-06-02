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

class MyBot(object):
    """
        TELEGRAM BOT

        Configuration:
        It is necessary to configure the catalog endpoint as address and port

        BOT COMMAND LIST:

        info - Catalog Webservice Info
        user - Command: /user name surname email | Ex: /user name1 surname1 email1 | Add new user
        device - Command: /device host port resources | Ex: /device localhost 8080 ["humidity"] | Add new device
        resource - Command: /resource deviceId resourceId | Ex: /resouce 11-12-33-33 | Start device's resource
        users - Get list of users
        devices - Get list of devices
        resources - Command: /resources deviceId | Ex: /resources 11-12-33-33 | Get list of resources for a device
        help - commands list
        
        UPDATE bot list:
        BOTFATHER:
        1. /setcommands
        2. choose @iotSmartHomeBot
        3. copy list 
    """

    def __init__(self,endpoint):
        print "Bot started..."
        self.endpoint=endpoint

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        print error

    def getInfo(self, bot, update):
        try:
            r = requests.get(self.endpoint)
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get info").error()
            print e
            print error
        else: 
            update.message.reply_text(r.text)

    def getUsers(self, bot, update):
        try:
            r = requests.get(self.endpoint+'/users')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get users").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getDevices(self, bot, update):
        try:
            r = requests.get(self.endpoint+'/devices')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get devices").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getResources(self, bot, update,args):
        try:
            r = requests.get(self.endpoint+'/resources?id='+args[0])
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
        user = json.dumps({"endpoint": args[0], "resources": args[1]})
        try:
            r = requests.post(self.endpoint+'/addDevice', data=user)
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to create new device").error()
            print e
            print error
        else:
            update.message.reply_text("New device added! Your smart home said:")
            update.message.reply_text(r.text)

    def startResource(self, bot, update,args):
        try:
            r = requests.get(self.endpoint+'/device?id='+args[0])
            update.message.reply_text("DEVICE:")
            update.message.reply_text(r.text)
            device=json.loads(r.text)["info"]
            r = requests.get(device["endPoints"]+'/resource?id='+args[1])
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to start resource").error()
            print e
            print error
        else: update.message.reply_text(r.text)
    
    def rebootDevice(self, bot, update,args):
        try:
            r = requests.get(self.endpoint+'/device?id='+args[0])
            update.message.reply_text("DEVICE:")
            update.message.reply_text(r.text)
            device=json.loads(r.text)["info"]
            r = requests.get(device["endPoints"]+'/reboot')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to reboot device").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getHelp(self, bot, update):
        commandsList="""BOT COMMAND LIST:

        info - Catalog Webservice Info
        device - Command: /device host port resources | Ex: /device localhost 8080 ["humidity"] | Add new device
        resource - Command: /resource deviceId resourceId | Ex: /resouce 11-12-33-33 | Start device's resource
        users - Get list of users
        devices - Get list of devices
        resources - Command: /resources deviceId | Ex: /resources 11-12-33-33 | Get list of resources for a device
        """
        
        update.message.reply_text(commandsList)
  #      user - Command: /user name surname email | Ex: /user name1 surname1 email1 | Add new user

    def main(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater("589534581:AAEjVfLTNkPFycdscg_XaVQJEcUP0eFgPec")

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("info", self.getInfo))
        dp.add_handler(CommandHandler("help", self.getHelp))

        dp.add_handler(CommandHandler("users", self.getUsers))
        dp.add_handler(CommandHandler("devices", self.getDevices))
        dp.add_handler(CommandHandler("resources", self.getResources,pass_args=True))

        dp.add_handler(CommandHandler("resource", self.startResource,pass_args=True))
        # dp.add_handler(CommandHandler("user", self.newUser,pass_args=True))
        dp.add_handler(CommandHandler("device", self.newDevice,pass_args=True))
        dp.add_handler(CommandHandler("reboot", self.rebootDevice,pass_args=True))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

if __name__ == '__main__':
    #catalog address
    address = '192.168.1.7'
    #catalog port
    port = 8080
    #catalog endpoint
    endpoint = 'http://'+address+':'+str(port)
    bot = MyBot(endpoint)
    bot.main()