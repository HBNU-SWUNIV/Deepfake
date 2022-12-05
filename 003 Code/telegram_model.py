from system_simulator import SystemSimulator
from behavior_model_executor import BehaviorModelExecutor
from system_message import SysMessage
from definition import *

#import pygsheets

from config import *

import pymysql

import re

class TelegramModel(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name, updater):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("IDLE")
        self.insert_state("IDLE", Infinite)
        self.insert_state("WAKE", 2)
  
        self.insert_input_port("msg")

        self.recv_msg = []
        self.updater = updater
        self.conn = pymysql.connect(host='teamatedb', user='root', password='simlab@417', db="dialog", charset='utf8mb4')
        #self.gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
        #self.sh = self.gc.open(GOOGLE_SPREAD_SHEET)
        #self.wks = self.sh.worksheet('title','chat_data')
        
        self.emoji_pattern = re.compile(u"(["                     # .* removed
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "])", flags= re.UNICODE)             # + removed

    def deEmojify(self, inputString):
        returnString = ""

        for character in inputString:
            try:
                character.encode("ascii")
                returnString += character
            except UnicodeEncodeError:
                replaced = unidecode(str(character))
                if replaced != '':
                    returnString += replaced
                else:
                    try:
                        returnString += "[" + unicodedata.name(character) + "]"
                    except ValueError:
                        returnString += "[x]"

        return returnString     
    
    def ext_trans(self,port, msg):
        if port == "msg":
            print("[Model] Received Msg")
            self._cur_state = "WAKE"
            self.recv_msg.append(msg.retrieve())
            self.cancel_rescheduling()
                        
    def output(self):
        if self._cur_state == "WAKE":
            #for _ in range(100):
            while True:
                if self.recv_msg:
                    msg = self.recv_msg.pop(0)
                    #chat_data_df = self.wks.get_as_df()
                    #print(stu_list_df)
                    #preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', msg[0])
                    #self.wks.update_value('A' + str(len(chat_data_df)+2), msg[1])
                    #self.wks.update_value('B' + str(len(chat_data_df)+2), msg[2])
                    #self.wks.update_value('C' + str(len(chat_data_df)+2), msg[3])        
                    #self.wks.update_value('D' + str(len(chat_data_df)+2), preprocessing_chat)
                    #self.wks.update_row((len(chat_data_df)+2),msg,col_offset=0)
                    #print(msg)
                    
                    #if not re.findall(self.emoji_pattern, msg[3]):
                    cur = self.conn.cursor()
                    #print(re.match(self.emoji_pattern, msg[3]).group(0))
                    
                    start = 0
                    contents = []
                    
                    for m in re.finditer(self.emoji_pattern, msg[3]):
                        contents.append(msg[3][start:m.span()[0]])
                        start = m.span()[1]
                    if len(msg[3]) > start:
                        contents.append(msg[3][start:len(msg[3])])

                    cur.execute(f"insert into team_chat(date, gid, uid, dialog) values('{msg[0]}', {msg[1]}, {msg[2]}, '{msg[3]}')")
                    cur.close()
                    self.conn.commit()

                else:
                    break
                    
                
            #self.recv_msg = []
            pass

    def int_trans(self):
        if self._cur_state == "WAKE":
            self._cur_state = "IDLE"
    
    def __del__(self):
        pass