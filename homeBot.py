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
import logging
import string
import requests
import json

class MyBot(object):
    """
        COMMAND LIST:

        info - Webservice info
        user - Command: /user name surname email | Ex: /user name1 surname1 email1 | Add new user
        device - Command: /device host port resources | Ex: /device localhost 8080 ["humidity"] | Add new device
        resource - Command: /resource device_id | Ex: /resouce 11-12-33-33 | Start device's resource
        users - Get list of users
        devices - Get list of devices
        resources - Command: /resources id | Ex: /resouces 11-12-33-33 | Get list of resources for a device

    """
    def __init__(self, address, port):
        print "Bot started..."
        self.address = 'http://'+address+':'+str(port)

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        logger = logging.getLogger(__name__)

        self.CHOOSING, self.TYPING_REPLY, self.TYPING_CHOICE, self.ADD_USER = range(
            4)

        self.reply_keyboard = [['Add user', 'List users', 'Add device', 'List devices'],
                               ['Done']]

        self.markup = ReplyKeyboardMarkup(
            self.reply_keyboard, one_time_keyboard=True)

    # def facts_to_str(self, user_data):
    #     facts = list()

    #     for key, value in user_data.items():
    #         facts.append('{} - {}'.format(key, value))

    #     return "\n".join(facts).join(['\n', '\n'])

    # def start(self,bot, update):
    #     update.message.reply_text(
    #         "Hello! You may choose an action",
    #         reply_markup=self.markup)

    #     return self.CHOOSING

    # def regular_choice(self, bot, update, user_data):
    #     text = update.message.text
    #     user_data['choice'] = text
    #     print user_data['choice']
    #     update.message.reply_text(
    #         'Let\'s {}!'.format(text.lower()))

    #     return self.ADD_USER
        # if user_data['choice'] == "Add user":
        #     del user_data['choice']

        #     MessageHandler(Filters.text,
        #                                    newUser,
        #                                    pass_user_data=True)

        #     update.message.reply_text('What is your name?')
        #     text = update.message.text
        #     user_data['name']= text

        #     update.message.reply_text('What is your surname?')
        #     text = update.message.text
        #     user_data['surname']= text

        #     update.message.reply_text('What is your email?')
        #     text = update.message.text
        #     user_data['email']= text
        #     print(user_data['name'],user_data['email'])

        #     user=User("a","b","c")

        #     self.newUser(user)

        #     return self.CHOOSING

    # def custom_choice(self,bot, update):
    #     update.message.reply_text('Alright, please send me the category first, '
    #                             'for example "Most impressive skill"')

    #     return self.TYPING_CHOICE

    # def received_information(self, bot, update, user_data):
    #     text = update.message.text
    #     category = user_data['choice']
    #     user_data[category] = text
    #     del user_data['choice']

    #     update.message.reply_text("Neat! Just so you know, this is what you already told me:"
    #                               "{}"
    #                               "You can tell me more, or change your opinion on something.".format(
    #                                   facts_to_str(user_data)), reply_markup=self.markup)

    #     return self.CHOOSING

    # def done(self, bot, update, user_data):
    #     if 'choice' in user_data:
    #         del user_data['choice']

    #     update.message.reply_text("I learned these facts about you:"
    #                               "{}"
    #                               "Until next time!".format(facts_to_str(user_data)))

    #     user_data.clear()
    #     return ConversationHandler.END

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def getInfo(self, bot, update):
        try:
            r = requests.get(self.address)
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get info").error()
            print e
            print error
        else: 
            update.message.reply_text(r.text)

    def getUsers(self, bot, update):
        try:
            r = requests.get(self.address+'/users')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get users").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getDevices(self, bot, update):
        try:
            r = requests.get(self.address+'/devices')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get devices").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def getResources(self, bot, update):
        try:
            r = requests.get(self.address+'/resources')
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to get resources").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    def newUser(self, bot, update, args):
        user = json.dumps(
            {"name": args[0], "surname": args[1], "email": args[2]})
        try:
            r = requests.post(self.address+'/addUser', data=user)
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to create new user").error()
            print e
            print error
        else:
            update.message.reply_text("New user added! Your smart home said:")
            update.message.reply_text(r.text)

    def newDevice(self, bot, update, args):
        user = json.dumps({"endpoint": args[0], "resources": args[1]})
        try:
            r = requests.post(self.address+'/addDevice', data=user)
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to create new device").error()
            print e
            print error
        else:
            update.message.reply_text("New device added! Your smart home said:")
            update.message.reply_text(r.text)

    def startResource(self, bot, update,args):
        try:
            r = requests.get(self.address+'/resource',args[0])
        except requests.exceptions.RequestException as e:
            error=Msg("Unable to start resource").error()
            print e
            print error
        else: update.message.reply_text(r.text)

    # def handleNewUser(self,bot,update,user_data):

    #     def getParam(param,update,user_data):
    #         user_data[param]=update.message.text

    #     update.message.reply_text("name?")
    #     MessageHandler(Filters.text,
    #                         getParam("name",update,user_data),
    #                         pass_user_data=True)

    #     update.message.reply_text("surname?")
    #     MessageHandler(Filters.text,
    #     getParam("surname",update,user_data),
    #     pass_user_data=True)

    def main(self):
        # Create the Updater and pass it your bot's token.
        updater = Updater("589534581:AAEjVfLTNkPFycdscg_XaVQJEcUP0eFgPec")

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        # conv_handler = ConversationHandler(
        #     entry_points=[CommandHandler('start', self.start)],

        #     states={
        #         self.CHOOSING: [RegexHandler('^(Add user|Add Device|List users|List devices)$',
        #                                 self.regular_choice,
        #                                 pass_user_data=True)
        #                 #                 ,
        #                 # RegexHandler('^Something else...$',
        #                 #                 self.custom_choice),
        #                 ],
        #         self.TYPING_CHOICE: [MessageHandler(Filters.text,
        #                                     self.regular_choice,
        #                                     pass_user_data=True),
        #                         ],
        #         # self.GET_NAME: [MessageHandler(Filters.text,
        #         #             self.getName,
        #         #             pass_user_data=True),
        #         # ]
        #         # self.GET_SURNAME: [MessageHandler(Filters.text,
        #         #             self.getName,
        #         #             pass_user_data=True),
        #         # ]
        #         # self.GET_EMAIL: [MessageHandler(Filters.text,
        #         #             self.getName,
        #         #             pass_user_data=True),
        #         # ]
        #         # self.ADD_USER: [MessageHandler(Filters.text,
        #         #             self.handleNewUser,
        #         #             pass_user_data=True),
        #         # ]
        #         # self.TYPING_REPLY: [MessageHandler(Filters.text,
        #         #                             self.received_information,
        #         #                             pass_user_data=True),
        #         #             ],
        #     },

        #     fallbacks=[RegexHandler('^Done$', self.done, pass_user_data=True)]
        # )

        # dp.add_handler(conv_handler)

        dp.add_handler(CommandHandler("info", self.getInfo))
        dp.add_handler(CommandHandler("users", self.getUsers))
        dp.add_handler(CommandHandler("devices", self.getDevices))
        dp.add_handler(CommandHandler("resources", self.getResources))

        dp.add_handler(CommandHandler("resource", self.startResource,pass_args=True))
        dp.add_handler(CommandHandler("user", self.newUser,pass_args=True))
        dp.add_handler(CommandHandler("device", self.newDevice,pass_args=True))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

if __name__ == '__main__':
    address = '192.168.1.5'
    port = 8080
    bot = MyBot(address, port)
    bot.main()