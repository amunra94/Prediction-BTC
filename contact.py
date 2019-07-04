""" This module works with telegram """

import logging
import telebot
import time
import dbwork
import settings
import re
import os
import urllib.request as urllib

from telebot import apihelper
from bs4 import BeautifulSoup as bs



class TBotNotify:
    def __init__(self, token):
        self.token = token
        self.proxies = self.get_new_proxies()
        if self.proxies is None or self.proxies == []:
            apihelper.proxy = {'https': '205.202.41.16:8083'}
        apihelper.proxy = self.proxies[0]

        self.bot = telebot.TeleBot(self.token)

    def get_new_proxies(self):
        site = 'https://free-proxy-list.net/'
        hdr = {'User-Agent': 'Mozilla/5.0'}
        logger = logging.getLogger('App.get_new_proxies')
        try:
            req = urllib.Request(site, headers=hdr)  # sending requests with headers
            url = urllib.urlopen(req).read()  # opening and reading the source code
            html = bs(url, "lxml")  # structuring the source code in proper format
            rows = html.findAll("tr")  # finding all rows in the table if any.
            proxies = []
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text for ele in cols]
                try:
                    ip = cols[0]  # ip which presents in the first element of cols list
                    port = cols[1]  # port which presents in the second element of cols list
                    proxy = ':'.join([ip, port])
                    https = cols[6]  # portName variable result will be yes / No
                    if https == "yes":
                        proxies.append({'https': str(proxy)})  # if no then it appends the proxy with http
                except Exception:
                    pass
        except Exception:
            logger.warning('Cannot connect to proxy %s' % apihelper.proxy['https'])
            return None
        logger.info('Added new proxies!')
        return proxies

    def send_plot(self, plot):
        """
        Load list of users telegram bot from database and send plot.

        """
        logger = logging.getLogger('App.send_plot')
        db = dbwork.DataBase(settings.NAME_DATABASE)
        db.init_user_table(settings.NAME_TABLE_USER)
        users_id = db.get_users_id(settings.NAME_TABLE_USER)

        if users_id == []:
            return False
        i = 0
        while (True):
            try:
                for chat_id in users_id:
                    self.bot.send_photo(chat_id, open(plot, 'rb'))
                    time.sleep(1)
                    logger.info('Send plot success!')
                break
            except Exception as e:
                logger.warning('Send plot cannot connect %s' % apihelper.proxy['https'])
                time.sleep(2)
                i += 1
                if i >= len(self.proxies):
                    i = 0
                    self.proxies = self.get_new_proxies()

                apihelper.proxy = self.proxies[i]
        return True

    def send_message(self, text):
        """
        Load list of users telegram bot from database and send message.
        """
        logger = logging.getLogger('App.send_message')
        db = dbwork.DataBase(settings.NAME_DATABASE)
        db.init_user_table(settings.NAME_TABLE_USER)
        users_id = db.get_users_id(settings.NAME_TABLE_USER)
        if users_id == []:
            return False
        i = 0
        while (True):
            try:
                for chat_id in users_id:
                    self.bot.send_message(chat_id[0], text)
                    time.sleep(1)
                    logger.info('Send message success!')
                break
            except Exception:
                logger.warning('Send message cannot connect %s' % apihelper.proxy['https'])
                time.sleep(2)
                i += 1
                if i >= len(self.proxies):
                    i = 0
                    self.proxies = self.get_new_proxies()

                apihelper.proxy = self.proxies[i]
        return True

    def start(self):
        """
        Start bot to manage application.
        Adding emails for notifications, get users list, run app.py for prediction.
        """
        logger = logging.getLogger('Contact.TBotNotify.start')
        i = 0
        while (True):
            try:
                @self.bot.message_handler(commands=['help', 'start'])
                def send_welcome(message):
                    chat_id = message.chat.id
                    user_id = message.from_user.id
                    fname = message.chat.first_name
                    lname = message.chat.last_name
                    uname = message.chat.username
                    db = dbwork.DataBase(settings.NAME_DATABASE)
                    db.init_user_table(settings.NAME_TABLE_USER)
                    if db.check_user(settings.NAME_TABLE_USER, user_id):
                        self.bot.reply_to(message,
                                          "Еще раз привет, %s %s!\nТы уже есть в базе моих друзей!" % (fname, lname))
                    else:
                        db.push_user(settings.NAME_TABLE_USER, user_id, chat_id, fname, lname, uname)
                        self.bot.reply_to(message, "Привет, %s %s !\n Я бот, который поможет тебе торговать!\n\n"
                                                   "Каждый день я буду писать тебе о моём прогнозе цены Bitcoin!" % (
                                              fname, lname))
                    logger.info('Succes send welcome!')

                @self.bot.message_handler(commands=['users'])
                def get_users_list(message):
                    command = message.text.split(' ')
                    if len(command) < 2:
                        self.bot.send_message(message.chat.id, 'Введите пароль...')
                    else:
                        password = command[1]
                        if password == str(settings.PASSWORD):
                            db = dbwork.DataBase(settings.NAME_DATABASE)
                            db.init_user_table(settings.NAME_TABLE_USER)
                            users = db.get_users(settings.NAME_TABLE_USER)
                            l_users = []
                            for user in users:
                                l_users.append('|'.join(list(map(str, user))))

                            self.bot.send_message(message.chat.id, '\n'.join(l_users))
                            logger.info('Success get users list!')
                        else:
                            self.bot.send_message(message.chat.id, 'Не верный пароль.')

                @self.bot.message_handler(commands=['insert_email'])
                def insert_email(message):
                    command = message.text.split(' ')
                    if len(command) != 3:
                        self.bot.send_message(message.chat.id, 'Введите корректный запрос: command password email')
                    else:
                        password = command[1]
                        email = command[2]
                        if password == str(settings.PASSWORD):
                            db = dbwork.DataBase(settings.NAME_DATABASE)
                            db.init_email_table(settings.NAME_TABLE_EMAILS)
                            db.push_email(settings.NAME_TABLE_EMAILS, email)
                            self.bot.send_message(message.chat.id, 'Почтовый ящик добавлен!')
                            logger.info('Success inserted email!')

                        else:
                            self.bot.send_message(message.chat.id, 'Введите корректный пароль...')

                @self.bot.message_handler(commands=['make'])
                def make_predict(message):
                    command = message.text.split(' ')
                    if len(command) != 2:
                        self.bot.send_message(message.chat.id, 'Введите корректный запрос: make password')
                    else:
                        password = command[1]
                        if password == str(settings.PASSWORD):
                            os.system('python3 app.py')
                            self.bot.send_message(message.chat.id, 'Прогноз получен!')
                            logger.info('Success make_predict!')
                        else:
                            self.bot.send_message(message.chat.id, 'Введите корректный пароль...')

                @self.bot.message_handler(commands=['params'])
                def get_users_list(message):
                    columns = message.text.split(' ')
                    if len(columns) < 4:
                        self.bot.send_message(message.chat.id, 'Введите корректный запрос..')
                        return None
                    try:
                        _, password = tuple(columns[0:2])
                        param, value = tuple(columns[2:])
                    except Exception:
                        self.bot.send_message(message.chat.id, 'Введите корректный запрос..')
                        return None

                    with open('settings.py', 'r') as fsettings:
                        lines = fsettings.readlines()

                    for i in range(len(lines)):
                        if re.match(param.upper(), lines[i]):
                            lines[i] = '='.join([param.upper(), value]) + '\n'
                            break

                    with open('settings.py', 'w') as fsettings:
                        fsettings.writelines(lines)

                self.bot.remove_webhook()
                self.bot.polling(none_stop=True, interval=20)

            except Exception:
                logger.warning('Start process cannot connect! ')

                time.sleep(1)
                i += 1
                if i >= len(self.proxies):
                    i = 0
                    self.proxies = self.get_new_proxies()
                apihelper.proxy = self.proxies[i]


if __name__ == '__main__':
    bot = TBotNotify(settings.BOT_TOKEN)
    bot.start()
