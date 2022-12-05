from telegram.ext.conversationhandler import ConversationHandler
import contexts
from telegram import Update, ForceReply, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

#2021.08.26
from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *
from states import REGISTER_STATES,ASSISTANT_STATES,GROUP_STATE,CHECK_STATES
from telegram_model import TelegramModel as TM
import pygsheets
import signal
from config import *

from time import strftime

from register_handler import RegisterHandler
from assistant_handler import AssistantHandler
from group_handler import GrouptHandler
from Check_handler import CheckHandler
import re
import sys,os

'''
# Simulation Configuration


se.get_engine("sname").simulate()'''

class TelegramManager():
	def __init__(self,engine, tel_token):
		self.se = engine
		self.updater = Updater(tel_token)

		signal.signal(signal.SIGINT,  self.signal_handler)
		signal.signal(signal.SIGABRT, self.signal_handler)
		signal.signal(signal.SIGTERM, self.signal_handler)

		self.is_terminating = False

		model = TM(0, Infinite, "tm", "sname", self.updater)

		self.se.coupling_relation(None, "start", model, "start")
		self.se.coupling_relation(None, "msg", model, "msg")


		self.se.register_entity(model)


		self.gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
		self.sh = self.gc.open(GOOGLE_SPREAD_SHEET)
		dispatcher = self.updater.dispatcher
		self.Rstate_map ={state:idx for idx, state in enumerate(REGISTER_STATES)}
		self.Astate_map ={state:idx for idx, state in enumerate(ASSISTANT_STATES)}
		self.Gstate_map ={state:idx for idx, state in enumerate(GROUP_STATE)}
		self.Cstate_map ={state:idx for idx, state in enumerate(CHECK_STATES)}
		self.handlers =[
                        RegisterHandler(self.Rstate_map,self.sh),
						CheckHandler(self.Cstate_map,self.sh),
						GrouptHandler(self.Gstate_map,self.sh)

        ]
		for handler in self.handlers:
			dispatcher.add_handler(handler.get_handler())

		# on different commands - answer in Telegram

		dispatcher.add_handler(CommandHandler("update", self.update_freq))
		dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & ~Filters.chat_type.private, self.collect_msg))
		dispatcher.add_handler(MessageHandler(Filters.photo& ~Filters.command & ~Filters.chat_type.private,self.collect_photo))
		dispatcher.add_handler(MessageHandler(Filters.document& ~Filters.command& ~Filters.chat_type.private, self.collect_file))
		dispatcher.add_handler(CommandHandler('start', self.start_))
		# Start the Bot		
		self.updater.start_polling()



		#dispatcher.add_handler(CommandHandler('start', self.start))


	def start_(self, update: Update, context: CallbackContext) -> None:
		#command /start

		context.user_data.clear()

		resp = ""
		for handler in self.handlers:
			resp += handler.get_help()
			resp += "\n"
		update.message.reply_text(resp)   



	def update_freq(self, update: Update, context: CallbackContext) -> None:
		print(update.message.text)
		user = update.effective_user
		tokens = update.message.text.split(" ")
		#self.se.simulate()
		self.se.insert_external_event("msg", [float(tokens[1]), user.id])

	def start(self) -> None:
		"""Start the bot."""
		# Create the Updater and pass it your bot's token.

		# Get the dispatcher to register handlers

		self.se.simulate()

	def collect_photo(self, update: Update, context: CallbackContext) -> None:
		msg = []
		preprocessing_chat = "photophotophotophotohellophoto"
		
		
		msg.append(strftime('%Y-%m-%d %H:%M:%S'))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))
		msg.append(preprocessing_chat)

		self.se.insert_custom_external_event("msg", msg)

	def collect_file(self, update: Update, context: CallbackContext) -> None:
		msg = []
		preprocessing_chat = "filefilefilefilefilefilehellofile"
		
		
		msg.append(strftime('%Y-%m-%d %H:%M:%S'))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))
		msg.append(preprocessing_chat)

		self.se.insert_custom_external_event("msg", msg)

	def collect_msg(self, update: Update, context: CallbackContext) -> None:
		msg = []
		print(update.message.text)
		preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', update.message.text)
		
		
		#msg.append(str(update.message.date))
		msg.append(strftime('%Y-%m-%d %H:%M:%S'))
		msg.append((update.message.chat_id))
		msg.append((update.effective_user.id))
		msg.append(preprocessing_chat)

		self.se.insert_custom_external_event("msg", msg)


	def signal_handler(self, sig, frame):
		print("Terminating Monitoring System")
		
		if not self.is_terminating:
			self.is_terminating = True
			self.updater.stop()
			del self.se
		
		sys.exit(0)