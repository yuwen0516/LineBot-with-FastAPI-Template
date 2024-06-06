import sys
import google.generativeai as genai
from firebase import firebase
from linebot import LineBotApi
from linebot.models import TextMessage, TextSendMessage
sys.path.append(".")
import config
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
firebase_url = config.FIREBASE_URL
genai.configure(api_key = config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
def handle_message(event) -> None:
 """Event - User sent message

 Args:
     event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#message-event
 """
 user_id = event.source.user_id
 msg_type = event.message.type
 reply_token = event.reply_token
 fdb = firebase.FirebaseApplication(firebase_url, None)
 user_chat_path = f'chat/{user_id}'
 chat_state_path = f'state/{user_id}'
 chatgpt = fdb.get(user_chat_path, None)
 # Text message
 if isinstance(event.message, TextMessage):
     # Get user sent message
     user_message = event.message.text
     if chatgpt is None:
             messages = []
     else:
         messages = chatgpt
     if user_message == '!清空':
             reply_msg = TextSendMessage(text='對話歷史紀錄已經清空！')
             fdb.delete(user_chat_path, None)
     else:
         model = genai.GenerativeModel('gemini-pro')
         messages.append({'role':'user','parts': [user_message]})            
         response = model.generate_content(messages)
         messages.append({'role':'model','parts': [response.text]})                
         reply_msg = TextSendMessage(text=response.text)
         # 更新firebase中的對話紀錄
         fdb.put_async(user_chat_path, None , messages)
     # Reply with same message
     #messages = TextSendMessage(text=user_message)

     # Reply with AI Reply
     line_bot_api.reply_message(reply_token=reply_token, messages=reply_msg)
