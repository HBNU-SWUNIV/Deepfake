
from config import *
#from instance.config import *
from telegram_mgr import TelegramManager
#from errtelegram_mgr import ErrorDetectAlarm


from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *

import os


# System Simulator Initialization
se = SystemSimulator()

se.register_engine("sname", SIMULATION_MODE, TIME_DENSITY)
se.register_engine("errdetect", SIMULATION_MODE, TIME_DENSITY)

se.get_engine("sname").insert_input_port("start")
se.get_engine("sname").insert_input_port("msg")

se.get_engine("errdetect").insert_input_port("start")
se.get_engine("errdetect").insert_input_port("msg")

# Telegram Manager Initialization
tm = TelegramManager(se.get_engine("sname"), TELEGRAM_API_KEY_COLLECT)
# Error Detect BOT
#ed = ErrorDetectAlarm(se.get_engine("errdetect"), TELEGRAM_ERROR_DETECT)

# Monitoring System Start
tm.start()
#ed.start()
