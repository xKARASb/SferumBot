import requests, os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from models.user import User
from models.db import connect_db

load_dotenv()

key = (os.getenv("KEY")).encode("utf-8")

def chek_cookie(cookie) -> dict:
  cookies = {
    "remixdsid": cookie
  }
  params = {
     "v": 5.204,
     "act": "web_token",
     "app_id": "8202606"
  } 
  resp = requests.get("https://web.vk.me/", params=params, cookies=cookies).json()[0]
  if resp.get("error", False):
    return {"error", True}
  
  id = resp["user_id"]

  return {"id": id}



def get_user_id(cookie) -> int:
  cookies = {
    "remixdsid": cookie
  }
  params = {
     "v": 5.204,
     "act": "web_token",
     "app_id": "8202606"
  } 
  resp = requests.get("https://web.vk.me/", params=params, cookies=cookies).json()
  id = resp[0]["user_id"]
  return id 

def get_access_token(cookie) -> str:
  cookies = {
    "remixdsid": cookie
  }
  params = {
     "v": 5.204,
     "act": "web_token",
     "app_id": "8202606"
  } 
  resp = requests.get("https://web.vk.me/", params=params, cookies=cookies).json()
  access_token = resp[0]["access_token"]
  return access_token

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



def encrypt_cookie(cookie: str) -> str:
  fernet = Fernet(key)
  encrypted = fernet.encrypt(cookie.encode()).decode()
  return encrypted

def decrypt_cookie(encryp_cookie: str) -> str:
  fernet = Fernet(key)
  dectex = fernet.decrypt(encryp_cookie.encode()).decode()
  return dectex

def message_text_validate(text: str):
  validate_text = []
  
  for char in text:
    if char in ('_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!'):
      validate_text.append("\\")
    validate_text.append(char)
  return "".join(validate_text)