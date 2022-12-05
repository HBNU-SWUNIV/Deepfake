
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler,CallbackQueryHandler, CallbackContext
from config import *

from pygsheets import Spreadsheet

class CheckHandler():
    def __init__(self,state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        self.sh = sh
        self.Cwks =self.sh.worksheet('title','class')
        self.Gwks = self.sh.worksheet('title','group')
        self.Awks = self.sh.worksheet('title','attendance')
        self.Hwks = self.sh.worksheet('title','Homework')
        self.Swks = self.sh.worksheet('title','score')

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('Check', self.handle_register_start)],
            states={
                self.state_map["GET_STUDENT_ID"]: [
                    MessageHandler(
                        Filters.regex(r'\d{5}'), self.handle_check_user
                    ),
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(r'\d{5}')), self.handle_unwanted_data),
                ],
                self.state_map["SELECT_BUTTON"]:[
                    CallbackQueryHandler(self.select_act)
                ],                
                self.state_map["SCORE_CHECKED"]: [
                    CallbackQueryHandler(self.check_score)
                ],
                self.state_map["ATENDACNE_CHECKED"]: [
                    CallbackQueryHandler(self.check_attendance)
                ],
                self.state_map["SCORE_SELECT"]: [
                    CallbackQueryHandler(self.select_score)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

    def get_handler(self) -> Dispatcher:
        return self.handler
    
    def get_help(self):
        return f"/Check: [확인]\n출석 혹은 점수 확인."

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Display the gathered info and end the conversation."""
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END

    def handle_unwanted_data(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("다시 입력해주세요.")
        return self.state_map[context.user_data['next_state']]
    
    def handle_register_start(self, update: Update, context: CallbackContext) -> int:

        if update.message.chat.type != "private":
            update.message.reply_text("그룹 채팅에서는 사용할 수 없는 기능입니다.\n종료합니다.")
            return ConversationHandler.END
        else:
            update.message.reply_text("학번을 입력해주세요.")
            context.user_data['next_state'] = "GET_STUDENT_ID"
            return self.state_map[context.user_data['next_state']]

    def check_valid_user(self, stu_id:int, user_id:int) -> bool:
        df = self.Cwks.get_as_df()
        try:
            idx = df.index[df['학번'] == stu_id].tolist()
            telID = self.Cwks.get_value('D'+str(idx[0]+2))
        except:
            return -1
        print(idx[0]+2)
        print(telID)
        print("DDDD")
        print(user_id)
        if int(telID)==int(user_id):
            return idx[0]

        elif telID!=user_id:
            return -1
        else:
            return -1

    def handle_check_user(self, update: Update, context: CallbackContext) -> int:
        stu_id = int(update.message.text)
        user_id = update.effective_user.id
        if (row := self.check_valid_user(stu_id,user_id)) >= 0:
            context.user_data['id'] =   stu_id
            context.user_data['user_id'] =   user_id   
            context.user_data['row'] = row + 2
            

            

            show_list =[[InlineKeyboardButton("출석 확인",callback_data="attendace")],[InlineKeyboardButton("성적 확인",callback_data="score")]]

            show_markup = InlineKeyboardMarkup(show_list)

            update.message.reply_text("확인하고 싶은 사항을 선택해주세요",reply_markup=show_markup)
            context.user_data['next_state'] = "SELECT_BUTTON"
            return self.state_map[context.user_data['next_state']]
        else:
            update.message.reply_text(f"조교에게 사용자 등록 관련 확인 바랍니다. \n문의 사항 : {ASSISTANT_EMAIL}")
            context.user_data.clear()
            return ConversationHandler.END

    def select_act(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query

        if query.data =='attendace':
            show_list =[[InlineKeyboardButton("네",callback_data="yes")],[InlineKeyboardButton("아니오",callback_data="no")]]
            show_markup = InlineKeyboardMarkup(show_list)
            update.callback_query.message.edit_text("-> 출석확인 선택 ")

            context.bot.send_message(chat_id=update.effective_chat.id, text="출석확인 맞으신가요",reply_markup=show_markup)

            #update.message.reply_text("출석확인 맞으신가요?",reply_markup=show_markup)
            

            context.user_data['next_state'] = "ATENDACNE_CHECKED"
            return self.state_map[context.user_data['next_state']]
        elif query.data =='score':
            show_list =[[InlineKeyboardButton("네",callback_data="yes")],[InlineKeyboardButton("아니오",callback_data="no")]]
            show_markup = InlineKeyboardMarkup(show_list)
            update.callback_query.message.edit_text("-> 성적확인 선택 ")

            context.bot.send_message(chat_id=update.effective_chat.id, text="성적확인 맞으신가요?",reply_markup=show_markup)

            context.user_data['next_state'] = "SCORE_CHECKED"
            return self.state_map[context.user_data['next_state']]

    
    def check_score(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        if query.data == "no":
            update.callback_query.message.edit_text("-> 다시 선택을 진행합니다")
            show_list =[[InlineKeyboardButton("출석 확인",callback_data="attendace")],[InlineKeyboardButton("성적 확인",callback_data="score")]]

            show_markup = InlineKeyboardMarkup(show_list)
            
            context.bot.send_message(chat_id=update.effective_chat.id, text="확인하고 싶은 사항을 다시 선택해주세요.\n/cancel 을 선택하시면 대화가 종료됩니다",reply_markup=show_markup)

            context.user_data['next_state'] = "SELECT_BUTTON"
            return self.state_map[context.user_data['next_state']]

        elif query.data == "yes":
            update.callback_query.message.edit_text("성적 중 확인할 사항을 골라주세요")
            show_list =[[InlineKeyboardButton("과제 제출 확인",callback_data="submitcheck")],[InlineKeyboardButton("전체 성적 확인",callback_data="allscore")]]

            show_markup = InlineKeyboardMarkup(show_list)
            
            context.bot.send_message(chat_id=update.effective_chat.id, text="확인하고 싶은 사항을 선택해주세요.\n/cancel 을 선택하시면 대화가 종료됩니다",reply_markup=show_markup)

            context.user_data['next_state'] = "SCORE_SELECT"
            return self.state_map[context.user_data['next_state']]



    def select_score(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        if query.data == "submitcheck":
            update.callback_query.message.edit_text("Loading...")

            row = self._check_valid_user(context.user_data['id'],self.Hwks)
            Hlist=self.Hwks.get_row(row)
            Hindex =self.Hwks.get_row(1,returnas='matrix', include_tailing_empty=False)

            printContextList =[]
            for Hindex_,Hlist_ in zip(Hindex,Hlist):
                a=str(Hindex_)+" : "+str(Hlist_)
                printContextList.append(a)
            
            printContext = "\n".join(printContextList)
            update.callback_query.message.edit_text("<과제 현황>")
            context.bot.send_message(chat_id=update.effective_chat.id, text=printContext)
            context.bot.send_message(chat_id=update.effective_chat.id, text= f"문의 사항 : {ASSISTANT_EMAIL}")
            return ConversationHandler.END

        elif query.data == "allscore":

            update.callback_query.message.edit_text("Loading...")

            row = self._check_valid_user(context.user_data['id'],self.Swks)
            Hlist=self.Swks.get_row(row)
            Hindex =self.Swks.get_row(1,returnas='matrix', include_tailing_empty=False)

            printContextList =[]
            for Hindex_,Hlist_ in zip(Hindex,Hlist):
                a=str(Hindex_)+" : "+str(Hlist_)
                printContextList.append(a)
            
            printContext = "\n".join(printContextList)
            update.callback_query.message.edit_text("<최종 점수 현황>")
            context.bot.send_message(chat_id=update.effective_chat.id, text=printContext)
            context.bot.send_message(chat_id=update.effective_chat.id, text= f"문의 사항 : {ASSISTANT_EMAIL}")
            return ConversationHandler.END




    def _check_valid_user(self, stu_id:int,sh) -> bool:
        #df = self.Awks.get_as_df()
        df = sh.get_as_df()
        idx = df.index[df['학번'] == stu_id].tolist()

        return idx[0]+2



    def check_attendance(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        if query.data == "no":
            update.callback_query.message.edit_text("-> 다시 선택을 진행합니다")

            show_list =[[InlineKeyboardButton("출석 확인",callback_data="attendace")],[InlineKeyboardButton("성적 확인",callback_data="score")]]

            show_markup = InlineKeyboardMarkup(show_list)
            
            context.bot.send_message(chat_id=update.effective_chat.id, text="확인하고 싶은 사항을 다시 선택해주세요.\n/cancel 을 선택하시면 대화가 종료됩니다",reply_markup=show_markup)

            context.user_data['next_state'] = "SELECT_BUTTON"
            return self.state_map[context.user_data['next_state']]
        elif query.data == "yes":
            update.callback_query.message.edit_text("Loading...")
            row = self._check_valid_user(context.user_data['id'],self.Awks)
            Alist=self.Awks.get_row(row)
            Aindex =self.Awks.get_row(1,returnas='matrix', include_tailing_empty=False)
            for index,value in enumerate(Alist):
                if value =="1":
                    Alist[index]="출석"
                elif value =="0.5":
                    Alist[index]="지각"
                elif value == "0":
                    Alist[index]="결석"
                elif value == '':
                    Alist[index]="수업 미진행"
                
                else:
                    pass
                
            print(len(Alist))
            print(len(Aindex))
            printContextList =[]
            for Aindex_,Alist_ in zip(Aindex,Alist):
                a=str(Aindex_)+" : "+str(Alist_)
                printContextList.append(a)
            
            printContext = "\n".join(printContextList)
            update.callback_query.message.edit_text("<출석 현황>")
            context.bot.send_message(chat_id=update.effective_chat.id, text= printContext)
            context.bot.send_message(chat_id=update.effective_chat.id, text= f"문의 사항 : {ASSISTANT_EMAIL}")
            
            return ConversationHandler.END

