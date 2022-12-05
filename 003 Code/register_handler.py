
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler,CallbackQueryHandler, CallbackContext

from pygsheets import Spreadsheet
from config import *
class RegisterHandler():
    def __init__(self,state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        self.sh = sh
        self.Cwks =self.sh.worksheet('title','class')
        self.Gwks = self.sh.worksheet('title','group')

        self.handler = ConversationHandler(
            entry_points=[CommandHandler('student_register', self.handle_register_start)],
            states={
                self.state_map["GET_STUDENT_ID"]: [
                    MessageHandler(
                        Filters.regex(r'\d{5}'), self.handle_check_user
                    ),
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(r'\d{5}')), self.handle_unwanted_data),
                ],

                self.state_map["TEAM_CHECKED"]:[
                    CallbackQueryHandler(self.matching_team)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

    def get_handler(self) -> Dispatcher:
        return self.handler
    
    def get_help(self):
        return f"/student_register: [사용자 등록]\n사용자 등록을 진행합니다. 학번과 팀을 등록합니다."

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

    def check_valid_user(self, user_id:int) -> bool:
        
        df = self.Cwks.get_as_df()

        user_data = df.index[df['학번'] == user_id].tolist()
        if user_data:
            return user_data[0]
        else:
            return -1

    def handle_check_user(self, update: Update, context: CallbackContext) -> int:

        stu_id = int(update.message.text)
        if (row := self.check_valid_user(stu_id)) >= 0:

            context.user_data['id'] = stu_id        
            context.user_data['row'] = row + 2
            context.user_data['next_state'] = "TEAM_CHECKED"

            checked=self.handle_check_stuid(context.user_data['row'],context.user_data['id'],update.effective_user.id)
            if checked>0:
                if  checked==0:
                    update.message.reply_text("개인등록이 완료되었습니다.")
                else :
                    update.message.reply_text("이 전 등록 과정을 이어서 진행합니다.")


                teamlist =self.get_team_info()
                show_list= []
                for team in teamlist:
                    show_list.append([InlineKeyboardButton(team,callback_data=team)])
                show_list.append([InlineKeyboardButton("없음",callback_data="no")])
                show_markup = InlineKeyboardMarkup(show_list)

                
                print("팀등록시작")
                update.message.reply_text("팀등록을 시작합니다\n해당되는 팀을 선택해주세요.",reply_markup=show_markup)

 
                context.user_data['next_state'] = "TEAM_CHECKED"
                return self.state_map[context.user_data['next_state']]
                

    
            elif checked ==-1:
                print("다른학번")
                update.message.reply_text("해당 학번에 이미 다른 텔레그램 아이디가 등록되어있습니다. 조교님께 확인바랍니다")
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"문의 사항 : {ASSISTANT_EMAIL}")
                return ConversationHandler.END
                  
            
        else:
            update.message.reply_text("수강신청 등록이 안된 사용자입니다.\n담당교수님께 확인하시길 바랍니다.")
            context.bot.send_message(chat_id=update.effective_chat.id, text= f"문의 사항 : {ASSISTANT_EMAIL}")
            context.user_data.clear()
            return ConversationHandler.END

    def check_pasword(self, idx:int, stu_id:str,user_id:str) -> bool:
        
        if (existsID := self.Cwks.get_value('D'+str(idx))):
            return existsID
        else:
            return 0

    def handle_check_stuid(self, idx:int,stu_id:str,user_id:str) -> int:
        print("handle_check_stuid")
        id_ =self.check_pasword(idx, stu_id,user_id)
        if id_==0:
            self.Cwks.update_value('D'+str(idx),user_id)
            return 1
        elif str(id_) == str(user_id):
            print("있는데 같아")
            return 2
        elif str(id_) != str(user_id):

            print("달라")
            return -1

    def get_team_info(self):
        
        df = self.Gwks.get_as_df()

        return list(set(df['classcode'].tolist()))      

    def matching_team(self, update: Update, context: CallbackContext) -> int:

        query = update.callback_query

        if query.data =='no':
            update.callback_query.message.edit_text("-> 그룹채팅방에서 등록을 완료했는지 조장에게 확인해주세요.해결하지 못한다면 조교님께 연락 바랍니다.")
            context.bot.send_message(chat_id=update.effective_chat.id, text= f"문의 사항 : {ASSISTANT_EMAIL}")
            return ConversationHandler.END

        else:

            groupID=self.check_groupid(query.data)
            df = self.Cwks.get_as_df()
            user_data = df.index[df['telegram_id'] == update.effective_user.id].tolist()
            self.Cwks.update_value('E'+str(user_data[0]+2),groupID)
            update.callback_query.message.edit_text("팀 등록이 완료되었습니다.")
            return ConversationHandler.END
    
    def check_groupid(self, code:str)->int:
        df = self.Gwks.get_as_df()

        user_data = df.index[df['classcode'] == code].tolist()


        
        if user_data:


            return self.Gwks.get_value('A'+str(user_data[0]+2))
        else:
            return -1