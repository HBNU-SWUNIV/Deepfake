
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from pygsheets import Spreadsheet

class GrouptHandler():
    def __init__(self,state_map:dict, sh:Spreadsheet):
        self.state_map = state_map
        self.sh = sh

        self.handler = ConversationHandler(
			entry_points=[CommandHandler("classcode", self.handle_register_start)],
            states={
				self.state_map["GET_STUDENT_ID"]:[
                    CommandHandler("code_registration",self.get_stu_id)],
                
			},fallbacks=[CommandHandler('cancel', self.cancel)],)

    def get_handler(self) -> Dispatcher:
        return self.handler
    
    def get_help(self):
        return f"/classcode: [그룹등록]\n봇을 이용하여 그룹등록을 합니다.\n그룹구성원 중 그룹의 대표가 진행합니다. \n개인채팅에서는 사용할 수 없는 기능입니다."

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Display the gathered info and end the conversation."""
        context.user_data.clear()
        update.message.reply_text("취소 되었습니다.")
        return ConversationHandler.END

    def handle_register_start(self, update: Update, context: CallbackContext) -> int:

        if update.message.chat_id>0:
            update.message.reply_text("개인채팅에서 사용이 불가능한 기능입니다.\n명령어 실행을 취소합니다.")
            return ConversationHandler.END
            
        elif self.sdu_id_checked(update.message.chat_id)==1:
            update.message.reply_text("이미 등록된 그룹입니다.\n종료합니다.")
            return ConversationHandler.END

        else:
            update.message.reply_text("팀 코드를 등록하려면 /code_registration 를 클릭하세요.\n취소하려면 /cancel 을 클릭하세요..")
            context.user_data['next_state'] = "GET_STUDENT_ID"
            return self.state_map[context.user_data['next_state']]    
       
    def get_stu_id(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text("등록을 진행합니다")
        print(update.message.chat.title)
        self.classcode_add(update.message.chat.title,update.effective_user.id,update.message.chat_id)

        update.message.reply_text("등록이 완료되었습니다.")
        return ConversationHandler.END

    def sdu_id_checked(self, user_id:int) -> bool:

        wks = self.sh.worksheet('title','group')
        df = wks.get_as_df()

        user_data = df.index[df['group_id'] == user_id].tolist()
        if user_data:
            return 1
        else:
            return 0

		
    def classcode_add(self, classcode,user_id,group_id) -> None:
        infoGroup = [str(group_id),str(classcode),str(user_id)]
        wks = self.sh.worksheet('title','group')
        df = wks.get_as_df()
        wks.update_row((len(df)+2),infoGroup,col_offset=0)
