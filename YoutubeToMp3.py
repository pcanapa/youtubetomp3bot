from flask import Flask, request
import telegram
import os, subprocess
import lxml
from urllib import urlopen, urlretrieve
import httplib
from lxml import etree
from threading import Thread
import random, string
import re, pipes
from datetime import datetime
import urlparse
#import time
import json
import unicodedata

class YoutubeToMP3(object):
	def __init__(self, token, host, port, cert, cert_key, working_dir):
    		
		self.token = token
		self.host = host
		self.port = port
		self.cert = cert
		self.cert_key = cert_key

		self.bot = telegram.Bot(self.token)
		self.app = Flask(__name__)
		self.context = (self.cert, self.cert_key)
		self.working_dir = working_dir
		self.kb = [[telegram.KeyboardButton('Offer me a coffee'), telegram.KeyboardButton('Source Code')]]
		self.kb_markup = telegram.ReplyKeyboardMarkup(self.kb, resize_keyboard=True)

	def Parser(self, message, chat_id, user):
		if(message == "/start"):
			self.bot.sendMessage(chat_id=chat_id, text='Yo! Start by sending me a youtube link..', reply_markup = self.kb_markup)
			try:
				os.makedirs(self.working_dir + '/' +str(chat_id).replace("-", ""))
			except:
				pass

		if (message == "Offer me a coffee"):
			self.bot.sendMessage(chat_id=chat_id, text='Bitcoin: 1KAFnFWUqwJUX4ZrbkzB3ja8a58EWfpKH5\nPayPal: https://paypal.me/PaoloPulli')

		if (message == "Source Code"):
			self.bot.sendMessage(chat_id=chat_id, text='https://github.com/pcanapa/youtubetomp3bot')

		if re.search(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be|m.youtube\.com|m.youtu\.?be)\/.+$', message):
			try:
				os.makedirs(self.working_dir + '/' +str(chat_id).replace("-", ""))
			except:
				pass
			self.downloader(message, chat_id, user)

	def downloader(self, message, chat_id, user):
		try:
			curr_dir = self.working_dir + '/' + str(chat_id).replace("-", "")
			os.chdir(curr_dir)
			RequestUrl = 'http://www.youtubeinmp3.com/fetch/index.php?format=json&video=%s' % (message)
			JsonVideoData = json.load(urlopen(RequestUrl))
			self.bot.sendMessage(chat_id=chat_id, text = 'Downloading ' +  JsonVideoData['title'] + '...');
			f = urlopen(JsonVideoData['link'], JsonVideoData['title'].replace('/', '').encode('utf-8').strip() + '.mp3')
			fulltitle = (curr_dir + '/' + JsonVideoData['title'].replace('/', '') + '.mp3')
			fulltitle = unicodedata.normalize('NFKD', fulltitle).encode('utf-8').strip()
			with open(fulltitle, 'wb') as mp3:
				mp3.write(f.read());
			with open(fulltitle) as mp3:
				self.bot.sendAudio(chat_id=chat_id, audio=mp3)
			os.remove(fulltitle);
			with open('log', 'a') as f:
				f.write(message + " " + str(datetime.now().time()))
				f.write("\n");
				f.close()
		except ValueError as e:
			self.bot.sendMessage(chat_id=chat_id, text = 'Video not found on the database of www.youtubeinmp3.com, but you can download the mp3 (and update the database) by using this link: ');
			RequestUrl = 'http://www.youtubeinmp3.com/download/?video=%s' % (message)
			self.bot.sendMessage(chat_id=chat_id, text = RequestUrl)
		except Exception as e:
			if str(e) != "101":					
				self.bot.sendMessage(chat_id=chat_id, text = 'Something went wrong, maybe the video does not exists,\nif the error persist send the code in the next message to the developer, Telegram: @aakagoree')
				self.bot.sendMessage(chat_id=chat_id, text = str(chat_id))
			with open('log', 'a') as f:
				f.write("!!EXCEPTION!!! " + message + " " + str(datetime.now().time()) + " " + str(e))
				f.write("\n");
				f.close()			
		finally:
			os.chdir(self.working_dir)
			
	def hello(self):
		return "Hello World!"
	def WebHook(self):
		try:
			update = telegram.update.Update.de_json(request.get_json(force=True), self.bot)
			thread = Thread(target = self.Parser, args = (update.message.text, update.message.chat_id, update.message.from_user))
			thread.start()
			return 'OK'
		except:
			return 'KO'

	def setWebhook(self):
		print('https://%s:%s/%s' % (self.host, self.port, self.token))
		self.bot.setWebhook(webhook_url='https://%s:%s/%s' % (self.host, self.port, self.token),certificate=open(self.cert, 'rb'))
	
	def botRun(self):
		
		#self.setWebhook()
		#time.sleep(5)

		self.app.add_url_rule('/' + self.token, view_func=self.WebHook,  methods=['POST'])
		self.app.add_url_rule('/', view_func=self.hello,  methods=['GET'])
		self.app.run(host=self.host,port=self.port,ssl_context=self.context,debug = False)
