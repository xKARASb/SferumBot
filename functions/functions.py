import requests, os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from models.user import User
from models.db import connect_db

load_dotenv()

key = (os.getenv("KEY")).encode("utf-8")

def chek_cookie(cookie) -> dict:
  cookies = {
    "remixdsid": cookie,
    "remixweb_vk_me_profile_type": "2",
  }
  params = {
     "v": 5.204,
     "act": "web_token",
     "app_id": "8202606"
  } 
  resp = requests.get("https://web.vk.me/", params=params, cookies=cookies).json()
  if resp[0].get("error", False):
    return {"error", True}
  
  resp = resp[0] if resp[0].get("profile_type", 0) == 2 else resp[1]
  
  id = resp["user_id"]
  return {"id": id}

#VK API
def get_user_id(cookie) -> int:
  cookies = {
    "remixdsid": cookie,
    "remixweb_vk_me_profile_type": "2",
  }
  params = {
     "v": 5.204,
     "act": "web_token",
     "app_id": "8202606"
  } 
  resp = requests.get("https://web.vk.me/", params=params, cookies=cookies).json()
  
  resp = resp[0] if resp[0].get("profile_type", 0) == 2 else resp[1]
  
  return resp["user_id"]
#VK API
def get_access_token(cookie) -> str:
  cookies = {
    "remixdsid": cookie,
  }
  params = {
     "v": 5.204,
     "act": "web_token",
     "app_id": "8202606"
  } 
  resp = requests.get("https://web.vk.me/", params=params, cookies=cookies).json()
  resp = resp[0] if resp[0].get("profile_type", 0) == 2 else resp[1]

  access_token = resp["access_token"]
  return access_token

# VK API
def get_members(vk_id) -> None:
  session = connect_db()
  user_db = session.query(User).filter(User.vk_id==vk_id).first()
  cookie = user_db.cookie
  peer = user_db.peer
  cookie = decrypt_cookie(cookie)
  access_token = get_access_token(cookie)

  data= {"peer_id": peer, "offset":0, "extended": 1, "group_id": 0, "fields": "id,first_name, last_name", "access_token":access_token}
  resp = requests.post("https://api.vk.me/method/messages.getConversationMembers?v=5.204", data=data)
  return resp.json()["response"]["profiles"]


#Шифрование куки
def encrypt_cookie(cookie: str) -> str:
  fernet = Fernet(key)
  encrypted = fernet.encrypt(cookie.encode()).decode()
  return encrypted

#Дешифрование куки
def decrypt_cookie(encryp_cookie: str) -> str:
  fernet = Fernet(key)
  dectex = fernet.decrypt(encryp_cookie.encode()).decode()
  return dectex

#Обработка текста для отправки в телеграм
def message_text_validate(text: str):
  validate_text = []
  
  text = "\n".join(text.split("<br>"))

  for char in text:
    if char in ('_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!', ">"):
      validate_text.append("\\")
    validate_text.append(char)
  return "".join(validate_text)